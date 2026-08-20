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
- Latest run link or note: **confirmed green.** Commit `a5857a4` (pushed to
  `final-project`) triggered `CI #1` on GitHub Actions, which completed
  successfully (green checkmark) in 18 seconds. Verified directly on GitHub's
  Actions tab (`https://github.com/ayoubhayik-cmyk/task-tracker/actions`) and by
  fetching the commit itself, which confirms all 26 files — including
  `.github/workflows/ci.yml`, `Dockerfile`, `.dockerignore`, `AGENTS.md`, and the
  full `docs/` set — landed on the `final-project` branch exactly as written. This
  means all three CI steps (`verify_a`, the full pytest suite, and the live
  `/health` check) passed on a real GitHub-hosted Ubuntu runner, not just locally.
- Test command used by CI: `python -m tests.verify_a` then `pytest tests/ -v`
  (same commands verified locally above), plus a live `/health` check via `curl
  --fail` against the app started in the CI job itself.
- Shortcut check: confirmed by reading `.github/workflows/ci.yml` directly —
  no `continue-on-error`, no `|| true`, pytest is not skipped or conditional,
  Python version is pinned to `3.12` (not "latest" or unspecified), and
  dependencies are explicitly installed via `pip install -r requirements.txt`
  before any test step runs.

## Docker evidence

- Build command: `docker build -t task-tracker .`
- Build result: **succeeded.** Ran with Docker version 29.7.2 (build a7dcaa6).
  All 6 build steps completed (base image pull, WORKDIR, dependency install from
  `requirements-docker.txt`, app code copy, non-root user creation), image tagged
  `task-tracker:latest`.
- Run command: `docker run -p 8000:8000 task-tracker`
- `/health` check: **confirmed, real result.** With the container running, ran
  `curl -w "\nHTTP %{http_code}\n" http://127.0.0.1:8000/health` from a second
  terminal against the live container. Actual response body:
  `{"status":"ok","timestamp":"2026-08-18T20:37:06.567975+00:00"}` followed by
  `HTTP 200`. Independently confirmed by the container's own server log, which
  recorded `"GET /health HTTP/1.1" 200 OK` for that same request.
- Non-root check: **confirmed, real result.** `docker run task-tracker whoami`
  printed `appuser`, not `root`, matching the `USER appuser` instruction in the
  `Dockerfile`.
- No-baked-secrets check: `.dockerignore` explicitly excludes `.env`, `.env.*`,
  `*.pem`, `*.key`, `.git/`, and `.github/`. The `Dockerfile` only `COPY`s
  `requirements-docker.txt` and `app/` — no `.env` file exists anywhere in this
  repo to begin with (confirmed via `find . -iname "*.env*"`, zero results).

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README states `GET /health` returns 200 | Ran `curl http://127.0.0.1:8000/health` against a live `uvicorn` instance | **Confirmed** — returned `{"status":"ok",...}` with HTTP 200 | None needed |
| README states the test suite has "28 tests" and all pass | Ran `pytest tests/ -v` and counted the summary line | **Confirmed** — `28 passed, 0 failed` | None needed |
| README's status-transition table claims `Done → ToDo` is invalid (422) | Ran `curl -X PATCH .../tasks/{id} -d '{"status":"ToDo"}'` on a task already moved to `Done` | **Confirmed** — returned 422 with the expected "Invalid status transition" detail message | None needed |
| README claims `docker run` + `/health` works end-to-end | Built and ran the actual Docker image, then curled `/health` against the live container | **Confirmed** — real container returned HTTP 200 (see Docker evidence above) | None needed |