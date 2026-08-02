# Mission Frame — #525 physics units-convention audit + unify

## Intent
De-overload/disambiguate physics model parameter unit conventions producer→consumer:
audit every channel's conventions, **label the variables** (unit-suffixed fields + clean
co-located headers), unify the two-producer lateral split onto one convention and
retire/generalize the #522 `car_prior` patch, add a durable unit-map doc wired into agent
context with a review-update mandate, and one output-level guard. **Audit-first**, with a
human decide-fix checkpoint that (re)plans the fix gates from the audit evidence.

## Affected Capabilities
- **physics parameter measurement / capability API** — the per-channel producers
  (`lateral_view`, `LateralEnvelopeFit`, `longitudinal_fit`, `braking_fit`, the layer2
  views) and the shared `LateralParameters`/`PhysicsParameterSet` consumers feed the gg-v
  `CapabilityEnvelope`. This run unifies their unit conventions.
- **ideal-lap simulation** (`physics_simulator`, `sim_evaluator`) — consumes the params;
  the one output-level guard (ideal-lap top speed + corner cap in a physical band) lands
  on this surface via `tests/known_answer/test_published_f1_data.py`.
- **driver utilization (C1)** — `car_prior.build_car_ceiling` bridges store→params→envelope;
  the #522 `_assemble_lateral` and #518 `_build_longitudinal` boundary conversions are the
  exact patches this run generalizes/retires.

## Structural Anchors
- `struct:physics` (container) — `physics_data_models.py` (`LateralParameters`,
  `LongitudinalParameters`, `BrakingParameters`, `TractionParameters`,
  `PhysicsParameterSet`), `physics_simulator.py`, `sim_evaluator.py`,
  `lateral_envelope.py` (convention-A producer), `longitudinal_fit.py` (`MASS_KG`),
  `braking_fit.py` (`G_MS2` — duplicated constant), `capability_envelope.py`.
- `struct:physics.layer2` (component) — `lateral_view.py` (convention-B g-unit producer),
  `session_lateral.py`, `estimate_store.py`, the per-channel views (`braking_view`,
  `traction_view`, `power_drag_view`, `coast_view`).
- `struct:physics.utilization` (component) — `car_prior.py` (`_assemble_lateral`,
  `_build_longitudinal` — the boundary conversions).
- `tests/known_answer/test_published_f1_data.py` — the guard surface.
- `docs/architecture/reference/physics-unit-conventions.md` (new durable unit-map table),
  `docs/AGENT_GUIDE.md` (single top-level direct reference + review-update mandate).

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — audit/unify stays physics-region; no
  evo-region import introduced.
- **Physics model change → highest-applicable L1–L4 truth evidence, units/bounds/invariants
  explicit** (engine-config + CREW_CONTEXT). A units-representation change is an exact fit
  for L2 known-answer + L3 limit-case evidence.
- **No behavior regression** — `sim_evaluator` (current evaluator), the C1 utilization path,
  and the published-F1 known-answer tests must all stay physical post-unification.

## Decision Anchors & Decision Pressure
- `decision:ideal_lap_sim_two_sided_evaluator` — records BOTH `car_prior` boundary
  conversions (G5 `p_max` watts→W/kg, G2 lateral g→m/s²). This run modifies/retires the
  lateral one → its **Review Trigger fires again** (reconcile must update the anchor).
- `decision:c1_driver_utilization_design` — the car_prior denominator; unaffected in intent
  but the lateral assembly is where the patch lives.
- **Decision pressure (forced to human at the decide-fix checkpoint, NOT pre-decided):**
  (1) the canonical lateral convention — A (unitless/g-coef everywhere, consumer moves,
  bigger blast radius incl. live `sim_evaluator`) vs B (m/s² at consumer, producers
  normalize up, smaller blast radius); user is not hard on unitless — choose by
  de-overloading value vs blast radius. (2) ρ-in-aero disposition — if unification needs a
  refit, STOP and route out vs fix-local. Both resolved at the checkpoint from audit
  evidence.

## Claims / Evidence Surfaces
- `claim:lateral_car_prior_boundary_conversion` (verified-by
  `tests/unit/physics/test_car_prior.py::test_tunnel_corner_cap_is_realistic`, cap
  63.19 m/s) — the exact surface this run retires or generalizes. The guard + region suite
  must re-confirm the tunnel cap and ideal-lap top speed stay physical after unification.

## Map Confidence / Staleness / Disputes
- `struct:physics` packet, `decision:ideal_lap_sim_two_sided_evaluator`, and
  `constraints.yml` were **reconciled in #522 (2026-06-27), high confidence** — no stale
  area requires a scout gate. The **audit gate (G1) IS the verification**: it reads source
  directly and produces the authoritative producer→consumer map, treating the packet as a
  starting index, not ground truth.

## Out of Scope
- Re-fitting the physics parameters (representation/alignment only).
- Evo/prediction composition (#509 P-phase).
- A units library (`pint`) or per-parameter typed-unit wrappers.
- A per-parameter magnitude-band test matrix (the guard is ONE output-level assertion).
