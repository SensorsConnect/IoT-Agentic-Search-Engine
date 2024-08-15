import logging
from state_graph import AgentState

def IoT_engine(state: AgentState):
    logging.info("Using branch B")
    return input