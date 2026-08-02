# Implementer Handoff — G2: log-space property mixture + support-driven-k fix (#638)

## Gate
g2-implement

## Task
Rework the Phase-1 corner property-class mixture so the mandatory F12 held-out-circuit
stability gate earns a GENUINE PASS, by fixing the MODEL (not weakening the check). Full
root-cause + chosen fix + real-data evidence are in
`.agent-work/638-f12-stability-rework/DIAGNOSIS.md` — READ IT FIRST. Summary of the fix you
implement (all four choices are decided; do not re-derive):

1. **Fit `fit_property_mixture` in `(log10(radius_m), lateral_g)` space.** Root cause RC1: raw
   `radius_m` is a heavy-tailed continuum (~2 decades), so GMM component *locations* shift with
   circuit composition — even fixed-k fails 1/5 in raw space. log10(radius) is near-symmetric and
   makes locations composition-STABLE (fixed k=4 log space = 5/5 on real data). radius is
   physically multiplicative (adjacent corner classes ~order-of-magnitude apart).
2. **Support criterion = "component holds ≥ `MIN_COMPONENT_WEIGHT_FRAC` (0.05) of the data OR
   ≥ `MIN_COMPONENT_SUPPORT_COUNT` (150) observations."** Root cause RC2: the relative 5% floor
   is composition-brittle at large N (real split-3 half-A: a 4th component with 12,097 real
   observations rejected only for being 4.27% < 5%). 150 ≈ 30 observations per estimated Gaussian
   parameter (2D full-cov = 5 params) — the estimability minimum. Keep the pre-registered 0.05 as
   the fraction arm; ADD the absolute-count arm (OR). Component supported ⟺ `weight ≥ 0.05` OR
   `weight * N ≥ 150`.
3. **`k_range` default = `(2, 4)`.** Ceiling 4 = the physically-motivated max number of
   corner-severity classes (tight / medium / fast / very-fast). Frozen from domain structure, not
   tuned to seeds. k stays support-driven within (2,4): BIC-select among candidates clearing the
   support criterion (falls to fewer classes when unsupported; falls back to k=1 if none clear).
4. **Gate `mixture_stability.py` compares in log-radius units:** the radius axis normalization
   constant becomes `LOG_RADIUS_SCALE = 0.30` (adjacent classes ~factor-2 apart ≈ 0.30 in log10;
   mirrors the old `RADIUS_SCALE_M=50` domain rationale, in log space). `LATERAL_G_SCALE=0.5`,
   `F12_AGREEMENT_THRESHOLD=1.0`, the Hungarian match, and the k-mismatch→inf auto-fail are
   UNCHANGED. (Required because the fit now lives in log space; `scaler.inverse_transform(means_)`
   now yields log10-radius, so the gate must normalize it with a log scale, not metres.)

## Protected Intent
- EARN the PASS by a genuinely more-stable model; do NOT game the gate. `F12_AGREEMENT_THRESHOLD`
  stays 1.0; the k-mismatch auto-fail stays; the discriminating synthetic test stays able to FAIL.
- All new constants (`MIN_COMPONENT_SUPPORT_COUNT=150`, `k_range` ceiling 4, `LOG_RADIUS_SCALE=0.30`)
  are FROZEN in-module with a domain-reasoned comment, chosen BEFORE the real-data run (this handoff
  is that pre-registration) — never tuned to a result.
- k stays support-driven (must respond to genuine structure), not a hardcoded constant.
- `physics.layer2` must NOT import evo (`constraint:physics_region_no_evo_import`).

## Test Mode
test-after allowed (fast synthetic/unit tests; NO real DB). Do NOT run the ~6-min real-data F12 —
the commander runs it in G3. Prove correctness via synthetic tests only.

## Close Criteria (each proven)
- `fit_property_mixture` fits in log-radius space, encapsulated so callers passing RAW
  `(radius_m, lateral_g)` need no change (see Allowed Scope callers). The log-transform helper is
  applied in BOTH `fit_property_mixture` (before scaler.fit) AND `posterior_membership` (before
  scaler.transform) so query coordinates match the fit space.
- Support criterion is the fraction-OR-count form above; `MIN_COMPONENT_SUPPORT_COUNT=150` frozen.
- `k_range` default `(2,4)`; k support-driven within it.
- `mixture_stability.py` normalizes the radius axis by `LOG_RADIUS_SCALE=0.30`; all other gate
  constants/logic unchanged.
- `tests/unit/physics/layer2/test_property_mixture.py` + `test_mixture_stability.py` updated and
  GREEN, INCLUDING:
  - The discriminating test (`TestCheckHoldoutStabilityDiscriminating`): same-generator → PASS,
    shifted-generator → FAIL, still able to fail. Its scenario is legitimately changed by the log
    transform — reseed/rewrite the blob generators/shifts so the discrimination holds in log space
    (a shifted generator must still exceed `F12_AGREEMENT_THRESHOLD`). NAME this as an expected
    rewrite.
  - A test showing large-N no longer over-selects k (a big clean synthetic dataset selects a small
    stable k, not the ceiling-by-noise the old raw BIC did).
  - A MECHANICAL support-driven-k test: k RESPONDS UPWARD when a genuine well-supported cluster is
    added (2 blobs→k=2, 3 blobs→k=3) and DOWN with fewer; and a genuinely tiny cluster (< both
    support arms: < 5% AND < 150 obs) is floor-rejected. This must FAIL if k were pinned to a
    constant.
  - Existing tests that assert old raw-space behavior (e.g. `MIN_COMPONENT_WEIGHT_FRAC == 0.05`
    exact, the k-mismatch fixture, `RADIUS_SCALE_M` references) reconciled to the new model.
- `py -m src.utils.simplification_limits` passes on every touched `src/` path.
- Region unit suite green: `py -m pytest tests/unit/physics/layer2/test_property_mixture.py
  tests/unit/physics/layer2/test_mixture_stability.py -q`.

## Allowed Scope
- `src/physics/layer2/property_mixture.py` (fit space, support criterion, k_range, constants).
- `src/physics/layer2/mixture_stability.py` (radius-axis normalization → `LOG_RADIUS_SCALE`;
  keep everything else). If `RADIUS_SCALE_M` is exported/imported elsewhere, keep a name that
  callers/tests can import (rename to `LOG_RADIUS_SCALE` and update the two test files + any
  import; the scripts import it in `scripts/f12_held_out_stability.py` — update that import/print).
- `tests/unit/physics/layer2/test_property_mixture.py`, `test_mixture_stability.py` (pre-authorized
  to reseed/rewrite the scenarios the behavior change invalidates).
- MAY touch `scripts/f12_held_out_stability.py` ONLY to keep its `RADIUS_SCALE_M`→`LOG_RADIUS_SCALE`
  import/print consistent (no logic change). Do NOT change its DB path or run logic.

## Specific Exclusions
- Do NOT change `src/physics/layer2/corner_descriptors.py` (the descriptor stays raw
  `(radius_m, lateral_g)`; the log-transform lives INSIDE property_mixture). [#638]
- Do NOT change `regime_rollup.py`, `segment_classifier.py`, `build_regime_rollup.py` logic — they
  call `posterior_membership`/`fit_property_mixture` with raw descriptors and MUST keep working via
  encapsulation (verify they still import/run; the commander re-runs the rollup in G3). [#625 owned]
- Do NOT weaken/remove the k-mismatch auto-fail or change `F12_AGREEMENT_THRESHOLD`. [pre-ruling]
- No production defaults / `circuits.yaml` / gold-bundle changes. Do NOT run the real DB.

## Constraints
- `MixtureFit` fields (do not change the dataclass shape callers rely on): `gmm: GaussianMixture`,
  `k: int`, `scaler: StandardScaler`, `bic_scores: dict[int,float]`. `fit.scaler` must be the
  scaler fit on the LOG-space descriptors, so `scaler.inverse_transform(gmm.means_)` yields
  `(log10 radius, lateral_g)` — the gate depends on this.
- Keep `fit_property_mixture` deterministic (thread `random_state` to every GMM).
- POSIX-form verification commands; run from the worktree (`C:/Programs/f1-638`), where
  `import src.physics...` resolves to the worktree (editable-install `.pth` trap: only cwd-inside-
  worktree is safe — pytest is cwd-safe).

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/property_mixture.py::fit_property_mixture`,
  `mixture_stability.py::component_agreement_stat/_normalize`.
- **Capability:** property-mixture-fit; f12-holdout-stability.
- **Constraints:** support-driven k; F12 falsifiable (discriminating test preserved); no evo import.
- **Decision anchors:** `decision:regime_readiness_rubric` (#512, circuit-dominated structure);
  the fix decision recorded in DIAGNOSIS.md (log space + OR-support + cap 4 + log gate scale).
- **Evidence expectations:** discriminating synthetic test PASS/FAIL intact; region suite green.

## Deliverable Path Check
- Committed: `src/physics/layer2/property_mixture.py`, `src/physics/layer2/mixture_stability.py`,
  `tests/unit/physics/layer2/test_property_mixture.py`,
  `tests/unit/physics/layer2/test_mixture_stability.py` (and maybe
  `scripts/f12_held_out_stability.py`) — all verified NOT gitignored (`git check-ignore` exit 1).
- Local-only: your `IMPLEMENTER_RESULT` at
  `.agent-work/638-f12-stability-rework/crew-handoffs/g2-implement-result.md` (under `.agent-work/`).

## Required Evidence
- Full output of the region suite command below (paste it).
- Output of `py -m src.utils.simplification_limits <touched paths>`.
- The exact new/changed constants and their frozen-rationale comments.
- Confirmation the discriminating test still fails on shifted data (show that test passing, i.e.
  it correctly asserts FAIL on the shifted scenario).

## Verification Commands
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -c "import src.physics.layer2.property_mixture as m; print(m.__file__)"   # must be under C:\Programs\f1-638
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/layer2/test_mixture_stability.py -q
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits src/physics/layer2/property_mixture.py src/physics/layer2/mixture_stability.py
```

## Suggested Model Tier
stronger — multi-file coherent change (fit space + gate + tests), falsifiability must be preserved,
encapsulation must not break 3 callers.

## Authority
The fix design (all four choices + the three frozen constants) is DECIDED by the commander from
real-data diagnosis — implement it, do not substitute a different approach. You DO own: the exact
encapsulation of the log-transform, the precise test rewrites, and clean code. If you believe a
frozen constant or the design is wrong, STOP and return it as a blocker with evidence — do not
silently change it.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; an excluded file must change; the region suite
cannot be made green without weakening the gate; a frozen constant appears wrong; the discriminating
test cannot be kept able-to-fail.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/638-f12-stability-rework/crew-handoffs/g2-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence (pasted suite + simplification-limits
output), assumptions, stop conditions hit, out-of-scope observations, and workflow feedback.
