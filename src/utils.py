from langchain_core.output_parsers import JsonOutputParser
import os
from langchain_groq import ChatGroq  # Assuming this is the correct import


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