# Ranger plan — illuma-ai/rem-python#9

_Mode: `planning` · executor: `claude-haiku-4-5` · risk: `trivial` · review: `skip`_

## Task

> Trivial: add httpx example to README quickstart
>
> The README mentions "FastAPI" but the existing README example shows curl with port 8000. Update the README's quickstart to also include the equivalent `httpx` Python snippet alongside the curl example. Single-file change to README.md.

## Plan

Plan summary: Add an httpx Python snippet (alongside a curl example) to the README quickstart targeting the /health endpoint on :8000.
Plan steps:
  1. Read README.md (already ~60 lines) and locate the 'Local run (no GHA)' section that starts the server on port 8000.
  2. In that section (or immediately after it), add a small 'Call the endpoint' block showing both: (a) a `curl http://127.0.0.1:8000/health` example, and (b) an equivalent Python `httpx` snippet (e.g. `import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())`).
  3. Keep formatting consistent with existing fenced code blocks (```bash for curl, ```python for httpx). Do not modify any other file.
  4. Verify the README still renders cleanly (headings, spacing) and that no other sections reference the new block.

## Why this executor

Single-file, docs-only README edit with zero logic risk — exactly the trivial-textual-edit shape Haiku is designated for. No code paths or tests are touched, so review is unnecessary.
