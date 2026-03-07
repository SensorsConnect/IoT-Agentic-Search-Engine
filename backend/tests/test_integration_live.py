"""
Integration tests that exercise the real LangGraph agents with live LLM calls.

Requirements:
    - A valid .env file in backend/ with API keys (GROQ_API_KEY, MONGODB_URL, etc.)
    - python-dotenv installed

Run with:
    cd backend && python -m pytest tests/test_integration_live.py -v -m integration

These tests are slow (real LLM round-trips) and are NOT run in CI by default.
"""
import os
import sys
import uuid

import pytest

# ---------------------------------------------------------------------------
# Load .env before any src imports (keys must be present for ChatGroq, etc.)
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# Add src/ to path so graph_init, agents, etc. can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

try:
    from graph_init import initialize_graph
except (ImportError, TypeError) as exc:
    pytest.skip(
        f"Cannot import graph (likely Python 3.13 + docarray incompatibility): {exc}",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Skip the entire module if required env vars are missing
# ---------------------------------------------------------------------------
REQUIRED_KEYS = ["GROQ_API_KEY", "MONGODB_URL"]
missing = [k for k in REQUIRED_KEYS if not os.environ.get(k)]
if missing:
    pytest.skip(f"Missing env vars: {missing}", allow_module_level=True)

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build():
    """Build a compiled graph with an in-memory checkpointer (no Postgres)."""
    graph = initialize_graph()
    return graph.compile(checkpointer=MemorySaver())


def _thread(tid=None):
    return {"configurable": {"thread_id": tid or str(uuid.uuid4())}}


def _invoke(runnable, text, thread, location=None):
    """Invoke the graph the same way production does."""
    content = text
    if location:
        content += f"\n\n[User Location: {location[0]}, {location[1]}]"
    return runnable.invoke(
        {"messages": [HumanMessage(content=content)], "query": content},
        thread,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGreetingLive:
    """assistant -> reviewer -> finalize -> END"""

    def test_greeting(self):
        r = _build()
        result = _invoke(r, "Hello! How are you?", _thread())

        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["node"] == "finalize_turn"
        assert len(result["thread_summary"]) == 2
        assert result["thread_summary"][0]["role"] == "user"
        assert result["thread_summary"][1]["role"] == "assistant"


class TestServiceRecommendationLive:
    """assistant -> IoT/GoogleMaps -> generator -> reviewer -> finalize"""

    @pytest.mark.skipif(
        not os.environ.get("GOOGLE_MAPS_API_KEY"),
        reason="GOOGLE_MAPS_API_KEY not set",
    )
    def test_service_recommendation(self):
        r = _build()
        result = _invoke(
            r,
            "Find coffee shops near me",
            _thread(),
            location=(43.6532, -79.3832),  # Toronto
        )

        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["node"] == "finalize_turn"


class TestHardQuestionLive:
    """assistant -> scrapper -> generator -> reviewer -> finalize"""

    def test_hard_question(self):
        r = _build()
        result = _invoke(r, "What is the capital of Mongolia?", _thread())

        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["node"] == "finalize_turn"


class TestMultiTurnLive:
    """Two turns on the same thread — thread_summary should accumulate."""

    def test_multi_turn(self):
        r = _build()
        thread = _thread()

        result1 = _invoke(r, "Hi there!", thread)
        assert len(result1["thread_summary"]) == 2

        result2 = _invoke(r, "What can you help me with?", thread)
        assert len(result2["thread_summary"]) == 4
        assert result2["thread_summary"][0]["role"] == "user"
        assert result2["thread_summary"][2]["role"] == "user"
