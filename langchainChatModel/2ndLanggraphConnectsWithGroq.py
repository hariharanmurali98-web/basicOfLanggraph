"""
==========================================================
LANGGRAPH PROGRAM 2: REAL LLM NODE (ChatGroq)
==========================================================
Demonstrates connecting ChatGroq with:
1. MessagesState reducer pattern (add_messages)
2. Direct invocation using full message history
3. Merged state output via compiled graph
==========================================================
"""

import os
from typing import Annotated, Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# ==========================================================
# 1. ENVIRONMENT & LLM INITIALIZATION
# ==========================================================
# Make sure GROQ_API_KEY is defined in your .env file
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7,
)

# ==========================================================
# 2. STATE DEFINITION
# ==========================================================
class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ==========================================================
# 3. NODE LOGIC (REAL LLM CALL)
# ==========================================================
def chatbot(state: ChatState) -> dict:
    """
    Consumes entire message history from state, invokes the model,
    and returns a delta update containing the new AIMessage.
    """
    messages = state["messages"]

    # Optional: Prepend a SystemMessage if one isn't already present
    has_system = any(isinstance(m, SystemMessage) for m in messages)
    if not has_system:
        messages = [
            SystemMessage(content="You are a concise, helpful AI assistant.")
        ] + list(messages)

    # Invoke ChatGroq with the full conversation context
    ai_response = llm.invoke(messages)

    # Returning {"messages": [ai_response]} triggers `add_messages`
    # to automatically append it to the existing list in state
    return {"messages": [ai_response]}


# ==========================================================
# 4. GRAPH CONSTRUCTION
# ==========================================================
builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()

# ==========================================================
# 5. EXECUTION
# ==========================================================
initial_input = {
    "messages": [
        HumanMessage(content="Explain what a state reducer is in 2 sentences.")
    ]
}

print("Running graph with ChatGroq...\n")
result = graph.invoke(initial_input)

# ==========================================================
# 6. INSPECT FINAL STATE
# ==========================================================
print("=" * 60)
print("FINAL CONVERSATION STATE")
print("=" * 60)

for message in result["messages"]:
    role = message.__class__.__name__
    print(f"\n[{role}]")
    print(message.content)


# What Changed Under the Hood
# Full History Passed to LLM: llm.invoke(messages) receives the entire array of BaseMessage objects, enabling the model to see context from previous turns.

# Automatic Reducer Append: Because the node returns {"messages": [ai_response]}, add_messages appends the model's new AIMessage to the state without replacing the initial HumanMessage.

# System Prompt Injection: The node dynamically prepends a SystemMessage if missing, demonstrating how nodes can modify the payload sent to the LLM before execution.