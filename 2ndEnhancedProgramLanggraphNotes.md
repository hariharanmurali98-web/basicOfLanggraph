What to Add When Moving to Real Production
Use Built-in MessagesState: LangGraph includes a pre-built state class that already implements this:

Python
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    user_id: str
    documents: list[str]
Message ID Deduplication: add_messages doesn't just append—if an incoming message has the same id as an existing message in state, it overwrites that message in place instead of duplicating it (crucial for streaming tokens and tool call adjustments).

Context Trimming: Real models have token limits. Before llm.invoke(), production nodes pass messages through trim_messages() to avoid context window blowouts.