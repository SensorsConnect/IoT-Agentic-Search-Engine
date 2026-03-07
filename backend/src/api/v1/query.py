import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from auth.clerk import get_current_user, UserContext
from db.engine import get_db
from db.models import Conversation, Message
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


@router.put("/query")
async def query_handler(
    query: QueryRequest,
    request: Request,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Query received: user={user.clerk_id}, text='{query.text[:100]}', threadId='{query.threadId}'")

    try:
        thread = {"configurable": {"thread_id": query.threadId}}

        message_content = query.text
        if query.location:
            message_content += f"\n\n[User Location: {query.location.latitude}, {query.location.longitude}]"

        human_message = HumanMessage(content=message_content)
        messages = [human_message]

        result = runnable.invoke({"messages": messages, "query": message_content}, thread)

        response_text = result.get("response", "")
        if not response_text:
            logger.warning(f"Empty response for query: {query.text[:100]}")
            return JSONResponse(
                status_code=200,
                content={"answer": "I'm sorry, I couldn't process your request. Please try again.", "conversationId": ""}
            )

        # Upsert conversation
        conversation = db.query(Conversation).filter(Conversation.thread_id == query.threadId).first()
        if not conversation:
            title = query.text[:50].strip()
            if len(query.text) > 50:
                title += "..."
            conversation = Conversation(
                user_id=user.user_id,
                thread_id=query.threadId,
                title=title,
            )
            db.add(conversation)
            db.flush()

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=query.text,
        )
        db.add(user_msg)

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
        )
        db.add(assistant_msg)
        db.commit()

        return {"answer": response_text, "conversationId": str(conversation.id)}

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
