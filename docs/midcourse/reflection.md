# Reflection

For this Mid-Course Project I used an AI chat assistant (Claude) as my primary coding
tool for both features, working the same way the course teaches: one scoped prompt
per change, inspect the output, run the app or tests, and correct before moving on.
I used it to draft the Pydantic model changes, the storage-layer logic, the new
route parameters, the pytest tests, and the frontend markup/JS for the due-date and
tag UI.

The AI helped most on repetitive, pattern-matched work. Once I pointed it at the
existing `title` field's `field_validator` pattern in `app/models.py`, it correctly
reused that same shape for the new `tags` validator (trim, reject blank, cap length)
without me having to spell out every line. It also correctly generated the
`overdue`/`tag` query parameters in `GET /tasks` by mirroring the existing
`status`/`priority` filter pattern already in the file — that consistency would have
taken me longer to enforce by hand.

The AI slowed me down once, in a way worth recording: my first (weak) prompt for
"add due dates" produced an `is_overdue` calculation that only checked
`due_date < today` and ignored task status entirely. On the surface it looked
correct — it passed a quick eyeball check — but it meant a task I'd already finished
late would stay flagged "Overdue" forever, which isn't the behavior anyone actually
wants from a task tracker. I only caught this by writing a specific test for it
(`test_done_task_with_past_due_date_is_not_overdue`) before trusting the feature,
which is exactly the "review, don't assume" habit the module keeps emphasizing.

The place my review changed the result most was the Break Test step. Both new
features initially looked done once the happy-path tests were green. Deliberately
breaking `_compute_overdue` and the blank-tag check, one at a time, and confirming
the right tests failed for the right reason, is what actually proved the tests were
meaningful rather than just present. Without that step I would have had no evidence
that my tests protected anything real — they could have been checking the wrong
thing and I wouldn't have known until a real bug shipped.

Overall the workflow held up: AI accelerated the boilerplate and pattern-reuse, but
the validation logic that actually mattered (the Done-task exemption, the blank-tag
rejection) only became trustworthy once I forced it through tests and a real
break-and-restore cycle instead of taking the first green run at face value.
