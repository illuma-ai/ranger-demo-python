# ranger-demo-python

Minimal FastAPI service used to demonstrate the
[Ranger Agent](https://github.com/illuma-ai/ranger-agent) end-to-end on
Python codebases. One endpoint, one test, ~20 lines of code.

## What's here

- An `app/main.py` with a single `/health` endpoint.
- `.ranger/skills/` containing org conventions + FastAPI-specific rules.
- `.github/workflows/ranger.yml` that runs the agent on labeled issues.

## How the agent runs

1. Open an issue describing what you want changed (e.g. "Add /version endpoint").
2. Apply the **`auto-fix`** label to the issue.
3. The workflow fires:
   - Clones the repo.
   - Loads skills from `.ranger/skills/` and the bundled `builtin:python`.
   - Runs the LLM agent against AWS Bedrock (Sonnet 4.6 by default).
   - Validates the diff (non-empty, applies cleanly, `python -m compileall app/` passes).
   - Branches, commits, pushes, and opens a draft PR.
4. Review the PR. Merge or close.

If anything fails (validation, model limits, no diff) the workflow exits
with a clear status and no PR is opened. Agent never opens broken PRs.

## Required secrets

Set these on the repo via Settings → Secrets and variables → Actions:

| Secret | Purpose |
|---|---|
| `BEDROCK_AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `BEDROCK_AWS_ACCESS_KEY_ID` | IAM key with `bedrock:InvokeModel` |
| `BEDROCK_AWS_SECRET_ACCESS_KEY` | matching secret |

The default `GITHUB_TOKEN` is used for git push and PR creation. For
production use a fine-grained PAT or GitHub App so the bot's PR triggers
downstream CI workflows.

## Manual trigger (without an issue)

```bash
gh workflow run "Ranger Agent" \
    --ref main \
    -f task="Add a /version endpoint that returns {\"version\":\"0.1.0\"}"
```

## Conventions enforced via `.ranger/skills/`

- `org-style.md` — always-on rules (commit messages, tests, security)
- `python-fastapi.md` — file_pattern triggered for `**/*.py`:
  FastAPI patterns, Pydantic v2 DTOs, package layout, iteration commands.

A bundled `builtin:python` skill also loads automatically — repo-level
skills override it where they conflict.

## Local run (no GHA)

```bash
pip install -e ".[dev]"
pytest -q                                             # ~1s
uvicorn app.main:app --reload                         # /health on :8000
```

Then hit it from Python:

```bash
curl http://127.0.0.1:8000/health
```

```python
import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())
```

## Architecture reference

- Agent CLI: [illuma-ai/ranger-agent](https://github.com/illuma-ai/ranger-agent)
- Action source: [illuma-ai/ranger-agent/action](https://github.com/illuma-ai/ranger-agent/tree/main/action)
