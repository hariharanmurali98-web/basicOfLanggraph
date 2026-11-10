from langchain_core.messages import HumanMessage, AIMessage,SystemMessage

messages = []
messages.append(SystemMessage(content="you are an medical pharmacy specialist"))
messages.append(AIMessage(content="Hi How can i help you",name="instructor"))
messages.append(HumanMessage(content="I am having headache, what should i do",name="hari"))

messages.append(AIMessage(content="if its an mild head ache take dolo, for severe check with doctor",name="instructor"))
messages.append(HumanMessage(content="okay i check",name="hari"))

print(f"the foramt of the messages is :{messages} like this <-")
# if you see there in this message there would be ,meta data and etc
for m in messages:
    m.pretty_print()