# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement (REWORK after BLOCK) — #522 G2 Lateral Units Fix v2 / Option A`

## Completed slice
Discarded the entire first-attempt diff (which had fixed the SHARED consumer for
g-units and broke the legacy convention-A path), then implemented **Option A**:
the g-unit → m/s² conversion is now localized at the `car_prior` boundary
(`_assemble_lateral`), exactly mirroring the #518 G5 `p_max/MASS_KG` boundary
conversion in `_build_longitudinal`. The shared consumer
(`physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`), the
producer (`lateral_view.py`), the store schema, and `regime_utilization.py` are
all UNTOUCHED.

**Commander follow-up fix (default-fallback landmine, same gate/scope):** the
conversion is now applied ONLY to store-pooled (g-unit) values. The
no-lateral-data fallback uses `cfg.default_A0=30.0` / `cfg.default_A2=0.001`,
which are ALREADY convention-A m/s² (the same RAW values `parameter_estimator.py`
feeds the m/s² consumer), so they pass through UNCONVERTED. Before this fix, the
uniform `×G` turned the 30.0 m/s² default into 294 m/s² (≈30 g) — an absurd
fallback floor for constructors with no causal lateral data. A new regression
test (`test_no_lateral_data_fallback_is_physical`) guards it. The store/truth-anchor
path is unchanged (63.19 m/s).

## Scope
**Files changed:**
- `src/physics/utilization/car_prior.py` (the only `src/` change)
- `tests/unit/physics/test_car_prior.py` (truth anchor + g-unit `_rec` defaults + converted L1 assertion + no-lateral-data fallback regression)

**Specific exclusions touched:** `no` — consumer files are byte-identical to
`HEAD` (verified: `git diff --name-only` lists only the two files above).
`lateral_view.py`, the store schema, and `regime_utilization.py` were not touched.

## Behavior changed
`yes` — the C1 car-capability ceiling now produces a physically real Monaco-tunnel
corner speed (~63 m/s) instead of the absurd ~17 m/s the unconverted g-units gave.
`params.lateral.A0` is now the converted mechanical grip in m/s² (≈31.4), and
`params.lateral.A2` is in the consumer's `A2·ρ·v²` convention. No behavior change
on the legacy/`sim_evaluator` convention-A path (consumer untouched, its tests
unchanged and green).

## The conversion + covariance math

The five-view `lateral_view` store carries lateral grip as a dimensionless
COEFFICIENT in **g-units**: `mu_max(v) = A0_g + A2_g·v²`, physical capability
`a_lat_max(v) = (A0_g + A2_g·v²)·G` (m/s²). The shared consumer is written in the
convention-A **m/s²** units: `mechanical = A0·g_track`, `aero = A2·ρ·v²`.

Conversion at the `car_prior` boundary (with `G = G_MS2 = 9.81`, imported from
`src/physics/braking_fit.py` — not redefined; `air_density` = the mean causal-row
ρ already computed in `build_car_ceiling` ~line 512 and passed to the consumer):

```
A0_param = A0_g · G                  (g-coef → m/s²; the dominant fix)
A2_param = A2_g · G / air_density    (so A2_param·ρ·v² == A2_g·G·v² when ρ == air_density)
```

Because the **same** `air_density` flows from `build_car_ceiling` to the consumer,
the A2 conversion is EXACT (not an approximation):
`A2_param · air_density == A2_g · G`. Verified numerically:
`A2_param·air_density = 0.0031392 == A2_g·G = 0.00032·9.81 = 0.0031392`.

Covariance transforms by the Jacobian `J = diag(G, G/air_density)`:
`cov' = J · cov · Jᵀ`. So `[0,0]·G²`, `[1,1]·(G/air_density)²`, off-diagonal
`·G·(G/air_density)`. Applied to BOTH the diagonal `A0_σ²/A2_σ²` path AND the
`_pick_representative_blob` 2×2 blob path (single `jac @ lat_cov @ jac.T` after
the blob/diagonal is chosen, so both share the transform). Verified:
- diagonal: A0var = `(0.15·G)² = 2.16531`, A2var = `(3e-5·G/1.18)² = 6.220e-8` ✓
- blob (off-diagonal): `J @ blob @ Jᵀ` reproduced exactly, correlation preserved (off-diagonal non-zero) ✓

**Defaults are NOT converted (follow-up fix).** The conversion is applied ONLY in
the store-pooled branch. When no causal record carries lateral A0/A2, the fallback
uses `cfg.default_A0=30.0` / `cfg.default_A2=0.001` — ALREADY convention-A m/s²
(the RAW values `parameter_estimator.py` feeds the m/s² consumer) — and they pass
through unconverted (`A0_param = default_A0`, `A2_param = default_A2`, covariance
from the m/s² `fallback_lateral_*_std` directly). Verified: fallback A0_param = 30.0
m/s² → 3.06 g floor (physical), NOT 294 m/s² / 30 g. A stored g-unit
`lateral_covariance` blob is correctly NOT applied to the m/s² defaults in this
branch.

A `# TODO(#525)` notes this is the localized Option-A patch the wider audit will
generalize (push into the producer/store) or retire.

## Map Impact

- **Structural anchors touched:** `struct:physics.utilization` —
  `car_prior._assemble_lateral` (the conversion boundary). Gained an `air_density`
  parameter (threaded from `build_car_ceiling`) and a `G_MS2` import from
  `braking_fit`; it is now the lateral sibling of the `_build_longitudinal` G5
  `p_max/MASS_KG` boundary conversion.
- **Capabilities affected:** lateral capability ceiling for the C1 ideal-lap path
  now emits consumer-convention (m/s²) A0/A2 — corner caps are physically real.
- **Constraints/assumptions touched:** relies on the invariant that the SAME
  `air_density` reaches both `_assemble_lateral` and the consumer
  (`CapabilityEnvelope.from_parameters(params, air_density, cfg)` and
  `_compute_speed_caps(..., air_density)`); this is what makes the A2 conversion
  exact. If a future change feeds the consumer a different ρ than the car_prior
  mean, the exactness degrades to an approximation.
- **Decision candidates / resolved decisions:** realizes
  `decision:ideal_lap_sim_two_sided_evaluator` (G5 boundary-conversion precedent)
  for the lateral channel; supports `decision:c1_driver_utilization_design`.
- **Claims/evidence produced:** corrected C1-path tunnel cap = 63.19 m/s (truth
  anchor, VER actual 63.3); convention-A consumer tests pass unchanged (legacy
  path intact); 641 physics-region tests green.
- **Triage candidates:** #525 — repo-wide unit-convention audit to generalize or
  retire this localized car_prior conversion (referenced by the inbound Map Anchors).

## Test mode
**Required:** `test-first (TDD: red → green)`
**Satisfied:** `yes` — truth anchor written and observed RED on the unconverted
code (~17 m/s, A0=3.2 raw), then GREEN after the conversion (63.19 m/s, A0=31.39).

## Evidence

Truth-anchor RED (before the conversion):
```bash
py -m pytest tests/unit/physics/test_car_prior.py -k "tunnel_corner_cap or converted_A0" -q
```
**Result:** `2 failed` — `Monaco tunnel corner cap = 17.36 m/s; expected ~63–66`
and `params.lateral.A0 == 3.2` (raw g-units, not converted). This is the RED state.

Truth-anchor GREEN + all car_prior tests (after the conversion):
```bash
py -m pytest tests/unit/physics/test_car_prior.py -q
```
**Result:** `30 passed` — including `test_tunnel_corner_cap_is_realistic`
(cap = 63.19 m/s, in [63,66]), `test_converted_A0_is_mechanical_ms2`
(A0 = 31.392 m/s² = 3.2·G), and the new
`test_no_lateral_data_fallback_is_physical` (fallback floor 3.06 g, A0=30.0,
A2=0.001 unconverted).

Full physics region:
```bash
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
```
**Result:** `642 passed, 6 skipped in 267.42s` (the 6 skips are pre-existing and
unrelated). One more pass than the pre-follow-up run (641) — the new fallback
regression test. Green before AND after the Commander follow-up fix.

**Convention A unbroken (NO re-baselining):** the reverted consumer tests
`test_physics_data_models.py` (37), `test_physics_simulator.py` (13),
`test_capability_envelope.py`, plus `test_sim_evaluator.py` (legacy convention-A
producer) and `test_regime_utilization.py` (untouched) all pass UNCHANGED — the
diff touches none of those files. This is the evidence the legacy/`sim_evaluator`
path is intact.

Diff scope (only the two allowed files):
```bash
git diff --name-only
# src/physics/utilization/car_prior.py
# tests/unit/physics/test_car_prior.py
```
Consumer files byte-identical to baseline:
```bash
git diff --name-only -- src/physics/physics_data_models.py src/physics/physics_simulator.py src/physics/capability_envelope.py
# (empty — BYTE-IDENTICAL)
```

Simplification limits:
```bash
py -m src.utils.simplification_limits --paths src/physics/utilization/car_prior.py
```
**Result:** `PASS (1 files checked)`

## TDD evidence, if required

- Failing test observed: `2 failed` — tunnel cap 17.36 m/s; A0=3.2 raw (RED).
- Passing test observed: `29 passed` — tunnel cap 63.19 m/s; A0=31.392 (GREEN).
- Refactor while green: `no` — the conversion is the minimal change; no further refactor needed.

## Docs/contracts touched
- `src/physics/utilization/car_prior.py` module docstring: the scalar→PhysicsParameterSet
  bridge table rows for A0/A2/covariance updated from "direct" to note the
  `g→m/s²` Jacobian conversion (#522); `_assemble_lateral` gained a G5-style
  docstring documenting the conversion, the exactness condition, the Jacobian, and
  the `# TODO(#525)`.

## Assumptions
- The store row's lateral A0/A2 are in `lateral_view` g-units (A0 ≈ grip
  coefficient ~1.6–5.0, confirmed against the real `data/physics_estimates.db`:
  A0 min/median/max = 1.64/2.68/4.99, A2 ~0.0005, ρ ~1.18). The truth anchor uses
  A0=3.2, A2=0.00032, ρ=1.18 (a representative top-car Monaco row).
- κ ≈ 0.011 1/m for the Monaco tunnel apex (VER's measured apex 63.3 m/s); the
  conversion makes the consumer's `_compute_speed_caps` reproduce it (63.19 m/s).
- The existing `_rec` test helper and L1 `setup_method` previously defaulted A0=26
  (a stale m/s² assumption); I updated them to realistic g-units and re-pointed
  `test_lateral_A0_A2` to assert the converted m/s² values (A0·G, A2·G/ρ). This is
  within the allowed `test_car_prior.py` scope and is REQUIRED for the test file to
  reflect the true store convention.

## Stop conditions hit
- `none` — `air_density` threaded into `_assemble_lateral` cleanly (already
  computed in `build_car_ceiling`); the truth anchor reached 63.19 m/s with the
  consumer UNTOUCHED; no consumer edit was needed.

## Out-of-scope observations
- The cap exactness depends on the same ρ reaching both the boundary and the
  consumer. This holds today, but a stronger long-term fix (the #525 audit) is to
  make the producer/store carry m/s² (or to adopt one capability-API convention)
  so no boundary conversion is needed. Captured as the #525 TODO in code.
- **Mixed-convention defaults are a #525 smell.** The root cause of the
  default-fallback landmine is that `cfg.default_A0/default_A2` live in the m/s²
  convention while the store lives in g-units, and `_assemble_lateral` now spans
  both. The branch-the-conversion fix is correct and local, but #525's audit
  should make the producer/store and the config defaults share ONE convention so
  this dual-units hazard cannot recur.
- `as_of_means["A0"]/["A2"]` now report the CONVERTED (m/s²-convention) values, not
  the raw store g-units. This is intentional (they should match what the consumer
  sees), but any downstream diagnostic that expected raw store g-units from
  `as_of_means` would need to read the store directly. No such consumer found in
  the touched scope.

## Workflow Feedback
- **Handoff gaps:** The handoff was thorough and self-consistent. One thing it did
  not spell out: the existing `test_car_prior.py` `_rec` helper and L1 setup
  **already** encoded the stale m/s² assumption (default A0=26.0) and
  `test_lateral_A0_A2` asserted A0==26.0 unchanged. The handoff said "build a
  ceiling from a g-unit store row (A0≈3.2)" for the NEW truth anchor but did not
  flag that the EXISTING L1 lateral assertion would necessarily flip to converted
  values. I handled it (both are inside the allowed test-file scope), but a one-line
  "expect to re-point the existing L1 lateral_A0_A2 assertion to converted values"
  would have removed the ambiguity about whether that counted as scope creep.
- **Context rediscovered:** I had to read `lateral_view.py` to confirm the producer
  convention (A0 = g-unit grip COEFFICIENT, `a_lat_max = mu·g`, A2 NOT ρ-divided)
  and query the real `physics_estimates.db` to ground realistic A0/A2/ρ ranges for
  the truth anchor. The handoff named the conversion but not the producer's exact
  semantics (that A2_g is a pure coefficient, so `A2_param = A2_g·G/ρ`); the Map
  Anchor `decision:c1_driver_utilization_design` plus a one-line producer-units
  pointer would have carried that.
- **Instructions improvised around:** The checklist engine runs `command`
  postcondition checks via `subprocess.run(shell=True)`, which on this Windows host
  is `cmd.exe` — my initial bash-style checks (`test -z`, `&&`, `| grep | tail`)
  failed. I rewrote every check as a portable `py -c` wrapper (exit-code based).
  Worth noting in the implementer skill / template that command checks must be
  shell-portable (cmd.exe on Windows), not bash.
- **What would have made this easier:** A note in the handoff that the existing
  L1 lateral test would need re-pointing, plus a one-line statement of the producer
  units (A2_g is a pure coefficient), would have removed the two context digs.
- **Engine misfit (follow-up work after gated plan completion):** the Commander's
  default-fallback fix arrived AFTER my 5-gate `gated` plan was already `DONE`. The
  engine refuses `append` on gated checklists (`append only on survey checklists`)
  and re-`reopen`ing a completed terminal plan to bolt on a new gate would distort
  the rework counters. Closest compliant thing: I executed the fix + new regression
  test under the SAME gate/scope, re-ran the full physics region (642 green), and
  documented it here and in the result. The engine plan record reflects the
  original 5 gates; this addendum is the durable record of the follow-up. Flagging
  so the Commander/Charter can decide whether late-arriving same-gate fixes should
  reopen the last gate or be tracked as a documented addendum (current choice).

## Return status
`complete`
