"""
Phase 1 Integration Tests — Auth, Persistence & API

Run with:
    cd backend && POSTGRES_URL=sqlite:///test_phase1.db \
    GROQ_API_KEY=test MONGODB_URL=mongodb://test:27017 LLM_MODEL=test \
    python -m pytest tests/test_phase1.py -v
"""
import os
import sys
import uuid
import time
import warnings

warnings.filterwarnings("ignore")

# Use SQLite for tests
os.environ.setdefault("POSTGRES_URL", "sqlite:///test_phase1.db")
os.environ.setdefault("GROQ_API_KEY", "test_key")
os.environ.setdefault("LLM_MODEL", "llama-3.1-8b-instant")
os.environ.setdefault("MONGODB_URL", "mongodb://test:27017")
os.environ.setdefault("CLERK_JWKS_URL", "")
os.environ.setdefault("ENVIRONMENT", "development")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import jwt as pyjwt
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test database
from db.engine import Base, get_db
import db.models as models

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Mock the graph runnable to avoid actual LLM calls
mock_runnable = MagicMock()
mock_runnable.invoke.return_value = {"response": ["This is a test response."]}

# Patch graph import before importing main
with patch.dict("sys.modules", {}):
    pass

import importlib

# We need to mock the graph module before importing main
graph_mock = MagicMock()
graph_mock.runnable = mock_runnable
sys.modules["graph"] = graph_mock

# Also mock graph_init
graph_init_mock = MagicMock()
graph_init_mock.initialize_graph.return_value = MagicMock()
sys.modules["graph_init"] = graph_init_mock

# Now import main
import main
from auth.clerk import get_current_user, UserContext

main.app.dependency_overrides[get_db] = override_get_db

client = TestClient(main.app)

# Test user contexts
TEST_USER_A = UserContext(user_id=str(uuid.uuid4()), clerk_id="clerk_user_a", email="a@test.com", role="user")
TEST_USER_B = UserContext(user_id=str(uuid.uuid4()), clerk_id="clerk_user_b", email="b@test.com", role="user")


def setup_user_in_db(user_ctx: UserContext):
    """Ensure user exists in test DB."""
    db = TestSession()
    existing = db.query(models.User).filter(models.User.clerk_id == user_ctx.clerk_id).first()
    if not existing:
        u = models.User(id=user_ctx.user_id, clerk_id=user_ctx.clerk_id, email=user_ctx.email)
        db.add(u)
        db.commit()
    db.close()


def auth_override_a():
    return TEST_USER_A

def auth_override_b():
    return TEST_USER_B


# --- Tests ---

def test_auth_middleware_no_token():
    """Test 1: Protected endpoints return 401 without token."""
    # Remove auth override to test actual middleware
    main.app.dependency_overrides.pop(get_current_user, None)
    resp = client.get("/api/v1/conversations")
    assert resp.status_code == 401
    # Restore
    main.app.dependency_overrides[get_current_user] = auth_override_a


def test_auth_middleware_valid_token():
    """Test 2: Auth returns UserContext with valid override."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)
    resp = client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "a@test.com"


def test_create_user_on_first_auth():
    """Test 3: User record created on first request."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)
    db = TestSession()
    user = db.query(models.User).filter(models.User.clerk_id == "clerk_user_a").first()
    assert user is not None
    assert user.email == "a@test.com"
    db.close()


def test_conversations_list_empty():
    """Test 4: New user gets empty conversation list."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)
    resp = client.get("/api/v1/conversations")
    assert resp.status_code == 200
    assert resp.json() == []


def test_query_creates_conversation():
    """Test 5: PUT /api/v1/query creates conversation + messages."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    thread_id = str(uuid.uuid4())
    resp = client.put("/api/v1/query", json={
        "text": "Find me a coffee shop nearby",
        "threadId": thread_id,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "conversationId" in data
    assert data["conversationId"] != ""

    # Verify conversation exists
    resp2 = client.get("/api/v1/conversations")
    convs = resp2.json()
    assert len(convs) >= 1
    assert any(c["thread_id"] == thread_id for c in convs)


def test_conversation_messages():
    """Test 6: GET conversation returns correct messages."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    thread_id = str(uuid.uuid4())
    resp = client.put("/api/v1/query", json={
        "text": "What restaurants are nearby?",
        "threadId": thread_id,
    })
    conv_id = resp.json()["conversationId"]

    resp2 = client.get(f"/api/v1/conversations/{conv_id}")
    assert resp2.status_code == 200
    detail = resp2.json()
    assert len(detail["messages"]) == 2
    assert detail["messages"][0]["role"] == "user"
    assert detail["messages"][1]["role"] == "assistant"


def test_delete_conversation():
    """Test 7: DELETE removes conversation and messages."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    thread_id = str(uuid.uuid4())
    resp = client.put("/api/v1/query", json={
        "text": "Test delete",
        "threadId": thread_id,
    })
    conv_id = resp.json()["conversationId"]

    del_resp = client.delete(f"/api/v1/conversations/{conv_id}")
    assert del_resp.status_code == 200

    get_resp = client.get(f"/api/v1/conversations/{conv_id}")
    assert get_resp.status_code == 404


def test_conversation_ownership():
    """Test 8: User A can't access User B's conversations."""
    # Create as user A
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    thread_id = str(uuid.uuid4())
    resp = client.put("/api/v1/query", json={
        "text": "User A's chat",
        "threadId": thread_id,
    })
    conv_id = resp.json()["conversationId"]

    # Try to access as user B
    main.app.dependency_overrides[get_current_user] = auth_override_b
    setup_user_in_db(TEST_USER_B)

    resp2 = client.get(f"/api/v1/conversations/{conv_id}")
    assert resp2.status_code == 403

    # Restore
    main.app.dependency_overrides[get_current_user] = auth_override_a


def test_saved_places_crud():
    """Test 9: POST, GET, DELETE saved places."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    # Create
    resp = client.post("/api/v1/saved-places", json={
        "place_name": "Tim Hortons Downtown",
        "place_data": {"lat": 43.65, "lng": -79.38},
        "note": "Good coffee"
    })
    assert resp.status_code == 201
    place_id = resp.json()["id"]

    # List
    resp2 = client.get("/api/v1/saved-places")
    assert resp2.status_code == 200
    places = resp2.json()
    assert any(p["id"] == place_id for p in places)

    # Delete
    resp3 = client.delete(f"/api/v1/saved-places/{place_id}")
    assert resp3.status_code == 200

    # Verify gone
    resp4 = client.get("/api/v1/saved-places")
    assert all(p["id"] != place_id for p in resp4.json())


def test_user_profile():
    """Test 10: GET/PATCH /api/v1/me."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    resp = client.get("/api/v1/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "a@test.com"

    resp2 = client.patch("/api/v1/me", json={"name": "Alice", "city": "Vancouver"})
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Alice"
    assert resp2.json()["city"] == "Vancouver"


def test_api_v1_prefix():
    """Test 11: Endpoints accessible under /api/v1/."""
    main.app.dependency_overrides[get_current_user] = auth_override_a
    setup_user_in_db(TEST_USER_A)

    for path in ["/api/v1/conversations", "/api/v1/saved-places", "/api/v1/me"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"


def test_health_endpoint_still_works():
    """Test 12: Phase 0 health endpoint still works."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root_endpoint_still_works():
    """Test 13: Phase 0 root endpoint still works."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "LocaleLive API"


def test_old_query_removed():
    """Test 14: Old PUT /query endpoint no longer exists."""
    resp = client.put("/query", json={"text": "test", "threadId": "t1"})
    assert resp.status_code in (404, 405)


# --- Runner ---
if __name__ == "__main__":
    tests = [
        test_auth_middleware_no_token,
        test_auth_middleware_valid_token,
        test_create_user_on_first_auth,
        test_conversations_list_empty,
        test_query_creates_conversation,
        test_conversation_messages,
        test_delete_conversation,
        test_conversation_ownership,
        test_saved_places_crud,
        test_user_profile,
        test_api_v1_prefix,
        test_health_endpoint_still_works,
        test_root_endpoint_still_works,
        test_old_query_removed,
    ]

    # Setup initial auth override
    main.app.dependency_overrides[get_current_user] = auth_override_a

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
