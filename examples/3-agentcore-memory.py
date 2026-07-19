"""
3-agentcore-memory.py — AgentCore Memory: Create, Store, and Retrieve

Demonstrates Amazon Bedrock AgentCore Memory as a standalone service
(no runtime deployment needed). This script:

  1. Creates a Memory resource with strategies (semantic + user preference)
  2. Stores conversation events (short-term memory)
  3. Waits for long-term memory extraction
  4. Retrieves relevant memories using semantic search

Think of AgentCore Memory as a managed "memory database" for your agents:
  - Short-term memory: raw conversation events (like chat history)
  - Long-term memory: extracted facts, preferences, summaries (auto-generated)

Prerequisites:
  - pip install bedrock-agentcore
  - AWS credentials with bedrock-agentcore:CreateMemory, CreateEvent permissions

NOTE: In this lab, memory names must start with "FinancialAdvisorMemory"
(IAM policy constraint) and match [a-zA-Z][a-zA-Z0-9_]{0,47}.
In your own account, use any name.
"""

import time
import uuid
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MEMORY_NAME = "FinancialAdvisorMemory"
ACTOR_ID = "student-user-1"
SESSION_ID = str(uuid.uuid4())

print("=" * 60)
print("  AgentCore Memory — Create, Store, and Retrieve")
print("=" * 60)

# ---------------------------------------------------------------------------
# Step 1: Create a Memory resource with strategies
# ---------------------------------------------------------------------------
print("\n[1/4] Creating Memory resource...")
print(f"  Name: {MEMORY_NAME}")

memory_client = MemoryClient()

# Define what the memory should extract from conversations:
# - Semantic: factual information (e.g., "user earns $5000/month")
# - User Preference: preferences (e.g., "prefers low-risk investments")
memory_strategies = [
    {
        StrategyType.SEMANTIC.value: {
            "name": "user_facts",
            "description": "Extracts factual information about the user",
            "namespaces": ["{actorId}/facts"],
        }
    },
    {
        StrategyType.USER_PREFERENCE.value: {
            "name": "user_preferences",
            "description": "Captures user preferences and choices",
            "namespaces": ["{actorId}/preferences"],
        }
    },
]

# Check if memory already exists (reuse if so)
existing_memories = memory_client.list_memories()
memory_id = None

for mem in existing_memories:
    if mem.get("name") == MEMORY_NAME:
        memory_id = mem["id"]
        print(f"  ✓ Using existing memory: {memory_id}")
        break

if not memory_id:
    # Create the memory (this takes 30-60 seconds)
    memory = memory_client.create_memory_and_wait(
        name=MEMORY_NAME,
        strategies=memory_strategies,
        description="Demo memory for AgentCore Memory example",
        event_expiry_days=7,
    )
    memory_id = memory["id"]
    print(f"  ✓ Memory created: {memory_id}")

# ---------------------------------------------------------------------------
# Step 2: Store conversation events (short-term memory)
# ---------------------------------------------------------------------------
print("\n[2/4] Storing conversation events...")

# Simulate a multi-turn conversation with the agent
conversations = [
    # Turn 1: User provides financial context
    [
        ("Hi, I need help with my finances. I earn $8000 per month as a software engineer.", "USER"),
        ("I'd be happy to help! With a monthly income of $8000, you have a solid foundation. What are your main financial goals?", "ASSISTANT"),
    ],
    # Turn 2: User shares preferences
    [
        ("I want to save for a house down payment. I prefer low-risk investments and I'm targeting $60,000 in 2 years.", "USER"),
        ("Great goals! For a 2-year timeline with low risk preference, I'd suggest high-yield savings accounts and short-term bonds. You'd need to save about $2,500/month to reach $60,000.", "ASSISTANT"),
    ],
    # Turn 3: More context
    [
        ("My monthly expenses are about $4000 including rent of $1800. I also have $10,000 in student loans.", "USER"),
        ("With $4000 in expenses, you have $4000 remaining. After allocating $2,500 for your house fund, you'd have $1,500 for loan payments and discretionary spending.", "ASSISTANT"),
    ],
]

for i, messages in enumerate(conversations, 1):
    event = memory_client.create_event(
        memory_id=memory_id,
        actor_id=ACTOR_ID,
        session_id=SESSION_ID,
        messages=messages,
    )
    print(f"  ✓ Event {i}/3 stored (event_id: {event.get('eventId', 'N/A')})")

# ---------------------------------------------------------------------------
# Step 3: Wait for long-term memory extraction
# ---------------------------------------------------------------------------
print("\n[3/4] Waiting for memory extraction...")
print("  (AgentCore processes events and extracts facts/preferences)")
print("  This may take 30-90 seconds...")

# Wait for extraction to complete — poll until records appear
namespace = f"{ACTOR_ID}/facts"
extracted = memory_client.wait_for_memories(
    memory_id=memory_id,
    namespace=namespace,
    test_query="income salary",
    max_wait=120,
    poll_interval=10,
)

if extracted:
    print("  ✓ Memory extraction completed!")
else:
    print("  ⚠️  Extraction may still be in progress (continuing anyway)")

# ---------------------------------------------------------------------------
# Step 4: Retrieve memories using semantic search
# ---------------------------------------------------------------------------
print("\n[4/4] Retrieving memories with semantic search...")

queries = [
    ("What is the user's income?", f"{ACTOR_ID}/facts"),
    ("What are the user's investment preferences?", f"{ACTOR_ID}/preferences"),
    ("How much does the user spend on rent?", f"{ACTOR_ID}/facts"),
]

for query, ns in queries:
    print(f"\n  Query: \"{query}\"")
    print(f"  Namespace: {ns}")

    records = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace=ns,
        query=query,
        top_k=3,
    )

    if records:
        for j, record in enumerate(records, 1):
            content = record.get("content", record.get("text", "N/A"))
            score = record.get("score", "N/A")
            print(f"    [{j}] (score: {score}) {content}")
    else:
        print("    (no records found — extraction may still be in progress)")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  Done!")
print("=" * 60)
print(f"\n  Memory ID:  {memory_id}")
print(f"  Memory Name: {MEMORY_NAME}")
print(f"  Actor ID:   {ACTOR_ID}")
print(f"  Session ID: {SESSION_ID}")
print(f"\n  Run 3-create-test-request.py to query this memory interactively.")
print(f"  The memory will auto-expire in 7 days (event_expiry_days=7).")
