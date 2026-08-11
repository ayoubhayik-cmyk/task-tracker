# Task Tracker

A FastAPI backend + vanilla JS Kanban frontend, built across Modules 1-3 of the
AI-Assisted Coding course.

## What's here

- `app/` — FastAPI backend: models, in-memory storage, CRUD routes, status-transition
  business rules.
- `frontend/index.html` — Kanban board (fetch/render, loading/empty/ready/error states,
  drag-and-drop, create/edit modal).
- `tests/` — `verify_a.py` (model verification script) and the pytest suite
  (`test_tasks.py`, 28 tests).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

- Health check: `curl http://127.0.0.1:8000/health`
- Interactive API docs: http://127.0.0.1:8000/docs

## Run the frontend

The frontend must be served (not opened as a `file://` URL) so the browser sends a
proper origin for CORS. With the backend already running on port 8000:

```bash
cd frontend
python -m http.server 5500
```

Then open http://localhost:5500 in your browser. If you serve the frontend from a
different port, add that origin to the `allow_origins` list in `app/main.py`.

## Run the tests

```bash
python -m tests.verify_a      # 8 model-validation checks, should all print PASS
pytest tests/ -v               # 28 tests, should all pass
```

### Break Test (proving the tests are meaningful)

1. Comment out `validate_status_transition(...)` in the PATCH route in `app/main.py`.
2. Run `pytest tests/ -v -k "invalid_transition or same_status"` — both should now fail.
3. Restore the line and confirm the suite is green again.
4. Repeat with the blank-title check in `app/models.py` and the
   `test_create_task_blank_title_returns_422` test.

## API summary

| Method | Route              | Status codes        |
|--------|--------------------|----------------------|
| GET    | `/health`          | 200                  |
| POST   | `/tasks`           | 201, 422             |
| GET    | `/tasks`           | 200 (optional `status`, `priority`, `overdue`, `tag` filters) |
| GET    | `/tasks/{task_id}` | 200, 404             |
| PATCH  | `/tasks/{task_id}` | 200, 404, 422        |
| DELETE | `/tasks/{task_id}` | 204, 404             |

### Status transition rules

Allowed: `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress`.
Everything else (including same-status no-ops) returns `422`.

### Due dates + overdue

- Optional `due_date` (ISO date, e.g. `2026-08-01`) on create/update.
- `is_overdue` is computed server-side: true only if `due_date` is in the past
  **and** the task's status is not `Done`.
- Filter with `GET /tasks?overdue=true`.

### Tags

- Optional `tags` list on create/update. Each tag is trimmed; blank tags are
  rejected (422); max 10 tags per task, 30 chars per tag.
- Filter with `GET /tasks?tag=backend`.

## Mid-Course Project documentation

See [`docs/midcourse/`](docs/midcourse/) for user stories, the mini-ADR, the prompt
log, verification evidence (including Break Tests and post-submission bug fixes),
and the reflection for the two features added on the `mid-course-project` branch
(due dates + overdue filter, and tags/labels).

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope — no new
  product features were added on this branch.
- CI (`.github/workflows/ci.yml`) runs `python -m tests.verify_a`, the full pytest
  suite, and a live `/health` check on every push and pull request.
- A Docker image builds from `Dockerfile`/`requirements-docker.txt` with a
  runtime-only dependency set (no test tooling baked in) and runs as a non-root
  user; see `docs/release-evidence.md` for exact verification status.
- AI review, security, and ownership evidence is in `docs/final-ai-review.md`;
  repo-specific AI guardrails are in `AGENTS.md`.

### How to run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### How to run tests

```bash
python -m tests.verify_a
pytest tests/ -v
```

### How to run with Docker

```bash
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
curl http://127.0.0.1:8000/health
```

### Evidence files

- [`docs/release-evidence.md`](docs/release-evidence.md)
- [`docs/final-ai-review.md`](docs/final-ai-review.md)
- [`docs/ai-playbook.md`](docs/ai-playbook.md)

### AI assistance summary

AI helped draft or review: CI workflow, Dockerfile hardening, AGENTS.md, security
review, and documentation.
I verified the work by: running the full test suite and Break Tests, live curl
checks against a running server, a headless-DOM reproduction of a real bug fix, and
a clean-venv simulation of the Docker image's exact dependency set (proven to serve
`/health` → 200 before the container itself was ever built).
One AI suggestion I rejected or corrected: an AI-suggested "fix" to weaken
`VALID_TRANSITIONS` to make a frontend bug stop surfacing — rejected because it
would have silently reversed a deliberate, already-tested backend rule; fixed the
real frontend defect instead (see `docs/final-ai-review.md`).
