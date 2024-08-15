import logging
from state_graph import AgentState
from vector_db.vector_database import vector_search
from mongo_db.database_connection import get_nearByPlaces
from serivce_recommender.sorting_serivces import get_recommendedSerivce
from utils import prepaer_states
from langchain_core.messages import ToolMessage

def IoT_engine(state: AgentState):
    print("IoT_engine insde here")
    logging.info("Using IoT_engine agent")
    user_query= state["query"]
    logging.info(f"user_query:  {user_query}")
    print(f"user_query:  {user_query}")


    services_types= vector_search(user_query= user_query, limit= 3)
    # print("Query type: " + query_type)
    logging.debug("Services types (top 3 in semantic meaning): " + str(services_types))


    collection = services_types[0]
    latitude= 43.6914028
    longitude= -79.4037579
    results= get_nearByPlaces(latitude, longitude, collection, search_range=10000)
    
    ###################
    services=[service for service in results]
    
    for result in results:
        logging.info(result['Service Address'])
        logging.info(result['Service Name'])
        logging.info(result['location']['coordinates'])

    print(services)
    ResponseInJson=get_recommendedSerivce(longitude,latitude,services)
    logging.debug(ResponseInJson)
    if ResponseInJson:
        return prepaer_states({
            "messages": [ToolMessage(content=str(ResponseInJson), name="IoT_engine", tool_call_id="call_IoT_engine")],
            "handled": [True],
            "node": ["IoT_engine"],
            "context": str(ResponseInJson),
            "call":"generator_agent"
        })
    else:
        return prepaer_states({"handled": [False], "call":"generator_agent"})