"""
==========================================================
PROGRAM 5
LANGGRAPH MEMORY
CHECKPOINTER + THREAD ID
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

# ==================================================
# IMPORTS
# ==================================================

from dotenv import load_dotenv

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.graph.message import (
    add_messages
)

# Memory Checkpointer

from langgraph.checkpoint.memory import (
    MemorySaver
)

from langchain_core.messages import (
    HumanMessage
)

from langchain_groq import (
    ChatGroq
)

# ==================================================
# LOAD ENV
# ==================================================

load_dotenv()

# ==================================================
# MODEL
# ==================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# ==================================================
# STATE
# ==================================================

class ChatState(TypedDict):

    messages: Annotated[
        list,
        add_messages
    ]

# ==================================================
# CHATBOT NODE
# ==================================================

def chatbot(state: ChatState):

    print("\nNode Running...")

    response = llm.invoke(
        state["messages"]
    )

    return {
        "messages": [
            response
        ]
    }

# ==================================================
# GRAPH
# ==================================================

builder = StateGraph(
    ChatState
)

builder.add_node(
    "chatbot",
    chatbot
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_edge(
    "chatbot",
    END
)

# ==================================================
# MEMORY SAVER
# ==================================================

"""
Stores graph state
between executions.
"""

memory = MemorySaver()

# ==================================================
# COMPILE
# ==================================================

graph = builder.compile(
    checkpointer=memory
)

# ==================================================
# THREAD CONFIG
# ==================================================

"""
Every user/session
needs a unique thread_id.
"""

config = {

    "configurable": {

        "thread_id":
        "hari-chat"

    }

}

# ==================================================
# FIRST MESSAGE
# ==================================================

result1 = graph.invoke(

    {
        "messages": [

            HumanMessage(
                content=
                "My name is Hari."
            )

        ]
    },

    config=config
)

print("\nAI RESPONSE 1:")
print(
    result1["messages"][-1]
    .content
)

# ==================================================
# SECOND MESSAGE
# ==================================================

result2 = graph.invoke(

    {
        "messages": [

            HumanMessage(
                content=
                "What is my name?"
            )

        ]
    },

    config=config
)

print("\nAI RESPONSE 2:")
print(
    result2["messages"][-1]
    .content
)