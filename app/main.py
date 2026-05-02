from __future__ import annotations

import time

from fastapi import FastAPI

from app.notes.router import router as notes_router

_START_TIME = time.monotonic()

app = FastAPI(title="ranger-demo-python")
app.include_router(notes_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe used by ECS/ALB and the agent's PR validation step."""
    return {"status": "ok"}


@app.get("/health/extended")
async def health_extended() -> dict[str, str | float]:
    """Extended health check with uptime and version information."""
    return {
        "status": "ok",
        "uptime_seconds": float(time.monotonic() - _START_TIME),
        "version": "1.0.0",
    }
