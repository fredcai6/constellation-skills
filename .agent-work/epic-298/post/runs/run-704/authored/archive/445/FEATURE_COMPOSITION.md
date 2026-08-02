# Phase-3 / feature composition — physics → prediction (epic #445)

PURPOSE REFRAME (user 2026-06-13): the point is PREDICTION. We do NOT need high-fidelity forces — we need
enough to BOUND PERFORMANCE so we can build CONFIDENCE in car-to-car and driver-to-driver capability. This
retroactively justifies the project's instincts: RELATIVE (not absolute — car-to-car needs only the delta);
COVARIANCE everywhere (confidence-in-capability IS the covariance); CAR-vs-DRIVER separation via the fleet
(grip proved it: envelope=car, utilization=driver).

## THE PREDICTION TARGET (user 2026-06-13, the core goal): regime-decomposed capability fingerprints
Fundamentally want: which teams are good in SLOW vs FAST corners, who has advantages in styles of CIRCUITS.
This is already latent in the physics decomposition:
- grip load model a_lat_max(v)=μ·(g + (k_df/m)·½ρv²): LOW speed → μ·g = SLOW-corner MECHANICAL grip (μ is
  the slow-corner fingerprint); HIGH speed → μ·k_df·v² = FAST-corner AERO grip (k_df is the fast-corner
  fingerprint). + longitudinal power/drag = STRAIGHT-line fingerprint. THREE regimes, all decomposed.
- CAR regime-capability VECTOR (± cov): [slow-corner grip (μ,traction) · fast-corner grip (k_df downforce) ·
  straight-line (power/drag) · degradation].
- CIRCUIT = a regime-MIX: its distribution of v²κ (lateral demand vs speed) = slow/fast-corner/straight
  share. Monaco/Hungary slow-heavy; Silverstone/Suzuka fast-heavy; Monza straights. (GRIP-3's per-circuit
  κ(s) profile DOUBLES as this circuit fingerprint.)
- DRIVER layer rides on top: utilization PER REGIME (some extract more in fast corners, some in braking).
- PREDICTION = match car regime-strengths to circuit regime-demands → "strong at Suzuka (fast corners),
  weak at Monza (straights)", with confidence scaling with clean-data coverage per car×regime.
- This TILTS the composition fork → DIRECT regime-descriptors as the features (interpretable: "strong in
  fast corners"), lap-sim demoted to VALIDATION (do the regime capabilities reproduce observed lap times?).

## The feature layer — two axes, bounded, with confidence
- CAR axis (teammate-shared → fleet tightens it): grip envelope per compound + degradation, deployed-power
  index, CdA — each RELATIVE + COVARIANCE-bearing. Bounds the car decomposed by WHERE: corners (grip),
  straights (power vs drag), tyre life (degradation).
- DRIVER axis (residual once car subtracted): utilization (% of envelope extracted), consistency, where
  they find time. Fleet does the subtraction (car = teammate-shared part, driver = what's left).
- CONFIDENCE scales with data automatically: many clean laps → tight envelope → confident comparison;
  sparse → wide bounds. Honest-covariance chain = no over-claiming on thin evidence.

## Composition fork (open, user to weigh)
1. LAP-SIM: capability envelope → point-mass lap sim (`src/physics/physics_simulator.py`, forward-backward)
   → bounded sector/lap time + propagated covariance → "car A is X±Y tenths, HERE". Interpretable, physical,
   bounding-flavored. Cost: sim adds its own modeling assumptions atop the honest descriptors.
2. DIRECT DESCRIPTORS: feed grip/power/drag/utilization straight to the evo predictor as features; let it
   learn the composition. Fewer assumptions, fully A/B-testable, less interpretable.
   Admiral lean: (2) first as the cleanest test of the original bet, (1) as interpretable enrichment/sanity.

## Closes the epic loop
Either route → relative capability deltas (car) + utilization deltas (driver), with confidence, become the
PHYSICS FEATURES INTO THE EVO A/B HARNESS = Phase 3 / the done-bar. Tested vs standing KPIs + the ~0.80
quali data-ceiling the whole bet targeted. The force survey built the feature INPUTS; this is where they
meet the predictor.

## Status of the force inputs (what each honestly provides — see MODEL_SCOPE)
- grip: μ_lat envelope + track-vs-tyre degradation (supplants compound γ-plateau); wear-ordering needs multi-race.
- drag: CdA~1.0 (lower-envelope, relative, track-varying); slipstream/cr/DRS-coast null.
- downforce: absorbed into grip k_df; separate identity parked (2026 active-aero trigger).
- power: deployed-power index + energy-management profiles; ICE-vs-deploy split parked (2026 trigger).
- mass: anchored nuisance (rules+fuel).
