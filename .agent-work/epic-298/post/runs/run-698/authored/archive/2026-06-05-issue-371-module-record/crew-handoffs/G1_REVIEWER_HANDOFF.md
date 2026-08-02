# Reviewer Handoff

## Gate
`g1`

## What Was Implemented
Opt-in `collect_record: bool = False` keyword param on `evaluate_labeled_batches`
(src/evo_predictor/module_training_orchestration.py). When on, each per-event row gains a
`"record"` dict of in-memory arrays (pi, sigma_pi, target_mu None-safe, outcome,
actual_positions aligned-or-None, pair_index, features, dqi, entity_ids, feature_names,
feature_schema_version, event_id). Two module-local helpers added: `_align_actual_positions`,
`_build_event_record`. New test file tests/unit/evo_predictor/test_evaluate_labeled_batches_record.py (19 tests).

## How to Inspect the Diff
Repo root: C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record
- `git diff src/evo_predictor/module_training_orchestration.py` (uncommitted, vs HEAD adac146)
- `git status --short` then read the new untracked test file in full.

## Task Statement
Original implementer handoff (read it): .agent-work/issue-371-module-record/crew-handoffs/G1_IMPLEMENTER_HANDOFF.md
Frozen intent: .agent-work/issue-371-module-record/PROBLEM_STATEMENT.md

## Close Criteria (each is a review check)
- Default-off path byte-identical: same keys/values, no `"record"` key anywhere, metrics unchanged; zero added per-event overhead when off (tensor→numpy conversions only inside the collect branch).
- Collect-on: every non-skipped event row carries `"record"` with arrays exactly equal to fake-produced values incl. full (n,n) sigma_pi.
- `target_mu=None` event → record with `target_mu is None`, rest populated.
- Missing `sigma_pi` with collect on ⇒ hard error; **handoff required module/event named in the error message — implementer used bare AttributeError from attribute access. VERIFY whether the raised message names module/event; if not, this is a contract deviation: report it and weigh BLOCK vs note.**
- `actual_positions` absent from diagnostics ⇒ record carries None; present ⇒ aligned float64 ndarray with NaN for missing entities, aligned to batch.entity_ids order.
- Numerical-error skip path (LinAlgError): skipped events produce neither metrics row nor record.
- Function stays pure: no filesystem knowledge, no paths, no writes, no module-level state.
- Scope respected: ONLY module_training_orchestration.py + the new/existing test file touched. Exclusions untouched: run.py/cmd_module_backtest, any npz/json writing, gold_cycle config/builders, fusion.py, report schema, docs.

## Constraints the Implementation Must Respect
- `py` not `python` for all commands.
- Style matches surrounding code; comment density similar.
- **Strict simplification check**: implementer reports 10 pre-existing violations, 0 new. Verify: run `py -m src.utils.simplification_limits --paths src/evo_predictor/module_training_orchestration.py tests/unit/evo_predictor` and confirm no violation names a symbol introduced/modified by this diff (evaluate_labeled_batches, _align_actual_positions, _build_event_record, new tests).

## Evidence Produced (verify, don't trust)
- TDD red: 13 failed pre-implementation (TypeError on unknown kwarg); green: 22 passed.
- Full focused suite: `py -m pytest tests/unit/evo_predictor/ -q` → 1213 passed.
- Re-run yourself: `py -m pytest tests/unit/evo_predictor/test_evaluate_labeled_batches.py tests/unit/evo_predictor/test_evaluate_labeled_batches_record.py -q` and the full focused suite.

## Suggested Model Tier
simple bounded — one-function seam, fully specified contract, strong test pattern.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.

## Working agreement
Work from repo root C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record. Read-only on src/; you may run tests/commands. Do not modify code; do not commit.
