# LocaleLive Documentation

**LocaleLive** is an AI-powered hyperlocal discovery platform — ask natural-language questions about what's nearby and get real-time recommendations backed by 37,000+ IoT sensor documents, Google Maps, and live web data.

- Live demo: [localelive.space](https://localelive.space)
- GitHub: [SensorsConnect/IoT-Agentic-Search-Engine](https://github.com/SensorsConnect/IoT-Agentic-Search-Engine)
- Paper: [Agentic Search Engine for Real-Time IoT Data (Sensors, 2025)](https://www.mdpi.com/1424-8220/25/19/5995)

---

## What's in these docs

| Section | Contents |
|---------|----------|
| [Architecture](architecture/overview.md) | Request path, CI/CD, Lambda config, data services |
| [Migration Summary](architecture/migration-summary.md) | EC2 → Lambda migration (July 2026), lessons learned |
| [Deploy Checklist](architecture/migration-deploy-checklist.md) | Step-by-step deploy runbook |
| [Lambda Warm-Up](ops/lambda-warmup.md) | CloudWatch ping to prevent cold-start timeouts |
| [Local Development](development/local-dev.md) | Docker Compose local dev setup |
| [Environment Variables](development/env-guide.md) | Frontend env vars — what each does and how CI bakes them in |
| [Anonymous Chat](features/anonymous-chat.md) | How unauthenticated access works |
| [Location System](location/network-location-guide.md) | GPS + IP fallback location architecture |
| [Product Roadmap](product/roadmap.md) | Phased plan from research demo to production platform |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 18, TypeScript, Tailwind CSS, Clerk (auth), Mapbox |
| Backend | Python 3.11, FastAPI 0.115, LangGraph 0.2, LangChain 0.3 |
| LLM | Groq (llama-3.1 family) |
| IoT Data | MongoDB Atlas — 37k+ documents, 500 service types, geospatial indexes |
| Embeddings | HuggingFace Inference API (BAAI/bge-small-en-v1.5, 384-dim) |
| Conversation Persistence | Neon PostgreSQL via SQLAlchemy |
| Hosting | Vercel (frontend) + AWS Lambda + API Gateway (backend) |
