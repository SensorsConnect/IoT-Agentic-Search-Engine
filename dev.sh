#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# dev.sh — Start backend (FastAPI) and frontend (Next.js) for local development
# ---------------------------------------------------------------------------

BACKEND_PORT=8000
FRONTEND_PORT=3000
CONDA_ENV="IoT-engine"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prefer the Miniforge conda install if present, since this repo's local env
# was created there and shell init may still point bash at a different conda.
if [[ -x "/opt/homebrew/bin/conda" ]]; then
    CONDA_BIN="/opt/homebrew/bin/conda"
else
    CONDA_BIN="$(command -v conda)"
fi

# Load backend env vars
set -a
source "$SCRIPT_DIR/backend/.env"
set +a

# Use SQLite checkpointer for local dev (avoids psycopg segfault with conda)
export POSTGRES_URL="sqlite:///checkpoints.db"

# Activate conda environment (provides Python + Node 18)
# Temporarily allow unset vars — conda activation scripts may reference undefined vars
set +u
eval "$("$CONDA_BIN" shell.bash hook)"
conda activate "$CONDA_ENV"
set -u

cleanup() {
    echo ""
    echo "Shutting down..."
    [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null
    [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null
    wait 2>/dev/null
    echo "Done."
}
trap cleanup SIGINT SIGTERM EXIT

# Create SQLite tables from models (Alembic migrations are Postgres-only)
echo "Ensuring local SQLite tables exist..."
python -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR/backend/src')
from db.engine import Base, engine
import db.models
Base.metadata.create_all(engine)
print('Tables ready.')
"

# Start backend
echo "Starting backend on port $BACKEND_PORT (conda env: $CONDA_ENV)..."
uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload \
    --app-dir "$SCRIPT_DIR/backend/src" &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on port $FRONTEND_PORT..."
cd "$SCRIPT_DIR/frontend"
# The script sourced backend/.env above, which includes production Clerk keys.
# Clear those for the frontend so Next can load local test keys from frontend/.env.local.
unset NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
unset CLERK_SECRET_KEY
unset CLERK_JWKS_URL
NODE_ENV=development NEXT_PUBLIC_BACKEND_URL="http://localhost:$BACKEND_PORT" npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "============================================"
echo "  Backend:  http://localhost:$BACKEND_PORT/docs"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Press Ctrl+C to stop both services"
echo "============================================"
echo ""

wait
