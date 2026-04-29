from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.notes import service
from app.notes.schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(payload: NoteCreate) -> NoteResponse:
    return service.create_note(payload)


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    tag: str | None = Query(default=None, description="Filter notes by tag"),
) -> list[NoteResponse]:
    return service.list_notes(tag=tag)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int) -> NoteResponse:
    note = service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
