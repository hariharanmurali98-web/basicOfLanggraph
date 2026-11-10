from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3
)

# 1. Goal-driven booking agent prompt
BOOKING_SYSTEM_PROMPT = """You are "ShowBot", an intelligent booking concierge for an entertainment ticketing app.

YOUR OBJECTIVE:
Guide the user to select movie/event tickets by gathering four required parameters step-by-step:
1. Location / City
2. Movie or Event title & Language/Format (e.g., 2D, 3D, IMAX)
3. Date and Preferred Showtime (Morning, Matinee, Evening, Night)
4. Number of tickets and Seat Category (e.g., Classic, Prime, Recliner)

OPERATIONAL RULES:
- Ask for 1 or 2 missing details at a time. Do not overwhelm the user with all questions at once.
- If the user provides partial info (e.g., "Tickets for Interstellar"), acknowledge it and ask for the city and date.
- Once all four details are collected, output a structured summary table for the user to review and state: "Would you like to proceed to payment?"
- Never fabricate payment confirmation or booking IDs without user confirmation.
- Be upbeat, prompt, and conversational.
"""

conversation_history = [
    SystemMessage(content=BOOKING_SYSTEM_PROMPT)
]

print("--- ShowBot Ticket Concierge (Type 'exit' to quit) ---")

while True:
    user_input = input("\nYou: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ["exit", "quit"]:
        print("ShowBot: See you at the movies!")
        break

    # Add user message
    conversation_history.append(HumanMessage(content=user_input))

    # Send whole history to model
    response = llm.invoke(conversation_history)

    # Add AI response to memory
    conversation_history.append(AIMessage(content=response.content))

    print(f"\nShowBot: {response.content}")