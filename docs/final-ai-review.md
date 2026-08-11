# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

## AI code review mini-log

Reviewed file: `frontend/index.html`, specifically the `task-form` submit handler,
which was the site of the post-submission "editing a task without changing status
fails (422)" bug fix.

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| "The submit handler always sends `status` in the PATCH body, even when the dropdown was never touched. Since the backend rejects same-status transitions, every non-status edit will 422." | **Useful** | This was the actual, confirmed root cause of the reported bug. | Reproduced with curl (unchanged status → 422) and by driving the real submit flow in a headless DOM (payload correctly omitted `status` after the fix). Accepted. |
| "Consider removing the same-status entries from `VALID_TRANSITIONS`'s exclusion so any status value is always accepted, which would also fix this." | **Wrong** | This "fix" would have silently changed backend business-rule behavior (Part 2.3's intentional same-status rejection) to paper over a frontend bug. It solves the symptom by weakening validation, not by fixing the actual defect. | Rejected. Fixed the frontend instead: only include `status` in the payload when it actually changed. `app/business_rules.py` was not touched. |
| "`renderMetaChips` duplicates the `escapeHtml` call pattern already used in `renderCard`; consider extracting a shared `renderChip(text, className)` helper." | **Noise** | True but not relevant to correctness, and it doesn't touch the reported bug or any real risk. Restructuring working, tested rendering code post-submission adds review surface for no functional benefit. | Rejected for this branch — noted as a low-priority style idea, not applied. Matches the "no new product features / minimal touch" rule in `AGENTS.md`. |
| "The `field-tags` input trims each tag but doesn't cap the number of tags client-side before sending, unlike the backend's `MAX_TAGS` limit." | **Useful** | Accurate observation — the frontend has no client-side tag-count limit, so a user could type 20 tags and only find out via a 422 after submitting. | Verified by reading `app/models.py` (`MAX_TAGS = 10` is backend-only) and `frontend/index.html` (no matching client check). Not fixed on this branch — it's a UX polish item, not a bug or security issue, and is out of scope for "no new product features." Logged here instead of silently ignored. |

## AI security mini-review

Read-only review of `app/main.py`, `app/models.py`, `requirements.txt`, `Dockerfile`,
and the repository tree, run for real against this repo (not a generic checklist).

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| Docker image installed test-only dependencies (`pytest`, `httpx`) into the production runtime image via `COPY requirements.txt` + full install. | `Dockerfile` (before fix), `requirements.txt` | **Valid** | Test tooling has no reason to ship in a production container — it increases image size and unnecessary attack surface for no benefit. | **Fixed.** Added `requirements-docker.txt` with only runtime deps (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`) and pointed the `Dockerfile` at it instead. Verified the app still imports and serves `/health` → 200 using only that lean dependency set. |
| `CORSMiddleware` uses `allow_credentials=True` together with `allow_methods=["*"]` and `allow_headers=["*"]`. | `app/main.py` | **False Positive** | This pattern is dangerous only when combined with a wildcard `allow_origins=["*"]`, which browsers actually reject alongside `allow_credentials=True` anyway. Here `allow_origins` is an explicit, small list of local dev origins (`localhost:5500`, `127.0.0.1:5500`, etc.) — not a wildcard — so credentialed requests are still restricted to those named origins only. | None needed. Documented here so a future reviewer doesn't have to re-derive this. |
| Dependency versions in `requirements.txt`/`requirements-docker.txt` use `>=` lower bounds instead of exact pins (e.g. `fastapi>=0.110`). | `requirements.txt`, `requirements-docker.txt` | **Valid** (noted, not fixed) | Unpinned lower bounds mean a future `pip install` could pull in a newer, untested major version, which is a real reproducibility/supply-chain risk for a "teammate-maintainable release." | **Not fixed on this branch.** Pinning exact versions is a reasonable follow-up, but doing it correctly requires actually testing against the pinned versions, which is beyond this pass. Recorded here rather than silently pinned without verification. |
| No rate limiting or request-size limit on `POST /tasks` / `PATCH /tasks/{id}`. | `app/main.py` | **Noise** (for this project's scope) | This is a real production concern in general, but this app has no database, no auth, and is explicitly an in-memory learning project not intended for public deployment. Flagging it as an actionable finding here would be checklist-following, not judgment. | None. Noted only to show it was considered, not missed. |

## Manual security check

I manually ran `find . -iname "*.env*"` and a case-insensitive `grep` across
`app/*.py`, `frontend/index.html`, `README.md`, and `AGENTS.md` for the terms
`api_key`, `secret`, `password`, `token`, and `credential` — independent of any
AI-generated finding, specifically to satisfy the "no real secrets... in the repo"
submission requirement myself rather than trusting an AI summary of it. Result: no
`.env`-pattern files exist anywhere in the repo, and the only match for those terms
was the FastAPI `allow_credentials=True` CORS setting (a config flag name, not a
secret value) and this file's own guardrail text in `AGENTS.md`. No real secrets,
tokens, or credentials are present.

## One AI output I rejected or corrected

Described in the code review log above, but restated here as the flagship example:
during the post-submission bug fix, the AI's first suggested fix for "editing a task
without changing status fails" was to remove same-status pairs from the *rejected*
side of `VALID_TRANSITIONS` (i.e., make the backend accept a same-status PATCH as
valid). I rejected this because it would have quietly reversed a deliberate,
already-tested business rule from Module 2 (Part 2.3) — same-status "transitions"
are intentionally invalid, not an oversight — purely to make a frontend bug stop
surfacing. I asked for a frontend-only fix instead: track the task's status when the
edit modal opens, and only include `status` in the PATCH payload if it actually
changed. This kept the backend's validation logic completely untouched (all 28
existing tests still pass unmodified) and fixed the real defect at its source.

## Three AI usage rules

1. **Never paste:** real `.env` values, API keys, tokens, production database
   contents, or any real user/customer data into an AI tool — this app has none of
   those to begin with, and it stays that way.
2. **Always verify:** any AI-suggested fix against a reproduction of the actual
   reported behavior (a failing curl request, a failing test, or a real DOM/browser
   run) before trusting it — never accept a fix because it "looks right."
3. **Record AI contributions by:** keeping a real prompt log (`docs/midcourse/prompt-log.md`)
   and a real review log (this file) that name the actual file, the actual AI
   suggestion, and an explicit Useful/Noise/Wrong or Valid/False Positive/Noise
   grade with a reason — not a vague "AI helped with X" summary.

## Ownership statement

I'm comfortable submitting this repo as my own work because every claim in these
docs is backed by something I actually ran: real curl output, real pytest runs (28
passing, with two Break Tests that proved the tests fail when the code they protect
is broken), a real headless-DOM reproduction of the status-omission bug fix, and a
real dependency-set verification for the Docker image (proven to serve `/health`
with only the runtime-only requirements file, before ever touching real Docker). I
rejected the one AI suggestion that would have weakened tested backend behavior to
mask a frontend bug, and I fixed the actual defect instead. Where I found a real
issue myself during the security pass (test dependencies leaking into the
production image), I fixed it and verified the fix rather than just logging it. I
did not accept any change I couldn't explain, and the two things I deliberately
left unfixed (unpinned dependency versions, no client-side tag-count limit) are
recorded here as conscious scope decisions, not oversights.
