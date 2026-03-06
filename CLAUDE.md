# CLAUDE.md

## Development Commands

### Backend (FastAPI + LangGraph)
```bash
cd backend
pip install -r requirements_pip.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev          # dev server on port 3000
npm run build        # production build
npm run start        # start production server
```

### Docker (full stack)
```bash
docker-compose up --build   # starts Traefik (80/443), frontend (3000), backend (8000)
```

## Architecture

### Multi-Agent LangGraph Flow
Query enters via `PUT /query` (text, threadId, location) and flows through:

1. **assistant_agent** - Classifies intent (greeting / service recommendation / hard question)
2. **IoT_engine** - MongoDB vector+geospatial search across 37k+ IoT documents
3. **GoogleMaps** - Fallback for uncovered zones (Google Maps API)
4. **scrapper** - Web search via Tavily for general questions
5. **generator_agent** - Produces human-readable response from context
6. **reviewer_agent** - Validates quality, may loop back for refinement

Key files:
- Graph definition: `backend/src/graph_init.py`
- Graph execution: `backend/src/graph.py`
- State schema: `backend/src/state_graph.py` (AgentState TypedDict)
- Agent implementations: `backend/src/agents/`
- Prompts: `backend/src/agents_prompt.py`
- LLM config: `backend/src/utils.py` (ChatGroq, temperature=0)

### Data Layer
- **MongoDB** (`Sensors_Connect_DB_V2`): 500 service types, geospatial indexes. Connection in `backend/src/mongo_db/database_connection.py`
- **VectorDB**: HNSW + DocArray with Sentence-BERT (768-dim) embeddings in `backend/src/vector_db/vector_database.py`
- **SQLite checkpointer**: Thread-based conversation persistence

### Frontend Structure
- Landing page: `frontend/app/page.tsx`
- Chat interface: `frontend/app/chat/` + `frontend/components/Chat/`
- Location context: `frontend/components/Location/LocationContext.tsx`
- Chat hook sends PUT to `NEXT_PUBLIC_BACKEND_URL/query`

## Environment Variables

### Backend
| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq LLM access |
| `LLM_MODEL` | Model name for ChatGroq |
| `MONGODB_URL` | MongoDB connection string |
| `Google_Maps_API_Key` | Google Maps nearby/text search |
| `ORS_API_KEY` | OpenRoute Service (travel time) |
| `TAVILY_API_KEY` | Tavily web search |
| `LANGCHAIN_API_KEY` | LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | Enable tracing (true/false) |

### Frontend
| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL (e.g., `http://localhost:8000`) |
| `BACKEND_DOMAIN_NAME` | Routing config |

## Tech Stack
- **Backend**: Python 3.11, FastAPI 0.115, LangGraph 0.2, LangChain 0.3, PyMongo, Groq
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Radix UI
- **Infra**: Docker, Traefik (reverse proxy + TLS)
