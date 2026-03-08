# Local Development with Docker Compose

## Prerequisites

- Docker & Docker Compose installed
- Backend `.env` file at `backend/.env` with all required variables (see CLAUDE.md)
- Frontend Clerk keys in `frontend/.env.local`

## Quick Start

```bash
# From project root:
docker compose -f docker-compose.local.yml up --build -d
```

This starts:
- **Frontend** at http://localhost:3000
- **Backend** at http://localhost:8001

> The backend runs on port **8001** (not 8000) to avoid conflicts with VS Code port forwarding.

## First startup is slow

The backend downloads the sentence-transformer model (~400MB) on first boot. Check progress with:

```bash
docker logs -f iot-agentic-search-engine-backend-1
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Rebuild after code changes

```bash
# Rebuild everything
docker compose -f docker-compose.local.yml up --build -d

# Rebuild only backend (faster)
docker compose -f docker-compose.local.yml up --build -d backend

# Rebuild only frontend
docker compose -f docker-compose.local.yml up --build -d frontend
```

## Force rebuild (no cache)

Use this when code changes aren't reflected in the running containers:

```bash
# Full no-cache rebuild + recreate
docker compose -f docker-compose.local.yml build --no-cache && docker compose -f docker-compose.local.yml up -d --force-recreate

# No-cache rebuild frontend only
docker compose -f docker-compose.local.yml build --no-cache frontend && docker compose -f docker-compose.local.yml up -d --force-recreate frontend
```

## Testing on a physical phone (mobile view)

Your phone must be on the **same Wi-Fi network** as your computer.

1. Find your machine's local IP:
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. Update `docker-compose.local.yml` build args and CORS with your IP:
   ```yaml
   frontend:
     build:
       args:
         - NEXT_PUBLIC_BACKEND_URL=http://<YOUR_IP>:8001
   backend:
     environment:
       - CORS_ORIGINS=http://localhost:3000,http://<YOUR_IP>:3000
   ```

3. Rebuild with no cache and start:
   ```bash
   docker compose -f docker-compose.local.yml build --no-cache frontend && docker compose -f docker-compose.local.yml up -d --force-recreate
   ```

4. Open on your phone: `http://<YOUR_IP>:3000`

## View logs

```bash
# Both services
docker compose -f docker-compose.local.yml logs -f

# Backend only
docker logs -f iot-agentic-search-engine-backend-1

# Frontend only
docker logs -f iot-agentic-search-engine-frontend-1
```

## Stop

```bash
docker compose -f docker-compose.local.yml down
```

## Optional: Enable Google Place Details API

The Place Details API (phone numbers, website links on Google Maps cards) is disabled by default to save costs. To enable, add to `docker-compose.local.yml` under backend environment:

```yaml
environment:
  - ENABLE_PLACE_DETAILS=true
```

## Switching between local and production

The frontend `NEXT_PUBLIC_BACKEND_URL` is baked at **build time** inside `frontend/Dockerfile.local`. It's set to `http://localhost:8001` for local dev.

For production, use the main `docker-compose.yml` which points to `https://api.localelive.space`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 8001 in use | `docker compose -f docker-compose.local.yml down` then retry |
| Backend won't start | Check `docker logs iot-agentic-search-engine-backend-1` for missing env vars |
| Frontend shows blank | Wait for backend to finish starting, then refresh |
| Stale containers | `docker compose -f docker-compose.local.yml down --remove-orphans` |
