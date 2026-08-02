# Drag force — first round of estimation (epic #445 Phase-2)

Aero = drag (downforce lumped/parked). Model v2 (MODEL_SCOPE): aero = ½ρ|v_air|²·CdA(θ)·f_follow(gap),
decomposed along-velocity (drag) + perpendicular (side force). First cut = free-air clean-coast CdA
baseline + cr + global slipstream f_follow(gap). θ-dependence and δ_wind are LATER layers (not this round).

## DRAG-1 — Free-air clean-coast CdA + global slipstream (worktree expt-drag1, branch expt/448-drag1)

Question: measure the clean intrinsic CdA + rolling cr from FREE-AIR, CLEAN-COAST segments (correcting
F2's CONTAMINATED pooled CdA≈0.94, which mixed coast-behind-cars), and fit the global slipstream
drag-reduction f_follow(gap).

### Keep it LIGHT and SINGLE-PASS (anti-thrash — hard lesson)
- This is the LONGITUDINAL drag first cut — use the CLEAN SPEED CHANNEL directly (v, and ΔV/decel over
  coast segments); do NOT run per-lap trajectory-smoother fits (not needed for longitudinal drag; the
  smoother is for geometry/grip). Positions are needed only for gap-to-car-ahead (free-air segmentation),
  which is cheap.
- Run as ONE bounded script invocation, FOREGROUND-polled, modest scope (2 races, full field for gaps).
  Evidence to `.agent-work/expt-drag1/evidence/` (define EVID = an ABSOLUTE path under THIS worktree's
  .agent-work; do NOT hardcode a different repo path). NEVER background a long step and end the turn.

### Method
1. COAST candidates: Throttle≈0 (e.g. <3%) & Brake=0, across the session.
2. CLEANLINESS GATE (user — hybrid-era contamination): off-throttle in the hybrid era is NOT free-roll —
   ERS HARVEST and engine OVERRUN add deceleration that fakes drag; energy CLIPPING makes it erratic.
   Reject contaminated coast: keep only segments whose deceleration is CONSISTENT with pure aero+rolling
   (decel ∝ v², smooth, repeatable at the same track location lap-to-lap); reject over-decelerating /
   erratic segments. Prefer HIGH-SPEED coast (drag dominates → strong signal). "ID cleaner sections and
   believe them" — quality over quantity. Report how many segments survive the gate and the gate's effect.
3. FREE-AIR segmentation: compute gap-to-car-ahead from the FIELD's positions/timing (FastF1 has all
   cars; gap = time to car ahead at that track position). FREE-AIR = gap > ~1.5-2 s; FOLLOWING = below.
4. Fit CdA_freeair + cr on free-air clean coast: −a_long = cr + ½ρ(CdA/m)·v_air², v_air = v_ground −
   headwind-along-heading (station wind, BASIC — full CdA(θ) deferred to the next layer). Air density from
   weather (ideal gas). Honest DRIFT-INFLATED covariance (per-lap scatter 4-5× formal SE, F2/G1). Mass
   anchored (~798 kg + fuel).
5. GLOBAL slipstream f_follow(gap): from FOLLOWING clean-coast segments, fit the field-shared drag
   reduction as a function of gap (NOT of who's ahead). Free-air anchors f_follow→1.
6. DRS conditioning (DRS-open coast is rare per F2 — check/report).
7. Compare CdA_freeair to F2's contaminated 0.94 — how much does free-air + cleanliness move it?

### Guardrails
Held-out coast segments (predict ΔV, score); does the cleanliness gate TIGHTEN CdA (lower σ) vs ungated?
Honest-null: if clean free-air coast is too rare in the hybrid era to fit (esp. f_follow), say so + report
how much survives. Covariance is the referee.

### Rules
Offline cache `C:/Programs/f1Brainz/outputs/cache` (raw streams, never get_telemetry; pos dm, speed km/h);
DB + weather via FastF1 session; sessions 2022 Spain R + one more race (varied field/gaps); `py` not
`python`; numpy/scipy only; commit+push; FOREGROUND single bounded run. 

Return: CdA_freeair + cr ± honest covariance (vs F2's 0.94); the cleanliness-gate effect (survivors,
σ tightening); f_follow(gap) curve (or honest-null if too little following-coast); DRS note; held-out;
evidence paths.
