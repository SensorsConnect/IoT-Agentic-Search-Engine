from typing import TypedDict, Annotated, Sequence, List
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    context: str
    response: str
    call: str
    node: str
    location_finder_results: dict
    thread_summary: Annotated[List[dict], operator.add]
    places: List[dict]
    search_type: str
    user_location: dict
    correlation_id: str
