import os
import logging
from contextlib import asynccontextmanager

# --- Structured logging (must be first — basicConfig is a no-op if any handler
#     already exists, and any logging call before this would auto-install one) ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,  # override any handler auto-installed by earlier imports
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Env var validation ---
REQUIRED_ENV_VARS = ["GROQ_API_KEY", "LLM_MODEL", "MONGODB_URL"]
OPTIONAL_ENV_VARS = ["POSTGRES_URL", "GOOGLE_MAPS_API_KEY", "ORS_API_KEY", "TAVILY_API_KEY",
                     "LANGCHAIN_API_KEY", "CORS_ORIGINS", "CLERK_JWKS_URL"]

missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

for v in OPTIONAL_ENV_VARS:
    if not os.environ.get(v):
        logger.warning(f"Optional env var {v} is not set")


# --- Rate limiting ---
def _rate_limit_key(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        import jwt
        try:
            payload = jwt.decode(auth_header[7:], options={"verify_signature": False})
            clerk_id = payload.get("sub", "")
            if clerk_id:
                return f"user:{clerk_id}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_rate_limit_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from vector_db.vector_database import vector_db_push_batch
    vector_db_push_batch()  # no-op if collection already populated
    yield


# Lambda has a 10s init timeout — skip lifespan (vector DB init) on cold start.
# vector_db_push_batch() is called lazily on first IoT_engine invocation instead.
IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
app = FastAPI(
    title="LocaleLive API",
    version="1.0.1",
    lifespan=None if IS_LAMBDA else lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "")

if ENVIRONMENT == "production" and CORS_ORIGINS:
    origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]
else:
    origins = ["*"]
    if ENVIRONMENT == "production":
        logger.warning("CORS_ORIGINS not set in production, allowing all origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API v1 Router ---
from api.v1 import v1_router
app.include_router(v1_router)


@app.get("/")
async def root():
    return {
        "name": "LocaleLive API",
        "version": "1.0.1",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "swagger_url": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# Lambda handler — Mangum translates API Gateway events to ASGI
# Only active when running inside Lambda (AWS_LAMBDA_FUNCTION_NAME is set by the runtime)
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
