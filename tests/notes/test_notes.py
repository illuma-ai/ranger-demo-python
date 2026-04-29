from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.notes.service as notes_service
from app.main import app

client = TestClient(app)


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


def test_get_note_404_for_missing_id() -> None:
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
