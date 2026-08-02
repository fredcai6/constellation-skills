# Reviewer Handoff — G1: meta-learner data-builder

## Gate
`g1`

## What Was Implemented
`scripts/fusion_replay/metalearner.py` (NEW) — a data-builder ONLY (no modelling): `build_pairwise_dataset(records_dir, task)` produces, per task, a pooled pairwise supervised dataset from already-generated per-event module records, reusing the fusion_replay scorecard harness for record load / canonical join / constructor lineage / per-event preprocessing. `tests/unit/evo_predictor/test_metalearner.py` (NEW) — 13 tests (11 pass on real quali records, 2 skipped pending race_start/race generation).

This feeds a Step-3 epic gate measuring interaction headroom over module outputs. The dataset must represent the four module pi values per entity EXACTLY as the production scoring harness sees them (same alignment/lineage), so downstream Model1/Model2 numbers stay comparable to issue #373's ceilings. ANY divergence from the harness's per-event preprocessing corrupts the gate — that is the core thing to verify.

## How to Inspect the Diff
```powershell
Set-Location C:/Programs/f1Brainz/.claude/worktrees/agent-ade67b306f11aa4fb
git status --short
git diff --stat
git diff -- scripts/fusion_replay/metalearner.py tests/unit/evo_predictor/test_metalearner.py
```
The two files are NEW (untracked). Read them in full. The harness functions reused live in `scripts/fusion_replay/scorecard.py` (`_preprocess_events` L477, `_build_module_field_results` L235, `_align_driver_pi` L380, `canonicalize_and_join` L184, `_compute_event_residuals` L408 — the alignment idiom to mirror), `src/evo_predictor/constructor_projection.py::project_constructor_field_to_drivers`, `src/evo_predictor/fusion_training/_calibration.py::module_names_for_task`.

## Task Statement
Build `build_pairwise_dataset(records_dir, task)` returning a dict with: `X_delta (n_pairs,4)` = the 4 module Δpi=pi_i−pi_j in `module_names_for_task(task)` order `[constructor_recent, driver_recent, constructor_weekend, driver_weekend]`; `dev_delta (n_pairs,2)` = per-scope deviation difference (col0 = constructor_weekend−constructor_recent differenced over the pair = (M[:,2]−M[:,0])_i−(...)_j; col1 = driver_weekend−driver_recent differenced); `y (n_pairs,)` = 1.0 iff actual_position_i < actual_position_j; `event_ids` and `seasons` for bootstrap/LOSO grouping; a coverage dict. Pairs emitted ONCE per unordered pair (i<j by driver_ids order) with distinct, non-NaN actual positions (skip ties + NaN), mirroring `scoring.pairwise_log_loss`'s `triu_indices(n,k=1)` + valid mask; the mirror pair is NOT emitted. MUST reuse the harness functions — no hand-rolled alignment/lineage/join.

## Close Criteria (each is a review check — re-derive, do not trust the implementer's claims)
- **C1 — harness reuse, no reimplementation.** The builder imports and calls `_preprocess_events`, `_build_module_field_results`, `_align_driver_pi`, `canonicalize_and_join`, `project_constructor_field_to_drivers`, `module_names_for_task`. It does NOT reimplement the canonical join, the constructor-lineage normaliser, constructor→driver projection, or driver pi alignment. Confirm by reading the file.
- **C2 — alignment mirrors `_compute_event_residuals`.** Per event: build `M (n_drivers,4)` column-by-column in module_order; driver scope via `_align_driver_pi`, constructor scope via `project_constructor_field_to_drivers`; if ANY column returns None / raises ValueError, the WHOLE event is skipped and counted (mirrors the harness `continue`/`except`). Verify the skip semantics match.
- **C3 — pairwise label + antisymmetry.** Verify INDEPENDENTLY (write your own ~10-line snippet, do not reuse the builder's internals): pick a real quali event, recompute its triu pairs, and assert `y = (pos_i < pos_j)` and that exactly one of each unordered pair is present. Then assert antisymmetry as a property: for the builder's output, swapping i↔j would negate `X_delta` and `dev_delta` and flip `y` (the builder emits only i<j, so verify by reconstructing a mirror row by hand and checking the sign relationship).
- **C4 — deviation feature = weekend − recent per scope.** Independently recompute, on one event, `ctor_dev = M[:,2]−M[:,0]` and `drv_dev = M[:,3]−M[:,1]`, difference over a known pair, and assert it equals the builder's `dev_delta` for that pair to ~1e-9. (This is the #140 feature; getting the scope/sign wrong silently corrupts the deviation gate.)
- **C5 — season groups present and correct.** `seasons` integer-matches the year prefix of `event_ids` for every row (assert elementwise on the real output).
- **C6 — coverage on quali ≈ 173 events (RE-DERIVE).** Run the builder on `outputs/evo_runs/issue-374-records` task=`quali` and confirm `coverage['n_events_used']` is 173 (±a few). ALSO re-derive the expected count by an INDEPENDENT path: load the 4 quali modules with `_load_module_events`, `canonicalize_and_join`, `_preprocess_events`, and count prepped events — assert the builder's n_events_used matches the prepped count minus alignment skips. (The Commander smoke-verified 173 prepped, 0 skipped — you should reproduce that.)
- **C7 — test green on REAL records.** `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` is green (11 pass, 2 skip acceptable — the 2 skips are race_start/race, still generating). Confirm the skipped tests are guarded by a real "module files absent" condition, NOT unconditionally skipped.

## Allowed Scope
NEW `scripts/fusion_replay/metalearner.py`; NEW `tests/unit/evo_predictor/test_metalearner.py`. May import/call any existing `scripts/fusion_replay/*` and `src/evo_predictor/*`.

## Specific Exclusions (flag if touched)
- NO changes under `src/evo_predictor/` (production frozen) — `git diff` must show zero src/evo_predictor edits.
- NO modelling/CV/metrics in this gate (data-builder only) — flag if any logistic/torch/LOSO/bootstrap code appears (that is G2).
- NO sklearn import. NO new record-generation logic.

## Constraints the Implementation Must Respect (each a review check)
- `py` not `python`; tests via `py -m pytest`.
- `PYTHONIOENCODING=utf-8` in any python subprocess whose output is captured (PowerShell: `$env:PYTHONIOENCODING='utf-8'` before the call) — set it in YOUR verification shell.
- DB read-only at `C:/Programs/f1Brainz/data` (the harness handles DB internally; the builder passes nothing — confirm it does not open the DB directly or write anywhere).
- Records dir for the quali end-to-end check: `outputs/evo_runs/issue-374-records` (quali complete; race_start/race still generating — do NOT assert their counts).

## Evidence Produced (from IMPLEMENTER_RESULT — verify, don't trust)
- `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` → `11 passed, 2 skipped in 0.59s` (Python 3.14.3, pytest-9.0.2).
- quali coverage: n_events_used=173, n_pairs=31926, n_events_skipped_alignment=0, n_events_skipped_no_valid_pairs=0, per_season {2018:21,2019:21,2020:17,2021:22,2022:22,2023:22,2024:24,2025:24}, X_delta (31926,4), y-mean 0.4847.

## Suggested Model Tier
stronger — reason: must verify subtle harness reuse (constructor lineage/projection), pairwise/antisymmetry semantics, and deviation sign/scope; a quiet error here silently corrupts an epic-level gate. RE-DERIVE coverage and the dev feature by an independent code path; do not merely re-read the builder.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed; the builder reimplements join/lineage/alignment instead of reusing the harness; pairwise label or antisymmetry is wrong; deviation sign/scope is wrong; quali coverage is materially off 173 (signals a join/alignment regression); any `src/evo_predictor/` edit appears; or evidence is unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (C1–C7 with the numbers you independently re-derived — especially the quali n_events_used and the dev_delta cross-check), blockers, out-of-scope observations.
