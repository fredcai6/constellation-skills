# Implementation Result — g3 (class-grain utilization observable + one-sided G band + energy)

## Assigned gate
g3-implement (issue #664, epic #659, delegated). Worktree `C:/Programs/f1brainz-wt/epic659-664`.

## Completed slice
Delivered the per-driver, per-CLASS quali-side utilization observable composing (1) the g1
absolute point deficit, (2) a one-sided grip (G) uncertainty band, and (3) a relative
energy-deployment channel; plus an additive `driver_class_observables` table on the g2 own-DB.
All four implementation gates driven through the engine (m0→m4), each red-then-green.

## Scope
**Files changed:**
- `src/physics/utilization/class_utilization_observable.py` (NEW)
- `tests/unit/physics/test_class_utilization_observable.py` (NEW)
- `src/physics/utilization/reference_utilization_store.py` (ADDITIVE edit — new
  `driver_class_observables` table + `DriverClassObservableRow` + read/write methods;
  `reference_laps` behavior untouched)
- `.agent-work/664-reference-laps/crew-plans/g3-implement-plan.json` (engine plan)

**Specific exclusions touched:** no — no point-G subtraction, no G re-fit, no μ move (#678), no
absolute SOC/kW, no ERS inference, no CLI/season-run/validation (g4), no race-side observables,
`segment_map/car_prior/physics_simulator` and the `reference_laps` table all untouched.

## Behavior changed
Yes — new observable API + new store table. No existing behavior altered (existing
`test_reference_utilization_store.py` stays green).

## Key design decisions (mine to make, per the handoff Authority)
- **σ⁺-from-G mapping:** `onesided_sigma_from_grip(mu, sigma) = hypot(mu, sigma)` — the RMS of
  the directed grip level and its propagated uncertainty. Always ≥ 0; sign-insensitive (uses
  G's magnitude, never mu as a shift). Consumed via `get_grip_at` only.
- **Band form:** `OneSidedGripBand` = a HALF/truncated Student-t (`PredictiveT` at
  `DEFAULT_NU_LOSS=4`), located at the per-class TIME deficit, extending ONLY toward larger
  deficit. `upper_bound(level) = loc + σ⁺·t.ppf((1+level)/2, ν)`. Point deficit is
  byte-identical with/without G (`g_sigma_onesided=0` when `grip=None`).
- **Energy proxy:** single KE channel — `deployment_share_by_class` (relative, sums to 1 over
  populated classes) + `deployment_phase_fraction`, built from positive `d(½v²)` only, over the
  real lap. Descriptive/instrument, NOT gated. `derate_flag` left DORMANT (a real one needs a
  threshold = out of scope).
- **Store:** one additive sibling table; PK on
  (year, session_type, gp_name, round_idx, constructor, driver, class, map_version);
  `INSERT OR REPLACE` idempotent; `_migrate_missing_class_columns` additive self-heal.

## ENERGY elevation-convention FINDING (explicit)
**A SINGLE kinetic-energy (½v²) channel suffices; the total-mechanical-energy (½v² + g·h)
convention is NOT needed here — so a single channel, not dual.** Reasoning: the deployment
proxy is explicitly RELATIVE — it reads only KE *changes* (`d(½v²)`, a derivative) and
normalizes each class's share by the car's OWN lap deployment total (its rolling baseline). The
potential-energy term `g·h(distance)` is a property of the TRACK, identical at each distance for
both laps under a same-circuit comparison, so it is common-mode and cancels; and any absolute
additive energy-level offset (a fictitious ERS/SOC baseline) differentiates to zero. The
total-mechanical-energy convention would only be required for an ABSOLUTE, cross-circuit
deployment figure — explicitly out of scope (relative-not-absolute; there is no ERS/SOC channel
in the telemetry, so an absolute figure would be fabricated). **Honest proxy scope:** a relative
positive-KE-gain share per class + a deployment phase fraction, over the driver's real lap;
descriptive/instrument only, its pre-registered §7 comparison is downstream (g4). This finding is
stated at the top of the module docstring.

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — new
  `class_utilization_observable.py` (consumes g1 `class_ledger.class_deficits/build_weight_matrix`,
  `struct:physics.layer2.grip_store.get_grip_at`, `src.common.student_t`); additive extend
  `reference_utilization_store.py` (sibling `driver_class_observables` table).
- **Capabilities added:** per-driver per-class utilization observable = absolute deficit +
  one-sided G band + relative energy channel.
- **Constraints honored:** frozen-constants (no new physical literal — only a hypot scale and
  reused g1 `DEFAULT_MIN_SPEED_MS`); no-normality (Student-t half-t); own-db; pre-quali (no race
  leakage); anti-circular (deficits straight from g1, no ratio).
- **Decision anchors:** G one-sided wrap (settled/inherited) — honored, not re-opened;
  `decision:c1_driver_utilization_design` (absolute deficit, strictly_pre) — honored.
- **Claims/evidence produced:** `claim:G-band-one-sided` (point byte-identical, σ one-sided,
  heavy-tailed) — tested; `claim:anti-circular` — point equals direct `class_deficits`;
  energy-relative-not-absolute — invariance test.
- **Trust limitations:** legacy pre-#627 grip rows expose narrower/absent `curve_*_sigma` → a
  narrower σ⁺ (documented soft-degrade, never crashes).

## Test mode
**Required:** test-after allowed (synthetic + temp DB, #656).
**Satisfied:** yes — drove genuine red→green per gate (m1 via module-hide, m2/m3/m4 via
symbol-absent import/attr failures), synthetic data + temp DB only, no live session load.

## Evidence
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest \
  tests/unit/physics/test_class_utilization_observable.py \
  tests/unit/physics/test_reference_utilization_store.py -q
```
**Result:** pass — `23 passed in 0.50s` (15 new + 8 existing store tests untouched).

```bash
git check-ignore src/physics/utilization/class_utilization_observable.py \
  tests/unit/physics/test_class_utilization_observable.py \
  src/physics/utilization/reference_utilization_store.py; echo "exit $?"
```
**Result:** `exit 1` — none gitignored (committable).

### Load-bearing tests
- `test_point_deficit_equals_direct_class_deficits` — point = g1 verbatim (anti-circular).
- `test_point_deficit_byte_identical_with_and_without_grip` — G moves ONLY σ⁺.
- `test_onesided_sigma_uses_magnitude_not_signed_shift` — magnitude, never a shift.
- `test_grip_band_is_one_sided_toward_larger_deficit` + `..._heavy_tailed_not_gaussian` — half-t,
  fatter than a normal at the 0.99 tail, ν=DEFAULT_NU_LOSS.
- `test_grip_consumed_via_get_grip_at_temp_db` + `test_module_does_not_refit_grip` — get_grip_at
  path on a synthetic temp-DB GripStore; grep confirms no `grip_baseline` / `.fit_`.
- `test_energy_channel_relative_invariant_to_absolute_offset` — invariant to an absolute offset.
- `test_driver_class_observables_round_trip` / `..._idempotent_rerun` /
  `test_escalation_columns_present_but_dormant` / `..._reference_laps_table_untouched`.

## Assumptions
- G's `(mu, sigma)` pace units are treated as commensurate with the transit-time deficit (s) for
  the band scale; because G contributes only a σ⁺ *width* (never a point shift) and "G barely
  moves utilization" is the expected outcome, this is a low-stakes scale choice, not a physical
  claim. Flagged for g4/review if a unit reconciliation is wanted.
- The observable takes `grip=(mu,sigma)` as data (caller fetches via `get_grip_at`) so the pure
  core stays unit-testable without a live store; `grip_scale_from_store` is the store-backed seam
  that actually calls `get_grip_at` (exercised end-to-end on a temp DB).

## Stop conditions hit
- None. No new physical threshold was needed (only a hypot scale + reused frozen g1 floor); the
  one-sided G wrap was fully expressible from `get_grip_at`'s `(mu, sigma)`; the energy proxy was
  buildable relative-only.

## Out-of-scope observations (triage candidates)
- **Derate flag needs a threshold ruling** — turning the dormant `derate_flag` column into a real
  2026-rampdown derate signal requires an energy threshold (STOP-and-return per this run's rules).
  Candidate for a follow-on once the §7 energy comparison (g4) motivates it.
- **G pace-unit ↔ deficit-second reconciliation** — if the band scale should be unit-exact rather
  than magnitude-commensurate, a small G-unit audit would settle it (informational, band is a
  width only).

## Workflow Feedback
- **Handoff gaps:** none blocking. The σ⁺-from-G *functional form* was correctly left to me
  ("You DECIDE: the exact σ⁺-from-G mapping"); the one under-specified point was whether the band
  attaches to the TIME deficit or the SPEED deficit — I chose TIME (G's pace units are
  time-like). A one-line steer in the handoff would have removed the judgment call.
- **Context rediscovered:** the synthetic `SegmentMap` construction pattern (`SegmentMap.build`
  args + soft severity membership) was not in the handoff; I recovered it from
  `tests/unit/physics/test_class_ledger.py`. A pointer to that fixture would save a lookup.
- **Instructions improvised around:** the plan template pairs a TDD-red `c1` with a command `c2`,
  but the handoff sanctions test-after; I kept the red step honest by observing a genuine failure
  before each green (hiding the module for m1; symbol-absent import/attr errors for m2–m4) rather
  than collapsing `c1`. Worked cleanly.
- **What would have made this easier:** name the band's target deficit (time vs speed) and cite
  the `test_class_ledger.py` SegmentMap fixture in the handoff.

## Return status
complete
