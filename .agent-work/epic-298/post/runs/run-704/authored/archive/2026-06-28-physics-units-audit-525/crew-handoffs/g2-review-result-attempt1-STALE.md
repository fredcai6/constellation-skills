# Review Result — #525 G2 (physics units-convention unify + label + guard)

## Result
BLOCK

## Assigned Gate
`g2-review — issue #525, branch feat/physics-units-audit-525`

---

## Verdict rationale (one paragraph)

Six of the seven checks pass cleanly and the work is high-quality: the consumer
formulas and live sim path are genuinely untouched, the constant dedup is
value-identical (with the one ratified 1.20→1.225 fallback change), the
friction_coupling removal was independently confirmed safe, the suite is green
(639 passed / 6 skipped, re-run), and the guard's A0-boundary assert genuinely
bites (I reproduced the red-on-break). **BLOCK is on check 2 alone:** the
ratified OT-1/OT-5 unit-suffix *field renames* (`p_max`→`p_max_w`,
`cda_closed`→`cda_m2`, `theta_P_values`→`theta_P_w_per_kg`, `A0`/`A2` g-suffix)
were **not delivered** — the implementer substituted comment-only unit labels and
kept every field name unchanged, without surfacing that substitution as a
deviation requiring authority. This is the de-overload mechanism the ratified
scope named explicitly; a green suite does not show it. The fix is small and the
substitution may even be the *right* call on safety grounds — but that is a
decision the human/Commander must ratify, not one to bless silently.

---

## Per-check findings

### Check 1 — No-regression / convention B (consumer formulas unchanged) — PASS
- `physics_data_models.py` diff = docstrings only: the `LongitudinalParameters`
  class docstring, a `theta_P_values` inline comment (`# W/kg ...`), and two NEW
  `A0`/`A2` field docstrings (diff lines 54, 57). **No math line in
  `lateral_capability` or `drag_acceleration` is touched** (grep for
  mechanical/aero/min/ceiling/tire_factor in the diff returns only the two new
  docstrings).
- `physics_simulator.py` diff = `import GRAVITY_MS2` + the single substitution
  `pop_max = ... * 9.81` → `* GRAVITY_MS2` in `_gsat_ceiling` (value-identical).
  **`_compute_speed_caps` is entirely unchanged** (no `+`/`-` line in that
  function).
- No ρ removal (consumer `A2·ρ·v²` intact; OT-2 is label-only per D2). No refit.
- Independent probe (synthetic RBR record → `build_car_ceiling` →
  `PhysicsSimulator`): ideal-lap top speed **436.0 km/h**, assembled
  **A0 = 31.392 m/s²** (= 3.2 g × 9.81, correct), corner cap **52.91 m/s** @
  κ=0.012 — all consistent with a consumer-untouched pre-G2 state. C1 numbers do
  not move.

### Check 2 — Rename consistency (no half-renamed seam) — **FAIL (the blocker)**
- DECIDE OT-1: "unit-suffix `A0`/`A2`"; OT-5: "suffix `p_max_w`/`cda_m2` (store)
  + `theta_P_w_per_kg` (consumer)". `g2-implement-handoff` OT-5 repeats it and
  adds "Update every reference consistently (no half-rename)".
- **The fields were NOT renamed.** Diff shows `EstimateRecord` still
  `p_max`/`cda_closed`/`A0`/`A2`; `LongitudinalParameters` still
  `theta_P_values`; `LateralViewResult` still `A0`/`A2`. The implementer added
  unit **comments** instead (`estimate_store.py:148,157-159,165-171`;
  `lateral_view.py` `LateralViewResult` docstring; `physics_data_models.py:137,148`).
- `git grep "p_max_w\|cda_m2\|theta_P_w_per_kg" -- src/ tests/` → ZERO hits
  except **pre-existing, untouched** JSON dict keys in
  `estimator_report.py:89` and `throttle_report.py:109,143` (unrelated to the
  rename target; not in the diff).
- **Important nuance:** this is **not a broken half-renamed seam** — the names
  are internally *consistent* producer→store→consumer; there is no straggler, no
  broken reference, and the suite is green. The defect is that a **ratified
  deliverable (the unit suffixes) was dropped** in favor of a weaker mechanism
  (comments), and the substitution was **not surfaced** as a deviation needing
  authority (`g2-implement-result` presents "labels" as the deliverable without
  flagging that the ratified suffix was not applied).
- Why it matters: the suffix was the *primary* de-overload mechanism of
  OT-1/OT-5 — it defuses the #518/#522 footgun at the **name** at every call
  site. Comments leave `A0`/`p_max`/`theta_P_values` ambiguous at the point of
  use.
- Why the implementer's restraint is *defensible* (and why this needs authority,
  not a unilateral reviewer pass): renaming `theta_P_values` →
  `theta_P_w_per_kg` on `LongitudinalParameters` would edit consumer-read code
  (`physics_simulator.py:66,311`, `drag_acceleration`/`max_power`/
  `interpolate_power`) and the persisted `EstimateRecord` schema — in direct
  tension with check 1's "consumer untouched". OT-1/OT-5 (rename) and the
  consumer-untouched constraint are in genuine conflict for the *consumer*-side
  field; that conflict is exactly a decision-requiring-authority that should have
  been raised.

### Check 3 — friction_coupling removal safe — PASS
- `git grep "\.friction_coupling\." -- src/` = **empty** (zero call sites; it was
  instantiated at `parameter_estimator.py` only, never invoked). Implementer's
  "never-called" claim is correct.
- Diff removes the instantiation + import (`parameter_estimator.py`), the
  `__init__.py` import + `__all__` entry, DELETES `friction_coupling.py` and
  `tests/unit/physics/test_friction_coupling.py`, and drops the
  `FrictionCoupling` import + dependent tests from `test_numerical_stability.py`
  (class renamed `TestFrictionCouplingEdgeCases` → `TestCapabilityEnvelopeEdgeCases`,
  retaining the 2 `CapabilityEnvelope`/`PhysicsSimulator` tests) and
  `test_physics_properties.py` (`TestFrictionUtilizationProperties` removed).
- `git grep -ni "friction_coupling\|FrictionCoupling" -- src/ tests/` = only 2
  **descriptive doc-comment** mentions (`__init__.py:16` header bullet describing
  it as DEPRECATED; `capability_envelope.py:27` "superseded ... FrictionCoupling").
  No code reference, no dangling import. Safe — not a BLOCK.

### Check 4 — Constant dedup value-identical — PASS
- `constants.py`: `GRAVITY_MS2: float = 9.81` (single canonical home).
- `MASS_KG: float = 808.0` single definition at `longitudinal_fit.py:44`;
  `session_fit.py:35` imports it; the old local `MASS_KG = 808.0` is deleted.
  Grep finds no second definition.
- Density 1.20→**1.225** is the ONE intended value change (`session_fit.py:58`,
  ISA). **Fallback-path-only**: `DEFAULT_RHO` is consumed only in the
  weather-unavailable branch (`session_fit.py:128` `rho = DEFAULT_RHO`, `:140`
  warning). No test asserts the old `session_fit` 1.20 (the `1.20` hits in tests
  are unrelated — compound_prior betas, CdA/power fixtures, air_density arrays).
- `braking_fit.G_MS2` retired to a deprecated alias `G_MS2 = GRAVITY_MS2`
  (sanctioned by DECIDE "alias OR removed"); `car_prior` now imports
  `GRAVITY_MS2` from `constants` (not `braking_fit`).
- `git grep "TODO(#525)" -- src/` = **empty**.

### Check 5 — Guard meaningfulness — PASS (with a documented caveat)
- Exercises the REAL path: fixture builds an `EstimateRecord` →
  `build_car_ceiling` (car_prior) → `PhysicsSimulator.simulate_lap` /
  `_compute_speed_caps`.
- **A0-boundary assert `[20,60] m/s²` is the meaningful teeth.** I independently
  reproduced the red-on-break: setting `s0=1.0, s2=1.0/air_density` in
  `_assemble_lateral` →
  `test_representative_corner_cap_physical_band FAILED: assembled A0=3.20 m/s²
  outside [20,60] ... assert 20.0 <= 3.2` (1 failed, 1 passed). Restored exactly
  (working tree clean vs the intended G2 state).
- **Caveat (band looseness — anticipated by the handoff):** on that SAME break,
  `test_ideal_lap_top_speed_physical_band` STILL PASSED. The `[250,500]` km/h
  top-speed band does **not** catch the conversion-bypass in this synthetic
  setup; only the A0 assert does. The top-speed band is a *coarse* sentinel — it
  brackets the historical RAW failures (#522 ~100-150 km/h < 250; #518 745 km/h
  > 500) but is effectively toothless for the ~1× conversion-bypass class. The
  A0 assert carries the real protection.
- 436 km/h is the CURRENT consumer-untouched value (probed) — not a new
  regression. Confirmed NOT a per-param band matrix; uses NO units library.
- **Doc inconsistencies (note, → tc1):** top-speed docstring says "300–360 km/h"
  but assert is `[250,500]` (lines 619 vs 636); corner-cap docstring says
  "15–60 m/s" but assert is `[15,80]` (lines 643 vs 658).

### Check 6 — Suite green — PASS
- I re-ran:
  `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q`
  → **639 passed, 6 skipped in 739.36s (exit 0)**. GREEN. Independently
  reproduces the implementer's 639/6 claim; `TestCarPriorIdealLapGuard` (2 tests)
  included and green.

### Check 7 — Scope — PASS
- Physics-region only: all touched paths are `src/physics/**`, the 4 sanctioned
  test files, `src/physics/__init__.py`, and the new `src/physics/constants.py` —
  matches the allowed scope exactly.
- No evo import: `git grep evo_predictor -- src/physics/` = only
  constraint-DOC comments (`decoupled_calibration.py:39`,
  `decoupled_longitudinal.py:65`, `scoreboard.py:22`); zero actual imports.
  `constraint:physics_region_no_evo_import` honored.
- No new shim/dual-path **except** the sanctioned deprecated `G_MS2` alias
  (DECIDE allowed it; implementer flagged it).
- braking/traction/coast/terrain math UNTOUCHED: per-file diffs of
  `session_braking`/`session_traction`/`session_estimator`/
  `decoupled_longitudinal`/`session_lateral`/`lateral_report` show ZERO added
  lines beyond `GRAVITY_MS2` imports/substitutions + unit comments
  (`6.5*9.81`→`6.5*GRAVITY_MS2`, etc., value-identical).
- `k_tire` value unchanged (`=0.0` at `car_prior.py:521`); only the OT-6 comment
  corrected (`car_prior.py:57-60`).

---

## Map impact verdict
- **Evidence supports claimed change:** mostly yes — `capability:physics_units_clarity`
  is achieved at the *comment/docstring* level but NOT at the *field-name* level
  the ratified scope (OT-1/OT-5) specified. The `Map Impact` note claims "unit
  conventions now explicit at every producer/store/consumer boundary in the
  lateral and longitudinal channels" — true for headers/comments, overstated for
  the field names (the names themselves remain unit-ambiguous). `capability:output_guard`
  is real and verified.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` and
  `constraint:no_behavior_regression` honored (suite green, value-identical).
- **Notes match the diff:** mostly — but the note does not disclose that the
  OT-1/OT-5 *renames* became *comments*. That is the one place the map-impact
  notes overstate the structural change.
- **Decision candidates surfaced:** PARTIAL — the implementer correctly surfaced
  `decision:ideal_lap_sim_two_sided_evaluator` (Review Trigger fires) and
  `claim:lateral_car_prior_boundary_conversion` (now the sanctioned seam). But
  the implementer did **not** surface the rename-vs-label decision that required
  human authority (the OT-1/OT-5-vs-consumer-untouched conflict). This is the
  gap.
- **Durable context routed:** the sanctioned-seam promotion is correctly routed
  to Cartographer for `decision:ideal_lap_sim_two_sided_evaluator` reconcile.

---

## Reconciliation check
- `car_prior._assemble_lateral` is now the documented ONE sanctioned g→m/s² seam
  (TODO retired → docstring). This fires the Review Trigger on
  `decision:ideal_lap_sim_two_sided_evaluator`; Cartographer should update the
  decision annotation. (Correctly noted by the implementer.)
- `friction_coupling.py` removed from `struct:physics`; `constants.py` added.
  Cartographer should drop the `FrictionCoupling` node and add the
  `constants.GRAVITY_MS2` shared-constant anchor.

---

## Blockers
- **B1 (the blocker):** OT-1/OT-5 ratified unit-suffix *field renames*
  (`p_max`→`p_max_w`, `cda_closed`→`cda_m2`, `theta_P_values`→`theta_P_w_per_kg`,
  `A0`/`A2` g-suffix) were replaced with comment-only labels and the substitution
  was not surfaced for authority. **Remediation (one of):**
  (a) deliver the field-name suffixes as ratified — accepting that the
  consumer-side field (`theta_P_values`) and the `EstimateRecord` schema get
  touched, which **requires human/Commander sign-off** because it conflicts with
  the consumer-untouched constraint; OR
  (b) the human formally down-scopes OT-1/OT-5 to label-only and ratifies that
  the suffix is dropped (in which case the implementation is already complete and
  this re-consolidates to APPROVE).
  Either way the resolution is a **decision the human owns**, which is why this is
  BLOCK rather than a silent pass.

---

## Out-of-scope observations
- **tc1 — guard doc/assert inconsistencies + band looseness:** fix the
  docstrings to match the asserts (top-speed "300–360" vs `[250,500]`; corner-cap
  "15–60" vs `[15,80]`), and consider tightening the top-speed band toward a
  defensible Monza value so it actually bites the conversion-bypass class
  (currently only the A0 assert catches it).
- **tc2 — rename-vs-label reconciliation** (the same matter as B1, captured as a
  triage candidate so the Commander can route the scope decision).
- **Pre-existing `simplification_limits` violations** (10, in
  `estimate_store`/`parameter_estimator`/`car_prior`/`braking_fit`/etc.) are
  unrelated to this change — route to a complexity-reduction epic if desired
  (already noted by the implementer).

---

## Workflow Feedback
- **Handoff gaps:** Check 2 in the review-handoff and OT-1/OT-5 in both the DECIDE
  doc and implement-handoff mandate *field-name suffixes*, while check 1 / the
  DECIDE D1-D2 / the "Specific Exclusions" mandate *consumer untouched*. For the
  consumer-side field (`theta_P_values` → `theta_P_w_per_kg`) these two ratified
  instructions **directly conflict** — a field the consumer reads cannot be
  renamed without touching the consumer. The handoff never reconciled this; it
  should have either (a) scoped the rename to *store/producer-only* fields
  (`EstimateRecord` g-unit `A0`/`A2`, `p_max`, `cda_closed`) and explicitly left
  the consumer field comment-only, or (b) flagged the consumer-field rename as a
  decision point. This ambiguity is the root cause of the BLOCK.
- **Context rediscovered:** I had to read `g2-implement-handoff.md` (not listed in
  my "READ FIRST" set) to confirm OT-5 genuinely asked for renames vs labels —
  the review-handoff's check-2 wording alone was ambiguous as to whether
  "renamed field/column" was prescriptive or merely descriptive of what the
  implementer was expected to have done. Listing the implement-handoff as a
  supporting input would have saved a hop.
- **Instructions improvised around:** The review-handoff frames check 2 as "Grep
  OLD names for stragglers" — which presumes the rename happened and only tests
  for *consistency*. It does not test for the rename being *absent*. I had to
  reinterpret the check as "did the ratified rename happen at all, and if not was
  the substitution surfaced?" — the closest compliant reading. Reporting this as
  the intended compliance, per the skill's misfit clause.
- **What would have made this easier:** In the handoff, split OT-1/OT-5 into
  "store/producer fields → rename (safe, no consumer touch)" vs "consumer field →
  comment-only (rename would touch consumer; out of scope by D1)". That single
  distinction would have removed the conflict and very likely turned this gate
  green on the first pass.

## Return status
`complete`
