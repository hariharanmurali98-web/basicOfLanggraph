# LangGraph Revision Guide

Connecting fundamental LLM primitives to graph-driven, stateful workflows.

## Foundations check

Already covered: ChatGroq, `invoke()`, HumanMessage, AIMessage, SystemMessage, message history, and why production systems should not keep conversation state only in Python lists.

## The core concept: State

State is a **shared notebook** that travels through the graph. Every node can read it, modify it, and return updates.

```text
Node A → Node B → Node C
```

### Before LangGraph

```python
response = llm.invoke([HumanMessage(content="What is RAG?")])
```

`Question → LLM → Answer`

### LangGraph flow

`Question → State → Node 1 → Node 2 → Node 3 → Answer`

> **Key architectural shift:** The LLM is one part of a larger workflow, rather than the entire application wrapper.

## Concept 1: State

State holds the structured schema shared by components.

### Minimal state

```python
from typing import TypedDict

class State(TypedDict):
    question: str

state = {"question": "What is RAG?"}
```

### More realistic state

```python
from typing import TypedDict

class State(TypedDict):
    question: str
    answer: str

state = {"question": "What is LangGraph?", "answer": ""}
```

Without shared State, one node does not know what another did. With State, nodes can exchange information through updates.

## Concept 2: Nodes

A node is usually a Python function that consumes current state and returns changes.

```python
def chatbot(state):
    state["answer"] = "LangGraph is used for AI workflows."
    return state
```

`State → chatbot() → Updated State`

## Concept 3: StateGraph

`StateGraph` is the workflow blueprint.

```python
from langgraph.graph import StateGraph

graph_builder = StateGraph(State)
```

Define a node on the blueprint:

```python
from typing import TypedDict
from langgraph.graph import StateGraph

class State(TypedDict):
    question: str
    answer: str

def chatbot(state):
    state["answer"] = "LangGraph is a framework for AI workflows."
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
```

## Concept 4: START and END

Every workflow has an explicit entry and exit:

```python
from langgraph.graph import START, END

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
```

`START → chatbot → END`

## Complete first LangGraph program

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    answer: str

def chatbot(state):
    state["answer"] = f"You asked: {state['question']}"
    return state

graph_builder = StateGraph(State)       # 1. Blueprint
graph_builder.add_node("chatbot", chatbot)  # 2. Node
graph_builder.add_edge(START, "chatbot")    # 3. Edges
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()             # 4. Compile

result = graph.invoke({                     # 5. Invoke
    "question": "What is LangGraph?",
    "answer": ""
})
print(result)
```

Output:

```python
{'question': 'What is LangGraph?', 'answer': 'You asked: What is LangGraph?'}
```

## Real LangGraph with ChatGroq

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-20b")

def chatbot(state):
    response = llm.invoke(state["question"])
    return {"answer": response.content}
```

## Common production state: messages

Instead of separate question/answer strings, graphs can hold a message stream:

```python
from typing import TypedDict
from langchain_core.messages import BaseMessage

class State(TypedDict):
    messages: list[BaseMessage]
```

This is the foundation for chatbots, agents, memory, and multi-agent systems.

```python
state = {"messages": [HumanMessage(content="Hello")]}

def chatbot(state):
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state
```

HumanMessage, AIMessage, and SystemMessage are important because LangGraph commonly passes sequences of these message types through state.

## What to learn next

1. `TypedDict` — define structured State schemas.
2. Nodes — write update functions such as `chatbot(state)`.
3. `START` — designate the entry point.
4. `END` — designate the exit point.
5. `StateGraph` — instantiate the blueprint.
6. `compile()` — prepare the executable graph.
7. `graph.invoke()` — execute with initial state.

```text
State with Messages → Chatbot Graph → Memory → Checkpointer → thread_id → Production LangGraph
```

This leads to checkpointer architectures, multi-tenant thread persistence, and production backends such as Postgres and Redis.
