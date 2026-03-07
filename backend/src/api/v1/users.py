import logging
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.clerk import get_current_user, UserContext
from db.engine import get_db
from db.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])


class UserProfileOut(BaseModel):
    id: str
    email: Optional[str]
    name: Optional[str]
    avatar_url: Optional[str]
    role: str
    city: Optional[str]
    created_at: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None


@router.get("/me", response_model=UserProfileOut)
async def get_profile(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user.user_id).first()
    return UserProfileOut(
        id=str(db_user.id),
        email=db_user.email,
        name=db_user.name,
        avatar_url=db_user.avatar_url,
        role=db_user.role,
        city=db_user.city,
        created_at=db_user.created_at.isoformat(),
    )


@router.patch("/me", response_model=UserProfileOut)
async def update_profile(
    body: UpdateProfileRequest,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user.user_id).first()
    if body.name is not None:
        db_user.name = body.name
    if body.city is not None:
        db_user.city = body.city
    db.commit()
    db.refresh(db_user)
    return UserProfileOut(
        id=str(db_user.id),
        email=db_user.email,
        name=db_user.name,
        avatar_url=db_user.avatar_url,
        role=db_user.role,
        city=db_user.city,
        created_at=db_user.created_at.isoformat(),
    )
