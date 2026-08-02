# IMPLEMENTER_RESULT — g6 (determinism acceptance test + usage doc)

Status: complete. Determinism GUARANTEE REFRAMED with human approval (see below).

## Files changed
- NEW `tests/integration/test_utilization_determinism.py` — 2 tests:
  - `test_utilization_determinism_fixed_threads_worker_count_invariant` (headline): same bounded job set run at
    n_workers=1/threads=1 (in-process) vs n_workers=2/threads=1 (pool) into SEPARATE output trees; asserts
    structural byte-identity (result count, input-order job keys, manifest+backtest JSON structure with
    created_at/paths/numeric-leaves normalized, artifact filenames) + trained weights agree within 1e-2.
  - `test_utilization_determinism_catches_divergence` (anti-vacuity: seed perturbation drifts weights past tol).
- MODIFIED `docs/evo/analysis_refresh.md` — `### Resource utilization (--utilization)` subsection; Last verified 2026-06-03.

## HUMAN-APPROVED guarantee reframe (was: "byte-identical weights at fixed threads")
- FINDING: trained-weight byte-identity is physically unattainable on torch 2.10 CPU / py3.14 / Win even at
  single-thread + same-seed + fixed PYTHONHASHSEED (~3e-4 intrinsic FP-reduction-order drift run-to-run).
- PROOF it is NOT a parallelism bug: 1-worker-vs-2-worker drift 2.8e-4 ~= same-1-worker rerun drift 3.1e-4.
  Worker count adds NO systematic divergence; run_jobs runs the (intrinsically noisy) worker faithfully.
- DECISION (human, 2026-06-03): accept reframed guarantee = structural byte-identity (exact) + weight agreement
  within 1e-2 (30x over the 3e-4 floor) + empirical proof worker-count adds no drift. File a separate issue for
  the broader torch-CPU bit-reproducibility investigation (tracked as triage candidate).

## Test mode: TDD/anti-vacuity satisfied
- Divergence-catch proven 2 ways: (1) committed perturbation test passes by detecting seed-drift past tol;
  (2) throwaway job-order reversal made the headline test FAIL on the input-order key assertion. Plus the headline
  test legitimately failed twice in dev (manifest/backtest drift) before normalization was corrected.

## Evidence
- `py -m pytest -q -k utilization_determinism` -> 2 passed, 2 (unrelated) skipped, in ~8.8s. Both RAN against local data (verified -v).
- `py -m src.utils.simplification_limits --paths tests/integration/test_utilization_determinism.py` -> PASS.

## Bounding
2 recent_history quali modules (no compound-prior dep), train_years=[2022,2023], eval_year=2024,
max_rounds_per_year=1, 2 epochs; jobs via production build_main_train_backtest_jobs; skipif data/retro_truth absent.

## Doc
docs/evo/analysis_refresh.md (gold-cycle runbook): three levels + workers*threads~=cores table + RAM auto-cap +
non-policy-hint (gold-allowed, not in applied_overrides/report) + determinism guarantee.

## Out-of-scope observations (triage candidate)
- Latent-power training is not bit-reproducible run-to-run on torch 2.10 CPU even single-thread/fixed-seed
  (~3e-4 weight drift; rank metrics swing O(0.1-0.3)). Orthogonal to run_jobs; means gold artifacts aren't
  bit-stable across reruns generally. Needs a torch.use_deterministic_algorithms / deterministic-reduction
  investigation -> separate issue (human approved filing).
