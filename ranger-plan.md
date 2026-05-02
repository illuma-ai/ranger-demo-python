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

Plan summary: Add JWT bearer auth (PyJWT HS256) to notes write endpoints with tests and README update
Plan steps:
  1. Add `pyjwt` to dependencies in pyproject.toml.
  2. Create app/auth.py exposing `verify_token(token: str) -> dict | None` that decodes HS256 using secret from env `JWT_SECRET` (default 'dev-secret-do-not-use-in-prod'), returning None on InvalidTokenError/ExpiredSignatureError. Also expose a FastAPI dependency `require_auth` that reads `Authorization: Bearer <token>` header, calls verify_token, and raises HTTPException(401) on missing/malformed/invalid/expired tokens (include WWW-Authenticate: Bearer header).
  3. Update app/notes/router.py to add `dependencies=[Depends(require_auth)]` on the write endpoints only: POST /notes (create_note) and PATCH /notes/{id}/archive (archive_note). Leave all GET endpoints public. Note: the spec mentions PUT/DELETE but the current router has none — only apply to the existing write endpoints (POST, PATCH) and note this in the PR.
  4. Extend tests/notes/test_notes.py (or add tests/test_auth.py) with cases: valid token → 201 on POST, missing Authorization header → 401, malformed token (e.g. 'Bearer garbage' or wrong scheme) → 401, expired token (encoded with past `exp`) → 401. Use the same JWT_SECRET default and PyJWT to mint test tokens. Confirm GET endpoints still return 200 without a token.
  5. Update README.md API section to document that write endpoints require `Authorization: Bearer <jwt>` (HS256, signed with `JWT_SECRET`), GETs remain public, and include a short example curl with a token.

## Why this executor

Real auth boundary (token verification, 401 semantics, header parsing, expiry handling) — per routing rules security-critical surfaces go to the judgment + tool-use tier, not the coding specialist. Scope is small (one new module, a dependency wire-up, tests, README) so Sonnet is sufficient; Opus would be overkill. needs_review=true because auth mistakes (e.g. accepting unsigned tokens, swallowing exceptions, forgetting to require the dep) have outsized impact.

## Review

**Outcome:** ✅ `approved`

> JWT auth correctly applied to write endpoints only; tests cover all required cases; README updated.

_No findings; the diff implements the plan cleanly._
