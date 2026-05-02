# Ranger plan — illuma-ai/rem-python#11

_Mode: `planning` · executor: `claude-haiku-4-5` · risk: `trivial` · review: `requested`_

## Task

> Medium: add notes search endpoint with case-insensitive query
>
> Add a search endpoint to the notes API: `GET /notes/search?q=<term>` returning notes whose title or body contains the query string (case-insensitive). Reuse the existing notes router pattern in `app/notes/`. Add at least 3 unit tests covering: hits in title, hits in body, no matches → empty list. Update `tests/notes/test_*.py` accordingly.

## Plan

Plan summary: Add GET /notes/search?q= endpoint with case-insensitive title/body matching plus ≥3 unit tests (title hit, body hit, no matches).
Plan steps:
  1. Read app/notes/router.py, app/notes/service.py, and tests/notes/test_notes.py to assess current state — note that the /notes/search route, service.search_notes(), and tests covering title hit / content hit / no-match / case-insensitivity / archived exclusion / ordering / missing-q 422 already appear to be implemented.
  2. Run the test suite (pytest tests/notes/test_notes.py) to confirm the existing implementation passes. If green, the task's acceptance criteria are already satisfied — report this clearly as a no-op with evidence (list of relevant test names from tests/notes/test_notes.py).
  3. If any gap is found (e.g. a required test missing, or behavior regression), fill it minimally: add the missing test(s) to tests/notes/test_notes.py under the existing '# GET /notes/search' section, and/or adjust app/notes/service.py:search_notes following the established router/service pattern (Query(..., min_length=1), case-insensitive substring match via .lower(), exclude archived, newest-first by id).
  4. Do NOT duplicate existing tests or rename existing symbols. Preserve the existing route ordering in router.py (/search must remain before /{note_id} to avoid path collision).
  5. Summarize findings in the final message: either 'already implemented, N relevant tests passing' or the specific diff applied.

## Why this executor

Inspection shows the endpoint, service function, and a superset of the required tests already exist in the repo. The executor's real job is verification + possible tiny gap-fill, which Haiku handles fine in a single file scope. Review stays on because the planner is instructing a no-op and we want a second pass to confirm nothing was silently changed or missed.

## Review

**Outcome:** ❌ `failed`

> reviewer output unparseable: Bare JSON failed to parse: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
