from langchain_core.messages import ToolMessage
# from langchain_community.tools.tavily_search import TavilySearchResults

import logging
from state_graph import AgentState
from agents_prompt import assistant_prompt
from utils import parser,prepaer_states
import os
from tavily import TavilyClient

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')


# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def scrapper(state: AgentState):
    humman_message = state["query"]
    response = tavily_client.search(humman_message)
    if response["results"]:
        search_result = response["results"]
        return prepaer_states({
            "messages": [ToolMessage(content=str(search_result[0]), name="scrapper", tool_call_id="call_scrapper")],
            "handled": [True],
            "node": ["scrapper"],
            "context": str(search_result[0])
        })
    else:
        return prepaer_states({"handled": [False]})
