# LocaleLive — Architecture

How the app runs today, post-migration. For the history of *why* it changed, see
[`migration-summary.md`](./migration-summary.md); for the deploy runbook, see
[`migration-deploy-checklist.md`](./migration-deploy-checklist.md).

## Request Path

![Infrastructure architecture](https://raw.githubusercontent.com/SensorsConnect/IoT-Agentic-Search-Engine/main/infra/diagrams/infra-architecture.png)

- **Frontend** — `localelive.space` is a Next.js 15 app hosted on Vercel, using Clerk for auth.
  It lives in its own repo (`SensorsConnect/localelive-frontend`), pulled into this repo as a git
  submodule at `frontend/`.
- **Backend** — `api.localelive.space` points at an API Gateway HTTP API, which proxies every
  request to a single Lambda function (`localelive-backend`). The function runs as a **container
  image** (not a zip package) — FastAPI wrapped in a Mangum ASGI adapter, running the same
  LangGraph multi-agent graph described in `CLAUDE.md`.
- **Data & external services** — MongoDB Atlas (IoT/service documents + vector search), Neon
  Postgres (conversation persistence, via SQLAlchemy with `NullPool` since Lambda freezes/thaws
  containers), HuggingFace Inference API (embeddings — replaced the in-process
  `sentence-transformers` model that made the image too large for Lambda), Groq (LLM inference),
  Google Maps, Tavily, and OpenRouteService (ORS).

**Two hard timeouts to know about:**
- API Gateway cuts any connection at **29 seconds**, no matter what the Lambda function timeout is
  set to (currently 5 minutes). Multi-hop LangGraph queries that run long will appear to hang in
  the browser even though Lambda is still working.
- Lambda has a **10-second cold-start init timeout** separate from the request timeout. Anything
  imported or initialized at module load time (vector DB, model loading) must be deferred to first
  request — see `backend/src/main.py` and `backend/src/vector_db/vector_database.py`.

## CI/CD — Build & Deploy Flow

![CI/CD deploy flow](https://raw.githubusercontent.com/SensorsConnect/IoT-Agentic-Search-Engine/main/infra/diagrams/cicd-flow.png)

A push to `main` or `deployment` that touches `backend/**` triggers
`.github/workflows/ci.yml` (`build-backend` job):

1. Builds the backend image for `linux/amd64` with `provenance=false` (Lambda rejects the
   multi-platform manifest that provenance attestations produce).
2. Pushes the same image to **two** registries: Docker Hub (`elewah/localelive-backend` — still
   used by EC2 and local `docker-compose`) and **Amazon ECR** (`localelive-backend` — the only
   source Lambda container images can be pulled from; this is an AWS constraint, not a design
   choice, so the ECR repo is required and should not be deleted).
3. Runs `aws lambda update-function-code` against the ECR image, so every merge to `main`
   auto-deploys the backend.

The frontend has no equivalent CI step — Vercel deploys directly from the
`localelive-frontend` repo on push.

## Lambda Secrets

The Lambda function's 14 environment variables are set via AWS Console/CLI, not in this repo
(they're real secrets: `GROQ_API_KEY`, `MONGODB_URL`, `POSTGRES_URL`, etc). To avoid re-deriving
"what does Lambda need" from tribal knowledge:

- [`infra/lambda-env.example`](https://github.com/SensorsConnect/IoT-Agentic-Search-Engine/blob/main/infra/lambda-env.example) — versioned, keys only, no values. This is
  the durable reference for which vars exist.
- [`infra/scripts/pull-lambda-env.sh`](https://github.com/SensorsConnect/IoT-Agentic-Search-Engine/blob/main/infra/scripts/pull-lambda-env.sh) — fetches the *live* values
  from the Lambda function into `infra/.env.lambda` (gitignored — never committed).
- [`infra/scripts/push-lambda-env.sh`](https://github.com/SensorsConnect/IoT-Agentic-Search-Engine/blob/main/infra/scripts/push-lambda-env.sh) — reads `infra/.env.lambda`,
  diffs it against the live Lambda config, shows what would change, and asks for confirmation
  before calling `aws lambda update-function-configuration`.

Typical flow: `pull-lambda-env.sh` to get a local working copy → edit `infra/.env.lambda` →
`push-lambda-env.sh` to sync the change back up.

## Multi-Agent Backend Flow

The Lambda-hosted FastAPI app runs a LangGraph graph: `assistant_agent` (classifies intent) →
`IoT_engine` (MongoDB vector + geospatial search) → `GoogleMaps` (fallback for uncovered zones) /
`scrapper` (Tavily web search for general questions) → `generator_agent` (produces the response) →
`reviewer_agent` (validates quality, may loop back). This isn't re-diagrammed here — see
`CLAUDE.md` and `backend/src/graph_init.py` for the source of truth.

## Cleanup History

- **`fastapi` ECR repo** (account `025628150716`, `us-east-1`) — a leftover from an earlier,
  unrelated project (6 images, ~1.9GB, last pushed 2025-04-25). Confirmed unreferenced by the
  `localelive-backend` Lambda function, `ci.yml`, and `docker-compose.yml`, then deleted on
  2026-07-05.
