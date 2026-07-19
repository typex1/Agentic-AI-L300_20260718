# AgentCore Memory — Give Your Agent Long-Term Memory

This document walks through what `3-agentcore-memory.py` does — using Amazon
Bedrock AgentCore Memory as a standalone service to store and retrieve
information across conversations.

## What is AgentCore Memory?

AgentCore Memory is a managed service that gives your agents persistent memory.
It works independently from AgentCore Runtime — you can use it with any agent
framework, even locally.

```
┌─────────────────────────────────────────────────────┐
│                AgentCore Memory                      │
│                                                     │
│  ┌───────────────┐     ┌────────────────────────┐   │
│  │ Short-Term    │     │ Long-Term Memory        │   │
│  │ Memory        │────▶│ (auto-extracted)        │   │
│  │               │     │                         │   │
│  │ Raw events    │     │ • Facts (semantic)      │   │
│  │ (chat turns)  │     │ • Preferences           │   │
│  │               │     │ • Summaries             │   │
│  └───────────────┘     │ • Episodes              │   │
│                         └────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         ▲                          │
         │ create_event()           │ retrieve_memories()
         │                          ▼
┌─────────────────────────────────────────────────────┐
│  Your Agent (local or deployed)                     │
└─────────────────────────────────────────────────────┘
```

**Short-term memory** = raw conversation events you store with `create_event()`

**Long-term memory** = facts, preferences, and summaries that AgentCore
automatically extracts from your events using the strategies you configure.

## Memory Strategies

Strategies tell AgentCore *what* to extract from conversations:

| Strategy | What it extracts | Example |
|----------|-----------------|---------|
| `SEMANTIC` | Factual information | "User earns $8000/month" |
| `USER_PREFERENCE` | Preferences and choices | "Prefers low-risk investments" |
| `SUMMARY` | Conversation summaries | "Discussed savings plan for house" |
| `EPISODIC` | Temporal episodes | "Met with advisor on July 19" |

## Step-by-Step Walkthrough

### Step 1: Create a Memory Resource

```python
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

memory_client = MemoryClient()

strategies = [
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

memory = memory_client.create_memory_and_wait(
    name="FinancialAdvisorMemory-demo",
    strategies=strategies,
    description="Demo memory",
    event_expiry_days=7,
)

memory_id = memory["id"]
```

Key points:
- `create_memory_and_wait()` polls until the memory is `ACTIVE` (~30-60s)
- `namespaces` use templates: `{actorId}` is replaced with the actual actor ID
- `event_expiry_days` controls how long raw events are kept

### Step 2: Store Conversation Events

```python
memory_client.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    messages=[
        ("I earn $8000 per month.", "USER"),
        ("Great, that gives you a solid foundation.", "ASSISTANT"),
    ],
)
```

Key points:
- `messages` is a list of `(text, role)` tuples
- Roles: `USER`, `ASSISTANT`, `TOOL`
- `actor_id` identifies the user — memories are organized per actor
- `session_id` groups related events (one conversation session)
- After storing, AgentCore automatically runs extraction strategies

### Step 3: Wait for Extraction

After storing events, AgentCore needs time to extract long-term memories
(typically 30-90 seconds):

```python
ready = memory_client.wait_for_memories(
    memory_id=memory_id,
    namespace="user-123/facts",
    test_query="income",
    max_wait=120,
    poll_interval=10,
)
```

### Step 4: Retrieve Memories

Query extracted memories using semantic search:

```python
records = memory_client.retrieve_memories(
    memory_id=memory_id,
    namespace="user-123/facts",      # Exact namespace match
    query="What is the user's income?",
    top_k=3,
)

for record in records:
    print(f"  {record['content']}  (score: {record['score']})")
```

You can also search across all namespaces for an actor:

```python
records = memory_client.retrieve_memories(
    memory_id=memory_id,
    namespace_path="user-123/",      # Prefix search (all sub-namespaces)
    query="investment preferences",
    top_k=5,
)
```

## Namespace Design

Namespaces organize memories hierarchically. Use templates in strategy
definitions:

```
{actorId}/facts          → "user-123/facts"
{actorId}/preferences    → "user-123/preferences"
{actorId}/sessions/{sessionId}  → "user-123/sessions/abc-def-123"
```

When retrieving:
- `namespace="user-123/facts"` — exact match (faster, more precise)
- `namespace_path="user-123/"` — prefix match (searches across all sub-namespaces)

## Other Useful Methods

```python
# List all memory resources
memories = memory_client.list_memories()

# Get short-term memory (last K turns)
turns = memory_client.get_last_k_turns(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    k=5,
)

# Delete a memory resource
memory_client.delete_memory(memory_id)
```

## Lab Constraint

In this lab, the IAM policy restricts memory names to `FinancialAdvisorMemory-*`
(after internal ID generation). The name itself must match `[a-zA-Z][a-zA-Z0-9_]{0,47}`.
We use `FinancialAdvisorMemory` which generates an ID like `FinancialAdvisorMemory-abc123`.
In your own AWS account, you can use any valid name.

## Files

| File | Purpose |
|------|---------|
| `3-agentcore-memory.py` | Creates memory, stores events, retrieves records |
| `3-create-test-request.py` | Queries existing memory interactively |
| `3-agentcore-memory.md` | This walkthrough |
