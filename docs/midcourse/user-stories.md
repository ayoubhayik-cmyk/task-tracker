# User Stories

## Feature 1: Due dates + overdue filter

**Story 1 — Set a due date when creating a task**
As a user, I want to set an optional due date when I create a task, so I know when it's supposed to be finished.
*Acceptance criteria:*
- The create modal has an optional "Due date" field.
- Submitting without a due date still succeeds (it's optional).
- An invalid date value is rejected by the backend with a 422.

**Story 2 — See which tasks are overdue at a glance**
As a user, I want overdue tasks to be visually flagged on their card, so I don't have to check each due date manually.
*Acceptance criteria:*
- A task with a due date in the past shows a red "Overdue" chip on its card.
- A task without a due date shows no chip.

**Story 3 — A finished task is never "overdue"**
As a user, I don't want a task I already finished late to still be flagged as overdue, since that's misleading noise.
*Acceptance criteria:*
- A task with `status: Done` never shows as overdue, even if its due date is in the past.
- **AI assumption corrected:** the first version I asked for computed `is_overdue` purely from `due_date < today`. I had to explicitly add the rule that `Done` tasks are excluded — the AI's first draft would have shown a completed task as permanently overdue.

**Story 4 — Update a task's due date**
As a user, I want to change a task's due date after creating it, so I can push back deadlines.
*Acceptance criteria:*
- `PATCH` accepts a `due_date` field and updates it.
- The `is_overdue` flag is recomputed immediately after the update, not left stale.

**Story 5 — Filter the board to overdue tasks only**
As a user, I want to filter the board to show only overdue tasks, so I can triage what's late first.
*Acceptance criteria:*
- An "Overdue only" checkbox above the board filters the visible cards.
- `GET /tasks?overdue=true` returns only tasks where `is_overdue` is true.

## Feature 2: Tags / labels

**Story 1 — Add tags when creating a task**
As a user, I want to add one or more tags to a task, so I can categorize work by area or type.
*Acceptance criteria:*
- The create modal has a "Tags" field accepting comma-separated values.
- Tags are trimmed and stored as a clean list (no leading/trailing whitespace).

**Story 2 — Blank tags are rejected**
As a user, I expect the system to reject a tag that's just whitespace, so my tag list doesn't fill up with junk entries.
*Acceptance criteria:*
- Submitting a tag that is empty or only spaces returns a 422.
- **AI assumption corrected:** the AI's first draft only trimmed tags for display, it didn't validate them on the way in. I had to explicitly ask for a `field_validator` that raises on blank tags, matching the same pattern already used for `title`.

**Story 3 — See tags on the board**
As a user, I want to see a task's tags directly on its card, so I don't have to open the edit modal to know what it's tagged with.
*Acceptance criteria:*
- Each tag renders as a small chip on the card.
- A task with no tags shows no chips (no empty/placeholder chip).

**Story 4 — Update a task's tags**
As a user, I want to add, remove, or change a task's tags after creating it.
*Acceptance criteria:*
- `PATCH` accepts a `tags` field and replaces the tag list.
- Tags are preserved if a `PATCH` request doesn't include the `tags` field at all (partial update).

**Story 5 — Filter the board by tag**
As a user, I want to filter tasks by a specific tag, so I can focus on one category of work.
*Acceptance criteria:*
- A text filter above the board filters cards by tag.
- `GET /tasks?tag=backend` returns only tasks that include that tag.
