# Production Conversation Memory Architecture

LangChain and LangGraph notes on storing conversation history, managing context, and structuring a production service.

## Big misconception beginners have

Many beginners store history in a Python list:

```python
conversation_history = []
```

This is useful for learning and small demos, but the source guide warns that a process-local list is unsuitable as production persistence because data is lost on restart, it cannot be shared across servers, history grows, token costs increase, and model context limits can be exceeded.

## Real production architecture

```text
[ Frontend Client ]
        │ (HTTP / WS)
        ▼
[ FastAPI App (Stateless) ]
        │ Load History
        ▼
[ Postgres / Redis ]
        │ Retrieve Messages
        ▼
[ Context Trimming ]
        ▼
[ Groq / OpenAI / Claude ]
        ▼
[ AI Response ]
        ▼
[ Save New Messages ]
        ▼
[ Postgres / Redis ]
```

> Backend APIs are usually stateless. Conversation state lives in a database or distributed cache.

## How chat history is stored

Each conversation receives an identifier, for example `thread_123`, `session_456`, or `user_999_chat_11`.

```python
session_id = "user_102_chat_456"
```

For each user question:

1. Fetch recent messages using `session_id`.
2. Convert stored data into message objects.
3. Send messages to the LLM.
4. Receive the response.
5. Persist both user and AI messages.

## LangGraph persistence by thread ID

LangGraph can restore graph state by thread ID instead of requiring application code to manually load and save each message:

```python
config = {"configurable": {"thread_id": "session-user-9823"}}
```

```python
response = await graph.ainvoke(
    {"messages": [HumanMessage(content=user_query)]},
    config=config
)
```

Internally: load prior conversation → reconstruct state → append new message → invoke model → update checkpoint.

## Conversation storage layers

| Storage | Purpose | Examples |
| --- | --- | --- |
| Permanent storage | Historical conversation archive | PostgreSQL, MongoDB, DynamoDB |
| Fast cache | Current active sessions | Redis |
| Long-term analytics | Reporting and compliance | Data warehouse |

## Context overflow

Sending every message on every model call can cause higher costs, higher latency, context-window overflow, and poor performance.

### Strategy 1: Sliding-window memory

Keep only recent messages. Example input:

```text
System Message
User Question 8
AI Response 8
User Question 9
AI Response 9
User Question 10
AI Response 10
```

Messages 1–7 are excluded. The guide suggests this for customer support, helpdesk agents, ticket systems, and FAQ bots.

### Strategy 2: Rolling summarization

Compress older conversation into a summary while keeping recent turns:

```text
Summary:
User previously discussed a home loan,
submitted salary proof, and requested EMI calculations.

Recent Messages:
21
22
23
24
25
```

The guide lists healthcare agents, financial advisors, legal assistants, and long-running conversations as use cases.

## LangChain message trimming

```python
from langchain_core.messages import trim_messages
```

```python
trimmer = trim_messages(
    max_tokens=2000,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human"
)
```

- `max_tokens` → maximum context size.
- `strategy="last"` → keep the most recent messages.
- `include_system` → preserve important instructions.
- `start_on="human"` → ensure valid conversation order.

## Database schema

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id VARCHAR(64),
    sender_type VARCHAR(20),
    content TEXT,
    tokens_used INT,
    created_at TIMESTAMP
);
```

Example `sender_type` values: `system`, `human`, `ai`.

## Data flow

```text
User Message
  ↓
Load Previous Messages
  ↓
Convert to HumanMessage / AIMessage
  ↓
Add Current User Message
  ↓
Trim Messages
  ↓
Send to LLM
  ↓
Receive AIMessage
  ↓
Persist New Messages
  ↓
Return Response
```

## Production service layer

1. User sends request.
2. API receives request.
3. Load chat history.
4. Create LangChain messages.
5. Trim context.
6. Invoke LLM.
7. Save messages.
8. Return response.

## Interview notes

- **Beginner approach:** `messages = []`
- **Production concerns:** thread ID, database, checkpointing, memory management, and message trimming.
- **Important concepts:** HumanMessage, AIMessage, SystemMessage, State, Checkpointer, Thread ID, Persistence, Redis, PostgreSQL, and context-window management.

## Final revision summary

- Do not use a process-local Python list as the only production chat-history store.
- Store messages using `thread_id` or `session_id`.
- Use Redis for active memory and PostgreSQL for durable storage (as suggested in this guide).
- Use LangGraph checkpointers for persistence.
- Trim messages before every LLM call.
- Keep SystemMessage permanently in the prompt context.
- Use summaries for very long conversations.
- Convert database rows back into HumanMessage, AIMessage, and SystemMessage objects before invoking the model.

> **Implementation note:** The source guide's architectural recommendations are high-level. Choose storage, retention, access controls, and trimming policies based on your application's actual reliability, privacy, and compliance needs.
