# Deploy a Web Search Agent to Amazon Bedrock AgentCore

This document walks through what `2-deploy-to-AgentCore.py` does — the simplest
possible path from a local Strands agent to a production endpoint on AgentCore.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Your machine (this script)                                     │
│                                                                 │
│  1. Write main.py + requirements.txt                            │
│  2. Create Cognito user pool (for auth)                         │
│  3. Configure & launch via starter toolkit                      │
│       ├── Upload source to S3                                   │
│       ├── CodeBuild builds ARM64 container                      │
│       ├── Push image to ECR                                     │
│       └── CreateAgentRuntime + endpoint                         │
│  4. Invoke endpoint with HTTP POST + Bearer token               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  AgentCore Runtime (AWS-managed)                                │
│                                                                 │
│  Container runs main.py:                                        │
│    BedrockAgentCoreApp → @app.entrypoint → Agent + web_search   │
│                                                                 │
│  Auto-scaling, observability, HTTPS endpoint                    │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python packages | `strands-agents`, `bedrock-agentcore`, `bedrock-agentcore-starter-toolkit`, `requests`, `ddgs` |
| IAM roles | `AmazonBedrockAgentCoreSDKRuntime-<region>` and `AmazonBedrockAgentCoreSDKCodeBuild-<region>-*` (pre-created in this lab) |
| Model access | `amazon.nova-pro-v1:0` enabled in Amazon Bedrock |

## Step 1: Write the Agent Code (`main.py`)

This is the code that runs **inside** the AgentCore container. It's a standard
Strands agent wrapped with `BedrockAgentCoreApp`:

```python
from strands import Agent, tool
from bedrock_agentcore import BedrockAgentCoreApp
from ddgs import DDGS

app = BedrockAgentCoreApp()

@tool
def web_search(query: str, max_results: int = 3) -> str:
    """Search the web using DuckDuckGo."""
    results = DDGS().text(query, max_results=max_results)
    if not results:
        return "No results found."
    output = []
    for r in results:
        output.append(f"* {r['title']}\n  {r['href']}\n  {r['body']}")
    return "\n\n".join(output)

agent = Agent(
    model="us.amazon.nova-pro-v1:0",
    tools=[web_search],
    system_prompt="You are a helpful assistant with web search capabilities.",
)

@app.entrypoint
async def invoke(payload):
    """Receives {"prompt": "..."}, yields streaming text chunks."""
    async for event in agent.stream_async(payload["prompt"]):
        if "data" in event:
            yield event["data"]

if __name__ == "__main__":
    app.run()
```

Key points:
- `BedrockAgentCoreApp` creates an HTTP server on port 8080 with `/invocations` and `/ping` endpoints
- The `@app.entrypoint` decorator registers your async generator as the handler
- Yielding strings produces a streaming SSE response to the caller

## Step 2: Set Up Cognito Authentication

AgentCore requires JWT authentication. We create a Cognito User Pool with:
- A user pool + app client
- A test user with a permanent password
- Credentials stored in AWS Secrets Manager for later retrieval

```python
from utils import setup_cognito_user_pool

cognito_config = setup_cognito_user_pool()

# This gives us:
#   cognito_config["client_id"]      — App client ID
#   cognito_config["discovery_url"]  — OIDC discovery URL
#   cognito_config["secret_name"]    — Secrets Manager key (for re-auth)
#   cognito_config["bearer_token"]   — Initial access token
```

The authorizer config passed to AgentCore:

```python
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"],
    }
}
```

## Step 3: Configure the AgentCore Runtime

The `bedrock_agentcore_starter_toolkit.Runtime` handles all deployment mechanics:

```python
from bedrock_agentcore_starter_toolkit import Runtime

agentcore_runtime = Runtime()

agentcore_runtime.configure(
    entrypoint="main.py",
    execution_role=execution_role_arn,   # Pre-created IAM role
    auto_create_execution_role=False,
    auto_create_ecr=True,               # Creates ECR repo automatically
    requirements_file="requirements.txt",
    region="us-east-1",
    agent_name="personal_finance_agent",
    authorizer_configuration=auth_config,
)
```

This generates a `Dockerfile` and `.bedrock_agentcore.yaml` config file.

## Step 4: Launch (Build + Deploy)

```python
launch_result = agentcore_runtime.launch()
# launch_result.agent_arn  → the ARN to invoke
# launch_result.agent_id   → the runtime ID
```

Behind the scenes:
1. Source code is zipped and uploaded to S3
2. AWS CodeBuild builds an ARM64 container image
3. Image is pushed to Amazon ECR
4. `CreateAgentRuntime` API creates the runtime resource
5. A `DEFAULT` endpoint is created and polled until active

Typical time: ~1-2 minutes.

## Step 5: Invoke the Deployed Agent

With the agent running, invoke it via HTTP POST:

```python
import requests, urllib.parse, uuid

def invoke_endpoint(agent_arn, payload, session_id, bearer_token, region="us-east-1"):
    escaped_arn = urllib.parse.quote(agent_arn, safe="")
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_arn}/invocations"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }

    response = requests.post(
        url,
        params={"qualifier": "DEFAULT"},
        headers=headers,
        json=payload,
        timeout=120,
        stream=True,
    )

    for line in response.iter_lines(chunk_size=1):
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                yield decoded[6:]

# Get a fresh token and invoke
bearer_token = reauthenticate_user(
    client_id=cognito_config["client_id"],
    secret_name=cognito_config["secret_name"],
)

for chunk in invoke_endpoint(
    agent_arn=launch_result.agent_arn,
    payload={"prompt": "What is Amazon Bedrock AgentCore?"},
    session_id=str(uuid.uuid4()),
    bearer_token=bearer_token,
):
    print(chunk, end="")
```

## What Gets Created in AWS

| Resource | Name/Pattern |
|----------|-------------|
| ECR Repository | `bedrock-agentcore-personal_finance_agent` |
| S3 Bucket | `bedrock-agentcore-codebuild-sources-<account>-<region>` |
| CodeBuild Project | `bedrock-agentcore-personal_finance_agent-builder` |
| AgentCore Runtime | `personal_finance_agent-<random>` |
| AgentCore Endpoint | `DEFAULT` (on the runtime above) |
| Cognito User Pool | `agentpool` |
| Secrets Manager | `agentcore-lab-credentials-<hex>` |

## Cleanup

To remove the deployed resources:

```python
import boto3

region = "us-east-1"
agentcore = boto3.client("bedrock-agentcore-control", region_name=region)

# Delete endpoint, then runtime
agentcore.delete_agent_runtime_endpoint(
    agentRuntimeId="personal_finance_agent-XXXXX",
    agentRuntimeEndpointId="DEFAULT"
)
agentcore.delete_agent_runtime(agentRuntimeId="personal_finance_agent-XXXXX")

# Delete ECR repo
ecr = boto3.client("ecr", region_name=region)
ecr.delete_repository(repositoryName="bedrock-agentcore-personal_finance_agent", force=True)

# Delete Cognito pool
from utils import delete_cognito_user_pool
delete_cognito_user_pool()
```

## Lab Note

In this lab environment, the IAM permissions restrict the ECR repository and
CodeBuild project names to `personal_finance_agent`. In your own AWS account,
you can use any `agent_name` you like.
