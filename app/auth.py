from __future__ import annotations

import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_JWT_SECRET_DEFAULT = "dev-secret-do-not-use-in-prod"
_ALGORITHM = "HS256"

_bearer_scheme = HTTPBearer(auto_error=False)

# Module-level singleton so ruff B008 (no function call in default) is satisfied.
_bearer_dep = Depends(_bearer_scheme)


def _secret() -> str:
    return os.environ.get("JWT_SECRET", _JWT_SECRET_DEFAULT)


def verify_token(token: str) -> dict | None:
    """Decode and verify a JWT.

    Returns the decoded payload dict on success, or ``None`` if the token is
    invalid (bad signature, malformed, expired, etc.).
    """
    try:
        return jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = _bearer_dep,
) -> dict:
    """FastAPI dependency that enforces a valid Bearer JWT.

    Raises ``HTTPException(401)`` with a ``WWW-Authenticate: Bearer`` header
    when the ``Authorization`` header is missing, uses the wrong scheme, or
    carries an invalid/expired token.

    Returns the decoded JWT payload so callers can access claims if needed.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
