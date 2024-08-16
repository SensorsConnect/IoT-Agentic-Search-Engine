import logging
from langchain_core.messages import SystemMessage,filter_messages
from state_graph import AgentState
from utils import parser, prepaer_states,llm  # Example import for utility functions
from agents_prompt import assistant_prompt

def assistant_agent(state: AgentState):
    logging.info("entering assistant node")
    agent_state = {"node": ["assistant_agent"]}
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
