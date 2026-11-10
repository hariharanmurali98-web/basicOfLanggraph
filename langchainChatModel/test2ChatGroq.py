"""
====================================================
CHATGROQ + LANGCHAIN COMPLETE BEGINNER PROGRAM
====================================================

TOPICS COVERED

1. python-dotenv
2. Environment Variables (.env)
3. ChatGroq Initialization
4. LLM Parameters
5. invoke()
6. Response Object
7. response.content
8. response.response_metadata
9. SystemMessage
10. HumanMessage
11. AIMessage
12. Message-Based Chat
13. pretty_print()
14. Chat History
15. LangGraph Preparation

====================================================
"""

# ==================================================
# IMPORTS
# ==================================================

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)

# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================
#
# Reads values from .env file
#
# Example:
#
# GROQ_API_KEY=gsk_xxxxxxxxxxxxx
#
# After loading, ChatGroq can automatically
# access the API key.
#

load_dotenv()

# ==================================================
# INITIALIZE CHAT MODEL
# ==================================================
#
# ChatGroq is a Chat Model.
#
# Chat Models work with:
#
# HumanMessage
# AIMessage
# SystemMessage
#
# Excellent for:
# - Chatbots
# - Agents
# - LangGraph
# - Conversational AI
#

llm = ChatGroq(

    # Model to use

    model="openai/gpt-oss-20b",

    # Controls creativity
    #
    # 0.0 = deterministic
    # 0.3 = focused
    # 0.7 = balanced
    # 1.0 = creative

    temperature=0.7,

    # Allow model to decide response length
    max_tokens=None,

    # Request timeout
    timeout=None,

    # Retry failed requests
    max_retries=2
)

print("\n" + "=" * 60)
print("EXAMPLE 1 : SIMPLE STRING INPUT")
print("=" * 60)

# ==================================================
# SIMPLE INVOKE
# ==================================================
#
# invoke()
#
# Sends prompt to the model.
#
# Flow:
#
# String
#   ↓
# ChatGroq
#   ↓
# AIMessage
#

response = llm.invoke(
    "Explain RAG in simple terms."
)

print("\nTYPE OF RESPONSE:")
print(type(response))

print("\nFULL RESPONSE OBJECT:")
print(response)

print("\nCONTENT ONLY:")
print(response.content)

print("\nRESPONSE METADATA:")
print(response.response_metadata)

print("\n" + "=" * 60)
print("EXAMPLE 2 : MESSAGE-BASED CHAT")
print("=" * 60)

# ==================================================
# MESSAGE OBJECTS
# ==================================================
#
# SystemMessage
# HumanMessage
#
# Chat Models understand roles.
#

messages = [

    SystemMessage(
        content="""
You are a Senior GenAI Mentor.

Explain concepts simply.

Give beginner-friendly examples.
"""
    ),

    HumanMessage(
        content="What should I learn first for GenAI Engineering?"
    )
]

response = llm.invoke(messages)

print("\nAI RESPONSE:")
print(response.content)

print("\nPRETTY PRINT:")
response.pretty_print()

print("\n" + "=" * 60)
print("EXAMPLE 3 : CHAT HISTORY")
print("=" * 60)

# ==================================================
# CHAT HISTORY
# ==================================================
#
# Conversations are stored as messages.
#
# LangGraph later stores these
# messages inside State.
#

messages = [

    SystemMessage(
        content="You are a GenAI Tutor."
    ),

    HumanMessage(
        content="What is LangChain?"
    ),

    response
]

print("\nMESSAGE HISTORY:\n")

for msg in messages:

    print(
        f"TYPE : {msg.__class__.__name__}"
    )

    print(
        f"CONTENT : {msg.content}"
    )

    print("-" * 50)

print("\n" + "=" * 60)
print("EXAMPLE 4 : pretty_print()")
print("=" * 60)

for msg in messages:

    msg.pretty_print()

print("\n" + "=" * 60)
print("LEARNING NOTES")
print("=" * 60)

print("""
1. invoke()
   - Sends input to model.
   - Returns AIMessage.

2. response.content
   - Gives generated text.

3. response_metadata
   - Token usage
   - Model info
   - Finish reason

4. HumanMessage
   - User input

5. AIMessage
   - Model output

6. SystemMessage
   - Instructions to the model

7. messages list
   - Stores conversation history

8. pretty_print()
   - Displays messages in readable format

9. ChatGroq
   - Chat model provider

10. LangGraph
    - Uses message objects extensively
""")