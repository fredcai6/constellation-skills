# Mission Frame — #638 F12 held-out-circuit stability rework

Map note: `physics/layer2` has no Cartographer packet; the durable map is
`docs/physics/625-phase1-segmentation-substrate.md` + `docs/agents/ORCHESTRATOR_CONTEXT.md`
(Physics subsystem: rigorous, truth-anchored, units/bounds/invariants explicit). Frame is
substantive (research fix), not trivial.

## Intent
Make the Phase-1 corner property-class mixture substrate stable enough that the mandatory F12
held-out-circuit gate earns a GENUINE PASS — by fixing the MODEL (k-selection), ideally leaving
the F12 gate itself frozen and untouched — so Phases 2/4 can load-bear on it. An honest
"instability is fundamental" is a complete fallback, but only after exhausting fixes.

## Affected Capabilities
- `property-mixture-fit` (`fit_property_mixture`) — BIC+support-floor GMM selection over
  standardized `(radius_m, lateral_g)`. THE locus of the instability; the fix lands here.
- `f12-holdout-stability` (`check_holdout_stability` / `component_agreement_stat`) — the
  falsifiable gate. Ideally FROZEN (constants, k-mismatch auto-fail, distance threshold, and
  the discriminating synthetic test all preserved). A PASS earned by fixing the model, not the
  gate, is the cleanest satisfaction of pre-rulings #1/#2.
- `regime-rollup` (`build_regime_rollup.py`) — consumes one shared `fit_property_mixture` fit
  (currently k=3); its verdict metadata must be re-run to reflect the new F12 state.

## Structural Anchors
- `src/physics/layer2/property_mixture.py` — `fit_property_mixture`, `MIN_COMPONENT_WEIGHT_FRAC`
  (pre-registered floor), `MixtureFit`. FILE-level.
- `src/physics/layer2/mixture_stability.py` — gate; frozen `RADIUS_SCALE_M`/`LATERAL_G_SCALE`/
  `F12_AGREEMENT_THRESHOLD`.
- `scripts/f12_held_out_stability.py`, `scripts/build_regime_rollup.py` — real-data drivers.
- `tests/unit/physics/layer2/test_property_mixture.py`, `test_mixture_stability.py` (holds the
  load-bearing discriminating synthetic test).
- Real data: `C:/Programs/f1Brainz/data/damage_integrals.db` `grip_bin_obs` (612,615 rows, 22
  circuits) — READ-ONLY.

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — layer2 must not import evo.
- Pre-registered support-driven k (property_mixture pre-ruling #1): k stays data/support-driven,
  not silently hardcoded to a constant.
- F12 must stay falsifiable (launch pre-ruling #2): discriminating synthetic test preserved,
  every threshold/constant frozen BEFORE the real-data run.
- No production defaults / `circuits.yaml` / gold-bundle changes. NEVER commit `data/*.db`;
  `git checkout -- data/` after any DB-touching run. Read DB READ-ONLY.
- Physics evidence bar: units/bounds/invariants explicit; truth-anchored.

## Decision Anchors & Decision Pressure
- `decision:regime_readiness_rubric` (#512): capability structure is circuit-DOMINATED
  (frac_circuit 0.44–0.65 vs frac_team 0–4%). Grounds the leading hypothesis that
  descriptor structure differs by circuit → circuit-conditional/hierarchical mixture may be the
  right fix. Note: the descriptor here is GEOMETRIC (radius, lateral_g = track layout), so
  property-class LOCATIONS should be universal; only mixing WEIGHTS vary by circuit.
- DECISION PRESSURE (resolved by G1 diagnosis, reconciled against launch-order preference
  cheap→expensive; float only if fundamental / gate-weakening required): which fix —
  (a) sample-size-robust / subsampled model selection, (b) held-out/CV selection,
  (c) narrower/regularized k_range, (d) circuit-conditional/hierarchical. Prefer the simplest
  that earns matched-k + sub-threshold locations across all 5 splits.

## Claims / Evidence Surfaces
- CLAIM to overturn: "the substrate's k is stable across circuit-composition splits." Current
  evidence: `docs/physics/625-f12-holdout-stability.json` = FAIL 0/5. Re-confirmed by the new
  real-data F12 run (the payoff evidence) + synthetic discriminating test still PASS/FAIL.
- Location-stability: once k matches, `component_agreement_stat` < `F12_AGREEMENT_THRESHOLD`
  (1.0) — the existing distance half of the gate IS the location-stability check.

## Map Confidence / Staleness / Disputes
- No packet map for layer2 → the fix is grounded in direct code + real-data diagnosis, not a
  trusted map. G1 diagnosis is the verification step that de-risks this.

## Out of Scope
- evo_predictor / gold bundle / production defaults / circuits.yaml.
- The `*_distance_share` top-level split (mixture-independent) — unaffected by k.
- Broader Phase-2/4 consumption (future phases).
