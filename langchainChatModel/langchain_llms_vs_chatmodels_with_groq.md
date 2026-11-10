# LangChain LLMs vs. Chat Models: Complete Guide with ChatGroq

When building AI applications with LangChain, one of the first foundational decisions is choosing between **LLMs (Text Completion Models)** and **Chat Models**.

---

## 1. The Core Difference: `LLMs` vs. `Chat Models`

LangChain splits model interfaces into two primary categories:

| Feature | Generic `LLM` (Text In $\rightarrow$ Text Out) | `ChatModel` (Messages In $\rightarrow$ Message Out) |
| :--- | :--- | :--- |
| **Input Type** | Raw string (plain text prompt) | List of structured message objects (`System`, `Human`, `AI`) |
| **Output Type** | Raw string | Structured `AIMessage` object |
| **Underlying API** | Legacy completion endpoints (e.g., text davinci) | Chat completion endpoints (`/chat/completions`) |
| **Primary Use Case** | Pure text continuation, autocomplete, single-prompt code completion | Conversational bots, role-playing, instruction-tuned tasks, tool calling |
| **Modern Status** | Mostly legacy / specialized | **Industry Standard** for almost all modern LLMs |

---

## 2. Approach 1: Generic LLM (Text In, Text Out)

### Why it's typically *not* preferred for chatbots:
* It does not natively distinguish between system instructions, user dialogue, and assistant responses.
* You have to manually format the entire conversation history as one giant prompt string (e.g., `"User: hi \n Assistant: hello \n User: ..."`).
* Modern open-source models hosted on platforms like Groq (Llama 3, Mixtral) are fine-tuned specifically for chat instruction formats.

### Example (Generic LLM interface):
```python
# Generic string-in / string-out pattern
from langchain_community.llms import OpenAI  # Or another completion LLM

llm = OpenAI(model_name="gpt-3.5-turbo-instruct")

# Input is just a plain string
response = llm.invoke("Explain photosynthesis in one sentence.")
print(response)  # Outputs raw string
```

---

## 3. Approach 2: Chat Model (`ChatOpenAI`, `ChatGroq`)

### Why this is the preferred way:
* **Role separation:** You can define a system persona (`SystemMessage`), user inputs (`HumanMessage`), and previous assistant responses (`AIMessage`).
* **Multi-turn memory:** LangChain conversational memory or chat histories slot directly into message lists.
* **Tool / Function Calling:** Modern features like structured outputs and tool calling are built into `ChatModel` abstractions.

---

## 4. Building with Groq (`ChatGroq`) — Fast & Free

Groq provides extremely fast inference and a generous free tier for open-source models like `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`.

### Step 1: Install Requirements
```bash
pip install langchain-groq langchain-core
```

Set your API key in your environment (obtainable free from [Groq Console](https://console.groq.com/)):
```bash
export GROQ_API_KEY="gsk_..."
```

---

### Step 2: Basic Invocation with Roles

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

# Initialize the chat model
chat = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
)

# Structured conversation input
messages = [
    SystemMessage(content="You are a helpful and concise coding assistant."),
    HumanMessage(content="How do I read a file line-by-line in Python?"),
]

response = chat.invoke(messages)

# Response is an AIMessage object
print(response.content)
```

---

### Step 3: Multi-turn Chat Example (Chatbot Simulation)

Because `ChatModel` takes a list of message objects, handling conversation history is straightforward:

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

# Conversation history list
chat_history = [
    SystemMessage(content="You are a friendly tutor who speaks in short sentences."),
]

def talk_to_bot(user_text: str):
    # 1. Add user message
    chat_history.append(HumanMessage(content=user_text))
    
    # 2. Invoke the model with full conversation context
    ai_reply = llm.invoke(chat_history)
    
    # 3. Append assistant reply to keep memory
    chat_history.append(ai_reply)
    
    return ai_reply.content

# Turn 1
print("Bot:", talk_to_bot("Hi, my name is Alex!"))

# Turn 2 (The model remembers the context)
print("Bot:", talk_to_bot("What is my name?"))
```

---

### Step 4: Using Prompt Templates (`ChatPromptTemplate`)

In production, you usually construct your chat pipeline using `ChatPromptTemplate` and LCEL (LangChain Expression Language):

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Define prompt structure
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert technical interviewer in {topic}."),
    ("human", "{question}"),
])

model = ChatGroq(model="llama-3.3-70b-versatile")

# Chain together using LCEL
chain = prompt | model

response = chain.invoke({
    "topic": "Python and FastAPI",
    "question": "What is dependency injection and why use it?"
})

print(response.content)
```

---

## 5. Summary Cheat Sheet

* Use **`ChatModel`** (`ChatGroq`, `ChatOpenAI`, `ChatAnthropic`) for:
  * Chatbots and conversational assistants
  * Multi-turn dialogue with memory
  * System prompts, tone controls, and personas
  * Tool/Function calling and structured outputs
* Avoid raw **`LLM`** completion classes (`OpenAI`, `Groq` completion) unless you are maintaining legacy code or specifically need plain text completion without chat fine-tuning.