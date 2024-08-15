import logging
from state_graph import AgentState
from utils import prepaer_states
def reviewer_agent(state: AgentState):
    logging.info("entering reviewer node")
    dictionary = {"handled": [True], "make_sense": [True]}
    return prepaer_states(dictionary)