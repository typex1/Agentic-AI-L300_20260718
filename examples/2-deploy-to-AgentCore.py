"""
2-deploy-to-AgentCore.py — Deploy a Simple Web Search Agent to Amazon Bedrock AgentCore

This script demonstrates the simplest possible deployment of a Strands agent to
Amazon Bedrock AgentCore Runtime. It deploys a web search agent (using DuckDuckGo)
and invokes it via the AgentCore endpoint.

Steps:
  1. Write a minimal main.py (the agent code that runs inside AgentCore)
  2. Write a requirements.txt for the container
  3. Set up Cognito authentication (required by AgentCore)
  4. Configure and launch the AgentCore Runtime
  5. Invoke the deployed agent

Prerequisites:
  - pip install bedrock-agentcore bedrock-agentcore-starter-toolkit strands-agents requests
  - IAM roles pre-created (AmazonBedrockAgentCoreSDKRuntime-<region>,
    AmazonBedrockAgentCoreSDKCodeBuild-<region>-5d12c2867b)

NOTE: The agent_name MUST be "personal_finance_agent" because the IAM/ECR
permissions in this lab are scoped to that name. In your own account you can
use any name.
"""

import json
import os
import sys
import uuid
import urllib.parse
from pathlib import Path
from typing import Optional, Any

import boto3
import requests
from boto3.session import Session

# Add the environment root so we can import the shared utils module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils import setup_cognito_user_pool, reauthenticate_user

from bedrock_agentcore_starter_toolkit import Runtime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REGION = "us-east-1"
AGENT_NAME = "personal_finance_agent"  # Must match IAM/ECR permissions in this lab

# We write the deployment files to a temporary working directory
WORK_DIR = Path(__file__).resolve().parent / "_agentcore_deploy"
WORK_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Step 1: Write main.py — the agent code that runs inside AgentCore
# ---------------------------------------------------------------------------
MAIN_PY = '''\
"""Minimal web search agent deployed on Amazon Bedrock AgentCore."""

from strands import Agent, tool
from bedrock_agentcore import BedrockAgentCoreApp
from ddgs import DDGS
import boto3

region = boto3.Session().region_name

app = BedrockAgentCoreApp()


@tool
def web_search(query: str, max_results: int = 3) -> str:
    """Search the web using DuckDuckGo and return results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 3).

    Returns:
        Search results with titles, URLs, and snippets.
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        output = []
        for r in results:
            output.append(f"* {r['title']}\\n  {r['href']}\\n  {r['body']}")
        return "\\n\\n".join(output)
    except Exception as e:
        return f"Search error: {e}"


agent = Agent(
    model="us.amazon.nova-pro-v1:0",
    tools=[web_search],
    system_prompt=(
        "You are a helpful assistant with web search capabilities. "
        "Use the web_search tool to find current information when needed. "
        "Always cite your sources."
    ),
)


@app.entrypoint
async def invoke(payload):
    """AgentCore entrypoint — receives a payload dict, yields streaming chunks."""
    user_message = payload["prompt"]

    async for event in agent.stream_async(user_message):
        if "data" in event:
            yield event["data"]


if __name__ == "__main__":
    app.run()
'''

REQUIREMENTS_TXT = """\
strands-agents>=1.7.0
bedrock-agentcore>=0.1.3
ddgs>=9.14.0
boto3
"""

main_path = WORK_DIR / "main.py"
req_path = WORK_DIR / "requirements.txt"

main_path.write_text(MAIN_PY)
req_path.write_text(REQUIREMENTS_TXT)

print(f"✓ Wrote deployment files to: {WORK_DIR}")
print(f"  - main.py  (agent code)")
print(f"  - requirements.txt")

# ---------------------------------------------------------------------------
# Step 2: Set up Cognito authentication
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Step 2: Setting up Amazon Cognito for authentication...")
print("=" * 60)

cognito_config = setup_cognito_user_pool()
if not cognito_config:
    print("❌ Cognito setup failed. Exiting.")
    sys.exit(1)

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"],
    }
}

# ---------------------------------------------------------------------------
# Step 3: Configure AgentCore Runtime
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Step 3: Configuring AgentCore Runtime...")
print("=" * 60)

sts_client = boto3.client("sts", region_name=REGION)
account_id = sts_client.get_caller_identity()["Account"]
execution_role_arn = f"arn:aws:iam::{account_id}:role/AmazonBedrockAgentCoreSDKRuntime-{REGION}"

agentcore_runtime = Runtime()

# Change to WORK_DIR so the toolkit can find main.py and requirements.txt
original_dir = os.getcwd()
os.chdir(WORK_DIR)

try:
    agentcore_runtime.configure(
        entrypoint="main.py",
        execution_role=execution_role_arn,
        auto_create_execution_role=False,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=REGION,
        agent_name=AGENT_NAME,
        authorizer_configuration=auth_config,
    )
    print("✓ Configuration completed")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    os.chdir(original_dir)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 4: Launch (build container + deploy to AgentCore)
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Step 4: Launching agent to AgentCore Runtime...")
print("  (This will take several minutes — building container, pushing to ECR,")
print("   creating runtime, waiting for endpoint to become active)")
print("=" * 60)

try:
    launch_result = agentcore_runtime.launch()
    print(f"\n✓ Launch completed!")
    print(f"  Agent ARN: {launch_result.agent_arn}")
    print(f"  Agent ID:  {launch_result.agent_id}")
except Exception as e:
    print(f"❌ Launch failed: {e}")
    os.chdir(original_dir)
    sys.exit(1)
finally:
    os.chdir(original_dir)

# ---------------------------------------------------------------------------
# Step 5: Invoke the deployed agent
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Step 5: Invoking the deployed agent...")
print("=" * 60)


def invoke_endpoint(
    agent_arn: str,
    payload: dict,
    session_id: str,
    bearer_token: str,
    region: str = REGION,
    endpoint_name: str = "DEFAULT",
) -> Any:
    """Invoke AgentCore endpoint using HTTP POST with bearer token."""
    escaped_arn = urllib.parse.quote(agent_arn, safe="")
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_arn}/invocations"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }

    response = requests.post(
        url,
        params={"qualifier": endpoint_name},
        headers=headers,
        json=payload,
        timeout=120,
        stream=True,
    )

    for line in response.iter_lines(chunk_size=1):
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                yield decoded[6:].replace('"', "")
            elif decoded:
                yield "\n" + decoded.replace('"', "")


# Get a fresh bearer token
bearer_token = reauthenticate_user(
    client_id=cognito_config["client_id"],
    secret_name=cognito_config["secret_name"],
)

# Send a test query
test_prompt = "What is Amazon Bedrock AgentCore? Search the web and summarize."
print(f"\nQuery: {test_prompt}\n")
print("Response:")
print("-" * 60)

for chunk in invoke_endpoint(
    agent_arn=launch_result.agent_arn,
    payload={"prompt": test_prompt},
    session_id=str(uuid.uuid4()),
    bearer_token=bearer_token,
):
    print(chunk.replace("\\n", "\n"), end="")

print("\n" + "-" * 60)
print("\n✓ Done! Your web search agent is live on AgentCore.")
print(f"  Agent ARN: {launch_result.agent_arn}")
print(f"  To invoke again, use the invoke_endpoint() function with a fresh bearer token.")
