# Prompt Log

## Feature 1: Due dates + overdue filter

### Prompt 1 (weak → strong rewrite)

**Weak version:**
> Add due dates to tasks.

**Why it was too weak:** it doesn't say where `is_overdue` should be computed, what
happens when a task is `Done`, or what date type to use. Left this open, the AI's
first pass computed overdue status live in the frontend only, with no backend field
or query filter at all — unusable for the "overdue filter" half of the feature.

**Improved version:**
> Add an optional `due_date: date` field to `TaskCreate`, `TaskUpdate`, and
> `TaskResponse` in `app/models.py`. Add a computed `is_overdue: bool` field to
> `TaskResponse`. A task is overdue only if `due_date` is in the past AND
> `status != Done`. Compute `is_overdue` in `app/storage.py` on both create and
> update (since either `due_date` or `status` can change it). Add an `overdue`
> query filter to `GET /tasks`. Do not compute overdue status in the frontend.

**What I accepted/edited/rejected:** accepted the model and storage changes as
generated. Rejected the AI's first draft of `_compute_overdue`, which only checked
`due_date < today` and ignored `status` — a `Done` task with an old due date would
have stayed flagged overdue forever. Edited it to add the `status == TaskStatus.DONE`
exclusion.

### Prompt 2 — fix the recompute-on-update gap

> My `update_task` in `app/storage.py` applies the PATCH fields but doesn't
> recalculate `is_overdue` afterward. Fix only `update_task` so `is_overdue` is
> recomputed from the resulting `due_date` and `status` after the update is applied.

**What AI returned:** a one-line addition recalculating `is_overdue` right before
saving the updated task back into `_tasks`.
**Accepted as-is** — verified with a test that PATCHes only `due_date` on an
existing task and checks `is_overdue` flips to `true`.

### Prompt 3 — the overdue filter

> Add an `overdue: bool | None` query parameter to `GET /tasks` in `app/main.py`,
> passed through to `storage.get_all_tasks`. When `overdue=true`, return only tasks
> where `is_overdue` is true. Don't touch the existing `status`/`priority` filters.

**What AI returned:** matched the spec exactly, reusing the same optional-parameter
pattern already used for `status` and `priority`. **Accepted as-is.**

---

## Feature 2: Tags / labels

### Prompt 1 (weak → strong rewrite)

**Weak version:**
> Add tags to tasks.

**Why it was too weak:** left "list vs comma-separated string" undecided, and had
no validation rule. The AI's first pass (asked with this weak prompt, for comparison)
stored tags as a raw string with no trimming or blank-rejection — a
`"backend, , urgent"` input would have silently stored an empty tag.

**Improved version:**
> Add `tags: list[str] = []` to `TaskCreate` and `TaskResponse`, and
> `tags: Optional[list[str]] = None` to `TaskUpdate`. Add a `field_validator` that
> trims each tag, rejects blank/whitespace-only tags, and caps both tag length
> (30 chars) and tag count (10) per task — following the same validation pattern
> already used for `title`. Do not accept a comma-separated string; the frontend
> will split the string into a list before sending it.

**What I accepted/edited/rejected:** accepted the validator logic. Edited the error
message wording to match the existing `title` validator's style for consistency.

### Prompt 2 — tag filter

> Add a `tag: str | None` query parameter to `GET /tasks`. When present, return only
> tasks where `tag in task.tags`. Reuse the existing filter pattern in
> `get_all_tasks`.

**What AI returned:** correct on the first pass. **Accepted as-is.**

### Prompt 3 — frontend tag input

> In `frontend/index.html`, add a "Tags (comma-separated)" text input to the modal.
> On submit, split the input on commas, trim each piece, and drop empty strings
> before sending the `tags` array to the API. When editing an existing task,
> pre-fill the input by joining `task.tags` with `", "`.

**What AI returned:** matched the spec. **Accepted as-is**, verified manually by
editing a task's tags and confirming the field round-trips correctly (chips on the
card update, and re-opening the modal shows the same tags back in the input).

---

## Post-submission bug fixes (from instructor feedback)

### Prompt — diagnose "editing a task without changing status fails (422)"

> The instructor reports every edit fails with 422 unless status is also changed.
> Trace the actual PATCH request the frontend sends when a user edits only the
> title, and check it against `VALID_TRANSITIONS` in `app/business_rules.py`.

**What AI found:** the submit handler in `frontend/index.html` always included
`status: document.getElementById("field-status").value` in the payload, even when
the dropdown was never touched. Since `VALID_TRANSITIONS` deliberately excludes
same-status pairs, every edit was being read as an (invalid) no-op transition.
**Accepted the diagnosis, rejected the AI's first suggested fix** — which was to
remove the same-status rejection from `VALID_TRANSITIONS` entirely. That would have
weakened backend validation to paper over a frontend bug. Instead asked for a
frontend-only fix: track the task's status when the modal opens, and only include
`status` in the payload if it changed.

### Prompt — diagnose "SyntaxError: Invalid or unexpected token" on load

> Check `frontend/index.html` for anything that could produce a JS parse error on
> load — in particular, any non-ASCII characters embedded directly in string
> literals.

**What AI found:** a raw Unicode en-dash (`–`) character inside a template literal
used as a placeholder for the column count badge. **Accepted the fix**: replaced it
with a plain ASCII hyphen. Verified with `node --check` on the extracted script and
by loading the full page in a headless DOM with no errors thrown.
