# Reviewer Handoff

## Gate
g1 (issue-87)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-87/g1-review/review.json`.

## What Was Implemented
Dormancy-clock rekey in `scripts/apply_lessons_delta.py`: (1) tick aging deduped by delta `work_id` via a new bounded (50) `ticked-work-ids` playbook-state header field — a repeat tick from a seen work-id ages nothing and does not bump `run_tick`; (2) same-epoch guard — on a real tick, a non-constellation lesson whose `added` OR `last-confirmed` date equals the tick stamp date is aged but never auto-deleted. Plus 10 new tests; the pre-existing `test_tick_auto_deletes_unconfirmed` was reseeded with a prior-dated `added` (its original same-day add-then-expire is exactly what the guard now forbids — expected, sanctioned by close criteria).

## How to Inspect the Diff
UNCOMMITTED working tree on branch `constellation/issue-87` in `C:\Programs\constellation-skills`. Use `git status --porcelain` then `git diff -- scripts/apply_lessons_delta.py tests/test_apply_lessons_delta.py`. Only those two files should be changed (`.agent-work/issue-87/**` run artifacts are Commander-owned; ignore them).

## Task Statement
Rekey the dormancy clock so a burst of apply invocations cannot expire a lesson: age at most once per distinct work-id (bounded seen-set in the header, mechanical parse/serialize), and never auto-delete a lesson on a tick dated the same as its added/last-confirmed date. Constellation lessons stay pinned; existing playbook headers parse and migrate without hand edits; TDD in tests/test_apply_lessons_delta.py; full suite green.

## Close Criteria
- Same work-id ticking twice ages a lesson exactly once; distinct work-ids age normally.
- A lesson at the dormancy threshold whose added or last-confirmed date equals the tick stamp date survives; a later-dated tick expires it as before.
- Constellation-scoped lessons still never auto-delete.
- Existing header `run-tick=20 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3` parses; a header without the new field migrates silently on first write.
- Malformed new-field state raises LessonsDeltaError (fail visibly, no silent fallback).
- Full suite green: `python -m pytest tests/ -q`.

## Allowed Scope
`scripts/apply_lessons_delta.py`, `tests/test_apply_lessons_delta.py` only.

## Specific Exclusions
`.agent-work/LESSONS.md` (never touched, applier never run against it), `scripts/verify_lessons_applied.py`, `scripts/checklist_engine.py`, docs. Flag if the diff touches any.

## Constraints the Implementation Must Respect
- Mechanism, not quality: dedupe by exact work-id string identity; guard by date-string equality only — no judgment logic.
- Backward-compatible playbook state; migration mechanical.
- Ripeness/`_apply_threshold_ripe` semantics unaffected. Note: the implementer reports `run_tick` now increments once per distinct aging round (deduped repeat ticks no longer bump it) and claims nothing reads `run_tick` for decisions — VERIFY that claim against the code.
- Matches existing code style; new constant documented.

## Map Anchors (inbound)
- **Structural:** struct:scripts/apply_lessons_delta.py — tick branch, STATE_RE/Playbook/load_playbook/render_playbook/_default_preamble, new `_stamp_date` helper; struct:tests/test_apply_lessons_delta.py
- **Capability:** capability:lessons-playbook-dormancy
- **Constraints/assumptions:** constraint:constellation-lessons-pinned; constraint:backward-compatible-playbook-state; constraint:mechanism-not-quality
- **Decision anchors:** decision:dormancy-key=distinct-work-ids+same-epoch-guard (human) — flag any deviation.
- **Evidence expectations:** claim:dormancy-behavior; claim:test-suite-green (this feeds g1-integrate.c1, `python -m pytest tests/ -q`)

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-87/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`: TDD red observed (7 failed pre-change), 52 pass in module, full suite `384 passed, 1 skipped, 18 subtests` (baseline 375 total). Re-run commands yourself; do not trust the transcript.

## Suggested Model Tier
stronger — state-migration and counter-semantics regression risk; the review must independently verify the run_tick claim.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-87/crew-handoffs/g1-review/REVIEW_RESULT.md`): verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
