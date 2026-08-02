# Review Result — #525 G1 audit (evidence-only)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review (audit verification)` — issue #525, branch `feat/physics-units-audit-525`.
Verifying the evidence-only physics units-convention audit (`AUDIT_MAP.md`,
`AUDIT_DISPOSITIONS.md`) against source. No diff — independent claim verification.

## Result
**APPROVE**

(Engine survey: 11/11 checks pass, 0 open fails, consolidated APPROVE.)

---

## Per-check findings (handoff close criteria 1–5)

### 1. Map accuracy — PASS
Read the cited code myself for all three load-bearing seams; the map matches source exactly.

- **Lateral two-producer seam:** `lateral_view.py:50-51,66-68` — `LateralViewResult.A0/A2`
  documented g-units, `grip_coef = A0 + A2·v²` dimensionless; the fit is ρ-free
  (`mu_obs = |a_lat|/(g·cos θ)` flat at L141, banked inverse at L139, design `[1, v²]` at
  L143). vs `physics_data_models.py:237-249` — `lateral_capability`: `mechanical = A0·tire_factor·g_track`,
  `aero = A2·rho·speed²` (m/s², ρ explicit, expects A0 in m/s²). vs
  `car_prior.py:_assemble_lateral (483-521)` — `s0 = G_MS2`, `s2 = G_MS2/air_density`,
  `A0_param = A0_mu·s0`, `A2_param = A2_mu·s2`, Jacobian `diag(s0,s2)` applied to covariance
  (L505), defaults pass through UNCONVERTED (L511-514), `# TODO(#525)` marker at L470. The
  ρ-cancellation note (map L60-61) matches the source comment at `car_prior.py:455-457`.
- **Longitudinal p_max/theta_P seam:** `estimate_store.py:253` stores `p_max=float(pd_.p_max)`
  (total watts); `car_prior.py:_build_longitudinal:344` `specific_power = p_max_mu / MASS_KG`
  (watts→W/kg), with the docstring (L336-341) confirming store=total-W vs consumer=W/kg —
  the #518 seam. Matches map.
- **G_MS2 claim (the audit's correction of the issue framing):** `G_MS2 = 9.81` is defined
  exactly ONCE at `braking_fit.py:36` and is the *only* `G_MS2` occurrence in that file
  (unused in braking's own math — braking fits natively in m/s²); imported by
  `car_prior.py:82` and used only for the *lateral* conversion (L483-484). The real
  duplication is the scattered `9.81`/`_G` literal across ≥13 sites I confirmed via grep
  (`lateral_view:70,86`, `braking_view:135`, `traction_view:80`, `power_drag_view:96`,
  `coast_view:88`, `decoupled_longitudinal:81`, `physics_simulator:484`, `lateral_report:21`,
  `session_lateral:18`, `session_braking:24`, `session_traction:27,165`, `session_estimator:95`).
  The audit's "defined once but mis-homed, not duplicated" correction is accurate.

### 2. Blast-radius honesty (CRITICAL / LOAD-BEARING) — PASS
Independently traced the live path from source (not from the audit's prose). The claim that
the live `sim_evaluator`/`fit_batch` path does NOT route through `car_prior` and does NOT read
the g-unit `EstimateStore` is **TRUE**:

- `fit_batch.py:36-76` (`run_batch`) imports only `fit_driver` + `FitStore` (L14-15); calls
  `fit_driver_fn(...)` → `store.upsert(rec)`. No `car_prior`, no `EstimateStore`.
- `session_fit.py`: `fit_driver` (L163, params built L239) and `fit_session_full` (L296,
  params built L401-403) both build params via `ParameterEstimator(cfg).estimate_parameters`.
  `session_fit` imports `ParameterEstimator` (L169/L334) and `CapabilityEnvelope` (L172) but
  NOT `car_prior` / `EstimateStore`.
- `parameter_estimator.py`: imports `LateralEnvelopeFit` (L23), `self.lateral_fit =
  LateralEnvelopeFit(self.config)` (L45), calls `self.lateral_fit.fit_envelope(...)` (L285) —
  convention A m/s². No `car_prior` / `EstimateStore`.
- `sim_evaluator.py:evaluate_session (169)` imports `fit_session_full` + `PhysicsSimulator`
  (L194,196), calls `fit_session_full(...)` (L218) then `simulator.simulate_lap(track_df,
  full.params, ...)` (L243). The only `FitStore` import sits in the `__main__` CLI block
  (L302), NOT the evaluate path. No `car_prior` / g-units anywhere on this path.
- Corroboration: a grep for `car_prior`/`build_car_ceiling`/`EstimateStore` consumers returns
  only `utilization/` (characterize, regime_utilization) and `layer2/` (pool_driver,
  estimate_batch, decoupled_braking_input) — never `fit_batch`, `session_fit`, `sim_evaluator`,
  or `physics_simulator`. The g→m/s² conversion is provably C1-utilization-path-only.

This is exactly the from-memory class of claim that got #522's first fix blocked; here it is
confirmed from source. The A-vs-B blast-radius split (A touches the live path + blessed
fixtures; B leaves them untouched) follows correctly.

### 3. ρ call soundness — PASS
ρ is genuinely absent from the lateral *fit*: `lateral_view.py:139,141,143,66-72` carry no ρ
term anywhere (de-conflation, design matrix, grip_coef, a_lat_max). ρ enters only at the
consumer (`physics_data_models.py:245 aero = A2·rho·speed²`) and is exactly cancelled at the
boundary (`car_prior.py:484,496` → `A2_param·rho == A2_g·G`, exact because the same
`air_density` flows downstream, L455-457). Therefore adding/removing ρ is a symbolic identity,
not a refit — no `lstsq`/bootstrap re-run is implied. The "pure representation, NO refit"
verdict (Recommendation 2 / OT-2) holds. The audit's contrast (drag DOES bake ρ via the
design matrix, but #525 does not propose changing it) is correct and appropriately scoped.

### 4. Completeness — PASS
All six channels cover every producer and consumer with `file:symbol` + unit, verified against
source: LATERAL (lateral_envelope + lateral_view → lateral_capability/simulator/CapabilityEnvelope/
apex/friction), LONGITUDINAL/POWER (longitudinal_fit + power_drag_view → drag_acceleration/
_compute_drive_accel/_power_accel), BRAKING (braking_fit:69-71 + braking_view:50-51 → a_brake
`physics_data_models:289-291`, braking_capability `capability_envelope:123` — all m/s²/1·m⁻¹,
consistent), TRACTION (traction_fit:66-68 + traction_view:61-62 → a_trac `:329-331`,
traction_capability `:118` — consistent), COAST (coast_view.coast_decel:48 ρ-explicit → car_prior
θ_R passthrough → simulator rolling), TERRAIN (terrain.py rad/m/dimensionless). A glob of all
60 `src/physics/**` files confirms NO additional force channel — `friction_coupling`/`apex_extract`
are consumers; `capability`/`ribbon`/`segment_classifier` produce no units-bearing model params.
The map's "Channels beyond listed set: None found" is accurate.

### 5. Recommend-not-decide — PASS
`AUDIT_DISPOSITIONS.md:4-5` states "I recommend; I do not decide. The canonical-convention
call and the in-scope-vs-routed split are ruled by the human at the decide-fix checkpoint."
Recommendation 1 recommends B with an honest both-sides blast-radius enumeration and tags the
convention `decide-at-checkpoint` (OT-1, summary table). Recommendation 2 flags ρ
`decide-at-checkpoint` without picking. Disposition tags consistently separate `fix-local`
(labelling, constant dedup) from `decide-at-checkpoint` (convention, where-to-convert) from
`route-out`. The artifacts recommend; they do not decide scope.

---

## Handoff compliance
Yes. The audit delivered the two required artifacts: a producer→consumer unit-convention map
covering every channel with `file:symbol(:line)` + unit + a one-line matrix, and a
disposition doc with the 7-item overload inventory, the A-vs-B recommendation (B), the honest
blast-radius, and the ρ representation-vs-refit call. It treated the architecture packet as an
index and re-verified each claim against source. Evidence-only; stop conditions respected.

## Scope drift
None. `git status --porcelain src/ tests/` is empty on `feat/physics-units-audit-525` — no
tracked source or test file changed. Deliverables are the two `.agent-work/525/*.md` artifacts
+ the implement-result/plan. Every specific exclusion (no code change, no convention decided,
no refit proposed in-scope, no evo coupling) is honored.

## Evidence verdict
Sufficient and accurate. Required evidence (the two artifacts + clean git status) is present
and demonstrates the claims. I spot-checked >12 distinct `file:symbol:line` citations against
source — all accurate, none overstated. The audit's central load-bearing fact (live-path
blast radius) was re-derived independently and confirmed.

## Code/doc quality
N/A for code (evidence-only). Doc quality of the artifacts is high: precise citations, the
two-store framing made explicit, and the issue's imprecise "duplicated G_MS2" framing
corrected against source rather than parroted.

## Map impact verdict
- **Evidence supports claimed change:** Yes — every convention/blast-radius claim is backed by
  a source citation I re-verified.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import` honored (no evo
  import); read-only.
- **Notes match the diff:** N/A (no diff); the Map Impact notes in the implement-result match
  what the artifacts actually contain — `claim:lateral_car_prior_boundary_conversion` verified
  at `car_prior.py:483-505` (C1-path-only), `decision:ideal_lap_sim_two_sided_evaluator`
  consistent with source.
- **Decision candidates surfaced:** Yes — the canonical-lateral fork and the longitudinal
  where-to-convert fork are surfaced for the human checkpoint, recommended not decided.
- **Durable context routed:** Yes — OT-6/OT-7 and the friction_coupling dead-path are routed
  out as triage candidates rather than silently fixed.

## Reconciliation check
No divergence requiring Commander reconcile. The audit *flags* packet/issue-vs-source drift
(the G_MS2 mis-home correction) rather than introducing any, and confirms the packet's
two-producer-split description matches source. This is the correct posture for an audit gate.

## Blockers
- none — confirmed after review: all five close criteria verified from source; the CRITICAL
  blast-radius claim re-derived independently and found true; no src/tests changed.

## Out-of-scope observations
- **OT-6:** `k_tire` default mismatch (0.01 Layer-1 vs 0.0 `car_prior`) — modelling default,
  not a unit overload. Route to a follow-up issue (triage candidate tc1).
- **OT-7:** `DEFAULT_RHO = 1.20` (`session_fit.py:58`) vs `reference_density_kg_m3 = 1.225`
  (`physics_config.py:91`) — default-value inconsistency, not a unit overload. Route out (tc2).
- **friction_coupling.py** is documented-superseded by `CapabilityEnvelope` (its docstring
  L5-6) yet still consumes `lateral_capability` — a dead-path cleanup candidate, not units (tc3).

These three are correctly identified by the audit itself and tagged route-out; surfacing here
so Commander can route them without re-reading the artifact.

## Workflow Feedback
This is workflow signal, not project signal.

- **Handoff gaps:** The handoff was unusually well-specified for verification — it named the
  exact seams, line-anchored the load-bearing checks, and explicitly framed the blast-radius
  as the #522-class risk to re-derive from source. That framing is what made the review
  efficient. One residual gap: the handoff (criterion 2) cited `lateral_envelope.py` /
  `physics_data_models.py:lateral_capability` for the convention-A side, but the *binding*
  consumer formula I needed to verify the A0-in-m/s² assumption was `lateral_capability` at
  `physics_data_models.py:237-249` specifically — the handoff's `lateral_envelope.py` pointer
  is the producer, not the shared consumer. Minor; both were easy to locate.
- **Context rediscovered:** None of substance — the implement-result and AUDIT_MAP front-loaded
  the two-store framing (`FitStore` m/s² vs `EstimateStore` g-units) that the implementer noted
  had to be reconstructed, so by review time it was already explicit. I did have to confirm the
  `sim_evaluator` FitStore import (L302) was in the CLI block, not the evaluate path, to be sure
  the live path is clean — worth a one-line note in a future handoff but not a defect.
- **Instructions improvised around:** The reviewer skill's `append` subcommand takes the *new*
  item's id as its positional argument, but the template wording ("append a check per rule")
  reads as if appending children under `r4-quality`; my first attempts passed `r4-quality` as
  the positional and were REFUSED ("already exists"). I improvised by appending the five
  load-bearing checks as new top-level items `r6`–`r10` (parenting `r4-quality` to them in
  findings), which the engine accepted and consolidated cleanly. Worth clarifying in the skill
  whether load-bearing checks should be top-level appends or child checklists.
- **What would have made this easier:** One concrete change — the survey template could ship a
  documented convention for "append N load-bearing checks from the handoff's close criteria"
  (id scheme + whether top-level or child), since this gate's real verification work lived
  entirely in those appended checks, not the six stock r0–r5 items.

## Return status
`complete`
