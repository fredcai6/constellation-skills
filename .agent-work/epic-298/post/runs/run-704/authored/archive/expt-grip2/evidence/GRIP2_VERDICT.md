# GRIP-2 — Grip evolution: track-vs-tyre decomposition + supplant compound (epic #445 Phase-2)

**Question.** Using the 2022-Spain-R fleet's pit-staggered tyre ages, can we SEPARATE
session-global track-grip evolution `T_track(session_time)` from per-stint per-compound
tyre degradation `μ_tyre(compound, tyre_age)` — and does the physics tyre-degradation
SUPPLANT the incumbent (lap-time-based) compound estimation (`src/compound_prior`)?

**Model fitted (simplest useful, per the ladder).**
```
μ_lat_eff(car,lap) = μ_tyre(compound, age) · T_track(session_time)
log μ_lat(i,l) = a_i (car) + b_{c} + g_{c}·age_l (tyre, age-indexed) + P(t_l) (track, time-indexed)
```
- `μ_lat` = per-lap peak kinematic `v²κ`, load-normalized by `N(v)/m = g + k_df·v²`.
  **k_df FIT jointly** (scanned, selected by min between-lap σ₀): lands **1.0e-4** s⁻²/(m/s)²
  (GRIP-1 borrowed 1.3e-4; here the data prefers the low end — borrowing was close but not fit).
- `T_track = exp(P(t))`, P = centred powers of session-time (order 2), shared across all 15 cars,
  anchored `T_track(t_ref)=1` at the median lap (t_ref=6805 s).
- `μ_tyre` per-compound = `exp(b_c + g_c·age)`, **linear-in-age** (quad-tyre adds <1% σ₀ → not needed).
- Honest covariance: var = smoother epistemic + **σ₀² = (6.0%)²** between-lap envelope drift,
  fit so reduced χ²→1 (the GRIP-1 ×2.6 race-drift inflation, made explicit). ell pinned = 10;
  auto-ell median 1.4 (rejected per GRIP-1); **chi2_pos median 0.99** (pos/speed fit honest).
- **Fleet: 15 cars** (all constructors), **n=384** peak-grip laps; SOFT 209 / MEDIUM 158 / HARD 17.
  HARD only MAG/MSC, late race (17 laps) — sparse, flagged throughout.

---

## (1) Separated track-grip evolution T_track — **RESOLVED, physically sensible (track greens up).**
Linear track coefficient τ₁ = **+0.035 ± 0.0036 (+9.7 σ)**; quadratic τ₂ = −0.0009 ± 0.004
(negligible → track evolution is linear-in-time over the race). T_track rises **+11.9 %**
across the race (0.937 at the start → 1.000 at ref → 1.057 at the end): the track **greens up /
rubbers in**, exactly the expected physics. Cross-check vs the measured DB track temp: 48.3 → 49.1 °C
(**flat & hot**), so the grip rise is **rubber-laydown, not temperature** — the anchor is the
reference lap (temp can't explain it). Direct fleet evidence: SOFT-at-low-age appears at the
race start AND after mid-race pits — e.g. VER/RUS/ALO run SOFT in an early stint (a_peak≈28-32 m/s²)
and again in a late stint at similar ages (a_peak≈33-35 m/s², **+~9 %**); same compound, same ages,
later session-time → higher grip = the T_track signal, isolated by the pit-stagger.

## (2) Per-compound μ_tyre(age) — **degradation EXISTS & is resolved per-compound; the compound RANKING is NOT.**
| comp | C# | μ_fresh (rel) | g = d(log μ)/d(age) | per-compound σ |
|------|----|---------------|---------------------|----------------|
| SOFT  | C3 | **1.008** | −0.00323 ± 0.00093 | **−3.5 σ** |
| MEDIUM| C2 | 0.990 | −0.00238 ± 0.00081 | **−2.9 σ** |
| HARD  | C1 | 0.994 | −0.00323 ± 0.00151 | −2.1 σ |

- **Fresh-grip ranking is right:** SOFT highest fresh μ (1.008), +1.8 % over MEDIUM (0.990) —
  softer compound → more lateral grip, measured purely from forces.
- **All three compounds demonstrably lose grip with age** (each g < 0 at 2–3.5 σ): degradation is
  a real, resolved force-signal, separated from the track trend.
- **BUT the between-compound wear ordering is NOT resolved above the drift floor:**
  SOFT−MEDIUM Δg = −0.7 σ, HARD−MEDIUM Δg = −0.5 σ. The textbook "soft wears fastest, hard slowest"
  monotone ladder does **not** emerge — SOFT and HARD read ~equal slope, MEDIUM slightly lower, all
  overlapping. Honest: GRIP-2 resolves *that tyres degrade* and cleans it of track, but the
  *compound-ordered* degradation rate is at the ~1 σ level here (Spain has only SOFT/MEDIUM with
  real support; HARD = 17 laps/2 cars). Not manufactured into a clean curve.

## (3) IDENTIFIABILITY — **track ↔ tyre is genuinely RESOLVED by the pit-stagger (not confounded).**
- corr(g_compound, track-linear slope): SOFT **−0.39**, MEDIUM **−0.27**, HARD **−0.15** — all far
  inside the |0.9| confound bar.
- **max canonical correlation (tyre-slope block ↔ track block) = 0.49** — with only 3 cars (smoke)
  it was 0.88 (badly confounded); the **full fleet's varied pit timing drops it to 0.49**, i.e. the
  natural experiment supplies real separating leverage. cond(design)=1.5e4 (well-posed).
- Robustness: order-1 (linear) track gives an identical picture (corr 0.49, τ₁ +12 %); quad-tyre
  drops canonical corr to 0.29. The separation is **not** a polynomial-order artifact.
- Verdict: **the decomposition is real.** Track and tyre are separated cleanly; the residual
  track↔tyre covariance is moderate (0.49), not degenerate.

## (4) SUPPLANT vs `src/compound_prior` (incumbent 2022 gold) — **breaks the incumbent's degeneracy; partial supplant.**
2022 Spain: SOFT=C3, MEDIUM=C2, HARD=C1 (verified from DB `compound_c_number`; gold reference = C3).
| comp/C | phys μ_fresh | phys g | gold β (fresh) | gold γ (wear) |
|--------|--------------|--------|----------------|---------------|
| SOFT/C3  | 1.008 | −0.00323 | −0.00002 | **0.000210** |
| MEDIUM/C2| 0.990 | −0.00238 | +0.00059 | **0.000210** |
| HARD/C1  | 0.994 | −0.00323 | +0.00007 | **0.000208** |

- **The incumbent γ is a literal PLATEAU:** gold γ_C1 ≈ γ_C2 ≈ γ_C3 = 0.000210 (identical to 6 digits).
  This matches the recorded findings exactly: gold collapses the degradation axis, and the
  crossover-gate verdict (`compound_crossover_gate_findings.md`) is that **race-lap γ is CONFOUNDED,
  not recoverable without a de-confounding design** (the §7.7 "γ-up ladder is confounded" note).
- **GRIP-2 IS that de-confounding design** (force observable + pit-stagger, not lap time), and it
  **breaks the plateau**: it produces *differentiated*, individually-significant per-compound g
  (−0.0024 to −0.0032, each 2–3.5 σ) where the incumbent produces one tied number. It also separates
  the track-rubber trend (gold buries this in a per-segment fuel/evolution slope + per-race δ).
- **Can it supplant? Partially, and on the right axis.** GRIP-2 cleanly supplants the *track/fuel
  confound* and recovers a real per-compound degradation magnitude + correct fresh-grip ranking
  (SOFT > MEDIUM) that the incumbent's β also gets directionally (β_C3 fastest). But it does **not**
  yet deliver a monotone soft→hard wear ladder — the same axis the incumbent fails on, for the same
  root cause (in 2022 Spain the compound-wear *ordering* is ~1 σ / data-starved, esp. HARD). So:
  **supplants the confound and the plateau; does not yet supplant with a clean compound-ordered γ.**

## (5) Where the SIMPLE model hits its data-utility limit → seeds GRIP-3
1. **Compound-wear ranking is the binding limit:** SOFT/MEDIUM/HARD g separate at only ~0.5–0.7 σ.
   To resolve the *ordering* needs (a) more races / compounds with real support (HARD here = 17 laps),
   and/or (b) tyre-temp / thermal-degradation state — the linear-in-age μ can't tell thermal cliff
   from mechanical wear. **GRIP-3: add tyre-temp (thermal deg) and pool multiple races.**
2. **σ₀ = 6.0 % between-lap drift is the floor** — bigger than the smoother's formal per-lap sd by
   ~40×. Part is real (traffic, fuel-load on N, line choice); the **line-dependence / off-line grip**
   that GRIP-1/2 parked is a prime suspect for shrinking σ₀ → GRIP-3 line-resolved grip.
3. **k_df fit at the grid floor (1.0e-4)** and the modest residual track↔tyre corr (0.49) suggest the
   load model N(v) still under-absorbs at the envelope edge (GRIP-1's incomplete-load caveat) —
   a per-car k_df + ride-height proxy is the next aero refinement.

## Guardrails (proving ourselves wrong)
- **Held-out leave-one-STINT-out posterior-predictive:** trimmed reduced **χ² = 0.76**, frac<2σ = 0.93,
  median z² = 0.42 → the μ_tyre×T_track model **predicts unseen stints within honest covariance**.
  (Raw χ² is dominated by a few near-singular refits when a sparse compound — HARD, 17 laps — loses
  its only stint; those are flagged and trimmed, not hidden: `reduced_chi2_raw` is reported.)
  **Contrast GRIP-1's static-μ: held-out χ²≈35 (falsified).** Adding the evolution state fixes it.
- **Honest-null on the compound RANKING** (§2): reported, not curve-fitted away.
- **Identifiability falsified-or-not honestly** (§3): max canonical corr 0.49 quantified.

## ell
Pinned **ell = 10** (GRIP-1 grip regime). auto-ell median 1.4 (rejected, per GRIP-1: chi2_pos blind
to accel var). **chi2_pos median 0.99** → the position/speed smoother fit is honest.

## Evidence
- `grip2_2022_Spain_R_order2.json` — full fit: per-compound b/g ± sd, track τ ± sd, identifiability
  covariance (per-compound corr + canonical), k_df scan, σ₀, held-out-stint (trimmed + raw).
- `grip2_track_tyre_decomposition.png` — (1) T_track + measured track-temp, (2) μ_tyre(age) curves
  ±1σ, (3) identifiability bars + max canonical corr.
- per-car harvest checkpoints: `.agent-work/expt-grip2/ckpt/grip2_2022_Spain_R_*.json` (15 cars).
- scripts: `scripts/experiments/grip2_run.py`, `grip2_plot.py` (branch expt/448-grip2).

## Bottom line
**Track ↔ tyre decomposition: RESOLVED** (canonical corr 0.49; track greens up +11.9 % at +9.7 σ,
confirmed rubber-not-temp). **Per-compound degradation: resolved as existing** (each 2–3.5 σ) and
**held-out-validated** (χ²≈0.76 vs GRIP-1 static-μ's 35) — the evolution STATE is real and required.
**Supplant: breaks the incumbent's confounded γ-plateau** with a genuine de-confounding design and
recovers correct fresh-grip ranking, **but does not yet supplant with a clean compound-ordered wear
ladder** — that ordering is ~1 σ / data-starved in one race (esp. HARD) and is GRIP-3's target
(tyre-temp + multi-race pooling + line-resolution).
