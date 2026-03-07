import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.clerk import get_current_user, UserContext
from db.engine import get_db
from db.models import SavedPlace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/saved-places", tags=["saved-places"])


class SavePlaceRequest(BaseModel):
    place_name: str
    place_data: Optional[dict] = None
    note: Optional[str] = None


class SavedPlaceOut(BaseModel):
    id: str
    place_name: str
    place_data: Optional[dict]
    note: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[SavedPlaceOut])
async def list_saved_places(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    places = (
        db.query(SavedPlace)
        .filter(SavedPlace.user_id == user.user_id)
        .order_by(SavedPlace.created_at.desc())
        .all()
    )
    return [
        SavedPlaceOut(
            id=str(p.id),
            place_name=p.place_name,
            place_data=p.place_data,
            note=p.note,
            created_at=p.created_at.isoformat(),
        )
        for p in places
    ]


@router.post("", response_model=SavedPlaceOut, status_code=201)
async def save_place(
    body: SavePlaceRequest,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(SavedPlace)
        .filter(SavedPlace.user_id == user.user_id, SavedPlace.place_name == body.place_name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Place already saved")

    place = SavedPlace(
        user_id=user.user_id,
        place_name=body.place_name,
        place_data=body.place_data,
        note=body.note,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return SavedPlaceOut(
        id=str(place.id),
        place_name=place.place_name,
        place_data=place.place_data,
        note=place.note,
        created_at=place.created_at.isoformat(),
    )


@router.delete("/{place_id}")
async def delete_saved_place(
    place_id: str,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    place = db.query(SavedPlace).filter(SavedPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Saved place not found")
    if str(place.user_id) != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(place)
    db.commit()
    return {"deleted": True}
