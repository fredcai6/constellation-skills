# Reviewer Handoff — G1 (Issue #383)

## What was implemented
- `module_training_orchestration.py` `evaluate_labeled_batches`: per-event row now carries
  `entity_count = len(batch.entity_ids)` (row top-level, not in `metrics`).
- 6 tests: producer (positive int; no pollution), flow-through (`event_metric_rows`), dof-engagement (3).

## How to inspect
`git diff src/` (one 6-line hunk). Tests in test_evaluate_labeled_batches.py,
test_gold_module_cycle.py, test_gold_cycle_runner.py.

## Close criteria verified
1. entity_count positive int per scored event — PairBatch enforces len>=2; test asserts.
2. No aggregate/metrics pollution — _mean_metrics only iterates metrics keys; test asserts absent.
3. Dof term engages — captured demo: effective_dof [17,19,21,14] vs bug [1,1,1,1]; objective curve
   optimum at beta=0.1 with populated counts, inert/offset-only with None.
4. End-to-end flow verified: run.py serializes per_event verbatim (strip_record_from_rows is a
   blacklist removing only "record"); reports.py event_metric_rows reads event.get("entity_count").
5. Targeted tests: 93 passed (4 files) + 153 passed (wider sweep). pyright 0/0 on src+tests.
   simplification_limits --baseline exits 0; evaluate_labeled_batches 0 violations.
6. Scope: #384 untouched; pair_count untouched.

## Findings
- F1 (note, not blocker): committed reports/evo/*.details.json still show entity_count=None — they are
  stale generated artifacts from before the fix. Doctrine: regenerate, don't hand-edit. Regeneration =
  a full gold cycle (slow); the next gold cycle will populate them. Behavior is proven by tests + the
  end-to-end trace. -> deferred/triage, not a blocker for this fix.
- F2 (triage candidate): pair_count is None everywhere via the same root cause (adjacent missing field
  at the same producer). Out of #383 scope.

## Verdict
APPROVE.
