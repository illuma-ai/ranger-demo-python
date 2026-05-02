from __future__ import annotations

import time

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.auth import _ALGORITHM, _DEFAULT_SECRET
from app.main import app

client = TestClient(app)


def _valid_auth_headers() -> dict[str, str]:
    """Return an Authorization header with a fresh, valid HS256 token."""
    token = jwt.encode(
        {"sub": "test", "exp": int(time.time()) + 3600}, _DEFAULT_SECRET, algorithm=_ALGORITHM
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset the in-memory store before every test for isolation."""
    notes_service._store.clear()
    notes_service._next_id = 1


# ---------------------------------------------------------------------------
# POST /notes
# ---------------------------------------------------------------------------


def test_create_note_returns_201() -> None:
    response = client.post(
        "/notes", json={"title": "Hello", "content": "World"}, headers=_valid_auth_headers()
    )
    assert response.status_code == 201


def test_create_note_returns_note_with_id() -> None:
    response = client.post(
        "/notes", json={"title": "Hello", "content": "World"}, headers=_valid_auth_headers()
    )
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Hello"
    assert body["content"] == "World"
    assert body["tags"] == []


def test_create_note_stores_tags() -> None:
    response = client.post(
        "/notes",
        json={"title": "Tagged", "content": "Body", "tags": ["python", "fastapi"]},
        headers=_valid_auth_headers(),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["python", "fastapi"]


def test_create_note_increments_id() -> None:
    client.post("/notes", json={"title": "First", "content": "A"}, headers=_valid_auth_headers())
    response = client.post(
        "/notes", json={"title": "Second", "content": "B"}, headers=_valid_auth_headers()
    )
    assert response.json()["id"] == 2


def test_create_note_rejects_empty_title() -> None:
    response = client.post(
        "/notes", json={"title": "", "content": "Some content"}, headers=_valid_auth_headers()
    )
    assert response.status_code == 422


def test_create_note_rejects_empty_content() -> None:
    response = client.post(
        "/notes", json={"title": "Title", "content": ""}, headers=_valid_auth_headers()
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /notes
# ---------------------------------------------------------------------------


def test_list_notes_empty() -> None:
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_all_notes() -> None:
    client.post("/notes", json={"title": "First", "content": "A"}, headers=_valid_auth_headers())
    client.post("/notes", json={"title": "Second", "content": "B"}, headers=_valid_auth_headers())
    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "First"
    assert notes[1]["title"] == "Second"


def test_list_notes_filter_by_tag_returns_matches() -> None:
    client.post(
        "/notes",
        json={"title": "Python note", "content": "A", "tags": ["python"]},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "General note", "content": "B", "tags": ["general"]},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Both", "content": "C", "tags": ["python", "general"]},
        headers=_valid_auth_headers(),
    )

    response = client.get("/notes?tag=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert {n["title"] for n in notes} == {"Python note", "Both"}


def test_list_notes_filter_by_tag_returns_empty_when_no_match() -> None:
    client.post(
        "/notes",
        json={"title": "Note", "content": "A", "tags": ["python"]},
        headers=_valid_auth_headers(),
    )
    response = client.get("/notes?tag=nonexistent")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_no_filter_returns_all_tagged_notes() -> None:
    client.post(
        "/notes",
        json={"title": "Tagged", "content": "A", "tags": ["x"]},
        headers=_valid_auth_headers(),
    )
    client.post("/notes", json={"title": "Untagged", "content": "B"}, headers=_valid_auth_headers())
    response = client.get("/notes")
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# PATCH /notes/{id}/archive
# ---------------------------------------------------------------------------


def test_archive_note_returns_200_with_archived_flag() -> None:
    client.post(
        "/notes", json={"title": "To archive", "content": "Body"}, headers=_valid_auth_headers()
    )
    response = client.patch("/notes/1/archive", headers=_valid_auth_headers())
    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archive_note_404_for_missing_id() -> None:
    response = client.patch("/notes/999/archive", headers=_valid_auth_headers())
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_archive_note_hides_note_from_default_list() -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"}, headers=_valid_auth_headers())
    client.post("/notes", json={"title": "Hidden", "content": "B"}, headers=_valid_auth_headers())
    client.patch("/notes/2/archive", headers=_valid_auth_headers())

    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Visible"


def test_list_notes_include_archived_shows_all() -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"}, headers=_valid_auth_headers())
    client.post("/notes", json={"title": "Hidden", "content": "B"}, headers=_valid_auth_headers())
    client.patch("/notes/2/archive", headers=_valid_auth_headers())

    response = client.get("/notes?include_archived=true")
    assert len(response.json()) == 2


def test_list_notes_archived_flag_false_by_default() -> None:
    """Archived notes must not appear when include_archived is omitted."""
    client.post("/notes", json={"title": "Note", "content": "A"}, headers=_valid_auth_headers())
    client.patch("/notes/1/archive", headers=_valid_auth_headers())

    response = client.get("/notes")
    assert response.json() == []


def test_list_notes_tag_filter_excludes_archived_by_default() -> None:
    client.post(
        "/notes",
        json={"title": "Active", "content": "A", "tags": ["python"]},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Archived", "content": "B", "tags": ["python"]},
        headers=_valid_auth_headers(),
    )
    client.patch("/notes/2/archive", headers=_valid_auth_headers())

    response = client.get("/notes?tag=python")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Active"


def test_new_note_archived_flag_is_false() -> None:
    response = client.post(
        "/notes", json={"title": "Fresh", "content": "New"}, headers=_valid_auth_headers()
    )
    assert response.json()["archived"] is False


# ---------------------------------------------------------------------------
# GET /notes/search
# ---------------------------------------------------------------------------


def test_search_notes_matches_title() -> None:
    client.post(
        "/notes",
        json={"title": "Python tips", "content": "Some content"},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Unrelated", "content": "Other stuff"},
        headers=_valid_auth_headers(),
    )
    response = client.get("/notes/search?q=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Python tips"


def test_search_notes_matches_content() -> None:
    client.post(
        "/notes",
        json={"title": "Random title", "content": "FastAPI is great"},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Another note", "content": "Nothing relevant"},
        headers=_valid_auth_headers(),
    )
    response = client.get("/notes/search?q=fastapi")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Random title"


def test_search_notes_is_case_insensitive() -> None:
    client.post(
        "/notes",
        json={"title": "Hello World", "content": "Body text"},
        headers=_valid_auth_headers(),
    )
    for q in ("hello", "HELLO", "Hello", "hElLo"):
        response = client.get(f"/notes/search?q={q}")
        assert response.status_code == 200, f"failed for q={q!r}"
        assert len(response.json()) == 1, f"expected 1 result for q={q!r}"


def test_search_notes_returns_newest_first() -> None:
    client.post(
        "/notes",
        json={"title": "First match", "content": "keyword here"},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Second match", "content": "keyword here"},
        headers=_valid_auth_headers(),
    )
    client.post(
        "/notes",
        json={"title": "Third match", "content": "keyword here"},
        headers=_valid_auth_headers(),
    )
    response = client.get("/notes/search?q=keyword")
    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert ids == sorted(ids, reverse=True)


def test_search_notes_empty_when_no_match() -> None:
    client.post(
        "/notes", json={"title": "Note", "content": "Content"}, headers=_valid_auth_headers()
    )
    response = client.get("/notes/search?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_search_notes_excludes_archived() -> None:
    client.post(
        "/notes", json={"title": "Active note", "content": "keyword"}, headers=_valid_auth_headers()
    )
    client.post(
        "/notes",
        json={"title": "Archived note", "content": "keyword"},
        headers=_valid_auth_headers(),
    )
    client.patch("/notes/2/archive", headers=_valid_auth_headers())
    response = client.get("/notes/search?q=keyword")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Active note"


def test_search_notes_requires_q_param() -> None:
    response = client.get("/notes/search")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /notes/{id}
# ---------------------------------------------------------------------------


def test_get_note_returns_correct_note() -> None:
    client.post(
        "/notes", json={"title": "My note", "content": "Details"}, headers=_valid_auth_headers()
    )
    response = client.get("/notes/1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "My note"
    assert body["content"] == "Details"
    assert body["tags"] == []


def test_get_note_404_for_missing_id() -> None:
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
