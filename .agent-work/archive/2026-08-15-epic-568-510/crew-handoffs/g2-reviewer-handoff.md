# Reviewer handoff — `epic-568-510` g2-engine (independent falsifier)

**Worktree (work ONLY here, absolute):** `/home/tommy/projects/constellation-skills/.worktrees/epic-568-510`
**Branch:** `epic-568/510-hard-advisory` · **Base commit:** `23ed6b70`
**Your role:** independent falsifier. Try to BREAK the claims below. A refutation is a
success, not a failure. Do not fix anything; report.

## What was changed and why

A human ruled (via the Admiral's frozen launch order) that the ENGINE must change so that
the `start` its HARD advisory instructs is not punished — the advisory's wording must NOT
be narrowed to resolve the contradiction.

The contradiction: at a PENDING gate (`advance` is refused on a pending gate, so the only
way an over-the-line agent can leave a handoff AT that gate is `start` then
`advance --why`), `_trip_advisory`'s HARD branch instructs "request the refresh, then
begin THIS guarded gate (`start g`), then close it carrying your handoff". Obeying that
recorded a `begin-released` trip-ledger entry, and the very next `current` rendered
"TRIP LEDGER / TRIP HISTORY: N begin(s) at/over the hard line are on the record" — the
engine's own compliance signal branded the agent for obeying the engine.

**The change** (one branch, in `scripts/checklist_engine.py`, `_trip_hard_gate`, the sole
ledger write site): when `verb == "start"` AND the target is `active_id(cl)` AND that gate's
status is `pending` — exactly the state the "Now begin THIS guarded gate" advisory is
rendered from — the entry is appended with outcome `begin-instructed` instead of
`begin-released`. The two compliance selectors were NOT touched: they already ignore any
outcome outside `("begin-refused","begin-released")`.

## Claims to falsify

1. **The engine change is confined to that one branch.** `git diff` on
   `scripts/checklist_engine.py` should show the new branch plus docstring updates and
   nothing else. No change to `advance` semantics, gate lifecycle, or production defaults.
2. **No test was deleted, skipped, loosened, or converted to a weaker assertion kind.**
   Five existing tests were RE-AIMED (their expectations changed because the behavior they
   pinned was the ruled-away behavior). Verify each still pins its original guarantee at the
   same assertion strength — every whole-string `assertEqual` must still be a whole-string
   `assertEqual`. Run an assertion-kind census over `tests/test_checklist_engine.py` before
   (at `23ed6b70`) and after, and report the deltas.
   The five: `test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line`,
   `test_ledger_begin_released_is_recorded_through_the_cli`,
   `test_ledger_is_append_only_across_repeated_begins`,
   `test_compliance_line_also_rides_the_already_requested_hard_advisory`,
   `test_compliance_line_names_the_count_and_the_latest_begin`.
   Plus one re-pin of the deliberately-failing
   `test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it`.
3. **The exemption is NARROW.** Try to find a way to get an over-the-line begin recorded as
   `begin-instructed` when the HARD advisory did NOT instruct it. Specifically probe:
   `reopen`; a `start` with no keyed refresh-request; a `start` aimed at a non-active gate;
   a `start` at an in-progress or blocked gate; a survey checklist; a `why_exempt` gate
   (live why id `None`); a stale/absent gauge reading.
4. **`begin-released` is still reachable and still branded.** Confirm the compliance signal
   still fires for genuinely self-chosen over-the-line begins.
5. **The red/green is real.** `git stash` ONLY the `scripts/checklist_engine.py` change and
   confirm the new class `TripInstructedBeginIsNotAnOffence` fails; restore and confirm it
   passes. Confirm the new tests fail for the RIGHT reason (not an import or fixture error).
6. **Nothing else in the repo depends on the old semantics.** Grep the whole worktree for
   `begin-released` / `begin-refused` / `trip_ledger` and report anything that is now stale.
   NOTE: `docs/CHECKLIST_SCHEMA.md` documents the outcome vocabulary and IS now stale — this
   is known and deliberately NOT fixed (the file is outside this lane's ownership; it is
   floated to the Admiral). Confirm no TEST asserts on that doc's trip content.
7. **The AST call-graph pin still holds** (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`):
   `_append_trip_entry` must still have exactly one caller (`_trip_hard_gate`), and exactly
   three functions may name `trip_ledger`.

## Evidence you must produce

- Cache-clean full suite. **Clear `__pycache__` before EVERY run**:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  then `python -m pytest tests/ -q`. Stale `.pyc` from a worktree relocation has fabricated a
  phantom failure in this lane before.
- The assertion-kind census (before/after).
- Your own independent reproduction of the behavior change, written by you, not copied from
  the implementer's test.

## Write your result to

`/home/tommy/projects/constellation-skills/.worktrees/epic-568-510/.agent-work/epic-568-510/crew-handoffs/g2-reviewer-result.md`

End with an explicit **APPROVE** or **BLOCK** line and your reasoning. You are fenced from
push, PR, and merge. Do not commit.
