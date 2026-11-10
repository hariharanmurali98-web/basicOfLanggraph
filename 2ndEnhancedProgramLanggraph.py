"""
==========================================================
LANGGRAPH: MESSAGES STATE & REDUCER PATTERN
==========================================================
Demonstrates how state stores message sequences and how
add_messages manages message appending and deduplication.
==========================================================
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

# ==========================================================
# 1. STATE DEFINITION
# ==========================================================
# In production, use Sequence[BaseMessage] instead of bare list.
# LangGraph also provides `from langgraph.graph import MessagesState`
# which defines this exact structure out of the box.


class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ==========================================================
# 2. NODE LOGIC
# ==========================================================
def chatbot(state: ChatState) -> dict:
    """Consumes current messages and returns an update."""
    incoming = state["messages"]
    print(f"\n[Node Executing] Processing {len(incoming)} incoming message(s):")

    for msg in incoming:
        role = msg.__class__.__name__
        print(f"  • {role}: {msg.content}")

    # Simulated model output
    response = AIMessage(
        content="Hello! I am a stateful LangGraph chatbot."
    )

    # Return only the key being updated; add_messages handles the merge
    return {"messages": [response]}


# ==========================================================
# 3. GRAPH CONSTRUCTION
# ==========================================================
builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()

# ==========================================================
# 4. EXECUTION
# ==========================================================
input_payload = {
    "messages": [
        HumanMessage(content="Hi, I want to learn LangGraph.")
    ]
}

result = graph.invoke(input_payload)

# ==========================================================
# 5. INSPECT FINAL STATE
# ==========================================================
print("\n" + "=" * 60)
print("FINAL CONVERSATION STATE")
print("=" * 60)

for message in result["messages"]:
    print(f"\n[{message.__class__.__name__}]")
    print(message.content)

# ==========================================================
# 6. VISUALIZATION EXPORT
# ==========================================================
OUTPUT_FILENAME = "chat_graph.png"

try:
    png_data = graph.get_graph().draw_mermaid_png()
    with open(OUTPUT_FILENAME, "wb") as f:
        f.write(png_data)
    print(f"\nGraph visualization saved successfully as '{OUTPUT_FILENAME}'.")
except Exception as e:
    print(
        f"\nVisualization could not be generated: {e}\n"
        "(Requires 'pygraphviz' or internet access for Mermaid rendering service)."
    )