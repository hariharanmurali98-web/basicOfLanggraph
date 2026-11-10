"""
======================================================
PROGRAM 3
LANGGRAPH TOOL CALLING FUNDAMENTALS
======================================================

Concepts Covered:

1. State
2. Messages
3. Tool Result Storage
4. Conditional Routing
5. Agent Node
6. Tool Node

======================================================
"""

# ==================================================
# IMPORTS
# ==================================================

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

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

# ==================================================
# STATE
# ==================================================

"""
Production states often contain:

messages
tool_results
metadata

etc.
"""

class AgentState(TypedDict):

    messages: Annotated[
        list,
        add_messages
    ]

    tool_result: str


# ==================================================
# TOOL
# ==================================================

"""
A Tool is simply a Python function.

Later:
- Weather APIs
- Search APIs
- Database Queries
- Vector DB Retrieval

All become tools.
"""

def weather_tool():

    print("\nWeather Tool Running...")

    return "Current Chennai temperature is 32°C"


# ==================================================
# AGENT NODE
# ==================================================

"""
Agent analyzes user request.

Then decides:

Should I call a tool?

or

Respond directly?
"""

def agent(state: AgentState):

    last_message = state["messages"][-1]

    print(
        "\nAgent examining:",
        last_message.content
    )

    return {}


# ==================================================
# ROUTING LOGIC
# ==================================================

"""
Conditional Edge Router

Decides next node.

In production:

LLM often decides.
"""

def router(state: AgentState):

    user_query = (
        state["messages"][-1]
        .content
        .lower()
    )

    if "weather" in user_query:

        print(
            "\nDecision: Call Weather Tool"
        )

        return "weather_node"

    print(
        "\nDecision: Direct Response"
    )

    return "final_response"


# ==================================================
# WEATHER TOOL NODE
# ==================================================

def weather_node(
        state: AgentState
):

    result = weather_tool()

    return {

        "tool_result": result,

        "messages": [

            AIMessage(
                content=
                f"Tool Output: {result}"
            )

        ]
    }


# ==================================================
# FINAL RESPONSE NODE
# ==================================================

def final_response_node(
        state: AgentState
):

    return {

        "messages": [

            AIMessage(
                content=
                "No tool needed. Simple answer."
            )

        ]
    }


# ==================================================
# GRAPH
# ==================================================

builder = StateGraph(
    AgentState
)

builder.add_node(
    "agent",
    agent
)

builder.add_node(
    "weather_node",
    weather_node
)

builder.add_node(
    "final_response",
    final_response_node
)

# ==================================================
# FLOW
# ==================================================

builder.add_edge(
    START,
    "agent"
)

builder.add_conditional_edges(
    "agent",
    router
)

builder.add_edge(
    "weather_node",
    END
)

builder.add_edge(
    "final_response",
    END
)

graph = builder.compile()

# ==================================================
# EXECUTION
# ==================================================

result = graph.invoke(

    {
        "messages": [
            HumanMessage(
                content=
                "What is the weather in Chennai?"
            )
        ],

        "tool_result": ""
    }

)

# ==================================================
# OUTPUT
# ==================================================

print("\n")
print("=" * 50)
print("FINAL MESSAGES")
print("=" * 50)

for msg in result["messages"]:

    msg.pretty_print()

print("\nStored Tool Result:")
print(
    result["tool_result"]
)