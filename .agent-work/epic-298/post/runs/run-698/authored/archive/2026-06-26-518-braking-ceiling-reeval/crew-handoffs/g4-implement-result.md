# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4 — C1 re-eval on the recalibrated (wired) ceiling + lap-sampling σ + headline GO/CONTEXTUAL/NO-GO verdict`

## Completed slice
Re-ran the C1 driver-utilization characterization on the G3 wired-braking ceiling vs the OLD #510
ceiling for the 4 RBR/VER dashboard cases; added a `--db` selector to the dashboard; made the deferred
lap-sampling σ first-class (SEM of the regime-mean ratio, combined in quadrature with the unchanged
envelope σ); diagnosed the headline; and wrote the per-regime verdict.

## Scope
**Files changed:**
- `src/physics/utilization/regime_utilization.py` — lap-sampling σ + total σ (quadrature) in the pure
  core; new dataclass fields; docstrings (module "Honest covariance", `RegimeUtilization`,
  `estimate_driver_utilization` Notes — resolves the "future lap-sampling hook" TODO); refactor of the
  result assembly into `_per_regime_metrics` + `_assemble_result` (behavior-preserving; keeps the
  function under the 100-line simplification limit).
- `src/physics/utilization/characterize.py` — threaded the new σ fields through `UtilizationRow`,
  `_error_row`, `_utilization_row_from`, `rows_to_dataframe`.
- `scripts/driver_utilization_dashboard.py` — `--db` arg (default = OLD, back-compat), `--cases`
  subset arg, per-store CSV tagging, new σ columns in the printed table.
- `tests/unit/physics/test_regime_utilization.py` — 5 new lap-sampling σ tests.
- `tests/unit/physics/test_driver_utilization_dashboard.py` — 5 new tests (`--db` default/override,
  `_parse_cases`, new σ columns flow through).

**Specific exclusions touched:** no — `car_prior.py`, the braking wiring (G3), `estimate_store.py`
schema, layer2 views, and `docs/architecture/**` are all untouched (verified via `git status`). Store
NOT repopulated. `split_is_impure` stays `True`; single canonical ideal-lap path preserved.

## Behavior changed
Yes. (1) `RegimeUtilization` / `UtilizationRow` / the dashboard CSV now carry `sigma_u_lapsampling_*`
and `sigma_u_total_*` alongside the unchanged envelope `sigma_u_*`. (2) The dashboard can target either
store via `--db` and run an explicit `--cases` subset. No change to U/consistency/envelope-σ math.

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — `regime_utilization.py` (new
  lap-sampling/total σ in the pure core + assembly helpers), `characterize.py` (σ threaded through),
  `scripts/driver_utilization_dashboard.py` (`--db`/`--cases` seams). `car_prior.py` read-only.
- **Capabilities affected:** per-regime driver utilization — now reports honest two-source covariance
  (envelope ⊕ lap-sampling). Behavior per "Behavior changed".
- **Constraints/assumptions touched:** honest-covariance constraint honored (lap-sampling σ additive,
  envelope σ untouched & separately reportable); `split_is_impure=True` preserved; single canonical
  ideal-lap path preserved; `constraint:physics_region_no_evo_import` respected (no evo imports added).
- **Decision anchors:** `decision:c1_driver_utilization_design` Review Trigger fired and is **answered**
  — recalibration does NOT make `u_braking`/`u_fast_corner` trustworthy (still clip 2.0). The binding
  constraint is the ideal-lap shape/alignment (`decision:ideal_lap_sim_two_sided_evaluator`), not the
  braking-frontier depth.
- **Claims/evidence produced:** `u_braking`/`u_fast_corner` do NOT un-clip on the wired ceiling
  (Δ=0.000, 4/4 RBR cases); only `u_straight` responds (Italy +0.134). Root cause diagnosed below.
- **Triage candidates:** (1) physics-aware / phase-aligned ideal-lap comparison to unblock
  braking/fast-corner U (the real fix); (2) wire the remaining 4 C1 constructors' r1–15 to generalize
  the verdict beyond RBR.

## Test mode
**Required:** test-after.
**Satisfied:** yes — added a lap-sampling σ unit test (closed-form SEM, 3-4-5 quadrature, envelope-σ
still separate, zero-spread→zero, 1/√n shrinkage) plus dashboard `--db`/`--cases` tests; kept the
existing suites green.

## Evidence

```bash
py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py tests/unit/test_utilization.py -q
# -> 60 passed in 5.29s

py -m src.utils.simplification_limits --paths src/physics/utilization/regime_utilization.py src/physics/utilization/characterize.py scripts/driver_utilization_dashboard.py tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py
# -> PASS (5 files checked)

# Re-eval runs (offline cache; single canonical path; 4/4 ok each):
py scripts/driver_utilization_dashboard.py --db data/physics_estimates_g3wired.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42
py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db          --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42
```

**Result:** pass (tests + simplification green; both re-eval runs 4/4 ok, 0 errors).

## TDD evidence, if required
Test-after (not TDD). First regime-test run surfaced a real defect in my own test (`np.all(mask_straight)`
false because the random ratio created braking points) → fixed the test to compute the closed-form SEM
over the actual straight mask. Re-ran → 22 passed.

## Headline numbers — OLD → NEW U (4 RBR/VER cases, mc=50, seed=42)

| Case | u_braking | u_slow_corner | u_fast_corner | u_straight |
|---|---|---|---|---|
| Monaco | 2.000 → **2.000** (0.000) | 1.644 → 1.615 | 2.000 → **2.000** (0.000) | 1.196 → 1.183 |
| Italy | 2.000 → **2.000** (0.000) | 1.439 → 1.486 | 2.000 → **2.000** (0.000) | 0.578 → **0.712** (+0.134) |
| Great Britain | 2.000 → **2.000** (0.000) | 1.829 → 1.840 | 2.000 → **2.000** (0.000) | 0.775 → 0.825 |
| Singapore | 2.000 → **2.000** (0.000) | 1.489 → 1.530 | 2.000 → **2.000** (0.000) | 0.831 → 0.888 |

**Did `u_braking`/`u_fast_corner` un-clip? NO.** Bit-for-bit 2.000 on both stores (Δ=0.000) in all 4
RBR cases. Only `u_straight` responds to recalibration (and stays physical, <1, on the 3 power/mixed
tracks; Monaco >1 is a known short-straight/DRS artifact).

**Per-regime σ (incl. new lap-sampling term), straight regime, WIRED:** Monaco env 0.005 / lap 0.056 /
total 0.056; Italy env 0.021 / lap 0.010 / total 0.023; GB env 0.007 / lap 0.024 / total 0.025;
Singapore env 0.011 / lap 0.029 / total 0.031. Lap-sampling dominates on short/point-poor straights.

## Per-regime verdict
- **Straight — CONTEXTUAL** (responds, physical `<1` on power tracks; Monaco DRS artifact).
- **Slow corner — NO-GO** (`U≈1.4–1.8` both stores; barely moves; not separating/physical).
- **Braking — NO-GO** (still pinned at 2.0; structural, not depth).
- **Fast corner — NO-GO** (still pinned at 2.0; structural, not depth).

**Root cause (diagnosed, not a depth problem):** an ideal-lap/real-lap longitudinal phase + envelope
mismatch. The simulator ideal lap reaches 206.9 m/s on straights (aphysical) and brakes deeper/later,
so in the real-braking mask the ideal lap is at the apex (mean 25.1 m/s) while the real lap is still
fast (mean 65.6 m/s) at the same grid index → per-point ratio 2.5–3.7, `frac(ratio≥2.0)=0.73–1.0` →
pinned at `U_CLIP_MAX`. Fast corner is worse (ideal ~16.7 vs real ~62.9, ratio ~3.7). The recalibration
moved braking-mask `v_ideal` 27.5→25.1 — swamped by the structural offset. Same family as the
trajectory-smoother-physics-blind / #496 phase-lag braking-knee problem. The real unblock is a
physics-aware / phase-aligned ideal-lap comparison, NOT a deeper braking frontier.

## Wired-scope statement
RBR-only. Verified `fitted_at >= 2026-06-25`: RBR = 15 rows (r1 Bahrain … r15 Singapore — covers
Monaco r6, GB r10, Italy r14, Singapore r15); Ferrari & Mercedes = 1 stray Bahrain row each (ignored);
the other 7 constructors carry only OLD-braking (2026-06-20) rows. Verdict scoped to the 4 RBR/VER
dashboard cases; the other 4 C1 constructors are a documented continuation (need r1–15 wired before
their cases reflect the recalibration). The headline (braking/fast still clip) is a method property and
RBR is sufficient to show it.

## Docs/contracts touched
- Docstrings in `regime_utilization.py` and `characterize.py` updated (module/class/function level).
  No `docs/architecture/**` edits (reconcile owns the map).

## Assumptions
- Re-ran OLD via `--db` with mc=50/seed=42 (not the stored mc=20 CSV) so OLD vs WIRED is apples-to-apples;
  OLD numbers match the #510 baseline CSV within MC noise.
- `--cases "gp:driver,…"` with year 2023 implied is an acceptable subset mechanism (handoff allowed an
  optional comparison helper; this keeps `_DEFAULT_CASES` intact and avoids a separate script).

## Stop conditions hit
- None. Wired store read cleanly; both re-eval runs completed 4/4; lap-sampling σ combined without
  disturbing the envelope σ; verdict is fully supported by the numbers.

## Out-of-scope observations
- The braking/fast-corner clip is a real, named blocker for C1 readiness independent of #518's ceiling
  work — recommend a continuation issue for a physics-aware/phase-aligned ideal-lap comparison (and to
  wire the remaining 4 C1 constructors). Captured as triage candidates above; not actioned here.
- `scripts/g3_store_manifest.py` is untracked (a G3 artifact, not mine) — flagging, not touching.

## Workflow Feedback
- **Handoff gaps:** The handoff body says "10-case C1 subset" throughout (Close Criteria, Exact seams),
  but the Commander's dispatch message narrowed it to **RBR-only / 4 cases**. The two are reconcilable
  via the Store-scope note, but the headline scope contradiction between the handoff text and the live
  message cost a verification step. Naming the 4 RBR cases in the handoff's Task section (not only in
  the scope caveat) would remove the ambiguity.
- **Context rediscovered:** The artifact-postcondition schema key is `evidence_type` (not the intuitive
  `artifact_type`); the engine `KeyError`'d on my first `advance`. The IMPLEMENTER_PLAN template's `m1`
  example only shows a `command` check, so the artifact-check shape had to be reverse-engineered from
  `checklist_engine.py:_check_condition`. A second template example with an `artifact` postcondition
  (showing `evidence_type` + `match`) would have prevented the round-trip.
- **Instructions improvised around:** `attest` defaults to `--which preconditions`; closing a
  `check: null` postcondition needs `--which postconditions`. Not stated in the implementer skill; found
  via `attest --help`. Minor, but worth a one-line note.
- **What would have made this easier:** Pre-stating the apples-to-apples MC setting (the OLD CSV is
  mc=20; I standardized both runs at mc=50/seed=42). One line in the handoff ("re-run OLD at the same
  mc/seed as WIRED") would have pre-empted the judgment call.

## Return status
`complete`
