# Production vs Exploration — Static Layer-by-Layer Audit (#445)

**Run 2026-06-17.  Baseline: VER/RBR @ Hungary 2023** (the only "best-behaved"
track in the notes — B identifiable; Monza's B collapsed, Suzuka data-failed).
Method: hold geometry + params STATIC (cached ribbon, cached/recorded params),
feed both implementations, diff.  Scripts: `static_sim_compare.py`,
`static_gripfit_compare.py`.

The exploration pipeline (user's framing): gather PVT → Matérn smoother → smooth
PVAT → layer physics → play physics over the median lap (ribbon) → ideal lap.

---

## Headline

The **longitudinal/drag channel** — the one the exploration found most
trustworthy — was ported faithfully AND hardened in production.  The
**lateral/grip channel** — the cornering signal the exploration identified as the
actual pace core (apex-pace −0.89) — was re-implemented with a weaker method that
**fails on real data and silently falls back to a generic default**.  The
cornering product is the weak link, consistent with the validation's −0.43-vs-−0.89
apex gap.

---

## Layer 1 — Smoother (PVT → PVAT)

**SHARED CODE, aligned.**  Both the exploration ideal-lap path (`ribbon_reeval.py`)
and the production engine (`physics_adapter`) import the SAME
`src.preprocessing.trajectory.StintSmoother`.

- It is **Matérn-5/2** (`smoother.py:125` → `matern52_sde`; `dynamics.py` defines
  only the 5/2 SDE).
- The validated-better **Matérn-7/2** (`envelope/matern_smoother.py order=4`,
  `MATERN72_VALIDATION.md`: reaches χ²≈1 at moderate ell, differentiable accel)
  was **never wired into either pipeline.**  Both run 5/2.  7/2 is an unadopted
  improvement, not a prod/expl divergence.

## Layer 2 — Ribbon (median-lap geometry)

**GAP: production has no ribbon-builder.**

- Exploration `build_clean_ribbon` pools 100–159 laps (VER+HAM Q+R) → mean XY →
  κ(s).  √N noise-averaging gives a clean Rmin (Hungary 27 m, Monza 26 m).
- Production `PhysicsSimulator` consumes an EXTERNAL `track_profile`
  (distance_m, curvature); it builds no geometry of its own.  The validation fed
  it PER-LAP curvature → noisier κ.  This per-lap-vs-pooled difference is a prime
  suspect for the apex −0.43-vs-−0.89 gap.

## Layer 3 — Parameter fits

| Sub-channel | Exploration | Production | Verdict |
|---|---|---|---|
| **Drag** | `drs_joint_fit` / `full_q_pd`: p90 per-speed-bin frontier, joint DRS `a=P/(mv)−0.5ρ·CdA·v²/m` | `fit_drag_throttle`: **same** frontier + joint solve, **+ honest cov, cond#, SNR gate** | **Aligned + hardened ✓** |
| **Power** | single scalar P | `fit_power_trajectory`: monotone P(t) grid | Richer, same physics ✓ |
| **Grip envelope** | `fit_grip_clean`: per-speed-bin p90, `min(A+B·v²,Gsat)`, bounds A∈[1,3] B∈[5e-4,5e-3] | `fit_envelope`: **global-top-quantile linear lstsq, NO speed-binning, NO saturation, NO bounds** | **DIVERGENT + DEFECTIVE ✗** |
| **Apex extract** | path-geometry κ=dθ/ds (well-conditioned) | per-corner argmin(v) apex (same idea) but radius from **kinematic κ=\|v×a\|/v³** unless a geometry curvature column is supplied | Noisier radius → log R noise (#484) |

### The grip-fit defect (most important finding)

On the SAME cached RBR/Hungary apex cloud (1054 nodes, 85–160 km/h):

| | A0 / A (intercept) | A2 / B (aero) | grip @ 60 km/h | grip @ 300 km/h |
|---|---|---|---|---|
| Exploration | 1.60 g | **+0.00095** (rises) | 1.86 g | 5.20 g (saturated) |
| Production | 3.37 g | **−0.00079 (NEGATIVE)** | 3.34 g | 2.70 g (falls) |

Production returns a **negative aero coefficient** — grip *decreasing* with speed,
physically backwards.  Cause: the apex cloud is a narrow 85–160 km/h band where the
tightest (slowest) corners carry the highest grip; a global-top-5%-quantile LINEAR
fit with no speed-binning picks up the spurious "slower = more grip" correlation and
infers negative aero.  The exploration **binned by speed first** precisely to remove
that speed–grip confound — and production ported that frontier method for DRAG but
NOT for GRIP.

**Consequence in the live pipeline:** `parameter_estimator.py` rejects negative A2
(`fallback_reason_lat="negative_A2"`) → falls back to DEFAULT grip.  So the per-car
cornering ceiling is frequently thrown out and replaced by a generic default — the
per-car cornering discrimination is lost at the grip-envelope level.

## Layer 4 — Ideal-lap sim

Same forward-backward quasi-static skeleton.  Corner-entry caps AGREE (solve the
same `v²κ = A0 + A2ρv²`; apex min-speed 86.3 vs 86.6 km/h).  Structural diffs:

1. **No grip saturation** in production (exploration caps at Gsat=5.2 g).
2. **Start-at-rest bug (#28):** `simulator_start_speed_ms=0.0` starts the flying
   lap at 0 m/s.
3. **No DRS-open straight drag** in production (closed CdA everywhere; exploration
   switches to CdA_open on straights — worth +0.81 s at Hungary).
4. **Corner-exit traction formulation:** exploration `min(√(G²−a_lat²)·g, P/mv)−drag`
   (tyre-grip & power as independent ceilings); production scales the power-limited
   accel by the grip-ellipse factor `(P/v−drag−roll)·√(1−(a_lat/a_lat_max)²)`.

On identical hand-mapped (positive-A2) params the two lap times agreed to **0.09 s**
— but via OFFSETTING errors (exit-too-fast from no-Gsat vs start-too-slow), not clean
agreement.  With production's OWN (negative-A2 → fallback) grip the ceiling diverges
more.

---

## Implication for implementation (for discussion — not yet acted on)

**Doctrine (user, 2026-06-17):** matching the exploration is DIAGNOSTIC SCAFFOLDING,
not a destination — keep parity only as far as it surfaces unknown issues, then
switch to the correct implementation.  Do NOT port the exploration's own bugs to
match (e.g. the grip-fit hard-bound collapse that gave Monza util>1, the 100 m/s
straight clamp, Matérn-5/2 over 7/2).  Once a layer's comparison has yielded its
findings, build it right.

1. **Grip-envelope fit is the priority.**  Take the exploration's per-speed-bin
   frontier + saturation METHOD into `LateralEnvelopeFit` (mirror what was already
   done for drag), but do it RIGHT: honest A/B covariance + report identifiability
   rather than slamming into hard bounds (the bound-collapse was a documented
   exploration failure).  Open design question: A (mechanical) vs B (aero) is
   genuinely underdetermined from one narrow-band weekend — the exploration's own
   PRODUCTION NOTES recommend a **season-level Bayesian downforce prior** to borrow
   strength across rounds.  Decide single-session-frontier vs season-prior.
2. **Apex radius = LOCAL path geometry** on the per-car processed state
   (`dθ/ds` off the car's own smoothed XY), NOT kinematic `|v×a|/v³`, and NOT the
   pooled ribbon.  Apex pace is a PER-CAR signal; the ribbon (cross-car mean) would
   wash out the per-car cornering line.  Ties to #484.
3. **Ribbon-builder** (Layer 2, ideal-lap-SIM geometry ONLY — separate from #2):
   production needs a track κ(s) source for the ceiling sim, or must accept per-lap
   noise; either way it should own curvature, not consume it.
4. **Switch to right, not match:** Matérn-7/2 adoption (validated better; do it when
   we touch the smoother); Gsat ceiling in the sim; start-at-rest (#28); DRS-open
   straight drag in the sim.
