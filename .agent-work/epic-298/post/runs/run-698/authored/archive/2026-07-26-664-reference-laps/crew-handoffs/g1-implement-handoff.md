# Implementer Handoff — g1 (class-grain time-ledger + fingerprint core)

## Gate
g1-implement (epic #659 / issue #664, delegated run). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN (CRITICAL): use
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` for every run
(3.14.3 / fastf1 3.8.1). NEVER bare `py`.

## Task
Deliver a NEW PURE module `src/physics/utilization/class_ledger.py`: a class-grain
time-ledger + fingerprint core over a persisted `SegmentMap`. No DB / session / FastF1
I/O — a smoother-agnostic numeric core (like `ribbon.build_ribbon` /
`driver_utility_observable.compute_regime_deficits`). It provides, given a `SegmentMap`
+ a lap's `(distance_m, speed)` profile [+ optionally a real lap's `v_real` on a shared
grid]:
1. **per-segment transit times** `Δt_i = ∫ ds/v` over each segment `[boundaries_m[i],
   boundaries_m[i+1]]` (use `v_avg = (v_i + v_{i+1})/2` with a positive min-speed floor,
   matching `PhysicsSimulator.simulate_lap`'s lap-time integral at
   `physics_simulator.py:115-121`).
2. **per-CLASS TIME-shares** over the `(2+k)` class vocabulary and they SUM to the lap.
3. **per-CLASS absolute deficits** — both a speed deficit (m/s) AND a transit-time deficit
   (s) — given `v_ideal` and `v_real` resampled on a shared grid. NEVER a `v_real/v_ideal`
   ratio (anti-circularity is binding).

## Protected Intent
- **Anti-circularity (#628):** the deficit is ABSOLUTE — `mean(v_ideal - v_real)` (speed)
  and `Δt_real - Δt_ideal` (time). There is NO division of `v_real` by `v_ideal` anywhere
  in this module (a reviewer will grep for it).
- **Membership-faithful attribution (design-it-twice RULING, settled/measured):** corner
  severity is SOFT; do not collapse it.

## Test Mode
TDD preferred (pure numeric core with exact construction invariants — easy to test first).
Author `tests/unit/physics/test_class_ledger.py`.

## Close Criteria
- `class_ledger.py` exposes a clear public API (name at your discretion, e.g.
  `class_time_shares(segment_map, distance_m, speed) -> dict[str, float]` and
  `class_deficits(segment_map, distance_m, v_ideal, v_real) -> <dataclass>`), documented
  with the unit conventions (m, m/s, s).
- **The (2+k) class vocabulary** = the two hard seg_type classes `"straight"`,
  `"braking_zone"` PLUS the `k` corner-severity classes named by the SegmentMap's own
  `class_ids` (the `severity_membership` columns). Use the map's `class_ids` labels for the
  severity classes — do NOT invent labels.
- **Attribution via a single `(n, 2+k)` weight matrix `W`** = `hstack([seg_type one-hot
  {STRAIGHT, BRAKING_ZONE}, severity_membership])`. Every class reduction is `Wᵀ ·
  (per-segment quantity)`:
  - class time-shares = `Wᵀ · Δt` (normalized by lap time → shares summing to 1).
  - class time-deficit = `Wᵀ · (Δt_real − Δt_ideal)` per segment.
  - class speed-deficit = membership-weighted MEAN of the per-segment mean speed deficit,
    weighted by each segment's point-count so it stays an honest absolute m/s (i.e.
    `(Wᵀ (d_speed_seg ⊙ n_pts_seg)) / (Wᵀ n_pts_seg)`).
  - **Assert each `W` row sums to 1.0** (within a tiny tol) before reducing — this is the
    construction invariant that makes time-shares-sum-to-lap structural. STRAIGHT and
    BRAKING_ZONE rows are one-hot (sum 1); CORNER rows carry `severity_membership` (rows sum
    to 1 by the mixture's `posterior_membership` contract); non-CORNER severity columns are
    exactly 0.0 (map invariant, `runtime.py:173-177`).
- **Do NOT argmax-collapse** the severity membership. A hard `argmax` "dominant class" view,
  if ever wanted, is a derived diagnostic OVER `W` (e.g. `W.argmax(axis=1)`), never the
  attribution mechanism — an argmax collapse makes the downstream GATING jackknife measure
  quantization noise instead of real attribution stability.
- Per-segment membership on a CONTIGUOUS lap: map each grid sample to its segment via
  `SegmentMap.segment_of(distance_m)` (returns segment ordinals; wraps at start/finish).
  Aggregate per-sample quantities to per-segment via the ordinal.
- Handle the shared-grid resample the same way `compute_regime_deficits` does (reuse
  `src/physics/sim_evaluator.resample_by_progress` / the existing regime-mask discipline —
  do NOT reinvent a resampler).

## Allowed Scope
- CREATE `src/physics/utilization/class_ledger.py`.
- CREATE `tests/unit/physics/test_class_ledger.py`.
- READ-ONLY reference (do not modify): `src/physics/segment_map/runtime.py`
  (`SegmentMap`, `SegType`, `segment_of`, `severity_membership`, `class_ids`,
  `boundaries_m`, `length_m`, `seg_type_code`), `src/physics/utilization/
  driver_utility_observable.py` (the #628 sibling — mirror its resample + mask discipline
  and its absolute-deficit convention), `src/physics/physics_simulator.py:115-121` (the
  lap-time integral to mirror), `src/physics/segment_map/protocols.py`
  (posterior_membership sums to 1).

## Specific Exclusions
- NO DB / SQLite / session / FastF1 / store I/O in this module (that is g2/g3).
- Do NOT touch `src/physics/segment_map/*` or any store — you CONSUME the SegmentMap.
- Do NOT implement the reference-lap product, the observables store, energy, or G here
  (later gates). This is the shared pure core ONLY.
- Do NOT mint any new literal threshold constant. If you believe you need one, STOP and
  return — a needed-but-unfrozen threshold is a commander/Admiral FLOAT, never an inline
  literal (F12 discipline). (This core should need no thresholds — it is pure geometry +
  the map's own membership.)

## Constraints
- `SegType` int codes: `STRAIGHT=0, BRAKING_ZONE=1, CORNER=2` (`runtime.py:25-31`).
- `SegmentMap.severity_membership` is shape `(n_segments, k)`, exactly 0.0 on non-CORNER
  rows, rows on CORNER segments sum to 1.
- `SegmentMap.class_ids` is the tuple of `k` severity class labels (fully-qualified, e.g.
  `"severity:2022-2025:v1:c0"`). Use them verbatim for the severity class keys.
- Deficit sign convention: positive deficit = the real lap is SLOWER than ideal
  (`v_ideal - v_real > 0`, `Δt_real - Δt_ideal > 0`). State it in the docstring.
- No baked-in normality — this core computes no distributional form (that is g3), so no
  Gaussian assumption should appear.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `src/physics/utilization/class_ledger.py`
  (new, component-level); depends on `struct:physics.segment_map.runtime`.
- **Capability:** per-regime driver utilization — a class-grain SIBLING to
  `compute_regime_deficits` (does not replace it).
- **Constraints:** `constraint:anti-circularity` (absolute deficit, no ratio);
  `constraint:frozen-constants` (no new literals).
- **Decision anchors:**
  - `decision:c1_driver_utilization_design` — absolute deficit; single canonical ideal-lap
    discipline. `@grade: settled/human · leans g1-implement`
  - `decision:class-attribution-membership-faithful` — single `(n,2+k)` `W` = seg_type
    one-hot ⊕ `severity_membership`; NO argmax. `@grade: settled/measured · leans
    g1-implement,g4-implement`
- **Evidence expectations:** `claim:deficits-sum-to-lap` (construction); `claim:anti-circular`
  (grep + unit test).
- **Map confidence flags:** the `segment_map` runtime is newer than the `physics.md` packet
  — trust the SOURCE (`runtime.py`), verified by direct read.

## Deliverable Path Check
- **Committed** — `src/physics/utilization/class_ledger.py`; `git check-ignore` exited 1
  (not ignored). Verified before dispatch.
- **Committed** — `tests/unit/physics/test_class_ledger.py`; `git check-ignore` exited 1.
- Both are NEW files → they appear in `git status` (untracked), not in `git diff` until
  staged.

## Required Evidence
- LOAD-BEARING (prove rigorously): (1) a unit test asserting per-class TIME-shares sum to
  1.0 (± tol) on a synthetic SegmentMap + lap; (2) a unit test asserting per-segment/per-
  class transit times sum to the whole-lap transit time (deficits-sum-to-lap CONSTRUCTION
  check); (3) the `W`-row-sums-to-1 guard is exercised (a malformed membership raises);
  (4) a `grep`-style test or assertion demonstrating NO `v_real/v_ideal` ratio (absolute
  deficit only).
- CONFIRMATORY (spot-check): soft-membership weighting distributes a corner segment's
  time/deficit fractionally across ≥2 severity classes on a fixture with a genuinely-soft
  corner; the argmax "dominant class" diagnostic (if provided) is derived over `W`.
- Run: `pytest tests/unit/physics/test_class_ledger.py -q` — paste the tail.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_class_ledger.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -c "import ast,sys; src=open('src/physics/utilization/class_ledger.py').read(); print('has_ratio_div:', 'v_real' in src and '/' in src)"  # manual anti-ratio spot-check; a real grep for v_real / v_ideal division must find none
```

## Suggested Model Tier
Stronger — numeric correctness + the anti-circularity and soft-attribution invariants are
load-bearing for the whole epic's GATING check; subtle to get right.

## Authority
Decisions ALREADY made (do not re-open): the `(2+k)` vocabulary; the single `W`-matrix
membership-faithful attribution (NO argmax); absolute-deficit-only. You DECIDE: exact
function names/signatures, the result dataclass shape, and the fixture design. You must NOT
decide alone: any new threshold constant (STOP + return — it is a float), or any change to
the SegmentMap or a store.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: you need a new literal threshold; the SegmentMap API
does not actually expose what this needs (report the exact gap); you would have to touch a
store/session to make the core work (it should not); or any allowed-scope boundary must be
crossed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced (with the pytest tail), assumptions used, stop conditions hit, out-of-scope
observations, and Workflow Feedback. WRITE the result to
`.agent-work/664-reference-laps/crew-results/g1-implement-result.md` AND return a tight
pointer summary (verdict + files + the key evidence numbers) as your final message.
