from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Literal
import random


# ==========================================================
# LANGGRAPH FUNDAMENTALS
# ==========================================================

# A Graph represents a workflow.
#
# The workflow consists of:
# 1. State   -> Shared data that flows through the graph
# 2. Nodes   -> Units of work that process the state
# 3. Edges   -> Connections that determine execution flow
#
# Every LangGraph workflow starts from START
# and eventually reaches END.


# ==========================================================
# STATE DEFINITION
# ==========================================================

# State is the shared memory of the graph.
#
# State is passed from one node to another.
#
# Every node can:
# - Read current state
# - Update state
# - Return state updates
#
# TypedDict defines the structure/schema of the state.

class JourneyState(TypedDict):
    current_location: str


# ==========================================================
# NODES
# ==========================================================

# Nodes are the building blocks of a graph.
#
# A node can be:
# - A Python function
# - An LLM call
# - A Tool call
# - An Agent
# - Any processing step
#
# Every node receives the current state.
# Every node returns updates to the state.


# --------------------------
# COIMBATORE NODE
# --------------------------

def coimbatore(state: JourneyState) -> JourneyState:

    print("\nStarting journey from Coimbatore")

    print("Incoming State:", state)

    # Return updated state
    return {
        "current_location": "Departed from Coimbatore"
    }


# --------------------------
# TRICHY NODE
# --------------------------

def trichy(state: JourneyState) -> JourneyState:

    print("\nArrived at Trichy")

    print("Incoming State:", state)

    return {
        "current_location": "Visited Trichy"
    }


# --------------------------
# SALEM NODE
# --------------------------

def salem(state: JourneyState) -> JourneyState:

    print("\nArrived at Salem")

    print("Incoming State:", state)

    return {
        "current_location": "Visited Salem"
    }


# ==========================================================
# CONDITIONAL ROUTING FUNCTION
# ==========================================================

# This function is used by a Conditional Edge.
#
# A Conditional Edge allows the graph to dynamically decide
# which node should run next based on the current state.
#
# Return value determines the next node.
#
# Possible returns:
# - "trichy"
# - "salem"

def decide_intermediate_city(
        state: JourneyState
) -> Literal["trichy", "salem"]:

    print(
        f"\nDeciding route based on state: "
        f"{state['current_location']}"
    )

    if random.random() < 0.5:

        print("-> Route Selected: Trichy")

        return "trichy"

    else:

        print("-> Route Selected: Salem")

        return "salem"


# ==========================================================
# CREATE THE GRAPH
# ==========================================================

# StateGraph is used to create a graph workflow.
#
# It manages:
# - Nodes
# - Edges
# - State flow

builder = StateGraph(JourneyState)


# ==========================================================
# ADD NODES
# ==========================================================

# Syntax:
#
# builder.add_node(
#     "node_name",
#     function_name
# )

builder.add_node("coimbatore", coimbatore)

builder.add_node("trichy", trichy)

builder.add_node("salem", salem)


# ==========================================================
# ADD EDGES
# ==========================================================

# Edges define how execution moves
# from one node to another.


# --------------------------
# START --> COIMBATORE
# --------------------------

# Every graph execution starts at START.

builder.add_edge(START, "coimbatore")


# --------------------------
# CONDITIONAL EDGE
# --------------------------

# After Coimbatore executes,
# LangGraph calls decide_intermediate_city().
#
# Based on the returned value:
#
# "trichy" -> execute Trichy node
#
# "salem" -> execute Salem node
#
# This allows dynamic routing.

builder.add_conditional_edges(
    "coimbatore",
    decide_intermediate_city
)


# --------------------------
# TRICHY --> END
# --------------------------

builder.add_edge("trichy", END)


# --------------------------
# SALEM --> END
# --------------------------

builder.add_edge("salem", END)


# ==========================================================
# COMPILE GRAPH
# ==========================================================

# compile()
#
# Converts graph definition into
# an executable graph object.
#
# Think of it like:
#
# Design Phase ---> Executable Phase

graph = builder.compile()


# ==========================================================
# EXECUTE GRAPH
# ==========================================================

# invoke()
#
# Runs the complete graph.
#
# Input:
# Initial State
#
# Output:
# Final State

print("\nExecuting Graph...\n")

result = graph.invoke(
    {
        "current_location": "Home"
    }
)


# ==========================================================
# FINAL RESULT
# ==========================================================

print("\nFinal State:")

print(result)


# ==========================================================
# VISUALIZE GRAPH
# ==========================================================

# Mermaid representation of graph

print("\nGraph Structure:\n")

print(graph.get_graph().draw_mermaid())


# Save graph as PNG image
# (Optional)

try:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("journey_graph.png", "wb") as f:
        f.write(png_data)

    print("\nGraph image saved as journey_graph.png")

except Exception as e:

    print(
        "\nCould not generate PNG."
        "\nInstall required visualization dependencies."
    )

    print("Reason:", e)

