# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g1-implement (epic #659 / issue #664) — class-grain time-ledger + fingerprint pure core.

## Completed slice
Delivered the NEW pure numeric core `src/physics/utilization/class_ledger.py` (no DB / session /
FastF1 / store I/O — the SegmentMap is consumed read-only) plus its unit suite. Public API:
- `build_weight_matrix(segment_map) -> (W, class_ids)` — the single `(n, 2+k)` attribution matrix
  `W = hstack([seg_type one-hot {STRAIGHT, BRAKING_ZONE}, severity_membership])`; vocabulary =
  `("straight", "braking_zone") + segment_map.class_ids` (map labels verbatim). Asserts every row
  sums to 1.0 (numeric tol) or raises `ValueError`. No argmax collapse.
- `class_time_ledger(...)` / `class_time_shares(...)` — per-segment transit times
  `Δt_i = Σ ds/max(v_avg, min_speed)` (mirrors `physics_simulator.py:115-121`), reduced by `Wᵀ·Δt`
  to per-CLASS time and shares summing to 1.0. Returns `ClassTimeLedger` dataclass / dict.
- `class_deficits(...)` — per-CLASS ABSOLUTE deficits: speed `(Wᵀ(d_speed_seg⊙n))/(Wᵀn)` (m/s) and
  time `Wᵀ(Δt_real − Δt_ideal)` (s); positive = real slower. Returns `ClassDeficits` dataclass.
- `dominant_class_of(W)` — derived argmax diagnostic OVER `W` (never the mechanism).

Built as 3 vertical slices (W-matrix → time-ledger → deficits), TDD red→green on each, driven
through the checklist engine (lease `g1-impl-1785054200`, all items complete, lease released).

## Scope
**Files changed:**
- `src/physics/utilization/class_ledger.py` (NEW)
- `tests/unit/physics/test_class_ledger.py` (NEW)

**Specific exclusions touched:** no — no store/session/segment_map source modified; no reference-lap
product, observables store, energy, G, or distributional form implemented; no new literal threshold
minted (the min-speed floor is inherited from `PhysicsEstimatorConfig.simulator_min_speed_ms`=0.5,
not a new constant; the `_ROW_SUM_ATOL=1e-9` is float-equality hygiene, not a domain threshold).

## Behavior changed
Yes — adds a new pure capability (class-grain time-ledger + absolute deficits). No existing behavior
altered; the module is standalone (imports only `numpy`, `segment_map.runtime`, `physics_config`).

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — NEW `class_ledger.py`
  (component-level), depends on `struct:physics.segment_map.runtime` (read-only consume of
  `SegmentMap.segment_of/severity_membership/class_ids/seg_type_code`, `SegType`, `SEG_TYPE_LABELS`)
  and on `physics_config.PhysicsEstimatorConfig` (min-speed floor default).
- **Capabilities added:** class-grain per-regime driver utilization — a SIBLING to
  `compute_regime_deficits` (does not replace it); attribution over the `(2+k)` seg_type⊕severity
  vocabulary rather than the four hard regime masks.
- **Constraints honored:** `constraint:anti-circularity` — absolute deficits only, no ratio (unit +
  source-grep test); `constraint:frozen-constants` — no new literal minted.
- **Decisions realized:** `decision:c1_driver_utilization_design` (absolute deficit);
  `decision:class-attribution-membership-faithful` (single `W`, NO argmax — soft membership carried
  through and verified to distribute a corner deficit fractionally across ≥2 severity classes).
- **Claims/evidence produced:** `claim:deficits-sum-to-lap` (per-segment transit times sum to the
  whole-lap integral within 1e-12; class time-shares sum to 1.0; class time-deficits partition the
  whole-lap time deficit); `claim:anti-circular` (source grep + `v_ideal - v_real` present).

## Test mode
**Required:** test-first (TDD).
**Satisfied:** yes — each of the 3 slices encoded a RED postcondition (new tests observed failing:
ModuleNotFoundError → ImportError for the missing symbol), attested manually, then GREEN via the
command check. Engine journal carries the red/green attests per item.

## Evidence

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_class_ledger.py -q
```

**Result:** pass — 14 passed in 0.36s.

```
tests\unit\physics\test_class_ledger.py ..............                   [100%]
============================= 14 passed in 0.36s ==============================
```

Key load-bearing checks (all green):
- `test_per_segment_transit_times_sum_to_whole_lap` — Σ dt_segment == reference lap integral (atol 1e-12).
- `test_class_time_shares_sum_to_one` — shares sum to 1.0 (abs 1e-9); keys = the (2+k) vocabulary.
- `test_malformed_membership_row_raises` — a corner row summing to 0.5 trips the W-row-sum guard.
- `test_no_v_real_over_v_ideal_ratio_in_source` — source grep finds NO `v_real/v_ideal` (or reverse)
  division; `v_ideal - v_real` present. Manual grep also confirmed `no-ratio-confirmed`.
- `test_soft_membership_distributes_corner_deficit_across_two_classes` — a corner-only deficit lands
  fractionally on both severity classes (c1 > c0 > 0 per 1.1D vs 0.9D membership), straight = 0.
- `test_time_deficit_sign_and_partition` — real slower ⇒ lap_time_deficit > 0 and class deficits
  partition it.

## TDD evidence, if required
- Failing test observed (per slice): m1 5 fail (no module) → m2 4 fail (`class_time_ledger`/
  `class_time_shares` absent) → m3 3 fail (`class_deficits` absent). Attested red each time.
- Passing test observed: m1 5/5 → m2 9/9 → m3 14/14 green.
- Refactor while green: minor — reworded a docstring line that literally contained `v_real / v_ideal`
  (the anti-ratio source test correctly flagged it); re-ran, 14/14 green.

## Docs/contracts touched
- none (module + test only; docstrings document unit conventions m/m·s⁻¹/s and the sign convention).

## Assumptions
- `class_deficits` consumes `v_ideal`/`v_real` already registered on a SHARED grid (mirrors
  `compute_regime_deficits`, which documents the same and does not itself call `resample_by_progress`).
  Upstream callers resample via `sim_evaluator.resample_by_progress` — not reinvented here.
- Each sample-interval is attributed to the segment of its START sample (`segment_of(distance[:-1])`).
  This keeps the partition EXACT (every interval → exactly one segment ⇒ Σ classes = lap); a boundary-
  straddling interval is lumped into one segment, sub-sample error only.
- Min-speed floor default = `PhysicsEstimatorConfig().simulator_min_speed_ms` (0.5 m/s), the same
  floor the simulator uses — exposed as a `min_speed_ms` kwarg, not hardcoded.
- A class with zero backing points yields `nan` speed deficit (guarded `np.divide`), mirroring the
  sibling's None-for-unpopulated intent in array form (`n_points_by_class` identifies them).

## Stop conditions hit
- none. No new threshold needed; the SegmentMap API exposed everything required
  (`segment_of`, `severity_membership`, `class_ids`, `seg_type_code`, `SegType`, `SEG_TYPE_LABELS`);
  no store/session contact required.

## Out-of-scope observations
- The `(n, 2+k)` `W` and the per-segment ledger are reusable for the g2/g3 observables-store and
  fingerprint gates; `ClassTimeLedger`/`ClassDeficits` are the natural persistence payloads there.
- `dominant_class_of` is provided as a derived diagnostic only; if a downstream wants a human-readable
  "dominant class label", it can index the `(2+k)` vocabulary — left for the product gate.

## Workflow Feedback
- **Handoff gaps:** none of substance. One minor sharp edge, worth flagging: the handoff's own
  verification command (`... 'v_real' in src and '/' in src`) is a coarse spot-check that would
  false-positive on ANY module mentioning `v_real` near any `/`. My stronger regex test caught that
  my OWN docstring prose (`v_real / v_ideal`) tripped the real invariant — the crude command would
  not have. The precise-regex approach is the right one; recommend future handoffs specify the regex,
  not the substring heuristic.
- **Context rediscovered:** the min-speed floor's provenance — the handoff said "matching
  PhysicsSimulator.simulate_lap's lap-time integral" but did not name `PhysicsEstimatorConfig.
  simulator_min_speed_ms` as the frozen source; I traced it to avoid minting a literal. Naming the
  config field in the handoff would have saved a lookup.
- **Instructions improvised around:** engine `attest --which` takes `preconditions|postconditions`
  with `--cond <id>` (not `--which c1`); `current` rejects `--session-id`. Minor CLI-shape friction,
  self-corrected from `--help`.
- **What would have made this easier:** name the exact frozen constant to inherit for the min-speed
  floor, and specify the anti-ratio check as a regex rather than a substring heuristic.

## Return status
complete
