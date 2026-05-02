# Ranger plan — illuma-ai/rem-python#10

_Mode: `planning` · executor: `qwen3-coder-480b-a35b` · risk: `low` · review: `requested`_

## Task

> Simple: add /health/extended endpoint with version + uptime
>
> Add a new endpoint `GET /health/extended` to `app/main.py` that returns:
> - `status: "ok"`
> - `uptime_seconds`: float, computed from a module-level `_START_TIME` set at import
> - `version`: "1.0.0"
>
> Add a unit test in `tests/test_health.py` named `test_health_extended_returns_all_fields` asserting the three keys are present with correct types. Do not change the existing `/health` endpoint.

## Plan

Plan summary: Add GET /health/extended endpoint returning status, uptime_seconds, and version, plus a unit test verifying the response shape.
Plan steps:
  1. Read app/main.py to identify the framework (likely FastAPI/Flask), the existing /health endpoint pattern, and current imports.
  2. Read tests/test_health.py to match the existing test style (client fixture, assertion patterns).
  3. In app/main.py, add `import time` if not present and a module-level `_START_TIME = time.time()` near the top (after imports, before routes).
  4. Add a new route `GET /health/extended` in app/main.py returning `{"status": "ok", "uptime_seconds": time.time() - _START_TIME, "version": "1.0.0"}`. Do not modify the existing /health handler.
  5. In tests/test_health.py, add `test_health_extended_returns_all_fields` that GETs /health/extended, asserts 200, and asserts `status` is str == 'ok', `uptime_seconds` is float (and >= 0), and `version` is str == '1.0.0'.
  6. Run/verify tests mentally against existing patterns; ensure no other endpoints or tests are altered.

## Why this executor

Routine add-an-endpoint-plus-test task with a clear spec — exactly the shape Qwen3-Coder is the default for, and it's the cheapest capable option. Low risk (single new endpoint, single new test, no changes to existing behavior), but review is kept on as cheap insurance against drift (e.g., forgetting _START_TIME placement or type assertions).

## Review

**Outcome:** ✅ `approved`

> Diff correctly implements the /health/extended endpoint and test per plan; all three fields covered with proper type checks.

_No findings; the diff implements the plan cleanly._
