from state_graph import AgentState

def assitant_router(state: AgentState):
    return state["call"]

def scrapper_router(state: AgentState):
    return state.get("call", "generator_agent")

def reviewer_router(state: AgentState):
    return state["call"]


def IoT_router(state: AgentState):
    return state["call"]

def googlemaps_router(state: AgentState):
    return state["call"]
