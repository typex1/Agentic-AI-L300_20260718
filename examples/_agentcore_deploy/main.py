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
            output.append(f"* {r['title']}\n  {r['href']}\n  {r['body']}")
        return "\n\n".join(output)
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
