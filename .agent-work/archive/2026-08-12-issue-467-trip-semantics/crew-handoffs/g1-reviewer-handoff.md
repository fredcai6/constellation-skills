# Reviewer Handoff

*Authored by `commander-w4-467-b` at the g1 seam, before handing off. Dispatch this as-is.*

## Gate
`g1-review` — of `.agent-work/issue-467-trip-semantics/execute.json` (issue #467, epic #418 wave 4).

## What was built

`g1-implement` produced a **disposable reproduction of issue #431's deadlock at unmodified HEAD**.

- Implementer's result: `.agent-work/issue-467-trip-semantics/crew-handoffs/g1-implementer-result.md`
- Its handoff (the spec it was held to): `.agent-work/issue-467-trip-semantics/crew-handoffs/g1-implementer-handoff.md`
- The repro itself: `.agent-work/issue-467-trip-semantics/red-repro/repro_431.py`
  (`--all` | `--face a` | `--face b` | `--assert-gauge-read`)
- Claimed: 24 `ASSERT OK`, 0 `ASSERT FAIL`, real exit 0; rebuilds its scratch root from nothing.

## The review question

**Not "does the repro run."** It runs. The question is **"is this RED genuine, and does it reproduce
#431 rather than something adjacent?"**

This matters more here than in an ordinary gate. Epic #418's central defect — the thing every wave
has been about — is **a check that cannot fail**. A manufactured RED is that defect wearing the
costume of evidence: it goes green after the fix and everyone concludes the fix worked. Cold critic
finding R1 kept this gate in the plan *specifically* so an independent reader would ask this
question. You are that reader. **Your job is to try to break the claim, not to confirm it.**

Answer these four, each with the evidence you personally reproduced:

1. **Was a fresh, valid reading actually READ?** Not "a gauge file existed" — *read*. #467's rule is
   "no absence is evidence": a silent governor and a governor with headroom are indistinguishable,
   and an absent or stale gauge makes the reader return `None`, which no-ops the whole band. Find the
   place in the output where the engine itself proves it read the number (its own
   `CONTEXT <n>% (>= hard)` line). Then check the planted record would actually survive
   `gauge_reader.read()`: four required fields, a calibrated model, and an `observed_at` inside the
   30-minute staleness window and not more than 2 minutes in the future.
2. **Is the stale DIGEST the real consequence of the shipped instruction, or was the repro arranged
   to produce it?** This is the crux. The implementer claims a counterfactual control — the same
   spine with no gauge advances the same gate and yields the *fresh* DIGEST. Verify that control
   exists and that it differs from the trip run **only** in the gauge. If the two runs differ in any
   other way, the staleness is not attributable to the refusal and the RED is not genuine.
3. **Would this repro go GREEN under the planned fix, and RED again if the fix were reverted?** The
   planned fix moves HARD's enforcement from `advance` to the verbs that *begin* work (`start`,
   `reopen`), so the tripped agent's `advance --why` completes and the DIGEST lands. Reason it
   through against the repro's actual assertions and say whether each one flips. An assertion that
   would pass on **both** sides of the fix is proving something other than #431 — name it if you find
   one.
4. **Is `git diff --stat -- scripts tests` empty?** Run it yourself. The RED must be observable at
   the *unmodified* HEAD; any source change under `scripts/` or `tests/` voids the gate.

## Scope limits you must hold the result to

The implementer volunteered a scope limit on Face B and asserted it in the script: `current` **does**
still list `c2 [unmet]` at HARD, so the masking is scoped to the `advance` **refusal path**, not to
the whole engine. Confirm the result does not claim wider than that anywhere. Honest narrow claims
are the standard here; a result that overclaims is a finding.

## What is NOT in scope for you

- Do not propose or evaluate the fix. Gates g2–g4 own it.
- Do not ask for the repro to become a regression test. #467 rules it disposable — the deadlock is a
  property of the refusal path being deleted, so it is unreproducible by construction afterwards.
  **Recommending its promotion is a wrong answer, not a nice-to-have.**
- Do not modify anything under `scripts/` or `tests/`. Do not write under
  `.agent-work/epic-418-redux/**` (the Admiral's). Do not touch `.claude/settings.json` (#458).
- Do not modify the live `.agent-work/issue-467-trip-semantics/spine.json` or `gauge.json` — a
  Commander run depends on both.

## Constraints

- Never use `py` to run pytest (#454 — false `HARNESS ERROR`). Use
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
- A piped command's `$?` is the **pipe's** exit code. Redirect to a file and read it separately, or
  use `${PIPESTATUS[0]}`. This has already produced one false "verified" in this epic.

## Required Evidence

Every one of the four questions answered with a command you ran and its literal output. A verdict
with no reproduction is not a review.

## Verdict

One of `ACCEPT` / `ACCEPT WITH FINDINGS` / `REJECT`, on the **first line** of your result, with the
reasoning under it. `ACCEPT WITH FINDINGS` is the normal healthy outcome; a bare `ACCEPT` on a gate
whose whole purpose is adversarial reading will itself be read as a check that could not fail.

## Return Format

Write `REVIEW_RESULT` to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g1-reviewer-result.md`, beginning with a line
reading exactly `# REVIEW_RESULT` and with the verdict on the line after it. Include: the four
answers with evidence, findings (each classified blocking / non-blocking), anything you could not
verify and why, and workflow feedback.

## Suggested Model Tier

`stronger` — distinguishing a genuine RED from a manufactured one requires reading the engine's HARD
*release* path, not just its refusal path.
