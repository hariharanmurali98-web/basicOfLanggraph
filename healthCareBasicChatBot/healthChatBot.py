from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2  # Low temperature for factual, consistent answers
)

# 1. Production-style System Prompt with strict domain rules and disclaimers
HEALTHCARE_SYSTEM_PROMPT = """You are "CareGuide", an AI triage assistant for a healthcare provider.

CORE OPERATIONAL RULES:
1. DISCLAIMER: You are an informational assistant, NOT a doctor. You cannot prescribe medications or confirm diagnoses.
2. EMERGENCY PROTOCOL: If the user mentions chest pain, severe shortness of breath, sudden numbness, uncontrolled bleeding, or suicidal thoughts, IMMEDIATELY instruct them to call 112/911 or visit the nearest emergency room. Stop normal triage immediately.
3. INFORMATION GATHERING: When a user reports a symptom, systematically clarify:
   - Duration (how long has it lasted?)
   - Severity (scale of 1-10)
   - Accompanying symptoms (e.g., fever, dizziness)
4. RECOMMENDATION: Recommend the appropriate care level (Home care, General Physician consultation, or Specialist like ENT/Dermatologist).
5. TONE: Empathetic, professional, concise, and clear. Avoid overly medical jargon.
"""

# 2. Maintain conversational state
conversation_history = [
    SystemMessage(content=HEALTHCARE_SYSTEM_PROMPT)
]

print("--- CareGuide Health Assistant (Type 'exit' to quit) ---")

while True:
    user_input = input("\nPatient: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ["exit", "quit"]:
        print("CareGuide: Take care. Goodbye!")
        break

    # Append user turn to history
    conversation_history.append(HumanMessage(content=user_input))

    # Invoke LLM with complete conversation state
    response = llm.invoke(conversation_history)

    # Append AI turn to preserve multi-turn context
    conversation_history.append(AIMessage(content=response.content))

    print(f"\nCareGuide:\n{response.content}")