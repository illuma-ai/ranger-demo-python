from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.auth import _ALGORITHM, _JWT_SECRET_DEFAULT
from app.main import app

# A single valid token used across all write calls in this test module.
_VALID_TOKEN = jwt.encode({"sub": "test-user"}, _JWT_SECRET_DEFAULT, algorithm=_ALGORITHM)

# Use a client with the auth header pre-set so all write calls are authenticated
# without touching every individual call site.  GET endpoints ignore the extra
# header, so read tests are unaffected.
client = TestClient(app, headers={"Authorization": f"Bearer {_VALID_TOKEN}"})


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset the in-memory store before every test for isolation."""
    notes_service._store.clear()
    notes_service._next_id = 1


# ---------------------------------------------------------------------------
# POST /notes
# ---------------------------------------------------------------------------


def test_create_note_returns_201() -> None:
    response = client.post("/notes", json={"title": "Hello", "content": "World"})
    assert response.status_code == 201


def test_create_note_returns_note_with_id() -> None:
    response = client.post("/notes", json={"title": "Hello", "content": "World"})
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Hello"
    assert body["content"] == "World"
    assert body["tags"] == []


def test_create_note_stores_tags() -> None:
    response = client.post(
        "/notes",
        json={"title": "Tagged", "content": "Body", "tags": ["python", "fastapi"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["python", "fastapi"]


def test_create_note_increments_id() -> None:
    client.post("/notes", json={"title": "First", "content": "A"})
    response = client.post("/notes", json={"title": "Second", "content": "B"})
    assert response.json()["id"] == 2


def test_create_note_rejects_empty_title() -> None:
    response = client.post("/notes", json={"title": "", "content": "Some content"})
    assert response.status_code == 422


def test_create_note_rejects_empty_content() -> None:
    response = client.post("/notes", json={"title": "Title", "content": ""})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /notes
# ---------------------------------------------------------------------------


def test_list_notes_empty() -> None:
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_all_notes() -> None:
    client.post("/notes", json={"title": "First", "content": "A"})
    client.post("/notes", json={"title": "Second", "content": "B"})
    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "First"
    assert notes[1]["title"] == "Second"


def test_list_notes_filter_by_tag_returns_matches() -> None:
    client.post("/notes", json={"title": "Python note", "content": "A", "tags": ["python"]})
    client.post("/notes", json={"title": "General note", "content": "B", "tags": ["general"]})
    client.post("/notes", json={"title": "Both", "content": "C", "tags": ["python", "general"]})

    response = client.get("/notes?tag=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert {n["title"] for n in notes} == {"Python note", "Both"}


def test_list_notes_filter_by_tag_returns_empty_when_no_match() -> None:
    client.post("/notes", json={"title": "Note", "content": "A", "tags": ["python"]})
    response = client.get("/notes?tag=nonexistent")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_no_filter_returns_all_tagged_notes() -> None:
    client.post("/notes", json={"title": "Tagged", "content": "A", "tags": ["x"]})
    client.post("/notes", json={"title": "Untagged", "content": "B"})
    response = client.get("/notes")
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# PATCH /notes/{id}/archive
# ---------------------------------------------------------------------------


def test_archive_note_returns_200_with_archived_flag() -> None:
    client.post("/notes", json={"title": "To archive", "content": "Body"})
    response = client.patch("/notes/1/archive")
    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archive_note_404_for_missing_id() -> None:
    response = client.patch("/notes/999/archive")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_archive_note_hides_note_from_default_list() -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"})
    client.post("/notes", json={"title": "Hidden", "content": "B"})
    client.patch("/notes/2/archive")

    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Visible"


def test_list_notes_include_archived_shows_all() -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"})
    client.post("/notes", json={"title": "Hidden", "content": "B"})
    client.patch("/notes/2/archive")

    response = client.get("/notes?include_archived=true")
    assert len(response.json()) == 2


def test_list_notes_archived_flag_false_by_default() -> None:
    """Archived notes must not appear when include_archived is omitted."""
    client.post("/notes", json={"title": "Note", "content": "A"})
    client.patch("/notes/1/archive")

    response = client.get("/notes")
    assert response.json() == []


def test_list_notes_tag_filter_excludes_archived_by_default() -> None:
    client.post("/notes", json={"title": "Active", "content": "A", "tags": ["python"]})
    client.post("/notes", json={"title": "Archived", "content": "B", "tags": ["python"]})
    client.patch("/notes/2/archive")

    response = client.get("/notes?tag=python")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Active"


def test_new_note_archived_flag_is_false() -> None:
    response = client.post("/notes", json={"title": "Fresh", "content": "New"})
    assert response.json()["archived"] is False


# ---------------------------------------------------------------------------
# GET /notes/search
# ---------------------------------------------------------------------------


def test_search_notes_matches_title() -> None:
    client.post("/notes", json={"title": "Python tips", "content": "Some content"})
    client.post("/notes", json={"title": "Unrelated", "content": "Other stuff"})
    response = client.get("/notes/search?q=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Python tips"


def test_search_notes_matches_content() -> None:
    client.post("/notes", json={"title": "Random title", "content": "FastAPI is great"})
    client.post("/notes", json={"title": "Another note", "content": "Nothing relevant"})
    response = client.get("/notes/search?q=fastapi")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Random title"


def test_search_notes_is_case_insensitive() -> None:
    client.post("/notes", json={"title": "Hello World", "content": "Body text"})
    for q in ("hello", "HELLO", "Hello", "hElLo"):
        response = client.get(f"/notes/search?q={q}")
        assert response.status_code == 200, f"failed for q={q!r}"
        assert len(response.json()) == 1, f"expected 1 result for q={q!r}"


def test_search_notes_returns_newest_first() -> None:
    client.post("/notes", json={"title": "First match", "content": "keyword here"})
    client.post("/notes", json={"title": "Second match", "content": "keyword here"})
    client.post("/notes", json={"title": "Third match", "content": "keyword here"})
    response = client.get("/notes/search?q=keyword")
    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert ids == sorted(ids, reverse=True)


def test_search_notes_empty_when_no_match() -> None:
    client.post("/notes", json={"title": "Note", "content": "Content"})
    response = client.get("/notes/search?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_search_notes_excludes_archived() -> None:
    client.post("/notes", json={"title": "Active note", "content": "keyword"})
    client.post("/notes", json={"title": "Archived note", "content": "keyword"})
    client.patch("/notes/2/archive")
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
    client.post("/notes", json={"title": "My note", "content": "Details"})
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
