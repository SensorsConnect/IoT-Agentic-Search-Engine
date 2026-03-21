import logging
import time
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
    logger.info(f"Query received: user={user_label}, text='{query.text[:100]}', threadId='{query.threadId}'")

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
        if query.location:
            message_content += f"\n\n[User Location: {query.location.latitude}, {query.location.longitude}]"

        human_message = HumanMessage(content=message_content)
        messages = [human_message]

        result = None
        last_exc = None
        for attempt in range(3):
            try:
                result = runnable.invoke({"messages": messages, "query": message_content}, thread)
                break
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

        return {"answer": response_text, "conversationId": str(conversation.id), "places": places_data, "userLocation": user_location}

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
