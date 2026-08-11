# AGENTS.md

Instructions for any AI coding assistant (Claude, Copilot, Cursor, etc.) working in
this repository. Read this file before making changes.

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, in-memory storage (no database).
- **Frontend:** Vanilla HTML/CSS/JS in a single file (`frontend/index.html`), no
  framework, no build step.
- **Tests:** pytest + FastAPI's `TestClient`.
- **CI:** GitHub Actions (`.github/workflows/ci.yml`).
- **Container:** Docker, single-stage `python:3.12-slim` image, backend only.

## Run / test commands

```bash
# Backend
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal, from the frontend/ directory)
python -m http.server 5500

# Tests
python -m tests.verify_a
pytest tests/ -v

# Docker
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
curl http://127.0.0.1:8000/health
```

## Read-first guardrail

Before proposing any change, read the actual files involved
(`app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/main.py`,
`frontend/index.html`, `tests/test_tasks.py`) rather than assuming a typical
FastAPI project layout. This repo has specific conventions (see below) that
differ from generic examples.

## Project rules

1. **Status values are exactly** `ToDo`, `InProgress`, `Done` — not `"in_progress"`,
   not `"To Do"`. Priority values are exactly `Low`, `Medium`, `High`.
2. **Status transitions are backend-enforced**, not UI-enforced. Valid transitions
   live in `app/business_rules.py::VALID_TRANSITIONS`. Same-status "transitions"
   are intentionally invalid (422) — this is a deliberate rule, not a bug. Do not
   "fix" a same-status rejection by weakening this set; if a caller doesn't want to
   change status, it should omit the `status` field from the PATCH body entirely.
3. **Server-managed fields** (`id`, `created_at`, `updated_at`, `is_overdue`) must
   never be accepted from client input. `TaskCreate`/`TaskUpdate` use
   `extra="forbid"` — keep it that way.
4. **`is_overdue` is computed in the backend** (`app/storage.py::_compute_overdue`),
   not the frontend. It depends on both `due_date` and `status` (a `Done` task is
   never overdue). Do not move this logic into the frontend.
5. **One small change at a time.** Do not rewrite `app/main.py`,
   `frontend/index.html`, or the test suite wholesale. Propose a focused diff for
   the specific function or section being changed.
6. **No new product features** on the `final-project` branch. This branch is for
   hardening, testing, documentation, CI, and Docker only — not comments,
   authentication, a real database, or notifications.
7. **No secrets, tokens, `.env` values, or real personal/customer data** in code,
   commits, prompts, or docs. This app uses in-memory storage and has no
   authentication; there should be no credentials anywhere in this repo.

## Unexpected app/ or frontend/ edits rule

`app/` and `frontend/` should only be touched for: a small, explainable bug fix; a
security fix; or a documentation-supported correction. Any such change must be
explained in `docs/final-ai-review.md`, including what was wrong and why the fix is
correct. Do not use a "cleanup" or "refactor" task as cover for unrelated feature
changes.

## Before finishing any task

- Run `python -m tests.verify_a` and `pytest tests/ -v` — both must pass.
- If you touched `frontend/index.html`, check for JS syntax errors
  (`node --check` on the extracted `<script>` block) and avoid embedding
  non-ASCII characters directly in string literals.
- State clearly what you changed, why, and how you verified it — do not claim a
  fix works without having run something to check it.
