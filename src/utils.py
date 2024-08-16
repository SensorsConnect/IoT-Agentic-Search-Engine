from langchain_core.output_parsers import JsonOutputParser
import os
from langchain_groq import ChatGroq  # Assuming this is the correct import
from langchain_core.messages import SystemMessage,filter_messages

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
parser = JsonOutputParser()

# Initialize the language model
llm = ChatGroq(model="llama3-8b-8192", temperature=0)

def prepaer_states(json_obj):
    """
    Ensure all keys are present in the JSON object. 
    If a key is missing, set its value to None.

    Args:
        json_obj (dict): The JSON object to check.
        keys (list): List of keys to ensure in the JSON object.

    Returns:
        dict: The updated JSON object with all specified keys.
    """
    keys = [ "handled", "make_sense", "node"]
    for key in keys:
        if key not in json_obj:
            json_obj[key] = [None]
    return json_obj

def get_thread(state):
    messages = state["messages"]
    human_messages = filter_messages(messages, include_types="human")
    if(len(human_messages)>1):
        index =0
        responses = state["response"]
        thread=[]
        for response in responses:
            thread.append(human_messages[index])
            thread.append(SystemMessage(content=response))
            index+=1
        thread.append(human_messages[-1])
    else:
        thread= human_messages
    return thread