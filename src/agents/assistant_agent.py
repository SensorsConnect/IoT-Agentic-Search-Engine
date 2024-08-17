import logging
from langchain_core.messages import SystemMessage,filter_messages
from state_graph import AgentState
from utils import parser, prepaer_states,llm,get_thread  # Example import for utility functions
from agents_prompt import assistant_prompt
# another_script.py
from sensorsconnect_coverage.geography_db import check_city_country_exists
from sensorsconnect_coverage.location_finder import finder
def assistant_agent(state: AgentState):
    logging.info("entering assistant node")
    agent_state = {"node": ["assistant_agent"]}

    thread= get_thread(state)

    prompt = [SystemMessage(content=assistant_prompt)] + list(thread)
    isParsed=False
    while isParsed == False:
        try:
            response = llm.invoke(prompt)
            logging.info(response)
            response_json = parser.parse(response.content)
            isParsed=True
        except:
            isParsed=True

    if response_json["query-type"] == "greeting-general":
        agent_state["call"] = "reviewer_agent"
        agent_state["response"] = [response_json["response"]]
    elif response_json["query-type"] == "service-recommendation":
        result = finder.process_location_query(response_json)
        logging.info(result)
        if result:
            covered_by_sensorsconnect = check_city_country_exists(result["city"], result["country"])
            agent_state["location_finder_results"]=result
            if covered_by_sensorsconnect:
                logging.info('Iot_engine')
                agent_state["call"] = "IoT_engine"
                agent_state["query"] = response_json["question"]
            else:
                logging.info("GoogleMaps")
                agent_state["call"] = "GoogleMaps"
                agent_state["query"] = response_json["question"]   
        else:
            logging.info("Iot_engine")
            agent_state["call"] = "IoT_engine"
            agent_state["query"] = response_json["question"]
    else:
        agent_state["query"] = response_json["question"]
        agent_state["call"] = "scrapper"
    agent_state["messages"] = [response]
    logging.info(agent_state)
    return prepaer_states(agent_state)
