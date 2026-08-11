# Mini ADR — Due Dates + Overdue Filter, and Tags/Labels

## Context

The Task Tracker needed two small, end-to-end features on top of the Module 1-3
baseline: due dates with overdue detection, and tags/labels. Both had to be usable
from the Kanban UI, backed by real validation, and covered by tests.

## Decision: Due dates + overdue

- `due_date` is stored as an optional `date` (not `datetime`) on the task, since the
  UI only needs day-level granularity and a plain `<input type="date">` maps directly
  to it.
- `is_overdue` is **computed and stored on the `TaskResponse`**, not computed live in
  the frontend. This was a deliberate choice over the alternative the brief allowed
  (computing overdue in the UI): computing it in the backend means the same rule
  (`due_date < today AND status != Done`) is enforced once, and the `overdue=true`
  query filter can reuse it directly instead of duplicating the logic in JavaScript.
- `is_overdue` is recalculated on every `PATCH`, not just on create, because either
  `due_date` or `status` can change independently and both affect the result.

**Alternative considered and rejected:** computing "overdue" purely on the frontend
by comparing `due_date` to `new Date()` at render time. Rejected because it would
have made the `overdue` query filter impossible to implement server-side, and it
would have required duplicating the "Done tasks are never overdue" rule in two
places (backend filter and frontend display) — a maintenance risk for a one-line rule.

## Decision: Tags / labels

- Tags are stored as `list[str]`, not a comma-separated string, matching the format
  the brief describes as acceptable ("tags as a list or normalized
  comma-separated field"). A list keeps filtering (`tag in task.tags`) simple and
  avoids re-parsing a string on every read.
- Validation (trim, reject blank, cap length/count) lives in the same
  `field_validator` pattern already used for `title`, reusing the existing
  convention rather than inventing a new validation style.
- The frontend still accepts a single comma-separated text input for tags (simpler
  UI than a tag-chip input widget) and splits/trims it client-side before sending
  the list to the API. The backend re-validates regardless, so a malformed request
  from any client is still caught server-side.

**Alternative considered and rejected:** a dedicated `Tag` model with its own id and
a many-to-many relationship. Rejected as out of scope — the brief explicitly flags
this kind of schema expansion as the sort of thing that "can become large quickly,"
and a plain string list satisfies every required test case (create, reject-blank,
update, filter, preserve-after-unrelated-update) without it.

## What was rejected as out of scope

- Timezone-aware due dates / due-time-of-day — the brief only asks for date-level
  overdue detection.
- A tag autocomplete or a persisted "known tags" list — pure UI polish, not required
  by any acceptance criterion.
- Combining the overdue and tag filters with status/priority filters in one combined
  query builder UI — that's the scope of the separate "Search + combined filters"
  feature option, which was not selected for this submission.
