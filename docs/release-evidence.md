# Release Evidence

## Baseline

- Branch: `final-project` (created from `mid-course-project`)
- Date: 2026-08-10
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- `/health` result: `{"status":"ok","timestamp":"2026-08-10T08:10:23.891274+00:00"}` — HTTP 200
- Frontend check: opened `frontend/index.html` via `python -m http.server 5500` and
  loaded `http://localhost:5500` in a browser with the backend running on port
  8000; the Kanban board (ToDo/InProgress/Done columns), drag-and-drop, and the
  New Task / Edit modal are all present and functional, matching the state already
  verified during the mid-course project (see `docs/midcourse/verification.md`).
- Test command: `python -m tests.verify_a && pytest tests/ -v`
- Test result: all 8 model checks PASS; **28 passed, 0 failed** (3 non-blocking
  `StarletteDeprecationWarning`s about `HTTP_422_UNPROCESSABLE_ENTITY` naming and
  `httpx`/`starlette.testclient` integration — cosmetic, do not affect behavior).

No product features were added on this branch. Changes are limited to: CI workflow,
Dockerfile/.dockerignore, a leaner `requirements-docker.txt`, `AGENTS.md`, and the
`docs/` files required by this stage.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: **pending first push.** The workflow's YAML was
  validated locally (`python -c "import yaml; yaml.safe_load(...)"` — parses
  cleanly, triggers on both `push` and `pull_request`, one job with 6 steps). Since
  this environment has no access to GitHub Actions runners, the workflow has not
  yet executed on GitHub itself as of writing this document. **Action required
  after push:** open the repo's Actions tab, confirm the `CI` workflow run for the
  `final-project` branch is green, and paste that run's URL into this line.
- Test command used by CI: `python -m tests.verify_a` then `pytest tests/ -v`
  (same commands verified locally above), plus a live `/health` check via `curl
  --fail` against the app started in the CI job itself.
- Shortcut check: confirmed by reading `.github/workflows/ci.yml` directly —
  no `continue-on-error`, no `|| true`, pytest is not skipped or conditional,
  Python version is pinned to `3.12` (not "latest" or unspecified), and
  dependencies are explicitly installed via `pip install -r requirements.txt`
  before any test step runs.

## Docker evidence

**Status: Dockerfile and `.dockerignore` are written and reasoned through below,
but the actual `docker build` / `docker run` has not been executed in this
environment because Docker is not available here.** This section will be completed
with real build/run output once run in an environment that has Docker (e.g. your
own machine with Docker Desktop, or after pushing and running it there).

- Build command: `docker build -t task-tracker .`
- Run command: `docker run -p 8000:8000 task-tracker`
- `/health` check: `curl http://127.0.0.1:8000/health` — **not yet run against an
  actual container; run and record the real status code/body here.**
- Non-root check: the `Dockerfile` creates a dedicated `appuser`/`appgroup` and
  switches to it with `USER appuser` before the app starts — verifiable by running
  `docker run task-tracker whoami` and confirming it prints `appuser`, not `root`.
- No-baked-secrets check: `.dockerignore` explicitly excludes `.env`, `.env.*`,
  `*.pem`, `*.key`, `.git/`, and `.github/`. The `Dockerfile` only `COPY`s
  `requirements-docker.txt` and `app/` — no `.env` file exists anywhere in this
  repo to begin with (confirmed via `find . -iname "*.env*"`, zero results).
- **Verified without Docker, as a substitute check:** the exact dependency set the
  Dockerfile installs (`requirements-docker.txt`: `fastapi`, `uvicorn`, `pydantic`,
  `python-dotenv` — deliberately excluding test-only `pytest`/`httpx`) was
  installed into a clean virtual environment, and `app.main:app` was confirmed to
  import and serve `GET /health` → `200` using only that dependency set. This
  proves the Docker image's dependency layer is sufficient to run the app, even
  though the container build itself is still pending.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README states `GET /health` returns 200 | Ran `curl http://127.0.0.1:8000/health` against a live `uvicorn` instance | **Confirmed** — returned `{"status":"ok",...}` with HTTP 200 | None needed |
| README states the test suite has "28 tests" and all pass | Ran `pytest tests/ -v` and counted the summary line | **Confirmed** — `28 passed, 0 failed` | None needed |
| README's status-transition table claims `Done → ToDo` is invalid (422) | Ran `curl -X PATCH .../tasks/{id} -d '{"status":"ToDo"}'` on a task already moved to `Done` | **Confirmed** — returned 422 with the expected "Invalid status transition" detail message | None needed |
| (Docker) README implies `docker run` + `/health` works end-to-end | No Docker available in this environment to test | **Not yet verifiable here** | Flagged explicitly above in "Docker evidence" rather than claimed as confirmed without proof |
