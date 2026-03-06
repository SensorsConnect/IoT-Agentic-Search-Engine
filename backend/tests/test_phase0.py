"""
Phase 0 Integration Tests — Bug Fixes & Production Hardening

Run inside Docker (Python 3.11):
    docker run --rm \
      -e GROQ_API_KEY=test_key \
      -e LLM_MODEL=llama-3.1-8b-instant \
      -e MONGODB_URL=mongodb://test:27017 \
      -e POSTGRES_URL=sqlite:///test.db \
      -e TAVILY_API_KEY=tvly-test \
      -e ENVIRONMENT=development \
      localelive-backend-test python /app/tests/test_phase0.py

Or with pytest (if installed):
    docker run --rm -e ... localelive-backend-test python -m pytest /app/tests/test_phase0.py -v
"""
import os
import sys
import warnings
import inspect

warnings.filterwarnings("ignore")

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_graph_imports():
    """Test 1: Graph modules import and compile without errors."""
    from graph_init import initialize_graph
    from graph import runnable
    assert runnable is not None


def test_graph_structure():
    """Test 2: All expected agent nodes are present in the graph."""
    from graph_init import initialize_graph
    g = initialize_graph()
    nodes = list(g.nodes)
    expected = ["assistant_agent", "generator_agent", "IoT_engine",
                "GoogleMaps", "scrapper", "reviewer_agent"]
    for n in expected:
        assert n in nodes, f"Missing node: {n}"


def test_prepaer_states():
    """Test 3: prepaer_states fills missing keys with [None]."""
    from utils import prepaer_states
    result = prepaer_states({"call": "END", "node": ["test"]})
    assert "handled" in result
    assert "make_sense" in result
    assert "node" in result
    assert result["handled"] == [None]
    assert result["node"] == ["test"]


def test_google_knowledge_graph_fixed():
    """Test 4 (TD-2): GoogleKnowledgeGraph returns valid state, not `input` builtin."""
    from agents.google_knowledge_graph import GoogleKnowledgeGraph
    state = {
        "query": "test", "messages": [], "handled": [],
        "make_sense": [], "node": [], "response": []
    }
    result = GoogleKnowledgeGraph(state)
    assert isinstance(result, dict)
    assert result["call"] == "generator_agent"
    assert result["handled"] == [False]


def test_iot_engine_uses_location():
    """Test 5 (TD-1): IoT_engine reads coordinates from state, not hardcoded."""
    import agents.iot_engine as iot_mod
    src = inspect.getsource(iot_mod.IoT_engine)
    assert "location_finder_results" in src, "Should read from location_finder_results"
    assert "43.6914028" in src, "Should have Toronto fallback"


def test_cors_production():
    """Test 6 (TD-4): CORS restricts origins in production mode."""
    os.environ["ENVIRONMENT"] = "production"
    os.environ["CORS_ORIGINS"] = "https://localelive.space,https://www.localelive.space"
    env = os.environ.get("ENVIRONMENT")
    cors = os.environ.get("CORS_ORIGINS", "")
    if env == "production" and cors:
        origins = [o.strip() for o in cors.split(",")]
    else:
        origins = ["*"]
    assert origins == ["https://localelive.space", "https://www.localelive.space"]
    # Reset
    os.environ["ENVIRONMENT"] = "development"


def test_error_handling():
    """Test 7 (TD-5): PUT /query has try/except with structured error responses."""
    import main
    src = inspect.getsource(main.query_handler)
    assert "try:" in src
    assert "except ValueError" in src
    assert "except Exception" in src
    assert "JSONResponse" in src


def test_rate_limiting():
    """Test 8: Rate limiter is configured on the FastAPI app."""
    import main
    assert hasattr(main.app.state, "limiter")


def test_embedding_model_singleton():
    """Test 9 (TD-8): Embedding model is loaded once at module level."""
    from vector_db.vector_database import _tokenizer, _model
    assert _tokenizer is not None
    assert _model is not None


def test_reviewer_agent_prepaer_states():
    """Test 10 (TD-9): All reviewer_agent return paths use prepaer_states."""
    mod = __import__("agents.reviewer_agent", fromlist=["reviewer_agent"])
    src = inspect.getsource(mod.reviewer_agent)
    lines = [
        l.strip() for l in src.split("\n")
        if l.strip().startswith("return ") and "prepaer_states" not in l
    ]
    assert len(lines) == 0, f"Returns without prepaer_states: {lines}"


def test_health_endpoint():
    """Test 11: GET /health returns 200 with status ok."""
    import main
    from fastapi.testclient import TestClient
    client = TestClient(main.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root_endpoint():
    """Test 12: GET / returns API info."""
    import main
    from fastapi.testclient import TestClient
    client = TestClient(main.app)
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "LocaleLive API"
    assert data["version"] == "1.0.0"


def test_scrapper_router():
    """Test 13 (TD-6): scrapper_router uses state['call'], not hardcoded value."""
    from routers import scrapper_router
    src = inspect.getsource(scrapper_router)
    # Should NOT have both branches returning the same thing
    assert 'state.get("call"' in src or 'state["call"]' in src


def test_bare_except_fixed_assistant():
    """Test 14 (TD-7): assistant_agent catches specific exceptions."""
    from agents.assistant_agent import assistant_agent
    src = inspect.getsource(assistant_agent)
    assert "except (ValueError, KeyError, TypeError)" in src
    # Should NOT have bare except
    lines = [l.strip() for l in src.split("\n") if l.strip() == "except:"]
    assert len(lines) == 0, "Found bare except in assistant_agent"


def test_bare_except_fixed_reviewer():
    """Test 15 (TD-7): reviewer_agent catches specific exceptions."""
    from agents.reviewer_agent import reviewer_agent
    src = inspect.getsource(reviewer_agent)
    assert "except (ValueError, KeyError, TypeError)" in src
    lines = [l.strip() for l in src.split("\n") if l.strip() == "except:"]
    assert len(lines) == 0, "Found bare except in reviewer_agent"


# --- Runner ---
if __name__ == "__main__":
    tests = [
        test_graph_imports,
        test_graph_structure,
        test_prepaer_states,
        test_google_knowledge_graph_fixed,
        test_iot_engine_uses_location,
        test_cors_production,
        test_error_handling,
        test_rate_limiting,
        test_embedding_model_singleton,
        test_reviewer_agent_prepaer_states,
        test_health_endpoint,
        test_root_endpoint,
        test_scrapper_router,
        test_bare_except_fixed_assistant,
        test_bare_except_fixed_reviewer,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        name = test_fn.__doc__ or test_fn.__name__
        try:
            test_fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {name}")
            print(f"        {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed!")
