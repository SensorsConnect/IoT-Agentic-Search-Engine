import os
import time
import logging
from dataclasses import dataclass
from typing import Optional

import jwt
import requests
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from db.engine import get_db
from db.models import User

logger = logging.getLogger(__name__)

CLERK_JWKS_URL = os.environ.get("CLERK_JWKS_URL", "")


@dataclass
class UserContext:
    user_id: str  # UUID as string
    clerk_id: str
    email: Optional[str]
    role: str


class ClerkJWTVerifier:
    def __init__(self):
        self._jwks: Optional[dict] = None
        self._jwks_fetched_at: float = 0
        self._cache_ttl: float = 3600  # 1 hour

    def _fetch_jwks(self) -> dict:
        now = time.time()
        if self._jwks and (now - self._jwks_fetched_at) < self._cache_ttl:
            return self._jwks

        if not CLERK_JWKS_URL:
            raise RuntimeError("CLERK_JWKS_URL is not configured")

        resp = requests.get(CLERK_JWKS_URL, timeout=10)
        resp.raise_for_status()
        self._jwks = resp.json()
        self._jwks_fetched_at = now
        return self._jwks

    def verify_token(self, token: str) -> dict:
        jwks = self._fetch_jwks()
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token header")

        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token missing kid")

        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not rsa_key:
            # Refresh JWKS in case keys rotated
            self._jwks = None
            jwks = self._fetch_jwks()
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find matching key")

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

        return payload


_verifier = ClerkJWTVerifier()


def _extract_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return auth_header[7:]


def _upsert_user(db: Session, clerk_id: str, email: Optional[str], name: Optional[str], avatar_url: Optional[str] = None) -> User:
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if user:
        if email and user.email != email:
            user.email = email
        if name and user.name != name:
            user.name = name
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
    else:
        user = User(clerk_id=clerk_id, email=email, name=name, avatar_url=avatar_url)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserContext:
    token = _extract_token(request)
    payload = _verifier.verify_token(token)

    clerk_id = payload.get("sub", "")
    email = payload.get("email") or payload.get("email_address")
    name = payload.get("name") or payload.get("first_name")
    avatar_url = payload.get("image_url") or payload.get("profile_image_url")

    user = _upsert_user(db, clerk_id, email, name, avatar_url)

    return UserContext(
        user_id=str(user.id),
        clerk_id=clerk_id,
        email=user.email,
        role=user.role,
    )


async def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[UserContext]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None
