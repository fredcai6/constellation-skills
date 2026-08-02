# #512 — Regime-Capability Vector Readiness — VERDICT (revised)

**Issue:** #512 (C3, epic #509). **Pool:** 2023-Q five-view estimate store
(`physics_estimates_g3wired.db`), 10 constructors × 22 rounds, 216 ok / 4 error.
**Evidence:** `reports/physics/regime_capability_2023Q.md` (+ plots), core
`src/physics/layer2/regime_readiness.py`. **Mode:** measured, NOT wired.

## Framing (the bar is "how much certainty can we get", not a 2σ pass/fail)
F1 quali is decided in hundredths — car capabilities are genuinely fine-margin, so a clean ≥2σ
per-axis car-separation was never the right bar. The readiness output is therefore the
**continuous recoverable signal** per axis (and its honest uncertainty), and the real question is
**what a covariance-bearing relative feature built on it can do downstream** (Phase P A/B), not a
binary gate. The `separation_ratio_manageable=2.0` flag is a **reference line, not a gate**.

## Two complementary lenses (both measured here)
1. **Raw per-session parameter (additive car-vs-circuit, `frac_team`):** circuit-DOMINATED —
   `frac_team` 0–4% vs `frac_circuit` 0.44–0.65. Expected fingerprint of cars set up per-track;
   the raw number is not directly a car axis. Large `frac_resid` (0.31–0.75) = real car×track
   structure (capability is track-conditional, NOT "cars identical").
2. **Pooled static latent vs its OWN uncertainty (`separation_ratio`, the pooling thesis):** the
   honest test of "pool many viewpoints → recover a static car latent". Result below.

## Static-latent separation (the headline) — 2023-Q
| Axis | separation_ratio (static car-spread / own σ) | note |
|---|---:|:--|
| **straight_line / max_power_w** | **1.16σ** | best *clean* axis; power is physically static |
| braking / brake_decel_ms2 | 1.41σ | weak |
| slow_corner / lateral_mech_grip_g | 0.74σ | weak |
| traction / traction_aero_accel_per_m | 0.73σ | weak (setup-conflated) |
| fast_corner / lateral_aero_grip_g | 0.61σ | weak (setup-conflated) |
| straight_line / power_drag_area_m2 | 0.59σ | weak (setup-conflated) |
| traction / traction_accel_ms2 | 0.57σ | weak |
| coast / coast_drag_area_m2 | 0.55σ | weak (setup-conflated) |
| coast / coast_rolling_decel_ms2 | 4.73σ | **separates, but a diagnostic PU/engine-braking fingerprint, not a capability** |
| braking / brake_aero_decel_per_m | 9.24σ | **DISCOUNT — artifact of under-estimated σ** (coheres with its zstd 1.93 over-claim), not real |

Plus covariance honesty (LOO zstd): mild-to-moderate over-claiming across the board (1.3–1.9);
only `max_power_w` calibrated (1.28).

**Static-power ordering** (max_power_w, n≈20–22): Ferrari 655.3 kW ± 9.0 → Williams 648.0 →
McLaren 643.7 → Haas 643.1 → Aston 640.9 → Alfa 636.7 → **Red Bull 633.3 (7th)** → Mercedes 628.8 →
Alpine 628.8 → AlphaTauri 623.8. All within overlapping σ — **do not over-read**. Note RBR (the
dominant 2023 car) is *mid-pack on fitted peak power* → consistent with the real differentiator
being **aero/drag efficiency**, which is exactly the **setup-conflated** axis the raw pooled mean
can't isolate.

## Verdict: CONTEXTUAL (per component)
The regime-capability vector carries a **weak, fine-margin, covariance-bearing relative signal** —
not a clean GO, not a flat NO-GO.

- **straight_line / power → CONTEXTUAL (strongest clean axis).** ~1.16σ, the only calibrated axis.
  Carry forward as a covariance-bearing *relative* feature; let Phase-P A/B decide if it helps.
- **braking → CONTEXTUAL-weak** (1.41σ, over-claimed σ).
- **slow/fast-corner grip, drag → CONTEXTUAL-marginal** (0.6–0.7σ; aero/drag setup-conflated —
  the *likely* real differentiator, recoverable only with a structured base-vs-setup model).
- **traction → CONTEXTUAL → #557** (flat per-sample + param-aliased −0.92; #557 corner-indexed
  cross-lap pooling is the recovery path; position-locked signal is real, r=0.925).
- **coast → CONTEXTUAL-diagnostic** (`coast_rolling` separates at 4.73σ but is a PU/engine-braking
  fingerprint, not a capability; `brake_aero` 9.24σ discounted as a σ artifact).

**Bet-bounding takeaway:** don't expect clean single-axis car-separation from raw pooled
capabilities; the recoverable per-axis signal is fine-margin (≲1.4σ on clean axes). The honest next
move is to **carry the covariance-bearing relative vector into Phase-P A/B and measure downstream
lift** ("see what we can do with it"), and to pursue the two concrete levers below where the signal
is most likely hiding.

## Forward levers (routing → triage)
1. **Power, restrict to power-observable sessions.** Peak-power identifiability is poor on
   short-straight tracks (inflates per-session σ → depresses `separation_ratio`). Re-running power
   on long-straight sessions only may lift 1.16σ. → triage.
2. **Aero/drag: structured base-vs-setup model.** The pooled mean conflates per-track downforce
   choices; a model with a downforce-level covariate (car's base aero platform + per-track setpoint)
   is the path to isolate the likely real differentiator. → triage (feeds #450 Phase-P + #499 multi-state CdA).
3. **Phase-P A/B with the covariance-bearing relative vector** — the direct "what can we do with it"
   test. → comment #450.
4. **Systematic σ over-claiming (zstd 1.3–1.9)** → links #506 (data-driven σ-floors) — would
   re-scale both the honesty and the static-separation denominators.
5. **coast_rolling 44%/4.73σ** → links #502 (PU index): a usable engine-braking PU fingerprint?
6. **Degenerate-ratio guard** (flag implausibly-small `med_sigma_mu`, e.g. brake_aero) → triage (small dashboard hardening).
7. **Rubric thresholds** → `decision:regime_readiness_rubric` (RECORD that 2σ is a reference, not a gate).

## Done-done (spec §4)
- Full test coverage: 42 (core) + 26 (dashboard) = 68 green. ✓
- Honest covariance first-class: real 2×2 blobs (param-pair); LOO out-of-sample zstd + LOO tau_resid;
  static estimate carries σ_μ. ✓
- Single canonical path: `EstimateStore → compute_readiness/static_separability → dashboard`. ✓
- Traceable data→dashboard: `reports/physics/regime_capability_2023Q.md` + plots. ✓
- Verdict: **CONTEXTUAL** (fine-margin covariance-bearing relative signal; power strongest clean
  axis ~1.16σ; traction → #557; coast diagnostic) — carry into Phase-P A/B; do not treat as a clean GO.
