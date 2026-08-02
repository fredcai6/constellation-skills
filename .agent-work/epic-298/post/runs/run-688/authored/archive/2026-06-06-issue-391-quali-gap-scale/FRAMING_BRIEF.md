# Framing Brief — Issue #391 (quali mean gap scale, decoupled from σ)

Compiled by Commander before interrogation. Source of record: `docs/evo/prediction_ceiling_and_priorities.md` §2, §3 Thrust A, §4.1/§4.2, §7.6.2, §9.

## What the ask is
Give the quali **mean** head a meaningful **gap scale** (how far apart drivers are), kept **DISTINCT** from the σ/uncertainty target. Deliver a **trustworthy gap baseline** that #386's "excess flip risk" can later be measured against. Measure on quali resolution KPIs (rank_mae / sign-accuracy, edge over persistence) whether a gap scale improves midfield resolution. Honest null is reportable.

## What I learned from the code/docs (load-bearing facts)

1. **The quali "mean head" today emits only an ORDERING (`pi`), not a magnitude.**
   - `scripts/diagnose_quali_same_pairs.py` scores the trained model as `driver -> -pi` (lower=better) through `pairwise_accuracy_event`. There is no gap magnitude in the prediction — only order.
   - Channels: `race_weekend` (standalone, the weak link, 0.6149) vs `recent_history` (0.7803, near ceiling 0.806). Failure concentrated on EASY far-apart pairs (#406/#381 §7.6.2).
   - Ordering-accuracy fix routes to **#375**, NOT here. My lane = gap MAGNITUDE.

2. **The data-side gap scale source is the quali `s_e` (#387 / §9).**
   - `src/evo_predictor/spread_target.py` → `load_spread_target(year, round_num, phase="quali")` → `SpreadTargetRecord(s_e, clamped, disagreement_rate, n_pairs, entity_scope)`.
   - Frame: `expected_gap_ij ≈ s_e · (pi_i − pi_j)`; `pi` DIMENSIONLESS ordering power; `s_e` per-event exchange rate in fraction-of-median units.
   - Quali `s_e` ≈ 0.023–0.033, 114 quali records (2021–2025), cross-event CV ≈ 0.80 (genuinely event-conditioned). Low disagreement (~1–11%).
   - **`disagreement_rate` is NOT mine to consume.** No σ-floor/tail logic.

3. **pi semantics are FROZEN.** Gap expression must go THROUGH the exchange rate; power differences stay log-odds-like. (Admiral guardrail.)

4. **Training risk:** full gold-cycle retrain needs Admiral approval. Bounded fits/calibrations/inference on existing artifacts are fine. The committed gold bundle (`gold_cycle_260603_173742_2018thru2024`) has inference records from #381.

## The central design ambiguity to resolve in interrogation
The prediction is consumed as an ordering; the gap scale is a magnitude. So:
- **Q-MECH: What mechanism?** The issue/Admiral name three families: (a) auxiliary `s_e` prediction head (predict the event scale from as-of features), (b) post-hoc per-event scale calibration of the ordinal head's output, (c) conditioning. Admiral says "prefer the smallest mechanism that meets acceptance; this epic has repeatedly rewarded default-preserving flags." Which family — and is this a *learned predict-s_e-from-features* deliverable, or a *calibration/baseline characterization* deliverable?
- **Q-MEASURE: What does "improve midfield resolution" mean when KPIs (rank_mae, sign-acc) are ORDERING metrics that a monotone scale cannot change?** A per-event positive scalar `s_e·Δpi` is monotone in `Δpi` → sign-accuracy and rank order are INVARIANT. So either (i) the KPI is a gap/magnitude error metric (predicted-gap vs observed-gap MAE in fraction-of-median units), or (ii) the "resolution improvement" is expected to be ~zero on ordering KPIs and the real deliverable is the baseline contract. This must be pinned or the acceptance test is ill-posed.
- **Q-BASELINE: What exactly does #386 consume, and where?** A function/artifact giving per-event (or per-pair) expected gap? The contract shape and location need ratification.
- **Q-ASOF: Is the deliverable a LABEL-side baseline (uses post-event `s_e`, like the retro labels) or a PREDICTIVE head (as-of features → predicted `s_e`)?** §9 says `s_e` is a post-event label; a predictive gap scale needs an as-of feature→s_e map. This changes scope dramatically.
- **Q-SCOPE/RETRAIN: Can acceptance be met without a gold retrain?** If a learned predict-s_e head must be trained into the bundle, that may be retrain-shaped → STOP/approval.

## Decision protocol reminders
- Covered → proceed + log. Cheap/reversible → defensible default, logged. Irreversible / scope-changing / retrain-shaped / pi-semantics-shaped → END run, report under "Blocked on".
