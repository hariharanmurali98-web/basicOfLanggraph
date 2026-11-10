In LangChain, a multi-turn production chatbot relies on three core concepts:

Message Roles: SystemMessage (domain guardrails, persona, behavior rules), HumanMessage (user input), and AIMessage (assistant responses).

Conversation History: LLMs are stateless; the model only remembers context if past HumanMessage and AIMessage turns are retained and passed back into the prompt array on every call.

Domain Guardrails: In domains like Healthcare (triage assistant) or Ticket Booking (e.g., BookMyShow-style assistant), the SystemMessage strictly bounds what the AI can and cannot do (e.g., no medical diagnosis, emergency escalation, structured booking info collection).

Below are practical, production-pattern implementations showing how messages and prompts are structured for both domains.

Example 1: Healthcare Triage Assistant ("CareGuide")
In healthcare, the system prompt must strictly establish safety boundaries: it must never diagnose, must collect symptoms methodically, and must escalate emergencies immediately to emergency lines (like 112/911).

Example 2: Cinema & Event Booking Assistant ("ShowBot" / BookMyShow-style)
In entertainment booking, the system prompt forces the model to act as a structured booking agent that collects parameters sequentially: City/Location → Movie/Event → Date & Show Format → Seat Category/Count, preventing premature confirmations.

## Production Enhancements to Keep in Mind

### Sliding window and trimming

If a user talks for many turns, passing the entire history can exceed the model's context window and increase token usage. Use `trim_messages` from `langchain_core.messages` to keep the SystemMessage plus an appropriate number of recent turns.

### Session storage

Instead of relying on an in-memory list (`conversation_history = [...]`), production systems can store messages in a database such as Redis or PostgreSQL, keyed by `session_id`.

For a fuller treatment of persistence, thread IDs, storage layers, sliding windows, rolling summaries, and message trimming, see [prodchatBotTipsGuide.md](prodchatBotTipsGuide.md).