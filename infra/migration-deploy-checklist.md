# LocaleLive AWS Migration — Deployment & Validation Checklist

Follow these steps in order. Do NOT transfer the domain until all checks in Step 5 pass.

---

## Step 0: Prerequisites

- [ ] AWS account with App Runner enabled in your target region (recommend `us-east-1`)
- [ ] Vercel account linked to your GitHub account
- [ ] Route 53 hosted zone already exists for `localelive.space` (keep it — don't delete)
- [ ] Current EC2 still running (do not stop until Step 6)
- [ ] Have your current `.env` file on EC2 handy (you'll copy values from it)

---

## Step 1: Create Migration Branch

```bash
git checkout main
git pull
git checkout -b feat/aws-cost-migration
git push -u origin feat/aws-cost-migration
```

---

## Step 2: Deploy Frontend to Vercel (preview URL — no domain change yet)

Vercel always deploys your **production branch** (`main`) as the live site. Every other branch gets an auto-generated **preview URL**. We use the preview URL for staging validation before merging to `main`.

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → Import from GitHub → select `localelive` repo
2. Leave the **Production Branch** set to `main` (do not change it)
3. **Root Directory** → click **Edit** → set to `frontend` (the Next.js app is not at the repo root)
4. Framework preset: **Next.js** (auto-detected)
5. Set these **Environment Variables** in Vercel dashboard → Settings → Environment Variables → scope them to **All Environments** (Preview + Production):

   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_BACKEND_URL` | *(leave blank for now — fill in after Step 3)* |
   | `NEXT_PUBLIC_MAPBOX_TOKEN` | *(copy from current frontend .env.production)* |
   | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | *(copy from current frontend .env.production)* |
   | `CLERK_SECRET_KEY` | *(copy from current frontend .env.production)* |
   | `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` |
   | `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` |
   | `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` | `/chat` |
   | `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` | `/chat` |

6. Click **Deploy** — Vercel builds from `main`
7. Vercel assigns a permanent project URL like `localelive-elewah.vercel.app` — note it down
8. Push any commit to `feat/aws-cost-migration` → Vercel auto-builds a **preview deployment** at a URL like `localelive-git-feat-aws-cost-migration-elewah.vercel.app` — use this URL for all staging tests

**Note:** The `main` branch Vercel deployment will fail until `NEXT_PUBLIC_BACKEND_URL` is set (Step 4). That is expected — the EC2 app is still serving production traffic via its own domain during this whole process.

**Check:** Open the preview URL in a browser. The landing page should load. Login will fail until backend is set up (Step 3).

---

## Step 3: Deploy Backend to AWS App Runner

### 3a. Create App Runner Service

1. AWS Console → **App Runner** → **Create Service**
2. Source: **Container registry** → **Other registry (public)** → Image URI: `elewah/localelive-backend:latest`
3. Deployment settings: **Automatic** (triggers redeploy when Docker Hub image changes)
4. Port: `8000`
5. CPU: `1 vCPU` | Memory: `2 GB`
6. Health check: Protocol `HTTP`, Path `/health`, Interval `10` seconds

### 3b. Set Environment Variables in App Runner

Copy these from your current EC2 `.env`:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | *(from EC2 .env)* |
| `LLM_MODEL` | *(from EC2 .env)* |
| `MONGODB_URL` | *(from EC2 .env)* |
| `POSTGRES_URL` | *(Neon URL from EC2 .env)* |
| `GOOGLE_MAPS_API_KEY` | *(from EC2 .env)* |
| `ORS_API_KEY` | *(from EC2 .env)* |
| `TAVILY_API_KEY` | *(from EC2 .env)* |
| `CLERK_JWKS_URL` | *(from EC2 .env)* |
| `LANGCHAIN_API_KEY` | *(from EC2 .env)* |
| `LANGCHAIN_TRACING_V2` | `true` |
| `MILVUS_DB_PATH` | `/app/src/vector_db/milvus_data/milvus.db` |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://localelive.space,https://localelive-xxx.vercel.app` *(add Vercel preview URL from Step 2)* |

7. Click **Create & deploy** — wait 3–5 minutes for first deployment
8. App Runner will give you a URL like `https://xxxx.us-east-1.awsapprunner.com` — note it down

### 3c. Test Backend Directly

```bash
# Health check
curl https://xxxx.us-east-1.awsapprunner.com/health
# Expected: {"status": "ok"} or similar

# Should return 401 (auth required — proves the endpoint is reachable)
curl https://xxxx.us-east-1.awsapprunner.com/api/v1/conversations
```

---

## Step 4: Connect Frontend → Backend (Still on Preview URL)

1. In Vercel dashboard → **Settings** → **Environment Variables** → set `NEXT_PUBLIC_BACKEND_URL` = `https://xxxx.us-east-1.awsapprunner.com` (the App Runner URL from Step 3)
2. Scope it to **All Environments** (Preview + Production)
3. Go to **Deployments** → find the latest deployment for `feat/aws-cost-migration` → click the three dots → **Redeploy**
4. Wait for redeploy to finish (~1–2 min)

---

## Step 5: Full Validation (DO THIS BEFORE TOUCHING DNS)

Use the **Vercel preview URL** for `feat/aws-cost-migration` branch for all tests below.
Find it in: Vercel dashboard → Deployments → click the deployment for branch `feat/aws-cost-migration` → copy the preview URL (format: `localelive-git-feat-aws-cost-migration-elewah.vercel.app`).

### Authentication
- [ ] Landing page loads correctly
- [ ] Click Sign In → Clerk sign-in modal/page appears
- [ ] Sign in with an existing account → redirected to `/chat`
- [ ] Sign up with a new account → redirected to `/chat`
- [ ] Sign out → redirected to landing page
- [ ] Refresh on `/chat` → stays logged in (session persists)

### Chat / Backend
- [ ] Map loads on the chat page (Mapbox visible)
- [ ] Send a simple greeting → backend responds within 10 seconds
- [ ] Send a location-based query (e.g. "coffee near me") → backend returns places
- [ ] Conversation appears in sidebar history
- [ ] Reload page → previous conversation is still in sidebar (PostgreSQL persistence)
- [ ] Rename a conversation → name updates
- [ ] Delete a conversation → it disappears

### Performance
- [ ] First request after 15+ minutes idle: response within 20 seconds (App Runner warm-up)
- [ ] Subsequent requests: response within 5–30 seconds (normal LangGraph latency)

### Error Cases
- [ ] Open browser devtools Network tab — no CORS errors on API calls
- [ ] Check App Runner logs (AWS Console → App Runner → your service → Logs) — no OOM or crash errors

---

## Step 6: Add Staging Subdomain (Optional but Recommended)

Before pointing `localelive.space` at Vercel, set up a temporary subdomain to test with a real domain:

1. In **Vercel dashboard** → Domains → Add `staging.localelive.space`
2. In **Route 53** → Hosted Zone for `localelive.space` → Add record:
   - Type: `CNAME`
   - Name: `staging`
   - Value: Vercel's assigned CNAME (shown in Vercel dashboard)
3. Wait for DNS propagation (~2–5 min with Route 53)
4. Test `https://staging.localelive.space` — all Step 5 checks should pass

---

## Step 7: Cut Over Domain (Production)

Only proceed if all Step 5 checks passed.

### 7a. Merge branch to main (triggers Vercel production build)

```bash
git checkout main
git merge feat/aws-cost-migration
git push origin main
```

Vercel will automatically build and deploy the `main` branch to production. Wait for the build to succeed in the Vercel dashboard before touching DNS.

### 7b. Add custom domain to Vercel

1. In **Vercel dashboard** → **Settings** → **Domains** → Add `localelive.space` and `www.localelive.space`
2. Vercel shows you the DNS records to add — copy them

### 7c. Update DNS in Route 53

1. In **Route 53** → Hosted Zone for `localelive.space` → update the `A` record for `localelive.space`:
   - Type: `A` (Alias) or `CNAME` → use Vercel's provided value
2. Update `www` CNAME similarly
3. DNS propagates in ~2–5 minutes with Route 53

### 7d. Add custom domain for backend

1. In **App Runner** → your service → **Custom domains** → Add `api.localelive.space`
2. App Runner shows a CNAME record → add it in Route 53
3. Update `NEXT_PUBLIC_BACKEND_URL` in Vercel to `https://api.localelive.space`
4. Update `CORS_ORIGINS` in App Runner env vars to `https://localelive.space`
5. In Vercel dashboard → Deployments → **Redeploy** latest `main` deployment

### Verify after DNS switch

- [ ] `https://localelive.space` loads (not the Vercel preview URL)
- [ ] SSL certificate is valid (padlock icon)
- [ ] Sign in works on production domain
- [ ] Chat query works end-to-end

---

## Step 8: Keep Warm (Prevent Cold Starts)

Set up a free uptime monitor to ping the backend every 5 minutes:

1. Go to [uptimerobot.com](https://uptimerobot.com) → Create free account
2. Add monitor: HTTP(S), URL = `https://api.localelive.space/health`, interval = 5 minutes
3. This prevents App Runner from pausing the container between user sessions

---

## Step 9: Decommission EC2 (48h After Cutover)

Wait 48 hours after the domain cutover. If no issues:

1. SSH into EC2 → `docker-compose down`
2. Verify `localelive.space` still works (serving from Vercel/App Runner now)
3. AWS Console → EC2 → Stop instance → wait 24h → Terminate instance
4. Release the Elastic IP
5. Delete the EBS volume

**Estimated monthly savings: ~$33–43/month**

---

## Rollback Plan

If something breaks after domain cutover:
1. In Route 53 → revert `localelive.space` A/CNAME records back to the EC2 Elastic IP
2. DNS propagates in 2–5 minutes (Route 53 TTL)
3. EC2 is still running until Step 9 — rollback is instant
