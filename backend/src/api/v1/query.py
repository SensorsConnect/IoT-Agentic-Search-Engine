import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from auth.clerk import get_optional_user, UserContext
from db.engine import get_db
from db.models import Conversation, Message, QueryEvent
from graph import runnable

logger = logging.getLogger(__name__)

router = APIRouter()


def _sanitize_for_json(obj):
    """Recursively replace non-finite floats (inf, -inf, nan) with None."""
    if isinstance(obj, float):
        import math
        return None if not math.isfinite(obj) else obj
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    return obj


class LocationData(BaseModel):
    latitude: float
    longitude: float


class QueryRequest(BaseModel):
    text: str
    threadId: str
    location: Optional[LocationData] = None


class QueryResponse(BaseModel):
    answer: str
    conversationId: str
    places: list = []
    userLocation: Optional[dict] = None


@router.put("/query")
async def query_handler(
    query: QueryRequest,
    request: Request,
    user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user_label = user.clerk_id if user else "anonymous"
    correlation_id = str(uuid.uuid4())
    t0 = time.time()
    logger.info(f"query_start rid={correlation_id} user={user_label} text='{query.text[:80]}' threadId='{query.threadId}'")

    # Track every query for usage analytics
    event = QueryEvent(
        user_id=user.user_id if user else None,
        is_authenticated=user is not None,
        query_text=query.text[:200],
        thread_id=query.threadId,
    )
    db.add(event)
    db.commit()

    try:
        thread = {"configurable": {"thread_id": query.threadId}}

        message_content = query.text
        human_message = HumanMessage(content=message_content)
        messages = [human_message]

        user_location = {}
        if query.location:
            user_location = {
                "latitude": query.location.latitude,
                "longitude": query.location.longitude
            }

        GRAPH_TIMEOUT_SECONDS = 90

        result = None
        last_exc = None
        for attempt in range(3):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        runnable.invoke,
                        {"messages": messages, "query": message_content, "user_location": user_location, "correlation_id": correlation_id},
                        thread,
                    )
                    result = future.result(timeout=GRAPH_TIMEOUT_SECONDS)
                from langchain_core.messages import ToolMessage as _TM
                routing_path = [m.name for m in result.get("messages", []) if isinstance(m, _TM) and m.name]
                result_count = len(result.get("places") or [])
                logger.info(
                    f"query_complete rid={correlation_id} user={user_label} "
                    f"duration={time.time() - t0:.2f}s "
                    f"path={routing_path if routing_path else ['direct_answer']} "
                    f"results={result_count}"
                )
                break
            except FuturesTimeoutError:
                logger.error(f"Graph invocation timed out after {GRAPH_TIMEOUT_SECONDS}s for query: {query.text[:100]}")
                return JSONResponse(
                    status_code=504,
                    content={"error": "Request timed out", "detail": "The search took too long. Please try again."}
                )
            except Exception as exc:
                exc_str = str(exc).lower()
                is_conn_err = any(k in exc_str for k in (
                    "ssl connection has been closed",
                    "consuming input failed",
                    "connection is closed",
                    "server closed the connection",
                    "could not connect to server",
                ))
                if is_conn_err and attempt < 2:
                    wait = 1.5 ** attempt
                    logger.warning(f"DB connection error on attempt {attempt + 1}, retrying in {wait:.1f}s: {exc}")
                    time.sleep(wait)
                    last_exc = exc
                else:
                    raise
        if result is None:
            raise last_exc

        response_text = result.get("response", "")
        if not response_text:
            logger.warning(f"Empty response for query: {query.text[:100]}")
            return JSONResponse(
                status_code=200,
                content={"answer": "I'm sorry, I couldn't process your request. Please try again.", "conversationId": "", "places": [], "userLocation": None}
            )

        # Extract and deduplicate places
        raw_places = result.get("places", []) or []
        seen_ids = set()
        places_data = []
        for p in raw_places:
            pid = p.get("id", "")
            if pid and pid in seen_ids:
                continue
            if pid:
                seen_ids.add(pid)
            places_data.append(p)

        user_location = None
        if query.location:
            user_location = {"latitude": query.location.latitude, "longitude": query.location.longitude}

        # Persist conversation and messages for all users (anonymous and authenticated)
        conversation = db.query(Conversation).filter(Conversation.thread_id == query.threadId).first()
        if not conversation:
            title = query.text[:50].strip()
            if len(query.text) > 50:
                title += "..."
            conversation = Conversation(
                user_id=user.user_id if user else None,
                thread_id=query.threadId,
                title=title,
            )
            db.add(conversation)
            db.flush()

        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=query.text,
        )
        db.add(user_msg)

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            metadata_={"places": places_data, "userLocation": user_location} if places_data else None,
        )
        db.add(assistant_msg)
        db.commit()

        payload = _sanitize_for_json({
            "answer": response_text,
            "conversationId": str(conversation.id),
            "places": places_data,
            "userLocation": user_location
        })
        return payload

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
