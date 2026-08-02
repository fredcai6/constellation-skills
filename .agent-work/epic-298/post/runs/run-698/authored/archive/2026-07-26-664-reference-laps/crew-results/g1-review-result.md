# Review Result

## Assigned Gate
`g1-review` — issue #664 (epic #659): class-grain time-ledger + fingerprint core (`src/physics/utilization/class_ledger.py` + tests). Delegated.

## Result
`APPROVE`

## Load-bearing checks (all independently reproduced)

1. **Single (n, 2+k) W, no argmax collapse in any reduction — PASS.** `build_weight_matrix` (L96-100) builds `W = hstack([column_stack([straight_col, braking_col]), severity_membership])` — exactly `[seg_type one-hot {STRAIGHT,BRAKING_ZONE} | severity_membership]`. Every class reduction is `Wᵀ·quantity`: `W.T @ dt_segment` (L234), `W.T @ sum_dspeed_seg` / `W.T @ n_pts_seg` (L343-344), `W.T @ time_deficit_seg` (L352). `argmax` appears ONLY in `dominant_class_of` (L115-123), a standalone diagnostic never called by any reduction (verified by reading the full module).
2. **W-row-sum-to-1 asserted; malformed raises — PASS.** L102-109 `np.allclose(row_sums, 1.0, atol=1e-9)` else `ValueError` naming bad rows. `test_malformed_membership_row_raises` (a 0.3+0.2=0.5 corner row) confirms the raise; I re-ran the suite green.
3. **Time-shares sum to 1; per-segment transit sums to whole-lap (construction) — PASS.** `time_by_class_s = Wᵀ·dt_segment` with unit-sum rows ⇒ `Σ shares = 1`; `dt_segment` built by `np.add.at` over `segment_of` intervals ⇒ partitions the `Σ ds/v_avg` integral exactly. Tests assert sum==1 (abs 1e-9) and sum==reference lap (atol 1e-12). Labeled "construction" in docstrings/tests, not validation.
4. **Deficits ABSOLUTE, no ratio — PASS.** Grep `v_real/v_ideal` and `v_ideal/v_real` (both orders) → NONE; broadened name-division grep → NONE. Deficits are `v_ideal - v_real` (L334) and `dt_real_seg - dt_ideal_seg` (L351). The only divisions present are legitimate (transit `ds/v_avg`, share normalization, sum/count mean). `test_no_v_real_over_v_ideal_ratio_in_source` also guards this in-repo.
5. **No fresh domain threshold; min-speed floor inherited — PASS.** `DEFAULT_MIN_SPEED_MS = PhysicsEstimatorConfig().simulator_min_speed_ms` (=0.5, physics_config.py:117), the same floor `PhysicsSimulator.simulate_lap` uses (physics_simulator.py:116,119). See transparency note below on `_ROW_SUM_ATOL`.
6. **Pure core, no I/O — PASS.** Imports limited to `dataclasses`, `numpy`, `src.physics.physics_config`, `src.physics.segment_map.runtime`. No sqlite/fastf1/store/session/database/file/network tokens (the sole "session" hit is docstring prose L18). SegmentMap consumed read-only.
7. **Tests green — PASS.** `python -m pytest tests/unit/physics/test_class_ledger.py -q` → **14 passed in 0.36s** (re-run myself with the pinned interpreter).

Note: g1 chooses no distributional form — no "baked-in normality" finding was manufactured (that is g3's concern), per handoff.

## Handoff compliance
Delivers exactly the assigned core with the specified public API (`build_weight_matrix`, `dominant_class_of`, `class_time_ledger`, `class_time_shares`, `class_deficits`, `ClassTimeLedger`, `ClassDeficits`). All stop conditions checked and none tripped.

## Scope drift
None. `git status --porcelain` shows only the two allowed deliverables (+ `.agent-work` workflow scratch). No store/session/energy/G-force/reference-lap code (g2/g3/g4). Referenced sources consumed read-only, not modified.

## Evidence verdict
IMPLEMENTER_RESULT present; every claimed invariant independently reproduced (see checks above). Tests are behavior/invariant-focused, not string-matching.

## Code/doc quality
Clean, deep, well-documented. Fowler baseline pass recorded (`fowler_pass.json`), `verify_fowler_pass.py` exit 0: 11 smells absent, `data-clumps` overridden with a logged standard (module is a declared sibling of `compute_regime_deficits`; global-crew "match surrounding conventions" — bundling the (map, distance, speeds) trio would diverge the pure-function surface and add an abstraction the handoff did not ask for).

## Map impact verdict
- **Evidence supports claimed change:** Yes — `struct:physics.utilization` new module consuming `struct:physics.segment_map.runtime`; class-grain sibling of `compute_regime_deficits`.
- **Constraints not violated:** anti-circularity, frozen-constants, purity all honored.
- **Notes match the diff:** Yes; docstring cites `decision:c1_driver_utilization_design` + `decision:class-attribution-membership-faithful` + #664/#628.
- **Decision candidates surfaced:** None required — the change implements settled decisions rather than needing authority.
- **Durable context routed:** `claim:deficits-sum-to-lap` (construction) and `claim:anti-circular` both backed; nothing dropped.

## Reconciliation check
No divergence — the change faithfully implements the recorded decisions. No reconciliation needed.

## Blockers
- None.

## Out-of-scope observations
- **Transparency note (not a blocker):** `_ROW_SUM_ATOL = 1e-9` (L72) is a newly-introduced numeric constant, but it is a floating-point equality tolerance for the `Wᵀ` row-sum `== 1.0` assertion guard — it cuts no physical quantity and is explicitly documented as NOT a domain threshold. The frozen-constants / F12 discipline targets physics cut-points; this is numerical hygiene (analogous to test `atol`s), so it does not constitute a minted domain threshold. Surfaced for Commander awareness only.

## Workflow Feedback
- **Handoff gaps:** The frozen-constants criterion is worded "If you find ANY new numeric threshold, that is a BLOCK." Read literally that would snag the `_ROW_SUM_ATOL=1e-9` float tolerance, which is clearly not the intent (F12 = frozen *physics* constants). A one-word qualifier ("any new *domain/physical* threshold") would remove the ambiguity a reviewer must adjudicate.
- **Context rediscovered:** None material — handoff carried the anchors, line-number citations, and evidence pointers cleanly; the module docstring itself cited `physics_simulator.py:115-121`, which made check 5 fast to verify.
- **Instructions improvised around:** None. Survey template + engine covered the run; appended r4a/r4b/r4c siblings to give each load-bearing constraint its own provenance (sanctioned by the skill).
- **What would have made this easier:** Only the domain-threshold wording nit above.

## Return status
`complete`
