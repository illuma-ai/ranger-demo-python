---
name: python-fastapi
trigger: file_pattern
file_patterns: ["**/*.py", "**/pyproject.toml"]
priority: high
---

# FastAPI conventions for this repo

These rules apply on top of `builtin:python` and `org-style.md`. When in
doubt, match the surrounding code.

## Folder layout

- One folder per feature: `app/<feature>/router.py`, `app/<feature>/service.py`,
  `app/<feature>/schemas.py`.
- Routers mount in `app/main.py` via `app.include_router(...)`. Don't
  declare endpoints directly in `main.py` beyond `/health`.
- Keep `app/__init__.py` empty.

## Schemas (Pydantic v2)

- All request/response models live in `schemas.py`.
- Split request and response models — never reuse a single model for both.
- Pydantic v2 only (`model_config`, `Field(...)`, `field_validator`). No
  `Config` inner classes, no v1-style validators.

## Services

- No mutable module-level state in `service.py`. Use plain functions or
  stateless classes. Inject dependencies via parameters or FastAPI's
  `Depends`.
- Services raise domain errors; routers translate them to
  `HTTPException(status_code=..., detail=...)`.

## Validation and errors

- Rely on Pydantic in route signatures — don't hand-roll validation
  inside the handler when the type system can do it.
- For business errors raise `HTTPException` with a specific status code
  and a short `detail` string. Don't return error dicts manually.

## Type hints and async

- Type hints required everywhere, including return types. Run
  `python -m compileall app/` before committing.
- `from __future__ import annotations` at the top of every module.
- Route handlers are `async def` by default. Only use sync `def` when
  you genuinely have a CPU-bound or blocking call you can't await.
- For outbound HTTP use `httpx.AsyncClient`. Don't pull in `requests`.

## Tests

- Tests live in `tests/<feature>/test_<thing>.py`, mirroring the app
  layout.
- Use `fastapi.testclient.TestClient(app)` for endpoint tests. Only
  reach for a real `httpx.AsyncClient` against a running server in
  integration tests.

## Iteration commands (use these, in this order)

- Type-check a module after edits: `python -m compileall app/`
- Run a single test: `pytest tests/path/test_x.py::test_name`
- Don't run the full `pytest` suite between every edit — it's slower
  than necessary while iterating.

## Lint

- `ruff check .` must pass with zero findings.
- Run `ruff format .` before commit.
