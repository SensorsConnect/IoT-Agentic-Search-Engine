import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.clerk import get_current_user, get_optional_user, UserContext
from db.engine import get_db
from db.models import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationOut(BaseModel):
    id: str
    title: Optional[str]
    thread_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: str

    class Config:
        from_attributes = True


class ConversationDetailOut(BaseModel):
    id: str
    title: Optional[str]
    thread_id: str
    messages: list[MessageOut]
    created_at: str
    updated_at: str


class RenameRequest(BaseModel):
    title: str


def _get_user_conversation(db: Session, conversation_id: str, user_id: str) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return conv


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not user:
        return []
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        ConversationOut(
            id=str(c.id),
            title=c.title,
            thread_id=c.thread_id,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in convs
    ]


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
async def get_conversation(
    conversation_id: str,
    user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="Sign in to view conversation history")
    conv = _get_user_conversation(db, conversation_id, user.user_id)
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return ConversationDetailOut(
        id=str(conv.id),
        title=conv.title,
        thread_id=conv.thread_id,
        messages=[
            MessageOut(
                id=str(m.id),
                role=m.role,
                content=m.content,
                metadata=m.metadata_ if m.metadata_ else None,
                created_at=m.created_at.isoformat(),
            )
            for m in msgs
        ],
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
    )


@router.patch("/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    body: RenameRequest,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_user_conversation(db, conversation_id, user.user_id)
    conv.title = body.title
    db.commit()
    return {"id": str(conv.id), "title": conv.title}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_user_conversation(db, conversation_id, user.user_id)
    db.delete(conv)
    db.commit()
    return {"deleted": True}
