# North-star prediction test — does the capability fingerprint forecast? (2026-06-15)

The program's north star: can physics-measured car capability PREDICT pace better
than the evo predictor's recency-dominated approach? Tested rigorously tonight on
2023 quali pace (gap-to-field-median per constructor per race). Code:
predict_drag_track.py, predict_grip_track.py, predict_combined.py; pace cached
quali_pace_2023.json; full-grid grip season_prior_nodes_full.npz (10 teams × 22 races).

## VERDICT: NO. Physics is for CHARACTER, not forecasting.
Three escalating tests, all negative:

### 1. Drag → quali pace (predict_drag_track.py): NULL
Interaction β wrong sign, in-sample R²=0.000, leave-one-race-out rank-corr −0.14
(worse than chance), corr(slipperiness, track-sensitivity)=+0.02. Physically right:
quali pace is grip/downforce-dominated; drag/top-speed is a small slice of one lap.

### 2. Downforce → quali pace (predict_grip_track.py): WEAK / WRONG
- CROSS-SECTIONAL corr(downforce_off, season pace) = −0.37 (right sign, weak) with
  gross failures: Haas measures HIGHEST downforce but is SLOWEST; Red Bull measures
  LOW downforce but is 2nd-fastest. The cornering-grip frontier ≠ lap pace.
- INTERACTION (df_off × track-DF-demand): right sign (β=−0.72) but corr −0.15 (noise).
- LEAVE-FUTURE-OUT predict-next-race rank-corr: capability fingerprint −0.15 vs
  last-race +0.55 vs season-avg +0.69. The fingerprint is ANTI-predictive; the dumbest
  pace baselines crush it.

### 3. Does physics ADD to a pace baseline? (predict_combined.py): NO — it DEGRADES
The fair test (physics needn't beat pace, just improve it on the track-specific part):
  season-avg pace baseline      +0.696
  + grip interaction            +0.649  (Δ −0.047)
  + grip + drag interaction     +0.633  (Δ −0.064)
  physics improved the forecast in only 12–18% of races.
Adding the fingerprint to recent pace makes prediction WORSE.

## Why (structural, not a bug to fix)
- The map physics-channels → lap time is many-to-one and lossy: two cars with equal
  measured downforce can have very different pace (power, mechanical grip, driver,
  balance, low-speed traction, tyre warm-up — none captured by a cornering-grip frontier).
- Actual recent pace is the INTEGRATED output that already contains all of it.
  Reconstructing pace from partial physics inputs is strictly worse than measuring it.
- The track-specific deviation physics MIGHT add sits at the noise floor (corr −0.15)
  and is swamped by the season-avg signal.

## Reframe for the program
The evo predictor being "dominated by previous weekends" is NOT a defect — recent
pace is genuinely the best available predictor, and physics-derived capability cannot
beat OR augment it. Physics' value is EXPLANATION (why a car is fast/slow — its aero
character, validated against known 2023 truth) and DIAGNOSIS, not FORECASTING.

## The one untested path (low expected payoff)
A full physics-predicted LAP TIME — fuse season-filtered downforce + drag + power on
each track's ribbon via the idealized-lap sim, and use THAT as the predictor (it
integrates channels the way pace does). Given single channels + the fingerprint failed
and the cross_circuit ideals were already below the ranking noise floor, expected payoff
is low, but it's the only physics-native pace predictor not yet wired to the leave-
future-out harness. Flagged for an explicit decision, not auto-pursued.

## Bottom line
Tonight established that per-car aero CHARACTER is cleanly measurable (the fingerprint)
— and, just as clearly, that it does NOT forecast pace. Use physics to understand cars;
use recent pace to predict them.
