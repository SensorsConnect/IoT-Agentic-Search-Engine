# LocaleLive — From Research Demo to Production App

## Context

LocaleLive (live at https://localelive.space/) is currently a research demo for the paper "Agentic Search Engine for Real-Time IoT Data" (https://www.mdpi.com/1424-8220/25/19/5995). The existing codebase has a FastAPI + LangGraph multi-agent backend and a Next.js chat frontend, with 37k+ IoT documents covering 500 service types in Toronto via MongoDB.

The goal is to transform this demo into a **production-ready hyperlocal discovery platform** where users discover real-time local offers, events, and crowd levels, and businesses publish real-time offers and updates. Solo founder, MVP-first, cost-aware.

**Key Decisions**:
- **Deployment**: AWS EC2 with Docker Compose (current) → ECS Fargate when scaling. $600 AWS credits available.
- **Auth**: Clerk (managed, free <10k MAU)
- **Priority**: Fix bugs first (Phase 0), then new features
- **Timeline**: ~3 months to beta (50 businesses, 200 users)
- **First market**: Canada (Toronto), then expand internationally

---

## 1. Product Vision

**What**: AI-powered hyperlocal discovery platform combining IoT real-time data (occupancy, wait times) with agentic AI for context-aware recommendations.

**Target Users**: Urban residents/visitors in Toronto who want "what's nearby, open, not crowded, and has good deals" — not just "what exists."

**Target Businesses**: Restaurants, cafes, salons, clinics, gyms, retail — any local business wanting real-time visibility to nearby customers.

**Differentiator**: 37k IoT documents with real occupancy data + agentic AI is a genuine moat that a chat wrapper over Google Maps cannot replicate.

**Business Model (Phased)**:
1. Free user platform for adoption
2. Free/low-friction business onboarding
3. Later: premium listings ($29/mo), promoted offers ($99/mo), event boosting, analytics subscriptions

---

## 2. Critical Bugs to Fix First

| ID | Bug | File | Fix |
|----|-----|------|-----|
| TD-1 | Hardcoded Toronto coordinates — ignores user location | `backend/src/agents/iot_engine.py:23-24` | Use `state["location_finder_results"]["coordinates"]` |
| TD-2 | GoogleKnowledgeGraph returns `input` (Python builtin) | `backend/src/agents/google_knowledge_graph.py:5` | Remove node entirely (broken/unused) |
| TD-3 | In-memory SQLite checkpointer — conversations lost on restart | `backend/src/graph.py:7` | Switch to `langgraph-checkpoint-postgres` |
| TD-4 | CORS wildcard `["*"]` | `backend/src/main.py:27` | Restrict to actual domain |
| TD-5 | No error handling on PUT /query | `backend/src/main.py:84-109` | Add try/except, structured error responses |
| TD-6 | Dead code in scrapper_router (both branches return same value) | `backend/src/routers.py:8-12` | Clean up |
| TD-7 | Bare except blocks in agents | `assistant_agent.py:23`, `reviewer_agent.py:41` | Catch specific exceptions |
| TD-8 | Embedding model loaded on every vector search call | `backend/src/vector_db/vector_database.py:31` | Load once at startup |
| TD-9 | reviewer_agent returns state without required keys in some branches | `backend/src/agents/reviewer_agent.py:70-72` | Always use `prepaer_states` |
| TD-10 | Massive requirements with unused packages (tensorflow, spacy, streamlit) | `backend/requirements_pip.txt` | Trim to what's actually used |

---

## 3. MVP Definition

### Core User Features

1. AI chat with **actual** location-aware recommendations (bug fix)
2. Real-time occupancy display (low/medium/high from IoT data)
3. Travel time estimates (OSRM, already built)
4. User auth (email + Google via Clerk)
5. Server-side conversation persistence
6. Saved/bookmarked places
7. Category browsing (`/explore` page) — non-chat discovery
8. Map view of nearby results (Leaflet.js)

### Core Business Features

1. Business claim flow (search existing IoT data, verify via email/phone)
2. Business profile (hours, description, photos, contact)
3. Post offers (title, description, discount, expiry)
4. Basic analytics (views, AI mentions)

### Admin Features

1. Approve/reject business claims
2. Content moderation queue
3. System health metrics

### NOT in v1

- Native mobile apps (responsive web is sufficient)
- Payment processing / subscriptions
- User-generated reviews
- Multi-city support
- Push notifications (email only)
- Social features
- Advanced ML models
- Microservices / Kubernetes

---

## 4. Phased Roadmap

### Phase 0: Foundation & Bug Fixes (Weeks 1-3)

**Goals**: Fix critical bugs, production hardening, CI/CD

**Deliverables**:
- Fix IoT_engine location bug (P0)
- Remove broken GoogleKnowledgeGraph agent
- Error handling on PUT /query endpoint
- CORS restrictions + rate limiting (slowapi)
- Structured logging, env var validation on startup
- GitHub Actions CI (ruff lint, tsc, smoke tests)
- Replace in-memory SQLite with langgraph-checkpoint-postgres
- Trim unused dependencies

**Success**: All features work with real user coordinates; zero crashes on happy path; CI green

### Phase 1: Auth, Persistence & API (Weeks 4-7)

**Goals**: User accounts, server-side persistence, proper API

**Deliverables**:
- Clerk integration (email + Google OAuth)
- Clerk JWT verification middleware on FastAPI
- PostgreSQL schema: `users`, `conversations`, `messages`, `saved_places`
- Alembic migrations setup
- API prefix `/api/v1/` with versioned endpoints
- Rate limiting per user
- Migrate frontend from localStorage to API for conversations
- New endpoints: conversations CRUD, saved places

**Key files to modify**:
- `backend/src/main.py` — add auth middleware, new routes
- `frontend/components/Chat/Chat.tsx` — API calls instead of localStorage
- `frontend/components/Chat/useChatHook.ts` — server-side persistence

### Phase 2: Business Portal & Offers (Weeks 8-13)

**Goals**: Businesses can claim listings, post offers; offers appear in AI responses

**Deliverables**:
- PostgreSQL schema: `businesses`, `business_locations`, `offers`, `events`, `categories`
- Business claim + verification flow
- Business dashboard pages (`/business/`)
- Offer creation + management
- Integrate offers into AI responses (new `offers_agent` in LangGraph or inline check)
- Category browsing page (`/explore`) with map view (Leaflet)
- Admin moderation queue
- Photo upload to AWS S3

**Key files to modify**:
- `backend/src/graph_init.py` — add offers_agent node
- `backend/src/agents_prompt.py` — update generator prompt to include offers
- New: `frontend/app/business/` pages, `frontend/app/explore/` page

### Phase 3: Real-Time & Engagement (Weeks 14-19)

**Goals**: Streaming responses, notifications, analytics

**Deliverables**:
- SSE streaming for AI responses (replace full-response pattern)
- Crowd status display (parse IoT occupancy -> colored badges)
- Email notifications via AWS SES (new offer from saved business, weekly digest)
- PostHog analytics integration
- Interactive map on /explore with crowd indicators
- Conversation memory summarization

### Phase 4: Monetization Infrastructure (Weeks 20-25)

**Goals**: Build billing infrastructure (keep everything free initially)

**Deliverables**:
- Tiered business accounts (Free/Pro/Premium schema, all free initially)
- Stripe integration
- Promoted listings infrastructure ("Sponsored" flag)
- Business API (API keys, usage tracking)
- Admin revenue dashboard

### Phase 5: Scale & Multi-City (Weeks 26+)

- Multi-city architecture (city selector, per-city data)
- Redis caching, connection pooling, LLM response caching
- Personalized recommendations from user history
- Second city launch (Vancouver or Montreal)
- Multi-region AWS deployment (ECS Fargate in other regions)

---

## 5. System Architecture

**Deployment**: AWS EC2 (current) -> AWS ECS Fargate (when scaling needed). $600 AWS credits available.

### Phase 0-2: EC2 + Docker Compose (Keep Current)

```
              [AWS EC2 + Docker Compose]
                       |
              [Traefik (TLS + routing)]
              /                       \
    [Next.js Frontend :3000]    [FastAPI Backend :8000]
              |                        |
         [Clerk Auth]           [LangGraph Agents]
                               /    |      |     \
                          [PostgreSQL] [MongoDB] [Redis]  [Groq LLM]
                           (RDS)     (Atlas)  (ElastiCache)
```

### Phase 3+: ECS Fargate (When Scaling Needed)

```
              [AWS ALB + ACM (TLS)]
              /                    \
    [ECS Fargate: Frontend]   [ECS Fargate: Backend]
              |                        |
         [Clerk Auth]           [LangGraph Agents]
                               /    |      |     \
                          [RDS Postgres] [MongoDB] [ElastiCache]  [Groq]
```

### Migration Path (use AWS credits wisely)

- **Now (Phase 0-1)**: Stay on EC2 + Docker Compose. It works. Add AWS RDS PostgreSQL (free tier: db.t3.micro, 20GB) to replace Neon — keeps data in same region, lower latency. Add ElastiCache Redis (cache.t3.micro) for rate limiting + caching.
- **Phase 2-3**: When traffic grows or you need auto-scaling, migrate to ECS Fargate. Your existing Dockerfiles work as-is. ALB replaces Traefik. ACM gives free TLS certificates.
- **Multi-country**: ECS + ALB makes it easy to deploy in other AWS regions (eu-west-1 for Europe, etc.). MongoDB Atlas already supports multi-region.

### Stack Summary

| Layer | Tech | Cost (AWS credits) | Why |
|-------|------|------|-----|
| Compute | EC2 t3.medium -> ECS Fargate | ~$30/mo (credits) | Already working, Docker-native scaling path |
| Frontend | Next.js 14 | Bundled with compute | Already built |
| Backend | FastAPI + LangGraph | Bundled with compute | Already built |
| Auth | Clerk | Free (<10k MAU) | Zero backend auth code, fastest to implement |
| Primary DB | AWS RDS PostgreSQL | Free tier (12mo) then ~$15/mo | Same-region latency, managed backups, IAM auth |
| IoT Data | MongoDB Atlas | Free (512 MB) -> $9/mo | Already in use, geospatial, multi-region ready |
| Cache | AWS ElastiCache Redis | ~$12/mo (credits) | Rate limiting, query caching, same VPC |
| LLM | Groq (llama-3.1-8b) | Free tier | Already integrated, fast inference |
| Maps Display | Leaflet.js | Free | Open source |
| Maps Search | Google Maps API | ~$17/1k reqs | Already integrated |
| Email | AWS SES | Free (62k/mo from EC2) | Already on AWS, much cheaper than alternatives |
| Analytics | PostHog | Free (1M events) | Features + analytics |
| Errors | Sentry | Free tier | Industry standard |
| Files | AWS S3 | Free tier (5 GB) then ~$0.02/GB | Already on AWS, no extra vendor |
| CI/CD | GitHub Actions | Free | Can also add AWS CodeDeploy later |
| DNS | AWS Route 53 | ~$0.50/mo | Needed for multi-region, health checks |

**Estimated cost with credits**: ~$0-20/month (free tiers + credits cover most). After credits: ~$60-80/month at 1000+ users.

**Key AWS advantage**: Everything in one VPC = low latency between services, IAM for security, CloudWatch for monitoring, and your $600 credits cover ~8-10 months of infrastructure.

---

## 6. Data Model

### PostgreSQL (New — via Alembic migrations)

**users** — synced from Clerk webhooks

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user',  -- 'user', 'business_owner', 'admin'
    city VARCHAR(100) DEFAULT 'Toronto',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**businesses**

```sql
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    category VARCHAR(100) NOT NULL,  -- maps to MongoDB collection names
    website VARCHAR(500),
    phone VARCHAR(50),
    email VARCHAR(255),
    logo_url TEXT,
    cover_image_url TEXT,
    claimed_by UUID REFERENCES users(id),
    verification_status VARCHAR(50) DEFAULT 'unclaimed',
        -- 'unclaimed', 'pending', 'verified', 'rejected'
    tier VARCHAR(50) DEFAULT 'free',  -- 'free', 'pro', 'premium'
    mongo_collection VARCHAR(255),
    stripe_customer_id VARCHAR(255),  -- nullable, for future monetization
    is_promoted BOOLEAN DEFAULT false,
    boost_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**business_locations**

```sql
CREATE TABLE business_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Toronto',
    province VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Canada',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    hours JSONB,  -- {"monday": {"open": "09:00", "close": "17:00"}, ...}
    is_primary BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_business_locations_geo ON business_locations
    USING GIST (ST_MakePoint(longitude, latitude));
```

**offers**

```sql
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    location_id UUID REFERENCES business_locations(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type VARCHAR(50),  -- 'percentage', 'fixed', 'bogo', 'freebie'
    discount_value DECIMAL(10,2),
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'active',  -- 'draft', 'active', 'expired', 'paused'
    max_redemptions INT,
    current_redemptions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_offers_active ON offers (status, end_date)
    WHERE status = 'active';
```

**events**

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    location_id UUID REFERENCES business_locations(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule VARCHAR(255),  -- iCal RRULE format
    status VARCHAR(50) DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**conversations** — replaces SQLite checkpointer

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    city VARCHAR(100) DEFAULT 'Toronto',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant'
    content TEXT NOT NULL,
    metadata JSONB,  -- agent used, response time, location at time of query
    created_at TIMESTAMP DEFAULT NOW()
);
```

**saved_places**

```sql
CREATE TABLE saved_places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, business_id)
);
```

**categories**

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(50),
    parent_id INT REFERENCES categories(id),
    display_order INT DEFAULT 0
);
```

**crowd_status** — cached from IoT, 15-min TTL

```sql
CREATE TABLE crowd_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'very_high'
    occupancy_pct INT,  -- 0-100
    source VARCHAR(50) DEFAULT 'iot',  -- 'iot', 'google', 'user_report'
    measured_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '15 minutes'
);
```

**analytics_events** — append-only

```sql
CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,
        -- 'query', 'view_business', 'save_place', 'view_offer', 'click_offer'
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_analytics_events_type_date ON analytics_events (event_type, created_at);
```

**moderation_queue**

```sql
CREATE TABLE moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,  -- 'business', 'offer', 'event'
    entity_id UUID NOT NULL,
    reason VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### MongoDB (Keep existing, enhance)

Keep `Sensors_Connect_DB_V2` (37k docs, 500 collections). Add `postgres_business_id` field to link IoT data to PostgreSQL business records after claiming.

---

## 7. AI Strategy

| Use Case | Current | Recommendation | Rules Alternative |
|----------|---------|---------------|-------------------|
| Intent classification (assistant_agent) | LLM (Groq) | **Keep LLM** — handles nuanced queries well | Regex/keywords would fail on "somewhere not crowded for a quick bite" |
| Response generation (generator_agent) | LLM with context | **Keep LLM** — core value prop | Template-based would lose conversational quality |
| Quality review (reviewer_agent) | LLM | **Replace with rules** for v1 — saves 1 LLM call/query | Check: response non-empty, contains entities, addresses query keywords |
| Service type matching (vector_db) | Sentence-BERT + HNSW | **Keep** — handles synonyms well | 500-entry keyword dict would miss fuzzy matches |
| Offer relevance (NEW) | N/A | **Start with rules** (category + distance + active) | Add LLM ranking only if rules produce irrelevant results |
| Personalization | N/A | **Defer to Phase 5** | Time-of-day heuristics sufficient for now |

**Cost optimization**: Groq free tier (30 RPM). Cache identical queries in Redis (15-min TTL for location-dependent, 1-hour for general). Replace reviewer LLM with rules = ~33% fewer LLM calls.

---

## 8. Crowd & Real-Time Strategy

**v1 (Phase 0-2)**: Read occupancy from existing IoT MongoDB docs (hourly occupancy per day-of-week). Map to labels: 0-30% "Not Busy", 31-60% "Moderate", 61-80% "Busy", 81-100% "Very Busy". Display as colored badges. Fix: `sorting_serivces.py` strips occupancy data before returning — stop deleting it.

**v2 (Phase 3-4)**: Merge IoT + Google Popular Times + business self-reports. Weight: IoT 50%, Google 30%, business 20%. Cache in `crowd_status` table (15-min TTL).

**v3 (Phase 5+)**: Predictive models on historical patterns + weather/event correlation.

---

## 9. Business Portal Strategy

### Onboarding Flow

1. Business owner signs up (Clerk, same auth as users, with "business_owner" role)
2. Search for their business in the existing IoT database
3. If found: "Claim this business" -> verify via phone/email code
4. If not found: "Add your business" -> fill in details -> admin approval
5. After verification: access to business dashboard

### Business Profile

- Name, category, description (rich text, max 500 chars)
- Photos (up to 5, stored in AWS S3)
- Operating hours (JSONB, supports special hours)
- Contact info (phone, email, website, social links)
- Location on map (auto-populated from IoT data or manual pin)

### Offers & Events

- **Offer creation**: Title, description, discount type/value, date range, optional photo
- **Scheduling**: Set start/end dates; offers auto-expire
- **Limits**: Free tier: 3 active offers at a time. Pro tier: unlimited.
- **Events**: Similar to offers but with date/time, optional recurring

### Dashboard

- **Overview**: Profile completeness score, total views, total AI mentions
- **Offers**: Active/expired offers, create new
- **Analytics**: Views over time, query keywords that surfaced this business
- **Settings**: Business info, notification preferences

### Moderation

- All new businesses and offers go through moderation queue
- Auto-approve if business was in IoT database (pre-verified)
- Manual review for new additions
- Flag system for inappropriate content

---

## 10. Go-To-Market Technical Support

- **Toronto first**: Downtown core + Liberty Village, Kensington Market, Queen West, Yorkville, Distillery District
- **Pre-seed**: Script to import 500+ businesses from MongoDB into PostgreSQL `businesses` table
- **Business outreach**: 50 businesses via email/in-person; "Founding Business" badge (permanent)
- **Pilot**: 10 friends (weeks 1-2) -> 50 closed beta (weeks 3-4) -> 200 open beta (weeks 5-8) -> public launch
- **Landing page**: Improve existing `/` with clear value prop, demo video, waitlist
- **Feedback**: Embedded widget (Canny free or simple form)

---

## 11. Monetization Readiness

Build these abstractions now, monetize later:

1. **Tier system**: Every business has a `tier` field from day one. All features check tier permissions even if all tiers have same limits initially.
2. **Feature flags**: Simple config-based feature flags (JSON in env var or Postgres table).
3. **Usage metering**: Track offer creation count, API calls, analytics views per business per month in `analytics_events`.
4. **Stripe Customer ID**: `stripe_customer_id` nullable field on `businesses` from day one.
5. **Promoted results**: `is_promoted` and `boost_score` fields on businesses. Generator_agent prompt extends to mention "Sponsored" flag.

### Revenue Streams (When Ready)

1. **Business subscriptions**: Pro ($29/mo), Premium ($99/mo)
2. **Promoted listings**: Pay-per-impression or flat monthly boost
3. **Event boosting**: One-time fee to boost event visibility
4. **Analytics upsell**: Detailed analytics only for paid tiers
5. **API access**: For chains/enterprises wanting programmatic access

---

## 12. Security, Privacy & Compliance

- **Auth**: Clerk handles passwords, sessions, CSRF
- **CORS**: Restrict to actual domain (fix `["*"]`)
- **Rate limiting**: Per-IP and per-user on all endpoints
- **Location privacy**: Store at city-block precision (3 decimals ~100m); no location history log; clear opt-out
- **Input sanitization**: Pydantic v2 validates requests; strip HTML from user input
- **Business verification**: Email/phone code + admin approval; max 3 claims/user/day
- **Content moderation**: All new businesses/offers go through moderation queue
- **Canadian compliance**: PIPEDA (privacy policy required), CASL (email opt-in required), WCAG 2.1 AA
- **Secrets**: AWS Secrets Manager or Parameter Store (not .env in production)

---

## 13. Development Plan (Solo Founder)

### 30-Day Action Plan

| Day | Task | Output |
|-----|------|--------|
| 1 | Fix IoT_engine location bug | Correct coordinates in queries |
| 2 | Remove GoogleKnowledgeGraph; fix reviewer_agent returns | Clean agent graph |
| 3 | Error handling on PUT /query | Structured error responses |
| 4 | CORS fix + slowapi rate limiting | Security hardened |
| 5 | Structured logging + env var validation | Production logging |
| 6-7 | GitHub Actions CI (ruff, tsc, smoke tests) | Green CI pipeline |
| 8-9 | langgraph-checkpoint-postgres migration | Persistent conversations |
| 10-11 | Clerk setup + frontend auth flow | Users can sign up/in |
| 12-13 | Clerk JWT middleware on FastAPI | Authenticated API |
| 14 | Users table + Clerk webhook | User records in Postgres |
| 15-16 | Alembic setup + conversations/messages tables | Migration system |
| 17-18 | Conversation persistence API endpoints | Server-side history |
| 19-20 | Frontend migration from localStorage to API | Conversations persist across devices |
| 21-22 | Saved places API + frontend UI | Users can bookmark |
| 23-24 | Category browsing page (/explore) | Non-chat discovery |
| 25-26 | Business schema + Alembic migration | Data model ready |
| 27-28 | Business search + claim initiation | Businesses can start claiming |
| 29-30 | E2E testing + bug fixes + deploy | Phase 1 complete |

### 90-Day Roadmap

| Month | Focus | Outcome |
|-------|-------|---------|
| 1 | Bug fixes + Auth + Persistence | App works correctly with user accounts |
| 2 | Business portal + Offers | Businesses claim listings, post offers |
| 3 | Polish + Beta launch | 50 businesses, 200 users, real feedback |

### Buy vs Build

| Component | Decision | Why |
|-----------|----------|-----|
| Auth | BUY (Clerk) | Security-critical, free <10k MAU |
| Email | USE (AWS SES) | Already on AWS, 62k free emails/mo from EC2 |
| Database | USE (AWS RDS PostgreSQL) | Same VPC, managed backups, free tier 12mo |
| Cache | USE (AWS ElastiCache Redis) | Same VPC, low latency, covered by credits |
| File storage | USE (AWS S3) | Already on AWS, free tier 5GB |
| Analytics | BUY (PostHog) | Building from scratch = months |
| Error tracking | BUY (Sentry) | Free tier sufficient |
| Maps display | USE (Leaflet) | Free, open-source |
| Maps search | USE (Google Maps) | Already integrated |
| LLM | USE (Groq) | Already integrated, fast |
| Payment | BUY (Stripe) | Phase 4 only |
| Chat UI | BUILD | Core product |
| Business portal | BUILD | Core product |
| AI agents | BUILD | Core differentiator |
| Admin tools | BUILD (simple) | Protected Next.js pages |

### What to Postpone

- Native mobile apps
- Multi-language support
- Advanced ML models (recommendation, prediction)
- Real-time bidding / ad system
- Social features
- Business API / webhooks
- Multi-tenant architecture

---

## 14. Technical Debt & Risk Register

### Existing Technical Debt

| ID | Debt | Severity | Location |
|----|------|----------|----------|
| TD-1 | Hardcoded Toronto coordinates in IoT_engine | CRITICAL | `backend/src/agents/iot_engine.py:23-24` |
| TD-2 | Broken GoogleKnowledgeGraph agent | HIGH | `backend/src/agents/google_knowledge_graph.py:5` |
| TD-3 | In-memory SQLite checkpointer | HIGH | `backend/src/graph.py:7` |
| TD-4 | CORS wildcard `["*"]` | HIGH | `backend/src/main.py:27` |
| TD-5 | No error handling on query endpoint | HIGH | `backend/src/main.py:84-109` |
| TD-6 | Dead code in scrapper_router | LOW | `backend/src/routers.py:8-12` |
| TD-7 | Bare except blocks in agents | MEDIUM | `assistant_agent.py`, `reviewer_agent.py` |
| TD-8 | Embedding model loaded on every call | MEDIUM | `backend/src/vector_db/vector_database.py:31` |
| TD-9 | reviewer_agent missing state keys | MEDIUM | `backend/src/agents/reviewer_agent.py:70-72` |
| TD-10 | Unused packages in requirements | LOW | `backend/requirements_pip.txt` |

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Groq API downtime | Medium | High | Add OpenAI/Anthropic fallback; cache responses |
| MongoDB free tier limits | Low | High | Monitor; upgrade ($9/mo) when needed |
| Solo founder burnout | High | Critical | Strict MVP scope; use AI coding tools; 2-week sprints |
| No business adoption | Medium | High | Pre-seed from IoT data; personal outreach |
| LLM generates incorrect recommendations | Medium | High | Rules-based reviewer; content safety checks |
| Google Maps API costs | Low | Medium | Cache results; consider OSM alternatives |
| IoT data staleness | Medium | Medium | "Last updated" timestamps; flag stale data |
| Privacy complaint about location | Low | High | Clear consent; precision reduction; privacy policy |

---

## 15. Top 5 Mistakes to Avoid

1. **Building features before fixing bugs** — hardcoded coordinates mean every recommendation is wrong for non-center users. Fix this first.

2. **Building your own auth** — use Clerk, save weeks, avoid security holes. Solo founders spend weeks building auth that has vulnerabilities.

3. **Premature multi-city** — go deep in Toronto before going wide. A mediocre experience in 5 cities is worse than an excellent experience in 1 city.

4. **Over-engineering** — no microservices, no K8s, no event sourcing. A FastAPI monolith + PostgreSQL + MongoDB handles 10k users easily.

5. **Launching monetization before PMF** — keep everything free until 500+ active users and 50+ active businesses. If businesses won't use it for free, they won't pay.

---

## Verification Checklist

After implementing each phase:

- [ ] Run full agent query flow with real Toronto coordinates and verify correct results
- [ ] Run with non-Toronto coordinates and verify Google Maps fallback works
- [ ] Verify conversations persist across server restarts
- [ ] Test auth flow end-to-end (signup -> query -> save place -> return)
- [ ] Load test: 10 concurrent queries should complete < 5s each
- [ ] Business flow: claim -> verify -> post offer -> offer appears in AI response
- [ ] Check Sentry for unhandled exceptions; LangSmith for LLM traces
- [ ] Mobile responsive check on iOS Safari and Android Chrome
- [ ] Security: test CORS, rate limiting, auth bypass attempts
