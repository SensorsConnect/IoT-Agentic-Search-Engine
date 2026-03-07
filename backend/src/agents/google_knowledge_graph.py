import logging
from state_graph import AgentState
from utils import prepaer_states

def GoogleKnowledgeGraph(state: AgentState):
    logging.warning("GoogleKnowledgeGraph is deprecated and should not be called")
    return prepaer_states({
        "node": "GoogleKnowledgeGraph",
        "call": "generator_agent"
    })
