# Implementer Handoff

## Gate
g1 (issue-87)

## Task
Rekey the lessons-playbook dormancy clock in `scripts/apply_lessons_delta.py` so a burst of apply invocations cannot expire a lesson:

1. **Once per distinct work-id.** A `tick=true` delta ages lessons (increments `runs_since_confirmed`) only if the delta's `work_id` has not already ticked. Repeat invocations from the same work-id must not double-age. Track seen work-ids in the playbook-state header (mechanical, parse/serialize like the existing counters); bounded retention is acceptable (e.g. keep the most recent ~50) — document the bound in a comment.
2. **Same-epoch guard.** On a tick, a lesson whose `added` date or `last-confirmed` date equals the tick's stamp date must not be auto-deleted, regardless of its `runs-since-confirmed` count. (Aging may still increment; only expiry is guarded.) A lesson must never die on the same day it was added or last confirmed.

Background (why): the 20260706-dogfood-audit epic ran ~19 apply invocations in one day; `runs_since_confirmed` blew past `dormancy-runs=10` and auto-deleted a useful one-observation lesson that had to be re-added at closeout.

## Protected Intent
The playbook stays hard-bounded and mechanically maintained: cap, grounding, and counter enforcement unchanged; constellation-scoped lessons stay pinned (never auto-deleted); `run_tick` semantics elsewhere (e.g. apply-threshold ripeness, `_apply_threshold_ripe`) must not silently change meaning — if the rekey alters what `run_tick` counts, verify ripeness logic still behaves as documented and say so in the result.

## Test Mode
TDD required — behavior change in a tested script; extend `tests/test_apply_lessons_delta.py`.

## Close Criteria
- Same work-id ticking twice ages a lesson exactly once.
- Two distinct work-ids age a lesson twice (normal behavior preserved).
- A lesson at the dormancy threshold whose `added` or `last-confirmed` date equals the tick stamp date survives the tick; on a later-dated tick it expires as before.
- Constellation-scoped lessons still never auto-delete.
- The existing `.agent-work/LESSONS.md` header (`run-tick=20 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3`) parses without error; a playbook without the new field(s) migrates silently on first write (new field appears, nothing else rewritten by hand).
- Full suite green: `python -m pytest tests/ -q` (375 tests pre-change).

## Allowed Scope
`scripts/apply_lessons_delta.py`, `tests/test_apply_lessons_delta.py`. Do NOT commit; leave changes in the working tree for review.

## Specific Exclusions
- `.agent-work/LESSONS.md` — never hand-edit; do not run the applier against the real playbook.
- `scripts/verify_lessons_applied.py`, `scripts/checklist_engine.py`, docs (a separate gate covers docs).

## Constraints
- Mechanism, not quality: dedupe by work-id string identity and date string equality only — no judgment calls in the script.
- Fail visibly: malformed new-field state raises `LessonsDeltaError`, no silent fallback.
- Match existing code style (dataclasses, header comment serialization pattern).

## Map Anchors (inbound)
- **Structural:** struct:scripts/apply_lessons_delta.py — tick branch (~lines 493-508), playbook-state header parse/serialize; struct:tests/test_apply_lessons_delta.py
- **Capability:** capability:lessons-playbook-dormancy
- **Constraints/assumptions:** constraint:constellation-lessons-pinned; constraint:backward-compatible-playbook-state; constraint:mechanism-not-quality
- **Decision anchors:** decision:dormancy-key=distinct-work-ids+same-epoch-guard (human, issue-87 understand q1) — do not substitute a different keying without stopping.
- **Evidence expectations:** claim:dormancy-behavior (new tests); claim:test-suite-green (full pytest run)

## Required Evidence
New/changed test names with passing output; full-suite pytest tail; brief note on the seen-work-ids storage format chosen and its bound; confirmation note on `run_tick`/ripeness semantics.

## Verification Commands

```bash
python -m pytest tests/test_apply_lessons_delta.py -q
python -m pytest tests/ -q
```

## Suggested Model Tier
stronger — bounded scope but state-migration and cross-cutting counter semantics carry regression risk.

## Authority
Human decided: keying = distinct work-ids + same-epoch guard; item 7/8 out of scope. You decide: storage format of seen work-ids and the retention bound. Do not decide alone: any change to ripeness/`run_tick` meaning, any new CLI flag, any schema change beyond the header field(s) — stop and return instead.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/issue-87/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`): completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
