# Phase 0 — Coast-Drag Regen Bias & Density Path Validation

**Date:** 2026-06-16
**Script:** `.agent-work/445/phase0_regen_bias_validation.py`
**Scope:** D1 decision — where should `src/physics` get per-car drag from?
**Status:** READ-ONLY spike; no production code modified.

---

## 1. Regen Bias Quantification (Task A)

### Method

For three representative 2023 Q sessions — **Italian** (Monza, low drag), **Hungarian**
(high downforce), **Mexico City** (altitude, rho=0.905) — all 10 teams were processed:

1. Extracted coast points: throttle <= 10 (0-100 scale), brake < 0.5, speed > 150 km/h,
   deceleration −15 < a < −0.2 m/s². This exactly matches `ControlState.is_coasting` thresholds
   in `src/physics/physics_data_models.py` plus a high-speed filter to target straight-line aero.
2. Fit the **exact `fit_drag_rolling` model** from `src/physics/longitudinal_fit.py`:
   `−a = theta_R + theta_D * rho * v²` (unweighted OLS, identical to the production fit without sample weights).
3. Converted to `CdA_equiv = 2 * MASS * theta_D` (MASS = 808 kg).
4. Compared to the trusted reference: `CdA_closed` (index [0]) from `.agent-work/445/envelope/season_drs.json`,
   which is the joint DRS fit (full-throttle, well-conditioned), our gold-standard per-car drag axis.

Correlations were computed per-session (10 teams) and field-relative pooled (log-detrend each session
by its field median — removing the track-level wing configuration offset, which is the correct metric).

### Results

| Session     | N teams | Spearman | Pearson | theta_R median (m/s²) |
|-------------|---------|----------|---------|----------------------|
| Italian     | 10      | −0.248   | −0.104  | 2.836                |
| Hungarian   | 10      | +0.212   | +0.426  | 2.519                |
| Mexico City | 8       | +0.071   | +0.296  | 2.886                |

**Field-relative pooled (log-detrend by session, N=28):**
- Spearman = **+0.125**
- Pearson = **+0.233**

*(Prior `coast_decouple.py` result with a simpler constant-only intercept model: −0.12.
Adding `theta_R` as a free intercept marginally improves from −0.12 to +0.125 Spearman pooled —
still near-zero and not statistically meaningful.)*

**Naive cross-track pooled** (N=28, raw CdA values across wing configs): Spearman +0.547,
Pearson +0.648. This is spurious — it measures track-level wing configuration variation, not
per-car discrimination. DO NOT use for D1.

### theta_R Physical Diagnosis

The model's `theta_R` intercept is supposed to absorb rolling resistance (~0.02–0.05 m/s² for F1).

**Measured theta_R: median 2.71 m/s², std 0.64 m/s² — approximately 77× the physical rolling resistance.**

This is unambiguous evidence that `theta_R` is absorbing **regen/engine-brake deceleration**, not
rolling friction. The cross-team spread (0.64 m/s²) is much larger than any conceivable rolling
friction variation and tracks per-team harvest strategy rather than tire/bearing properties.

### Why the Intercept Doesn't Rescue the Fit

The prompt noted a key concern: constant-POWER regen gives a `~1/v` force, NOT a constant force.
The model intercept `theta_R` is a constant (speed-independent). Therefore:

- A team harvesting at constant power `P_regen` experiences decel = `P_regen / (m * v)`
- The model tries to absorb this as `theta_R` (constant) + `theta_D * rho * v^2` (v² term)
- The residual `1/v − theta_R_fitted / a_total` is non-zero and correlates with speed
- This residual bleeds into the `theta_D` (v² coefficient) because `1/v` and `v^2` are not orthogonal
  over a finite speed range: at lower coast speeds `1/v` is large, at higher speeds it's small,
  causing `theta_D` to be pulled upward by the low-speed regen deceleration
- The net effect: `theta_D` (and therefore coast-CdA) reflects **regen harvest intensity** more
  than drag area, at a rate varying by team strategy

**The intercept does NOT rescue the fit.** Field-relative correlation +0.125 (Spearman) is
consistent with random noise (not distinguishable from uncorrelated for N=10 teams).

### Comparison with Prior -0.12 Result

The prior `coast_decouple.py` used a simpler `−a = A + B * v²` (bin-median robust, no `rho`
threading). The src/physics model adds `rho` weighting and uses all points (not binned medians).
Despite this, the field-relative result is essentially the same: near-zero, consistent with
the coast signal being overwhelmed by regen at the per-team level.

---

## 2. Density Path Audit (Task B)

### `ParameterEstimator._get_air_density()` — src/physics/parameter_estimator.py

```python
def _get_air_density(self, weather: Optional[object]) -> float:
    if weather is None:
        return self.config.reference_density_kg_m3
    for attr in ("air_density", "density", "rho"):
        if hasattr(weather, attr):
            value = getattr(weather, attr)
            if value is not None:
                return float(value)
    if isinstance(weather, dict):
        for key in ("air_density", "density", "rho"):
            if key in weather:
                return float(weather[key])
    return self.config.reference_density_kg_m3
```

**Finding (i):** The fit CAN receive a measured density — but ONLY if the caller passes a
`weather` object with an `.air_density`, `.density`, or `.rho` attribute (or a dict with those
keys). The `reference_density_kg_m3` default is **1.225** (from `PhysicsEstimatorConfig`, line 77).
There is no automatic lookup of FastF1 weather or the `air_density.py` helper within `src/physics`
itself. The caller must wire this. In the current production path, if `weather=None` (or if the
object lacks the expected attributes), the fit uses 1.225 for every session — wrong by up to 35%
at Mexico City.

The `src/utils/environment.py::estimate_air_density_kg_m3` function exists and is correct
(altitude + temp + humidity → ISA pressure → moist-air density). The envelope's `air_density.py`
wraps it and adds measured-barometric-pressure as the preferred source. Neither is called by
`src/physics` automatically.

### `PhysicsSimulator.simulate_lap()` — src/physics/physics_simulator.py

```python
def simulate_lap(self, track_profile, parameters, sample=True):
    distances, curvatures = self._extract_track_profile(track_profile)
    air_density = self.config.reference_density_kg_m3   # LINE 31 — HARDCODED
    ...
```

**Finding (ii):** The simulator hardcodes density to `config.reference_density_kg_m3` (1.225).
There is no parameter to override this, no weather argument.

### Is This a Real Correctness Bug?

**Yes, for CdA and lateral grip — qualified No for lap time in a consistency case.**

The physics:

- `theta_D` is fit as: `theta_D = CdA / (2 * m * rho_fit)`, so `theta_D` encodes `CdA / rho_fit`.
- Simulator drag: `theta_D * rho_sim * v² = (CdA / rho_fit) * rho_sim * v²`.
  If `rho_sim == rho_fit`, drag force is correct. If not (Mexico: rho_fit=0.905 vs rho_sim=1.225),
  drag is overcounted by factor **1.354** — car appears to have 35% more drag than reality,
  producing too-low top speed.

- Lateral grip `A2 * rho_sim * v²` has the same issue: if `A2` was fit at `rho_fit = 0.905` but
  the sim uses `rho_sim = 1.225`, the aero downforce term is inflated 35% → faster cornering → 
  laptime error.

- **Power fitting (`fit_power_trajectory`) uses the fit's `air_density` consistently**, so there
  is internal consistency between the drag subtraction and the power estimate within the fit.
  However, the simulator then uses a DIFFERENT density for drag, which breaks this consistency.

- DENSITY_FIX_FINDINGS.md claimed "ρ cancels" in the quasi-static sim. That claim is only valid
  when `rho_fit == rho_sim`. Since the simulator hardcodes 1.225 and the fit receives a passed
  density (when the caller wires it), the cancellation does NOT hold when they differ.

**Practical severity:**
- At sea-level warm tracks (rho ~1.14): error ~7% on drag force. Small but present.
- At Mexico City (rho ~0.905): error ~35% on drag and aero-grip. Material — simulated top speed
  and cornering speed are both wrong.
- The DENSITY_FIX_FINDINGS.md conclusion ("the reported CdA feature now the true drag area,
  comparable across tracks") applies to the **envelope fitting** (which correctly uses `rho`
  throughout). It does NOT apply to `src/physics`, which hasn't been updated.

### The Altitude Bug

`src/utils/environment.py::estimate_air_density_kg_m3` is the altitude-based fallback.
The envelope `air_density.py` correctly documents (and works around) the known-buggy circuit
altitude lookup: "Mexico City → 0 m" and the three US races sharing Country="United States".
The solution (use measured barometric pressure from FastF1 weather) is already implemented in
the envelope but NOT wired into `src/physics`.

---

## 3. Verdict: Is src/physics Coast Drag Usable?

**No. Coast drag from `src/physics/longitudinal_fit.py::fit_drag_rolling` is NOT a usable
per-car signal for the same reason identified in the prior session.**

Per-session field-relative correlation with the trusted full-throttle reference:
- Italian: Spearman −0.248 (negative — wrong ordering)
- Hungarian: Spearman +0.212 (noise level for N=10)
- Mexico City: Spearman +0.071 (near-zero)
- **Pooled (field-relative): Spearman +0.125, Pearson +0.233**

These values are all below the "usable signal" threshold of >0.5. For context, a randomly
shuffled null would give ~0.0 ± (1/√(N−1)) ≈ ±0.33 for N=10 — the measured values are
within random-noise territory.

The `theta_R` intercept (median 2.71 m/s², 77× physical rolling resistance) confirms the model
is fitting regen + engine brake as a constant offset, which partially decouples regen from `theta_D`
but cannot remove it because constant-power regen gives a 1/v force, not a constant.

---

## 4. D1 Recommendation

**Recommendation: Switch to the full-throttle joint DRS fit as the drag source.
Do NOT use coast drag as a per-car drag input to the physics engine.**

Rationale tied to the numbers:

1. **Coast drag is invalid** (field-relative Spearman +0.125 ≈ noise). The src/physics model
   inherits the same fundamental problem identified in the envelope: MGU-K regen swamps the v²
   aero signal on coast-down. The constant-intercept rescue attempt fails because regen power
   is not a constant force.

2. **The full-throttle joint DRS fit is the validated per-car drag axis** (it was built
   precisely because coast-down failed). `season_drs.json[round][team][0]` (CdA_closed) is
   well-conditioned (honest σ, DRS-open lever arm extending the high-speed range) and survives
   cross-track comparison after log-space detrending.

3. **Practical path for src/physics integration:**
   - Wire `air_density.py` (measured barometric pressure, ISA-altitude fallback) into
     `ParameterEstimator.estimate_parameters()` so the fit density is correct.
   - Wire the same measured density into `PhysicsSimulator.simulate_lap()` via a new parameter
     (or via `PhysicsParameterSet`) so fit and sim densities match.
   - For per-car drag: either (a) use the joint DRS CdA as a Bayesian prior in the fit
     (season prior on `theta_D` = `CdA_drs / (2*m*rho_session)`) and don't trust the raw
     coast-drag posterior, or (b) skip the coast fit entirely for `theta_D` and use the
     joint-fit CdA_closed directly, keeping the coast fit only for `theta_R` diagnostics.

4. **Alternative considered — gating coast to low-regen moments:** The prior session noted
   "lower-ENVELOPE coast (least-regen points) might approach pure aero." This is worth a
   future experiment but has low expected value (the prior result was −0.12 even with high-speed
   filtering at >180 km/h; our replication at >150 km/h gives +0.125 — marginally better but
   still noise). No ERS deployment channel is available in FastF1 to identify truly zero-regen
   moments.

5. **Hybrid approach (recommended for Phase 3 #445):** Use joint-fit `CdA_closed` (with its
   identifiability σ) as a strong prior on `theta_D = CdA / (2*m*rho)`. Use coast data only
   to estimate `theta_R` (which is large and noisy but at least measures the real resistance
   environment the car operates in during coast). Power then falls from the full-throttle fit
   with the prior-constrained `theta_D`, recovering the partially-decoupled mid-band power.

---

## 5. Files Referenced

| File | Role |
|------|------|
| `src/physics/longitudinal_fit.py` | Production fit (coast drag) — BIASED |
| `src/physics/segment_classifier.py` | Coast classification (throttle <=10, brake <0.2) |
| `src/physics/parameter_estimator.py` | `_get_air_density()` — needs caller to wire density |
| `src/physics/physics_simulator.py:31` | Hardcoded `reference_density_kg_m3` — bug for non-sea-level |
| `src/physics/physics_config.py:77` | `reference_density_kg_m3 = 1.225` default |
| `src/utils/environment.py` | `estimate_air_density_kg_m3()` — altitude-based, altitude lookup buggy |
| `.agent-work/445/envelope/season_drs.json` | Trusted per-car CdA_closed reference |
| `.agent-work/445/envelope/air_density.py` | Measured-pressure density (correct, not wired to src/physics) |
| `.agent-work/445/envelope/coast_decouple.py` | Prior coast validation (corr −0.12) |
| `.agent-work/445/DENSITY_FIX_FINDINGS.md` | Full density + coast-down failure narrative |
| `.agent-work/445/phase0_regen_bias_validation.py` | This spike's analysis script |
