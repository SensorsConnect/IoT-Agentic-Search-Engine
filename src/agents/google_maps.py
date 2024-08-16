import logging
from state_graph import AgentState
from googleMaps.google_maps_client import gmaps_text_search_client
def GoogleMaps(state: AgentState):
    results= gmaps_text_search_client.text_search_with_details("best coffee shops in San Francisco", 37.7749, -122.4194, limit=3)
    logging.info("Using branch C")
    return input
