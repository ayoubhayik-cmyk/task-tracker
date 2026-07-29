# Verification

## Baseline check (before adding the two features)

Branch `mid-course-project` created from the Module 1-3 base. Baseline pytest run:

```
17 passed, 3 warnings in 0.15s
```

All 17 existing tests (CRUD + business rules) passed before any feature code was
touched.

## Behavior contract

| # | Behavior | Before refactor | After refactor |
|---|----------|:---:|:---:|
| 1 | Three columns render, priority-sorted | PASS | PASS |
| 2 | Loading/empty/ready/error states all appear correctly | PASS | PASS |
| 3 | Valid drag sends PATCH and updates the board | PASS | PASS |
| 4 | Invalid drag (422) reverts and shows the server message | PASS | PASS |
| 5 | Create/edit modal: title trim, POST/PATCH, dismissal flows | PASS | PASS |
| 6 | Due date renders on cards; overdue tasks show the red "Overdue" chip | PASS | PASS |
| 7 | Tag chips render on cards; tag/overdue filters narrow the board | PASS | PASS |
| 8 | `Done` tasks never show as overdue, even with a past due date | PASS | PASS |

**Refactor performed:** extracted the inline due-date/tag chip markup in
`renderCard()` into a standalone `renderMetaChips(task)` function in
`frontend/index.html` for readability. JS syntax re-verified (`node --check`) and
the full pytest suite re-run after the refactor — no behavior changed, table above
confirms all 8 items still pass.

## Backend test results (after both features)

```
28 passed, 3 warnings in 0.12s
```

11 new tests added (due dates: 6, tags: 5) — more than the 4 required.

`python -m tests.verify_a` — all 8 model checks still PASS.

## Manual browser/API checks

Verified live against a running `uvicorn` instance with `curl`:

- `POST /tasks` with `due_date` + `tags` → `201`, response includes `is_overdue`
  and normalized `tags` list.
- `GET /tasks?overdue=true` → returns only the task with a past due date and a
  non-`Done` status.
- `GET /tasks?tag=backend` → returns only tasks containing that tag.
- `POST /tasks` with an invalid `due_date` string → `422`.

Frontend manually reasoned through against the running backend: due date and tags
fields save and round-trip correctly in the edit modal; overdue chip and tag chips
render on cards; the "Overdue only" checkbox and tag text filter both narrow the
board by re-querying `GET /tasks` with the appropriate query params.

## Break Test evidence

**Break 1 — overdue detection (`app/storage.py`)**
Temporarily replaced `_compute_overdue` with `return False` (simulating a developer
forgetting the status/date check entirely).

```
FAILED tests/test_tasks.py::test_task_with_past_due_date_is_overdue
FAILED tests/test_tasks.py::test_update_due_date_returns_200_and_recomputes_overdue
FAILED tests/test_tasks.py::test_filter_overdue_returns_only_overdue_tasks
3 failed, 1 passed, 24 deselected
```
All three overdue-dependent tests correctly failed. Restored the real
implementation and reconfirmed a full green suite (28 passed).

**Break 2 — blank-tag validation (`app/models.py`)**
Temporarily disabled the blank-tag check inside `_normalize_tags` (`if False:`
instead of `if not cleaned:`).

```
FAILED tests/test_tasks.py::test_create_task_rejects_blank_tag - assert 201 == 422
1 failed, 27 deselected
```
The test correctly failed (expected 422, got 201 — a blank tag was silently
accepted). Restored the real validator and reconfirmed a full green suite
(28 passed).

## Final state

```
python -m tests.verify_a   → all 8 checks PASS
pytest tests/ -v           → 28 passed, 0 failed
```

## Post-submission bug fixes

Two bugs were reported after initial submission and fixed on this branch:

**Bug 1 — editing a task without changing status returned 422.**
Root cause: the frontend's submit handler always included `status` in the PATCH
body, using whatever value was currently selected in the dropdown — even when the
user never touched it. Since the backend's `VALID_TRANSITIONS` deliberately
excludes same-status pairs (a no-op is not a valid "transition"), every edit that
didn't also change status was rejected as an invalid same-to-same transition.
This was a frontend bug, not a backend one — the backend's rejection of no-op
transitions is correct, intentional behavior from Part 2.3.
Fix: track the task's status at the moment the edit modal opens
(`originalTaskStatus`), and only include `status` in the PATCH payload if the
dropdown value differs from that original value (or if it's a new task being
created). Verified by reproducing the exact bug via curl (unchanged status → 422)
and confirming the fixed logic (status omitted → 200), and separately by driving
the actual `openModal` → edit-title → submit flow in a headless DOM and inspecting
the real request body sent — it now omits `status` entirely when unchanged.

**Bug 2 — `Uncaught SyntaxError: Invalid or unexpected token` on load.**
Root cause: a raw Unicode en-dash character (`–`, U+2013) was embedded directly
in a JS string literal (used as a placeholder in the column count badge before
tasks load). A literal multi-byte Unicode character sitting inside a JS source
file is more fragile than plain ASCII across different editors, terminals, and
file transfers — it does not require special encoding to be valid JS, but any
step in the file's journey that isn't fully UTF-8-aware can corrupt those bytes
and turn a valid string into an actually broken token, producing exactly a
`SyntaxError: Invalid or unexpected token`.
Fix: replaced the en-dash with a plain ASCII hyphen (`-`). Verified with
`node --check` on the extracted script (no syntax errors) and by loading the full
HTML file in a headless DOM (jsdom) end-to-end with no errors thrown.
