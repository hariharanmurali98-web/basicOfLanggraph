What Happens Internally?
Step 1

User asks:

Plain Text
What is 500 multiplied by 300?

State:

Python
[
HumanMessage(...)
]
Step 2

Agent Node

Python
response = llm_with_tools.invoke(
messages
)

Model examines available tools.

It sees:

Python
multiply()
Step 3

Instead of answering directly

Model returns:

Python
AIMessage(
tool_calls=[
...
]
)

Example:

Plain Text
Call multiply
a=500
b=300
Step 4

Router

Python
if last_message.tool_calls:

returns:

Python
"tools"

Graph moves to:

Plain Text
ToolNode
Step 5

ToolNode executes:

Python
multiply(
a=500,
b=300
)

Returns:

Plain Text
150000
Step 6

Tool result added to messages

Python
ToolMessage(
content="150000"
)
Step 7

Back to Agent

Python
tools
│
▼
 
agent

Agent now sees:

Plain Text
User Question
 
Tool Result
 
150000
Step 8

Final response

Plain Text
500 multiplied by 300 equals 150000.
Production Understanding

This loop:

Plain Text
Agent
│
▼
 
Tool
 
│
▼
 
Agent

is the foundation of:

Plain Text
ChatGPT Tools
Claude Tools
LangGraph Agents
 
RAG Agents
 
Web Search Agents
 
Database Agents
 
SQL Agents
 
Code Agents
What You Must Understand Before Program 5

Understand these perfectly:

Tool
Python
@tool
Tool Registration
Python
tools = [...]
bind_tools()
Python
llm.bind_tools()
ToolNode
Python
ToolNode(tools)
tool_calls
Python
last_message.tool_calls
Agent Loop
Plain Text
Agent
↓
Tool
↓
Agent
Program 5

Next, build a Production Chat Agent with Memory:

Plain Text
HumanMessage
↓
 
Agent
 
↓
 
Tool Calls
 
↓
 
MemorySaver
 
↓
 
thread_id
 
↓
 
Conversation History
 
↓
 
Answer