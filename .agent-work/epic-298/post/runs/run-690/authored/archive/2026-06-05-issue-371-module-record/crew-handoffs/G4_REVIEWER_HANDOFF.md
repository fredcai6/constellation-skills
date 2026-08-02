# Reviewer Handoff

## Gate
`g4`

## What Was Implemented
(a) tests/integration/test_module_record_emit.py — bounded real-data test: trains driver_quali_power_from_recent_history once (2022-2023 train, 2024 eval, max_rounds 1, 2 epochs, seed 0, threads 1), backtests the same bundle twice (flag off / flag on), asserts byte-identical backtest JSON, sidecars only flag-on, exact round-trip, index count == event_count. (b) Evidence smoke gold-cycle run (mode smoke, LOSO on, emit_module_record true) from .agent-work/issue-371-module-record/evidence/g4_smoke_config.toml with results captured in evidence/g4-smoke-run.md (97s wall clock, 96 sidecars across mains/LOSO/calibration, loaded-record printout, details.json no-echo check).

## Critical context — the seeding judgment
The implementer found two sequential backtests of the same bundle differ WITHOUT the flag: the network stays in training mode after bundle load, dropout is active at inference (pre-existing defect; already flagged tc3 for triage — NOT yours to fix or re-litigate). To isolate the flag's effect the test pins torch.manual_seed(0) immediately before EACH backtest call so both draws follow the identical RNG path. Your job on this point: verify the isolation logic is sound and honestly documented in the test (docstring), and that byte-equality is asserted RAW (no normalization, no tolerance) — the handoff allowed a bundle_manifest_path normalization fallback only if genuinely needed; verify whether it was needed and that nothing else is normalized away.

## How to Inspect the Diff
Repo root: C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record
- Untracked: tests/integration/test_module_record_emit.py (read in full)
- Evidence: .agent-work/issue-371-module-record/evidence/ (g4_smoke_config.toml, g4-smoke-run.md, g4_smoke_run.log, smoke_output/, smoke_reports/)
- `git diff` vs HEAD cdab832 must show ZERO src//configs//docs/ changes (hard exclusion for this gate).

## Task Statement
Original implementer handoff (read it): .agent-work/issue-371-module-record/crew-handoffs/G4_IMPLEMENTER_HANDOFF.md
Frozen intent: .agent-work/issue-371-module-record/PROBLEM_STATEMENT.md

## Close Criteria (each is a review check)
- Integration test RUNS here (not skipped): re-run `py -m pytest tests/integration/test_module_record_emit.py -q` yourself; expect 1 passed in minutes (bounded training inside).
- Test asserts, concretely: raw byte equality of the two backtest JSONs; .record.npz/.record.json exist next to flag-on output ONLY; flag-off side has none; load_module_record round-trip with pi length == n_entities, sigma_pi (n,n), index event count == backtest JSON event_count.
- Skip guard follows the determinism-test mold (data + retro_truth presence) and skips cleanly when absent.
- Budgets exactly as specified (train_years [2022,2023], eval 2024, max_rounds_per_year 1, 2 epochs, seed 0, threads 1, cheap module).
- evidence/g4-smoke-run.md: exact command, duration, grouped listing with all three dir families populated (verify counts against the actual smoke_output tree yourself — ls the dirs), loaded-record printout, details.json no-echo spot-check. Verify the details.json on disk in smoke_reports/ really lacks emit_module_record (check it yourself, not just the evidence prose).
- Pollution check: the smoke run wrote nothing outside .agent-work/issue-371-module-record/evidence/ — verify outputs/evo_runs and reports/evo have no files with mtime during the run window (implementer noted pre-existing smoke1 files from an earlier unrelated run — distinguish carefully by timestamp/slug before accusing).
- `py -m src.utils.simplification_limits --paths tests/integration/test_module_record_emit.py` PASS.
- Scope: ONLY the new test file + evidence dir. ZERO src//configs//docs/ diffs.

## Constraints the Implementation Must Respect
- `py` not `python`; no tolerance-based JSON comparison; bounded budgets not raised.

## Evidence Produced (verify, don't trust)
- pytest 1 passed in 1.75s (NOTE: suspiciously fast for a test that trains a module — investigate whether training is cached/reused from a prior invocation in this checkout, e.g. fixture reuse or the test reusing the smoke run's bundle. If the test silently reuses pre-existing artifacts and would NOT be self-contained on a clean checkout, that is a finding: the skip-guard/bootstrap contract must be honest. A test-scoped tmp_path bundle trained in a session-scoped fixture that ran earlier in the implementer's session could explain 1.75s — find the real explanation.)
- simplification PASS (1 file).

## Suggested Model Tier
stronger scrutiny — evidence-validity gate: the run artifacts are the product, and one timing anomaly needs a real explanation.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.

## Working agreement
Work from repo root C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record. Read-only on src/, configs/, docs/; you may run tests/commands and inspect evidence artifacts. Re-running the integration test is REQUIRED. Do not modify code; do not commit.
