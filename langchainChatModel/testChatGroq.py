import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Reads key-value pairs from .env and injects them into os.environ
load_dotenv()

# 2. ChatGroq automatically detects os.environ["GROQ_API_KEY"]
chat = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)

# Test run
response = chat.invoke("Explain microservices architecture in two sentences.")
print(response.content)