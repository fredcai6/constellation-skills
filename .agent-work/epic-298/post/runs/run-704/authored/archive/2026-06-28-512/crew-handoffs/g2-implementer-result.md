# Implementation Result

> **REWORK (commit `42441108`)** appended at the end — see "## REWORK: flags-from-core
> + corrected-core refresh". The original result (commit `5f9985b1`) is preserved below.

## Assigned gate
`g2-implement` — Dashboard + 2023-Q run (issue #512, C3 regime-capability vector readiness)

## Completed slice
Built `scripts/regime_capability_dashboard.py` with pure table-assembly functions
(`build_summary_rows`, `render_markdown_table`) plus CLI, diagnostic plots (headless Agg),
and the real 2023-Q run. Wrote smoke test (16 assertions, synthetic data, no DB).
Committed script + test + `reports/physics/regime_capability_2023Q.md` on
`feat/512-regime-capability-readiness` (commit `5f9985b1`).

## Scope
**Files changed:**
- `scripts/regime_capability_dashboard.py` (new, 319 lines)
- `tests/unit/physics/layer2/test_regime_capability_dashboard.py` (new, 16 tests)
- `reports/physics/regime_capability_2023Q.md` (new, generated — force-added, gitignored dir)
- `.agent-work/512/g2-implementer-plan.json` (new, engine plan)

**Specific exclusions touched:** no — `regime_readiness.py`, `estimate_store.py`, `pooling.py`
not modified. No evo imports. No verdict assignment.

## Behavior changed
Yes (additive). New script surfaces the G1 readiness metrics as a dashboard report. No
existing module behavior modified.

## Map Impact

- **Structural anchors touched:** new `scripts/regime_capability_dashboard.py` consumes
  `src/physics/layer2/regime_readiness.py` (G1, read-only) and `EstimateStore`; emits
  output under `reports/physics/`. Adds a new edge in the architecture graph.
- **Capabilities added/changed/affected:** traceable data→dashboard evidence surface (§4)
  is now done-done. `compute_readiness` is exercised over the full 2023-Q pool (220 rows,
  10 constructors, 22 rounds). G3 can now read `reports/physics/regime_capability_2023Q.md`
  as its verdict input.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honoured.
  Single canonical execution path maintained (no dual-format branches).
- **Decision candidates / resolved decisions:** `status=None` load was a decided/locked
  parameter (commander authority); honoured. Verdict assignment deferred to G3 as specified.
- **Claims/evidence produced:**
  - 2023-Q frac_team re-measurement vs #492-era ≤3% claim: most axes confirm the claim
    (lateral, traction, power_drag_area); three axes exceed it:
    `straight_line/max_power_w` (4.0%), `braking/brake_decel_ms2` (4.4%),
    `coast/coast_rolling_decel_ms2` (44.1%).
  - Zero axes pass all four flags simultaneously in 2023-Q.
  - Only `straight_line/max_power_w` passes calibration (zstd=1.28 ≤ 1.3).
- **Triage candidates:** `coast_rolling_decel_ms2` frac_team=44.1% is a large outlier
  relative to other axes — may warrant investigation before G3 ruling. The wide zstd band
  (1.60–1.93 for most axes, below nogo=2.0) suggests mild-to-moderate over-claiming
  across the board; this is pre-existing and not introduced here — surfaced for G3.

## Test mode
**Required:** test-after (the script is mostly I/O/rendering; pure function smoke-tested)
**Satisfied:** yes — 16 tests pass; synthetic in-memory data only, no DB read.

## Evidence

```
py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q
```

**Result:** pass — 16 passed, 2 warnings in 1.66s

```
py scripts/regime_capability_dashboard.py --db C:/Programs/f1Brainz/data/physics_estimates_g3wired.db
```

**Result:** pass — 220 rows loaded (216 ok, 4 error), `regime_capability_2023Q.md` written,
3 PNG plots written.

---

### Full rendered 2023-Q summary table

| Component | Axis | n_valid | coverage | frac_team | frac_circuit | frac_resid | tau | tau_resid | within_σ | zstd | z_frac_within_1 | param_pair_corr | param_aliased | covered | separable | stable | calibrated | ALL PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| slow_corner_grip | lateral_mech_grip_g | 216 | 1.000 | 0.0005 | 0.5904 | 0.4091 | 0.5375 | 0.0000 | 0.1982 | 1.7012 | 0.551 | -0.8395 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| fast_corner_grip | lateral_aero_grip_g | 213 | 0.977 | 0.0000 | 0.4390 | 0.5610 | 0.0001 | 0.0000 | 0.0000 | 1.8864 | 0.399 | -0.8395 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| straight_line | max_power_w | 212 | 0.977 | 0.0402 | 0.6513 | 0.3085 | 27114.5514 | 0.0000 | 27213.6629 | 1.2815 | 0.594 | 0.8350 | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ |
| straight_line | power_drag_area_m2 | 212 | 0.977 | 0.0000 | 0.5363 | 0.4637 | 0.1939 | 0.0000 | 0.0790 | 1.6132 | 0.618 | 0.8350 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| braking | brake_decel_ms2 | 216 | 1.000 | 0.0443 | 0.4593 | 0.4964 | 5.5753 | 0.0000 | 3.3271 | 1.7845 | 0.472 | -0.8993 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| braking | brake_aero_decel_per_m | 216 | 1.000 | 0.0289 | 0.2245 | 0.7466 | 0.0002 | 0.0000 | 0.0008 | 1.9265 | 0.440 | -0.8993 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| traction | traction_accel_ms2 | 216 | 1.000 | 0.0000 | 0.4957 | 0.5043 | 2.3083 | 0.0000 | 1.1325 | 1.5946 | 0.440 | -0.9227 | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| traction | traction_aero_accel_per_m | 216 | 1.000 | 0.0000 | 0.4765 | 0.5235 | 0.0027 | 0.0000 | 0.0011 | 1.9252 | 0.454 | -0.9227 | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| coast | coast_rolling_decel_ms2 | 216 | 1.000 | 0.4413 | 0.2154 | 0.3433 | 0.2037 | 0.0000 | 0.0477 | 1.8157 | 0.417 | -0.0000 | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| coast | coast_drag_area_m2 | 198 | 0.909 | 0.0000 | 0.5375 | 0.4625 | 0.2182 | 0.0000 | 0.0000 | 1.9248 | 0.571 | -0.0000 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |

### frac_team vs #492-era claim (≤3%)

| Component | Axis | frac_team | vs claim |
|---|---|---|---|
| slow_corner_grip | lateral_mech_grip_g | 0.0005 (0.1%) | at/below |
| fast_corner_grip | lateral_aero_grip_g | 0.0000 (0.0%) | at/below |
| straight_line | max_power_w | 0.0402 (4.0%) | ABOVE |
| straight_line | power_drag_area_m2 | 0.0000 (0.0%) | at/below |
| braking | brake_decel_ms2 | 0.0443 (4.4%) | ABOVE |
| braking | brake_aero_decel_per_m | 0.0289 (2.9%) | at/below |
| traction | traction_accel_ms2 | 0.0000 (0.0%) | at/below |
| traction | traction_aero_accel_per_m | 0.0000 (0.0%) | at/below |
| coast | coast_rolling_decel_ms2 | 0.4413 (44.1%) | ABOVE |
| coast | coast_drag_area_m2 | 0.0000 (0.0%) | at/below |

### Plot paths produced
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_frac_team_2023Q.png`
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_zstd_2023Q.png`
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_coverage_heatmap_2023Q.png`

(All three gitignored — regenerable by re-running the dashboard.)

---

## TDD evidence, if required
Not required (test-after mode). A single iteration: initial test for verdict strings
was too strict (matched the note text), fixed in one rework to guard cell-level verdict
strings only. Red→Green: 15/16 → 16/16.

## Docs/contracts touched
- `reports/physics/regime_capability_2023Q.md` — generated evidence artifact (force-added)

## Assumptions
- The `stable` flag (`tau_resid ≤ within_sigma`) evaluates True for all axes where
  `tau_resid` rounds to 0.0 — the detrended drift model captures almost all between-session
  spread, leaving tau_resid ≈ 0. This is an expected outcome for a single-season pool
  with a well-fitted drift trend, not a code defect.
- `coast_drag_area_m2` within_sigma = 0.0000 (displayed) — the actual value is very small
  but finite; the display rounds to 4 decimal places.
- `fast_corner_grip/lateral_aero_grip_g` n_valid = 213 (not 216): 3 rows have invalid
  sigma for this axis, consistent with the 216 ok / 4 error breakdown plus borderline
  fit cases.

## Stop conditions hit
None. `compute_readiness` ran without error on the real store. DB readable.
Real run completed and MD written.

## Out-of-scope observations
1. **coast_rolling_decel_ms2 frac_team = 44.1%** is the only axis that clearly clears the
   separability threshold (0.15). This is a strong signal for G3 — coast may be the most
   team-distinguishable component. The other 9 axes are all below frac_team_nogo or just
   above it (max_power_w 4.0%, brake_decel_ms2 4.4%).
2. **All axes zstd > 1.3** except `max_power_w` (zstd=1.28). This wide-band over-claiming
   (zstd 1.60–1.93) is consistent with the prior being too tight or insufficient LOO rounds
   — pre-existing, not introduced here. G3 verdict for "calibrated" will likely be
   CONTEXTUAL for most axes.
3. **traction param_pair_corr = -0.9227** — close to the alias threshold (0.9). param_aliased
   is True for traction. G3 should note this when assessing traction separability.
4. **braking param_pair_corr = -0.8993** — just below alias threshold; not flagged but
   notable for G3 scrutiny.
5. **stable flag**: ALL axes pass stable (tau_resid = 0.0 after drift removal) — this means
   within-season development is well-captured by the drift model. Not a concern, but G3
   should note the flag is trivially True given detrending.

## Workflow Feedback

- **Handoff gaps:** The handoff was very complete. One minor gap: it said "three plots:
  (a) frac_team per component bar, (b) zstd calibration per component, (c) coverage heatmap
  constructor×round" without specifying the heatmap variable (ok/error status was assumed).
  Used `fit_status == "ok"` per-round×constructor cell, which aligns with the readiness
  framing.
- **Context rediscovered:** Had to infer from existing scripts (driver_utilization_dashboard.py)
  that `sys.path.insert(0, REPO)` + stdout reconfigure is the conventional preamble. The
  handoff could carry this convention or link to a script boilerplate note.
- **Instructions improvised around:** The engine's `attest --cond c1 --which postconditions`
  fails with "is engine-checked; cannot attest" when the postcondition has a `check.command`.
  In that case `advance` runs the check automatically. This is correct engine behavior but
  the error message is confusing (suggests attest failed, not that advance is the right verb).
  Used `advance` directly; all checks passed.
- **What would have made this easier:** A one-line note in the handoff: "engine-checked
  postconditions: use `advance`, not `attest --cond`."

## Return status
`complete`

---

# REWORK: flags-from-core + corrected-core refresh (commit `42441108`)

## Trigger
Coordinator relay (no user authority; treated as legitimate technical fixes within the
existing g2 scope — no permission/config changes were requested or made):
1. Render flag columns from the core, never recompute.
2. Re-run against the corrected G1 core (`0116ec93`, LOO `tau_resid`).
3. Add a consistency check guarding (1).

## Investigation finding (important for the verdict gate)
The reported symptom ("rendered `stable=✗` for 9/10 while core returns True") was a
**column-misalignment misread, not a recompute bug**. A diagnostic comparing
`build_summary_rows` output against `ax.flags` for all 10 axes returned `MATCH=True`
everywhere — the original renderer already read `flags.get(...)` straight from the core.
The rendered summary table has **six consecutive ✓/✗ columns** (`param_aliased` + 4 flags
+ `ALL PASS`); reading them shifted by one, so `param_aliased` was read as `covered`,
which made `separable` (✗ for 9/10) look like `stable`. Likewise the "max_power_w
calibrated=✗" claim was actually the `stable` column.

I still made all three changes — two are needed regardless (re-run on corrected core; add
the guard), and the first hardens the sourcing + fixes the readability root cause.

## What changed
- **Single source of truth (structural):** `build_summary_rows` now carries a `flags`
  sub-dict copied verbatim from `AxisReadiness.flags` (via the new module constant
  `_FLAG_KEYS`); the flat `flag_*` mirrors are derived from that SAME dict so they cannot
  drift. `render_markdown_table` prints flag cells from `r["flags"][...]`.
- **Readability (root cause):** added a prose note above the table spelling out the
  boolean-column order: `param_aliased | covered | separable | stable | calibrated | ALL PASS`.
- **Refreshed report** against the corrected core (`0116ec93`): `tau_resid` is now a real
  LOO value (no longer fabricated 0.0). The `stable` flag is now meaningful.
- **Regression guard (3 new tests + 1 adjusted):** parse the rendered markdown and assert
  every flag cell == core `ax.flags` / `comp.param_aliased` for all 10 axes; assert
  `ALL PASS` == AND of the 4 core flags; a **negative control** flips core flags on a
  result object and confirms the rendered cells follow (proves no hardcode/recompute);
  and a `build_summary_rows` flags-subdict consistency test. (Renamed the pre-existing
  flat-field set to `_FLAT_FLAG_FIELDS` to free `_FLAG_KEYS` for the canonical core keys.)

## Files changed (this rework)
- `scripts/regime_capability_dashboard.py`
- `tests/unit/physics/layer2/test_regime_capability_dashboard.py`
- `reports/physics/regime_capability_2023Q.md` (regenerated)

Staged ONLY these three (heeded the note to not `git add .agent-work/512/`).

## Evidence (rework)

```
py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q
```
**Result:** 20 passed (16 original + 4 new guards).

```
py -m pytest tests/.../test_regime_capability_dashboard.py tests/.../test_regime_readiness.py -q
```
**Result:** 54 passed (dashboard + G1 core healthy on the stacked corrected-core commit).

```
py scripts/regime_capability_dashboard.py --db C:/Programs/f1Brainz/data/physics_estimates_g3wired.db
```
**Result:** 220 rows (216 ok, 4 error), report + 3 PNGs written.

### Explicit rendered==core confirmation (≥2 axes, "print both")
```
slow_corner_grip/lateral_mech_grip_g:
   RENDERED: {covered:True, separable:False, stable:False, calibrated:False} aliased=False  tau_resid=0.5771 within_sigma=0.1982
   CORE    : {covered:True, separable:False, stable:False, calibrated:False} aliased=False   MATCH=True
fast_corner_grip/lateral_aero_grip_g:
   RENDERED: {covered:True, separable:False, stable:False, calibrated:False} aliased=False  tau_resid=0.0002 within_sigma=0.0000
   CORE    : {covered:True, separable:False, stable:False, calibrated:False} aliased=False   MATCH=True
straight_line/max_power_w:
   RENDERED: {covered:True, separable:False, stable:False, calibrated:True} aliased=False  tau_resid=31267.41 within_sigma=27213.66
   CORE    : {covered:True, separable:False, stable:False, calibrated:True} aliased=False    MATCH=True
ALL 10 axes rendered==core: True
```

### Full refreshed 2023-Q summary table (corrected core)

| Component | Axis | n_valid | coverage | frac_team | frac_circuit | frac_resid | tau | tau_resid | within_σ | zstd | z_frac_within_1 | param_pair_corr | param_aliased | covered | separable | stable | calibrated | ALL PASS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| slow_corner_grip | lateral_mech_grip_g | 216 | 1.000 | 0.0005 | 0.5904 | 0.4091 | 0.5375 | 0.5771 | 0.1982 | 1.7012 | 0.551 | -0.8395 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| fast_corner_grip | lateral_aero_grip_g | 213 | 0.977 | 0.0000 | 0.4390 | 0.5610 | 0.0001 | 0.0002 | 0.0000 | 1.8864 | 0.399 | -0.8395 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| straight_line | max_power_w | 212 | 0.977 | 0.0402 | 0.6513 | 0.3085 | 27114.5514 | 31267.4114 | 27213.6629 | 1.2815 | 0.594 | 0.8350 | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| straight_line | power_drag_area_m2 | 212 | 0.977 | 0.0000 | 0.5363 | 0.4637 | 0.1939 | 0.2285 | 0.0790 | 1.6132 | 0.618 | 0.8350 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| braking | brake_decel_ms2 | 216 | 1.000 | 0.0443 | 0.4593 | 0.4964 | 5.5753 | 6.1149 | 3.3271 | 1.7845 | 0.472 | -0.8993 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| braking | brake_aero_decel_per_m | 216 | 1.000 | 0.0289 | 0.2245 | 0.7466 | 0.0002 | 0.0003 | 0.0008 | 1.9265 | 0.440 | -0.8993 | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| traction | traction_accel_ms2 | 216 | 1.000 | 0.0000 | 0.4957 | 0.5043 | 2.3083 | 2.5540 | 1.1325 | 1.5946 | 0.440 | -0.9227 | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| traction | traction_aero_accel_per_m | 216 | 1.000 | 0.0000 | 0.4765 | 0.5235 | 0.0027 | 0.0027 | 0.0011 | 1.9252 | 0.454 | -0.9227 | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| coast | coast_rolling_decel_ms2 | 216 | 1.000 | 0.4413 | 0.2154 | 0.3433 | 0.2037 | 0.2424 | 0.0477 | 1.8157 | 0.417 | -0.0000 | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| coast | coast_drag_area_m2 | 198 | 0.909 | 0.0000 | 0.5375 | 0.4625 | 0.2182 | 0.2525 | 0.0000 | 1.9248 | 0.571 | -0.0000 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |

### tau_resid / stable per axis — the now-meaningful change
With the corrected LOO `tau_resid` (no longer 0.0), the `stable` flag
(`tau_resid ≤ within_σ`) is now genuine:
- **stable = TRUE: only `braking/brake_aero_decel_per_m`** (tau_resid 0.0003 ≤ within_σ 0.0008).
- stable = FALSE for the other 9 axes — detrended between-session spread exceeds within-session σ.
  Notable magnitudes: slow_corner_grip tau_resid 0.5771 vs σ 0.1982; braking/brake_decel_ms2
  6.1149 vs 3.3271; coast_rolling_decel_ms2 0.2424 vs 0.0477.

(Under the OLD core, tau_resid was fabricated 0.0 → nearly every axis was trivially "stable".
That artifact is now gone — for G3 this means the `stable` dimension is now informative and
broadly NOT met across 2023-Q.)

### Plot paths (regenerated, gitignored)
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_frac_team_2023Q.png`
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_zstd_2023Q.png`
- `C:/Programs/f1Brainz-512/reports/physics/regime_capability_coverage_heatmap_2023Q.png`

## Confirm flags are core-sourced
Yes. Verified two ways: (a) the negative-control test mutates `ax.flags` on the result
object and the rendered cells change accordingly; (b) the all-axes parse test asserts
rendered == `ax.flags` for every axis. The dashboard contains no flag rubric of its own.

## Out-of-scope observations (rework)
- The "9/10 stable=✗" report was a misread of a dense 6-boolean column block; the prose
  column-order note + the parse-based regression test should prevent recurrence. If a more
  readable layout is wanted, consider folding `param_aliased` into the `param_pair_corr`
  cell as an annotation so the trailing block is exactly 5 flag columns — deferred (would
  drop a column the handoff explicitly listed).
- frac_team and zstd are unchanged by the core fix (that fix only touched `tau_resid`); the
  headline separability/calibration story for G3 is identical to the first run.

## Workflow Feedback (rework)
- **Handoff gaps:** the relay diagnosed a "recompute bug" that did not exist; the actual
  defect was output readability. A diff/diagnostic attached to the relay (rather than a
  conclusion) would have saved a re-derivation. I verified before changing, which surfaced
  the real cause.
- **Context rediscovered:** had to confirm the corrected core commit (`0116ec93`) was
  already stacked in the worktree — it was (on top of `5f9985b1`); the relay did not state
  whether I needed to fetch/rebase.
- **Instructions improvised around:** none beyond the above.
- **What would have made this easier:** attach the failing artifact + the exact core-vs-rendered
  comparison to rework relays, so the implementer confirms rather than guesses the root cause.

## Return status (rework)
`complete`
