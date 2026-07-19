"""
1-agent-with-web-search.py — Strands Agent with DuckDuckGo Web Search

Demonstrates:
- Creating a custom web search tool using the ddgs library
- The agent autonomously deciding when to search the web
- Using amazon.nova-pro-v1:0 as the foundation model
"""

from strands import Agent, tool
from ddgs import DDGS


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
            output.append(f"• {r['title']}\n  {r['href']}\n  {r['body']}")
        return "\n\n".join(output)
    except Exception as e:
        return f"Search error: {e}"


agent = Agent(
    model="us.amazon.nova-pro-v1:0",
    tools=[web_search],
    system_prompt=(
        "You are a helpful assistant with access to web search. "
        "Use the web_search tool to find current information when needed."
    ),
)

# --- Run a sample query ---
if __name__ == "__main__":
    response = agent("Search the web for 'Amazon Bedrock Strands Agents SDK' and summarize what it is.")
    print(f"\n{'='*60}")
    print(f"Response:\n{response}")
