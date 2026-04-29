from __future__ import annotations

from app.notes.schemas import NoteCreate, NoteResponse

# In-memory store: maps note ID -> NoteResponse.
# Replaced with a database in a future iteration.
_store: dict[int, NoteResponse] = {}
_next_id: int = 1


def create_note(payload: NoteCreate) -> NoteResponse:
    global _next_id
    note = NoteResponse(
        id=_next_id,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
    )
    _store[_next_id] = note
    _next_id += 1
    return note


def list_notes(tag: str | None = None) -> list[NoteResponse]:
    notes = list(_store.values())
    if tag is not None:
        notes = [n for n in notes if tag in n.tags]
    return notes


def get_note(note_id: int) -> NoteResponse | None:
    return _store.get(note_id)
