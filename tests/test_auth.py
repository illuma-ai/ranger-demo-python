"""Tests for JWT auth on notes write endpoints."""

from __future__ import annotations

import time

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.main import app

client = TestClient(app)

_SECRET = "dev-secret-do-not-use-in-prod"


def _make_token(*, expires_in: int = 3600, secret: str = _SECRET) -> str:
    """Mint a minimal valid HS256 token."""
    payload = {"sub": "test-user", "exp": int(time.time()) + expires_in}
    return jwt.encode(payload, secret, algorithm="HS256")


def _expired_token() -> str:
    """Mint a token that expired one second in the past."""
    payload = {"sub": "test-user", "exp": int(time.time()) - 1}
    return jwt.encode(payload, _SECRET, algorithm="HS256")


@pytest.fixture(autouse=True)
def reset_store() -> None:
    notes_service._store.clear()
    notes_service._next_id = 1


# ---------------------------------------------------------------------------
# POST /notes — auth coverage
# ---------------------------------------------------------------------------


def test_create_note_with_valid_token_returns_201() -> None:
    token = _make_token()
    response = client.post(
        "/notes",
        json={"title": "Auth note", "content": "Body"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_create_note_missing_auth_header_returns_401() -> None:
    response = client.post("/notes", json={"title": "No auth", "content": "Body"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_create_note_malformed_token_returns_401() -> None:
    response = client.post(
        "/notes",
        json={"title": "Bad token", "content": "Body"},
        headers={"Authorization": "Bearer garbage.token.here"},
    )
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_create_note_wrong_scheme_returns_401() -> None:
    """A non-Bearer scheme (e.g. 'Token ...') must be rejected with 401."""
    token = _make_token()
    response = client.post(
        "/notes",
        json={"title": "Wrong scheme", "content": "Body"},
        headers={"Authorization": f"Token {token}"},
    )
    assert response.status_code == 401


def test_create_note_expired_token_returns_401() -> None:
    token = _expired_token()
    response = client.post(
        "/notes",
        json={"title": "Expired", "content": "Body"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_create_note_wrong_secret_returns_401() -> None:
    token = _make_token(secret="wrong-secret")
    response = client.post(
        "/notes",
        json={"title": "Wrong secret", "content": "Body"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PATCH /notes/{id}/archive — auth coverage
# ---------------------------------------------------------------------------


def test_archive_note_with_valid_token_returns_200() -> None:
    token = _make_token()
    client.post(
        "/notes",
        json={"title": "To archive", "content": "Body"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.patch(
        "/notes/1/archive",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archive_note_missing_auth_returns_401() -> None:
    response = client.patch("/notes/1/archive")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_archive_note_expired_token_returns_401() -> None:
    token = _expired_token()
    response = client.patch(
        "/notes/1/archive",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET endpoints — must remain public (no token required)
# ---------------------------------------------------------------------------


def test_list_notes_is_public() -> None:
    response = client.get("/notes")
    assert response.status_code == 200


def test_get_note_is_public() -> None:
    # 404 is fine — it proves auth isn't blocking us
    response = client.get("/notes/999")
    assert response.status_code == 404


def test_search_notes_is_public() -> None:
    response = client.get("/notes/search?q=anything")
    assert response.status_code == 200
