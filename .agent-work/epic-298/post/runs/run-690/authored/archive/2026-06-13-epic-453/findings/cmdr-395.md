# cmdr-395 Findings: Race-Start Recent-History Form Encoding Investigation

**Issue:** #395  
**Epic:** #453 Wave 2  
**Commander:** cmdr-395  
**Date:** 2026-06-11  
**Recommendation:** DROP with reasons (primary); one CONDITIONAL-DEFER candidate

---

## Problem Statement (confirmed)

The race-start recent-history module (`driver_race_start_power_from_recent_history`, `constructor_race_start_power_from_recent_history`) tracks **grid→target-lap GAIN** — position improvement from qualifying grid to lap 3 position. This is structurally different from quali pace-gap history (#369), which is a continuous pace measure. The question is whether any variance-enriching re-encoding of this gain history is meaningful, feasible from DB data, and worth speccing.

This investigation is orthogonal to the race_weekend quali-channel gap (#451 verdict — that gap is feature-representational in the `qs_*` channel, not related to gain encoding).

---

## Current Feature Set (baseline)

From `src/evo_predictor/race_start_recent_history_adapter.py`, the `_HISTORY_FEATURE_NAMES` vector already contains:

| Feature | What it is |
|---|---|
| `mean_grid_to_target_lap_gain` | Mean of (start_pos - target_lap_pos) over history |
| `median_grid_to_target_lap_gain` | Median of gain over history |
| **`std_grid_to_target_lap_gain`** | **Std of gain over history — variance already present** |
| `availability_fraction` | Fraction of history events where driver appeared |
| `mean_target_lap_gap` | Mean of (target_lap_pos - start_pos) — opposite sign |
| `median_target_lap_gap` | Median of the same |
| `support_count` | Count of events in history |

**Critical observation:** `std_grid_to_target_lap_gain` is already in the feature vector. This already captures within-driver variability of the gain signal. Any "variance-enriching" enrichment must add something beyond this.

---

## DB Data Availability Probes

Probed per-year DBs (`f1_data_2022.db` through `f1_data_2025.db`). Key findings:

| Data source | Availability | Notes |
|---|---|---|
| `race_start_order` (year, round_num, driver_id, running_position_at_target_lap) | Full: 2022-2025, all race events | Primary source for current gain computation |
| `session_classifications` (quali Q positions as grid) | Full: 2022-2025, all race events | Grid start source |
| `lap_times` for race sessions (laps 1-3) | ~90-97% driver coverage per event | Lap 1 is race formation+start lap (ratio to lap 2: 1.03-1.89x), lap 3 is target lap |
| `telemetry` for race sessions | **0 rows across all years** | No race telemetry collected |
| `processed_telemetry` for race sessions | **0 rows across all years** | No processed race telemetry |

---

## Candidate Enrichments: Assessment

### Candidate 1: Field-churn-normalized gain (`gain / field_std_at_event`)

**What it is:** Normalize each event's gain by the field-wide standard deviation of gains at that event. Intended to make a "+3 position gain" at a chaotic race (field_std=5.0) comparable to a "+1 position gain" at a processional race (field_std=1.0).

**DB availability:** Yes — computable from `race_start_order` + `session_classifications Q`.

**Physics-limited?** No.

**Measured field_std distribution (2024, 24 events):**
- Min=0.81, Max=5.34, Mean=2.32
- 13 of 24 events have field_std < 2.0 (low-churn)
- 1 of 24 events has field_std > 4.0

**Why this is problematic:**
1. `std_grid_to_target_lap_gain` ALREADY captures the within-driver variance of gain. The field_std is a DIFFERENT quantity (cross-driver variance at one event), but it's largely driven by Safety Car, DNFs, and other non-driver-quality factors.
2. Correlation test (VER 2023): gain vs field_std correlation = **-0.12** — near zero. The driver's individual gain is nearly uncorrelated with field chaos. This means field_std_normalization adds mostly noise: it inflates gains in chaotic events where the chaos was not driver-attributable.
3. The signal being normalized is ordinal (position), not continuous pace. A gain of +3 in a chaotic race tells us almost nothing different about the driver's start ability vs +1 in a clean race — SC/DNF reshuffles are random.
4. The current feature already encodes the start_grid_delta (absolute and threshold-sliced) which partially accounts for whether there was opportunity to gain.

**Verdict: DROP.** Field_std normalization would add noise attributable to SC/DNF variance, not driver start quality. The within-driver std already in the vector is the correct variance signal. Would require new as-of policy (field_std per event in historical context), missingness definition (events with SC early → field_std inflated), and adds complexity with no expected precision gain.

---

### Candidate 2: Target-lap pace gap (`(driver_lap3_time - field_median_lap3_time) / field_median_lap3_time`)

**What it is:** Instead of (or in addition to) position gain, encode the driver's lap-time pace quality at the target lap — analogous to how #369 encoded quali pace gaps.

**DB availability:** `lap_times` is available with ~90-97% coverage. Lap 3 times are present for most drivers.

**Physics-limited?** No.

**Why the premise is questionable:**
1. The module is called `race_start_power_from_recent_history` — it predicts **lap 3 position ordering**, not pace. Position is the label; pace at lap 3 is partially colinear with position (slower drivers are typically further back by lap 3) but with meaningfully different missingness and noise.
2. Lap 3 race pace is heavily influenced by car pace / compound / degradation — it is NOT primarily a start-skill signal. A driver who starts P18 and gains 5 places by lap 3 through a good start may be driving a fast car on fresh rubber, not demonstrating exceptional start skill.
3. The module label is `running_position_at_target_lap` (from `race_start_order`). Adding a pace-gap feature creates a partially-redundant signal that mixes start execution quality with car pace — likely to add confounding rather than variance.
4. The `race_start_adapter.py` (race-weekend module, not recent-history) already encodes `BASE_RACE_POWER_FEATURE_NAMES` which include FP/quali pace features. Adding pace at lap 3 into the recent-history module duplicates that channel.

**Verdict: DROP.** Target-lap pace gap is a car-pace + compound signal, not a start-skill signal. It would confound the module's intent (start execution quality), duplicate the pace channel already present in `race_start_power_from_race_weekend`, and requires a new DB read path with as-of contracts and ~3-10% missingness policy. No expected discrimination gain on start ordering.

---

### Candidate 3: Variance-of-gain windows (rolling window std of gain over last N events)

**What it is:** Rather than std over all available history, compute std over a shorter recent window (e.g. last 4 events). Intended to capture whether a driver has been consistently executing starts recently vs having high recent variability.

**DB availability:** Yes — computable from `race_start_order` + `session_classifications Q`.

**Physics-limited?** No.

**Why this is weak:**
1. `std_grid_to_target_lap_gain` already computes std over `prior_events[-max_history_events:]` — a bounded window. The window is already 8 events max.
2. A shorter window (e.g. 4) would have very low statistical power: 4 events gives an extremely noisy std estimate. The meaningful signal (driver consistently gains vs consistently loses) is already captured by mean + std over 8 events.
3. There is no strong prior that "recent window variability" discriminates start quality differently from the full-window std. This would be an engineering bet without theoretical grounding.
4. Driver fields change year-to-year (rookies, substitutes) reducing even 4-event windows to 2-3 data points in many cases.

**Verdict: DROP.** The existing std over the bounded window already captures the relevant variance. A shorter window would be noisier without adding information. As-of contract would be identical to current design. The marginal information content is expected to be near zero.

---

### Candidate 4: Launch-delta (telemetry-derived reaction time / 0-100m delta)

**What it is:** Per-driver reaction time at lights out (measured as time to cross a threshold speed or distance from launch position), providing a direct measurement of start execution quality.

**DB availability:** **ABSENT.** Race telemetry rows = 0 for all years (2022-2025) in per-year DBs. Zero rows in both `telemetry` and `processed_telemetry` tables for race sessions.

**Physics-limited?** Yes — even if telemetry were available, extracting launch-delta requires physics preprocessing (trajectory + speed reconstruction at sub-second resolution). This is Phase 3 of epic #445.

**Verdict: DROP (physics-limited, data absent).** Flag under #443/#445 Phase 3. Data would need to be collected AND the physics pipeline (preprocessing/trajectory_grading) extended to the race start phase before this is feasible. Cannot build a pursue-spec on it.

---

### Candidate 5: Grid-position-binned gain (gain stratified by starting tier)

**What it is:** Rather than a single mean gain, encode separate mean gains for races where the driver started in the front (P1-5), midfield (P6-15), and rear (P16+). Intended to capture that starting from the back allows different gain magnitudes.

**DB availability:** Yes — computable from `race_start_order` + `session_classifications Q`. However, thin data: a driver starting from P1-5 consistently (e.g. VER) would have very few rear-start history events.

**Physics-limited?** No.

**Why this is weak:**
1. The current feature already includes `race_start_grid_features` which encodes `grid_delta_signed_norm`, `grid_ahead_ge_{threshold}`, `grid_behind_ge_{threshold}` — these already stratify by grid position at the PAIR level.
2. The recent-history adapter uses per-event vectors that already encode the actual gain from whatever start position occurred. The gain IS stratified implicitly by the start positions in those events.
3. For drivers like VER who start P1-2 consistently, there is near-zero variance in starting tier, making the stratification uninformative.
4. Sparse bins for many drivers (most drivers rarely start P1-5 over 8 events).

**Verdict: DROP.** Grid-position stratification is already partially encoded in the grid-delta features. Stratified history would be very sparse, adding noise for most drivers. No expected improvement over current design.

---

## Summary Candidate Table

| Enrichment | Data Availability | Physics-Limited? | Verdict |
|---|---|---|---|
| Field-churn-normalized gain (gain / field_std_at_event) | Yes (race_start_order + session_classifications Q) | No | DROP: noise from SC/DNF dominates field_std; within-driver std already present |
| Target-lap pace gap (lap3 time vs median) | Yes, ~90-97% coverage (lap_times) | No | DROP: car-pace signal not start-skill; confounds module intent; duplicates race-weekend channel |
| Rolling window variance of gain (shorter window) | Yes (same as current sources) | No | DROP: existing std over 8-event window already captures this; shorter window would be noisier |
| Launch-delta (telemetry reaction time) | ABSENT (0 race telemetry rows) | YES — physics epic #445 Phase 3 | DROP/PARK: data not collected; requires physics pipeline; route to #443/#445 |
| Grid-position-binned gain history | Yes (same as current sources) | No | DROP: already partially encoded in grid-delta features; sparse bins for most drivers |

---

## Recommendation: DROP

**All five candidate enrichments are recommended for drop**, with the following primary reasons:

1. **The key variance signal already exists.** `std_grid_to_target_lap_gain` is already in the feature vector at position 3 of `_HISTORY_FEATURE_NAMES`. The issue premise ("variance-enriching re-encoding") may have been based on a gap that does not exist in the current implementation.

2. **The domain difference from quali pace-gap is fundamental.** Quali pace-gap (#369) encodes a continuous, well-defined quantity (lap time relative to field) where the analogy to position-quality re-encoding was clear. Grid-to-target-lap GAIN is a positional delta over a ~3-lap window in a chaotic environment (SC, DNF, first-lap incidents). There is no pace quantity to substitute here — the signal IS positional ordinal gain, and the current encoding (mean + median + std + availability + h2h edge) adequately represents it.

3. **Telemetry-derived candidates have no data.** Launch-delta — the most physically motivated enrichment — requires race telemetry, which is completely absent from the DB (0 rows). It is correctly parked under #443/#445 Phase 3.

4. **Field normalization adds noise.** The field-level gain std is dominated by non-driver factors (SC, DNF, retirements). Normalizing by it would amplify noise attributable to random race incidents, not driver start skill.

**If any candidate were to be re-examined,** it would be the target-lap pace gap — lap 3 time relative to field median is DB-available and could theoretically add information about the quality of the position achieved. However, it would require careful isolation from car-pace contamination (which is not achievable without controlling for team/compound), a defined missingness policy for laps with SC or DNF, and an explicit A/B measurement against the current baseline. The burden of proof is on showing this discriminates start skill beyond what position-gain already captures. Current evidence does not support that.

**No pursue-with-spec recommendation is issued.**

---

## Triage Candidates

- **Launch-delta:** Already pre-routed to #443/#445 Phase 3 per LO-395 pre-rulings. No new issue needed.

---

## Out of Scope

- Qualifying (v2 encoding, #369) — not touched
- Race (main race outcome) encodings — not touched
- Any src/ changes — this is investigation only

---

## Evidence Artifacts

- DB probes: per-year DBs `f1_data_2022.db` through `f1_data_2025.db` read via `sqlite3` URI `?mode=ro`
- Source files read: `src/evo_predictor/race_start_recent_history_adapter.py`, `src/evo_predictor/race_start_adapter.py`, `src/evo_predictor/quali_pace_gap_history.py`
- Architecture: `docs/architecture/index.md` (evo reconciliation entries for #369, #451)
