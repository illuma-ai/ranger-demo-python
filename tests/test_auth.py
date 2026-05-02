from __future__ import annotations

import time

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.auth import _ALGORITHM, _JWT_SECRET_DEFAULT, verify_token
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset the in-memory store before every test for isolation."""
    notes_service._store.clear()
    notes_service._next_id = 1


# ---------------------------------------------------------------------------
# Unit tests for verify_token
# ---------------------------------------------------------------------------


def test_verify_token_returns_payload_for_valid_token() -> None:
    token = jwt.encode({"sub": "alice"}, _JWT_SECRET_DEFAULT, algorithm=_ALGORITHM)
    result = verify_token(token)
    assert result is not None
    assert result["sub"] == "alice"


def test_verify_token_returns_none_for_bad_signature() -> None:
    token = jwt.encode({"sub": "alice"}, "wrong-secret", algorithm=_ALGORITHM)
    assert verify_token(token) is None


def test_verify_token_returns_none_for_malformed_token() -> None:
    assert verify_token("not.a.jwt") is None


def test_verify_token_returns_none_for_expired_token() -> None:
    token = jwt.encode(
        {"sub": "alice", "exp": int(time.time()) - 60},
        _JWT_SECRET_DEFAULT,
        algorithm=_ALGORITHM,
    )
    assert verify_token(token) is None


# ---------------------------------------------------------------------------
# Integration tests via POST /notes
# ---------------------------------------------------------------------------


def test_valid_token_allows_create_note() -> None:
    token = jwt.encode({"sub": "alice"}, _JWT_SECRET_DEFAULT, algorithm=_ALGORITHM)
    response = client.post(
        "/notes",
        json={"title": "Secure note", "content": "Body"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_missing_auth_header_returns_401() -> None:
    response = client.post(
        "/notes",
        json={"title": "No auth", "content": "Body"},
        # deliberately omit Authorization header
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing token"
    assert response.headers.get("www-authenticate") == "Bearer"


def test_malformed_token_returns_401() -> None:
    response = client.post(
        "/notes",
        json={"title": "Bad token", "content": "Body"},
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing token"


def test_expired_token_returns_401() -> None:
    expired_token = jwt.encode(
        {"sub": "alice", "exp": int(time.time()) - 60},
        _JWT_SECRET_DEFAULT,
        algorithm=_ALGORITHM,
    )
    response = client.post(
        "/notes",
        json={"title": "Expired", "content": "Body"},
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing token"
