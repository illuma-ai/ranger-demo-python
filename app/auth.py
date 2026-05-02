from __future__ import annotations

import os

import jwt
from fastapi import Header, HTTPException

_DEFAULT_SECRET = "dev-secret-do-not-use-in-prod"
_ALGORITHM = "HS256"


def _secret() -> str:
    return os.environ.get("JWT_SECRET", _DEFAULT_SECRET)


def verify_token(token: str) -> dict | None:
    """Decode and verify a JWT signed with HS256.

    Returns the decoded payload dict on success, or None when the token is
    invalid, expired, or cannot be decoded.
    """
    try:
        return jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, jwt.DecodeError):
        return None


async def require_auth(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    """FastAPI dependency that enforces a valid Bearer JWT.

    Raises HTTP 401 when:
    - The Authorization header is absent.
    - The scheme is not "Bearer".
    - The token is invalid, expired, or malformed.
    """
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format; expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(parts[1])
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
