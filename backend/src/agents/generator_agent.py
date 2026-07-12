import logging
from langchain_core.messages import SystemMessage,filter_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from state_graph import AgentState
from agents_prompt import assistant_prompt
from utils import parser,prepaer_states,llm,get_thread
from agents_prompt import scrapper_prompt,IoT_engine_prompt,GoogleMaps_prompt

logger = logging.getLogger(__name__)

TavilySearch = TavilySearchResults(max_results=2)  # increased number of results

def generator_agent(state: AgentState):
    rid = state.get("correlation_id", "")
    question= state.get("query", "")
    context= state.get("context", "")
    from_node = state.get("node", "")
    logger.info(f"generator_agent start rid={rid} from_node={from_node} context_present={bool(context)}")

    if context=="":
        if state["node"]=='IoT_engine':
            logger.info(f"generator_agent fallback rid={rid} IoT_engine had no results -> GoogleMaps")
            return prepaer_states({"node": "generator_agent", "response": "", "call": "GoogleMaps"})
        elif state["node"]=='GoogleMaps':
            logger.info(f"generator_agent fallback rid={rid} GoogleMaps had no results -> scrapper")
            return prepaer_states({"node": "generator_agent", "response": "", "call": "scrapper"})
        else:
            logger.info(f"generator_agent fallback rid={rid} node={state['node']} -> cannot_handle")
            return prepaer_states({"node": "generator_agent", "response": "I can't handle this query", "call": "scrapper"})


    if state["node"]=='scrapper':
        node =state["node"]

        thread= get_thread(state)
        prompt = [SystemMessage(content=scrapper_prompt.format(context=context, node=node))] + list(thread)
    elif state["node"]=='IoT_engine':
        node =state["node"]

        thread= get_thread(state)
        prompt = [SystemMessage(content=IoT_engine_prompt.format(JsonObject=context, node=node))] + list(thread)
    elif state["node"]=='GoogleMaps':
        node =state["node"]
        thread= get_thread(state)
        prompt = [SystemMessage(content=GoogleMaps_prompt.format(JsonObject=context, node=node))] + list(thread)
    response = llm.invoke(prompt)
    logger.debug(f"generator_agent LLM response preview: {str(response.content)[:200]}")
    logger.info(f"generator_agent complete rid={rid} from_node={from_node}")
    return prepaer_states({"messages": [response], "node": "generator_agent", "response": response.content})
