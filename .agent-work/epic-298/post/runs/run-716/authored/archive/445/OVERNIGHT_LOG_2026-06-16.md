# Overnight autonomous run — epic #445 physics feature engineering (2026-06-16)

Human AFK, granted full reign. Mandate: FEATURE ENGINEERING (not prediction — prediction loses
to recency, don't chase it). Reeval items flagged as possibly funky; investigate, don't paper over.
Build production notes along the way. Each item dispatched as a subagent; Admiral (this session,
Opus) adjudicates, digs into funkiness, assembles PRODUCTION_NOTES.md.

## Foundation (clean, this session)
- Calibrated node caches (per-session smoother χ²≈1): calibrated_{aniso,braking}_nodes.npz, calibrated_hp.json.
- Grip: pure-lateral apex frontier G_lat=A_r+B_c v²; A environmental (not a car axis); RBR-top correct; Haas #2 (grip≠pace).
- Recursive Bayes downforce prior (two-stage Kalman, σ²_op-calibrated R); baseline fingerprint (RBR efficient #1).
- Matérn-7/2 beats 5/2 for the smoother (held-out speed; 4 sessions).

## Dispatched (background)
- **A1 — Longitudinal acceleration math reeval** (Opus). Friction-ellipse projection, B_long=downforce+drag
  decomposition, sensor-cap censoring. Is the math right? Is there a valid longitudinal FEATURE?
  → LONGITUDINAL_REEVAL_FINDINGS.md ; files `longreeval_*`.
- **A2 — HAA tell + apex-speed feature** (Opus). Why high grip / low pace (Haas). Build apex-speed /
  corner-time observable; is it more pace-relevant than frontier-g B?
  → APEX_PACE_FINDINGS.md ; files `apex_*`.
- **A3 — Ribbon + ideal-lap reeval on clean kinematics** (Sonnet). Re-pool track curvature κ(s) and re-run
  the quasi-static ideal-lap sim on calibrated kinematics. Cleaner? Still fixed-fit-noise spread? Funky?
  → RIBBON_IDEALLAP_REEVAL_FINDINGS.md ; files `ribbon_*`.
- **A4 — Matérn-7/2 production validation** (Sonnet). Widen the per-order χ²-calibrated held-out-speed
  test to all 22 sessions / many drivers; production PR plan for src/preprocessing/trajectory.
  → MATERN72_VALIDATION.md ; files `m72_*`.

## Adjudication log
- [dispatch] A1, A2, A3, A4 launched background.
- [A1 DONE — ACCEPTED, overturns a recorded finding] Longitudinal channel is a DUD. The
  "+0.48 corroboration" I logged this session is a **GSAT-clip artifact**: fit_weekend (reused
  verbatim) clips along_eq at GSAT=5.2 — a LATERAL tyre ceiling — silently applied to the
  longitudinal cloud; ~9% high-trail-brake points (whose inflation is computed from B_lat) get
  discarded, manufacturing the coupling. Relax clip → −0.29; remove → +0.04. Also: G_lat
  extrapolated 1.3–2× into the braking regime (80% of points beyond its support, 29% pinned at
  GSAT, 12% imaginary alat/G_lat>1); sensor truncation suppresses the downforce-regime slope 3.4×
  (frontier peaks at ~230 km/h then DECREASES — impossible). No κ·B_lat decomposition recovers drag
  (corr ≈ −0.05 vs CdA). VERDICT: retire the braking channel; only lateral-apex B and independent
  CdA are valid aero observables. Verified vs longreeval_report.json. Corrected findings + memory.
  Production lesson: GSAT clip must be an explicit required arg, never silently leak onto a non-lateral axis.

- [A2 INCOMPLETE — recovering myself] Agent built the HAA frontier baseline + the full apex-speed
  pipeline (apex_extract.py, apex_feature.py — both sound) but ran out of context mid-extraction
  ("Round 4 done" truncated final msg); apex_corners.npz never written, no APEX_PACE_FINDINGS.md.
  HAA frontier baseline (apex_baseline_frontier.json) is solid and confirms the paradox: HAA reads
  HIGHEST frontier-g (3.07) but is near-last in pace (+0.95); FER LOWEST grip (2.20) but 2nd-fastest
  (−0.62) — frontier-g anti-correlates with pace. No SendMessage tool to continue the agent, so:
  re-ran apex_extract.py (background) → apex_feature.py → will write the findings + production notes myself.

- [A3 DONE — ACCEPTED, confirms not overturns] Ribbon = sound track model (clean 87–98% corr to
  contaminated; pooling 100+ laps √N-averages noise; clean slightly truer — Monza tightest radius
  26m clean vs 44m contaminated). Ideal-lap-time = NOT a per-car feature: clean kinematics exposes
  the `A+B·v²` frontier fit as the noise source — B unidentifiable single-weekend (Monza A/B-collinear
  in flat 88–148 km/h range → B pins to bound → ideal 82–84s vs 80.3s pole, util>1 unphysical; only
  Hungary has enough nodes). Confirms the old fixed-fractional fit-noise finding + mechanism (noisy-B).
  Corroborates between/within<1 → season Bayesian prior is the right path. Flags Suzuka short-ell →
  Matérn-7/2 fix (A4 domain). RIBBON_IDEALLAP_REEVAL_FINDINGS.md, files ribbon_*.

- [A2 DONE — ACCEPTED + VERIFIED — HEADLINE WIN] Agent actually completed (its earlier "completed"
  was the harness firing when it yielded to its own bg extraction; it resumed, finished, wrote
  apex_corners.npz 63,702 corners/438 car-weekends + APEX_PACE_FINDINGS.md). My duplicate
  apex_extract.py (bsrv219ne) is redundant — harmless (same output), let it finish.
  **APEX-SPEED IS PACE-RELEVANT.** Verified independently: apex-speed@radius (on-limit, geometry-
  normalized, season-median) Spearman vs quali pace = **−0.891** vs frontier-g's −0.152. HAA resolved:
  #1 grippiest (frontier-g) → #6 (apex-speed) ≈ #8 pace. HAA paradox = aggregation artifact (mean of
  heavy-tailed B, a few near-ceiling nodes inflate slope; MEAN→MEDIAN drops HAA #1→#5) + real mid-corner
  deficit (loses in the 40–120m medium corners that dominate a lap; near-parity at high-g extremes the
  frontier-g is built from). Robust (LOTO −0.85→−0.90). Caveat: only SEASON aggregate stable (per-round
  split-half +0.29); β≈0.32 sub-√R. → PRODUCTIONIZE as a separate CORNERING-PACE channel (alongside,
  not replacing, frontier-g = downforce-ceiling descriptor). First pace-relevant cornering observable in #445.

- [A4 STALLED at 18/22 — but CONCLUSIVE; doc finished by Admiral] Agent stalled (watchdog) after 18
  sessions; left m72_validation_cache.json. Aggregated: **7/2 wins 18/18 sessions** on held-out speed.
  Pooled median 5/2 0.759 → 7/2 0.451 m/s; glitch>5 14.6%→2.5%; short-ell collapse 5/2 3/18 (British/
  Hungarian/Singapore, med 7–11 m/s, glitch 60–71%) vs 7/2 0/18. Cost (Admiral-measured): order-4
  ~1.10× order-3 (91.8 vs 83.3 ms/fit) — O(N) loop dominates, only ~10% overhead (not 1.7×).
  MATERN72_VALIDATION.md written (validation + cost + PR plan: add order param, keep order-3 default +
  analytic P_inf for nesting safety, Lyapunov P_inf for order≥4, regression-gate then flip default).

## CLOSEOUT
- All 4 prongs adjudicated. Assembled PRODUCTION_NOTES.md (capstone). Folded apex win + longitudinal
  retraction into memory. bsrv219ne (redundant apex extract) left to finish harmlessly (same output).
- HEADLINE: apex-speed is the first pace-relevant cornering feature (−0.89); longitudinal retired
  (artifact); ideal-lap not a feature (B unidentifiable); Matérn-7/2 validated 18/18 for production.
