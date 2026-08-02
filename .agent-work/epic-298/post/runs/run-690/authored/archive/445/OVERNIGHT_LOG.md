# Overnight autonomous exploration — epic #445 physics (2026-06-14 night)

Human AFK, granted authority to explore autonomously: "try audacious ideas, keep
exploring, take your time." Admiral = this session. Source-of-truth context:
`.agent-work/445/PIPELINE_FINDINGS_2026-06-15.md`.

## The new idea (human, this turn)
Before going deeper into compounds: **chase a prior through the season.** Thin-data
tracks (Monza, few corners) struggle on a fresh per-race solve, but ~13 races
precede Monza. Carry a per-car capability PRIOR forward race-to-race and UPDATE it
each weekend — upgrades are perturbations to the prior (process noise / jumps), not
a reason to re-solve. "An update to a prior, not a fresh solve."

## Two prongs (dispatched) + my thread
- **Prong A — prior-building architecture (subagent, Opus, bg).** Sequential
  Bayesian/Kalman season filter for car GRIP capability. Latent must be config-
  invariant (per-track B is wing-dependent). Prototype on the 13 pre-Monza 2023
  rounds → show Monza posterior beats the thin Monza-only fit.
  Files: season_prior*.py → SEASON_PRIOR_FINDINGS.md.
- **Prong B — compound/de-confound hardening (subagent, Sonnet, bg).** Harden
  grip_deconf.py: robustify SAR-Suzuka outlier; clean-air gate to explain the
  Mercedes race-vs-quali flip; per-compound wear; cross-validate.
  Files: deconf2*.py → DECONF_FINDINGS.md.
- **Thread C — me (audacious).** Validate the prior-chasing architecture on the
  DRAG channel first — the one channel we TRUST (cross_circuit: drag re-fits
  sensibly, RBR efficient / Merc draggy is known ground truth). If a season drag
  prior cleanly tracks and thin tracks borrow strength, the architecture is proven
  independent of grip noise → clean "architecture works, grip data is the limit"
  triangulation. Files: drag_prior*.py.

## Operating rules tonight
- Additive files only; namespaced per thread; no edits to shared modules.
- Cache collected nodes to .npz (many-race collection is expensive).
- Measured negatives are complete results. Honesty over hope; surface artifacts.
- Log dispatches / rulings / merges below as they happen.

## Log
- [dispatch] Prong A (season-prior architecture, grip) — Opus, background.
- [dispatch] Prong B (de-confound hardening) — Sonnet, background.
- [start] Thread C (drag-channel season prior) — me.
- [DONE] Thread C (drag prior) → DRAG_PRIOR_FINDINGS.md. ARCHITECTURE VALIDATED:
  season forward-filter recovers known 2023 DRAG CHARACTER (RBR −0.033, WIL −0.013
  = low drag; FER +0.016, MERC +0.032 = high drag), tames thin races, tight season
  σ. Engine power NOT recoverable (P↔CdA/ERS degeneracy; same-engine MERC/WIL not
  closest) — observability limit, not architecture. Lesson: prior-chasing delivers
  iff the per-race observable is clean.
- [DONE] Prong B (de-confound hardening) → DECONF_FINDINGS.md. Strong qualified
  NEGATIVE: clean-air gating does NOT reconcile the Merc-Hungary flip (real race
  operating-point diff, not dirty air); SAR-Suzuka is a key-level data artifact
  (needs per-key drop, Huber insufficient); tyre terms DON'T transfer across tracks
  (CV ~0); per-compound wear leaks the quali/race session intercept. VERDICT: quali
  is truth for downforce (best between/within ratio 2.88), race is truth for nothing
  yet. RBR-high-downforce survives every fit = most robust fact.
- [running] Prong A (grip season prior) — the heavy one (13-race Kalman collection).

## SYNTHESIS so far (2 of 3 threads in)
Convergent, trustworthy car signals are RELATIVE, QUALI, SEASON-FILTERED:
- DRAG character (RBR/WIL slippery, MERC/FER draggy) — recovered cleanly, known-true.
- DOWNFORCE in quali (RBR high, Merc fast-corner-weak) — robust across all fits.
Race data = volume but un-transferable confounds → quali-only basis. Prior-chasing
(season filter) is the right tool to beat per-race noise/thin data — VALIDATED on
drag. The trustworthy "capability fingerprint" = season-filtered quali relative
descriptor per channel. RBR = efficient high-DF/low-drag benchmark; Williams =
low-drag/low-DF; Mercedes = draggy + quali fast-corner-weak.
- [DONE] Prong A (grip season prior) → SEASON_PRIOR_FINDINGS.md. POSITIVE: chasing a
  config-invariant downforce-offset prior through 13 pre-Monza races makes the Monza
  posterior 84% tighter, 20× more teammate-consistent, 8× closer to season truth
  (rank-corr +0.50 vs fresh +0.05), RBR#1/Williams#4 (fresh gave nonsense). Robust
  Williams-last/Merc-#3; RBR-vs-FER top tie stays below the floor. Borrow-strength
  VALIDATED. Flagged: Zandvoort A-degeneracy (anchor A globally), RTS smoothing next.
- [DONE] Thread D (me) → FINGERPRINT_FINDINGS.md. CAPSTONE: fused the two validated
  season channels (Prong A downforce + Thread C drag). All 4 constructors separate
  into correct KNOWN-2023 quadrants: RBR[hiDF,loDrag]=efficient, FER[hiDF,hiDrag]=
  draggy-grippy, WIL[loDF,loDrag]=slippery minnow, MERC[loDF,hiDrag]=draggy-no-DF.
  The RBR-vs-FER tie (0.21σ downforce) BREAKS on drag (1.95σ). Aero-efficiency: RBR
  +2.33 clear #1. The capability fingerprint the program chased — emerges only from
  the recipe RELATIVE + QUALI + SEASON-FILTERED + MULTI-CHANNEL. Recovers CHARACTER
  (known), not pace/championship (Merc P2 despite worst aero quadrant) — not yet a
  predictor.
- [start] Thread D2 (me): generalization — drag character for ALL 10 constructors
  vs known straightline rankings (cheap, car_data only).

- [DONE] Thread D2 (drag character, all 10 teams) → drag_fingerprint10.py. PARTIAL
  generalization (honest bound): extremes correct (AMR draggiest +0.057 ✓, RBR/WIL
  slippery ✓, MERC draggy ✓) but midfield within noise (±0.034σ on ±0.06 spread) and
  confounded — McLaren reads draggy because the simple filter AVERAGES across its
  mid-season step-upgrade (needs Prong A's adaptive jump term); Alpine tag likely
  wrong (engine-limited, not draggy). The fingerprint is cleanest for cars with
  DISTINCT character + STABLE platform; blurs in the midfield noise floor and for
  step-change upgrades.

## NOT launched (compute judgment)
Full-grid (10-team) GRIP season prior: would need heavy Kalman collection (~10 teams
× 14 races) AND the adaptive jump term for mid-season upgrades. The 10-team DRAG run
shows the midfield sits at the noise floor, so marginal insight is bounded — not
worth the unsupervised heavy compute. Clearly-scoped next step for human approval.

## SESSION 2 (compute unconstrained — "just try things"): the PREDICTION north star
- [DONE] Full-grid grip collection (season_prior_collect_full.py): 10 teams × 22 races
  quali nodes → season_prior_nodes_full.npz.
- [DONE] Prediction tests (predict_drag_track/predict_grip_track/predict_combined.py)
  → PREDICTION_FINDINGS.md. DECISIVE NEGATIVE across 3 tests:
  1. drag→quali pace: NULL (quali is grip-dominated; LFO rank-corr −0.14).
  2. downforce→quali pace: WEAK/WRONG — cross-sectional −0.37 with gross failures
     (Haas highest-DF but slowest; RBR low-DF but fast); leave-future-out −0.15 vs
     last-race +0.55 vs season-avg +0.69 (fingerprint ANTI-predictive).
  3. does physics ADD to pace baseline? NO — DEGRADES it (season-avg +0.696 →
     +grip +0.649 → +grip+drag +0.633; helps in 12-18% of races).
  STRUCTURAL: physics-channels→lap-time is lossy/many-to-one; recent pace is the
  integrated truth. REFRAME: evo "dominated by previous weekends" is CORRECT — recent
  pace is the best predictor; physics can't beat or augment it. Physics = EXPLANATION
  (aero character, validated) + DIAGNOSIS, NOT forecasting.
  One untested path (low odds, flagged not pursued): idealized-lap-time from fused
  season-filtered channels as the predictor.

## HEADLINE (overnight)
The human's "chase a prior through the season" idea WORKED, on BOTH channels, and
composed into the program's first clean per-car CAPABILITY FINGERPRINT (recipe:
relative-to-field + quali-only + season-filtered + multi-channel; recovers all 4
constructors' known 2023 aero character; front-of-grid grip tie broken via drag).
BUT the north-star PREDICTION test is a decisive NO: the fingerprint recovers
CHARACTER, does NOT forecast pace, and does not even add to a recent-pace baseline.
NET: physics is for understanding cars, recent pace is for predicting them — and
that reframes the evo predictor's recency-dominance as correct, not a defect.
