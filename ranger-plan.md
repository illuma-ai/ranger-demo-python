# Ranger plan — illuma-ai/rem-python#12

_Mode: `planning` · executor: `claude-sonnet-4-6` · risk: `high` · review: `requested`_

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

Plan summary: Add JWT (HS256) auth dependency and protect notes write endpoints, with tests and README docs.
Plan steps:
  1. Add PyJWT to dependencies in pyproject.toml.
  2. Create app/auth.py exposing verify_token(token: str) -> dict | None using PyJWT HS256, reading JWT_SECRET env var (default 'dev-secret-do-not-use-in-prod'); return None on InvalidTokenError/ExpiredSignatureError/DecodeError. Also define a FastAPI dependency require_auth that extracts the 'Authorization: Bearer <token>' header, calls verify_token, and raises HTTPException(401) on missing/malformed/invalid/expired tokens (use WWW-Authenticate: Bearer header).
  3. Update app/notes/router.py to apply require_auth via Depends only to write endpoints: create_note (POST '') and archive_note (PATCH '/{note_id}/archive'). If PUT/DELETE handlers do not exist yet, protect only the existing write endpoints (POST, PATCH) — do NOT invent new endpoints beyond the task spec. Leave all GET endpoints public.
  4. Add tests in tests/notes/test_auth.py (or extend tests/notes/test_notes.py) covering: (a) valid token → 201 on POST /notes, (b) missing Authorization header → 401, (c) malformed token (e.g. 'Bearer not-a-jwt' or wrong scheme) → 401, (d) expired token (jwt.encode with exp in the past) → 401. Use the same JWT_SECRET via monkeypatch or by importing the default; encode tokens with PyJWT HS256 in the test helpers.
  5. Update README.md API section to document that POST/PATCH (write) endpoints require 'Authorization: Bearer <token>' using HS256 signed with JWT_SECRET env var, and that GET endpoints remain public. Include a short curl example.
  6. Run tests mentally/verify imports; ensure no GET endpoint accidentally gets the dependency.

## Why this executor

Real auth boundary (JWT verification, header parsing, expiry handling, secret management) where executor judgment during implementation prevents subtle bugs review can miss (e.g. silently accepting unsigned tokens, wrong algorithm, leaking 500s instead of 401s). Sonnet's judgment + tool-use reliability tier is the documented fit for auth/crypto surfaces; Qwen3-Coder is cheaper but the catalog explicitly steers real auth boundaries to Sonnet. Review still on.

## Review

**Outcome:** ✅ `approved`

> JWT auth dependency correctly applied to write endpoints only; tests cover all required cases; README documented.

_No findings; the diff implements the plan cleanly._
