# Issue #129 continuation — clean round-2 wording measurement

## Mission (frozen launch order)
Produce the clean terminal-completion measurement rounds 1–2 never got. Metric = SUBJECT
spine driven to terminal `archive` with genuine engine provenance (lease + journal) +
`work-complete.txt`. Target >=2/3 terminal. Iterate completion-side wording only if short.
HARD CONSTRAINT: eval task.md carries zero test-awareness / workflow coaching (untouchable).

## Reap-safe drive pattern (PR #132/#135)
- run-0 (fresh): `py scripts/run_skill_eval.py evals/euler-1-multiples --worktree C:/Programs/constellation-wt-129 --keep-temp --max-new-runs 1 --json`
  -> prints "kept temp dir: <PATH>" on stderr. Launches ONE subject, blocks until it
  finalizes (<=2400s), exits. Run in BACKGROUND (single run fits under ~60min reap).
- resume: `... --resume <PATH> --worktree C:/Programs/constellation-wt-129 --max-new-runs 1 --json`
  adjudicates any orphan, launches ONE remaining subject.
- Repeat until 3 runs complete; final resume prints the verdict.
- If a meta sticks at "launched" past deadline: `--resume` orphan adjudication records
  inconclusive/fenced + tree-kills recorded pid (live-proven).

## Grading instrument (FROZEN — float if I find a bug, do not edit)
Three gating checks (checks/*.py top-level; answer/ is advisory only):
1. spine_completed.py — terminal gated shape (all tasks complete) + engine_session lease
   (monotonic claim<=heartbeat<=release) + engine evidence grammar (e-<task>-<n>, engine
   command-output present, satisfied engine checks backed by engine evidence) + journal
   cross-verify (hash-chain intact, seq 1..N, monotonic ts in lease window, every complete
   task has advance/record entry, satisfied-check evidence journal-referenced).
   GRANDFATHER: no-journal spine still passes on lease+grammar. MY subjects run journal-
   emitting engine, so a terminal pass MUST carry a consistent journal.
2. artifact_present.py — non-empty solution.py in workspace (NO sentinel fallback).
3. tests_green.py — pytest green over workspace test files.

Verdict mapping (run_skill_eval.py):
- completed-pass: all checks green (or timeout carve-out: timed-out run whose workspace
  passes ALL checks = PASS; timeout with any failing check = fenced/inconclusive).
- completed-fail: ran to exit but a check fails.
- inconclusive (fenced): timeout-with-failing-check, orphaned-runner-died, infra death.
  Fenced runs EXCLUDED from denominator.
- N-of-M 2-of-3; process-checks-carry-verdict.

## Terminal-completion = the metric
Engine ENTRY was solved round 1 (3/3). Do NOT report entry as success. Only a spine driven
to terminal archive (all 3 checks green incl. consistent journal) + work-complete.txt counts.

## Wording strategies
- Strategy 1: round-2 as shipped (SKILL.md line 17 "solution is the MIDDLE, not the end").
  NO changes to worktree — measuring main as-is.
- Strategy 2+: authored only if strategy 1 < 2/3. Completion-side wording only, in
  skills/commander-delegated/SKILL.md and/or evals/*/fixture/CLAUDE.md. task.md untouchable.

## Honest-null
If sonnet stays < 2/3 across >=3 genuinely distinct strategies, the documented tier
boundary posted on #129 IS the complete successful deliverable.

## Round log
- R2/strategy-1 run-0: LAUNCHED (bg brn7izd0k), temp dir TBD.

## Round log (updated)
- R2 subject A (run-0, 6lcnbis9): completed-fail, NEAR-TERMINAL release-ordering fail.
  All 10 steps complete, artifact+tests+work-complete.txt PASS, journal sound; only
  spine_completed fails on "journal entry after lease release". #129 off-ramp CLOSED.
  See RUN0_CLASSIFICATION.md.
- R2 subject B (g6o67i9t): LAUNCHED concurrently, monitor watching deadline.
- R2 subject C (iricdfpb): LAUNCHED concurrently, monitor watching deadline.

## Watch-failure note (for report)
Background-task completion notification for run-0 arrived ~2h LATE (fired at wake time,
not at the 09:39 process exit). The single-completion-signal watch is unreliable here.
Fix applied: an independent wall-clock Monitor polling each subject's meta.json against
launched_at+timeout_seconds(+grace); wakes on FINALIZED or DEADLINE-EXCEEDED.

## Round 3 (D/E) — combined ordering fix, FIRST attempt (both died upstream at execute)
- D (ir02q8l0): completed-fail, 4/10 (execute in-progress), 631s. Final line "The crew
  dispatch is running in the background. I'll wait for it to complete." => dispatched crew
  then ENDED ITS TURN to wait => headless process death. NEW SHADE: wait-by-ending-turn.
- E (rwtnxyih): completed-fail, 4/10 (execute in-progress), 601s. Final line "...Implementation
  complete." => quit-early recurrence (implementation-complete != run-complete).
- Neither reached archive => release-ordering fix UNMEASURED by D/E. High run-to-run variance
  (round-2 A/B reached 10/10; round-3 D/E died at 4/10, same base wording).

## WATCH ROOT CAUSE (confirmed)
My Monitor fired FINALIZED + BOTH-DONE correctly, but delivery was suspended ~8h until an
external message woke my session. Notifications in this env do NOT reliably wake an idle
session. FIX: never go idle — poll actively in bounded foreground loops within my turn.

## Round 3-continued: added wait-loop clause (SKILL.md step 5). Runs G/H/I, active-polled.

## Round 3-continued (G/H/I) — combined fix (ordering + wait-loop), active-polled
- G (4yqedpsu): completed-pass, 10/10, lease released, journal consistent (52 entries), sentinel. TERMINAL.
- H (h3bten13): completed-pass, 10/10, lease released, journal consistent (50 entries), sentinel. TERMINAL.
  Both PASS the strict spine_completed incl. release-window => release-after-final-advance worked.
- I: launched, active-polling.
=> 2/2 terminal so far; combined ordering fix VALIDATED against the unchanged strict instrument.

## FINAL — round-3-continued 3/3 terminal
- I (d4clr3hp): completed-pass, 10/10, lease released, journal 50 entries, post-release=[]
  (advance archive @04:24:35 THEN release @04:24:42). TERMINAL.
- Round-3b G/H/I = 3/3 TERMINAL. Combined ordering+wait-loop fix validated vs unchanged instrument.
- Committed 1e015d8, pushed, PR #137, #129 comment posted.
- Pre-commit: provenance 27 passed; 168 template-consuming tests passed.
