import logging
from state_graph import AgentState
from googleMaps.google_maps_client import gmaps_text_search_client
from utils import prepaer_states
from langchain_core.messages import ToolMessage
def GoogleMaps(state: AgentState):
    logging.info("Using GoogleMaps")
    location=state.get("location_finder_results", {})
    coordinates=location.get('coordinates', [])
    print("Coordinates in GoogleMaps agent:", coordinates)
    print("coordinates type:", type(coordinates))
    
    # Validate coordinates
    if not coordinates or len(coordinates) < 2:
        logging.error(f"Invalid coordinates received: {coordinates}")
        return prepaer_states({
            "handled": [False],
            "node": ["GoogleMaps"],
            "call":"generator_agent"
        })
    
    # Ensure coordinates are numeric
    try:
        lat = float(coordinates[0])
        lon = float(coordinates[1])
    except (ValueError, TypeError) as e:
        logging.error(f"Coordinates are not valid numbers: {e}")
        return prepaer_states({
            "handled": [False],
            "node": ["GoogleMaps"],
            "call":"generator_agent"
        })
    
    query=state.get("query", "")
    results= gmaps_text_search_client.text_search_with_details(query, lat, lon, limit=3)
    
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
