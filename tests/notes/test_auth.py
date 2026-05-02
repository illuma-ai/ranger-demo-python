"""Auth tests for notes write endpoints (POST /notes, PATCH /notes/{id}/archive)."""

from __future__ import annotations

import time

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.auth import _ALGORITHM, _DEFAULT_SECRET
from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_token(secret: str = _DEFAULT_SECRET, exp_offset: int = 3600) -> str:
    """Return a signed HS256 JWT.  exp_offset < 0 produces an expired token."""
    payload: dict = {"sub": "test-user", "exp": int(time.time()) + exp_offset}
    return jwt.encode(payload, secret, algorithm=_ALGORITHM)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_store() -> None:
    notes_service._store.clear()
    notes_service._next_id = 1


# ---------------------------------------------------------------------------
# POST /notes — auth scenarios
# ---------------------------------------------------------------------------


def test_create_note_valid_token_returns_201() -> None:
    """Valid HS256 token → write succeeds."""
    response = client.post(
        "/notes",
        json={"title": "Auth note", "content": "Body"},
        headers=_auth(_make_token()),
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Auth note"


def test_create_note_missing_auth_header_returns_401() -> None:
    """No Authorization header → 401."""
    response = client.post("/notes", json={"title": "Title", "content": "Body"})
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_create_note_malformed_token_returns_401() -> None:
    """'Bearer not-a-jwt' → 401."""
    response = client.post(
        "/notes",
        json={"title": "Title", "content": "Body"},
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_create_note_wrong_scheme_returns_401() -> None:
    """Non-Bearer scheme (e.g. Basic) → 401."""
    response = client.post(
        "/notes",
        json={"title": "Title", "content": "Body"},
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_create_note_expired_token_returns_401() -> None:
    """JWT with exp in the past → 401."""
    expired = _make_token(exp_offset=-1)
    response = client.post(
        "/notes",
        json={"title": "Title", "content": "Body"},
        headers=_auth(expired),
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


# ---------------------------------------------------------------------------
# PATCH /notes/{id}/archive — auth scenarios
# ---------------------------------------------------------------------------


def _create_note_authed() -> int:
    """Helper: create a note with a valid token; return its id."""
    r = client.post(
        "/notes",
        json={"title": "Note", "content": "Body"},
        headers=_auth(_make_token()),
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_archive_note_valid_token_returns_200() -> None:
    note_id = _create_note_authed()
    response = client.patch(f"/notes/{note_id}/archive", headers=_auth(_make_token()))
    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archive_note_missing_auth_header_returns_401() -> None:
    note_id = _create_note_authed()
    response = client.patch(f"/notes/{note_id}/archive")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_archive_note_malformed_token_returns_401() -> None:
    note_id = _create_note_authed()
    response = client.patch(
        f"/notes/{note_id}/archive",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401


def test_archive_note_expired_token_returns_401() -> None:
    note_id = _create_note_authed()
    response = client.patch(
        f"/notes/{note_id}/archive",
        headers=_auth(_make_token(exp_offset=-1)),
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET endpoints remain public (no auth required)
# ---------------------------------------------------------------------------


def test_list_notes_is_public() -> None:
    response = client.get("/notes")
    assert response.status_code == 200


def test_search_notes_is_public() -> None:
    response = client.get("/notes/search?q=anything")
    assert response.status_code == 200


def test_get_note_is_public() -> None:
    """GET /notes/{id} returns 404 (not 401) when id is absent → endpoint is public."""
    response = client.get("/notes/999")
    assert response.status_code == 404
