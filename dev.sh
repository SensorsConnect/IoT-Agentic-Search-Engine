#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# dev.sh — Start backend (FastAPI) and frontend (Next.js) for local development
# ---------------------------------------------------------------------------

BACKEND_PORT=8000
FRONTEND_PORT=3000
CONDA_ENV="IoT-engine"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="$SCRIPT_DIR/.dev-certs"

# Detect LAN IP so the phone can reach the dev server from the same Wi-Fi.
LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
if [[ -z "${LAN_IP:-}" ]]; then
    LAN_IP="$(ipconfig getifaddr en1 2>/dev/null || true)"
fi
if [[ -z "${LAN_IP:-}" ]]; then
    LAN_IP="$(ifconfig 2>/dev/null | awk '/inet / && $2 != "127.0.0.1" {print $2; exit}')"
fi

# Ensure a locally-trusted TLS cert exists so the Geolocation API works on phones.
# mkcert signs with a root CA the phone trusts after a one-time install; without
# HTTPS a LAN-IP origin is insecure and browsers silently refuse GPS access.
if ! command -v mkcert >/dev/null 2>&1; then
    echo "ERROR: mkcert is not installed." >&2
    echo "Install it once with:  brew install mkcert nss && mkcert -install" >&2
    echo "Then install the root CA on your phone (see plan docs)." >&2
    exit 1
fi

mkdir -p "$CERT_DIR"
CERT_FILE="$CERT_DIR/dev-cert.pem"
KEY_FILE="$CERT_DIR/dev-key.pem"
# Regenerate the cert if it's missing OR doesn't include the current LAN IP.
NEEDS_CERT=0
if [[ ! -f "$CERT_FILE" || ! -f "$KEY_FILE" ]]; then
    NEEDS_CERT=1
elif [[ -n "${LAN_IP:-}" ]] && ! openssl x509 -in "$CERT_FILE" -noout -ext subjectAltName 2>/dev/null | grep -q "$LAN_IP"; then
    NEEDS_CERT=1
fi
if [[ "$NEEDS_CERT" = "1" ]]; then
    echo "Generating mkcert dev cert (localhost 127.0.0.1 ${LAN_IP:-})..."
    ( cd "$CERT_DIR" && mkcert -cert-file dev-cert.pem -key-file dev-key.pem \
        localhost 127.0.0.1 ${LAN_IP:+$LAN_IP} )
fi

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
echo "Starting frontend on port $FRONTEND_PORT (HTTPS)..."
cd "$SCRIPT_DIR/frontend"
if [[ ! -d node_modules ]]; then
    echo "node_modules missing — running npm install..."
    npm install
fi
# Clear Next.js build cache to guarantee a fresh compile picks up all changes.
rm -rf .next
# The script sourced backend/.env above, which includes production Clerk keys.
# Clear those for the frontend so Next can load local test keys from frontend/.env.local.
unset NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
unset CLERK_SECRET_KEY
unset CLERK_JWKS_URL
# Force NEXT_PUBLIC_BACKEND_URL to empty so api calls are same-origin and
# proxied by Next's rewrite to localhost:8000. A bare `unset` isn't enough —
# Next would then fall through to .env.local / .env (which hold the prod
# backend URL), re-introducing a cross-origin CORS failure. Shell env takes
# precedence over dotfiles only when the variable is actually set.
NODE_ENV=development \
NEXT_PUBLIC_BACKEND_URL= \
    npm run dev -- \
    --experimental-https \
    --experimental-https-key  "$KEY_FILE" \
    --experimental-https-cert "$CERT_FILE" \
    -H 0.0.0.0 \
    -p "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "============================================"
echo "  Backend:  http://localhost:$BACKEND_PORT/docs   (proxied via Next)"
echo "  Frontend: https://localhost:$FRONTEND_PORT"
if [[ -n "${LAN_IP:-}" ]]; then
    echo "  Phone:    https://$LAN_IP:$FRONTEND_PORT"
fi
echo "  Press Ctrl+C to stop both services"
echo "============================================"
echo ""

wait
