# Wave-4 Verdict — #626 Phase 2: four-layer weekend-state model

**Commander:** ShipE-626 (delegated, constellation-commander-delegated). **Epic:** #601. **Date:** 2026-07-18.
**Branch:** `feat/626-weekend-state-model` (worktree `C:/Programs/f1-626`). **Base:** main `08e14014`.

---

## 1. VERDICT: PASS

The four-layer weekend-state model **beats x4's weekend-relative floor on 9/11 axes** (threshold ≥7/11)
on a **held-out weekend split**, by a margin outside the frozen car-season bootstrap noise, with the
signal-preservation guard gating every beat. Median convergence-speed ratio **0.40 (~2.5× faster to
resolve a slow-moving component than the raw floor)**. The methodology was frozen (g1) before any layer
or held-out number was seen; the verdict was not tuned post-hoc; the g5 reviewer independently reran the
gate against the live store and reproduced the committed result exactly.

**Load-bearing honesty caveat (surfaced, not buried):** the PASS holds on the accuracy-preserved subset —
only **~30% (268/888) of car-season-axis instances preserve held-out accuracy** through the signal-
preservation guard. `max_power_w` (guard-pass 3/80) and `coast_drag_area_m2` (0/81) are honest per-axis
nulls. The 9/11 count is over axes with adequate coverage (≥5 held-out car-seasons, tc1 floor) whose
accuracy-preserved instances beat the paired floor.

---

## 2. The four layers (each with honest σ)

1. **Explained physics** (`layer1_physics.py`) — removes a density(measured `rho`)+mass component from
   the 7 ρ-sensitive axes (3 CdA + max_power + 3 aero-slope companions, grouping grounded in
   `estimate_store.py` SYSTEMATIC_FLOOR); 4 mass-normalized accel axes are code-enforced no-ops
   (explained==0). Density from MEASURED per-session pressure — the store `rho` validated **bit-identical**
   to `environment.moist_air_density_from_pressure` on `telemetry_store.tele_weather` measured pressure (NOT
   fixed RHO=1.2, NOT the buggy altitude lookup). σ = axis `_sigma` + model uncertainty, inflated where
   `rho_is_fallback`. **Ablation −L1 Δ0 convergence — honestly small** (the axes were already ρ-fit; this
   layer's job is de-confounding the density common-mode, which it does for the density secondary check).
2. **Within-session evolution** (`layer2_evolution.py`) — a smooth field-level grip latent (penalised
   spline over `cumulative_track_laps`, controlling corner-bin FE + tyre_life) fit from **actual Q-session**
   `grip_bin_obs` grip, with honest per-weekend σ + a wide-σ near-zero fallback outside coverage. The
   signal is **REAL and identifiable** (slope +0.00196 g/lap, t=28.4, positive in all 9 weekends; LOO
   held-out grip RMSE −2.56%; orthogonality vs season-time r²≈0 — genuinely within-session, NOT the F5
   season-time double-count trap). **But it FLOATS as a per-car Layer-2 correction on the frozen split**
   (see §5). Kept in the pipeline as a documented inert wide-σ seam; **ablation −L2 Δ0 exactly** confirms it.
3. **Field-car common-mode** (`layer3_fieldcar.py`) — cake-and-eat-it two-stage: **(a) relative** = car −
   that weekend's field median (fast-resolving), σ folding the field-median SE; **(b) re-anchor** = a smooth
   per-year field-car ABSOLUTE trajectory via `pooling.fit_drift`/`DriftFit.predict` over `round_idx`, so
   `absolute = fieldcar_traj + relative` and absolute development still accrues. Both stages carry σ.
   Reuses `src/physics/layer2/pooling.py` (imported, not reinvented). **Ablation −L3 → 2 beats** — L3's
   median differencing is what keeps the L4 shrink accuracy-preserving; without it the guard correctly
   rejects the over-shrinker on 9/11 axes (F1 working as designed).
4. **Car signal** (`layer4_car.py`) — the empirical-Bayes shrunk per-weekend relative deltas off the field
   car (`pool_random_effects`, τ = "how much this car really moves week to week"), with σ. **This is the
   engine: ablation −L4 → 0 beats.** It is the quantity the F6 gate measures.

`model.py` (`WeekendStateModel`) composes L1→L2→L3→L4 with an explicit `fit(train)`→`car_signal(held-out)`
split; each layer carries its own σ column (`layer_sigma_cols()`). **No leakage** — held-out car-signal
driven only by train-fit hyperparameters; verified on the live store across all 11 axes × every held-out
round (**5464 comparisons, 0 mismatches**).

---

## 3. The F6 gate (held-out, frozen, un-gameable)

- **Split:** frozen deterministic held-out = weekends with `round_idx % 3 == 0` (`holdout.py`), leaving ≥2
  held-out weekends for all 81 trusted car-seasons. Frozen in g1 **before** any layer was fit.
- **Metric:** x4's OWN metric (`floor.py` reproduces the 624 baseline table within ~1.5% — proven, not a
  new metric). `noise_sd`=within-car-season SD around season mean; `field_sigma`=median cross-constructor
  SD; `N_weekends=(noise_sd/field_sigma)²`; convergence-speed ratio vs the floor.
- **Paired comparison (cold-critic F2):** the raw x4 floor is recomputed on the IDENTICAL held-out weekends,
  paired per car-season — NOT the 624 full-sample table.
- **Signal-preservation guard (cold-critic F1):** the held-out car-signal is scored by its OUT-OF-SAMPLE
  residual around the train-fit trajectory, so an over-shrinker (constant per car-season) cannot win — a
  PASS requires faster convergence AND preserved held-out accuracy. Directly demonstrated: forcing the
  over-shrinker (−L3) drops beats from 9 to 2.
- **Decision rule (cold-critic F3, frozen):** PASS iff ≥7/11 covered axes beat the paired held-out floor
  by a margin outside a **car-season-resampled bootstrap** (fixed seed, N=2000), tie = not-a-beat; the
  median ratio is the reported summary. Plus an MDE/power sanity helper.
- **Per-axis coverage floor (tc1, folded from g1 review):** an axis-beat requires ≥5 held-out car-seasons
  (`MIN_COVERED_CAR_SEASONS=5`), so thin-coverage axes cannot pad the tally (strictly tightening).
- **Result:** 9/11 covered axes beat; median convergence ratio 0.40.
- **Per-layer ablation (cold-critic F4):** full 9 / −L1 9 / −L2 9 / −L3 2 / −L4 0 beats — each layer's
  marginal contribution is reported; no dead layer is credited (L2's ~0 is the confirmed FLOAT).
- Machine-readable: `docs/physics/626-f6-holdout-gate.json`; narrative: `docs/physics/626-phase2-weekend-state-model.md`.

---

## 4. Density secondary check (Mexico vs Monaco)

Falsifiable residual-consistency test (cold-critic F6), NOT confirmatory-by-construction: after density
handling, the SAME constructor's drag/power residual at **Mexico (ρ≈0.90)** vs **Monaco (ρ≈1.19)** must
agree within σ. The density layer **halves the normalized gap** (drag CdA mean |z| 2.51→1.63; max power
1.66→0.85; 90–95% of car-seasons improved; 6/7 density-sensitive axes tighten). The residual does not
close to <1σ on every car-season — honestly attributed to the acknowledged aero-trim/track setup confound
(Mexico ≠ Monaco in more than density), not blamed on density. Falsifiability proven directly: forcing the
density beta to zero makes the check fail. The density layer EXPLAINS the known cross-track difference
physically rather than needing an ad-hoc per-track correction.

---

## 5. FLOATED to the Admiral — ADJUDICATED

**Layer 2 per-car session-time bridge (tc3 — ARCHITECTURE FLOAT).** The within-session grip-evolution
signal is real and identifiable, but it cannot act as a **per-car** Layer-2 correction on the frozen split
because `physics_estimates.db:session_estimates` carries **no per-car representative-lap
`cumulative_track_laps`** — the field-level track-state latent is absorbed by the weekend-median
subtraction. Secondary: `grip_bin_obs` Q coverage is 2023-only (backfill 2022/2024+); a grip-g →
11-axis-unit map is unmeasured. Full detail:
`C:/Programs/f1-626/.agent-work/wave4-626/TRIAGE_RECOMMENDATIONS.md` (tc3).

**ADMIRAL RULING (delegated, logged; received 2026-07-18):** **ACCEPT the field-level within-session
evolution for Phase 2.** The Admiral verified directly that this is NOT a collection gap — per-car
session-time IS present in the raw stores (`telemetry_store.db → tele_laps.lap_start_time_s/lap_end_time_s/
stint`; `f1_data → telemetry.session_time_ms`); the limit is only that the `session_estimates` store the
g1 frame reads is aggregated to one row per car per session, averaging the within-session time dimension
away. The **per-car** version is therefore **deferred to Phase 4 (#513), NOT dropped** — the Admiral
annotated **#513** to make "per-car within-session grip evolution from the per-lap fits" an explicit Phase-4
deliverable, closing the loop back to this Layer-2 limit. Directed scope: record the **field-level-only**
within-session evolution honestly (done — Layer 2 is the field-level latent, kept as an inert wide-σ seam
on this split, ablation −L2 Δ0); do NOT extend the g1 frame to per-lap grain in this wave (that is Phase-4
scope). This verdict's PASS stands on the four-layer model with Layer 2 at field-level grain.

Nothing else floated — the one genuine gap was pre-dispositioned by Pre-Ruling 2 (build+test+report) and
has now been adjudicated by the Admiral (field-level accepted for Phase 2, per-car → Phase 4 #513).

---

## 6. Deviations from the launch order (with reason)

- **Observability router not a runtime dependency (DC2).** The launch order suggested "use the observability
  router to route which segments inform which layer/parameter." The four layers decompose the **11 already-fit
  axis outputs**, not Phase-1 segments — the router (regime→view evidence routing) is an estimator-fitting
  concern UPSTREAM of these outputs. It is therefore not wired as a runtime dependency of this model.
  Overridable per the Pre-Ruling latitude; recorded as a deliberate scoping decision, no capability lost.

---

## 7. Isolation · tests · commits · triage · map

- **Isolation:** `git worktree list` → `C:/Programs/f1Brainz 08e14014 [main]` and
  `C:/Programs/f1-626 [feat/626-weekend-state-model]` — distinct. All work on the feature branch; no
  `data/*.db` committed (checked every gate).
- **Tests:** `py -m pytest tests/unit/physics/weekend_state/ -q` → **90 passed**. Each gate's tests re-run
  by the commander independently. No production defaults / gold bundle touched.
- **Commits (6):** g1 8ed2f9ea · g2 1e662f19 · g3 b1fd0393 · g4 ea37dd3d · g5 6dab8d5a · arch 1bf691ca.
- **Triage:** tc1 fixed-now (coverage floor, in g5); tc2 (weather anchor), tc3 (ARCHITECTURE FLOAT — Layer-2
  bridge), tc4 (gate_f6 DRY), DB_PATH portability → recommend-and-defer (Admiral owns #601 filing).
  Recs: `.agent-work/wave4-626/TRIAGE_RECOMMENDATIONS.md`.
- **Map impact:** new `struct:physics.weekend_state` node folded into `docs/architecture/packets/physics.md`
  + `index.md` + overlays + new `decision:weekend_state_f6_gate_rubric`; `check_arch_map.py` green (43
  nodes, 21 packets). Two Open Structural Questions routed to triage (Layer-2 FLOAT, hardcoded DB_PATH).
- **PR:** https://github.com/fredcai6/f1Brainz/pull/643 (base main; **do not merge** — Admiral merges at the epic boundary).

---

## 8. Rigor trail

Cold plan-critic (no authoring context) run before freeze; 6 findings ALL accepted and folded into the plan
(`.agent-work/wave4-626/PLAN_CRITIC_DISPOSITIONS.md`): F1 over-shrinkage guard, F2 paired held-out floor,
F3 pinned decision rule + car-season bootstrap, F4 per-layer ablation, F5 Layer-2 season-time-confound
discipline, F6 falsifiable density check. Every gate implement+review through independent crews; each
review re-ran the tests and (g1/g4/g5) reproduced the load-bearing numbers on the live store.
