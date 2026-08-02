# Tire-age epic — Research plan: 25 ideas to try ("see what sticks")

The first build is a **baseline, not the answer.** This epic established a solid, expandable base
(mass model → race-session fit path → tyre-age separation + supplant + the neutral pairwise-P harness)
and an honest verdict: **physics gives a clean, monotone-up, separable grip-DECAY axis, but
grip-decay-rate ≠ run-window pace-degradation** (window-selected ~flat), so it's CONTEXTUAL — usable as
a *feature*, not a pace-degradation supplant. These 25 ideas are the iteration roadmap. Each is meant to
be cheap-ish to try against the now-standing measurement backbone (the `race_stint_estimates` store +
`src/common/pairwise_ordering` P-harness + the `tyre_age_dashboard`).

Tags: [TRUTH] degradation-truth channel · [SIGNAL] new/better physics signal · [POOL] pooling/priors ·
[FUEL] mass/fuel model · [DATA] coverage/inputs · [COMPOSE] toward Phase-P #450 use.

## A. Fix the yardstick — the degradation TRUTH channel (highest leverage)
The capstone bottleneck was the truth, not the predictor. Better truths may flip CONTEXTUAL→GO.
1. **[TRUTH] Full-stint-to-cliff truth.** The current truth is window-selected (~flat because softs are pitted pre-cliff). Build a truth that captures degradation *to the cliff* — model the stint to its natural end / include the cliff lap — so the per-compound degradation isn't censored by strategy.
2. **[TRUTH] Stint-survival / window-selection model.** Jointly model *when* a stint ends (pit decision) with the degradation slope (a selection/Heckman-style correction) so the truth isn't biased by strategic pitting.
3. **[TRUTH] Telemetry-anchored truth (not lap-time).** Use the #443 DRS-clean corner/straight contrast as the truth's grip channel instead of lap-time — removes the fuel confound structurally and makes physics-vs-truth same-modality. (Watch circularity: keep the physics predictor's features distinct.)
4. **[TRUTH] Cross-driver same-lap contrasts.** Within a lap, compare drivers on different tyre ages (de-confounds fuel/track entirely — everyone shares the same lap conditions). The cleanest non-parametric degradation truth.
5. **[TRUTH] Sector-time truth.** Use corner-sector degradation (S2/S3) rather than whole-lap — the #443 survey found corners carry the grip signal while the power sector is fuel-dominated.

## B. Sharper / new physics signal
6. **[SIGNAL] Longitudinal (traction) decay channel.** TelemetryStore currently lacks acceleration channels, so the longitudinal sensor is absent (#443 honest-null). Ingest/derive accel → add the traction-decay axis (the Piece-3 vector's second leg; →#557).
7. **[SIGNAL] Per-corner-type grip decay.** Split lateral into slow-mechanical vs fast-aero corners (the #443 finding: slow > fast for degradation); fit decay per corner class.
8. **[SIGNAL] Tyre-age² curvature / cliff detection.** Current model is `exp(-k·age)` (smooth); add a curvature/cliff term per compound to catch the non-linear drop the window-selection truth hides.
9. **[SIGNAL] Thermal state.** Fold track-temp / tyre-warmup (age≥3 warm-in) into the decay model — degradation rate is temperature-dependent.
10. **[SIGNAL] v²/r grip coefficient.** Compute a direct grip coefficient from speed+curvature per corner (the physical μ) rather than the frontier g0 — a cleaner grip primitive.
11. **[SIGNAL] Racing-line / commitment drift.** Use throttle/brake-commitment telemetry as a degradation proxy (drivers manage a worn tyre differently).

## C. Pooling, priors, identification
12. **[POOL] Compound as the strong season-pooled axis, multi-season.** Pool the per-compound k across 2022–2025 (huge N on the same compound) for a tight informative prior; the single-season fit is thin for the rarer compounds.
13. **[POOL] Hierarchical circuit shrinkage.** Partial-pool the per-circuit `g_track` and per-circuit degradation deviations toward a global with proper random-effects (the regularizer's structure) rather than per-race independent slopes.
14. **[POOL] Injectable structural prior tuning.** The structural monotone+non-neg prior currently ships as a no-op default; sweep prior strength and measure where it helps vs over-shrinks (per-compound).
15. **[POOL] Joint multi-stint fit (the "B" fallback).** If per-stint covariance is thin for slow-deg HARD/long stints, fit decay jointly across stints with a shared pooled k (the joint-hierarchical option we held in reserve).
16. **[POOL] Driver tyre-management random effect.** Some drivers nurse tyres; add a per-driver management effect so it doesn't leak into the compound k.

## D. Mass / fuel model refinements (the W1 follow-ons)
17. **[FUEL] Full fuel-mass pace-validation (filed follow-on).** Prove the fuel correction actually flattens start-vs-end stint pace on real stints (W1 shipped formula+bounds+sanity only).
18. **[FUEL] Estimate per-team mass offset (filed follow-on).** Replace the default-0 `team_offset` hook with a data-estimated overweight term (teams run over the limit, esp. early season) — weakly identified, so treat carefully.
19. **[FUEL] Non-linear / measured fuel burn.** Replace linear burn with a circuit-specific burn profile (lift-and-coast, fuel-save phases) and SC delta beyond the ~half-rate approximation.
20. **[FUEL] Unify k_tire across paths (#525 routing).** Resolve the `k_tire` 0.0 (car_prior) vs 0.01 (live sim) inconsistency as a grip-evolution decision — the quali ceiling's 0.0 is the fresh-tyre special case of the race-state model.

## E. Data / coverage
21. **[DATA] Multi-season population.** Extend `race_stint_estimates` to 2022/2024/2025 (the store + path are already season-agnostic) — more stints, the era-wide picture.
22. **[DATA] FP-session fits (→#513).** Populate the session-agnostic store from FP1/FP2/FP3 (the interface is already built) — feeds the weekend-local pre-quali prediction path.
23. **[DATA] Wet/intermediate degradation.** 55 INTER + 3 WET stints exist; characterize wet-tyre degradation separately (different physics).

## F. Composition — toward Phase-P #450 (the actual payoff)
24. **[COMPOSE] Grip-decay as a race-sim pace-curve feature.** The #443 POC + this verdict both point here: feed `f_tyre(compound,age)` into a per-car stint-pace-evolution race simulation (modeling the window-selection), and A/B the race-prediction lift — the integration level where degradation can actually matter, vs the failed cross-driver finish-ranking bolt-on.
25. **[COMPOSE] Live-γ + #443 triangulation in the supplant.** Wire the live `compound_prior` γ model + the #443 telemetry sensor as comparators against a *better* truth (idea 1/3) — the three-way agreement (physics telemetry / lap-time γ / #443 contrast) is the real cross-modal validation that can promote CONTEXTUAL→GO.

---
**Top 3 to try first** (highest expected value): **#1** (full-stint-to-cliff truth — directly attacks the
verdict bottleneck), **#24** (grip-decay as a race-sim feature — the actual prediction payoff #443's POC
demanded), **#6/#21** (longitudinal channel + multi-season — cheapest signal/coverage gains on the
standing backbone).
