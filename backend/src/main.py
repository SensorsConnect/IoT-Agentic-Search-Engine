import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Env var validation ---
REQUIRED_ENV_VARS = ["GROQ_API_KEY", "LLM_MODEL", "MONGODB_URL"]
OPTIONAL_ENV_VARS = ["POSTGRES_URL", "Google_Maps_API_Key", "ORS_API_KEY", "TAVILY_API_KEY",
                     "LANGCHAIN_API_KEY", "CORS_ORIGINS", "CLERK_JWKS_URL"]

missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

for v in OPTIONAL_ENV_VARS:
    if not os.environ.get(v):
        logging.warning(f"Optional environment variable {v} is not set")

# --- Structured logging ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


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

app = FastAPI(title="LocaleLive API", version="1.0.0")
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
        "version": "1.0.0",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "swagger_url": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
