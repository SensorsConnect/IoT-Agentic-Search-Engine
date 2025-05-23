import logging
from state_graph import AgentState
def assitant_router(state: AgentState):
    return state["call"]

def scrapper_router(state: AgentState):
    logging.info("STATE at assistant_router:", state)
    last_handled = state["handled"]
    if last_handled:
        return "generator_agent"
    else:
        return "generator_agent"

# def reviewer_router(state: AgentState):
#     logging.info("I'm in reviewer router")
#     if state["make_sense"]:
#         return "END"
#     else:
#         return "IoT_engine"
def reviewer_router(state: AgentState):
    logging.info("I'm in reviewer router")
    return state["call"]


def IoT_router(state: AgentState):
    return state["call"]

def router(state: AgentState):
    return "END"

def googlemaps_router(state: AgentState):
    return state["call"]
