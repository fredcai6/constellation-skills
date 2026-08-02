# Reviewer Handoff

## Gate
g6 — Determinism acceptance test + usage doc

## What Was Implemented
NEW `tests/integration/test_utilization_determinism.py` (headline worker-count-invariance test + anti-vacuity
divergence-catch test) exercising REAL gold-cycle train+backtest through run_jobs at fixed threads; and a
`--utilization` usage subsection in `docs/evo/analysis_refresh.md`.

## How to Inspect the Diff
- `git status --porcelain` (expect: NEW tests/integration/test_utilization_determinism.py; MODIFIED docs/evo/analysis_refresh.md; ignore `.agent-work/`).
- Read the new test in full; `git diff -- docs/evo/analysis_refresh.md`.
Implementer result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g6-implementer-result.md`.

## *** REFRAMED GUARANTEE (human-approved 2026-06-03) — verify the test against THIS, not the original ***
The original criterion ("trained-weight byte-identity at fixed threads") was found physically unattainable on this
torch 2.10 CPU / py3.14 / Win stack: even single-thread + same-seed + fixed PYTHONHASHSEED training drifts ~3e-4
run-to-run (intrinsic FP reduction-order nondeterminism). The implementer measured 1-vs-2-worker drift (2.8e-4) ≈
same-path rerun drift (3.1e-4) → worker count adds NO systematic divergence. The HUMAN ACCEPTED the reframed
guarantee:
- **Structural byte-identity (must be EXACTLY equal):** result count; input-order job keys (run_jobs reassembly);
  per-job manifest JSON structure after normalizing created_at + absolute paths + numeric leaves; artifact
  filenames; backtest JSON structure after normalizing bundle path + numeric leaves.
- **Trained-weight agreement within 1e-2** (≈30× over the 3e-4 floor); backtest metric VALUES intentionally NOT
  compared (rank-metric discretization noise), only their structure.
- Do NOT block because weights aren't byte-identical — that is the sanctioned reality.

## Close Criteria (each a review check)
- The test is NON-VACUOUS: it would FAIL on a real divergence. Confirm the committed divergence-catch test actually
  fails-then-passes logic is sound, and ideally reproduce a perturbation (e.g. reverse Run B's job order) and see
  the headline test fail on the input-order key assertion.
- Structural assertions are correct and exact (counts, input-order keys, normalized manifest/backtest structure, filenames).
- Weight tolerance 1e-2 is justified vs the measured ~3e-4 floor and is meaningfully tighter than the perturbation gap.
- The test RUNS (not just skips) against local data — confirm `pytest -k utilization_determinism -v` shows PASSED, not skipped.
- Bounded runtime (~seconds), deterministic seeds, skipif guard on data/retro_truth absence with a clear reason.
- Doc accuracy: `docs/evo/analysis_refresh.md` --utilization section matches reality — three levels, workers×threads≈cores,
  RAM auto-cap, gold-allowed non-policy hint NOT in applied_overrides/report (cross-check `_apply_utilization_hint`
  in run.py and that utilization is absent from build_run_config), and the (reframed) determinism guarantee.

## Allowed Scope
tests/integration/test_utilization_determinism.py (new), docs/evo/analysis_refresh.md.

## Specific Exclusions (flag if touched)
NO production code change (src/, scripts/, utilization.py, gold cycle). NO report-schema change. NO architecture-map
change (Commander reconcile handles that). If the test reveals a REAL fixed-thread worker-count divergence, that's a
BLOCK (production defect) — but the implementer's measurements indicate none exists.

## Constraints (each a review check)
- Deterministic, bounded, non-vacuous.
- `py -m src.utils.simplification_limits --paths tests/integration/test_utilization_determinism.py` → clean.

## Evidence Produced
- `py -m pytest -q -k utilization_determinism` → 2 passed (+unrelated skips) ~9s (re-run; confirm RAN not skipped).
- Divergence-catch confirmation.

## Suggested Model Tier
stronger — reason: the test IS the feature's acceptance; verifying it's faithful (non-vacuous, correct normalization,
justified tolerance) and that the reframed guarantee is honestly captured is the crux.

## Stop Conditions
Return BLOCK if: the test is vacuous / wouldn't catch divergence, the structural assertions are wrong, the weight
tolerance is meaningless, the test only skips, the doc is inaccurate, production code was changed, or a REAL
worker-count divergence at fixed threads is found.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope
observations. State whether you reproduced the divergence-catch.
