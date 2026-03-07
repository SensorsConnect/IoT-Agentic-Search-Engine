"""
LangGraph Route Tests — verify every path through the agent graph after refactor.

Run with:
    cd backend && python -m pytest tests/test_langgraph_routes.py -v

These tests build the same graph topology as production but replace every node
with a lightweight mock. No LLM calls, no MongoDB, no external APIs.
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore")

os.environ.setdefault("POSTGRES_URL", "sqlite:///test_routes.db")
os.environ.setdefault("GROQ_API_KEY", "test_key")
os.environ.setdefault("LLM_MODEL", "test")
os.environ.setdefault("MONGODB_URL", "mongodb://test:27017")
os.environ.setdefault("TAVILY_API_KEY", "test_key")

import pytest
from typing import TypedDict, Annotated, Sequence, List
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, filter_messages
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver


# ---------------------------------------------------------------------------
# Inline AgentState (avoids importing src/ which pulls in heavy deps)
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    context: str
    response: str
    call: str
    node: str
    location_finder_results: dict
    thread_summary: Annotated[List[dict], operator.add]


# ---------------------------------------------------------------------------
# Inline routers (exact copies from src/routers.py)
# ---------------------------------------------------------------------------

def assitant_router(state):
    return state["call"]

def scrapper_router(state):
    return state.get("call", "generator_agent")

def reviewer_router(state):
    return state["call"]

def IoT_router(state):
    return state["call"]

def googlemaps_router(state):
    return state["call"]

def knowledge_graph_router(state):
    return "END"


# ---------------------------------------------------------------------------
# Inline finalize_turn (exact copy from src/agents/finalize.py)
# ---------------------------------------------------------------------------

def finalize_turn(state):
    query_text = state.get("query", "")
    if not query_text:
        human_msgs = filter_messages(state["messages"], include_types="human")
        query_text = human_msgs[-1].content if human_msgs else ""
    response_text = state.get("response", "")
    if not response_text:
        return {"node": "finalize_turn"}
    return {
        "node": "finalize_turn",
        "thread_summary": [
            {"role": "user", "content": query_text},
            {"role": "assistant", "content": response_text},
        ],
    }


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_graph(node_fns: dict):
    """Build and compile a LangGraph matching production topology."""
    graph = StateGraph(AgentState)
    for name, fn in node_fns.items():
        graph.add_node(name, fn)
    graph.add_node("finalize_turn", finalize_turn)

    graph.add_conditional_edges(
        "assistant_agent", assitant_router,
        {"reviewer_agent": "reviewer_agent", "IoT_engine": "IoT_engine",
         "GoogleMaps": "GoogleMaps", "scrapper": "scrapper"},
    )
    graph.add_conditional_edges(
        "scrapper", scrapper_router,
        {"generator_agent": "generator_agent", "GoogleKnowledgeGraph": "GoogleKnowledgeGraph"},
    )
    graph.add_conditional_edges(
        "IoT_engine", IoT_router,
        {"generator_agent": "generator_agent", "GoogleMaps": "GoogleMaps"},
    )
    graph.add_conditional_edges(
        "GoogleMaps", googlemaps_router,
        {"generator_agent": "generator_agent", "scrapper": "scrapper"},
    )
    graph.add_conditional_edges(
        "GoogleKnowledgeGraph", knowledge_graph_router,
        {"generator_agent": "generator_agent", "scrapper": "scrapper"},
    )
    graph.add_edge("generator_agent", "reviewer_agent")
    graph.add_conditional_edges(
        "reviewer_agent", reviewer_router,
        {"IoT_engine": "IoT_engine", "scrapper": "scrapper",
         "GoogleMaps": "GoogleMaps", "END": "finalize_turn"},
    )
    graph.add_edge("finalize_turn", END)
    graph.set_entry_point("assistant_agent")

    return graph.compile(checkpointer=MemorySaver())


# ---------------------------------------------------------------------------
# Mock node factories
# ---------------------------------------------------------------------------

def make_assistant_greeting(response_text="Hello!"):
    def fn(state):
        return {
            "node": "assistant_agent",
            "call": "reviewer_agent",
            "response": response_text,
            "messages": [AIMessage(content=response_text)],
        }
    return fn


def make_assistant_service(call="IoT_engine", query="coffee shops", location=None):
    def fn(state):
        r = {
            "node": "assistant_agent",
            "call": call,
            "query": query,
            "messages": [AIMessage(content="Routing to " + call)],
        }
        if location:
            r["location_finder_results"] = location
        return r
    return fn


def make_assistant_hard_question(query="What is quantum computing?"):
    def fn(state):
        return {
            "node": "assistant_agent",
            "call": "scrapper",
            "query": query,
            "messages": [AIMessage(content="Routing to scrapper")],
        }
    return fn


def make_iot_engine(has_results=True, context="[{service: 'coffee'}]"):
    def fn(state):
        if has_results:
            return {
                "messages": [ToolMessage(content=context, name="IoT_engine", tool_call_id="call_IoT")],
                "node": "IoT_engine", "context": context, "call": "generator_agent",
            }
        return {"node": "IoT_engine", "call": "generator_agent"}
    return fn


def make_google_maps(has_results=True, context="[{place: 'Starbucks'}]"):
    def fn(state):
        if has_results:
            return {
                "messages": [ToolMessage(content=context, name="GoogleMaps", tool_call_id="call_GM")],
                "node": "GoogleMaps", "context": context, "call": "generator_agent",
            }
        return {"node": "GoogleMaps", "call": "generator_agent"}
    return fn


def make_scrapper(has_results=True, context="Web search result"):
    def fn(state):
        if has_results:
            return {
                "messages": [ToolMessage(content=context, name="scrapper", tool_call_id="call_scr")],
                "node": "scrapper", "context": context, "call": "generator_agent",
            }
        return {"node": "scrapper", "call": "generator_agent"}
    return fn


def make_generator(response_text="Here are your results."):
    def fn(state):
        return {
            "messages": [AIMessage(content=response_text)],
            "node": "generator_agent",
            "response": response_text,
        }
    return fn


def make_generator_fallback():
    """Generator that cascades: IoT->GoogleMaps->scrapper when no context."""
    def fn(state):
        ctx = state.get("context", "")
        node = state.get("node", "")
        if ctx == "":
            if node == "IoT_engine":
                return {"node": "generator_agent", "response": "", "call": "GoogleMaps"}
            elif node == "GoogleMaps":
                return {"node": "generator_agent", "response": "", "call": "scrapper"}
            else:
                return {"node": "generator_agent", "response": "I can't handle this", "call": "scrapper"}
        return {
            "messages": [AIMessage(content="Generated response")],
            "node": "generator_agent",
            "response": "Generated response",
        }
    return fn


def make_reviewer_accept():
    def fn(state):
        return {"node": "reviewer", "call": "END"}
    return fn


def make_reviewer_reject_to(target="scrapper", query="refined"):
    counter = {"n": 0}
    def fn(state):
        counter["n"] += 1
        if counter["n"] == 1:
            return {"node": "reviewer", "call": target, "query": query,
                    "messages": [AIMessage(content="Needs more info")]}
        return {"node": "reviewer", "call": "END"}
    return fn


def make_google_knowledge_graph():
    def fn(state):
        return {"node": "GoogleKnowledgeGraph", "call": "generator_agent"}
    return fn


def _thread(tid="t1"):
    return {"configurable": {"thread_id": tid}}


def _default_nodes(**overrides):
    """Return a full set of mock nodes, with optional overrides."""
    nodes = {
        "assistant_agent": make_assistant_greeting(),
        "reviewer_agent": make_reviewer_accept(),
        "generator_agent": make_generator(),
        "IoT_engine": make_iot_engine(),
        "GoogleMaps": make_google_maps(),
        "scrapper": make_scrapper(),
        "GoogleKnowledgeGraph": make_google_knowledge_graph(),
    }
    nodes.update(overrides)
    return nodes


# ===========================================================================
# TEST CASES
# ===========================================================================


class TestGreetingRoute:
    """Route: assistant -> reviewer -> finalize_turn -> END"""

    def test_greeting_basic(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting("Hi there!"),
        ))
        result = r.invoke({"messages": [HumanMessage(content="Hello")], "query": "Hello"}, _thread("g1"))

        assert isinstance(result["response"], str)
        assert result["response"] == "Hi there!"
        assert result["node"] == "finalize_turn"
        assert len(result["thread_summary"]) == 2
        assert result["thread_summary"][0]["role"] == "user"
        assert result["thread_summary"][1] == {"role": "assistant", "content": "Hi there!"}

    def test_greeting_empty_response_no_crash(self):
        """Empty response must not raise InvalidUpdateError in finalize_turn."""
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting(""),
        ))
        result = r.invoke({"messages": [HumanMessage(content="Hello")], "query": "Hello"}, _thread("g2"))
        assert result["node"] == "finalize_turn"
        # No thread_summary since response was empty
        assert "thread_summary" not in result or len(result.get("thread_summary", [])) == 0


class TestIoTRoute:
    """Route: assistant -> IoT_engine -> generator -> reviewer -> finalize -> END"""

    def test_iot_with_results(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_service(
                call="IoT_engine", query="coffee shops",
                location={"coordinates": [43.65, -79.38]}),
            IoT_engine=make_iot_engine(has_results=True, context="[{name:'Tim Hortons'}]"),
            generator_agent=make_generator("Coffee shops near you."),
        ))
        result = r.invoke({"messages": [HumanMessage(content="coffee shops")], "query": "coffee shops"}, _thread("iot1"))

        assert result["response"] == "Coffee shops near you."
        assert result["node"] == "finalize_turn"
        assert len(result["thread_summary"]) == 2
        assert result["thread_summary"][0]["content"] == "coffee shops"

    def test_iot_no_results_fallback_to_googlemaps(self):
        """IoT(no context) -> generator(call=GoogleMaps) -> reviewer(routes to GoogleMaps)
        -> GoogleMaps -> generator -> reviewer(accept) -> finalize."""
        rev_count = {"n": 0}
        def reviewer_fallback(state):
            rev_count["n"] += 1
            resp = state.get("response", "")
            call = state.get("call", "END")
            # First time: empty response, forward the generator's call
            if rev_count["n"] == 1 and resp == "":
                return {"node": "reviewer", "call": call}
            return {"node": "reviewer", "call": "END"}

        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_service(
                call="IoT_engine", query="restaurants",
                location={"coordinates": [43.65, -79.38]}),
            IoT_engine=make_iot_engine(has_results=False),
            generator_agent=make_generator_fallback(),
            GoogleMaps=make_google_maps(has_results=True, context="[{place:'Pizza'}]"),
            reviewer_agent=reviewer_fallback,
        ))
        result = r.invoke({"messages": [HumanMessage(content="restaurants")], "query": "restaurants"}, _thread("iot2"))
        assert result["response"] == "Generated response"
        assert result["node"] == "finalize_turn"


class TestGoogleMapsRoute:
    """Route: assistant -> GoogleMaps -> generator -> reviewer -> finalize -> END"""

    def test_googlemaps_with_results(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_service(
                call="GoogleMaps", query="pharmacies",
                location={"coordinates": [40.71, -74.00]}),
            GoogleMaps=make_google_maps(has_results=True, context="[{place:'CVS'}]"),
            generator_agent=make_generator("Pharmacies nearby."),
        ))
        result = r.invoke({"messages": [HumanMessage(content="pharmacies")], "query": "pharmacies"}, _thread("gm1"))
        assert result["response"] == "Pharmacies nearby."
        assert result["node"] == "finalize_turn"

    def test_googlemaps_no_results_fallback_to_scrapper(self):
        """GoogleMaps(no context) -> generator(call=scrapper) -> reviewer(routes to scrapper)
        -> scrapper -> generator -> reviewer(accept) -> finalize."""
        rev_count = {"n": 0}
        def reviewer_fallback(state):
            rev_count["n"] += 1
            resp = state.get("response", "")
            call = state.get("call", "END")
            if rev_count["n"] == 1 and resp == "":
                return {"node": "reviewer", "call": call}
            return {"node": "reviewer", "call": "END"}

        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_service(
                call="GoogleMaps", query="rare bookstore",
                location={"coordinates": [40.71, -74.00]}),
            GoogleMaps=make_google_maps(has_results=False),
            generator_agent=make_generator_fallback(),
            scrapper=make_scrapper(has_results=True, context="Bookstore found online"),
            reviewer_agent=reviewer_fallback,
        ))
        result = r.invoke({"messages": [HumanMessage(content="rare bookstore")], "query": "rare bookstore"}, _thread("gm2"))
        assert result["response"] == "Generated response"
        assert result["node"] == "finalize_turn"


class TestScrapperRoute:
    """Route: assistant -> scrapper -> generator -> reviewer -> finalize -> END"""

    def test_scrapper_with_results(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_hard_question("What is quantum computing?"),
            scrapper=make_scrapper(has_results=True, context="Quantum uses qubits..."),
            generator_agent=make_generator("Quantum computing is..."),
        ))
        result = r.invoke({"messages": [HumanMessage(content="quantum?")], "query": "quantum?"}, _thread("sc1"))
        assert result["response"] == "Quantum computing is..."
        assert result["node"] == "finalize_turn"


class TestReviewerLoopRoute:
    """Reviewer rejects and loops back to another agent."""

    def test_reviewer_rejects_to_scrapper(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_service(call="IoT_engine", query="gyms"),
            IoT_engine=make_iot_engine(has_results=True),
            generator_agent=make_generator("Gyms found."),
            reviewer_agent=make_reviewer_reject_to(target="scrapper", query="gyms web"),
            scrapper=make_scrapper(has_results=True, context="More gyms"),
        ))
        result = r.invoke({"messages": [HumanMessage(content="gyms")], "query": "gyms"}, _thread("rl1"))
        assert result["node"] == "finalize_turn"
        assert isinstance(result["response"], str)

    def test_reviewer_rejects_to_googlemaps(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting("Hello"),
            generator_agent=make_generator("Updated results."),
            reviewer_agent=make_reviewer_reject_to(target="GoogleMaps", query="pizza"),
            GoogleMaps=make_google_maps(has_results=True, context="[{place:'Dominos'}]"),
        ))
        result = r.invoke({"messages": [HumanMessage(content="pizza")], "query": "pizza"}, _thread("rl2"))
        assert result["node"] == "finalize_turn"

    def test_reviewer_rejects_to_iot(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting("Hello"),
            generator_agent=make_generator("Parking found."),
            reviewer_agent=make_reviewer_reject_to(target="IoT_engine", query="parking"),
            IoT_engine=make_iot_engine(has_results=True, context="[{service:'parking'}]"),
        ))
        result = r.invoke({"messages": [HumanMessage(content="parking")], "query": "parking"}, _thread("rl3"))
        assert result["node"] == "finalize_turn"


class TestStateSchema:
    """Verify the refactored state schema is correct."""

    def _run_greeting(self, tid):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting("Hi!"),
        ))
        return r, r.invoke({"messages": [HumanMessage(content="hi")], "query": "hi"}, _thread(tid))

    def test_response_is_string(self):
        _, result = self._run_greeting("ss1")
        assert isinstance(result["response"], str)
        assert not isinstance(result["response"], list)

    def test_node_is_string(self):
        _, result = self._run_greeting("ss2")
        assert isinstance(result["node"], str)
        assert not isinstance(result["node"], list)

    def test_no_handled_or_make_sense(self):
        _, result = self._run_greeting("ss3")
        assert "handled" not in result
        assert "make_sense" not in result

    def test_thread_summary_accumulates_across_turns(self):
        r = _build_graph(_default_nodes(
            assistant_agent=make_assistant_greeting("Hello!"),
        ))
        thread = _thread("ss4")

        result1 = r.invoke({"messages": [HumanMessage(content="Hi")], "query": "Hi"}, thread)
        assert len(result1["thread_summary"]) == 2

        result2 = r.invoke({"messages": [HumanMessage(content="How are you?")], "query": "How are you?"}, thread)
        assert len(result2["thread_summary"]) == 4
        assert result2["thread_summary"][0]["role"] == "user"
        assert result2["thread_summary"][2]["role"] == "user"


class TestFullFallbackCascade:
    """IoT(empty) -> GoogleMaps(empty) -> scrapper(results) full cascade."""

    def test_iot_to_googlemaps_to_scrapper(self):
        """Full cascade: IoT(empty) -> gen(call=GM) -> reviewer(forward GM) ->
        GoogleMaps(empty) -> gen(call=scr) -> reviewer(forward scr) ->
        scrapper(results) -> gen(response) -> reviewer(accept) -> finalize."""
        call_log = []
        rev_count = {"n": 0}

        def iot(state):
            call_log.append("IoT_engine")
            return {"node": "IoT_engine", "call": "generator_agent"}

        def gmaps(state):
            call_log.append("GoogleMaps")
            return {"node": "GoogleMaps", "call": "generator_agent"}

        def scr(state):
            call_log.append("scrapper")
            return {
                "messages": [ToolMessage(content="Web", name="scrapper", tool_call_id="x")],
                "node": "scrapper", "context": "Web result", "call": "generator_agent",
            }

        def gen(state):
            call_log.append(f"gen(node={state.get('node','')})")
            ctx = state.get("context", "")
            node = state.get("node", "")
            if ctx == "":
                if node == "IoT_engine":
                    return {"node": "generator_agent", "response": "", "call": "GoogleMaps"}
                elif node == "GoogleMaps":
                    return {"node": "generator_agent", "response": "", "call": "scrapper"}
            return {
                "messages": [AIMessage(content="Final")],
                "node": "generator_agent", "response": "Final answer",
            }

        def reviewer(state):
            rev_count["n"] += 1
            resp = state.get("response", "")
            call = state.get("call", "END")
            # Forward fallback calls from generator when response is empty
            if resp == "" and call in ("GoogleMaps", "scrapper", "IoT_engine"):
                return {"node": "reviewer", "call": call}
            return {"node": "reviewer", "call": "END"}

        r = _build_graph({
            "assistant_agent": make_assistant_service(call="IoT_engine", query="sushi"),
            "IoT_engine": iot, "GoogleMaps": gmaps, "scrapper": scr,
            "generator_agent": gen,
            "reviewer_agent": reviewer,
            "GoogleKnowledgeGraph": make_google_knowledge_graph(),
        })
        result = r.invoke({"messages": [HumanMessage(content="sushi")], "query": "sushi"}, _thread("fc1"))

        assert "IoT_engine" in call_log
        assert "GoogleMaps" in call_log
        assert "scrapper" in call_log
        assert result["response"] == "Final answer"
        assert result["node"] == "finalize_turn"


class TestFinalizeTurnUnit:
    """Direct unit tests for finalize_turn function."""

    def test_with_response(self):
        result = finalize_turn({
            "messages": [HumanMessage(content="q")],
            "query": "test query", "response": "test response",
            "node": "reviewer", "context": "", "call": "END",
        })
        assert result["thread_summary"][0] == {"role": "user", "content": "test query"}
        assert result["thread_summary"][1] == {"role": "assistant", "content": "test response"}

    def test_empty_response_returns_nonempty_dict(self):
        result = finalize_turn({
            "messages": [HumanMessage(content="q")],
            "query": "q", "response": "", "node": "r", "context": "", "call": "END",
        })
        assert result != {}
        assert "node" in result

    def test_empty_query_uses_messages(self):
        result = finalize_turn({
            "messages": [HumanMessage(content="from messages")],
            "query": "", "response": "resp", "node": "r", "context": "", "call": "END",
        })
        assert result["thread_summary"][0]["content"] == "from messages"


class TestReviewerEmptyResponse:
    """Reviewer handles empty response without crashing."""

    def test_empty_response_chain(self):
        """IoT(empty) -> generator(empty resp, route GM) -> reviewer(empty resp, END) -> finalize."""
        rev_count = {"n": 0}
        def reviewer(state):
            rev_count["n"] += 1
            resp = state.get("response", "")
            if resp == "":
                return {"node": "reviewer", "call": "END"}
            return {"node": "reviewer", "call": "END"}

        def gen(state):
            ctx = state.get("context", "")
            node = state.get("node", "")
            if ctx == "":
                if node == "IoT_engine":
                    return {"node": "generator_agent", "response": "", "call": "GoogleMaps"}
                elif node == "GoogleMaps":
                    return {"node": "generator_agent", "response": "", "call": "scrapper"}
            return {
                "messages": [AIMessage(content="park info")],
                "node": "generator_agent", "response": "park info",
            }

        r = _build_graph({
            "assistant_agent": make_assistant_service(call="IoT_engine", query="parks"),
            "IoT_engine": make_iot_engine(has_results=False),
            "GoogleMaps": make_google_maps(has_results=False),
            "scrapper": make_scrapper(has_results=True, context="park data"),
            "generator_agent": gen,
            "reviewer_agent": reviewer,
            "GoogleKnowledgeGraph": make_google_knowledge_graph(),
        })
        result = r.invoke({"messages": [HumanMessage(content="parks")], "query": "parks"}, _thread("re1"))
        assert result["node"] == "finalize_turn"
