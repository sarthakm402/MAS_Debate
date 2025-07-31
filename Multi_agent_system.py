# import os
# import google.generativeai as genai
# from langchain.memory import ConversationBufferMemory
# from langchain.schema import messages_to_dict, messages_from_dict
# from langgraph.graph import StateGraph
# from typing import TypedDict, List

# genai.configure(api_key="")
# model = genai.GenerativeModel("gemini-2.0-flash-lite")

# memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history", k=3)

# FOR_PROMPT = """
# Conversation history:
# {history}

# You are a skilled debater. Argue *in favor* of the following topic:
# Topic: {topic}
# Make sure your response is logical, persuasive, and concise.
# """

# AGAINST_PROMPT = """
# Conversation history:
# {history}

# You are a skilled debater. Argue *against* the following topic:
# Topic: {topic}
# Make sure your response is logical, persuasive, and concise.
# """

# FACT_CHECK_PROMPT = """
# Conversation history:
# {history}

# You are a fact-checker. Please analyze both arguments and point out any factual inaccuracies or unsupported claims.
# Fact-check results:
# """

# MEDIATOR_PROMPT = """
# Conversation history:
# {history}

# You are a neutral moderator. Two arguments have been presented:
# Use the above conversation to analyze both sides on logic, facts, and persuasiveness, then declare which side wins and why.
# """

# class DebateState(TypedDict):
#     topic: str
#     fact_check: str
#     verdict: str

# def for_agent(state: DebateState) -> DebateState:
#     history = memory.load_memory_variables({})["chat_history"]
#     prompt = FOR_PROMPT.format(history=history, topic=state["topic"])
#     response = model.generate_content(prompt)
#     arg = response.text.strip()
#     memory.chat_memory.add_user_message(f"FOR request: {state['topic']}")
#     memory.chat_memory.add_ai_message(arg)
#     return state

# def against_agent(state: DebateState) -> DebateState:
#     history = memory.load_memory_variables({})["chat_history"]
#     prompt = AGAINST_PROMPT.format(history=history, topic=state["topic"])
#     response = model.generate_content(prompt)
#     arg = response.text.strip()
#     memory.chat_memory.add_user_message(f"AGAINST request: {state['topic']}")
#     memory.chat_memory.add_ai_message(arg)
#     return state

# def fact_checker(state: DebateState) -> DebateState:
#     history = memory.load_memory_variables({})["chat_history"]
#     prompt = FACT_CHECK_PROMPT.format(history=history)
#     response = model.generate_content(prompt)
#     state["fact_check"] = response.text.strip()
#     memory.chat_memory.add_user_message("FACT CHECK request")
#     memory.chat_memory.add_ai_message(state["fact_check"])
#     return state

# def mediator(state: DebateState) -> DebateState:
#     history = memory.load_memory_variables({})["chat_history"]
#     prompt = MEDIATOR_PROMPT.format(history=history)
#     response = model.generate_content(prompt)
#     state["verdict"] = response.text.strip()
#     memory.chat_memory.add_user_message("MEDIATOR request")
#     memory.chat_memory.add_ai_message(state["verdict"])
#     return state

# graph = StateGraph(DebateState)
# graph.add_node("ForAgent", for_agent)
# graph.add_node("AgainstAgent", against_agent)
# graph.add_node("FactChecker", fact_checker)
# graph.add_node("Mediator", mediator)

# graph.set_entry_point("ForAgent")
# graph.add_edge("ForAgent", "AgainstAgent")
# graph.add_edge("AgainstAgent", "FactChecker")
# graph.add_edge("FactChecker", "Mediator")
# graph.set_finish_point("Mediator")
# runnable = graph.compile()

# if __name__ == '__main__':
#     topic = "Should AI be regulated by governments?"
#     for i in range(3):
#         print(f"\n===== Round {i + 1} =====")
#         initial_state: DebateState = {"topic": topic, "fact_check": "", "verdict": ""}
#         result = runnable.invoke(initial_state)
#         print("\nConversation history:")
#         for msg in memory.chat_memory.messages:
#             print(f"{msg.type}: {msg.content}")
#     print("\nFact Check:\n", result["fact_check"])
#     print("\nMediator Verdict:\n", result["verdict"])





import os
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.schema import messages_to_dict, messages_from_dict
from langgraph.graph import StateGraph
from typing import TypedDict, Optional

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history", k=3)

FOR_PROMPT = """
Conversation history:
{history}

You are a skilled debater. Argue *in favor* of the following topic:
Topic: {topic}
Make sure your response is logical, persuasive, and concise.
"""

FOR_REVISION_PROMPT = """
Conversation history:
{history}

Your previous 'for' argument:
{previous}

Fact-check feedback:
{feedback}

Revise and strengthen your argument in favor of the topic, addressing the feedback.
"""

AGAINST_PROMPT = """
Conversation history:
{history}

You are a skilled debater. Argue *against* the following topic:
Topic: {topic}
Make sure your response is logical, persuasive, and concise.
"""

AGAINST_REVISION_PROMPT = """
Conversation history:
{history}

Your previous 'against' argument:
{previous}

Fact-check feedback:
{feedback}

Revise and strengthen your argument against the topic, addressing the feedback.
"""

FACT_CHECK_PROMPT = """
Conversation history:
{history}

You are a fact-checker. Please analyze both arguments and point out any factual inaccuracies or unsupported claims.
Fact-check results:
"""

MEDIATOR_PROMPT = """
Conversation history:
{history}

You are a neutral moderator. Two arguments have been presented:
Use the above conversation to analyze both sides on logic, facts, and persuasiveness, then declare which side wins and why.
"""

class DebateState(TypedDict):
    topic: str
    for_argument: Optional[str]
    against_argument: Optional[str]
    fact_check: Optional[str]
    verdict: Optional[str]

def for_agent(state: DebateState) -> DebateState:
    history = memory.load_memory_variables({})["chat_history"]
    prev = state.get("for_argument", "") or ""
    if state.get("fact_check") and prev:
        prompt = FOR_REVISION_PROMPT.format(history=history, previous=prev, feedback=state["fact_check"])
    else:
        prompt = FOR_PROMPT.format(history=history, topic=state["topic"])
    response = model.generate_content(prompt)
    arg = response.text.strip()
    state["for_argument"] = arg
    memory.chat_memory.add_user_message(f"FOR request: {state['topic']}")
    memory.chat_memory.add_ai_message(arg)
    return state

def against_agent(state: DebateState) -> DebateState:
    history = memory.load_memory_variables({})["chat_history"]
    prev = state.get("against_argument", "") or ""
    if state.get("fact_check") and prev:
        prompt = AGAINST_REVISION_PROMPT.format(history=history, previous=prev, feedback=state["fact_check"])
    else:
        prompt = AGAINST_PROMPT.format(history=history, topic=state["topic"])
    response = model.generate_content(prompt)
    arg = response.text.strip()
    state["against_argument"] = arg
    memory.chat_memory.add_user_message(f"AGAINST request: {state['topic']}")
    memory.chat_memory.add_ai_message(arg)
    return state

def fact_checker(state: DebateState) -> DebateState:
    history = memory.load_memory_variables({})["chat_history"]
    prompt = FACT_CHECK_PROMPT.format(history=history)
    response = model.generate_content(prompt)
    state["fact_check"] = response.text.strip()
    memory.chat_memory.add_user_message("FACT CHECK request")
    memory.chat_memory.add_ai_message(state["fact_check"])
    return state

def mediator(state: DebateState) -> DebateState:
    history = memory.load_memory_variables({})["chat_history"]
    prompt = MEDIATOR_PROMPT.format(history=history)
    response = model.generate_content(prompt)
    state["verdict"] = response.text.strip()
    memory.chat_memory.add_user_message("MEDIATOR request")
    memory.chat_memory.add_ai_message(state["verdict"])
    return state

graph = StateGraph(DebateState)
graph.add_node("ForAgent", for_agent)
graph.add_node("AgainstAgent", against_agent)
graph.add_node("FactChecker", fact_checker)
graph.add_node("Mediator", mediator)

graph.set_entry_point("ForAgent")
graph.add_edge("ForAgent", "AgainstAgent")
graph.add_edge("AgainstAgent", "FactChecker")
graph.add_edge("FactChecker", "ForAgent")
graph.add_edge("ForAgent", "AgainstAgent")
graph.add_edge("AgainstAgent", "Mediator")
graph.set_finish_point("Mediator")

runnable = graph.compile()

if __name__ == '__main__':
    topic = "Should AI be regulated by governments?"
    initial_state = {"topic": topic, "for_argument": None, "against_argument": None, "fact_check": None, "verdict": None}
    result = runnable.invoke(initial_state)
    for msg in memory.chat_memory.messages:
        print(f"{msg.type}: {msg.content}")
    print("Final Verdict:", result["verdict"])
