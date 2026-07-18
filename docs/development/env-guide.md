# Environment Variables Guide — LocaleLive Frontend

## How env files work in this project

Next.js loads env files in priority order (highest first):

```
.env.local          ← local dev overrides, never committed, never used in Docker
.env.production     ← baked INTO the Docker image at build time via CI secret
.env                ← base defaults (not used here)
```

In CI, the GitHub Actions workflow writes `frontend/.env.production` from the
`FRONTEND_ENV_PRODUCTION` secret before running `docker build`. This means
**whatever is in that secret is what ships to production**.

---

## Variables used by the UI and what they do

### `NEXT_PUBLIC_BACKEND_URL`
- **Used in**: `frontend/utils/environment.ts` → `config.apiUrl`
- **Used by**: `SearchBar.tsx`, `MobileSearchSheet.tsx`, `Chat.tsx` — every query to the backend
- **In production**: `https://api.localelive.space`
- **In local dev**: empty string `""` — Next.js rewrites `/api/v1/*` to `http://127.0.0.1:8000` via `next.config.js`
- **If wrong or missing**: all queries fail silently, app appears frozen

### `NEXT_PUBLIC_MAPBOX_TOKEN`
- **Used in**: `frontend/components/Map/PlacesMap.tsx` line 10
- **Used by**: the map component — passed directly to `mapboxAccessToken`
- **In production**: `pk.eyJ1IjoiZWxld2FoIiwiYSI6ImNtbWd4bzM3cTBhZmoyb3B4ZnM5NnBsY3cifQ.nsIRGmWgYL4ThmZpZ2b_OQ`
- **If missing**: Mapbox refuses to initialize, map renders a black/empty box
- **⚠️ THIS IS MISSING from the current `.env.production`** — add it now (see below)

### `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- **Used in**: Clerk's Next.js middleware and `<ClerkProvider>`
- **In production**: must be the **live** key `pk_live_Y2xlcmsubG9jYWxlbGl2ZS5zcGFjZSQ`
- **⚠️ Current `.env.production` has the test key** (`pk_test_*`) — sign-in on localelive.space will fail

### `CLERK_SECRET_KEY`
- **Used in**: server-side Clerk calls (token verification, session management)
- **In production**: must be the **live** key `sk_live_*`
- **⚠️ Current `.env.production` has the test key** (`sk_test_*`) — auth will fail in production

### `NEXT_PUBLIC_CLERK_SIGN_IN_URL` / `NEXT_PUBLIC_CLERK_SIGN_UP_URL`
- **Used in**: Clerk redirect config
- **Value**: `/sign-in` and `/sign-up` (same in all environments)

### `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL` / `NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL`
- **Used in**: where Clerk redirects after successful login/signup
- **Value**: `/chat` (same in all environments)

---

## Status of `prod_env_files/frontend/.env.production`

This file is correct and complete — use it as-is.

| Variable | Status |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | ✅ `https://api.localelive.space` |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | ✅ present |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | ✅ live key (`pk_live_*`) |
| `CLERK_SECRET_KEY` | ✅ live key (`sk_live_*`) |
| Clerk redirect URLs | ✅ all present |

---

## How to set the GitHub secret

Paste the full contents of `prod_env_files/frontend/.env.production` into the
`FRONTEND_ENV_PRODUCTION` GitHub secret:

1. **GitHub → Settings → Secrets and variables → Actions**
2. Find `FRONTEND_ENV_PRODUCTION` → click **Update**
3. Paste the entire file contents
4. Save — next CI build will bake these values into the Docker image

---

## How to update the GitHub secret

1. Go to: **GitHub repo → Settings → Secrets and variables → Actions**
2. Find `FRONTEND_ENV_PRODUCTION` → click **Update**
3. Paste the corrected block above as the secret value
4. Push any frontend change to `main` to trigger a new CI build with the updated secret

---

## EC2 deployment — what goes where

On the EC2 instance, the root `.env` file (next to `docker-compose.yml`) supplies
**backend** environment variables. The frontend variables are baked into the image
at CI build time — you do **not** need a frontend env file on the EC2.

Backend variables required in the root `.env` on EC2:

| Variable | Purpose |
|---|---|
| `DOMAIN_NAME` | Frontend domain for Traefik routing (`localelive.space`) |
| `TRAFEIK_DOMAIN_NAME` | Traefik dashboard domain |
| `BACKEND_DOMAIN_NAME` | Backend API domain (`api.localelive.space`) |
| `GROQ_API_KEY` | LLM inference |
| `GOOGLE_MAPS_API_KEY` | Places fallback search |
| `ORS_API_KEY` | Travel time calculation |
| `TAVILY_API_KEY` | Web search for general questions |
| `MONGODB_URL` | IoT sensor database |
| `LANGCHAIN_API_KEY` | LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | Enable/disable tracing (`true`/`false`) |
| `POSTGRES_URL` | Conversation persistence (Neon) |
| `CLERK_JWKS_URL` | Backend JWT verification |
| `LLM_MODEL` | Groq model name (e.g. `llama-3.1-8b-instant`) |
| `ENABLE_PLACE_DETAILS` | Enable enriched place data (`true`) |
