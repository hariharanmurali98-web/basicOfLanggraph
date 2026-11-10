"""
==========================================================
LANGGRAPH: TOOL CALLING WITH CHATGROQ & TOOLNODE
==========================================================
Demonstrates:
1. Tool creation using LangChain's `@tool` decorator
2. Binding tools to ChatGroq via `llm.bind_tools()`
3. Automated tool execution with LangGraph's `ToolNode`
4. Dynamic loop control via `tools_condition`
==========================================================
"""

import os
from typing import Annotated, Sequence
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()


# ==========================================================
# 1. TOOL DEFINITIONS
# ==========================================================
@tool
def calculate(expression: str) -> str:
    """Evaluate a standard mathematical expression string, such as '15 * 8' or '240 / 6'."""
    try:
        # A simple restricted evaluation for demonstration
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Unsupported characters in mathematical expression."
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Calculation failed: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """Look up current weather conditions and temperature for a given city."""
    # Simulated weather data lookup
    db = {
        "chennai": "32°C, Sunny with humid winds",
        "london": "14°C, Overcast and light rain",
        "new york": "20°C, Clear skies",
    }
    return db.get(city.strip().lower(), f"Weather data not found for {city}.")


tools = [calculate, get_weather]


# ==========================================================
# 2. MODEL BINDING
# ==========================================================
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.0,
)

# bind_tools equips the model with schemas to generate tool_calls
llm_with_tools = llm.bind_tools(tools)


# ==========================================================
# 3. STATE DEFINITION
# ==========================================================
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ==========================================================
# 4. GRAPH NODES
# ==========================================================
def chatbot(state: AgentState) -> dict:
    """Invokes the tool-aware model with current message history."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ToolNode executes the functions requested in state['messages'][-1].tool_calls
tool_node = ToolNode(tools)


# ==========================================================
# 5. GRAPH CONSTRUCTION & CONDITIONAL ROUTING
# ==========================================================
workflow = StateGraph(AgentState)

# Register the nodes
workflow.add_node("chatbot", chatbot)
workflow.add_node("tools", tool_node)

# Flow: START -> chatbot
workflow.add_edge(START, "chatbot")

# Conditional Edge:
# If chatbot returns tool_calls -> route to "tools"
# If chatbot returns plain text -> route to END
workflow.add_conditional_edges(
    "chatbot",
    tools_condition,
    {"tools": "tools", END: END},
)

# Loop edge: Once tools finish executing, return to chatbot
workflow.add_edge("tools", "chatbot")

graph = workflow.compile()


# ==========================================================
# 6. VERIFICATION RUNS
# ==========================================================
def run_query(user_query: str):
    print("\n" + "=" * 60)
    print(f"USER: {user_query}")
    print("=" * 60)

    result = graph.invoke(
        {"messages": [HumanMessage(content=user_query)]}
    )

    for msg in result["messages"]:
        role = msg.__class__.__name__
        print(f"\n[{role}]")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool Requested: {msg.tool_calls}")
        if msg.content:
            print(msg.content)


if __name__ == "__main__":
    # Test 1: Triggers weather tool
    run_query("What is the weather like in Chennai right now?")

    # Test 2: Triggers calculation tool
    run_query("What is 452 * 12?")

    # Test 3: Standard conversational turn (routes directly to END)
    run_query("Hello! What are you capable of doing?")


# Key Mechanics to NoticeDocstrings and Type Hints: @tool reads function parameter hints (city: str) and the function docstring. The docstring is the only reference the LLM uses to know when and how to use the tool.   tools_condition Mapping: Built-in router from langgraph.prebuilt. It inspects state["messages"][-1]. If tool_calls is present, it returns the string "tools", else it returns END.   Cyclic Connection: Notice workflow.add_edge("tools", "chatbot"). When the tool node finishes, it doesn't end the graph; it passes the tool result back into the model so the model can read it and formulate a natural language response.