# #638 — F12 held-out-circuit stability rework — problem statement (delegated reconciliation)

## The ask (frozen launch order `ShipD-638`)
Root-cause the F12 k-instability in the Phase-1 corner property-class mixture substrate, fix
it so the mandatory F12 held-out-circuit stability gate earns a GENUINE PASS (or a
differently-scoped, still-falsifiable, honestly-reported result), and re-run the rollup so its
verdict metadata reflects the new state.

## Baseline reconciled against actual code (delegated pre-check)
Verified the order's assumed baseline matches the merged code on my worktree base
`20ab4a78` — no already-shipped-fix surprise:
- `src/physics/layer2/property_mixture.py::fit_property_mixture` selects `k` by **in-sample
  BIC** over `k_range=(2,6)` on **standardized `(radius_m, lateral_g)`** descriptors, with a
  `MIN_COMPONENT_WEIGHT_FRAC=0.05` support floor and a k=1 all-rejected fallback. This is the
  exact selection the FAIL evidence exercised.
- `src/physics/layer2/mixture_stability.py::check_holdout_stability` runs 5 seeded 50/50
  circuit-NAME splits, fits `fit_property_mixture` independently per half, and reports
  `component_agreement_stat` (Hungarian-matched, raw-unit inverse-transformed, normalized by
  frozen `RADIUS_SCALE_M=50`, `LATERAL_G_SCALE=0.5`, threshold `F12_AGREEMENT_THRESHOLD=1.0`).
  A `k_a != k_b` mismatch returns `inf` (auto-FAIL before the distance test).
- FAIL evidence `docs/physics/625-f12-holdout-stability.json`: n_pass 0/5; every split's two
  halves disagreed on k (4v6, 6v2, 4v6, 5v3, 3v4) — reproduced byte-identical twice.

The FAIL is real and the code matches the order's description. The genuine open work is the
diagnosis + fix, which the order deliberately leaves to this run (pre-ruling #3).

## Protected intent (must survive)
1. **Earn the PASS, don't game the gate** (pre-ruling #1): a PASS must come from a genuinely
   more-stable model. Forbidden without floating: loosening `F12_AGREEMENT_THRESHOLD`; removing
   the k-mismatch auto-fail; fixing k to a constant WITHOUT then proving component LOCATIONS
   are also stable across splits.
2. **The gate stays genuinely falsifiable** (pre-ruling #2): any revision must keep the
   discriminating synthetic test (stable→PASS `TestCheckHoldoutStabilityDiscriminating`,
   shifted→FAIL) and freeze every threshold/constant before the real-data run. A weaker/
   unfalsifiable gate is an Admiral decision → STOP + float.
3. **Diagnose before fixing** (pre-ruling #3): characterize WHY k is unstable first, then pick
   the simplest fix that earns a real PASS. Preference order: regularized selection (cheap) →
   circuit-conditional/hierarchical (expensive). Leading hypothesis: circuit-conditional, but
   prove it.
4. **Fundamental-instability finding is a complete deliverable** (pre-ruling #4 / honest-null),
   but only after exhausting the candidate fixes → report + float.
5. `MIN_COMPONENT_WEIGHT_FRAC` / support-driven-k is a pre-registered Phase-1 choice
   (property_mixture pre-ruling #1); k must stay support-driven, not silently hardcoded.

## Fences / constraints
- No production defaults, `circuits.yaml`, or gold-bundle changes. `physics.layer2` must not
  import evo (`constraint:physics_region_no_evo_import`).
- NEVER commit `data/*.db`; `git checkout -- data/` after any run touching a DB (#632
  side-effect). Read the DB READ-ONLY.
- Sole-writer files this wave: `src/physics/layer2/*.py`, tests, scripts, updated rollup
  evidence under `docs/physics/`. Verdict at
  `C:/Programs/f1Brainz/.agent-work/epic-601/wave3-638-verdict.md` (main checkout).
- No reachable human. Float genuine gaps to the Admiral via the verdict file + stop.

## Success criteria (acceptance, from #638)
1. Root-cause the k-instability with evidence (test the candidates).
2. Implement a fix the evidence supports.
3. Re-run F12 real-data → genuine PASS (or honestly-scoped still-falsifiable result), with
   frozen constants and location-stability shown if k is fixed.
4. Re-run `scripts/build_regime_rollup.py`; confirm its verdict metadata updates.
