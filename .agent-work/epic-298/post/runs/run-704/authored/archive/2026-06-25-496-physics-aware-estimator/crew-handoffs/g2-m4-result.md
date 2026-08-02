# G2 Spike M4 Result -- Regime-gated process noise

**Date:** 2026-06-24
**Branch/worktree:** worktree-agent-a509df901b2c9dc64 (off feat/physics-aware-estimator-496)
**Scoreboard commit:** 42c2e7a6 (extracted via git show, not cherry-picked)

---

## Mechanism (2-3 sentences)

M4 builds a time-varying roughness schedule r(t) and feeds it into NSStintSmoother so
the jerk process variance is inflated by gate_strength only inside brake-onset windows
([onset - lead_s, onset + trail_s]), and stays at 1.0 elsewhere. Onsets are detected
from regime transitions into "straight_brake" and/or a threshold on the raw speed
derivative (dv/dt < -thresh_g x 9.81 m/s2). No kind=3 anchor is added -- this is a
pure process-noise mechanism, fully isolated from the anchor channel.

---

## Two-cycle invariant

decision:two_cycle_external_anchor_design is NOT touched. M4 adds zero anchor
observations. The roughness schedule only controls the predict-step Q inflation;
anchor source and placement are unchanged. No extension needed.

---

## Scoreboard results

All numbers from a single run on common G1 cases: (2023, Bahrain/Monaco/Belgium, VER).
Raw reference: Bahrain raw_knee=-52.13, Monaco raw_knee=-37.51, Belgium raw_knee=-38.84.

### Knee table (m/s2; decel negative; closer to raw is better)

| Circuit | gaussian | kind3 | m4_default | m4_tight | m4_wide | m4_strong | m4_regime_only | m4_dv_only | raw_knee |
|---------|----------|-------|------------|----------|---------|-----------|----------------|------------|----------|
| Bahrain | -39.50 | -39.42 | -39.52 | -39.72 | -39.67 | -39.50 | -39.52 | -39.52 | -52.13 |
| Monaco  | -38.07 | -37.60 | -38.14 | -37.89 | -38.16 | -38.18 | -38.14 | -38.14 | -37.51 |
| Belgium | -34.93 | -37.41 | -36.98 | -34.92 | -37.56 | -37.47 | -36.98 | -36.98 | -38.84 |

### Knee gap vs raw (knee - raw_knee; positive = shallower; closer to 0 is better)

| Circuit | gaussian | kind3 | m4_default | m4_tight | m4_wide | m4_strong | m4_regime_only | m4_dv_only |
|---------|----------|-------|------------|----------|---------|-----------|----------------|------------|
| Bahrain | +12.63 | +12.71 | +12.61 | +12.42 | +12.46 | +12.63 | +12.61 | +12.61 |
| Monaco  |  -0.56 |  -0.09 |  -0.63 |  -0.38 |  -0.65 |  -0.66 |  -0.63 |  -0.63 |
| Belgium | +3.91 | +1.43 | +1.86 | +3.92 | +1.28 | +1.37 | +1.86 | +1.86 |

### Non-throttle ringing (m/s2; raw_ring shown; ringing <= raw_ring is good)

| Circuit | gaussian | kind3 | m4_default | m4_tight | m4_wide | m4_strong | m4_regime_only | m4_dv_only | raw_ring |
|---------|----------|-------|------------|----------|---------|-----------|----------------|------------|----------|
| Bahrain | +0.46 | +0.41 | +0.72 | +0.35 | +0.47 | +0.67 | +0.76 | +0.49 | -2.86 |
| Monaco  | +13.14 | +13.38 | +13.99 | +14.18 | +14.14 | +14.12 | +13.98 | +13.38 | +5.64 |
| Belgium | +4.36 | +4.44 | +5.69 | +5.57 | +5.93 | +6.05 | +5.69 | +4.36 | +4.57 |

### Ringing over ceiling (ringing - raw_ring; <=0 is good)

| Circuit | gaussian | kind3 | m4_default | m4_tight | m4_wide | m4_strong | m4_regime_only | m4_dv_only |
|---------|----------|-------|------------|----------|---------|-----------|----------------|------------|
| Bahrain | +3.32 | +3.28 | +3.58 | +3.22 | +3.33 | +3.53 | +3.62 | +3.35 |
| Monaco  | +7.50 | +7.73 | +8.34 | +8.54 | +8.49 | +8.47 | +8.34 | +7.73 |
| Belgium | -0.21 OK | -0.13 OK | +1.13 FAIL | +1.00 FAIL | +1.37 FAIL | +1.48 FAIL | +1.13 FAIL | -0.21 OK |

### Sweep parameter summary

| Variant | gate_strength | lead_s | trail_s | thresh_g | use_regime | use_dv |
|---------|---------------|--------|---------|----------|------------|--------|
| m4_default | 6.0 | 0.30 | 0.50 | 1.5 | Y | Y |
| m4_tight | 4.0 | 0.15 | 0.30 | 2.0 | Y | Y |
| m4_wide | 8.0 | 0.50 | 0.80 | 1.0 | Y | Y |
| m4_strong | 10.0 | 0.30 | 0.50 | 1.5 | Y | Y |
| m4_regime_only | 6.0 | 0.30 | 0.50 | -- | Y | N |
| m4_dv_only | 6.0 | 0.30 | 0.50 | 1.5 | N | Y |

---

## Honest failure modes

### 1. Bahrain: gate has essentially no effect on the knee (CRITICAL)

The Bahrain knee gap stays near +12.4 to +12.6 across ALL sweep settings vs gaussian +12.63 --
at best 0.2 m/s2 improvement, nowhere near closing the 12.6 m/s2 gap to raw (-52 m/s2).

Root cause: The brake slam occupies ~1-2 GPS samples at 10 Hz. Inflating Q during the onset
window changes the predict step, but the Kalman-RTS backward smoothing pass still rounds the knee
because the GPS position data constrains the state from both directions in time. The backward pass
is the dominant constraint; Q inflation on the forward pass is too weak to rescue a transient
that requires the filter to reproduce a 52 m/s2 peak within 0.1 s.

### 2. Monaco ringing gets WORSE with M4

Most M4 settings worsen Monaco ringing from +13.14 (gaussian) to +13.99-14.18.
Monaco's short straights create onset windows that overlap with coast/non-throttle regions where
the smoother rings, and loosening Q there promotes overshoot exactly where the ringing artifact
already lives. m4_dv_only (13.38, matching kind3) is the only setting that does not worsen vs
gaussian -- the speed-derivative detector fires less on Monaco's short coast segments.

### 3. Belgium ringing violations (most settings)

Most M4 settings break Belgium's ringing constraint (ringing_over_ceiling +1.0 to +1.5 vs -0.21
with gaussian). m4_dv_only is the sole exception (-0.21, ringing_ok=True) because the
speed-derivative detector avoids triggering on Belgium coast transitions.

### 4. Best-case variant (m4_dv_only): mixed

m4_dv_only (gate_strength=6, lead=0.3s, trail=0.5s, thresh=1.5g, dv-only detection):
- Belgium: knee gap 1.86 (better than gaussian 3.91; slightly worse than kind3 1.43), ringing_ok=True
- Monaco: ringing 13.38 (matches kind3; does not worsen gaussian baseline)
- Bahrain: knee gap 12.61 (no meaningful change)

Belgium gain is real but kind3 already delivers 1.43 there with a cleaner mechanism.
Bahrain -- the critical defect -- is unaddressed by any M4 configuration.

---

## Soundness self-assessment

The Belgium improvement from m4_dv_only is credible: loosening Q around hard-braking events
(speed-derivative triggered) lets the smoother track position through Spa's Raidillon-Pouhon
complex more faithfully. The Bahrain failure is fundamental -- GPS at 10 Hz cannot give the filter
sufficient support to reproduce a 52 m/s2 peak in 0.1 s regardless of how large Q is made. The
Monaco ringing worsening is not an artifact; it reflects the Q loosening during onset windows that
coincide with Monaco's non-throttle coast segments. The m4_dv_only configuration is the safest
because the speed-derivative detector is more specific to true hard-braking events vs regime
classification which picks up slow entries.

---

## Invariant note

decision:two_cycle_external_anchor_design: NOT touched. M4 adds zero anchor observations.
Roughness schedule modulates predict-step Q only. Anchor source = external raw a_long;
placement = plateau-only; two-cycle = unchanged. No extension.

---

## Re-run command

From worktree root (C:/Programs/f1Brainz/.claude/worktrees/agent-a509df901b2c9dc64):

  py scripts/run_m4_spike.py

Requires:
- src/physics/layer2/m4_regime_gated.py (present in worktree)
- src/physics/layer2/scoreboard.py (extracted from feat/physics-aware-estimator-496)
- cache at C:/Programs/f1Brainz/data/telemetry

---

## Prototype files

- C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/m4/m4_regime_gated.py
- C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/m4/run_m4_spike.py

---

## RECOMMENDATION: WEAK

Regime-gated process noise (M4) is WEAK for the primary target (Bahrain knee deepening).
The mechanism fails to recover the -12.6 m/s2 gap between smoother and raw sensor. The
fundamental constraint is that GPS position samples at 10 Hz cannot support a 52 m/s2 peak
in 0.1 s regardless of Q inflation magnitude -- the backward Kalman-RTS pass rounds it away.
The best variant (m4_dv_only) improves Belgium (gap 3.91->1.86) without ringing regression
but kind3 already achieves 1.43 there. Monaco ringing worsens with regime-based detection.
M4 is not a viable standalone mechanism for the Bahrain defect; it does not address the
backward-smoothing bottleneck that is the actual root cause.

---

## Workflow feedback

- Handoff gaps: Handoff states "The G1 scoreboard src/physics/layer2/scoreboard.py IS
  committed and present" but it was only on feat/physics-aware-estimator-496, not on the
  agent's worktree branch. Required git-show extraction. Should either merge scoreboard to
  the worktree branch before dispatching, or state which branch to extract from.
- Context rediscovered: Had to inspect NSStintSmoother.__init__ signature to confirm
  order=4 is supported (handoff only mentioned order=3 path) and to identify HP attributes
  to read off a dummy smoother instance.
- Instructions improvised around: checklist-engine.md not found at skill reference path;
  plan driven mentally. Handoff was clear enough to proceed without blocking.
- What would have made this easier: Ensure scoreboard.py is merged into the agent's
  worktree branch, or add an explicit "git show branch:path > dest" prep step to the prompt.
