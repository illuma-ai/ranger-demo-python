# Ranger plan — illuma-ai/rem-python#12

_Mode: `planning` · executor: `claude-sonnet-4-6` · risk: `medium` · review: `requested`_

## Task

> Security: add JWT auth to notes write endpoints
>
> Add basic JWT authentication for the notes write endpoints (POST/PUT/DELETE).
>
> Requirements:
> - New module `app/auth.py` exposing `verify_token(token: str) -> dict | None` using PyJWT (HS256). Secret read from `JWT_SECRET` env var; default `"dev-secret-do-not-use-in-prod"`.
> - A FastAPI dependency `require_auth` that reads the `Authorization: Bearer <token>` header, calls `verify_token`, raises 401 on failure.
> - Apply `require_auth` to the notes write endpoints only. GET endpoints stay public.
> - Add unit tests covering: valid token → 200, missing token → 401, malformed token → 401, expired token → 401.
>
> Document the auth requirement in the README's API section.

## Plan

Plan summary: Add JWT bearer auth to notes write endpoints with a new app/auth.py module, FastAPI dependency, tests, and README docs.
Plan steps:
  1. Add `pyjwt>=2.8` to `dependencies` in pyproject.toml (runtime dep, used by app/auth.py).
  2. Create `app/auth.py` exposing: (a) `verify_token(token: str) -> dict | None` that decodes HS256 using `JWT_SECRET` env var (default `"dev-secret-do-not-use-in-prod"`), returning the payload on success and `None` on any `jwt.PyJWTError` (invalid signature, malformed, expired, etc.); (b) a FastAPI dependency `require_auth` that reads the `Authorization` header, requires the `Bearer <token>` scheme, calls `verify_token`, and raises `HTTPException(status_code=401, detail="Invalid or missing token")` with `WWW-Authenticate: Bearer` header on missing/malformed header or when `verify_token` returns None. Return the decoded payload so endpoints can use it if needed.
  3. Edit `app/notes/router.py`: import `require_auth` from `app.auth` and attach it via `dependencies=[Depends(require_auth)]` on the write endpoints only — `create_note` (POST /notes) and `archive_note` (PATCH /notes/{id}/archive). Leave all GET endpoints (`list_notes`, `search_notes`, `get_note`) public. Note: task mentions PUT/DELETE but the router only has POST + PATCH writes today; apply auth to those existing write endpoints (do NOT add new PUT/DELETE handlers).
  4. Update existing tests in `tests/notes/test_notes.py` that hit POST `/notes` and PATCH `/notes/{id}/archive` so they continue to pass — simplest approach: add a `pytest` fixture (or helper) that injects a valid `Authorization: Bearer <token>` header on the shared `TestClient`, e.g. by generating a valid token with `app.auth` and using `client.headers.update(...)` in an autouse fixture. Keep GET tests untouched.
  5. Add `tests/test_auth.py` with unit tests covering: (1) valid token → POST /notes returns 201; (2) missing `Authorization` header → 401; (3) malformed token (e.g. `Bearer not.a.jwt`) → 401; (4) expired token (generate with `exp` in the past using the same secret) → 401. Use `jwt.encode` directly in tests with the module's secret to construct tokens; import `verify_token` for at least one direct unit test of the function as well.
  6. Update `README.md`: add a short "API / Authentication" subsection noting that POST and PATCH `/notes*` endpoints require `Authorization: Bearer <JWT>` signed HS256 with `JWT_SECRET`, that GET endpoints are public, and that the default dev secret must be overridden in production via the `JWT_SECRET` env var.
  7. Run `pytest -q` and `python -m compileall app/` locally in the executor's head to sanity-check before emitting the diff.

## Why this executor

Security-sensitive (auth surface) touching multiple files: new module, router wiring, test fixture changes, and docs. Sonnet is the right balance — Haiku is unsuitable for auth work, Opus is overkill for a well-scoped JWT dependency using PyJWT. Review is required because the task touches an auth boundary and because the task text says PUT/DELETE but the codebase only has POST/PATCH writes — a human should confirm the executor's interpretation.

## Review

**Outcome:** ✅ `approved`

> JWT auth correctly applied to POST/PATCH writes; verify_token, dependency, tests, and README all match the plan.

**Findings:**
- ranger-plan.md added at repo root — not in the plan; likely a tooling artifact but technically scope creep
- tests/notes/test_notes.py and tests/test_auth.py import private names (_ALGORITHM, _JWT_SECRET_DEFAULT) from app.auth; works fine but couples tests to internals — consider exposing these as public constants if reused
