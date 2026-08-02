# Implementation Result — g4-implement

## Assigned gate
`g4-implement` — Static-latent separability at manageable uncertainty (issue #512, C3)

## Completed slice
Additive extension of the readiness core + dashboard with a **static-latent separability**
readout: pool each car's many track-viewpoints into a static estimate `mu_c ± sigma_mu_c`, then
measure car separability **relative to that estimate's own uncertainty** (NOT vs circuit variance
— that is the existing, distinct `frac_team`). Backward-compatible: all G1/G2 metrics and flags
unchanged. No GO/NO-GO verdict (that is G3).

## Scope
**Files changed (the six I committed):**
- `src/physics/layer2/regime_readiness.py` — extended
- `tests/unit/physics/layer2/test_regime_readiness.py` — extended (+8 static tests)
- `scripts/regime_capability_dashboard.py` — static section render + caterpillar plot + console
- `tests/unit/physics/layer2/test_regime_capability_dashboard.py` — extended (+6 static tests)
- `reports/physics/regime_capability_2023Q.md` — refreshed (real-store run; tracked .md)
- `.agent-work/512/crew-handoffs/g4-implementer-result.md` — this file

**Deliberately NOT committed:** the PNGs (gitignored), the rest of the `.agent-work/512/` tree
(engine state + other roles' handoffs), and `docs/architecture/*` (cartographer's uncommitted
working changes — not mine). Added only my six files explicitly (lesson carried from round-2's
broad-add mistake).

**Specific exclusions touched:** No. `pooling.py` / `estimate_store.py` not modified. No evo
import. No grip-state / traction-rebuild. No verdict.

## What was added (core)
- `ReadinessThresholds.separation_ratio_manageable = 2.0` (injectable).
- `@dataclass StaticSeparability`: `name, car_spread, med_sigma_mu, separation_ratio, sep_F,
  manageable, per_car {ctor:(mu_c, sigma_mu_c, n_c)}, tau_pre, tau_post, setup_conflated`.
- `_static_separability(...)`: per car `pool_random_effects` → `(mu_c, sigma_mu_c, n_c)`;
  `_ctor_tau` → `(tau_pre, tau_post)` (LOO-detrended) so a developing car is not read as noisy.
  Across cars: `separation_ratio = stdev({mu_c}) / median({sigma_mu_c})`,
  `sep_F = var({mu_c}) / mean({sigma_mu_c**2})`, `manageable` vs the threshold. Returns `None`
  when fewer than two cars pool.
- `_axis_setup_conflated(axis)`: name-driven — True for drag/aero axes, False for power/mechanical.
- `AxisReadiness.static: StaticSeparability | None` (additive field, default None).

### Naming decision (within implementer authority — flagged)
The handoff specified `static_mean_setup_conflated` as a **per-component** flag. That is not
physically representable: `straight_line` mixes a CLEAN power axis (`max_power_w`) and a
CONFLATED drag axis (`power_drag_area_m2`). I made it **per-axis** (`StaticSeparability.setup_conflated`)
so power reads clean and drag reads conflated within the same component. Faithful to the physical
intent; reported here for the reconcile.

## Test mode
**Required:** TDD — synthetic fixtures with known separable / non-separable static latents.
**Satisfied:** yes. Magnitudes validated empirically (seed-locked) before asserting.

## Evidence

```bash
py -m pytest tests/unit/physics/layer2/test_regime_readiness.py tests/unit/physics/layer2/test_regime_capability_dashboard.py -q
```
**Result:** 68 passed (42 core incl. 8 new static; 26 dashboard incl. 6 new static). 2 pre-existing
FutureWarnings in an untouched fixture.

```bash
py -m src.utils.simplification_limits --paths <the 4 code files>
```
**Result:** PASS (4 files checked). `render_markdown_table` and `main` (already large from G2) were
refactored into helpers (`_render_header`, `_render_summary_table`, `_render_frac_team_headline`,
`_print_console_summary`) to stay under the caps once the file became in-scope.

### Synthetic recovery note (planted vs recovered)
- Clearly separable (means 3.0/3.5/4.0/4.5, σ=0.05, n=6): `separation_ratio ≈ 31`, manageable True,
  per-car ordering recovered exactly (RBR<Ferrari<Mercedes<McLaren), each `mu_c` within 0.1 of planted.
- Non-separable same-mean: `separation_ratio ≈ 0.40` → not manageable.
- Non-separable huge-σ (σ=2.0): `separation_ratio ≈ 0.78`, `med_sigma_mu ≈ 0.82` → not manageable.
- Developing car (slope 0.2/round, n=10): `tau_pre ≈ 0.60 → tau_post ≈ 0.38` (38% drop) — LOO
  detrend separates development from noise; static ordering still recovered.

## Real-store run (REQUIRED EVIDENCE)
```bash
py scripts/regime_capability_dashboard.py --db C:/Programs/f1Brainz/data/physics_estimates_g3wired.db
```
Loaded 220 rows (216 ok, 4 error), 2023 Q, status=None.

### Static-latent separability per component×axis (the headline for the revised verdict)
| component / axis | separation_ratio | sep_F | tau_pre→tau_post | manageable | setup_conflated |
|---|---:|---:|---|:--:|:--:|
| slow_corner_grip / lateral_mech_grip_g | **0.74σ** | 0.6 | 0.537→0.577 | ✗ | ✗ |
| fast_corner_grip / lateral_aero_grip_g | 0.61σ | 0.3 | 0.000→0.000 | ✗ | ✓ |
| straight_line / max_power_w | **1.16σ** | 1.3 | 27114→31267 | ✗ | ✗ |
| straight_line / power_drag_area_m2 | 0.59σ | 0.3 | 0.194→0.229 | ✗ | ✓ |
| braking / brake_decel_ms2 | **1.41σ** | 1.9 | 5.575→6.115 | ✗ | ✗ |
| braking / brake_aero_decel_per_m | 9.24σ | 10.1 | 0.000→0.000 | ✓ | ✓ |
| traction / traction_accel_ms2 | 0.57σ | 0.3 | 2.308→2.554 | ✗ | ✗ |
| traction / traction_aero_accel_per_m | 0.73σ | 0.5 | 0.003→0.003 | ✗ | ✓ |
| coast / coast_rolling_decel_ms2 | 4.73σ | 18.5 | 0.204→0.242 | ✓ | ✗ |
| coast / coast_drag_area_m2 | 0.55σ | 0.3 | 0.218→0.252 | ✗ | ✓ |

### Per-car STATIC POWER ordering (straight_line / max_power_w, n≈20–22 each)
1. Ferrari 6.553e5 W ± 8.98e3
2. Williams 6.480e5 ± 1.09e4
3. McLaren 6.437e5 ± 8.56e3
4. Haas 6.431e5 ± 8.26e3
5. Aston Martin 6.409e5 ± 1.01e4
6. Alfa Romeo 6.367e5 ± 7.13e3
7. Red Bull Racing 6.333e5 ± 7.31e3
8. Mercedes 6.288e5 ± 8.21e3
9. Alpine 6.288e5 ± 8.70e3
10. AlphaTauri 6.238e5 ± 7.92e3

### Reading (for the commander's verdict — NOT a verdict assignment)
- **Even pooled to a static latent, power does NOT separate cars at the manageable bar:**
  `separation_ratio = 1.16σ` (< 2.0). The car-spread of static power (~9 kW stdev) is only ~1.2× the
  per-car pooled-mean σ (~8 kW). So the pooling thesis — "a stable PU power capability that tells
  cars apart" — is **not** met at 2σ on this store; cars are within ~1σ of each other.
- **RBR is NOT top on static power** — it is 7th; Ferrari is top. The measured power frontier orders
  engine families plausibly (Ferrari/Mercedes/Honda-RBR/Renault-Alpine) but the spread is small and
  the ordering is well within overlapping uncertainties — do not over-read it.
- The only "manageable" non-conflated axis is **coast/coast_rolling_decel_ms2 (4.73σ)** — a
  diagnostic axis, not a primary capability.
- `brake_aero_decel_per_m` shows 9.24σ but is **setup-conflated** (aero) AND has `tau_pre=tau_post=0`
  (degenerate per-car pools, likely n=1 cars on that axis) — do not over-read it.
- `tau_post ≥ tau_pre` on most real axes: there is no monotonic development trend to remove, so LOO
  detrend does not shrink the spread (it slightly inflates it at series endpoints). Honest behavior —
  the dominant per-car spread is per-track setup, not season-long development.

## Assumptions
- `max_power_w` units are watts as stored; the ~6.3–6.6e5 W static means are reported verbatim.
- `setup_conflated` is name-driven (`"aero"`/`"drag"` in the axis name). Documented; matches the
  handoff's "True for drag/aero, False for power/mechanical".
- Headline `sigma_mu_c` is the RE-pool mean uncertainty (per the explicit handoff spec), so a
  developing car carries an inflated `sigma_mu_c`; `tau_pre`/`tau_post` is the diagnostic that
  explains a large `sigma_mu_c` as development vs noise.

## Stop conditions hit
- None. Real run executed cleanly.

## Out-of-scope observations
- Power not separable-at-2σ even pooled, and RBR mid-pack on static power, is a substantive input to
  the revised G3 verdict — surfaced above, not adjudicated here.
- `brake_aero_decel_per_m` degenerate per-car pools (tau_pre=tau_post=0) suggest sparse per-car
  coverage on that axis; a coverage gate could suppress its separation number. Triage candidate.
- The `straight_line` per-component conflation mismatch (mixed clean/conflated axes) is a reconcile
  note for the rubric decision anchor.

## Workflow Feedback
- **Handoff gaps:** `static_mean_setup_conflated` specified as per-component is physically wrong for
  `straight_line` (clean power + conflated drag in one component). Made it per-axis and flagged.
  Future handoffs: specify conflation at the granularity where the physics actually differs (axis).
- **Context rediscovered:** that `DriftFit.predict` returns the MEAN's sigma (not a new-observation
  predictive sigma) — relevant because `sigma_mu_c` from the RE pool is what drives separation_ratio,
  and on real data `tau_post ≥ tau_pre` (no trend) is expected, not a bug. Documented so G3 doesn't
  misread it.
- **Instructions improvised around:** the existing `render_markdown_table`/`main` were already over the
  simplification-limits line cap (grandfathered at G2 via `--baseline`); touching the file made the
  strict `--paths` check apply, forcing a refactor not mentioned in the handoff. Did the minimal
  helper extraction. A future handoff that says "you'll need to refactor X to stay under caps" would
  set expectations.
- **What would have made this easier:** a one-line note that the dashboard file already exceeds the
  line cap and will need helper extraction when extended.

## Return status
`complete`
