from fastapi import APIRouter

from api.v1.query import router as query_router
from api.v1.conversations import router as conversations_router
from api.v1.saved_places import router as saved_places_router
from api.v1.users import router as users_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(query_router)
v1_router.include_router(conversations_router)
v1_router.include_router(saved_places_router)
v1_router.include_router(users_router)
