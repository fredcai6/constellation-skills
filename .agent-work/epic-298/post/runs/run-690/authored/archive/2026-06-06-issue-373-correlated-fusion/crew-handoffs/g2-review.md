# Reviewer Handoff — G2: Correlated-covariance fusion (variant A) + cheap-B + R estimation

You are a fresh, INDEPENDENT reviewer crew. You did NOT write this code. Work ONLY from this
handoff. Repo: f1Brainz (Windows; `py` not `python`). Branch
`constellation/issue-373-correlated-fusion`; cwd = worktree root
(`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set `PYTHONIOENCODING=utf-8`
before any python command. Your job is to VERIFY, not to fix. Re-run everything yourself; do not
trust prose claims.

## What was built (G2)
An OPT-IN correlated-covariance fusion variant for issue #373's offline measurement harness.
Production `fuse_module_fields_ordered` must remain behaviorally UNCHANGED (no runtime call-site
flips). The deliverable is a measurement tool, not a production behavior change.

## The diff to inspect (uncommitted working tree, on top of committed G1 `9f52e75`)
- `src/evo_predictor/fusion.py` — ADDED `fuse_module_fields_correlated(...)` plus three private
  helpers (`_validate_correlation_matrix`, `_resolve_correlated_modules`, `_build_aligned_obs`).
  `fuse_module_fields_ordered` must be UNCHANGED.
- `src/evo_predictor/fusion_training/_correlation.py` — NEW: `estimate_cross_module_correlation`,
  `mask_correlation_to_block` (+ private helpers).
- `scripts/fusion_replay/variants.py` — NEW: `_fuse_baseline_diagonal_numpy`, `run_variant`,
  `cheapB_correlation`.
- `tests/unit/evo_predictor/test_fusion_correlated.py` — NEW: 12 tests.

Inspect via:
```
git diff src/evo_predictor/fusion.py
git status --short            # the three new files show as untracked
```
Read the three new files in full. They are untracked, so `git diff` will not show them — open them
directly.

## The math you are verifying (so you can judge correctness, not just run tests)
Production baseline = sequential per-entity Gaussian precision update over a task's enabled module
observations using the FULL n×n obs_cov (covariance_scale*sigma_pi + jitter + tension).

Variant A (`fuse_module_fields_correlated`) treats `correlation` as a k×k cross-MODULE error
correlation R and combines PER ENTITY i: D_i = diag(per-entity module stds), Sigma_i = D_i R D_i,
GLS-combine the k scalar observations of entity i's latent pi_i, then fold the scalar prior
(mean 0, var prior_sigma^2). At R=I, Sigma_i is diagonal so variant A reduces to a per-entity
DIAGONAL precision sum — which is NOT the full-matrix baseline. The documented identity anchor is
therefore the DIAGONALIZED baseline `_fuse_baseline_diagonal_numpy` (same sequential update with
each obs_cov replaced by its diagonal). This is a deliberate, documented modelling choice — verify
it is documented in the function docstring and the variants.py helper docstring, and that the
identity test compares against the diagonalized (not full-matrix) baseline.

## Review checklist — VERIFY EACH (mark PASS/FAIL with evidence)
1. **R=I identity is real and non-tautological.** Read `test_correlated_RI_equals_diagonal_baseline`
   and `_fuse_baseline_diagonal_numpy`. Confirm the reference is an INDEPENDENT re-derivation
   (sequential diagonal precision update), NOT a call back into `fuse_module_fields_correlated`.
   Confirm atol<=1e-9. Confirm the multi-seed spot-check exists.
2. **At R=I, variant A genuinely equals the diagonalized baseline** — re-run the test; also
   reason that the algebra (batched `w^T R^-1 w` with R=I == sum of per-module precisions ==
   sequential diagonal accumulation) is correct.
3. **Non-identity R changes the answer** (`test_correlated_RnotI_differs`): coupling materially
   changes pi AND posterior variance. Confirm.
4. **R estimator is in STANDARDIZED-residual space**, pooled across events on COMMON entities,
   shrunk toward I; recovers a planted correlation (`test_estimate_correlation_recovers_planted`).
   Verify standardization is per (event, module) (subtract mean, divide by std) and that
   shrinkage = (1-λ)R_hat + λI with unit diagonal preserved. Verify disjoint/missing entities and
   thin events are SKIPPED and COUNTED in diagnostics (never imputed). Confirm
   `test_diagnostics_report_skipped_events` and the shrinkage/conditioning tests.
5. **cheap-B masking is correct** (`mask_correlation_to_block` + `cheapB_correlation`): keeps ONLY
   the constructor<->driver same-evidence-source off-diagonal pairs, zeros all other off-diagonals,
   diagonal stays 1. Confirm `test_cheapB_masks_offblock` actually asserts the recent<->weekend
   cross terms are zeroed and the same-evidence ctor<->drv block is preserved.
6. **Production unchanged.** `git diff src/evo_predictor/fusion.py` must show NO deletions/edits to
   `fuse_module_fields_ordered` (only added helpers + the new function). Confirm
   `test_production_fusion_unchanged` still matches the real `fuse_module_fields_ordered` to 1e-9.
   Confirm no production/runtime call-site was flipped to the variant (grep for
   `fuse_module_fields_correlated` outside fusion.py / scripts / tests — should appear only in the
   harness + tests).
7. **Input validation present + explicit** (R shape/symmetry/unit-diag/PSD; module alignment;
   single event id; task match). numpy-only (no torch). No silent fallback/imputation.
8. **Simplification limits.** Re-run the command below. The ONLY remaining violations must be the
   two PRE-EXISTING `fuse_module_fields_ordered` ones (complexity=20, lines=118 — production code,
   out of scope per commander ruling). `fuse_module_fields_correlated` and the new files must be
   clean.

## Commands to RUN yourself (paste output tails into your result)
```
py -m pytest tests/unit/evo_predictor/test_fusion_correlated.py tests/unit/evo_predictor/test_fusion_replay_harness.py -q
py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay" -q
py -m src.utils.simplification_limits --paths src/evo_predictor/fusion.py src/evo_predictor/fusion_training/_correlation.py scripts/fusion_replay tests/unit/evo_predictor/test_fusion_correlated.py
git diff src/evo_predictor/fusion.py
```

## Close criteria for APPROVE
All 8 checklist items PASS, all commands green (modulo the 2 pre-existing ordered violations),
R=I identity confirmed non-tautological and exact, production behavior unchanged.

## Out of scope (do NOT block on these; note as observations if relevant)
- The 2 pre-existing `fuse_module_fields_ordered` simplification violations (commander ruling:
  production, do-not-touch; logged as triage).
- Record generation / real-data scorecard (that is G3).
- #374 interaction-headroom territory.

## Return Format
Return REVIEW_RESULT with: verdict (APPROVE or BLOCK), per-checklist-item PASS/FAIL with the
specific evidence (line refs / output), the exact command output tails you ran, any
non-tautology concern, any out-of-scope observations. If BLOCK, the precise minimal change needed.
