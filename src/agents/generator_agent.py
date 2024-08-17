import logging
from langchain_core.messages import SystemMessage,filter_messages
from langchain_community.tools.tavily_search import TavilySearchResults
import logging
from state_graph import AgentState
from agents_prompt import assistant_prompt
from utils import parser,prepaer_states,llm,get_thread
from agents_prompt import scrapper_prompt,IoT_engine_prompt,GoogleMaps_prompt

TavilySearch = TavilySearchResults(max_results=2)  # increased number of results

def generator_agent(state: AgentState):
    if state["node"][-1]=='scrapper':
        question = state["query"]
        context = state["context"]
        prompt = [
            SystemMessage(
                content=scrapper_prompt.format(question=question, context=context)
            )
        ]
    elif state["node"][-1]=='IoT_engine':
        question = state["query"]
        context = state["context"]
        node =state["node"][-1]
        
        thread= get_thread(state)
        prompt = [SystemMessage(content=IoT_engine_prompt.format(JsonObject=context, node=node))] + list(thread)
    elif state["node"][-1]=='GoogleMaps':
        question = state["query"]
        context = state["context"]
        node =state["node"][-1]
        thread= get_thread(state)
        prompt = [SystemMessage(content=GoogleMaps_prompt.format(JsonObject=context, node=node))] + list(thread) 
        # messages = [
        #     SystemMessage(
        #         content=IoT_engine_prompt.format(JsonObject=context, query=question, node=node)
        #     )
        # ]
    response = llm.invoke(prompt)
    return prepaer_states({"messages": [response], "node": ["generator_agent"], "response": [response.content]})

# def reviewer_agent(state: AgentState):
#     logging.info("entering reviewer node")
#     dictionary = {"handled": [True], "make_sense": [True]}
#     return prepaer_states(dictionary)





