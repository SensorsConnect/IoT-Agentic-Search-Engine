from langchain_core.messages import filter_messages
from state_graph import AgentState


def finalize_turn(state: AgentState):
    query_text = state.get("query", "")
    if not query_text:
        human_msgs = filter_messages(state["messages"], include_types="human")
        query_text = human_msgs[-1].content if human_msgs else ""

    response_text = state.get("response", "")
    if not response_text:
        # Must always write at least one key — LangGraph rejects empty dicts
        return {"node": "finalize_turn"}

    return {
        "node": "finalize_turn",
        "thread_summary": [
            {"role": "user", "content": query_text},
            {"role": "assistant", "content": response_text},
        ]
    }
