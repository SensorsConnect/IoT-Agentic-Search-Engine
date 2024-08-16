import logging
from langchain_core.messages import SystemMessage,filter_messages
from state_graph import AgentState
from utils import parser, prepaer_states,llm,get_thread  # Example import for utility functions
from agents_prompt import assistant_prompt

def assistant_agent(state: AgentState):
    logging.info("entering assistant node")
    agent_state = {"node": ["assistant_agent"]}

    thread= get_thread(state)

    prompt = [SystemMessage(content=assistant_prompt)] + list(thread)
    response = llm.invoke(prompt)
    logging.info(response)
    response_json = parser.parse(response.content)
    if response_json["query-type"] == "greeting-general":
        agent_state["call"] = "reviewer_agent"
        agent_state["response"] = [response_json["response"]]
    elif response_json["query-type"] == "service-recommendation":
        agent_state["call"] = "IoT_engine"
        agent_state["query"] = response_json["question"]
    else:
        agent_state["query"] = response_json["question"]
        agent_state["call"] = "scrapper"
    agent_state["messages"] = [response]
    logging.info(agent_state)
    return prepaer_states(agent_state)
