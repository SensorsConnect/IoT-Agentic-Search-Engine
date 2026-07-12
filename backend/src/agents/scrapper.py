from langchain_core.messages import ToolMessage
import logging
import time
from state_graph import AgentState
from agents_prompt import assistant_prompt
from utils import parser,prepaer_states
import os
from tavily import TavilyClient

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')


# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def scrapper(state: AgentState):
    humman_message = state["query"]
    rid = state.get("correlation_id", "")
    t0 = time.time()
    logger.info(f"scrapper start rid={rid} query='{humman_message[:80]}'")
    response = tavily_client.search(humman_message)
    if response["results"]:
        search_result = response["results"]
        logger.info(f"scrapper complete rid={rid} results={len(search_result)} duration={time.time()-t0:.2f}s")
        return prepaer_states({
            "messages": [ToolMessage(content=str(search_result[0]), name="scrapper", tool_call_id="call_scrapper")],
            "node": "scrapper",
            "context": str(search_result[0]),
            "call": "generator_agent"
        })
    else:
        logger.warning(f"scrapper no_results rid={rid} query='{humman_message[:80]}' duration={time.time()-t0:.2f}s")
        return prepaer_states({"node": "scrapper", "call": "generator_agent"})
