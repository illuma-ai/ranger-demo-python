---
name: org-style
trigger: always
priority: high
---

# Illuma org coding conventions

These rules apply to every change in this repository, regardless of
language or subproject.

## Commits and PRs

- One logical change per PR. If the task spans unrelated areas, stop
  and ask (or split into separate runs).
- Commit messages: imperative mood, present tense, ≤72 char first line.
  e.g. "Fix /users/{id} returning 500 on missing IDs"
- PR title mirrors the commit; PR body explains the *why*, not the *what*.

## Tests

- Every behavioral change includes a test. If a bug was reported,
  write a failing test first, then make it pass.
- Don't disable or skip existing tests to make a change land. If a test
  breaks, either the test or the change is wrong — figure out which.

## Style

- Match surrounding code over enforcing personal style.
- No new dependencies without justification (a one-line comment in the
  PR is enough).
- No commented-out code in the diff. Delete it; git remembers.

## Security

- Never log secrets. Never commit `.env`, `*.pem`, `*.key`, credentials.
- If the task involves auth, validate on the server, never trust the client.
