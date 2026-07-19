import logging
from langchain_core.messages import SystemMessage,filter_messages
from state_graph import AgentState
from utils import parser, prepaer_states,llm,get_thread  # Example import for utility functions
from agents_prompt import assistant_prompt
# another_script.py
from sensorsconnect_coverage.geography_db import check_city_country_exists
from sensorsconnect_coverage.location_finder import finder

logger = logging.getLogger(__name__)

def assistant_agent(state: AgentState):
    rid = state.get("correlation_id", "")
    logger.info(f"assistant_agent start rid={rid} query='{state.get('query', '')[:80]}'")
    agent_state = {"node": "assistant_agent"}

    thread= get_thread(state)

    prompt = [SystemMessage(content=assistant_prompt)] + list(thread)
    isParsed=False
    while isParsed == False:
        try:
            response = llm.invoke(prompt)
            logger.debug(f"assistant LLM response: {str(response.content)[:200]}")
            response_json = parser.parse(response.content)
            isParsed=True
        except (ValueError, KeyError, TypeError) as e:
            logging.warning(f"Failed to parse assistant response as JSON: {e}")
            user_query = state.get("query", "").strip().lower()
            greetings = {"hello", "hi", "hey", "thanks", "thank you", "bye", "goodbye", "good morning", "good evening"}
            if user_query and user_query not in greetings and len(user_query.split()) <= 3:
                response_json = {
                    "query-type": "service-recommendation",
                    "search_type": "keyword",
                    "service": state.get("query", "").strip(),
                    "city": "",
                    "country": "",
                    "address": "",
                    "question": state.get("query", "").strip()
                }
            else:
                response_json = {
                    "query-type": "greeting-general",
                    "response": response.content
                }
            isParsed=True

    if response_json["query-type"] == "greeting-general":
        agent_state["call"] = "reviewer_agent"
        agent_state["response"] = response_json["response"]
    elif response_json["query-type"] == "service-recommendation":
        agent_state["search_type"] = response_json.get("search_type", "text")

        user_loc = state.get("user_location") or {}
        user_lat = user_loc.get("latitude")
        user_lon = user_loc.get("longitude")
        has_user_gps = user_lat is not None and user_lon is not None

        if response_json.get('city') or response_json.get('country'):
            result = finder.process_location_query(response_json)
            logger.debug(f"location_finder result: city={result.get('city') if result else None} country={result.get('country') if result else None}")
            agent_state["location_finder_results"] = result
            if agent_state["search_type"] == "keyword":
                # A specific brand/landmark name can't be answered by IoT_engine's
                # generic service-category search, regardless of city coverage.
                logger.info(f"assistant_agent route rid={rid} -> GoogleMaps reason=keyword_search")
                agent_state["call"] = "GoogleMaps"
            else:
                covered_by_sensorsconnect = check_city_country_exists(result.get("city", ""), result.get("country", ""))
                if covered_by_sensorsconnect:
                    logger.info(f"assistant_agent route rid={rid} -> IoT_engine reason=sensorsconnect_covered")
                    agent_state["call"] = "IoT_engine"
                else:
                    logger.info(f"assistant_agent route rid={rid} -> GoogleMaps reason=outside_sensorsconnect")
                    agent_state["call"] = "GoogleMaps"
            agent_state["query"] = response_json["question"]
        elif has_user_gps:
            logger.info(f"assistant_agent route rid={rid} -> GoogleMaps reason=user_gps lat={user_lat:.4f} lon={user_lon:.4f}")
            agent_state["call"] = "GoogleMaps"
            agent_state["query"] = response_json["question"]
            agent_state["location_finder_results"] = {"coordinates": [user_lat, user_lon]}
        else:
            logger.info(f"assistant_agent route rid={rid} -> IoT_engine reason=no_location")
            agent_state["call"] = "IoT_engine"
            agent_state["query"] = response_json["question"]
    else:
        agent_state["query"] = response_json["question"]
        agent_state["call"] = "scrapper"
    agent_state["messages"] = [response]
    return prepaer_states(agent_state)
