from langchain_community.tools.tavily_search import TavilySearchResults

# 1. Instantiate an external search tool (requires TAVILY_API_KEY)
web_search_tool = TavilySearchResults(max_results=3)

# 2. Add it to your graph's tools list
tools = [calculate, get_weather, web_search_tool]

# 3. Bind to model and ToolNode
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

Key Details
No API Key Required: DuckDuckGoSearchRun queries the public web directly via HTTP without requiring registration or authentication headers.

Granular Snippet Control: If you need structured metadata (URLs, titles, snippets) rather than a single raw text string, swap DuckDuckGoSearchRun with DuckDuckGoSearchResults:

Python
from langchain_community.tools import DuckDuckGoSearchResults
web_search = DuckDuckGoSearchResults(max_results=3)
Rate Limits: Because DuckDuckGo is free and unauthenticated, sending high-concurrency requests or rapid automated loops can trigger rate limiting (HTTP 429 Ratelimit). For production architectures handling steady traffic, use dedicated search APIs like Tavily (TavilySearchResults) or SerpAPI.

## Related learning path

This tool setup follows the [production LangGraph roadmap](../langgraph_production_roadmap.md). For thread IDs, checkpointing, storage layers, and context trimming, see the [production conversation-memory guide](../healthCareBasicChatBot/prodchatBotTipsGuide.md).