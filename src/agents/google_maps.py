import logging
from state_graph import AgentState
from googleMaps.google_maps_client import gmaps_text_search_client
from utils import prepaer_states
from langchain_core.messages import ToolMessage
def GoogleMaps(state: AgentState):
    logging.info("Using GoogleMaps")
    location=state["location_finder_results"]
    coordinates=location['coordinates']
    query=state["query"]
    results= gmaps_text_search_client.text_search_with_details(query, coordinates[0], coordinates[1], limit=3)
    
    if results:
        return prepaer_states({
            "messages": [ToolMessage(content=str(results), name="GoogleMaps", tool_call_id="call_IoT_engine")],
            "handled": [True],
            "node": ["GoogleMaps"],
            "context": str(results),
            "call":"generator_agent"
        })
    else:
        return prepaer_states({"handled": [False],
                               "node": ["GoogleMaps"],
                               "call":"generator_agent"})
