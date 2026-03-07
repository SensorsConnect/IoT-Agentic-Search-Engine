from langchain_core.output_parsers import JsonOutputParser
import os
from langchain_groq import ChatGroq  # Assuming this is the correct import
from langchain_core.messages import AIMessage, HumanMessage, filter_messages

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
LLM_MODEL = os.environ.get('LLM_MODEL')
parser = JsonOutputParser()

# Initialize the language model
llm = ChatGroq(model=LLM_MODEL, temperature=0)

def prepaer_states(json_obj):
    return json_obj

def get_thread(state):
    thread_summary = state.get("thread_summary", [])
    thread = []
    for entry in thread_summary:
        if entry and entry.get("role") == "user":
            thread.append(HumanMessage(content=entry["content"]))
        elif entry and entry.get("role") == "assistant":
            thread.append(AIMessage(content=entry["content"]))
    current_query = state.get("query", "")
    if current_query:
        thread.append(HumanMessage(content=current_query))
    return thread
