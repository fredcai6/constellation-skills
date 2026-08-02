# F12 Pre-Registration Proposal — #668 Instrument Panel REPLICATION_* set
**Status: PROPOSED — awaiting owner signature via the Admiral. NOT yet minted.**
Freeze target: append to `src/physics/layer2/frozen_constants.py` (per #660's
`decision:replication-deferred`). Evidence-only pre-registration: grounded in the real 2023
driver×class SUPPORT distribution + a synthetic noise model. **No replication / coverage /
scorecard OUTCOME was computed to produce these values** (F12 firewall).

## What the real on-disk slice actually is (reconciliation finding — differs from the launch order)
The launch order states "only Great Britain 2023-Q is on disk (Monaco/Spain/Belgium
reference_laps+observables were never built/swept)." **The actual archived #666 slice
(`.agent-work/archive/2026-07-26-666-driver-fingerprint/artifacts/fp_slice_2023Q.db`) is
richer:** it holds `driver_class_observables` AND `reference_laps` for **4 circuits** —
Belgium (R12), Great Britain (R10), Monaco (R6), Spain (R7), all Q — for **4 drivers**
LEC, PER, SAI, VER (the two Ferraris + two Red Bulls). The #664 reference own-DB
(`reference_utilization_run.db`) has GB only, but the #666 slice carries all four.
**This enables a statistically-correct CROSS-CIRCUIT split-half** — the repeated-measurement
unit the golf-corrected replication actually needs — which a single GB-Q session could not
provide. See the "Split-half unit" section and the floated scope question below.

## Support distribution (SUPPORT/STRUCTURE only — the grounding)
Per-observation (driver × class × circuit) `n_points`, by severity class:
| class | min | median | max | note |
|---|---|---|---|---|
| severity:2023:v1:c0 | 263 | 280 | 538 | well-supported, all 16 obs |
| severity:2023:v1:c1 | 0.0 | 0.2 | 4.7 | **essentially empty — unresolvable** |
| severity:2023:v1:c2 | 112 | 168 | 316 | well-supported |
| severity:2023:v1:c3 | 4.5 | 24.7 | 36.5 | moderate |
There is a clean support gap between c1 (~0–5) and {c3,c0,c2} (~25–538). At a per-observation
floor of 15 n_points, 8/16 cells (c0,c2 × 4 drivers) resolve on all 4 circuits and 12/16 on
≥2 circuits; c1 drops out entirely. **Expect a SMALL signal size** (≈2–3 resolvable classes ×
4 drivers) — an honest no-frame-kill "small/zero size is a complete result" regime.

## Proposed REPLICATION_* frozen set (recommended values — owner may adjust)
All added to `src/physics/layer2/frozen_constants.py` as a NEW named block; consume #660
(scorecard triple already frozen) + #666 (`FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` etc.); no
inline literals elsewhere.

1. **`REPLICATION_MIN_SUPPORT_N = 15.0`** — per-observation `n_points` floor. An observation
   (driver, class, circuit) below this is excluded before splitting. Grounded: sits in the
   observed gap between the empty class (c1, ~0–5) and the real classes (c3 ~25, c0/c2 ≥112);
   matches #665's `MIN_RESOLVED_CELL_N = 15`.
2. **`REPLICATION_THRESHOLD = 0.5`** — the base split-half agreement floor. A (class, channel)
   "replicates" iff the split-half Pearson r of its DOUBLE-CENTERED per-driver interaction
   profile is ≥ this (subject to the support scaling below). 0.5 = moderate reproducibility;
   below it the per-class utilization signal is not distinguishable from noise at this support.
3. **support-count-scaling `r_floor(n)`** — thin support demands a HIGHER agreement bar
   (bounded, since a correlation ≤ 1):
   `r_floor(n) = REPLICATION_THRESHOLD + (R_FLOOR_CAP − REPLICATION_THRESHOLD) *
   clip((R_FLOOR_SUPPORT_REF − n) / R_FLOOR_SUPPORT_REF, 0, 1)`
   with **`R_FLOOR_CAP = 0.7`** and **`R_FLOOR_SUPPORT_REF = 100.0`** (`n` = the class's total
   resolved `n_points` in the tested half). ⇒ well-supported classes (c0 ~280, c2 ~168 ≥ ref)
   use the base 0.5; a thin class (c3 ~25) needs ≈0.55–0.6; the floor never exceeds 0.7.
4. **channel-comparison registration** — run the replication per class in BOTH channels
   (`utilization` = `time_deficit_s`, `energy` = `deployment_share`). Decision rule, frozen
   BEFORE any outcome: for each class, the channel with the higher split-half r **earns the
   join weight there** iff (a) its r ≥ `r_floor(n)` AND (b) it beats the other channel by
   **`CHANNEL_TIE_MARGIN = 0.1`** (Δr). If neither channel clears `r_floor(n)`, the class is
   "unresolved — no channel earns weight" (no-frame-kill). If both clear but within the tie
   margin, default to **`utilization` (time-deficit, the driver-aligned channel)** — the
   conservative registered tie-break.

## Split-half unit (registered)
- **PRIMARY — cross-circuit 2-vs-2:** split the 4 available circuits {Belgium, GB, Monaco,
  Spain} into two 2-circuit halves; compute the double-centered per-class interaction profile
  on each half; correlate across the 4 drivers. Average the split-half r over all 3 distinct
  2v2 partitions for stability. This is the statistically-correct repeated-measurement unit and
  is available on the actual slice. **Requires the floated scope ruling below.**
- **FALLBACK (if owner restricts to GB-Q only):** within-session lap-parity split (odd/even
  timed laps), needing per-lap telemetry re-derivation — heavier, weaker (shares one session's
  conditions), and its data availability on the slice is UNVERIFIED. Reported as a documented
  limitation with breadth routed to #670.
- **no-valid-split branch (no-frame-kill):** a class with < 2 resolved circuits per half (or,
  in fallback, insufficient laps) reports "unmeasurable — zero signal size is a COMPLETE
  result," never a fabricated number.

## Golf-correction method (registered — the load-bearing correctness point)
**DOUBLE-CENTERING**: within each split-half, subtract BOTH the driver main effect AND the
class main effect from each (driver, class) observation; the residual that must replicate is
the genuine **driver×class interaction**. Per-driver demean ALONE is insufficient — it leaves
the SHARED class main effect, which replicates trivially for every driver (a healthy-looking
replication with zero driver-utilization content; the exact artifact the owner ruling warns
of, caught by the cold plan critic). Double-centering is a DATA TRANSFORM (arithmetic
residual), **not** a fitted interaction term, so owner ruling 4 (no interaction terms / no
bespoke model) is respected.

## Noise model (for the synthetic falsifier that validates the threshold's discrimination)
Extend #665's generative model (`scripts/pooling_imbalance_validation_665.py`:
`draw_ground_truth` driver_sigma=0.15, class_sigma=0.30, obs_sigma=1.0) with a **true
driver×class interaction term** of tunable strength. The **3-arm** falsifier: (a) pure
overall-skill → corrected agreement ~0; (b) **pure shared-class, zero interaction → corrected
agreement ~0** (the arm that distinguishes a correct double-centering from a broken one);
(c) injected interaction → recovers ≈ its strength. `REPLICATION_THRESHOLD` = 0.5 must sit
below the recovered-interaction arm and above the two null arms in this synthetic regime.

## FLOATED SCOPE QUESTION for the owner (beyond my latitude — Admiral please route)
The launch order bounds validation to "GB 2023-Q only." But the actual slice carries 4
circuits × 4 drivers, and the golf-corrected replication is only statistically valid with a
cross-circuit split-half. **Recommendation:** validate the **replication instrument
cross-circuit** (all 4 circuits' observables for LEC/PER/SAI/VER) — that is what the
instrument needs to mean anything — while the variance decomposition and sector scorecard stay
anchored on GB (or extend to the 4 circuits' reference_laps, also on disk). If the owner holds
strictly to GB-Q, the replication falls back to the weaker within-session lap split and reports
a documented limitation, routing cross-circuit breadth to #670. Either way the multi-circuit
FULL season stays out of scope (#670, HITL).
