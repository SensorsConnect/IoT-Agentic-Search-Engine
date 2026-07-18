# LocaleLive: IoT-Agentic Search Engine

> The pulse of places lives at your fingertips.

**Live Demo**: [localelive.space](https://localelive.space)  
**Docs**: [sensorsconnect.github.io/IoT-Agentic-Search-Engine](https://sensorsconnect.github.io/IoT-Agentic-Search-Engine/)

## What This Project Does

- Leverages LLMs + RAG to support natural language queries over diverse IoT data streams.
- Implements a multi-agent architecture (GA-RAG) with Classifier, Retriever, Generator, and Reviewer agents for robust, context-aware responses.
- Embeds service descriptions using HuggingFace Inference API (BAAI/bge-small-en-v1.5, 384-dim) and stores them in a Milvus Lite HNSW vector database for fast semantic search.
- Integrates with MongoDB to manage 37,000+ IoT documents across 500 service types, with geospatial indexing for location-aware results.
- Outperforms generic assistants like Gemini by understanding complex, preference-rich queries and generating actionable, human-like responses.
- Built with **LangGraph**, **FastAPI**, **Tavily**, **OpenRouteService**, and **Google Maps** — deployed on AWS Lambda + Vercel.

> **Accuracy**: 92% top-1 intent detection for complex user queries  
> **Coverage**: Toronto region with 500 simulated services and 37,000+ IoT data points  
> **Response Time**: 99% of queries processed under 4.12 seconds

---

## Architecture

The full architecture is documented in [`infra/ARCHITECTURE.md`](./infra/ARCHITECTURE.md). In brief:

```
User → localelive.space (Vercel / Next.js 15 + Clerk)
         ↓
     api.localelive.space → API Gateway → Lambda
         ↓
     FastAPI + LangGraph multi-agent pipeline
         ↓
     MongoDB Atlas · Neon Postgres · HuggingFace API · Groq
```

**Two hard timeouts to know about:**
- API Gateway cuts any connection at **29 seconds** — queries that take longer appear to hang.
- Lambda has a **10-second cold-start init** — heavy imports must be deferred to first request.

A CloudWatch Events rule fires every 5 minutes to keep the Lambda container warm. See [`docs/ops/lambda-warmup.md`](./docs/ops/lambda-warmup.md).

---

## Multi-Agent Workflow

Queries flow through a 7-node LangGraph graph:

```
assistant_agent        → classifies intent (greeting / service search / general question)
  ├─ IoT_engine        → MongoDB vector + geospatial search (local service data)
  │    └─ GoogleMaps   → fallback for zones not covered by IoT data
  ├─ scrapper          → Tavily web search for open-ended questions
  └─ reviewer_agent    → validates quality, may loop back for refinement
       └─ finalize_turn
```

Key files: `backend/src/graph_init.py` (graph definition), `backend/src/agents/` (each node), `backend/src/agents_prompt.py` (prompts).

### Available Services

- Grocery stores, walk-in clinics, car rentals, parks, restaurants, and more (Toronto region)
- Results ranked by: reputation (ratings), real-time travel time (OpenRouteService), and occupancy data

### Example Query

```
I want to have dinner with my family at a Middle Eastern restaurant with a good reputation.
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 18, TypeScript, Tailwind CSS |
| Auth | Clerk |
| Maps | Mapbox GL |
| Backend | Python 3.11, FastAPI 0.115 |
| Agent framework | LangGraph 0.2, LangChain 0.3 |
| LLM | Groq (llama-3.1 family) |
| IoT data | MongoDB Atlas — geospatial + vector search |
| Embeddings | HuggingFace Inference API (no local model) |
| Conversation persistence | Neon PostgreSQL, SQLAlchemy NullPool |
| Hosting | Vercel (frontend) + AWS Lambda + API Gateway (backend) |

---

## Environment Variables

### Backend (Lambda / local)

| Variable | Required | Purpose |
|----------|----------|---------|
| `GROQ_API_KEY` | Yes | Groq LLM inference |
| `LLM_MODEL` | Yes | Model name (e.g. `llama-3.1-8b-instant`) |
| `MONGODB_URL` | Yes | MongoDB Atlas connection string |
| `HF_API_KEY` | Yes | HuggingFace Inference API (embeddings) |
| `POSTGRES_URL` | Yes | Neon PostgreSQL (conversation persistence) |
| `GOOGLE_MAPS_API_KEY` | Yes | Google Maps nearby/text search |
| `ORS_API_KEY` | Yes | OpenRouteService (travel time) |
| `TAVILY_API_KEY` | Yes | Tavily web search |
| `CLERK_JWKS_URL` | Yes | Clerk JWT verification |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `MILVUS_DB_PATH` | Yes | Path for Milvus Lite DB (`/tmp/milvus_lite.db` on Lambda) |
| `ENVIRONMENT` | Yes | `production` or `development` |
| `LANGCHAIN_API_KEY` | No | LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | No | `true` to enable LangSmith |

The full list with descriptions lives in [`infra/lambda-env.example`](./infra/lambda-env.example).  
To pull/push live Lambda env vars: see [`infra/scripts/`](./infra/scripts/).

### Frontend (Vercel)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL (`https://api.localelive.space`) |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Mapbox access token |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (use `pk_live_*` in production) |
| `CLERK_SECRET_KEY` | Clerk secret key (use `sk_live_*` in production) |

`NEXT_PUBLIC_*` values are baked into the JS bundle at `next build` time. See [`docs/development/env-guide.md`](./docs/development/env-guide.md) for the full guide.

---

## Local Development

See [`docs/development/local-dev.md`](./docs/development/local-dev.md) for the full Docker Compose setup. Quick start:

```bash
# Backend only (requires backend/.env)
cd backend
pip install -r requirements_pip.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend only (requires frontend/.env.local with Clerk keys)
cd frontend
npm install
npm run dev   # http://localhost:3000

# Full stack with Docker Compose
docker compose -f docker-compose.local.yml up --build -d
# Frontend: http://localhost:3000  Backend: http://localhost:8001
```

> The backend exposes interactive API docs at `http://localhost:8000/docs`.

---

## Deployment

### Production (Lambda + Vercel)

Every push to `main` that touches `backend/**` triggers `.github/workflows/ci.yml`:
1. Builds a `linux/amd64` container image with `provenance=false`
2. Pushes to both Docker Hub (`elewah/localelive-backend`) and Amazon ECR
3. Calls `aws lambda update-function-code` — the backend auto-deploys

The frontend auto-deploys via Vercel directly from the `SensorsConnect/localelive-frontend` repo on push. There is no frontend CI step in this repo.

Full deploy runbook: [`infra/migration-deploy-checklist.md`](./infra/migration-deploy-checklist.md).

### Self-Hosted (Docker Compose)

Pull and run the backend container:

```bash
docker pull elewah/localelive-backend
docker run -d \
  --name iot-ase-backend \
  -p 8000:8000 \
  --env-file .env \
  elewah/localelive-backend
```

---

## Documentation

Full docs are hosted at [sensorsconnect.github.io/IoT-Agentic-Search-Engine](https://sensorsconnect.github.io/IoT-Agentic-Search-Engine/) and cover:

- [Architecture & infra](docs/architecture/overview.md)
- [EC2 → Lambda migration history](docs/architecture/migration-summary.md)
- [Local development](docs/development/local-dev.md)
- [Anonymous chat feature](docs/features/anonymous-chat.md)
- [Location system](docs/location/network-location-guide.md)
- [Product roadmap](docs/product/roadmap.md)

---

## Citation

```bibtex
@article{elewah2025agentic,
  title={Agentic Search Engine for Real-Time Internet of Things Data},
  author={Elewah, Abdelrahman and Elgazzar, Khalid and Elnaffar, Said},
  journal={Sensors},
  volume={25},
  number={19},
  pages={5995},
  year={2025},
  publisher={MDPI}
}

@article{elewah2024sensorsconnect,
  title={Sensorsconnect framework: World-wide web for internet of things},
  author={Elewah, Abdelrahman and Elgazzar, Khalid},
  journal={IEEE Access},
  year={2024},
  publisher={IEEE}
}
```

Full thesis:

```bibtex
@article{elewah2025sensorsconnect,
  title={SensorsConnect: World Wide Web for Internet of Things},
  author={Elewah, Abdelrahman},
  year={2025}
}
```

---

## License

Apache License 2.0. See [LICENSE](LICENSE).
