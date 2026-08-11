# My AI Playbook

## When I reach for AI first

- **Boilerplate that follows an existing pattern in the repo** — a new Pydantic
  field/validator shaped like an existing one, a new query filter shaped like
  `status`/`priority`, a new pytest test shaped like the ones already in
  `test_tasks.py`. AI is fast and reliable here because there's a concrete
  precedent to copy, not a decision to make from scratch.
- **First-pass debugging from evidence.** When I have an actual failing
  request/response or a real traceback, handing that to AI and asking "what's the
  root cause" is faster than me reading every line myself first — as long as I then
  verify the diagnosis against the real code before trusting it.
- **Drafting documentation from facts I already have.** Turning verified test
  results, curl output, and decisions I already made into a written doc is exactly
  the kind of transcription task AI is good at and I find tedious.

## When I do not reach for AI first

- **Business-rule decisions with real consequences**, like what counts as a valid
  status transition or whether a `Done` task can be "overdue." These need my
  judgment about what the product should actually do, not AI's best guess at what's
  typical.
- **When I don't have a reproduction yet.** If I only have a vague symptom ("it
  doesn't work"), I reproduce it myself first — a specific curl command, a specific
  failing test — before asking AI to diagnose it. Otherwise I'm asking it to guess.
- **Anything touching validation or security logic that's already tested and
  working.** If AI suggests loosening a rule to make a bug "go away" (this actually
  happened — see `docs/final-ai-review.md`), that's exactly the moment to slow down
  and check whether it's fixing the real problem or just hiding it.

## My non-negotiables

- Never paste real secrets, `.env` values, tokens, or real personal/customer data
  into an AI tool — this project has none, and any future one won't either.
- Never accept a fix I haven't verified against a real reproduction (a failing
  test, a real request, a real running app) — "looks right" is not verification.
- Never let an AI suggestion touch tested business logic (like
  `VALID_TRANSITIONS`) to paper over a bug that's actually somewhere else.
- Never submit a change I can't explain in my own words, including exactly why
  it's correct.

## My review rules

- I read the actual diff, not just the AI's summary of it.
- For anything backend, I run the test suite before and after, and for any new
  logic I write a specific test rather than trusting the happy-path result.
- For anything that claims to fix a bug, I reproduce the bug first (a specific
  failing command or request), then confirm the fix flips that exact result —
  same-status PATCH returning 422 → 200, blank-tag rejected → accepted → rejected
  again after restoring, etc.
- I grade AI output honestly using categories (Useful/Noise/Wrong, or
  Valid/False Positive/Noise for security) instead of a blanket "accepted" —
  most AI suggestions I get are a mix, and pretending otherwise defeats the point
  of reviewing at all.

## What I am still figuring out

- How to scale this review discipline once changes get bigger than a single
  function — reading every line closely works at this project's size, but I don't
  yet have a good process for reviewing a much larger AI-generated diff without it
  turning into a rubber stamp.
- Where the line is between "AI suggestion I should push back on" and "AI
  suggestion that's actually right and I'm just being stubborn" — I don't have a
  reliable gut check for this yet beyond "can I articulate a concrete reason," which
  sometimes takes longer than it should.
- How much dependency-version pinning is actually worth the maintenance overhead
  for a project this small — I flagged it as a real finding in
  `docs/final-ai-review.md` but deliberately didn't fix it, and I'm not fully sure
  that was the right call.

## Decision Card

| Situation | My rule |
|---|---|
| **New feature** | Write the user story and acceptance criteria myself first, in my own words, before asking AI to implement anything — if I can't state what "done" looks like, AI can't either. |
| **Code review** | Grade every AI review comment Useful/Noise/Wrong with a one-line reason — never just "applied" or "ignored" without saying why. |
| **Debugging** | Reproduce the exact failure myself (specific command, specific test, specific status code) before asking AI to diagnose it — never start from "it's broken." |
| **Infrastructure** (CI/Docker/config) | Verify with a real run wherever possible; if I can't run it myself (e.g. no Docker in this environment), say so explicitly in the docs instead of writing it up as if it were tested. |
| **Never paste** | Real secrets, `.env` values, tokens, credentials, or real personal/customer data — no exceptions, no "just this once." |
| **One rule that covers all of it** | If I can't explain why a line, command, or config choice is correct, it doesn't go in as final work — full stop. |
