# G2 Spike M8 Result — Semi-parametric onset mean function

**Mechanism:** M8 models each braking onset with a parametric sigmoid/logistic mean function fitted to RAW a_long only (never the smoothed trajectory), then composes with the Gaussian smoother output: `a_long_m8 = a_long_gauss*(1-blend) + m*blend` with a `min()` safety cap to prevent ringing. The sharp step lives in the parametric mean; the Kalman/RTS never has to represent it.

**Prototype:** `spikes/m8/spike_m8.py`

**Re-run command:**
```
cd C:/Programs/f1Brainz/.claude/worktrees/agent-ae3f316be91bb25e3
py run_m8_scoreboard.py 2>&1
```
(requires `spike_m8.py` in same directory; main checkout at `C:/Programs/f1Brainz` on branch `feat/physics-aware-estimator-496` in Python path)

---

## Scoreboard: m8 vs gaussian vs kind3 (all 3 circuits, v2 variant)

| Circuit | Lap | n_brake | n_coast | gaussian_knee | kind3_knee | m8_knee | raw_knee |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bahrain | 14 | 18 | 0 | -39.50 | -39.42 | **-73.72** | -52.13 |
| Monaco | 29 | 21 | 1 | -38.07 | -37.60 | **-80.43** | -37.51 |
| Belgium | 21 | 22 | 0 | -34.93 | -37.41 | **-64.78** | -38.84 |

All units: m/s² (signed; decel negative). Knee = min a_long in straight_brake region.

### Ringing table

| Circuit | gaussian_ringing | kind3_ringing | m8_ringing | raw_ring | m8_ok |
| --- | --- | --- | --- | --- | --- |
| Bahrain | 0.46 | 0.41 | -8.89 | -2.86 | **true** |
| Monaco | 13.14 | 13.38 | -3.43 | 5.64 | **true** |
| Belgium | 4.36 | 4.44 | 4.36 | 4.57 | **true** |

### Gap vs raw (knee_gap_vs_raw = knee - raw_knee; negative = over-deepens)

| Circuit | gaussian_gap | kind3_gap | m8_gap | verdict |
| --- | --- | --- | --- | --- |
| Bahrain | +12.63 | +12.71 | **-21.59** | over-deepens 21.6 vs raw |
| Monaco | -0.56 | -0.09 | **-42.92** | massively over-deepens |
| Belgium | +3.91 | +1.43 | **-25.94** | over-deepens 25.9 vs raw |

Negative gap = over-deepening (more decel than raw sensor). Both directions are failures.

---

## Onset fit quality (v2, regime-aware a_post estimation)

### Bahrain (18 brake samples across 6 events, avg 3 per event)
- Clean (RMS < 3): 4 | Poor: 1 | Failed: 0 | Skipped: 1
- Notable: t=5012.34s RMS=0.50 but **depth=-144.82 m/s²** (impossible: 14.8g) — low-RMS artifact on 2 points
- Notable: t=5024.46s RMS=0.95, k=101.6/s (implies 10ms onset — unresolvable at 4 Hz)

### Monaco (21 brake samples across 8 events)
- Clean: 4 | Poor: 1 | Failed: 0 | Skipped: 3
- Notable: t=5017.53s RMS=0.73, **depth=-52.81 m/s²** — exceeds raw_knee (-37.5)

### Belgium (22 brake samples across 7 events)
- Clean: 2 | Poor: 2 | Failed: 0 | Skipped: 3
- Notable: t=5427.24s RMS=0.01, **depth=-48.29 m/s²** — near-perfect RMS but unphysical depth

**OptimizeWarning: "Covariance of the parameters could not be estimated"** on every case — confirms structurally under-constrained fits.

---

## Honest failure modes

### Root cause: data sparsity at 4 Hz GPS

With 2-4 brake-regime kinematic samples per event, a 4-parameter sigmoid (t0, k, depth, offset) is mathematically underdetermined. curve_fit finds low-RMS solutions with non-physical parameters. This is the primary failure of M8 at this data resolution.

### v1 failure (composition direction wrong)
v1 estimated a_post from window tail (post-braking recovery = near-zero decel), giving positive depth (+65 m/s²). Combined with full blend, this replaced braking-region output with a positive mean — catastrophic ringing (+39.7 m/s² Bahrain, knee shallowed from -39.5 to -22.6).

### v2 failure (composition direction correct but magnitudes wrong)
v2 fixed a_post estimation (brake-regime samples only). Now depth is correctly negative. But with 2-4 data points, the sigmoid depth is unconstrained and reaches -144 m/s². The safety `min()` cap prevents ringing (Monaco improves from 13.14 to -3.43, ringing_ok=true on all circuits) but passes through the over-deepened knee.

### Belgium regression
Belgium kind3 knee (-37.41, gap +1.43) is close to raw (-38.84). M8 v2 gives -64.78 (gap -25.94) — a severe regression vs both baselines.

---

## Invariant note (decision:two_cycle_external_anchor_design)

**Source**: RAW a_long only — COMPLIANT (never re-reads from smoothed trajectory).
**Placement**: NOT plateau-only. M8 fits the ONSET TRANSITION, not the established plateau. This is an EXTENSION of the invariant's placement rule.
**Mechanism**: Output-space composition (not a Kalman update). Does not participate in the smoother's internal state updates.

The extension is architecturally distinguishable from the existing kind=3 anchor and does not violate the overfitting guard. However, with degenerate fits, the "external anchor" value is meaningless (it is a numerical artifact, not a physics-derived value).

---

## Soundness self-assessment

**Ringing improvement: REAL.** The min() safety constraint validly clips spurious positive accel in non-throttle regions. Monaco ringing 13.14 → -3.43 m/s² is genuine (same Gaussian baseline, just capped by a less-positive m8 output).

**Knee numbers: ARTIFACTS.** The -73 to -80 m/s² knee values are not physical. They arise from poorly-constrained sigmoid depth parameters on 2-4 data points. The improvement metric (knee_gap_vs_raw negative) is a false positive.

**Conceptual soundness:** High. Mean-function decomposition is a correct and well-established technique (GP literature, changepoint models). The failure is purely empirical — the mechanism requires higher-resolution data than the scoreboard provides at the GPS position sampling rate.

---

## WEAK recommendation

**WEAK** — the mechanism is conceptually correct but produces degenerate numerical results at 4 Hz GPS data resolution (2-4 brake samples per event). The sigmoid is underdetermined, generating non-physical depth values. Ringing improvement is real but achievable more simply.

**Conditions for revival:**
1. **Use car telemetry (~44 Hz Throttle/Brake channels)** for onset detection and sigmoid fitting; apply the fitted sigmoid as a Kalman kind=3 prior with uncertainty reflecting fit quality.
2. **Fix k to a physics-informed range** (10-30 /s for 100-300ms brake-apply time) reducing to a 3-parameter fit.
3. **Constrain |depth| <= max observed raw decel** at each onset — prevents the -144 m/s² artifact.

Without at least (1), M8 cannot be reliably measured on this scoreboard.

---

## Workflow feedback

- **Handoff gap**: The `g2-COMMON.md` scoreboard description says `inp.t` samples are "4 Hz" but doesn't state that brake-regime events contain only 2-4 samples each. This is the critical constraint for M8; it should have been surfaced in the handoff ("check data density before designing the fit model").
- **Improvisation**: The v2 regime-aware `a_post` estimation was improvised after v1 failure (handoff implied a straightforward window-tail estimation). The fix worked for direction but not magnitude.
- **Seam correctness**: The `VariantFn` seam, `CaseInputs`, `_long_accel`, and `make_smoother` all worked exactly as documented. No seam issues.
