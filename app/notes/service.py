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


def list_notes(
    tag: str | None = None,
    include_archived: bool = False,
) -> list[NoteResponse]:
    notes = list(_store.values())
    if not include_archived:
        notes = [n for n in notes if not n.archived]
    if tag is not None:
        notes = [n for n in notes if tag in n.tags]
    return notes


def search_notes(q: str) -> list[NoteResponse]:
    """Return non-archived notes whose title or content contains *q* (case-insensitive).

    Results are ordered newest-first (highest ID first).
    """
    needle = q.lower()
    matches = [
        n
        for n in _store.values()
        if not n.archived and (needle in n.title.lower() or needle in n.content.lower())
    ]
    return sorted(matches, key=lambda n: n.id, reverse=True)


def get_note(note_id: int) -> NoteResponse | None:
    return _store.get(note_id)


def archive_note(note_id: int) -> NoteResponse | None:
    note = _store.get(note_id)
    if note is None:
        return None
    _store[note_id] = note.model_copy(update={"archived": True})
    return _store[note_id]
