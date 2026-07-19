# AgentCore Deployment: Starter Toolkit (Runtime) vs. Harness

Amazon Bedrock AgentCore offers two distinct paths to deploy agents. This
document compares them so you can pick the right one for your use case.

## Overview

- **AgentCore Runtime** (what we use in `2-deploy-to-AgentCore.py`) — you bring
  your own agent code in a container. Full control, any framework.

- **AgentCore Harness** (newer, higher-level) — you provide a configuration
  (model, tools, instructions). AWS runs the reasoning loop for you. No custom
  code required.

## Comparison

| | AgentCore Runtime | AgentCore Harness |
|---|---|---|
| **What you deploy** | Your own container with custom agent code | A configuration (no container needed) |
| **Agent framework** | Bring your own (Strands, LangChain, CrewAI, etc.) | AWS-managed reasoning loop |
| **How it works** | Write `main.py` with `BedrockAgentCoreApp`, build container, push to ECR | Call `CreateHarness` API with model + instructions + tools |
| **Invocation** | HTTP POST to runtime endpoint with Bearer token | `InvokeHarness` API (streaming events) |
| **Deployment tool** | `bedrock-agentcore-starter-toolkit` (Python) | `@aws/agentcore` CLI (Node.js) or `boto3` |
| **Custom logic** | Unlimited — any Python code, custom tools, multi-agent orchestration | Limited to built-in tool types and model configuration |
| **Memory** | Manual integration via `MemoryClient` | Built-in configuration option |
| **Auth** | Cognito JWT or custom authorizer | IAM-based |
| **Best for** | Complex agents, custom frameworks, full control | Simple agents, rapid prototyping, no-code setups |

## Runtime (Starter Toolkit) — How We Deploy

```
You write:          main.py (your agent code)
                    requirements.txt

Starter toolkit:    Generates Dockerfile
                    Uploads to S3
                    CodeBuild builds ARM64 container
                    Pushes to ECR
                    Calls CreateAgentRuntime API
                    Creates DEFAULT endpoint

You invoke:         HTTP POST with Bearer token
```

```python
from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()
runtime.configure(entrypoint="main.py", ...)
runtime.launch()  # builds, deploys, waits for READY
```

See: `examples/2-deploy-to-AgentCore.py` and `examples/2-deploy-to-AgentCore.md`

## Harness — The Managed Alternative

```
You provide:        Configuration (model, system prompt, tools)

AWS manages:        Reasoning loop, tool execution, streaming
                    No container, no Dockerfile, no ECR

You invoke:         InvokeHarness API or AgentCore CLI
```

```python
import boto3

# Create
client = boto3.client("bedrock-agentcore-control")
client.create_harness(
    harnessName="MyAgent",
    executionRoleArn="arn:aws:iam::...:role/MyRole"
)

# Invoke
client = boto3.client("bedrock-agentcore")
response = client.invoke_harness(
    harnessArn="arn:aws:bedrock-agentcore:us-east-1:...:harness/MyAgent-abc123",
    runtimeSessionId="some-uuid-at-least-33-chars-long",
    messages=[{"role": "user", "content": [{"text": "Hello!"}]}],
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        print(event["contentBlockDelta"]["delta"].get("text", ""), end="")
```

Or using the AgentCore CLI (Node.js):

```bash
npm install -g @aws/agentcore
agentcore create --name myagent --model-provider bedrock
agentcore deploy
agentcore invoke --harness myagent --session-id "$(uuidgen)" "Hello!"
```

Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-get-started.html

## When to Use Which

**Choose Runtime (Starter Toolkit) when:**
- You need custom agent logic (multi-agent, custom tools, complex workflows)
- You want to use a specific framework (Strands, LangChain, etc.)
- You need full control over the agent's behavior
- You're deploying production workloads with specific requirements

**Choose Harness when:**
- You want the fastest path to a working agent
- Your use case fits standard patterns (chat + built-in tools)
- You don't need custom Python code in the agent
- You want AWS to manage the reasoning loop and scaling

## Note for This Lab

This lab uses **AgentCore Runtime** via the starter toolkit because:
1. We deploy a custom Strands agent with a DuckDuckGo web search tool
2. The lab is designed to teach how agents work under the hood
3. Runtime gives students visibility into the full deployment pipeline

The Harness approach would not work here because our custom `web_search` tool
(using the `ddgs` Python library) requires custom code execution — something
only Runtime supports.
