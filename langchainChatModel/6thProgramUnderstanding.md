# LangGraph Program 5: State Persistence & Memory Architecture

## Program Goals
Master the core concepts of multi-turn conversational agents in LangGraph:
- [x] `MemorySaver`
- [x] Checkpointers
- [x] `thread_id`
- [x] Persistent Conversations
- [x] Multi-turn Chat
- [x] Production Memory Architecture
- [x] Why LangGraph is architecturally superior for stateful workflows

---

## 1. Core Concept: Checkpointer

### Mental Model: The Game Save
Think of a checkpointer as a **Save Game** system:
```text
Save Progress ──► Exit Application ──► Return Later ──► Continue Exactly Where You Left Off
```

LangGraph manages graph execution state identically:

### Without Checkpointer
Each graph execution starts with a clean slate; no memory travels across invocations:
```text
Graph Run 1 ──► [Completed] ──► State Lost ❌
Graph Run 2 ──► [Completed] ──► State Lost ❌
Graph Run 3 ──► [Completed] ──► No history preserved across runs.
```

### With Checkpointer
State transitions are captured at each step and persisted:
```text
Graph Run 1
     │
     ▼
State Saved to Checkpoint
     │
     ▼
Graph Run 2
     │
     ▼
Loads Existing History ──► Continues Conversation Seamlessly ✅
```

---

## 2. Core Concept: `thread_id`

When thousands of users interact with an agent concurrently:
- Hari is asking questions.
- Ravi is troubleshooting an issue.
- Kumar is booking an appointment.

How does LangGraph retrieve the right history for the right user?

Using a unique **`thread_id`**:
```python
# Session or user-scoped identifiers:
thread_id = "hari-chat"
# or
thread_id = "user-123"
```

### Context Isolation
```text
thread_id = "hari" ──► Isolated History A (Hari's messages only)

thread_id = "ravi" ──► Isolated History B (Ravi's messages only)
```

---

## 3. Complete Program 5 Code

```python
"""
==========================================================
PROGRAM 5
LANGGRAPH MEMORY: CHECKPOINTER + THREAD ID
==========================================================

Concepts:
1. State
2. Messages
3. ChatGroq
4. MemorySaver
5. Checkpointer
6. thread_id
7. Persistent Chat
==========================================================
"""

from typing import Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# ==================================================
# 1. LOAD ENV & INITIALIZE MODEL
# ==================================================
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# ==================================================
# 2. STATE DEFINITION
# ==================================================
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

# ==================================================
# 3. CHATBOT NODE
# ==================================================
def chatbot(state: ChatState):
    print("\nNode Running...")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ==================================================
# 4. GRAPH TOPOLOGY
# ==================================================
builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# ==================================================
# 5. MEMORY CHECKPOINTER & COMPILATION
# ==================================================
# MemorySaver stores graph checkpoints in memory between executions
memory = MemorySaver()

# Compiling with checkpointer enables persistence
graph = builder.compile(checkpointer=memory)

# ==================================================
# 6. THREAD CONFIGURATION
# ==================================================
# Unique thread identifier mapping to this user's state
config = {
    "configurable": {
        "thread_id": "hari-chat"
    }
}

# ==================================================
# 7. FIRST CONVERSATION TURN
# ==================================================
result1 = graph.invoke(
    {
        "messages": [
            HumanMessage(content="My name is Hari.")
        ]
    },
    config=config
)

print("\nAI RESPONSE 1:")
print(result1["messages"][-1].content)

# ==================================================
# 8. SECOND CONVERSATION TURN (RECALLS PRIOR STATE)
# ==================================================
result2 = graph.invoke(
    {
        "messages": [
            HumanMessage(content="What is my name?")
        ]
    },
    config=config
)

print("\nAI RESPONSE 2:")
print(result2["messages"][-1].content)
```

---

## 4. Execution Lifecycle: What Happens Internally?

### Request 1: Introduction
1. User provides: `"My name is Hari."`
2. Initial State:
   ```python
   [HumanMessage("My name is Hari.")]
   ```
3. AI generates: `"Nice to meet you, Hari."`
4. **Checkpoint Saved ✅** (Associated with `thread_id: "hari-chat"`).

### Request 2: Querying Prior Context
1. User provides: `"What is my name?"`
2. **Without Checkpointer**: Model only sees `"What is my name?"` and responds: `"I do not know your name."` ❌
3. **With `MemorySaver`**:
   - LangGraph inspects `thread_id: "hari-chat"`.
   - Hydrates previous state:
     ```python
     [
         HumanMessage("My name is Hari."),
         AIMessage("Nice to meet you, Hari.")
     ]
     ```
   - Appends the new turn via `add_messages`:
     ```python
     [
         HumanMessage("My name is Hari."),
         AIMessage("Nice to meet you, Hari."),
         HumanMessage("What is my name?")
     ]
     ```
   - Passes the full conversational context to the LLM.
4. AI generates: `"Your name is Hari."` ✅

---

## 5. Multi-User Session Isolation

```text
thread_id = "hari-chat"
│
└── History: [HumanMessage("My name is Hari"), AIMessage("Hi Hari")]

thread_id = "ravi-chat"
│
└── History: [HumanMessage("My name is Ravi"), AIMessage("Hi Ravi")]
```

LangGraph matches incoming calls directly to the correct isolated history ledger based on the supplied `thread_id`.

---

## 6. Development vs. Production Checkpointers

> [!WARNING]
> `MemorySaver()` stores snapshots in **volatile RAM**. When the Python process restarts, all conversation history is wiped.

### Production Persistence
Production systems replace `MemorySaver` with durable, external storage backends without modifying graph logic:

| Environment | Checkpointer | Storage Medium |
|---|---|---|
| **Development / Testing** | `MemorySaver()` | In-memory RAM (Ephemeral) |
| **Production Scale** | `PostgresSaver` / `AsyncPostgresSaver` | PostgreSQL Database |
| **Low-Latency Caching** | Redis Checkpointer | Redis Store |
| **Document/NoSQL** | MongoDBSaver / DynamoDBSaver | Document Datastores |

### Runtime Architecture Diagram
```text
User Input
    │
    ▼
LangGraph Engine
    │
    ▼
Lookup Checkpoint via thread_id
    │
    ▼
Hydrate Prior Messages from Checkpointer
    │
    ▼
ChatGroq Node (LLM Inference)
    │
    ▼
Generate Assistant Response
    │
    ▼
Save Updated State Checkpoint (Postgres/Redis/RAM)
```

---

## 7. Key Interview Preparation

### Question:
> **Why do we use `thread_id` in LangGraph?**

### Answer:
> A `thread_id` acts as the unique partition key for a conversation session. LangGraph uses it to query the checkpointer, automatically loading the correct conversational history into State before node execution and persisting the updated state once the graph reaches an `END` edge.

---

## 8. Program 6: The Next Step in Architecture

With state persistence mastered, the next milestone combines **Memory**, **Tools**, and **Agents**:

```text
User Input
    │
    ▼
Load Memory (Checkpointer)
    │
    ▼
Agent Reasoning Node
    │
    ▼
Conditional Edge: Need Tool?
 ├── YES ──► Tool Call ──► Tool Result ──► Return to Agent
 └── NO  ──► Final Answer
    │
    ▼
Commit Updated History to Checkpointer
    │
    ▼
Return Response to User
```

This pattern serves as the structural foundation for modern enterprise agents, multi-turn reasoning loops, and production Retrieval-Augmented Generation (RAG) systems.