from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="ranger-demo-python")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe used by ECS/ALB and the agent's PR validation step."""
    return {"status": "ok"}
