import logging
from langchain_core.messages import SystemMessage,filter_messages
from langchain_community.tools.tavily_search import TavilySearchResults
import logging
from state_graph import AgentState
from agents_prompt import assistant_prompt
from utils import parser,prepaer_states,llm
from agents_prompt import generator_prompt

TavilySearch = TavilySearchResults(max_results=2)  # increased number of results

def generator_agent(state: AgentState):
    question = state["query"]
    context = state["context"]
    messages = [
        SystemMessage(
            content=generator_prompt.format(question=question, context=context)
        )
    ]
    response = llm.invoke(messages)
    return prepaer_states({"messages": [response], "node": ["generator_agent"], "response": response.content})

def reviewer_agent(state: AgentState):
    logging.info("entering reviewer node")
    dictionary = {"handled": [True], "make_sense": [True]}
    return prepaer_states(dictionary)





