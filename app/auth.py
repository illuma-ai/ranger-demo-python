from __future__ import annotations

import os
from typing import Annotated

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer_scheme = HTTPBearer(auto_error=False)

_DEFAULT_SECRET = "dev-secret-do-not-use-in-prod"


def _get_secret() -> str:
    return os.environ.get("JWT_SECRET", _DEFAULT_SECRET)


def verify_token(token: str) -> dict | None:
    """Decode an HS256 JWT and return its payload, or None on any failure."""
    try:
        return jwt.decode(token, _get_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer_scheme)],
) -> dict:
    """FastAPI dependency — enforces a valid Bearer JWT.

    Raises HTTP 401 when the Authorization header is absent, malformed,
    or contains an invalid / expired token.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
