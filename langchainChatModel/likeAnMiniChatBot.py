from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

while True:

    user_input = input("You : ")

    if user_input.lower() == "exit":
        break

    response = llm.invoke(user_input)

    print("AI :", response.content)