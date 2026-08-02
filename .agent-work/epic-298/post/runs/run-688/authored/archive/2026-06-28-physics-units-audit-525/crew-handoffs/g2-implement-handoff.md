# Implementer Handoff — #525 G2 (unify + label + guard)

## Gate
g2-implement — issue #525, branch `feat/physics-units-audit-525`

## Authoritative inputs (READ BOTH FIRST)
- `.agent-work/525/DECIDE_FIX_DECISIONS.md` — the ratified scope (this is binding).
- `.agent-work/525/AUDIT_MAP.md` — the exact `file:symbol`+line seams for every item below.
Do not re-derive seams from memory; the audit map has them with line numbers.

## Task
De-overload the physics parameter unit conventions per the ratified decisions. **Convention =
B (m/s² at the consumer): the shared `LateralParameters` consumer and the live
`sim_evaluator`/`fit_batch` path are UNTOUCHED.** The work is mostly labelling + constant
dedup + one targeted removal + one new guard. **No formula changes to the consumer, no
refit.** Each item cites the audit-map seam:

1. **OT-1 (lateral B + labels):** unit-suffix the g-unit lateral `A0`/`A2` on the producer
   (`layer2/lateral_view.py` `LateralViewResult`) and the `EstimateStore` columns
   (`layer2/estimate_store.py`) to make the g-unit convention explicit in the name; add a
   co-located unit header to `LateralParameters` (`physics_data_models.py:~207-249`, m/s²)
   and to `LateralViewResult` / the store schema (g-units). Promote
   `car_prior._assemble_lateral` (the B→m/s² conversion) to the ONE sanctioned, documented
   seam: retire the `# TODO(#525)` marker and replace it with a short docstring stating it is
   the canonical g→m/s² boundary. **Keep the conversion math identical.**
2. **OT-2 (ρ label, KEEP explicit — DELETE NOTHING):** ρ stays explicit in the consumer's
   aero term (`A2·ρ·v²` is physically correct). De-overload by NAMING: document that the
   five-view `A2` is a **session-ρ-folded grip slope** and that `car_prior` un-folds it via
   `/air_density` to the **ρ-independent aero coefficient** the consumer expects. This is
   header/comment/naming only — no math change, no ρ removal, no refit.
3. **OT-3 (one gravity constant):** create `GRAVITY_MS2 = 9.81` in a neutral home (a physics
   constants module — reuse an existing one if present, else add `src/physics/constants.py`).
   Retire the mis-homed `braking_fit.G_MS2` (have `car_prior` import the new constant) and
   replace the ≥8 scattered `9.81`/`_G`/inline-g literals listed in `AUDIT_MAP.md` "Shared
   constants" with imports of `GRAVITY_MS2`. Pure value-identical substitution.
4. **OT-4 (one MASS_KG):** keep the canonical `MASS_KG` in `longitudinal_fit.py`; make
   `session_fit.py:57` import it instead of redefining. Value-identical.
5. **OT-5 (longitudinal LABEL ONLY):** unit-suffix the store columns (`p_max_w`, `cda_m2`)
   and the consumer field (`theta_P` → `theta_P_w_per_kg`) + co-located headers stating the
   physical-vs-engine unit gap. **KEEP the `/MASS_KG` & `/(2·MASS_KG)` conversions at
   `car_prior._build_longitudinal` — do NOT relocate them to the store-write.** Update every
   producer/consumer reference to a renamed field consistently (no half-rename).
6. **OT-7 (one air-density fallback):** consolidate to ONE fallback constant, value **1.225**
   (ISA standard). Retire `session_fit.DEFAULT_RHO = 1.20`. Update any test that asserts the
   old fallback value.
7. **friction_coupling removal (VERIFY-THEN-REMOVE):** `friction_coupling.py` is imported +
   instantiated (`parameter_estimator.py:22,46` `self.friction_coupling = FrictionCoupling(...)`),
   re-exported (`__init__.py:28`), and imported by 3 tests. **First confirm `self.friction_coupling`
   is never actually CALLED in the estimation flow** (grep for `.friction_coupling.` usages and
   read `parameter_estimator`). If it is genuinely instantiated-but-never-invoked, REMOVE: the
   instantiation + the import + the `__init__` export + delete `friction_coupling.py` + delete
   `tests/unit/physics/test_friction_coupling.py` + drop the `friction_coupling` references in
   `tests/unit/physics/test_numerical_stability.py` and `tests/property/test_physics_properties.py`.
   **If it IS actually called (live behavior), STOP and report — do NOT remove it** (route out).
8. **OT-6 (comment-fix ONLY):** fix the false comment at `car_prior.py:57` claiming
   `k_tire=0.0` "matches the single-session convention" (single-session is `0.01`). State it
   is a deliberate neutral default for the C1 ceiling, with the value-unification tracked in
   #511. **Do NOT change the `k_tire` value.**
9. **The ONE output-level guard:** extend `tests/known_answer/test_published_f1_data.py` with
   a test that exercises the REAL ideal-lap sim path (car_prior → CapabilityEnvelope →
   PhysicsSimulator) for a known car/track and asserts: (a) ideal-lap **top speed** ∈ a
   physical band (e.g. ~300–360 km/h), and (b) a representative **corner cap** ∈ a physical
   band. It must be **green now** and **fail on a #518/#522-class units mismatch** — show it
   red on a deliberate break in your result (e.g. temporarily skip the `car_prior` conversion)
   then restore. Optionally one 3-line plausibility `assert` at the `car_prior` conversion
   boundary. **No per-param band-test matrix. No units library. No refit.**

## Protected Intent
**No behavior regression.** The consumer + live sim path are untouched by design; the renames
and constant-dedups are value-identical; the guard pins the composed physical output. The C1
utilization numbers (CONTEXTUAL) must not move.

## Test Mode
Test-after allowed for the mechanical renames/headers (the region suite is the safety net);
**test-led for the guard** (it is a new test — write it, see it green, prove it goes red on a
deliberate units break, restore).

## Close Criteria
- All 9 items above done (or friction_coupling reported STOP+route if found called).
- `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` GREEN.
- `py -m src.utils.simplification_limits --paths <touched src/ and tests/ paths>` clean.
- The new guard demonstrably fails on a deliberate units break (show the evidence) and passes restored.
- No `# TODO(#525)` left in `car_prior.py`.

## Allowed Scope
`src/physics/**` (the seams in the audit map), `tests/unit/physics/**`,
`tests/known_answer/test_published_f1_data.py`, `tests/property/test_physics_properties.py`,
`src/physics/__init__.py`, a new `src/physics/constants.py` if needed.

## Specific Exclusions
- Do NOT touch the consumer's lateral/longitudinal FORMULAS (convention B = consumer
  untouched). No ρ removal. No refit. No relocating conversions off `car_prior`.
- Do NOT change the `k_tire` value (comment only).
- Do NOT change convention-consistent channels' math (braking/traction/coast/terrain) — only
  the gravity/mass constant imports touch them.
- No new dual path, alias, or compatibility shim.

## Constraints
- `constraint:physics_region_no_evo_import` — no evo-region import.
- `py`, not `python`.
- Renames must be consistent producer→store→consumer (no half-renamed seam).
- Physics change → units/bounds explicit; the guard is the L2 known-answer evidence.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (physics_data_models, longitudinal_fit, braking_fit,
  session_fit, parameter_estimator, __init__), `struct:physics.layer2` (lateral_view,
  estimate_store), `struct:physics.utilization` (car_prior), `tests/known_answer/test_published_f1_data.py`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (its Review Trigger
  fires — the lateral conversion is being promoted/labelled; note it for reconcile);
  `claim:lateral_car_prior_boundary_conversion` (now the sanctioned seam, not a TODO patch).
- **Constraints:** no-regression on sim_evaluator/C1/known-answer.

## Required Evidence
- The full region-suite + guard run output (GREEN).
- The guard red-on-break / green-on-restore demonstration.
- simplification_limits output on touched paths.
- A list of the renamed fields/columns with their producer→consumer update sites.

## Verification Commands
```bash
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
py -m src.utils.simplification_limits --paths <touched paths>
git grep -n "TODO(#525)" src/   # must be empty
```

## Suggested Model Tier
simple-bounded→moderate (Sonnet) — the audit map makes every seam exact; the judgment points
(friction verify-then-remove STOP rule; guard red-on-break) are spelled out. Escalate only if
a rename cascade or the guard wiring proves deeper than the map shows.

## Authority
- Convention B + keep-ρ + the in-scope/routed split are RATIFIED by the human
  (`DECIDE_FIX_DECISIONS.md`) — do not relitigate.
- You MAY decide constant-module placement and field-suffix spelling. You may NOT change any
  ratified disposition, remove friction_coupling if it's actually called, or change k_tire.

## Stop Conditions
Stop and return if: friction_coupling turns out to be actually invoked (report it, leave it);
a rename forces touching the consumer formula or a refit; the guard can't be made green at
current physical values (that would mean a real regression — report it); or any ratified
disposition can't be honored as written.

## Operating Discipline
Your **result file IS the deliverable** — you are not done until
`.agent-work/525/crew-handoffs/g2-implement-result.md` exists with the evidence. If you run a
long suite, poll it to completion and write the result before resting.

## Return Format
Return `IMPLEMENTER_RESULT`: items completed (1–9), files changed (with the rename map),
test-mode satisfied, evidence (suite GREEN + guard red-on-break demo + simplification_limits),
the friction_coupling verdict (removed / reported-called), assumptions, stop conditions hit,
out-of-scope observations, and **Workflow Feedback** (`none` needs a run-specific reason).
