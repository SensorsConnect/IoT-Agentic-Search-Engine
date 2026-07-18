# LocaleLive AWS Migration — Deployment & Validation Checklist

Follow these steps in order. Do NOT transfer the domain until all checks in Step 5 pass.

**Status:**
- [x] Step 1 — Migration branch created (`feat/aws-cost-migration`)
- [x] Step 2 — Frontend deployed to Vercel (`localelive-frontend.vercel.app`)
- [ ] Step 3 — Backend deployed to AWS Lambda
- [ ] Step 4 — Connect frontend to Lambda URL
- [ ] Step 5 — Full validation
- [ ] Step 6 — Staging subdomain (optional)
- [ ] Step 7 — Cut over domain
- [ ] Step 8 — Decommission EC2

---

## Architecture (Updated)

| Service | Role | Cost/month |
|---------|------|-----------|
| AWS Lambda + API Gateway | Backend API | ~$0 (free tier) |
| Vercel | Frontend | $0 (free tier) |
| Route 53 | DNS | ~$0.50 |
| **Total** | | **~$0.50/month** |

**Why Lambda is now viable** (was blocked before, now unblocked):
- Removed `torch` + `transformers` + `sentence-transformers` (~1.4GB) → image is now ~300MB
- Cold start dropped from 20–50s to ~3–8s
- Memory needed dropped from 2–3GB to 512MB–1GB
- Embeddings now use HuggingFace Inference API (`HF_API_KEY`)

---

## Step 0: Prerequisites

- [ ] AWS account with Lambda + API Gateway + ECR enabled (`us-east-1` recommended)
- [ ] Vercel project connected to `SensorsConnect/localelive-frontend` ✓ (done)
- [ ] Route 53 hosted zone for `localelive.space` (keep — don't delete)
- [ ] Current EC2 still running (do not stop until Step 8)
- [ ] `backend/.env` file handy with all current values

---

## Step 1: Migration Branch ✓ DONE

Branch `feat/aws-cost-migration` already exists and is pushed.

---

## Step 2: Frontend on Vercel ✓ DONE

Frontend is live at `localelive-frontend.vercel.app`.
`NEXT_PUBLIC_BACKEND_URL` is currently blank — fill in after Step 3.

---

## Step 3: Deploy Backend to AWS Lambda

### 3a. Push image to ECR

Lambda container images must come from **Amazon ECR** (not Docker Hub directly).

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repo (one-time)
aws ecr create-repository --repository-name localelive-backend --region us-east-1

# Pull from Docker Hub and push to ECR
docker pull elewah/localelive-backend:latest
docker tag elewah/localelive-backend:latest \
  <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/localelive-backend:latest
docker push \
  <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/localelive-backend:latest
```

### 3b. Add Mangum adapter to backend

Lambda needs an ASGI adapter. Add to `backend/requirements_pip.txt`:
```
mangum>=0.17.0
```

Update `backend/src/main.py` — add at the bottom:
```python
from mangum import Mangum
handler = Mangum(app, lifespan="off")
```

Rebuild and push the image after this change (GitHub Actions CI will do it on push to `main`).

### 3c. Create Lambda Function

1. AWS Console → **Lambda** → **Create function**
2. Select **Container image**
3. Image URI: browse ECR → select `localelive-backend:latest`
4. Architecture: `x86_64`
5. Memory: `1024 MB` (start here — increase to 2048 if needed)
6. Timeout: `5 minutes` (300 seconds — LangGraph queries can take 30–90s)
7. Click **Create function**

### 3d. Set Environment Variables in Lambda

Lambda console → your function → **Configuration** → **Environment variables** → Edit:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | *(from backend/.env)* |
| `LLM_MODEL` | *(from backend/.env)* |
| `MONGODB_URL` | *(from backend/.env)* |
| `POSTGRES_URL` | *(Neon URL from backend/.env)* |
| `GOOGLE_MAPS_API_KEY` | *(from backend/.env)* |
| `ORS_API_KEY` | *(from backend/.env)* |
| `TAVILY_API_KEY` | *(from backend/.env)* |
| `CLERK_JWKS_URL` | *(from backend/.env)* |
| `LANGCHAIN_API_KEY` | *(from backend/.env)* |
| `LANGCHAIN_TRACING_V2` | `true` |
| `HF_API_KEY` | *(from backend/.env)* |
| `MILVUS_DB_PATH` | `/tmp/milvus_lite.db` |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://localelive-frontend.vercel.app` |

> Note: `MILVUS_DB_PATH` uses `/tmp/` — the only writable directory in Lambda.

### 3e. Create API Gateway

1. AWS Console → **API Gateway** → **Create API** → **HTTP API**
2. Integration: Lambda → select your function
3. Routes: `ANY /{proxy+}` → your Lambda
4. Stage: `$default` (auto-deploy)
5. Click **Create**
6. Copy the API Gateway URL: `https://xxxx.execute-api.us-east-1.amazonaws.com`

### 3f. Fix PostgreSQL pool for Lambda

Lambda freezes/thaws containers — persistent connection pools go stale.
Add this to `backend/src/db/engine.py` (detect Lambda environment):

```python
import os
from sqlalchemy.pool import NullPool

# Lambda freezes containers — NullPool creates fresh connections per request
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    engine = create_engine(POSTGRES_URL, poolclass=NullPool)
else:
    engine = create_engine(POSTGRES_URL, pool_size=5, ...)
```

### 3g. Test Lambda directly

```bash
# Health check
curl https://xxxx.execute-api.us-east-1.amazonaws.com/health
# Expected: {"status": "ok"}

# Should return 401 (proves endpoint is reachable and auth is working)
curl https://xxxx.execute-api.us-east-1.amazonaws.com/api/v1/conversations
```

---

## Step 4: Connect Frontend to Lambda URL

1. Vercel dashboard → `localelive-frontend` project → **Settings** → **Environment Variables**
2. Set `NEXT_PUBLIC_BACKEND_URL` = `https://xxxx.execute-api.us-east-1.amazonaws.com`
3. Scope: **All Environments**
4. Trigger a redeploy: Deployments → latest → **Redeploy**

---

## Step 5: Full Validation (DO THIS BEFORE TOUCHING DNS)

Use `https://localelive-frontend.vercel.app` for all tests.

### Authentication
- [ ] Landing page loads correctly
- [ ] Sign In → Clerk modal appears
- [ ] Sign in with existing account → redirected to `/chat`
- [ ] Sign up with new account → redirected to `/chat`
- [ ] Sign out → redirected to landing page
- [ ] Refresh on `/chat` → stays logged in

### Chat / Backend
- [ ] Map loads on chat page (Mapbox visible)
- [ ] Send a greeting → backend responds within 15 seconds
- [ ] Send a location-based query (e.g. "coffee near me") → returns places
- [ ] Conversation appears in sidebar history
- [ ] Reload → previous conversation still in sidebar (PostgreSQL persistence)
- [ ] Rename a conversation → name updates
- [ ] Delete a conversation → disappears

### Performance
- [ ] First request (cold start): response within 15 seconds
- [ ] Subsequent requests: response within 5–30 seconds
- [ ] Second cold start (after 15+ min idle): still within 15 seconds

### Error Cases
- [ ] Browser devtools → no CORS errors
- [ ] Lambda console → Monitoring → no timeout or OOM errors

---

## Step 6: Add Staging Subdomain (Optional but Recommended)

1. Vercel dashboard → **Domains** → Add `staging.localelive.space`
2. Route 53 → add CNAME `staging` → Vercel's assigned value
3. API Gateway → **Custom domain names** → Add `api-staging.localelive.space`
4. Route 53 → add CNAME for `api-staging`
5. Test `https://staging.localelive.space` with `NEXT_PUBLIC_BACKEND_URL` = `https://api-staging.localelive.space`

---

## Step 7: Cut Over Domain (Production)

Only proceed if all Step 5 checks passed.

### 7a. Add custom domain to API Gateway

1. API Gateway → **Custom domain names** → Add `api.localelive.space`
2. API Gateway shows a CNAME → add it in Route 53
3. Update `CORS_ORIGINS` Lambda env var to `https://localelive.space`

### 7b. Add custom domain to Vercel

1. Vercel dashboard → **Settings** → **Domains** → Add `localelive.space` and `www.localelive.space`
2. Update Route 53 A/CNAME records to Vercel's provided values
3. Update `NEXT_PUBLIC_BACKEND_URL` in Vercel to `https://api.localelive.space`
4. Redeploy Vercel

### 7c. Verify after DNS switch

- [ ] `https://localelive.space` loads
- [ ] SSL certificate valid
- [ ] Sign in works on production domain
- [ ] Chat query works end-to-end

---

## Step 8: Decommission EC2 (48h After Cutover)

Wait 48 hours. If no issues:

1. SSH into EC2 → `docker-compose down`
2. Verify `localelive.space` still works
3. AWS Console → EC2 → Stop → wait 24h → Terminate
4. Release Elastic IP
5. Delete EBS volume

**No warm-up monitor needed** — Lambda cold starts are now ~3–8s, acceptable without keep-warm pings.

**Estimated monthly cost: ~$0.50/month** (vs ~$45–55 on EC2)

---

## Rollback Plan

If something breaks after domain cutover:
1. Route 53 → revert `localelive.space` records back to EC2 Elastic IP
2. DNS propagates in 2–5 minutes
3. EC2 is still running until Step 8 — rollback is instant
