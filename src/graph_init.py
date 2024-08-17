from langgraph.graph import END, StateGraph
from state_graph import AgentState
from agents import (
    assistant_agent,
    generator_agent,
    IoT_engine,
    GoogleMaps,
    GoogleKnowledgeGraph,
    scrapper,
    reviewer_agent
)
from routers import (
    assitant_router,
    scrapper_router,
    reviewer_router,
    IoT_router,
    googlemaps_router,
    router
)

def initialize_graph():
    graph = StateGraph(AgentState)
    graph.add_node("assistant_agent", assistant_agent)
    graph.add_node("generator_agent", generator_agent)
    graph.add_node("IoT_engine", IoT_engine)
    graph.add_node("GoogleMaps", GoogleMaps)
    graph.add_node("GoogleKnowledgeGraph", GoogleKnowledgeGraph)
    graph.add_node("scrapper", scrapper)
    graph.add_node("reviewer_agent", reviewer_agent)

    graph.add_conditional_edges(
        "assistant_agent", assitant_router, {"reviewer_agent": "reviewer_agent",
                                              "IoT_engine": "IoT_engine",
                                              "GoogleMaps":"GoogleMaps",
                                              "scrapper": "scrapper"}
    )

    graph.add_conditional_edges(
        "scrapper", scrapper_router, {"generator_agent": "generator_agent", "GoogleKnowledgeGraph": "GoogleKnowledgeGraph"}
    )

    graph.add_conditional_edges(
        "IoT_engine", IoT_router, {"generator_agent": "generator_agent", "GoogleMaps": "GoogleMaps"}
    )

    graph.add_conditional_edges(
        "GoogleMaps", googlemaps_router, {"generator_agent": "generator_agent", "scrapper": "scrapper"}
    )

    graph.add_conditional_edges(
        "GoogleKnowledgeGraph", router, {"generator_agent": "generator_agent", "scrapper": "scrapper"}
    )

    graph.add_edge("generator_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent", reviewer_router, {"scrapper": "scrapper", "GoogleMaps": "GoogleMaps", "END": END}
    )

    graph.set_entry_point("assistant_agent")
    
    return graph
