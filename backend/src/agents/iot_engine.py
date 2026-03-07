import logging
from state_graph import AgentState
from vector_db.vector_database import vector_search
from mongo_db.database_connection import get_nearByPlaces
from serivce_recommender.sorting_serivces import get_recommendedSerivce
from utils import prepaer_states
from langchain_core.messages import ToolMessage

def IoT_engine(state: AgentState):
    logging.info("Using IoT_engine agent")
    user_query= state["query"]
    logging.info(f"user_query:  {user_query}")

    services_types= vector_search(user_query= user_query, limit= 3)
    logging.debug("Services types (top 3 in semantic meaning): " + str(services_types))

    collection = services_types[0]

    # Use actual user coordinates from location_finder_results
    location_data = state.get("location_finder_results", {})
    coordinates = location_data.get("coordinates", [])
    if coordinates and len(coordinates) >= 2:
        latitude = float(coordinates[0])
        longitude = float(coordinates[1])
    else:
        # Default fallback to Toronto center if no location provided
        latitude = 43.6914028
        longitude = -79.4037579
        logging.warning("No user coordinates found, using default Toronto center")

    results= get_nearByPlaces(latitude, longitude, collection, search_range=10000)

    ###################
    services=[service for service in results]

    # Capture raw data BEFORE get_recommendedSerivce strips fields
    raw_data = {}
    for service in services:
        key = service.get("Service Name", "")
        raw_data[key] = {
            "id": str(service.get("_id", "")),
            "name": service.get("Service Name", ""),
            "address": service.get("Service Address", ""),
            "rating": service.get("Rate"),
            "about": service.get("About"),
            "opening_hours": service.get("Opening/Closing Time"),
            "google_maps_url": service.get("Service URL"),
            "latitude": service.get("Latitude"),
            "longitude": service.get("Longitude"),
        }
        # Fallback to location.coordinates if Latitude/Longitude not present
        if raw_data[key]["latitude"] is None and "location" in service:
            coords = service["location"].get("coordinates", [])
            if len(coords) >= 2:
                raw_data[key]["longitude"] = coords[0]
                raw_data[key]["latitude"] = coords[1]

    for result in results:
        logging.info(result['Service Address'])
        logging.info(result['Service Name'])
        logging.info(result['location']['coordinates'])

    ResponseInJson=get_recommendedSerivce(longitude,latitude,services)
    logging.debug(ResponseInJson)
    if ResponseInJson:
        # Build places list by merging raw data with computed metrics
        places = []
        for service in ResponseInJson:
            name = service.get("Service Name", "")
            raw = raw_data.get(name, {})
            places.append({
                "id": raw.get("id", ""),
                "name": name,
                "address": raw.get("address") or service.get("Service Address", ""),
                "latitude": raw.get("latitude"),
                "longitude": raw.get("longitude"),
                "rating": raw.get("rating") or service.get("Rate"),
                "about": raw.get("about"),
                "opening_hours": raw.get("opening_hours"),
                "google_maps_url": raw.get("google_maps_url"),
                "travel_time_min": service.get("Estimated Travel Time (min)"),
                "occupancy": service.get("Occupancy"),
                "overall_service_time_min": service.get("Estimated Overall Service Time (min)"),
                "source": "iot_engine"
            })

        return prepaer_states({
            "messages": [ToolMessage(content=str(ResponseInJson), name="IoT_engine", tool_call_id="call_IoT_engine")],
            "node": "IoT_engine",
            "context": str(ResponseInJson),
            "call":"generator_agent",
            "places": places
        })
    else:
        return prepaer_states({"node": "IoT_engine", "call":"generator_agent"})
