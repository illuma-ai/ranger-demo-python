from __future__ import annotations

import time

import jwt
import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.main import app

client = TestClient(app)

_SECRET = "dev-secret-do-not-use-in-prod"


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset the in-memory store before every test for isolation."""
    notes_service._store.clear()
    notes_service._next_id = 1


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """Return Authorization headers containing a fresh valid JWT."""
    payload = {"sub": "test-user", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, _SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# POST /notes
# ---------------------------------------------------------------------------


def test_create_note_returns_201(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes", json={"title": "Hello", "content": "World"}, headers=auth_headers
    )
    assert response.status_code == 201


def test_create_note_returns_note_with_id(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes", json={"title": "Hello", "content": "World"}, headers=auth_headers
    )
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Hello"
    assert body["content"] == "World"
    assert body["tags"] == []


def test_create_note_stores_tags(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes",
        json={"title": "Tagged", "content": "Body", "tags": ["python", "fastapi"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["python", "fastapi"]


def test_create_note_increments_id(auth_headers: dict[str, str]) -> None:
    client.post("/notes", json={"title": "First", "content": "A"}, headers=auth_headers)
    response = client.post(
        "/notes", json={"title": "Second", "content": "B"}, headers=auth_headers
    )
    assert response.json()["id"] == 2


def test_create_note_rejects_empty_title(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes", json={"title": "", "content": "Some content"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_create_note_rejects_empty_content(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes", json={"title": "Title", "content": ""}, headers=auth_headers
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /notes
# ---------------------------------------------------------------------------


def test_list_notes_empty() -> None:
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_all_notes(auth_headers: dict[str, str]) -> None:
    client.post("/notes", json={"title": "First", "content": "A"}, headers=auth_headers)
    client.post("/notes", json={"title": "Second", "content": "B"}, headers=auth_headers)
    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "First"
    assert notes[1]["title"] == "Second"


def test_list_notes_filter_by_tag_returns_matches(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Python note", "content": "A", "tags": ["python"]},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "General note", "content": "B", "tags": ["general"]},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Both", "content": "C", "tags": ["python", "general"]},
        headers=auth_headers,
    )

    response = client.get("/notes?tag=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert {n["title"] for n in notes} == {"Python note", "Both"}


def test_list_notes_filter_by_tag_returns_empty_when_no_match(
    auth_headers: dict[str, str],
) -> None:
    client.post(
        "/notes",
        json={"title": "Note", "content": "A", "tags": ["python"]},
        headers=auth_headers,
    )
    response = client.get("/notes?tag=nonexistent")
    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_no_filter_returns_all_tagged_notes(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Tagged", "content": "A", "tags": ["x"]},
        headers=auth_headers,
    )
    client.post("/notes", json={"title": "Untagged", "content": "B"}, headers=auth_headers)
    response = client.get("/notes")
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# PATCH /notes/{id}/archive
# ---------------------------------------------------------------------------


def test_archive_note_returns_200_with_archived_flag(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes", json={"title": "To archive", "content": "Body"}, headers=auth_headers
    )
    response = client.patch("/notes/1/archive", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["archived"] is True


def test_archive_note_404_for_missing_id(auth_headers: dict[str, str]) -> None:
    response = client.patch("/notes/999/archive", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_archive_note_hides_note_from_default_list(auth_headers: dict[str, str]) -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"}, headers=auth_headers)
    client.post("/notes", json={"title": "Hidden", "content": "B"}, headers=auth_headers)
    client.patch("/notes/2/archive", headers=auth_headers)

    response = client.get("/notes")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Visible"


def test_list_notes_include_archived_shows_all(auth_headers: dict[str, str]) -> None:
    client.post("/notes", json={"title": "Visible", "content": "A"}, headers=auth_headers)
    client.post("/notes", json={"title": "Hidden", "content": "B"}, headers=auth_headers)
    client.patch("/notes/2/archive", headers=auth_headers)

    response = client.get("/notes?include_archived=true")
    assert len(response.json()) == 2


def test_list_notes_archived_flag_false_by_default(auth_headers: dict[str, str]) -> None:
    """Archived notes must not appear when include_archived is omitted."""
    client.post("/notes", json={"title": "Note", "content": "A"}, headers=auth_headers)
    client.patch("/notes/1/archive", headers=auth_headers)

    response = client.get("/notes")
    assert response.json() == []


def test_list_notes_tag_filter_excludes_archived_by_default(
    auth_headers: dict[str, str],
) -> None:
    client.post(
        "/notes",
        json={"title": "Active", "content": "A", "tags": ["python"]},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Archived", "content": "B", "tags": ["python"]},
        headers=auth_headers,
    )
    client.patch("/notes/2/archive", headers=auth_headers)

    response = client.get("/notes?tag=python")
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Active"


def test_new_note_archived_flag_is_false(auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/notes", json={"title": "Fresh", "content": "New"}, headers=auth_headers
    )
    assert response.json()["archived"] is False


# ---------------------------------------------------------------------------
# GET /notes/search
# ---------------------------------------------------------------------------


def test_search_notes_matches_title(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Python tips", "content": "Some content"},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Unrelated", "content": "Other stuff"},
        headers=auth_headers,
    )
    response = client.get("/notes/search?q=python")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Python tips"


def test_search_notes_matches_content(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Random title", "content": "FastAPI is great"},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Another note", "content": "Nothing relevant"},
        headers=auth_headers,
    )
    response = client.get("/notes/search?q=fastapi")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Random title"


def test_search_notes_is_case_insensitive(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Hello World", "content": "Body text"},
        headers=auth_headers,
    )
    for q in ("hello", "HELLO", "Hello", "hElLo"):
        response = client.get(f"/notes/search?q={q}")
        assert response.status_code == 200, f"failed for q={q!r}"
        assert len(response.json()) == 1, f"expected 1 result for q={q!r}"


def test_search_notes_returns_newest_first(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "First match", "content": "keyword here"},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Second match", "content": "keyword here"},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Third match", "content": "keyword here"},
        headers=auth_headers,
    )
    response = client.get("/notes/search?q=keyword")
    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert ids == sorted(ids, reverse=True)


def test_search_notes_empty_when_no_match(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes", json={"title": "Note", "content": "Content"}, headers=auth_headers
    )
    response = client.get("/notes/search?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_search_notes_excludes_archived(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes",
        json={"title": "Active note", "content": "keyword"},
        headers=auth_headers,
    )
    client.post(
        "/notes",
        json={"title": "Archived note", "content": "keyword"},
        headers=auth_headers,
    )
    client.patch("/notes/2/archive", headers=auth_headers)
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


def test_get_note_returns_correct_note(auth_headers: dict[str, str]) -> None:
    client.post(
        "/notes", json={"title": "My note", "content": "Details"}, headers=auth_headers
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
