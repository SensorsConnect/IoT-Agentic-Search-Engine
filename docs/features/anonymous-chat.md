# Feature: Anonymous Chat Access

**Status:** Implemented
**Date:** 2026-03-21
**Goal:** Let users try LocaleLive without creating an account to reduce sign-up friction.

---

## Overview

Users can now use the full AI chat and map experience at `/chat` without signing in. Conversation history is only persisted for signed-in users.

| Capability | Anonymous | Signed-In |
|-----------|-----------|-----------|
| AI chat (ask questions, get recommendations) | Yes | Yes |
| Map with place markers | Yes | Yes |
| Location-aware results | Yes | Yes |
| In-session conversation continuity | Yes | Yes |
| Conversation history (across sessions) | No | Yes |
| Load past conversations | No | Yes |
| Rename/delete conversations | No | Yes |

---

## How It Works

### Anonymous Users
1. Visit `/chat` — no redirect to sign-in
2. A `threadId` (UUID) is generated client-side for the session
3. Queries hit `PUT /api/v1/query` without a Bearer token
4. Backend runs the full LangGraph agent pipeline (assistant → IoT/GoogleMaps/scrapper → generator → reviewer)
5. Results are returned with places and map data
6. **No database writes** — conversations and messages are not saved
7. LangGraph's checkpointer still tracks state via `threadId` for multi-turn conversations within the session

### Signed-In Users
1. Same flow, but requests include a Clerk Bearer token
2. Backend identifies the user via `get_optional_user`
3. Conversations and messages are saved to PostgreSQL
4. User can reload the page or return later and see full history
5. Conversation management (rename, delete) requires authentication

---

## Files Changed

### Frontend
| File | Change |
|------|--------|
| `frontend/middleware.ts` | Removed `/chat` from protected routes — no more redirect to sign-in |
| `frontend/lib/api.ts` | Removed auto-redirect to `/sign-in` on 401 responses |

### Backend
| File | Change |
|------|--------|
| `backend/src/api/v1/query.py` | Uses `get_optional_user` instead of `get_current_user`; skips DB writes when `user is None` |
| `backend/src/api/v1/conversations.py` | `list_conversations` returns `[]` for anonymous; `get_conversation` returns 401 with message |
| `backend/src/auth/clerk.py` | No change — `get_optional_user` already existed |

### Bug Fixes (bundled)
| File | Change |
|------|--------|
| `backend/src/agents/reviewer_agent.py` | Fixed null access: `state["response"]` → `state.get("response", "")` |
| `backend/src/agents/google_knowledge_graph.py` | **Deleted** — deprecated dead code |
| `backend/src/graph_init.py` | Removed GoogleKnowledgeGraph node and edges |
| `backend/src/agents/__init__.py` | Removed GoogleKnowledgeGraph import |
| `backend/src/routers.py` | Removed unused `router` function |

---

## Key Design Decisions

1. **No "guest user" records** — anonymous sessions are purely ephemeral. No DB schema changes needed.
2. **LangGraph checkpointer still works** — it keys on `threadId`, not user ID. Multi-turn conversations work within a session even without auth.
3. **Graceful degradation** — the frontend already handled missing tokens. The changes were mostly backend (removing hard 401s) and middleware (removing route protection).
4. **Auth-gated features are additive** — signing in unlocks history persistence, not core functionality.

---

## Testing Checklist

- [ ] Open `/chat` in incognito browser — page loads without redirect
- [ ] Send a query without signing in — get AI response + map markers
- [ ] Send follow-up query — context is maintained (multi-turn works)
- [ ] Refresh page — conversation is gone (expected for anonymous)
- [ ] Sign in → send query → refresh → conversation history loads
- [ ] Sign out → `/chat` still accessible
- [ ] `GET /api/v1/conversations` without token → returns `[]` (not 401)
- [ ] `PUT /api/v1/query` without token → returns AI response (not 401)
