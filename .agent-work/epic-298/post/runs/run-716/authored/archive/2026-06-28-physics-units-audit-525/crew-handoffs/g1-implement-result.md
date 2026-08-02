# Implementation Result — #525 G1 (evidence-only units audit)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement (audit)` — issue #525, branch `feat/physics-units-audit-525`.

## Completed slice
A complete, source-grounded producer→consumer unit-convention audit of every physics
model parameter across all channels in `src/physics/**`, delivered as two markdown
artifacts plus this result. **No code written** (inspection-only gate). Every convention
claim was re-verified by reading the cited source; the architecture packet was used only as
a starting index.

## Scope
**Files changed (artifacts only):**
- `.agent-work/525/AUDIT_MAP.md` — producer→consumer unit-convention map, every parameter,
  every channel, with `file:symbol(:line)` citations + the exact formula + unit each side assumes.
- `.agent-work/525/AUDIT_DISPOSITIONS.md` — overloaded-term inventory + A/B lateral
  recommendation + honest blast-radius + ρ-in-aero disposition.
- `.agent-work/525/crew-handoffs/g1-implement-result.md` — this file.
- `.agent-work/525/crew-handoffs/g1-implement-plan.json` — the implementer engine plan.

**Specific exclusions touched:** `no` — no `src/` or `tests/` file edited; no code fix, no
rename, no test edit; no refit proposed as in-scope; no canonical convention *decided* (only
recommended); no evo-region coupling introduced.

## Behavior changed
`no` — evidence-only. Zero runtime/behavior impact.

## Deliverable findings (summary for the checkpoint)

### A/B lateral recommendation
**Recommend Convention B (m/s² canonical at the consumer) + unit-suffixed field/column names
+ co-located unit headers.** Smallest, lowest-risk blast radius; the single g→m/s² conversion
already exists at `car_prior._assemble_lateral` and is tested. The user is not hard on
unitless, so B satisfies "best de-overload with acceptable blast radius."

### Independently-confirmed blast-radius fact (the #522-blocking fact)
**Confirmed from source (not memory):** the live `sim_evaluator` / `fit_batch` path does
**NOT** consume the g-unit EstimateStore and does **NOT** route through `car_prior`.
- `fit_batch.run_batch → fit_driver → session_fit.fit_session_full` (`session_fit.py:239`
  → `ParameterEstimator.estimate_parameters` → `LateralEnvelopeFit`, convention A m/s²) →
  `record_from_params` writes the FitStore in m/s² (`session_fit.py:89`).
- `sim_evaluator.evaluate_session` (`sim_evaluator.py:194–243`) calls `fit_session_full(...)`
  then `PhysicsSimulator.simulate_lap(track_df, full.params)` — native m/s², no g-units.
- The g→m/s² conversion lives ONLY on the C1 utilization path
  (`characterize → car_prior.build_car_ceiling → CapabilityEnvelope → regime_utilization →
  simulate_lap`, `regime_utilization.py:508,579`).
- **Consequence:** Option A (g-units everywhere) touches the proven sim path + blessed
  regression fixtures and forces a numeric re-baseline; Option B leaves them untouched.

### ρ-in-aero disposition
**PURE REPRESENTATION / CONVERSION change — NO refit required.** ρ is not in the lateral
*fit* (convention B's `μ_obs = |a_lat|/(g·cos θ)` is ρ-free, `lateral_view.py:141`); it
appears only as a deterministic multiplier in the consumer's `A2·ρ·v²` and is exactly
cancelled at the `car_prior` boundary (`A2_param = A2_g·G/air_density`, exact because the
same ρ flows downstream). Removing it is a symbolic identity, not a re-derivation — so it
does **not** trip the stop-and-route refit trigger. Recommended to bundle with the
convention ruling (decide-at-checkpoint), not because it needs a refit but because the
cleanest form depends on A-vs-B.

### Overloaded-term inventory (7 items)
- **OT-1** lateral `A0`/`A2` g-units (lateral_view/EstimateStore) vs m/s²
  (LateralParameters/simulator/FitStore) — same names, two meanings. *labelling fix-local;
  convention decide-at-checkpoint.*
- **OT-2** ρ-in-aero present (A) vs absent (B), round-trip cancelled. *pure representation,
  decide-at-checkpoint with convention.*
- **OT-3** `G_MS2` defined in `braking_fit.py:36` (unused there), imported by `car_prior`
  for the *lateral* conversion; plus `g=9.81` re-declared in ≥8 places. **The issue's
  "duplicated G_MS2" framing is slightly off:** `G_MS2` is defined once but mis-homed; the
  real duplication is the scattered `9.81`/`_G`. *fix-local (single GRAVITY constant).*
- **OT-4** `MASS_KG=808.0` defined twice (`longitudinal_fit.py:44` + `session_fit.py:57`).
  *fix-local (single def, imported).*
- **OT-5** longitudinal EstimateStore keeps RAW PHYSICAL units (`cda` m², `p_max` W) while
  the consumer wants ENGINE units (theta_D m⁻¹, theta_P W/kg); the #518 bug was the missing
  `/MASS_KG`. *labelling fix-local; where-to-convert decide-at-checkpoint (longitudinal
  sibling of the lateral fork).*
- **OT-6** `k_tire` default 0.01 (Layer-1) vs 0.0 (car_prior) — modelling default, not units.
  *route-out.*
- **OT-7** `DEFAULT_RHO=1.20` (session_fit) vs `reference_density_kg_m3=1.225` (config) —
  default-value inconsistency. *route-out.*

### Channels beyond the listed set
None found. The handoff's six channels (lateral, longitudinal/power, braking, traction,
coast, terrain) are complete. **Braking and traction are convention-consistent** across both
producers (Layer-1 fit + layer2 view) and the consumer — lateral is the **only** channel
with a producer convention split. Terrain (radians/meters) and coast (m/s²/m²) are
consistent. The material cross-cutting finding the list did not name: the **two stores**
(`FitStore` vs `EstimateStore`) carry the same parameter names in different unit conventions
— the structural root of OT-1/OT-5.

## Map Impact
- **Structural anchors touched:** none modified. Audit spans `struct:physics`,
  `struct:physics.layer2`, `struct:physics.utilization` (read-only).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored
  (no evo import seen/added). `claim:lateral_car_prior_boundary_conversion` — **verified
  against source**: the `_assemble_lateral` g→m/s² conversion (`car_prior.py:483–505`) is
  the exact surface G2 retires/generalizes; it is C1-path-only.
- **Decision candidates / resolved decisions:** the canonical-lateral fork (A vs B) and the
  longitudinal where-to-convert fork (OT-5) are surfaced for the human's decide-fix
  checkpoint — **recommended B**, not decided. `decision:ideal_lap_sim_two_sided_evaluator`
  (records both car_prior boundary conversions) confirmed accurate vs source.
- **Trust limitations / drift found:** the issue's "duplicated `G_MS2`" framing is imprecise
  (defined once, mis-homed) — see OT-3. The packet's two-producer-split description
  (`utilization` node) matches source.
- **Triage candidates:** OT-6 (`k_tire` default mismatch), OT-7 (`DEFAULT_RHO` vs config
  density) — route out as non-units follow-ups.

## Test mode
**Required:** `evidence-only`
**Satisfied:** `yes` — no `src/`/`tests/` edits; deliverables are the two markdown artifacts.
`git status --porcelain src/ tests/` is empty.

## Evidence

```bash
py -c "import pathlib,sys; sys.exit(0 if (pathlib.Path('.agent-work/525/AUDIT_MAP.md').exists() and pathlib.Path('.agent-work/525/AUDIT_DISPOSITIONS.md').exists()) else 1)"
git status --porcelain src/ tests/
```

**Result:** `pass` — both artifacts exist; `git status --porcelain src/ tests/` returns empty
(exit 0, no tracked source changed). Verified via the engine command-check postconditions on
gates m2/m3/m4.

## TDD evidence, if required
`n/a` — evidence-only gate, no test-first requirement.

## Docs/contracts touched
- None in `src/`/`docs/`. The two `.agent-work/525/*.md` audit artifacts are the
  deliverables; G2 (post-checkpoint) will wire the unit-map doc + `docs/AGENT_GUIDE.md`
  reference + the output-level guard per `PROBLEM_STATEMENT.md`.

## Assumptions
- "Producer/consumer" = code that *constructs/writes* a parameter vs code that *reads* it for
  computation; store rows count as a persistence boundary, examined for both.
- The `# TODO(#525)` marker in `car_prior._assemble_lateral` (L470) is the conversion surface
  G2 will retire/generalize — taken as confirmation, then re-verified against the surrounding code.
- Read-only: I did not run the physics test suite (no source changed; running it proves nothing
  about an evidence-only gate). I read the relevant tests to source the blast-radius.

## Stop conditions hit
- None. No cited seam was unreadable; no question required a code change to answer; no
  decision exceeded "recommend, don't decide."

## Out-of-scope observations
- OT-6 (`k_tire` 0.01 vs 0.0) and OT-7 (`DEFAULT_RHO` vs `reference_density_kg_m3`) are real
  inconsistencies but not unit overloads — recommend routing to follow-up issues, not G2.
- `friction_coupling.py` is documented-superseded by `CapabilityEnvelope` (its docstring,
  L5–6) yet still imports/consumes `lateral_capability` — a dead-path cleanup candidate
  (not units).

## Workflow Feedback
This is workflow signal, not project signal.

- **Handoff gaps:** the **Map Anchors** named "the duplicated `G_MS2` constant" as a known
  overload. Source shows `G_MS2` is defined exactly once (`braking_fit.py:36`) — it is
  *mis-homed*, not duplicated; the real duplication is the scattered `9.81`/`_G`. The handoff
  also (correctly) told me to treat the packet as an index and verify from source, which is
  the only reason I caught this. A handoff that asserts a specific overload should say
  "verify the exact form" — I treated it as a hypothesis and confirmed the precise shape.
- **Context rediscovered:** the existence of **two distinct stores** (`FitStore` vs layer2
  `EstimateStore`) carrying the same param names in different conventions is the structural
  root of the whole audit, but it had to be reconstructed by reading `session_fit`,
  `estimate_store`, and `fit_store` — the anchors named the seams individually without
  flagging "these two stores disagree on units," which is the single most important framing
  for the blast-radius. The packet's utilization node *does* describe the two-producer split,
  which helped.
- **Instructions improvised around:** the bundled `IMPLEMENTER_PLAN.template.json` m0 step
  uses a *postcondition* `c1` with `check: null`, but the engine's `attest` defaults to
  *preconditions*; the first `attest m0-context --cond c1` was REFUSED until I added
  `--which postconditions`. Minor, but the template + engine default are mismatched for the
  context-read step. I added `--which postconditions` and proceeded.
- **What would have made this easier:** one line in the handoff's Map Anchors —
  "the Layer-1 `FitStore` and the layer2 `EstimateStore` carry `A0`/`A2` in *different* unit
  conventions (m/s² vs g-units); the live sim path reads the former" — would have front-loaded
  the load-bearing fact instead of leaving it to be independently confirmed (which was the
  point of the gate, so this is a nice-to-have, not a defect).

## Return status
`complete`
