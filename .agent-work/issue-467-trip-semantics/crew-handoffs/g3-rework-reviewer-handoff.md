# Reviewer Handoff — g3 REWORK re-review

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree.

## Gate
`g3` — re-review, **scoped to the rework only**.

## Survey State Location

Create your review survey checklist at
`.agent-work/issue-467-trip-semantics/g3-rework-review/review.json` — under the issue workbench,
never at the worktree root. **Use that directory name, not `g3-review/`:** the first g3 review's
survey already lives there, and the two surveys share item ids, so writing into it would overwrite
that run's audit trail.

Your bundled engine was re-installed from this repo and **supports `amend` on surveys**. If a survey
postcondition carries an unresolved placeholder, fill it properly — **do not force-waive**.

## Why this is a narrow re-review

Gate `g3` was implemented, fully reviewed against nine close criteria, and returned **BLOCK with one
blocking finding (B-1)**. **Eight of the nine criteria passed** and were verified by attack — hostile
value sweeps through the real resolver, a four-way anti-vacuity experiment, neighbour isolation
asserted both sides by name, `_PROFILES` byte-identical, exactly one override repo-wide, four
mutations re-run. **Those eight are CLOSED. They are not yours to re-open**, and re-deriving them
would burn the run's context for nothing. The first review is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-reviewer-result.md` — read B-1 and the
criterion-8 section; skim the rest.

## The finding that was reworked

The g3 mutation log declared mutation **M15** an **EQUIVALENT mutant** — that no test could kill it,
because the gate being advanced is always the active gate. That reasoning enumerated `start` and
`advance` but never **`block()`**, which carries no status guard, and `blocked` is not in `TERMINAL`
— so `active_id()` can move **backwards**, behind a later `in-progress` gate. In that state the
no-silent-close rule's band decision must be read for the gate **named in the `advance`**, not for
`active_id()`.

**The shipped source code was and is CORRECT.** The rework is a missing test plus a corrected log
entry, and it contains **no source change**.

## What Was Implemented (the rework)

1. `tests/test_checklist_engine.py` — one new test,
   `GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate`
   (+38 lines), reaching the state through public verbs only
   (`start g1` / `advance g1` / `start g2` / `block g1` / `advance g2 --mechanical`).
2. `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — the M15 entry corrected from
   `EQUIVALENT` to `KILLED`, plus the summary line, with a visible CORRECTION note rather than a
   silent rewrite.

## How to Inspect the Diff

The rework is **uncommitted** in the working tree:

```
git status --porcelain
git diff -- tests .agent-work/issue-467-trip-semantics/g3-mutation-log.md
git diff --stat -- scripts        # must be EMPTY
```

Other modified/untracked `.agent-work/` paths (`execute.json`, its journal, `crew-runs.json`,
`crew-plans/`, `context/`, `mechanical/`, the handoffs) are the Commander's and the implementer's
engine driving — not your review target.

The implementer's own account is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-rework-implementer-result.md`.

## Close Criteria

1. **The new test genuinely kills M15.** Apply the mutation yourself — at
   `scripts/checklist_engine.py:2857-2858`, change
   `require_why=_trip_hard_band_reading(cl, base_dir, getattr(args, "id", None))` to
   `require_why=_trip_hard_band_reading(cl, base_dir)` — run the test, observe RED, then **revert
   and confirm `git diff --stat -- scripts` is empty again**. Paste both runs.
2. **The test is not vacuous.** It must reach the divergent state for the stated reason, not pass by
   accident. Specifically: does it assert the *refusal* rather than merely that nothing crashed; is
   the gauge reading actually live in the assertion window; would it still pass if the fixture never
   reached `active_id != gate being closed`? The standing trap on this run is a test that passes for
   the wrong reason.
3. **The state is reached through PUBLIC verbs**, not by hand-mutating checklist JSON into a shape
   the engine would never produce. A manufactured-unreachable fixture would make the kill hollow —
   that was the original declaration's own defence.
4. **No source change.** `git diff --stat -- scripts` empty.
5. **The M15 log correction is honest**: it states the kill, names the test, gives the failure
   count, and **visibly records that the earlier `EQUIVALENT` declaration was wrong** — including
   that `f9925be6`'s commit message asserted it. A quiet rewrite that reads as though the entry
   always said this would be a finding.
6. **The two closeout suites pass:**
   - `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py` — expect **572 passed, 535 subtests** (was 571 before the rework; +1 is the new test).
   - `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'` — expect **21 passed, 413 deselected, 125 subtests** (was 20; +1).

## Specific Exclusions — flag if touched

- **Anything under `scripts/`.** The rework was told not to, explicitly.
- **`block()`'s missing status guard, and `blocked`'s absence from `TERMINAL`.** Pre-existing, out of
  scope, already filed as an observation by the first review. It is also the state the new test
  depends on. If the rework "fixed" it, that is a scope violation, not an improvement.
- The eight passing criteria from the first review, and the other fifteen mutations.
- `decision:execute-gate-reserve-value` being `@grade: guess` — settled, already routed to the
  Admiral. Not a blocker.

## What the Commander already verified in its own shell

Stated so you can corroborate or contradict it, not so you can skip it:

- The B-1 reproduction, at the CLI with public verbs, shipped engine **refuses**
  `advance g2 --mechanical` / M15 mutant prints `g2 -> complete` on the identical fixture.
- The new test: **GREEN on shipped** (1 passed), **RED under the M15 mutation** (1 failed), scripts
  reverted clean.
- Both closeout suites: 572 passed / 535 subtests, and 21 passed / 125 subtests.

If any of that does not reproduce for you, **say so** — a contradiction is the most valuable thing
you can return.

## Suggested Model Tier

**Stronger (Opus).** Named reason: adversarial review — the job is to attack the claim that the kill
is real rather than to confirm a spec was followed. The standing default for this run is Sonnet.

## Stop Conditions

Stop and return `BLOCK` if: the diff cannot be accessed, evidence is absent or unverifiable, or a
policy decision is required before a verdict is possible.

**Do not modify `scripts/` or `tests/` yourself** beyond applying and reverting the M15 mutation for
criterion 1. Leave `execute.json`, `spine.json` and `STATE_NOTE.md` alone — the Commander holds
their lease.

## Return Format

Return REVIEW_RESULT. **Your verdict must be exactly `APPROVE` or `BLOCK`**, on the **first line**,
with the reasoning under it. No other verdict vocabulary — the engine matches that literal string.

`APPROVE` means **zero blocking findings**. Non-blocking findings alongside an APPROVE are welcome.
One blocking finding means `BLOCK`.

Also state, on its own line, **`blocking_findings: <N>`**.

Include: per-criterion findings (classified blocking / non-blocking), your own mutation run with
pasted RED and the reverted-clean proof, your suite runs, anything you could not verify and why,
out-of-scope observations, and workflow feedback.

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-rework-reviewer-result.md`.

**Deliver your REVIEW_RESULT via `SendMessage` to `commander-w4-467-f` before ending your turn.**
