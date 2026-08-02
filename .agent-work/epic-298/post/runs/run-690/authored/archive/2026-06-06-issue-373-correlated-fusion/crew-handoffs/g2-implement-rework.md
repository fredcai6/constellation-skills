# Implementer Handoff — G2 REWORK: make `fuse_module_fields_correlated` pass simplification limits

You are a fresh implementer crew. Work ONLY from this handoff. Repo: f1Brainz (Windows; `py`
not `python`). Branch `constellation/issue-373-correlated-fusion`; cwd = worktree root
(`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set `PYTHONIOENCODING=utf-8`
before any python command.

## Starting point (already present in the working tree — this is your inheritance)
A prior crew already implemented G2 (correlated-covariance fusion variant A + R estimator +
cheap-B + tests). It is COMPLETE and all 23 functional tests pass. Files already on disk:
- `src/evo_predictor/fusion.py` — ADDED `fuse_module_fields_correlated(...)` (production
  `fuse_module_fields_ordered` is untouched; do NOT change it).
- `src/evo_predictor/fusion_training/_correlation.py` — NEW: `estimate_cross_module_correlation`,
  `mask_correlation_to_block`.
- `scripts/fusion_replay/variants.py` — NEW: `_fuse_baseline_diagonal_numpy`, `run_variant`,
  `cheapB_correlation`.
- `tests/unit/evo_predictor/test_fusion_correlated.py` — NEW: 12 passing tests.

READ all four first. The math and tests are correct — do NOT rewrite the algorithm.

## Gate
g2 (rework)

## The ONE problem to fix
`py -m src.utils.simplification_limits` FAILS on the new function:
```
src/evo_predictor/fusion.py fuse_module_fields_correlated: cyclomatic_complexity=21 (limit: <20)
src/evo_predictor/fusion.py fuse_module_fields_correlated: function_lines=133 (limit: <100)
```
(NOTE: `fuse_module_fields_ordered` ALSO reports 2 violations — those are PRE-EXISTING on the
committed HEAD `9f52e75`, are production code under a do-not-touch ruling, and are NOT yours to
fix. Leave `fuse_module_fields_ordered` byte-for-byte unchanged. Only `fuse_module_fields_correlated`
must be brought under the limits.)

## What to do
Refactor `fuse_module_fields_correlated` to satisfy `cyclomatic_complexity < 20` AND
`function_lines < 100` by extracting cohesive private helpers, WITHOUT changing its behavior or
public signature. Suggested extractions (you choose the cleanest split):
- `_validate_correlation_matrix(correlation, k) -> np.ndarray` — the shape/symmetry/unit-diagonal/PSD
  validation block (this alone removes several branches + ~25 lines).
- `_resolve_enabled_modules(config, result_by_module) -> list[str]` — the enabled-module resolution
  + missing-module check + single-event-id check + task-match check (reuse where natural; keep the
  exact same error messages/ValueErrors).
- `_build_aligned_obs(enabled_modules, step_by_module, result_by_module, drivers, constructor_by_driver, config) -> tuple[np.ndarray, np.ndarray]` —
  the loop building `obs_mean_mat` (k,n) and `obs_std_mat` (k,n).
Keep the vectorized GLS core (W, R_inv, prec, ybar_num, posterior fold) and the diagnostics dict
in the main function. Helpers go near the other private helpers in fusion.py (after
`_inverse_or_pinv` / before `fuse_module_fields_ordered`, or grouped with the new function — your
call, but do not reorder or touch existing functions).

## Hard invariants (DO NOT break)
1. `fuse_module_fields_ordered` body + signature unchanged (git diff for that function = empty).
2. `fuse_module_fields_correlated` public signature unchanged; behavior identical (same outputs).
3. The R=I identity stays EXACT: at R=I, `fuse_module_fields_correlated` == `_fuse_baseline_diagonal_numpy`
   to atol<=1e-9 (the existing test must still pass unchanged).
4. All existing tests stay green; do NOT weaken or edit the tests to make limits pass.
5. numpy-only; explicit input validation (preserve every existing ValueError + message text).

## Close Criteria (prove each, paste output tails)
- `py -m src.utils.simplification_limits --paths src/evo_predictor/fusion.py src/evo_predictor/fusion_training/_correlation.py scripts/fusion_replay tests/unit/evo_predictor/test_fusion_correlated.py`
  reports ONLY the two pre-existing `fuse_module_fields_ordered` violations (complexity=20,
  function_lines=118) and NO `fuse_module_fields_correlated` violations. (i.e. your function is
  clean; the only remaining FAIL lines name `fuse_module_fields_ordered`.)
- `py -m pytest tests/unit/evo_predictor/test_fusion_correlated.py tests/unit/evo_predictor/test_fusion_replay_harness.py -q` passes (23 tests).
- `py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay" -q` passes.
- `git diff src/evo_predictor/fusion.py` shows the existing `fuse_module_fields_ordered` function
  unchanged (only additions + the refactor of `fuse_module_fields_correlated`).

## Allowed Scope
- EDIT: `src/evo_predictor/fusion.py` — refactor `fuse_module_fields_correlated` + add private
  helpers only. Do NOT touch `fuse_module_fields_ordered` or any other existing function.
- READ: the other three G2 files + anything under src/evo_predictor/.
- Do NOT edit `_correlation.py`, `variants.py`, or the test file unless a helper extraction
  genuinely requires an import change (it should not).

## Specific Exclusions
- Do NOT change production `fuse_module_fields_ordered`. Do NOT fix its pre-existing simplification
  violations (out of scope; logged as triage by commander).
- Do NOT touch quali-head / latent_power / `_correction.py` / docs.
- Do NOT generate records or run backtests (G3).

## Suggested Model Tier
sonnet.

## Stop Conditions
Stop and return if: you cannot get `fuse_module_fields_correlated` under both limits without
changing behavior, or any existing test breaks and you cannot restore it without weakening it.

## Return Format
Return IMPLEMENTER_RESULT: what you extracted, files changed (full paths), the simplification
output tail (showing only the 2 pre-existing ordered violations remain), the pytest tails (23 +
full suite), confirmation the R=I identity test still passes, assumptions, out-of-scope notes.
