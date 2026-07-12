import logging
from state_graph import AgentState
from utils import prepaer_states
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage,filter_messages
from agents_prompt import reviewer_prompt
from utils import llm,parser
from sensorsconnect_coverage.location_finder import finder
from sensorsconnect_coverage.geography_db import check_city_country_exists

logger = logging.getLogger(__name__)

def reviewer_agent(state: AgentState):
    rid = state.get("correlation_id", "")
    agent_state = {"node": "reviewer"}
    logger.info(f"reviewer_agent start rid={rid} from_node={state.get('node', '')}")

    if state["node"]=="assistant_agent":
        if state.get("query") is not None:
            query= HumanMessage(content=state["query"])
        else:
            logger.debug("reviewer_agent: query is None, using last human message")
            messages = state["messages"]
            human_messages = filter_messages(messages, include_types="human")
            query=human_messages[-1]
        response = AIMessage(content=state["response"])
        thread=[]
        thread.append(query)
        thread.append(response)
        prompt = [SystemMessage(content=reviewer_prompt)] + list(thread)
        isParsed=False
        while isParsed == False:
            try:
                response = llm.invoke(prompt)
                logger.debug(f"reviewer LLM response: {str(response.content)[:200]}")
                response_json = parser.parse(response.content)
                isParsed=True
            except (ValueError, KeyError, TypeError) as e:
                logging.warning(f"Failed to parse reviewer response as JSON: {e}")
                response_json={"query-type" : "answered"}
                isParsed=True

        if response_json["query-type"] == "answered":
            agent_state["call"] = "END"
        elif response_json["query-type"] == "service-recommendation":
            result = finder.process_location_query(response_json)
            logger.debug(f"reviewer location result: {result}")
            if result:
                covered_by_sensorsconnect = check_city_country_exists(result["city"], result["country"])
                agent_state["location_finder_results"]=result
                if covered_by_sensorsconnect:
                    logger.info(f"reviewer_agent route rid={rid} -> IoT_engine reason=sensorsconnect_covered")
                    agent_state["call"] = "IoT_engine"
                    agent_state["query"] = response_json["question"]
                else:
                    logger.info(f"reviewer_agent route rid={rid} -> GoogleMaps reason=outside_sensorsconnect")
                    agent_state["call"] = "GoogleMaps"
                    agent_state["query"] = response_json["question"]
            else:
                logger.info(f"reviewer_agent route rid={rid} -> IoT_engine reason=no_location")
                agent_state["call"] = "IoT_engine"
                agent_state["query"] = response_json["question"]
        else:
            agent_state["query"] = response_json["question"]
            agent_state["call"] = "scrapper"
        agent_state["messages"] = [response]
        return prepaer_states(agent_state)
    elif state.get("response", "") == "":
        agent_state["call"] = "END"
        return prepaer_states(agent_state)
    else:
        agent_state["call"] = "END"
    return prepaer_states(agent_state)
