import logging
from state_graph import AgentState
from utils import prepaer_states
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage,filter_messages      
from agents_prompt import reviewer_prompt
from utils import llm,parser
from sensorsconnect_coverage.location_finder import finder
from sensorsconnect_coverage.geography_db import check_city_country_exists
# def reviewer_agent(state: AgentState):
#     logging.info("entering reviewer node")
#     dictionary = {"handled": [True], "make_sense": [True]}
#     return prepaer_states(dictionary)
def reviewer_agent(state: AgentState):
    agent_state = {"node": ["reviewer"]}
    logging.info("entering reviewer node")
    
    if state["node"][-1]=="assistant_agent":
        # question = state["query"]
        if state["query"]!=None:
            print(state["query"])
            query= HumanMessage(content=state["query"])
        else:
            print("empty query detected")
            messages = state["messages"]
            human_messages = filter_messages(messages, include_types="human")
            query=human_messages[-1],
        response =state["response"][-1]
        thread=[]
        thread.append(query)
        thread.append(response)
        print(thread)
        prompt = [SystemMessage(content=reviewer_prompt)] + list(thread)
        isParsed=False
        while isParsed == False:
            try:
                response = llm.invoke(prompt)
                logging.info(response)
                response_json = parser.parse(response.content)
                isParsed=True
            except:
                response_json={"query-type" : "answered"}
                isParsed=True
                
        if response_json["query-type"] == "answered":
            agent_state["call"] = "END"
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
        return agent_state
    
    agent_state["call"] = "END"
    print("end of reviwer")
    return agent_state