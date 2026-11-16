"""LangGraph tool calling with MessagesState and built-in routing.

This example demonstrates how `tools_condition` routes an AI tool call to
`ToolNode`, then loops the tool result back to the model for a final answer.
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


load_dotenv()


# 1. Define a Python function and expose it as an LLM-callable tool.
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return their product."""
    return a * b


# Keep the same tool list for model binding and ToolNode execution.
tools = [multiply]


# A bound model can request tools; it does not execute them itself.
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to the .env file or environment."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)


# MessagesState provides a `messages` field with LangGraph's message reducer.
def tool_calling_llm(state: MessagesState) -> dict[str, list]:
    """Ask the model to answer, or request a tool call."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ToolNode executes tool calls found in the most recent AIMessage.
tool_node = ToolNode(tools)


# 2. Assemble the graph.
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", tool_node)

builder.add_edge(START, "tool_calling_llm")

# tools_condition chooses "tools" when the last AI message has tool_calls;
# otherwise it chooses END. The mapping makes both destinations explicit.
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

# After tool execution, give the ToolMessage back to the model.
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile()


def run_query(query: str) -> None:
    """Run one request and print the conversation/tool trace."""
    print(f"\nUSER: {query}")
    result = graph.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"recursion_limit": 10},
    )

    for message in result["messages"]:
        print(f"\n[{message.__class__.__name__}]")
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print(f"Requested tool call(s): {tool_calls}")
        if message.content:
            print(message.content)


if __name__ == "__main__":
    run_query("What is 452 multiplied by 12? Please use the multiply tool.")
    run_query("In one sentence, what does this graph demonstrate?")
