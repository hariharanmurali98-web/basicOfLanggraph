# Moving Message State Toward Production

## Use the built-in `MessagesState`

LangGraph includes a prebuilt state with a message field. Extend it with application-specific fields:

```python
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    user_id: str
    documents: list[str]
```

## Message ID behavior

`add_messages` does more than append: when an incoming message has the same ID as an existing message in state, it replaces that message rather than duplicating it. This can be useful when updating messages, including streaming and tool-call workflows.

## Context trimming

Models have token limits. Before `llm.invoke()`, production nodes can pass messages through `trim_messages()` to control context size and avoid context-window overflow.

## Core message-state pattern

The reducer-managed pattern is:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

`add_messages` merges new node-returned messages into the existing conversation rather than replacing the full list. For the full walkthrough, examples, and interview summary, see [2ndbasicLanggraphExplanation.md](2ndbasicLanggraphExplanation.md).

For the related production memory architecture—including thread IDs, storage layers, sliding windows, summaries, and `trim_messages()`—see [healthCareBasicChatBot/prodchatBotTipsGuide.md](healthCareBasicChatBot/prodchatBotTipsGuide.md).