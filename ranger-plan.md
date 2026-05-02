# Ranger plan — illuma-ai/rem-python#11

_Mode: `planning` · executor: `claude-haiku-4-5` · risk: `trivial` · review: `requested`_

## Task

> Medium: add notes search endpoint with case-insensitive query
>
> Add a search endpoint to the notes API: `GET /notes/search?q=<term>` returning notes whose title or body contains the query string (case-insensitive). Reuse the existing notes router pattern in `app/notes/`. Add at least 3 unit tests covering: hits in title, hits in body, no matches → empty list. Update `tests/notes/test_*.py` accordingly.

## Plan

Plan summary: Add GET /notes/search?q=<term> endpoint with case-insensitive title/body matching plus at least 3 unit tests (title hit, body hit, empty result).
Plan steps:
  1. Read app/notes/router.py and app/notes/service.py — both already define a `/notes/search` endpoint and a `search_notes` service function doing case-insensitive substring matching on title and content, ordered newest-first and excluding archived notes. Verify the implementation still matches the task requirements; no code changes needed unless gaps are found.
  2. Read tests/notes/test_notes.py — the `GET /notes/search` section already contains tests for title hits (`test_search_notes_matches_title`), body/content hits (`test_search_notes_matches_content`), case-insensitivity, ordering, empty-result (`test_search_notes_empty_when_no_match`), archived exclusion, and missing `q` param. The required ≥3 test cases (title hit, body hit, no-match empty list) are already present.
  3. If everything is already in place, make no code edits; instead run the test suite (e.g. `pytest tests/notes/test_notes.py -q`) to confirm the endpoint and tests pass, and report that the feature is already implemented.
  4. If any gap is discovered (e.g. endpoint missing, a required test case absent), add the minimal missing piece following the existing router/service patterns in app/notes/ and the test style in tests/notes/test_notes.py (use the `reset_store` fixture, TestClient from app.main).

## Why this executor

Standard coding-specialist work: small FastAPI endpoint + unit tests within a single module. Qwen3-Coder is the cheapest model that fits coding work. Inspection shows the feature already exists, so the executor may only need to verify — still worth reviewing to confirm nothing was silently regressed or duplicated.

## Review

**Outcome:** ✅ `approved`

> Feature and ≥3 required tests already exist; executor correctly made no code changes and the only diff is an agent meta-file.

_No findings; the diff implements the plan cleanly._
