# Problem statement — #626 Phase 2 four-layer weekend-state model (delegated)

Reconciled against frozen LAUNCH_ORDER (ShipE-626) + confirmed DESIGN_SPEC Phase 2 + F6/F9 dispositions.
No reachable human; Admiral is principal.

## The ask (one bounded issue)
Build a **four-layer weekend-state model on qualifying**, each layer carrying an honest σ, that turns
the raw per-session physics Q estimates (`data/physics_estimates.db:session_estimates`, 11 axes ×
`_sigma`, 2019–2026) into a properly-decomposed weekend state. Deliver a **held-out** falsifiable gate
(F6) proving the four layers do real work beyond weekend-median subtraction (x4's relative floor).

## The four layers (each with σ)
1. **Explained physics** — remove the density/mass-explained component per session. Density from
   MEASURED per-session pressure via `src/utils/environment.moist_air_density_from_pressure` (NOT fixed
   RHO=1.2, NOT the buggy altitude lookup); mass/fuel from `mass_kg_assumed`. Deterministic-ish; σ from
   pressure/measurement + model uncertainty.
2. **Structured within-session evolution** — a smooth grip latent for track rubbering-in *within* a
   session (the F9 foot-gun a weekend-constant median hides). Modelled as a smooth latent over session
   time with σ. **Identifiability crux (flagged):** `session_estimates` is one Q row per car-weekend with
   no within-session timing, so true within-session rubbering is below its granularity. Build from the
   finest reachable proxy (`damage_integrals.db:grip_bin_obs` track-grip-vs-cumulative-laps; else a
   season-time smooth track/conditions latent as the identifiable analog). Per Pre-Ruling 2 + float
   clause: build + test honestly on held-out; REPORT (and float) if it cannot earn its keep — never
   silently drop.
3. **Field-car common-mode state** — cake-and-eat-it two-stage: (a) RELATIVE = car − weekend field
   median (resolves fast); (b) re-anchor onto a best-estimate field car by fitting a SMOOTH field-car
   absolute trajectory over the season (reuse `src/physics/layer2/pooling.py` random-effects τ² +
   `weighted_trend`) so ABSOLUTE development still accrues. Both stages carry σ.
4. **Car signal** — the shrunk/smoothed deltas off the field car (the thing later phases want; the
   quantity whose noise_sd the F6 gate measures).

## Mechanism by which 4 layers can beat x4's floor (falsifiable, not guaranteed)
x4's "relative" reading is the RAW per-weekend (car − noisy ~10-sample field median), a single-weekend
point estimate. The four-layer car signal (a) removes explained physics first (less density/mass
common-mode leakage than a plain median) and (b) replaces each weekend's own noisy raw median with a
POOLED smooth field-car trajectory + shrinkage → lower within-car-season noise_sd → fewer weekends to
resolve → beats the floor. Honest-null is a real possible outcome (Pre-Ruling / Honest-Null clause).

## Gate (F6 — pinned, HELD-OUT mandatory)
Re-run x4's EXACT methodology (`normalization_stability.py`: noise_sd = within-car-season SD of weekend
readings around season mean; field_sigma = median cross-constructor within-weekend SD; N_weekends =
(noise_sd/field_sigma)²) on THIS model's output, on a **held-out weekend split** (weekends NOT used to
fit hyperparameters). Pinned statistic: median convergence-speed ratio across axes. Threshold: beat the
relative floor on ≥7/11 axes by a margin outside noise. Freeze methodology + split rule BEFORE looking
at held-out results. LOO/out-of-sample discipline mandatory (lesson:loo-residual-diagnostic) — a
self-weighted smoother pins predictions to their own value and is blind to the failure it tests.
Secondary: density layer must EXPLAIN a known cross-track difference (Mexico high-altitude low-density
vs Monaco sea-level) physically, not need an ad-hoc correction.

## Constraints / fences
- No evo import from physics (`constraint:physics_region_no_evo_import`).
- No production-default / gold-bundle change. No `data/*.db` commit (#632 — `git checkout -- data/`).
- Commander does NOT run multi-hour compute (lesson:admiral-owns-long-batch-compute). Analyses here are
  cheap (pandas over ~1.6k rows; smooth fits over ~159 weekends × 11 axes) — keep foreground ≤10 min.
- Worktree lacks untracked DBs → absolute paths into `C:/Programs/f1Brainz/data/*` (lesson:worktree-untracked-data).
- Durable homes: modules `src/physics/`, tests `tests/`, gate evidence + writeup `docs/physics/`.

## Float posture
No blocker now — the one genuine gap (Layer 2 identifiability) is pre-dispositioned by the launch order
(build+test+report). Float ONLY if: Layer 2 fundamentally cannot be identified after honest attempt
(report held-out evidence + float), a scope cut is needed, a production default must change, or work
requires touching Phase-3 scope / Phase-1 public surface.
