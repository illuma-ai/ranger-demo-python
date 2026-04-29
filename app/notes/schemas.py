from __future__ import annotations

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
