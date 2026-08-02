# Reviewer Handoff — G1: Offline fusion-replay harness + baseline reproduction

You are a fresh, independent reviewer crew. Verify the change against the criteria below by
INSPECTING and RE-RUNNING — do not trust the implementer's claims. Repo: f1Brainz (Windows;
`py` not `python`). Branch `constellation/issue-373-correlated-fusion`; cwd = worktree root.
Set `PYTHONIOENCODING=utf-8` before any python command.

## Gate
g1

## What Was Implemented
A numpy-only offline fusion-replay harness package plus a validation test that proves the
harness baseline reproduces production fusion exactly:
- `scripts/fusion_replay/__init__.py`, `records.py`, `baseline.py`, `scoring.py`
- `tests/unit/evo_predictor/test_fusion_replay_harness.py` (11 tests)
No production source modified (purely additive).

## How to Inspect the Diff
```
git status --short
git diff --stat
```
New files only under `scripts/fusion_replay/` and the one test file. Read each new file.
Confirm `git diff` shows NO changes under `src/evo_predictor/` (only `.claude/settings.local.json`
which is pre-existing and out of scope).

## Task Statement (what it had to build)
A reusable numpy-only harness that loads #371 module records, aligns a task's 4 modules by
entity_ids, reproduces `src/evo_predictor/fusion.py::fuse_module_fields_ordered` to <=1e-9 via
an INDEPENDENT numpy re-derivation, and scores a fused field (pairwise log-loss, rank MAE,
spearman vs actual_positions, credible-interval coverage vs target_mu). Baseline reproduction
encoded as an automated pytest with a SYNTHETIC fixture (no real data).

## Close Criteria (each becomes a review check — verify independently)
1. `py -m pytest tests/unit/evo_predictor/test_fusion_replay_harness.py -q` passes (re-run it).
2. The baseline test is NON-TAUTOLOGICAL: `_fuse_baseline_numpy` in `scripts/fusion_replay/baseline.py`
   must be an INDEPENDENT re-implementation of the precision-update loop (NOT a call to
   `fuse_module_fields_ordered`), and the test compares it to the REAL function. Read both and
   confirm. Also confirm a guard exists that the result is non-trivial (differs from the zero prior).
3. Scoring metrics are mathematically correct numpy with explicit sign conventions:
   spearman == +1 for a perfect predictor (highest pi = best/lowest actual position);
   rank_mae == 0 for perfect; pairwise_log_loss(perfect) < pairwise_log_loss(reversed);
   coverage of a tight interval around target==pi is ~1.0. Read `scoring.py` and confirm the
   math (sigmoid(pi_i-pi_j), label pos_i<pos_j; norm.ppf((1+level)/2) central intervals).
4. Missingness is EXPLICIT: NaN truth is skipped (not imputed); alignment returns dropped-entity
   counts and RAISES when a requested driver/constructor is missing. Read `records.py`.
5. numpy/scipy/stdlib only — NO torch, NO DB, NO FastF1, NO network imports anywhere in the package.
6. `py -m src.utils.simplification_limits --paths scripts/fusion_replay tests/unit/evo_predictor/test_fusion_replay_harness.py` passes (re-run it).
7. No production source behavior changed.

## Allowed Scope (what the implementation was permitted to touch)
CREATE only: `scripts/fusion_replay/*.py`, `tests/unit/evo_predictor/test_fusion_replay_harness.py`.

## Specific Exclusions (flag if touched)
Any modification to `src/evo_predictor/` production source; any variant-A / correlated-R /
cheap-B logic (that is G2, must NOT be present yet); any docs changes.

## Constraints the Implementation Must Respect
- numpy-only harness (scipy.stats allowed); no torch.
- One canonical path; explicit input validation; explicit missingness.

## Evidence Produced (implementer-claimed; verify)
- 11 passed; simplification PASS (5 files). Re-run both yourself and paste output.

## Suggested Model Tier
sonnet.

## Stop Conditions
Return BLOCK if: the baseline test is tautological (numpy path calls production), any metric
sign is wrong, missingness is imputed silently, a non-numpy/torch/DB import appears, production
source was changed, or any verification command fails.

## Return Format
Return REVIEW_RESULT: verdict (exactly APPROVE or BLOCK), per-check findings (1-7 above, each
pass/fail with what you observed), blockers, out-of-scope observations. Paste the re-run pytest
and simplification_limits output.
