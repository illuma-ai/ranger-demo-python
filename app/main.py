from __future__ import annotations

from fastapi import FastAPI

from app.notes.router import router as notes_router

app = FastAPI(title="ranger-demo-python")
app.include_router(notes_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe used by ECS/ALB and the agent's PR validation step."""
    return {"status": "ok"}
