"""
5thProgramCallsExternalWebSearch.py
==========================================================
Clean LangGraph tool integration with real-time logs,
hard thread-level search timeouts, and Groq API timeouts.
==========================================================
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Annotated, Sequence
from dotenv import load_dotenv

from ddgs import DDGS
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()


# ==========================================================
# 1. DEFINE SEARCH TOOL WITH HARD THREAD TIMEOUT
# ==========================================================
def _raw_ddgs_call(query: str, max_results: int = 3):
    """Isolated scraper call to run inside a worker thread."""
    return DDGS(timeout=5).text(query, max_results=max_results)


@tool
def web_search(query: str) -> str:
    """Search the public internet using DuckDuckGo to find up-to-date facts, news, and details."""
    SEARCH_TIMEOUT_SECONDS = 6.0
    print(f"\n  [TOOL RUNNING] Web search started for: '{query}' (Max wait: {SEARCH_TIMEOUT_SECONDS}s)")
    start_t = time.time()

    # Run network request inside an executor with a hard deadline
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_raw_ddgs_call, query, 3)
        try:
            results = future.result(timeout=SEARCH_TIMEOUT_SECONDS)
            duration = round(time.time() - start_t, 2)

            if not results:
                print(f"  [TOOL COMPLETE] Search finished in {duration}s — No results found.")
                return "No search results found."

            print(f"  [TOOL COMPLETE] Search finished in {duration}s — Found {len(results)} items.")
            formatted = []
            for r in results:
                formatted.append(
                    f"Title: {r.get('title', '')}\n"
                    f"Snippet: {r.get('body', '')}\n"
                    f"Link: {r.get('href', '')}"
                )
            return "\n\n".join(formatted)

        except FutureTimeout:
            duration = round(time.time() - start_t, 2)
            print(f"  [TOOL TIMEOUT] Search aborted after {duration}s! Falling back to LLM internal knowledge.")
            return "Search request timed out. Please answer using your existing knowledge or state that search is unavailable."

        except Exception as e:
            duration = round(time.time() - start_t, 2)
            print(f"  [TOOL ERROR] Failed after {duration}s: {e}")
            return f"Search error occurred: {str(e)}"


tools = [web_search]

# ==========================================================
# 2. MODEL & GRAPH SETUP WITH API TIMEOUT
# ==========================================================
print("[INIT] Connecting to ChatGroq with a 15-second request timeout...")
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.0,
    request_timeout=15.0,  # Fails fast if Groq API network socket freezes
    max_retries=1,
)
llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def chatbot(state: AgentState) -> dict:
    step_num = len(state["messages"])
    print(f"\n[NODE: CHATBOT] Submitting {step_num} message(s) to Groq...")
    start_t = time.time()

    try:
        response = llm_with_tools.invoke(state["messages"])
        duration = round(time.time() - start_t, 2)

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_names = [call["name"] for call in response.tool_calls]
            print(f"[NODE: CHATBOT] Done in {duration}s -> Model requested tools: {tool_names}")
        else:
            print(f"[NODE: CHATBOT] Done in {duration}s -> Model generated final text.")

        return {"messages": [response]}

    except Exception as e:
        print(f"[NODE: CHATBOT] Groq request failed or timed out: {e}")
        raise e


tool_node = ToolNode(tools)

builder = StateGraph(AgentState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

graph = builder.compile()

# ==========================================================
# 3. RUN WITH NODE-BY-NODE STREAMING & STEP LIMITS
# ==========================================================
if __name__ == "__main__":
    test_query = "What are the latest updates on space exploration this week?"
    print(f"\n>>> Starting Graph Execution for Query: '{test_query}'")
    print("-" * 65)

    initial_input = {"messages": [HumanMessage(content=test_query)]}

    # config={"recursion_limit": 6} prevents infinite ping-pong between chatbot and tools
    config = {"recursion_limit": 6}

    for output in graph.stream(initial_input, config=config):
        for node_name, state_update in output.items():
            print(f">>> [GRAPH STATUS] Finished step: '{node_name}'")

            # Print final assistant text as soon as the terminal chatbot step finishes
            if node_name == "chatbot":
                latest_msg = state_update["messages"][-1]
                if not getattr(latest_msg, "tool_calls", None) and latest_msg.content:
                    print("\n" + "=" * 65)
                    print("FINAL ASSISTANT RESPONSE")
                    print("=" * 65)
                    print(latest_msg.content)