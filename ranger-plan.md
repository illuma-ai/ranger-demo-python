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

Plan summary: Add GET /health/extended endpoint returning status/uptime/version to app/main.py and a unit test in tests/test_health.py
Plan steps:
  1. Read app/main.py to see the existing /health endpoint style, imports, and app instantiation so the new endpoint matches conventions.
  2. Read tests/test_health.py to match the existing test client setup (e.g. TestClient fixture / import pattern) for the new test.
  3. In app/main.py, add a module-level `_START_TIME = time.monotonic()` (import `time` if not already imported) near the top, without touching the existing /health handler.
  4. Add a new handler `GET /health/extended` in app/main.py returning {'status': 'ok', 'uptime_seconds': time.monotonic() - _START_TIME (float), 'version': '1.0.0'}.
  5. In tests/test_health.py, add `test_health_extended_returns_all_fields` that GETs /health/extended, asserts 200, and asserts the three keys exist with types str, float, str (and status=='ok', version=='1.0.0').
  6. Run/verify tests mentally: ensure uptime_seconds is a float (use float() cast if monotonic diff could be int-like) and that existing /health test still passes.

## Why this executor

Straightforward single-file feature addition plus a unit test — exactly the coding-specialist sweet spot. Qwen3-Coder is the cheapest capable fit; no security or judgment concerns. Review kept on as cheap insurance to confirm types and that /health wasn't altered.

## Review

**Outcome:** ✅ `approved`

> Diff matches plan exactly; new endpoint added cleanly, /health untouched, test covers all three keys and types.

_No findings; the diff implements the plan cleanly._
