# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g1-implement` — Readiness core module + tests (issue #512, C3 regime-capability vector readiness)

## Task
Build a **pure-over-DataFrame** readiness core: `src/physics/layer2/regime_readiness.py`.
Given the five-view estimate-store DataFrame (one row per (constructor, round) quali fit), compute
the **4 readiness metrics** for each regime-vector component, returning a typed result with a
per-axis pass/fail against injectable thresholds. **No estimation, no I/O, no plotting** — the
dashboard (G2, separate gate) does loading/rendering. This module is the tested logic core.

## Protected Intent
This is a **characterization** (measured-not-wired). Honest covariance is first-class: use the
real 2×2 covariance blobs for param-pair separability, never diagonal σ alone. A weak/negative
result is a valid finding — do not "fix" the data; just measure it faithfully.

## Test Mode
TDD required — metrics must be analytically checkable on synthetic fixtures with known answers.

## Components (each = 1–2 scalar sub-axes; value col, σ col; shared 2×2 covariance blob)
- **slow_corner_grip**: `lateral_mech_grip_g` (σ `lateral_mech_grip_g_sigma`)
- **fast_corner_grip**: `lateral_aero_grip_g` (σ `lateral_aero_grip_g_sigma`)
  - param-pair for the two lateral axes ↔ blob `lateral_covariance` (2×2: [mech, aero])
- **straight_line**: two sub-axes — `max_power_w` (σ `max_power_w_sigma`) and
  `power_drag_area_m2` (σ `power_drag_area_m2_sigma`); param-pair ↔ blob `power_drag_covariance`
- **braking**: `brake_decel_ms2` (σ `brake_decel_ms2_sigma`) and `brake_aero_decel_per_m`
  (σ `brake_aero_decel_per_m_sigma`); param-pair ↔ blob `braking_covariance`
- **traction**: `traction_accel_ms2` (σ `traction_accel_ms2_sigma`) and
  `traction_aero_accel_per_m` (σ `traction_aero_accel_per_m_sigma`); param-pair ↔ blob `traction_covariance`
- **coast** (minor/diagnostic): `coast_rolling_decel_ms2`, `coast_drag_area_m2`; blob `coast_covariance`

Key DataFrame columns also present: `constructor`, `gp_name`, `round_idx`, `fit_status`
(`'ok'`/`'error'`). Covariance blobs are stored as JSON-ish lists (text) — parse with the
existing `estimate_store._cov_list` helper (import it) → a flat list you reshape to 2×2, or
`None` when absent.

## The 4 metrics (compute per scalar sub-axis unless noted) — compose existing seams
1. **Coverage** — per constructor: fraction of its rows that are valid
   (`fit_status=='ok'` AND value finite AND σ finite & > 0) out of rows present. Aggregate =
   median across constructors; also return per-constructor and a per-circuit "regime-exercised"
   flag (a circuit where the value is null/NaN for ≥ half the field doesn't exercise the regime).
2. **Separability**
   - *car-vs-car* (primary): `pooling.fit_two_way(values, teams=constructor, circuits=gp_name)`
     over valid rows → use `.frac_team` as the car-separability score (variance fraction on the
     car axis). Also keep `.frac_circuit`, `.frac_resid`.
   - *param-vs-param*: per component, the off-diagonal **correlation** from the 2×2 blobs
     (median over sessions of `cov01/sqrt(cov00·cov11)`). |corr|→1 ⇒ the two params are aliased
     (σ inflated by collinearity). Report once per component (not per sub-axis).
3. **Cross-session stability** — per constructor: `pooling.pool_random_effects(values, sigmas)`
   → `.tau` (between-session spread beyond noise) and `.i2`. Compare `tau` to the median
   within-σ. Drift-aware: also `pooling.fit_drift(values, clock=round_idx, sigmas=sigmas)`,
   remove the fitted trend, recompute residual spread (`tau_resid`) so genuine development is
   not read as instability. Aggregate (median across constructors): `tau`, `tau_resid`,
   `tau_resid / median_within_sigma`.
4. **Covariance honesty** — drift-aware standardized residuals pooled across all
   (constructor, round): `z_i = (x_i − μ_pred_i)/sqrt(σ_i² + τ²)` where `μ_pred_i =
   DriftFit.predict(round_idx_i)` for that constructor and `τ` is its RE `tau`. Report
   `std(z)` (≈1 calibrated; >1 over-claiming/σ too small; <1 under-confident) and
   `frac(|z|<1)`.

## Return shape
- `DEFAULT_THRESHOLDS` named constant: `frac_team_go=0.15`, `frac_team_nogo=0.05`,
  `coverage_go=0.70`, `zstd_go=1.3`, `zstd_nogo=2.0`, `param_corr_alias=0.9` (injectable).
- `@dataclass AxisReadiness`: name, n_valid, coverage, frac_team, frac_circuit, frac_resid,
  tau, tau_resid, within_sigma, zstd, z_frac_within_1, and a `flags: dict[str,bool]`
  (separable / covered / stable / calibrated) computed vs thresholds.
- `@dataclass ComponentReadiness`: component name, `axes: dict[str, AxisReadiness]`,
  `param_pair_corr: float|None`, `param_aliased: bool`.
- `def compute_readiness(df, *, thresholds=DEFAULT_THRESHOLDS) -> dict[str, ComponentReadiness]`.
- **Do NOT assign GO/CONTEXTUAL/NO-GO here** — that synthesis is gate G3. Emit metrics + flags only.

## Allowed Scope
`src/physics/layer2/regime_readiness.py` (new); `tests/unit/physics/layer2/test_regime_readiness.py`
(new). Read-only import of `src/physics/layer2/pooling.py` and `estimate_store._cov_list`.

## Specific Exclusions
- No DB/file I/O, no matplotlib, no CLI (that's G2).
- No GO/CONTEXTUAL/NO-GO verdict assignment (that's G3).
- Do not touch `pooling.py`, `pool_driver.py`, `estimate_store.py` (read-only consumers).
- No grip-evolution state (#511), no traction rebuild (#557), no evo wiring.

## Constraints
- `constraint:physics_region_no_evo_import` — no `src.evo_predictor` / `latent_power` / `compound_prior` import.
- Tests independent of `data/` — build synthetic in-memory DataFrames with **known** frac_team / τ / z
  so assertions check recovered values (L1 analytical), plus degenerate cases: single session per car,
  all-error component, zero-variance, missing blob → graceful (L3). Banking on numeric tolerances.
- Honest covariance: param-pair separability MUST read the real 2×2 blob.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `pooling.py` (`pool_random_effects`/`fit_two_way`/`fit_drift`), `estimate_store.py` (`_cov_list`, the component columns); new `src/physics/layer2/regime_readiness.py`.
- **Capability:** new readiness readout over the five-view store (composes pooling; adds coverage / param-pair separability / covariance honesty).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; honest covariance first-class.
- **Decision anchors:** `decision:c1_driver_utilization_design` (cross-session causal prior posture). Decision pressure: the rubric thresholds → a reconcile candidate (keep them a named injectable constant, don't bury magic numbers).
- **Evidence expectations:** the core must be able to re-measure the #492-era "constructors not separable, frac_team ≤ 3%" claim (so `frac_team` per component is the headline output).
- **Map confidence flags:** `fit_evidence.py` exists but targets the OLD Layer-1 fit_store — reuse the *idea*, do NOT import it; point at the five-view estimate store schema above.

## Required Evidence
`py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q` green; a short note in the
result showing the synthetic fixtures recover the planted frac_team / τ / z within tolerance.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_regime_readiness.py -q
```

## Suggested Model Tier
`simple bounded` (Sonnet) — spec + seams are precise; the work is careful composition + tests.

## Authority
Component→column mapping, the 4 metric definitions, the return shape, and threshold defaults are
DECIDED (commander, user-ratified plan). The implementer must not redefine metrics or add a
GO/NO-GO verdict. Minor naming/structure within the module is the implementer's call.

## Stop Conditions
Stop and return if: a metric can't be computed from the given seams as specified, the covariance
blobs aren't parseable as 2×2, allowed scope must be exceeded, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (pytest
output + the recovered-known-values note), assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback.
