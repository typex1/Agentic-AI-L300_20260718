"""
3-create-test-request.py — Query an Existing AgentCore Memory

This script discovers an existing AgentCore Memory resource and lets you
query it interactively. Run after 3-agentcore-memory.py has completed.

Usage:
    python examples/3-create-test-request.py
    python examples/3-create-test-request.py "What does the user earn?"
    python examples/3-create-test-request.py --list-events
"""

import json
import sys
from bedrock_agentcore.memory import MemoryClient

ACTOR_ID = "student-user-1"


def discover_memory(memory_client: MemoryClient) -> dict:
    """Find an existing FinancialAdvisorMemory-demo-* memory."""
    memories = memory_client.list_memories()

    # Filter for our demo memories (matching on id which contains the name)
    demo_memories = [m for m in memories if m.get("id", "").startswith("FinancialAdvisorMemory")]

    if not demo_memories:
        print("❌ No AgentCore Memory found.")
        print("   Run 3-agentcore-memory.py first to create one.")
        sys.exit(1)

    # Use the most recently created one
    memory = demo_memories[-1]
    print(f"✓ Found memory: {memory['id']} (status: {memory.get('status', 'N/A')})")
    return memory


def list_events(memory_client: MemoryClient, memory_id: str):
    """List stored events (short-term memory)."""
    print("\n📋 Stored Events (Short-Term Memory):")
    print("-" * 60)

    # We need actor_id and session_id to list events
    # Try to find sessions by listing with a known actor
    try:
        events = memory_client.list_events(
            memory_id=memory_id,
            actor_id=ACTOR_ID,
            session_id="*",  # May not work — fall back
            max_results=20,
        )
        for i, event in enumerate(events, 1):
            print(f"\n  Event {i}:")
            messages = event.get("payload", {}).get("messages", [])
            for msg in messages:
                role = msg.get("role", "?")
                text = msg.get("content", msg.get("text", ""))[:100]
                print(f"    [{role}] {text}")
    except Exception as e:
        print(f"  Could not list events: {e}")
        print("  (This is normal — event listing requires exact session_id)")


def query_memories(memory_client: MemoryClient, memory_id: str, query: str):
    """Retrieve memories matching a query."""
    namespaces = [
        (f"{ACTOR_ID}/facts", "Facts"),
        (f"{ACTOR_ID}/preferences", "Preferences"),
    ]

    print(f"\n🔍 Query: \"{query}\"")
    print("-" * 60)

    found_any = False
    for namespace, label in namespaces:
        records = memory_client.retrieve_memories(
            memory_id=memory_id,
            namespace=namespace,
            query=query,
            top_k=5,
        )

        if records:
            found_any = True
            print(f"\n  [{label}] (namespace: {namespace})")
            for j, record in enumerate(records, 1):
                content = record.get("content", record.get("text", "N/A"))
                score = record.get("score", "N/A")
                print(f"    {j}. (score: {score}) {content}")

    if not found_any:
        # Try with namespace_path for broader search
        print("\n  Trying broader search with namespace_path...")
        records = memory_client.retrieve_memories(
            memory_id=memory_id,
            namespace_path=f"{ACTOR_ID}/",
            query=query,
            top_k=5,
        )
        if records:
            for j, record in enumerate(records, 1):
                content = record.get("content", record.get("text", "N/A"))
                score = record.get("score", "N/A")
                ns = record.get("namespace", "")
                print(f"    {j}. [{ns}] (score: {score}) {content}")
        else:
            print("  No memories found. Extraction may still be in progress.")
            print("  Wait a minute and try again.")


def interactive_mode(memory_client: MemoryClient, memory_id: str):
    """Run interactive query loop."""
    print("\n💬 Interactive mode — type a query or 'quit' to exit")
    print("   Example queries:")
    print("     - What is the user's income?")
    print("     - What are their savings goals?")
    print("     - What investment style do they prefer?")
    print("     - How much do they spend monthly?")

    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not query or query.lower() in ("quit", "exit", "q"):
            break

        query_memories(memory_client, memory_id, query)


def main():
    print("=" * 60)
    print("  AgentCore Memory — Test Queries")
    print("=" * 60)

    memory_client = MemoryClient()

    # Discover existing memory
    print("\n[1/2] Discovering memory resource...")
    memory = discover_memory(memory_client)
    memory_id = memory["id"]

    # Handle command-line arguments
    if len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:])

        if arg == "--list-events":
            list_events(memory_client, memory_id)
            return

        # Treat argument as a query
        print(f"\n[2/2] Querying memory...")
        query_memories(memory_client, memory_id, arg)
        return

    # Default: show a few standard queries, then go interactive
    print(f"\n[2/2] Running sample queries...")

    sample_queries = [
        "What is the user's monthly income?",
        "What kind of investments does the user prefer?",
        "What is the user saving for?",
    ]

    for q in sample_queries:
        query_memories(memory_client, memory_id, q)

    # Interactive mode
    interactive_mode(memory_client, memory_id)


if __name__ == "__main__":
    main()
