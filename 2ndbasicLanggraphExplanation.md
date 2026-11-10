# LangGraph State Deep Dive

Mastering `Annotated`, reducer functions, and state merging behavior.

## Concept 1: Why `Annotated`?

```python
messages: Annotated[list, add_messages]
```

This combines a normal list with special LangGraph behavior. Without `Annotated`:

```python
messages: list
```

LangGraph treats this as a plain dictionary value; without a reducer, a new value overwrites the existing list instead of merging node updates.

## Concept 2: Why `add_messages`?

Suppose initial state contains:

```python
[HumanMessage(content="Hello")]
```

and a node returns:

```python
[AIMessage(content="Hi")]
```

- **Without `add_messages` (default overwrite):** `[AIMessage("Hi")]` — the old message is lost.
- **With `add_messages` (reducer):** `[HumanMessage("Hello"), AIMessage("Hi")]` — the old message is preserved.

## Concept 3: What happens internally?

Input state:

```python
{"messages": [HumanMessage(content="Hi")]}
```

Node update:

```python
{"messages": [AIMessage(content="Hello")]}
```

State after reducer merge:

```python
{"messages": [HumanMessage(content="Hi"), AIMessage(content="Hello")]}
```

## Concept 4: Why this matters

A common message-state pattern is:

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

It supports chatbots, agents, tool calling, RAG architectures, multi-agent systems, and memory/checkpointing.

```text
User → HumanMessage → State["messages"] → Node → AIMessage → add_messages → Updated State
```

## Interview takeaway

**Question:** Why use `Annotated[list, add_messages]` in LangGraph?

> `add_messages` acts as a reducer. Rather than replacing the existing messages list, it merges/appends new messages returned by nodes so conversation history is preserved across graph execution.

## Immediate next step: LangGraph + ChatGroq

```python
def chatbot(state):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

The reducer handles the merge, so returning the response update appends it to the message state.

## Additional production notes from the existing LangGraph notes

### Built-in `MessagesState`

LangGraph provides a prebuilt state with a message field. Extend it to add application data:

```python
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    user_id: str
    documents: list[str]
```

### Message IDs

`add_messages` can replace an existing message when an incoming message has the same ID, rather than creating a duplicate. This is useful for updating messages, including streaming/tool-call workflows.

### Context trimming

Models have token limits. Before invoking the model, production nodes may pass messages through `trim_messages()` to control context size. See [prodchatBotTipsGuide.md](healthCareBasicChatBot/prodchatBotTipsGuide.md) for the broader memory and trimming architecture.
