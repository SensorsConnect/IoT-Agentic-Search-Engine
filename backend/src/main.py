import os
import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Env var validation ---
REQUIRED_ENV_VARS = ["GROQ_API_KEY", "LLM_MODEL", "MONGODB_URL"]
OPTIONAL_ENV_VARS = ["POSTGRES_URL", "Google_Maps_API_Key", "ORS_API_KEY", "TAVILY_API_KEY",
                     "LANGCHAIN_API_KEY", "CORS_ORIGINS"]

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

# Import graph after env validation
from graph import runnable

# --- Rate limiting ---
limiter = Limiter(key_func=get_remote_address)

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


class LocationData(BaseModel):
    latitude: float
    longitude: float

class Query(BaseModel):
    text: str
    threadId: str
    location: Optional[LocationData] = None


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


@app.put("/query")
@limiter.limit("30/minute")
def query_handler(query: Query, request: Request):
    logger.info(f"Query received: text='{query.text[:100]}', threadId='{query.threadId}', has_location={query.location is not None}")

    try:
        thread = {"configurable": {"thread_id": query.threadId}}

        message_content = query.text
        if query.location:
            message_content += f"\n\n[User Location: {query.location.latitude}, {query.location.longitude}]"

        human_message = HumanMessage(content=message_content)
        messages = [human_message]

        result = runnable.invoke({"messages": messages}, thread)

        response_text = result.get("response", [""])[-1] if result.get("response") else ""
        if not response_text:
            logger.warning(f"Empty response for query: {query.text[:100]}")
            return JSONResponse(
                status_code=200,
                content={"answer": "I'm sorry, I couldn't process your request. Please try again."}
            )

        return {"answer": response_text}

    except ValueError as e:
        logger.error(f"Validation error processing query: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request", "detail": str(e)}
        )
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": "An unexpected error occurred. Please try again."}
        )
