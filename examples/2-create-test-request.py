"""
2-create-test-request.py — Test an Existing AgentCore Runtime Deployment

This script discovers the deployed AgentCore runtime and Cognito credentials,
then sends a test request. Run this after 2-deploy-to-AgentCore.py has completed.

Usage:
    python examples/2-create-test-request.py
    python examples/2-create-test-request.py "Your custom question here"
"""

import json
import sys
import uuid
import urllib.parse
from pathlib import Path
from typing import Any

import boto3
import requests

# Add the environment root for shared utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils import reauthenticate_user

REGION = "us-east-1"


def discover_agent_runtime() -> dict:
    """Find the deployed AgentCore runtime."""
    client = boto3.client("bedrock-agentcore-control", region_name=REGION)
    response = client.list_agent_runtimes(maxResults=10)

    runtimes = response.get("agentRuntimes", [])
    if not runtimes:
        print("❌ No AgentCore runtimes found. Run 2-deploy-to-AgentCore.py first.")
        sys.exit(1)

    # Pick the first READY runtime
    for rt in runtimes:
        if rt.get("status") == "READY":
            print(f"✓ Found runtime: {rt['agentRuntimeName']} ({rt['agentRuntimeId']})")
            print(f"  Status: {rt['status']}")
            return rt

    # If none are READY, show what we found
    print("⚠️  No READY runtimes found. Current runtimes:")
    for rt in runtimes:
        print(f"  - {rt['agentRuntimeId']}: {rt.get('status', 'UNKNOWN')}")
    sys.exit(1)


def discover_cognito_credentials() -> dict:
    """Find and retrieve Cognito credentials from Secrets Manager."""
    secrets_client = boto3.client("secretsmanager", region_name=REGION)

    # List secrets matching our naming pattern
    response = secrets_client.list_secrets(
        Filters=[{"Key": "name", "Values": ["agentcore-lab-credentials"]}]
    )

    secret_list = response.get("SecretList", [])
    if not secret_list:
        print("❌ No Cognito credentials found in Secrets Manager.")
        print("   Run 2-deploy-to-AgentCore.py first to set up authentication.")
        sys.exit(1)

    # Use the most recently created secret
    secret = sorted(secret_list, key=lambda s: s.get("CreatedDate", ""), reverse=True)[0]
    secret_name = secret["Name"]

    # Retrieve the secret value
    secret_value = secrets_client.get_secret_value(SecretId=secret_name)
    credentials = json.loads(secret_value["SecretString"])

    print(f"✓ Found credentials: {secret_name}")
    return credentials


def get_bearer_token(credentials: dict) -> str:
    """Authenticate and get a fresh bearer token."""
    token = reauthenticate_user(
        client_id=credentials["client_id"],
        username=credentials["username"],
        password=credentials["password"],
    )
    return token


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

    if response.status_code != 200:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    for line in response.iter_lines(chunk_size=1):
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                yield decoded[6:].replace('"', "")
            elif decoded:
                yield "\n" + decoded.replace('"', "")


def main():
    # Custom prompt from command line, or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Search the web for the latest news about Amazon Bedrock and give me a brief summary."

    print("=" * 60)
    print("  AgentCore Runtime — Test Request")
    print("=" * 60)

    # Step 1: Discover the runtime
    print("\n[1/3] Discovering deployed runtime...")
    runtime = discover_agent_runtime()
    agent_arn = runtime["agentRuntimeArn"]

    # Step 2: Get authentication token
    print("\n[2/3] Authenticating...")
    credentials = discover_cognito_credentials()
    bearer_token = get_bearer_token(credentials)

    # Step 3: Send the request
    print(f"\n[3/3] Sending request...")
    print(f"\n  Prompt: {prompt}\n")
    print("-" * 60)

    for chunk in invoke_endpoint(
        agent_arn=agent_arn,
        payload={"prompt": prompt},
        session_id=str(uuid.uuid4()),
        bearer_token=bearer_token,
    ):
        print(chunk.replace("\\n", "\n"), end="")

    print("\n" + "-" * 60)
    print("\n✓ Request completed.")


if __name__ == "__main__":
    main()
