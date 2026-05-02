# Ranger plan — illuma-ai/rem-python#10

_Mode: `planning` · executor: `claude-haiku-4-5` · risk: `trivial` · review: `requested`_

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

Plan summary: Add GET /health/extended endpoint returning status, uptime_seconds, version; add unit test validating fields and types.
Plan steps:
  1. Edit app/main.py: add `import time` and a module-level `_START_TIME = time.monotonic()` near the top (after imports, before app creation).
  2. In app/main.py, add a new `@app.get('/health/extended')` async handler returning `{'status': 'ok', 'uptime_seconds': time.monotonic() - _START_TIME, 'version': '1.0.0'}` with an appropriate return type annotation (e.g. `dict[str, object]`). Leave the existing `/health` endpoint untouched.
  3. Edit tests/test_health.py: add `test_health_extended_returns_all_fields` that GETs `/health/extended`, asserts 200, then asserts `status` is str and equals 'ok', `uptime_seconds` is a float (>= 0), and `version` is str equal to '1.0.0'. Preserve existing test.
  4. Run `pytest tests/test_health.py` mentally/locally to confirm both tests pass.

## Why this executor

Two small, well-specified edits to two files with no logic branching or security surface — well within Haiku's trivial-tier capability. Keeping needs_review=true as cheap insurance to confirm types in the test match the spec and that _START_TIME is placed at module level (not inside the handler).

## Review

**Outcome:** ✅ `approved`

> Diff matches plan exactly: new endpoint, module-level _START_TIME, test covers all three fields with correct types.

_No findings; the diff implements the plan cleanly._
