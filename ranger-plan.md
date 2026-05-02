# Ranger plan — illuma-ai/rem-python#9

_Mode: `planning` · executor: `claude-haiku-4-5` · risk: `trivial` · review: `skip`_

## Task

> Trivial: add httpx example to README quickstart
>
> The README mentions "FastAPI" but the existing README example shows curl with port 8000. Update the README's quickstart to also include the equivalent `httpx` Python snippet alongside the curl example. Single-file change to README.md.

## Plan

Plan summary: Add an httpx Python snippet to the README quickstart showing how to hit /health on port 8000.
Plan steps:
  1. Open README.md and locate the 'Local run (no GHA)' section which contains the bash block with `pip install`, `pytest`, and `uvicorn app.main:app --reload` (referencing port 8000 via the trailing comment).
  2. Immediately after that bash fence, add a short follow-up paragraph like 'Then hit it from Python:' and a new ```python fenced block showing the equivalent httpx call, e.g. `import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())`.
  3. Optionally also show the curl equivalent (`curl http://127.0.0.1:8000/health`) in a bash block directly above the python block so readers see both — the task description explicitly mentions a curl example 'alongside' the httpx snippet.
  4. Keep wording minimal and consistent with the existing terse README style. Do not modify any other file; no dependency additions (httpx is illustrative, not a new project dep).

## Why this executor

Single-file docs edit to README.md with no logic impact — exactly the Haiku trivial-tier sweet spot. No review needed: nothing to verify beyond 'snippet renders and reads sensibly'.
