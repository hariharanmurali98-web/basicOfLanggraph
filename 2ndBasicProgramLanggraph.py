"""
==========================================================
LANGGRAPH PROGRAM 1
MESSAGES STATE + add_messages
==========================================================

GOAL

Learn:

1. Why LangGraph uses messages
2. What Annotated does
3. What add_messages does
4. How messages flow through State
5. How nodes add new messages

NO LLM YET

We are focusing only on understanding
how message-based state works.

==========================================================
"""

# ==========================================================
# IMPORTS
# ==========================================================

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

# add_messages is a special reducer
#
# It tells LangGraph:
#
# "When a node returns new messages,
# append them instead of replacing
# the old messages."

from langgraph.graph.message import add_messages

# Message objects

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

# ==========================================================
# STATE
# ==========================================================

"""
Most beginner examples use:

class State(TypedDict):
    question: str

Production chat systems use:

class State(TypedDict):
    messages: ...

Why?

Because conversations are made of:

HumanMessage
AIMessage
SystemMessage

instead of plain strings.
"""

class ChatState(TypedDict):

    messages: Annotated[
        list,
        add_messages
    ]

# ==========================================================
# NODE
# ==========================================================

"""
This node simulates a chatbot.

Current Flow:

HumanMessage
      ↓
chatbot()
      ↓
AIMessage

Later:

HumanMessage
      ↓
ChatGroq
      ↓
AIMessage

For now we'll manually create
the AI response.
"""

def chatbot(state: ChatState):

    print("\nNode Executing...")
    print("Incoming Messages:\n")

    # Print every incoming message

    for msg in state["messages"]:

        print(
            f"{msg.__class__.__name__}: "
            f"{msg.content}"
        )

    # Simulated AI response

    return {
        "messages": [

            AIMessage(
                content=
                "Hello! I am a future LangGraph chatbot."
            )

        ]
    }

# ==========================================================
# CREATE GRAPH
# ==========================================================

builder = StateGraph(ChatState)

# Add node

builder.add_node(
    "chatbot",
    chatbot
)

# ==========================================================
# FLOW
# ==========================================================

"""
START
  |
  v
chatbot
  |
  v
END
"""

builder.add_edge(
    START,
    "chatbot"
)

builder.add_edge(
    "chatbot",
    END
)

# ==========================================================
# COMPILE
# ==========================================================

graph = builder.compile()

# ==========================================================
# EXECUTE
# ==========================================================

"""
Initial state contains:

HumanMessage

In production this comes from:

User
 ↓
API
 ↓
LangGraph
"""

result = graph.invoke(

    {
        "messages": [

            HumanMessage(
                content=
                "Hi, I want to learn LangGraph."
            )

        ]
    }

)

# ==========================================================
# FINAL STATE
# ==========================================================

print("\n")
print("=" * 60)
print("FINAL STATE")
print("=" * 60)

# Let's inspect messages

for message in result["messages"]:

    print(
        f"\n{message.__class__.__name__}"
    )

    print(message.content)


try:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("2ndChatgraph.png", "wb") as f:
        f.write(png_data)

    print("\nGraph image saved as journey_graph.png")

except Exception as e:

    print(
        "\nCould not generate PNG."
        "\nInstall required visualization dependencies."
    )

    print("Reason:", e)