# Reviewer Handoff — g1 (class-grain time-ledger + fingerprint core)

## Gate
g1-review (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Survey State Location
Create your review survey at
`.agent-work/664-reference-laps/g1-review/review.json` (under the issue workbench, NOT the
worktree root).

## What Was Implemented
A NEW pure numeric module `src/physics/utilization/class_ledger.py` + tests
`tests/unit/physics/test_class_ledger.py`. It computes, over a persisted `SegmentMap` + a
lap's `(distance_m, speed)` profile: per-segment transit times, per-CLASS TIME-shares over
the `(2+k)` vocabulary, and per-CLASS absolute deficits (speed m/s + transit-time s) of
`v_real` vs `v_ideal`. Public API: `build_weight_matrix`, `dominant_class_of` (derived
diagnostic), `class_time_ledger`, `class_time_shares`, `class_deficits` (+ `ClassTimeLedger`
/ `ClassDeficits` dataclasses). 14 unit tests, all green.

## How to Inspect the Diff
This is an UNCOMMITTED working tree in a linked worktree. Inspect with:
`git status --porcelain` then `git diff` (both new files are UNTRACKED — use
`git status` / open the files directly; `git diff --name-only` hides untracked additions).
The two deliverable files are the whole change.

## Task Statement
See the implementer handoff at
`.agent-work/664-reference-laps/crew-handoffs/g1-implement-handoff.md`. Build the PURE
class-grain time-ledger + fingerprint core (no I/O), with membership-faithful `(n,2+k)`
`W`-matrix attribution and absolute-deficit-only (anti-circularity).

## Close Criteria (each becomes a review check)
- Attribution is a single `(n, 2+k)` weight matrix `W = hstack([seg_type one-hot
  {STRAIGHT, BRAKING_ZONE}, severity_membership])`; every class reduction is `Wᵀ·(segment
  quantity)`. Confirm there is NO argmax collapse in the attribution path (an argmax
  `dominant_class_of` is allowed ONLY as a derived diagnostic, never feeding a reduction).
- Each `W` row is asserted to sum to 1.0 (construction guard); a malformed membership raises.
- Per-class TIME-shares sum to 1.0 (± tol); per-segment/per-class transit times sum to the
  whole-lap transit time (deficits-sum-to-lap CONSTRUCTION check — label it construction,
  not validation).
- Deficits are ABSOLUTE: `mean(v_ideal - v_real)` (speed), `Δt_real - Δt_ideal` (time). GREP
  the module yourself for any `v_real / v_ideal` (either order) division — there must be
  NONE. (The implementer's own no-ratio test caught a docstring token; confirm the final
  state is clean.)
- NO new literal threshold constant is minted. Confirm the min-speed floor is INHERITED from
  `PhysicsEstimatorConfig.simulator_min_speed_ms` (not a fresh literal). If you find ANY new
  numeric threshold, that is a BLOCK (F12 discipline).
- The module is PURE: no DB/SQLite/session/FastF1/store import or call.
- Tests pass: re-run `pytest tests/unit/physics/test_class_ledger.py -q` yourself and
  confirm green.

## Allowed Scope
`src/physics/utilization/class_ledger.py` + `tests/unit/physics/test_class_ledger.py` only.
Read-only consumption of `segment_map/runtime.py`, `driver_utility_observable.py`,
`physics_simulator.py`, `segment_map/protocols.py`.

## Specific Exclusions
No store/session/energy/G/reference-lap code (those are g2/g3/g4). If any appears here, BLOCK.

## Constraints the Implementation Must Respect
- constraint:anti-circularity — absolute deficit, no ratio.
- constraint:frozen-constants — no new literal thresholds.
- pure core — no I/O.
- NOTE: g1 chooses NO distributional form, so the "no baked-in normality" criterion does NOT
  apply to this gate (it is checked in g3) — do not manufacture a normality finding here.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new `class_ledger.py`; consumes
  `struct:physics.segment_map.runtime`.
- **Capability:** class-grain sibling to `compute_regime_deficits`.
- **Constraints:** anti-circularity; frozen-constants; purity.
- **Decision anchors:**
  - `decision:c1_driver_utilization_design` — absolute deficit. `@grade: settled/human`
  - `decision:class-attribution-membership-faithful` — `(n,2+k)` `W`; NO argmax.
    `@grade: settled/measured` (a contradiction here is a float-back candidate, not yours to
    revise).
- **Evidence expectations:** `claim:deficits-sum-to-lap` (construction); `claim:anti-circular`.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/664-reference-laps/crew-results/g1-implement-result.md`:
`14 passed in 0.36s`; time-shares-sum-to-1 (abs 1e-9); transit-times sum to whole-lap
(atol 1e-12); no-ratio grep test + manual grep `no-ratio-confirmed`; W-row-sum guard raises
on sum 0.5; soft membership distributes fractionally (c1>c0>0). The APPROVE `review-result`
you return is matched at `g1-integrate.c2`.

## Suggested Model Tier
Stronger — the anti-circularity + soft-attribution + no-new-literal invariants are
load-bearing for the epic's GATING check.

## Stop Conditions
BLOCK if: the diff is inaccessible, any evidence is unverifiable, a `v_real/v_ideal` ratio
exists, a new literal threshold was minted, an argmax collapse feeds a reduction, or any I/O
appears in the module.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. WRITE it to
`.agent-work/664-reference-laps/crew-results/g1-review-result.md` AND return a tight verdict
summary as your final message.
