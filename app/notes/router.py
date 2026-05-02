from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import require_auth
from app.notes import service
from app.notes.schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    payload: NoteCreate,
    _auth: dict = Depends(require_auth),  # noqa: B008
) -> NoteResponse:
    return service.create_note(payload)


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    tag: str | None = Query(default=None, description="Filter notes by tag"),
    include_archived: bool = Query(default=False, description="Include archived notes"),
) -> list[NoteResponse]:
    return service.list_notes(tag=tag, include_archived=include_archived)


@router.get("/search", response_model=list[NoteResponse])
async def search_notes(
    q: str = Query(..., min_length=1, description="Keyword to search in title or content"),
) -> list[NoteResponse]:
    return service.search_notes(q)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int) -> NoteResponse:
    note = service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}/archive", response_model=NoteResponse)
async def archive_note(
    note_id: int,
    _auth: dict = Depends(require_auth),  # noqa: B008
) -> NoteResponse:
    note = service.archive_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
