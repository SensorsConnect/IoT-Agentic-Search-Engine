# LocaleLive AWS Migration Summary

## Overview

Migrated LocaleLive from a single EC2 instance (~$45–55/month) to a serverless architecture (~$1/month), saving ~$44–54/month (~$530/year).

**Migration date:** July 4, 2026

---

## Before → After

| Component | Before | After |
|-----------|--------|-------|
| Frontend | EC2 + Docker + Traefik | Vercel (free tier) |
| Backend | EC2 + Docker + Traefik | AWS Lambda + API Gateway |
| Container registry | Docker Hub only | Docker Hub + Amazon ECR |
| SSL/TLS | Traefik (Let's Encrypt) | Vercel (auto) + ACM (API Gateway) |
| DNS | Namecheap → EC2 IP | Namecheap → Vercel + API Gateway |
| Monthly cost | ~$45–55 | ~$1 |

---

## Architecture

```
User
 ├── localelive.space → Vercel (Next.js 15, Clerk auth)
 └── api.localelive.space → API Gateway → Lambda (FastAPI + LangGraph)
                                               ↓
                                    MongoDB Atlas (unchanged)
                                    Neon PostgreSQL (unchanged)
                                    HuggingFace Inference API (embeddings)
```

---

## Key Changes Made

### 1. Frontend — Moved to Separate Repo + Vercel

**Problem:** Frontend was in `frontend/` subdirectory of the monorepo — Vercel couldn't detect Next.js correctly, causing repeated 404 and "No framework detected" errors.

**Solution:**
- Created `github.com/SensorsConnect/localelive-frontend` as a standalone repo
- Added it back as a git submodule in the main repo at `frontend/`
- Vercel connects directly to `localelive-frontend` — no Root Directory config needed

**Files changed:**
- `frontend/vercel.json` — added `{"framework": "nextjs"}` to force detection
- `frontend/package.json` — renamed from `chatgpt-lite` to `localelive-frontend`
- `frontend/next.config.js` — made `output: 'standalone'` conditional on `DOCKER_BUILD=true` (Vercel needs standard output, Docker needs standalone)
- `frontend/Dockerfile` — added `DOCKER_BUILD=true` to `npm run build` step
- `frontend/app/layout.tsx` — added `suppressHydrationWarning` on `<html>` and `<body>` for theme provider
- `frontend/components/Link.tsx` — replaced `legacyBehavior` with `asChild` pattern (Next.js 15 breaking change)
- Removed `frontend/app/api/chat/route.ts` — unused OpenAI route was crashing Vercel's Edge runtime
- Removed `frontend/middleware.ts` — Clerk v5 bundled Node.js internals incompatible with Vercel Edge Runtime; middleware had no meaningful logic anyway

**Clerk issue:** Production keys locked to `localelive.space` — use test keys during staging on Vercel preview URLs, switch to production keys after domain cutover.

---

### 2. Backend — Replaced Torch/Transformers with HuggingFace API

**Problem:** `torch` + `transformers` + `sentence-transformers` added ~1.4GB to the Docker image, making Lambda impossible (10s init timeout, cold starts of 20–50s).

**Solution:** Replaced local `SentenceTransformer("BAAI/bge-small-en-v1.5")` with HuggingFace Inference API — same model, same vector dimensions (384), no local install needed.

**Files changed:**
- `backend/src/vector_db/vector_database.py` — replaced `SentenceTransformer` with `httpx.post()` to HF Inference API
- `backend/requirements_pip.txt` — removed `torch`, `transformers`, `sentence-transformers`, `safetensors`, `tokenizers`, `huggingface-hub`; kept `numpy<2`

**New env var required:** `HF_API_KEY` — free token from huggingface.co/settings/tokens

**Result:** Image size dropped from ~1.7GB to ~300MB

---

### 3. Backend — Lambda Compatibility

**Files changed:**

`backend/src/main.py`:
```python
# Lambda handler — only active when AWS_LAMBDA_FUNCTION_NAME is set
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")

# Skip lifespan on Lambda (10s init timeout — defer vector DB init)
IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
app = FastAPI(lifespan=None if IS_LAMBDA else lifespan)
```

`backend/src/db/engine.py`:
```python
# NullPool on Lambda — pooled connections go stale after container freeze/thaw
IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
if IS_LAMBDA:
    engine = create_engine(POSTGRES_URL, poolclass=NullPool)
else:
    engine = create_engine(POSTGRES_URL, pool_size=5, pool_pre_ping=True, ...)
```

`backend/src/vector_db/vector_database.py`:
- `vector_db_push_batch()` called lazily in `vector_search()` instead of at startup
- This avoids the 10s Lambda init timeout — health checks work instantly, vector DB loads on first IoT query

`backend/scripts/docker-entrypoint.sh`:
- On Lambda: copies pre-built `milvus_lite.db` from image to `/tmp/` (Lambda's only writable dir)
- On Lambda: skips Alembic migrations (Neon handles schema directly)

`backend/requirements_pip.txt`:
- Added `mangum>=0.17.0` (ASGI adapter for Lambda)
- Added `awslambdaric>=1.0.0` (Lambda Runtime Interface Client — needed for non-AWS base images)

**Lambda image config override** (set via AWS CLI, not Dockerfile — keeps EC2 unaffected):
```
EntryPoint: ["/app/.venv/bin/python", "-m", "awslambdaric"]
Command: ["main.handler"]
WorkingDirectory: "/app/src"
```

**Key gotcha:** Lambda has a **hard 10s init timeout** separate from the function timeout. Any heavy imports at module level (Milvus Lite starting its gRPC server, model loading) will hit this. All heavy init must be deferred to first request.

**Key gotcha:** API Gateway has a **hard 29s timeout** that cannot be changed. Lambda function timeout can be 5 min, but API Gateway cuts the connection at 29s. Queries that take longer appear to hang in the browser.

---

### 4. CI/CD — Added ECR Push + Lambda Auto-Deploy

`github/workflows/ci.yml` updated to:
- Build `linux/amd64` image with `provenance=false` (Lambda requires this format — ARM Mac re-pushes corrupt the manifest)
- Push to both Docker Hub (EC2 compatibility) and ECR (Lambda)
- Auto-update Lambda function after each push via `aws lambda update-function-code`

**GitHub secrets required:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**Why `provenance=false`:** Docker BuildKit adds provenance attestations by default which create a manifest list. Lambda only accepts single-platform manifests — provenance must be disabled.

---

### 5. DNS — Namecheap → Vercel + API Gateway

**Changes in Namecheap Advanced DNS:**

| Record | Before | After |
|--------|--------|-------|
| `A` → `@` | `3.95.138.221` (EC2) | `216.198.79.1` (Vercel) |
| `CNAME` → `api` | EC2 IP | `d-fumh51xtfd.execute-api.us-east-1.amazonaws.com` |

**SSL for `api.localelive.space`:** Requested via ACM (`us-east-1`), validated via DNS CNAME, attached to API Gateway custom domain.

---

### 6. AWS Resources Created

| Resource | Name/ID | Purpose |
|----------|---------|---------|
| ECR repository | `localelive-backend` | Stores Lambda container image |
| Lambda function | `localelive-backend` | Runs FastAPI backend |
| IAM role | `localelive-lambda-role` | Lambda execution permissions |
| API Gateway | `lcku7mzs4f` | HTTP API → Lambda proxy |
| ACM certificate | `055f659f-...` | SSL for `api.localelive.space` |
| API Gateway custom domain | `api.localelive.space` | Clean backend URL |

---

## Environment Variables

### Lambda (set via AWS Console or CLI)

| Key | Notes |
|-----|-------|
| `GROQ_API_KEY` | LLM provider |
| `LLM_MODEL` | e.g. `openai/gpt-oss-20b` |
| `MONGODB_URL` | MongoDB Atlas connection string |
| `POSTGRES_URL` | Neon PostgreSQL URL |
| `GOOGLE_MAPS_API_KEY` | Maps + Places |
| `ORS_API_KEY` | OpenRoute Service |
| `TAVILY_API_KEY` | Web search |
| `CLERK_JWKS_URL` | Auth verification |
| `LANGCHAIN_API_KEY` | LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | `true` |
| `HF_API_KEY` | HuggingFace Inference API (new) |
| `MILVUS_DB_PATH` | `/tmp/milvus_lite.db` (Lambda writable dir) |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://localelive.space,https://www.localelive.space` |

### Vercel (set in dashboard)

| Key | Notes |
|-----|-------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://api.localelive.space` |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Mapbox |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_...` (production) |
| `CLERK_SECRET_KEY` | `sk_live_...` (production) |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` | `/chat` |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` | `/chat` |

---

## Lessons Learned

1. **Lambda init timeout is 10s** — any module-level code that takes longer kills the cold start silently. Defer everything heavy to first request.

2. **API Gateway timeout is 29s hard limit** — cannot be configured. Long-running queries (LangGraph with multiple agent hops) can hit this. Monitor query duration in Lambda logs.

3. **Never pull ARM images and re-push for Lambda** — Lambda requires `linux/amd64` images built with `provenance=false`. Always build in CI on `ubuntu-latest` (x86_64).

4. **Vercel + monorepo = pain** — Vercel works best when the repo root IS the Next.js app. Moving frontend to its own repo eliminated all the Root Directory confusion and stale deployment issues.

5. **Clerk production keys are domain-locked** — use test keys (`pk_test_...`) during staging on Vercel preview URLs. Switch to production keys only after the real domain is configured.

6. **Milvus Lite file path on Lambda** — Lambda's container filesystem is read-only except `/tmp`. Set `MILVUS_DB_PATH=/tmp/milvus_lite.db` and copy the pre-built DB from the image to `/tmp` in the entrypoint script.

7. **CORS must include all origins** — `www.localelive.space` and `localelive.space` are different origins. Include both in `CORS_ORIGINS`.

---

## Rollback Plan

EC2 is still running at `3.95.138.221`. To roll back instantly:
1. Namecheap → change `@` A record back to `3.95.138.221`
2. DNS propagates in ~2 min
3. Everything runs from EC2 as before

**Decommission EC2** only after 48h of stable production traffic on the new architecture.
