import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.clerk import get_current_user, UserContext
from db.engine import get_db
from db.models import QueryEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/usage")
async def usage_stats(
    days: int = Query(default=7, ge=1, le=90),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total = db.query(func.count(QueryEvent.id)).filter(QueryEvent.created_at >= since).scalar() or 0
    authenticated = db.query(func.count(QueryEvent.id)).filter(
        QueryEvent.created_at >= since, QueryEvent.is_authenticated == True
    ).scalar() or 0
    anonymous = total - authenticated

    unique_users = db.query(func.count(func.distinct(QueryEvent.user_id))).filter(
        QueryEvent.created_at >= since, QueryEvent.is_authenticated == True
    ).scalar() or 0
    unique_anon_threads = db.query(func.count(func.distinct(QueryEvent.thread_id))).filter(
        QueryEvent.created_at >= since, QueryEvent.is_authenticated == False
    ).scalar() or 0

    return {
        "total_queries": total,
        "authenticated_queries": authenticated,
        "anonymous_queries": anonymous,
        "unique_authenticated_users": unique_users,
        "unique_anonymous_threads": unique_anon_threads,
        "period_days": days,
    }
