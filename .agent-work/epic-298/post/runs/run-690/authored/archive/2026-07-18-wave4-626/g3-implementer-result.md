# Implementation Result — g3 Layer 2 (within-session track-evolution latent)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` — Layer 2: structured within-session evolution (smooth grip latent for track
rubbering-in) with honest σ + an out-of-sample identifiability test. **THIS WAS THE
CRUX GATE.**

## Completed slice
Built `layer2_evolution.py` in full (smooth field-level within-session grip latent +
honest σ + wide-σ near-zero fallback outside coverage + LOO harness + orthogonality
check + honest verdict), with a passing test file. **Verdict: FLOAT-TO-ADMIRAL** — the
layer is real and identifiable *as a grip model*, but does **not** earn its keep as a
Layer-2 car-signal correction on the g1 frozen split. This is a complete, sanctioned
outcome (Pre-Ruling 2 / F5), not a silent drop and not a faked in-sample win.

## Scope
**Files changed (both NEW, untracked — not staged):**
- `src/physics/weekend_state/layer2_evolution.py`
- `tests/unit/physics/weekend_state/test_layer2_evolution.py`

**Specific exclusions touched:** no — no evo import (test asserts it); g1/g2 files,
estimator, evo, config untouched; no `data/*.db` modified or staged (git status shows
only the two new source files + `.agent-work/`).

## Behavior changed
Yes — a new physics-region module exposing: `load_grip_evolution_frame`,
`fit_track_evolution` (→ `TrackEvolutionFit`), `apply_track_evolution`,
`loo_earns_keep`, `orthogonality_vs_season`, and the `EARNS_KEEP_VERDICT` constant.
Nothing downstream consumes it yet (by design — it floats).

## The numbers (the deliverable as much as the code)

### Data / coverage caveat (LOUD)
`grip_bin_obs` Q rows are **2023-ONLY** — 14,968 rows across **9 weekends** (Abu Dhabi,
Austria, Azerbaijan, Bahrain, Great Britain, Hungary, Italy, Japan, Spain). **The handoff
stated "2023 and 2024"; the store as materialised this run carries only 2023** (verified:
`SELECT DISTINCT year FROM grip_bin_obs WHERE session_type='Q'` → {2023}). So the latent
is identifiable ONLY on these 9 weekends; the g1 physics-estimates frame spans 2019–2026.
Everywhere outside 2023 Q, `apply_track_evolution` returns a wide-σ near-zero prior
(0.0, σ=1.204) — no fabricated values.

### Is the within-session signal real? (identifiability — YES)
- Field-level within-(weekend,bin) FE WLS slope on `cumulative_track_laps`:
  **b_ctl = +0.001959 g/lap, se = 6.9e-5, t = 28.4**; **positive in all 9 weekends**.
  Over a ~350-lap session that is ~+0.69 g on a typical grip of ~2.77 g (~25%).
- **LOO (leave-one-WEEKEND-out, train/test disjoint, n=9 folds):** held-out weighted grip
  RMSE **0.82482 → 0.80368, a 2.563% reduction**. The slope **generalises out-of-sample** —
  it is not a self-weighted artifact. (Test `test_loo_folds_are_disjoint_not_self_inclusive`
  asserts the held-out weekend is never in its own training set.)

### Orthogonality vs the L3 season trajectory (NOT the F5 trap)
- corr(within-session `ctl` demeaned within weekend, season round_idx) = **-0.000000**,
  **r² = 0.000000**. The within-session axis lives in within-weekend variation; season-time
  is a between-weekend covariate → **orthogonal by construction**. It is genuinely a
  within-session signal, **not** L3's season-time axis in disguise.

### Does removing L2 change held-out CAR-SIGNAL noise on the g1 frozen split? (NO — FLOAT)
It cannot be evaluated there, for three principled reasons (none is "the signal isn't real"):
1. **Coverage:** 2023-only (9 weekends) vs the 2019–2026 frozen split — over the large
   majority of the split L2 is the wide-σ near-zero prior → zero car-signal effect.
2. **No bridge:** the g1 `frame` (`physics_estimates.db:session_estimates`) is one row per
   car-weekend with **no per-car representative-lap `cumulative_track_laps`** — so the
   field latent cannot be turned into a per-car adjustment there. (Cars *do* qualify at very
   different track states — best-lap `ctl` spread SD ≈ 100 laps within a weekend, so the F9
   foot-gun is real — but attaching a per-car session-time to each physics estimate is
   estimator work, and g1/g2 are frozen / out of scope.)
3. **Units:** the latent is lateral-grip g (`mu_lat_p90`), not the 11 physics axes; the map
   from grip-evolution to axis-estimate bias is unmeasured.

This is the handoff's explicit FLOAT stop-condition ("2023-only coverage makes held-out
evaluation impossible on the frozen split").

## Honest earns-keep verdict
**FLOAT-TO-ADMIRAL.** The within-session track-rubbering latent is REAL, identifiable
out-of-sample (LOO −2.56% grip RMSE), and orthogonal to season-time (r²≈0) — so it is NOT
the season-time double-count trap. But as a Layer-2 **car-signal correction on the g1
frozen held-out split** it is unidentifiable-at-this-granularity (coverage + no per-car
session-time bridge + unit mismatch), so it floats. Encoded verbatim in the module as
`EARNS_KEEP_VERDICT` (a test pins it so it can never silently drift to an in-sample "win").

## Test mode
**Required:** test-after (load-bearing = LOO harness + orthogonality check).
**Satisfied:** yes. Tests written before the module (observed RED = ImportError), then GREEN.

## Evidence
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer2_evolution.py -q
```
**Result:** pass — **12 passed in 3.97s**. (Whole-file RED observed first: ImportError,
`cannot import name 'layer2_evolution'`, before the module existed.)

Key tests: `test_loo_folds_are_disjoint_not_self_inclusive` (LOO not self-inclusive),
`test_apply_out_of_coverage_is_wide_sigma_near_zero` (fallback mean==0, σ wide),
`test_orthogonality_within_session_vs_season` (r²<0.01),
`test_coverage_is_2023_only`, `test_verdict_states_float_and_coverage_caveat`,
`test_no_evo_import`.

## TDD evidence
- Failing test observed: `py -m pytest ...` → `ImportError: cannot import name
  'layer2_evolution'` (module absent).
- Passing test observed: 12 passed (after one fix: coverage year normalised to `int`).
- Refactor while green: minor (year-type normalisation).

## Docs/contracts touched
- None. (Module docstring + `EARNS_KEEP_VERDICT` carry the coverage caveat and verdict.)

## Map Impact
- **Structural anchors touched:** `struct:layer2_evolution.py` (NEW, physics/weekend_state) —
  field-level within-session track-evolution latent; reads `damage_integrals.db:grip_bin_obs`
  (Q, 2023-only) joined to `damage_lap_integrals.cumulative_track_laps`.
- **Capabilities affected:** within-session track-evolution grip latent with σ — BUILT and
  within-grip-identifiable, but **not wired** into the weekend-state decomposition (floats).
- **Constraints touched:** `constraint:physics_region_no_evo_import` honored (asserted by
  test); LOO/out-of-sample smoother diagnostic honored (disjoint folds).
- **Decision candidates:** DC1 resolved → **FLOAT** (unidentifiable as a car-signal
  correction on the frozen split; identifiable as a grip model). Needs Admiral authority to
  either (a) accept the float, or (b) commission the per-car-session-time bridge below.
- **Trust limitations:** handoff's "2023 and 2024" claim is stale — store is 2023-only.
- **Triage candidates:** see below.

## Assumptions
- `mu_lat_p90` (lateral grip, g) is the within-session grip observable (handoff-named).
- Season-time proxy for orthogonality = 2023 F1 calendar round numbers for the 9 GPs
  (used only in `orthogonality_vs_season`, not in fit/apply).
- `mass_kg` is constant within 2023 (single season) → the mass control is degenerate here;
  bin FE + `tyre_life` are the effective controls (consistent with g2 layer1's finding that
  mass is not within-season identifiable).
- Smooth latent = penalised cubic smoothing spline of bin+tyre-adjusted grip vs a
  ctl-gridded axis, weighted by `n_samples`; linear-slope fallback if <6 grid points.

## Stop conditions hit
- **FLOAT (Pre-Ruling 2 / F5):** 2023-only coverage + no per-car session-time bridge in the
  g1 frame make held-out **car-signal** evaluation on the frozen split impossible. Reported
  with the held-out numbers above. (The within-grip LOO + orthogonality were fully run and
  are affirmative — the float is scoped precisely to the car-signal-correction question.)

## Out-of-scope observations (triage candidates for the Admiral)
1. **Per-car session-time bridge:** to make L2 a usable car-signal correction, the estimator
   would need to record each car's representative-lap `cumulative_track_laps` (or session
   clock) into `physics_estimates.db`. That is the single unlock — with it, L2 becomes a
   per-car track-state de-bias that does NOT cancel in `weekend_relative`. Estimator work,
   out of this gate's scope.
2. **grip_bin_obs Q coverage:** Q rows exist only for 2023. Backfilling 2022/2024 Q grip
   bins would widen identifiability toward the frozen split.
3. **Grip→axis unit map:** the latent is in lateral-grip g; a measured map to
   `lateral_mech_grip_g` / `lateral_aero_grip_g` would let L2 touch those axes directly.

## Workflow Feedback
- **Handoff gaps:** the handoff's Key-Data-Fact "grip_bin_obs only covers 2023 and 2024"
  is **wrong** — the store carries **2023-only** (9 weekends). I verified against the store
  before building. This shifts the coverage caveat and strengthens the float (even narrower
  than stated). Naming the exact expected weekend/year set in the handoff (or a one-line
  verification query) would have surfaced it upfront.
- **Context rediscovered:** the operational meaning of "earn its keep on the g1 held-out
  split" for a FIELD-level latter (shared across cars) had to be reasoned out — floor.py's
  `weekend_relative` median subtraction *absorbs* any across-car-shared shift, so a
  field-level latent can only move car-signal noise via a per-car session-time attachment
  that the g1 frame does not carry. The handoff pointed at the split + floor metric but not
  at this absorption/bridge subtlety, which is the whole crux.
- **Instructions improvised around:** the plan template's per-gate TDD-red (`c1` null
  check) vs the handoff's "test-after allowed" — I wrote the full test file first, observed
  a genuine whole-file RED (ImportError), and attested each gate's `c1` against that, rather
  than manufacturing a separate red per slice. Reasonable given test-after was sanctioned.
- **What would have made this easier:** a stated expectation that a field-level (not per-car)
  latent needs a per-car session-time hook to affect the car-signal metric — that framing is
  the entire earns-keep/float decision and I had to derive it.

## Return status
`complete` — slice built + tested + honestly reported. Model outcome: **FLOAT-TO-ADMIRAL**
(identifiable as a grip model; unidentifiable as a car-signal correction on the frozen split).
