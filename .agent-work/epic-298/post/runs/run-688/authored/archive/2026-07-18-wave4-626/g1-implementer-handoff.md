# Implementer Handoff

## Gate
`g1` — Frozen metric harness: normalization frame + held-out split + x4 floor reproduction + frozen F6 gate spec.

## Task
Build the NEW package `src/physics/weekend_state/` metric foundation that the whole four-layer model (later gates) is judged on, FROZEN before any layer exists:
- **frame.py** — load `session_estimates` (`session_type='Q'`, `fit_status='ok'`) from the ABSOLUTE main-checkout DB into a tidy long/wide frame keyed per `(year, gp_name, constructor, round_idx)` over the 11 axes + their `_sigma` columns. Also expose `rho`, `rho_is_fallback`, `mass_kg_assumed` (later layers need them). Read-only.
- **floor.py** — a FAITHFUL re-implementation of x4's exact metric, parameterizable to run on ANY value column (not just raw), so later gates run it on the model's output. Per axis: `field_sigma` = median over weekends (>=6 constructors) of the cross-constructor SD; `noise_sd` = median over car-seasons (>=4 ok weekends) of the within-car-season SD around that car-season's own mean; `N_weekends = (noise_sd/field_sigma)**2`; `snr` = between-car-season-spread-of-season-means / noise_sd. Provide a `weekend_relative(df, axis)` transform = axis minus that weekend's (year, round_idx) field MEDIAN.
- **holdout.py** — a DETERMINISTIC frozen weekend held-out split (e.g. hold out weekends where `round_idx % K == r0` for fixed K, r0, or a hash of (year, round_idx) — your choice, but FROZEN + documented + reproducible). Must leave >= a few held-out weekends per car-season so a within-car-season SD is computable on the held-out subset. Expose `is_holdout(year, round_idx) -> bool` and `split(df) -> (train_df, holdout_df)`.
- **gate_spec.py** — the FROZEN F6 decision rule as code + constants, authored NOW before any layer or held-out number is seen. It must encode the three cold-critic fixes below.

## Cold-critic fixes to bake into gate_spec.py (from PLAN_CRITIC_DISPOSITIONS.md — read it)
- **[F2] Paired held-out comparison.** The gate compares model-vs-floor on the IDENTICAL held-out weekends, paired per car-season. Provide a harness that recomputes the raw x4 weekend-relative floor on ANY given held-out weekend subset. The 624 full-sample table is only the reproduction/sanity target, NOT the comparison denominator.
- **[F1] Signal-preservation guard.** Provide a function to score a fitted model's held-out car-signal by its OUT-OF-SAMPLE residual around a train-fit trajectory (so an over-shrinker emitting a near-constant per car-season is punished by large held-out residual on developing cars) — NOT by its own self-dispersion. Encode that PASS requires faster convergence AND preserved held-out accuracy (define the accuracy criterion: held-out car-signal reconstructs the raw held-out weekend-relative reading within its stored `_sigma`, no systematic collapse).
- **[F3] Pinned decision rule.** `PASS` = model beats the paired held-out raw floor on **>=7/11 axes** by a margin OUTSIDE NOISE, where the noise margin comes from a bootstrap whose RESAMPLING UNIT is the car-season (fixed seed), tie = NOT-a-beat. The median convergence-speed ratio across axes is the reported summary (both named in the launch order). Include an MDE/power sanity helper on the chosen split (given the held-out car-season counts, what effect size is detectable).

Encode these as constants + pure functions with a fixed RNG seed; DO NOT read any held-out result to tune them — they are frozen here.

## Protected Intent
The metric the model is judged on must BE x4's own metric (reproduced within tolerance), frozen before any layer exists, and un-gameable by over-shrinkage. If floor.py silently diverges from x4, the whole F6 gate is meaningless.

## Test Mode
TDD-leaning / test-after allowed. The load-bearing test is the x4 floor reproduction — write it against the 624 table.

## Close Criteria
- `frame.py` loads the Q store faithfully from the absolute path; row count and columns match the store (1,562 ok Q rows region; don't hardcode — assert > 1500 and all 11 axes present).
- `floor.py` reproduces the 624-phase0-baseline-lock x4 table for ALL 11 axes (rel & abs `noise_sd` and `N_weekends`) within a TIGHT numeric tolerance (e.g. rel tol 1e-2 on noise_sd, given it re-derives the same medians) — proving floor.py IS x4's metric. `test_floor_reproduction.py`.
- `holdout.py` split is deterministic (same output across runs), documented, and leaves computable held-out car-seasons; `test_holdout_split.py` asserts determinism + that >= a threshold of car-seasons have >=2 held-out weekends.
- `gate_spec.py` decision rule + bootstrap are deterministic (fixed seed) and encode F1/F2/F3; `test_gate_spec.py` asserts: over-shrinker (constant-per-car-season synthetic model) does NOT PASS the signal-preservation guard; a synthetic model that genuinely lowers noise while preserving accuracy DOES register axis-beats; the >=7/11 rule + tie handling behave as specified.
- No evo import anywhere in the package. No `data/*.db` staged/committed.

## Allowed Scope
`src/physics/weekend_state/{__init__,frame,floor,holdout,gate_spec}.py`; `tests/unit/physics/weekend_state/{test_floor_reproduction,test_holdout_split,test_gate_spec}.py`. Create `tests/unit/physics/weekend_state/__init__.py` if the test tree needs it.

## Specific Exclusions
Do NOT build any of the four layers here (g2–g5). Do NOT touch the estimator (`src/physics/layer2/*`), evo, or production config. Do NOT commit or modify any `data/*.db`.

## Constraints
- Python is `py` (never `python`). numpy/pandas available.
- DB is UNTRACKED in this worktree — read from the ABSOLUTE main path `C:/Programs/f1Brainz/data/physics_estimates.db` (lesson:worktree-untracked-data). Make the path a module constant with a clear name; tests read the same path.
- `constraint:physics_region_no_evo_import` — import no evo.
- The `.pth` editable-install trap: assert `src.physics.weekend_state.frame.__file__` resolves under `C:/Programs/f1-626` if you write any bespoke check script (tests are cwd-safe).
- Floor metric MUST match x4's `normalization_stability.py` logic exactly (cite it): field SD on weekends with >=6 constructors (MIN_FIELD=6); car-season SD on car-seasons with >=4 ok weekends (MIN_WEEKENDS=4).

## Map Anchors (inbound)
- **Structural:** `src/physics/weekend_state/` (NEW greenfield); `data/physics_estimates.db:session_estimates` (11 axes + `_sigma`, PK(year,gp_name,session_type,constructor), plus `rho`,`rho_is_fallback`,`mass_kg_assumed`,`round_idx`,`final_rel_delta`).
- **Capability:** x4 weekend-relative floor metric reproduced as a reusable, column-parameterizable harness.
- **Constraints:** `constraint:physics_region_no_evo_import`; no `data/*.db` commit (#632).
- **Decision anchors:** DC3 — the held-out split is frozen HERE, before any layer is fit.
- **Evidence:** claim — 624 x4 floor table reproduced within tolerance; over-shrinker fails the F1 guard.

## Reference sources (cite exactly; read before coding)
- x4 method script (the metric to reproduce): `C:/Programs/f1-626/.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x4-analysis/normalization_stability.py`
- The frozen floor table: `C:/Programs/f1-626/docs/physics/624-phase0-baseline-lock.md`
- Cold-critic fixes: `C:/Programs/f1-626/.agent-work/wave4-626/PLAN_CRITIC_DISPOSITIONS.md`
- Store schema: `session_estimates` columns listed in MISSION_FRAME.md.

## Deliverable Path Check
- **Committed** — `src/physics/weekend_state/*.py`, `tests/unit/physics/weekend_state/*.py`; verified `git check-ignore` exits 1 (NOT ignored) for `src/physics/weekend_state/frame.py` and `tests/unit/physics/weekend_state/test_floor_reproduction.py` before dispatch.
- New files are untracked until staged: `git diff` shows them only after `git add`; they appear in `git status`.

## Required Evidence
- `py -m pytest tests/unit/physics/weekend_state/test_floor_reproduction.py tests/unit/physics/weekend_state/test_holdout_split.py tests/unit/physics/weekend_state/test_gate_spec.py -q` — all pass.
- A short printout (in the result) of floor.py's reproduced 11-axis table next to the 624 numbers, so the reviewer sees the match.
- `grep -r "evo" src/physics/weekend_state/` returns nothing importing evo.

## Verification Commands
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_floor_reproduction.py tests/unit/physics/weekend_state/test_holdout_split.py tests/unit/physics/weekend_state/test_gate_spec.py -q
```

## Suggested Model Tier
Stronger — the metric fidelity + un-gameable gate spec carry the whole run's validity.

## Authority
The gate decision rule (>=7/11, car-season bootstrap, signal-preservation guard) is FROZEN by the commander/launch-order — implement it exactly; do not soften or re-tune it. The held-out split RULE is yours to choose but must be frozen + documented + satisfy the computability constraint.

## Stop Conditions
Stop and return if: floor.py cannot reproduce the 624 table within a defensible tolerance (report the divergence — it may be a real methodology question to float), the absolute DB path is unreadable, or the held-out split cannot leave computable car-seasons.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/wave4-626/g1-implementer-result.md`: completed slice, files changed, test output, the reproduced-vs-624 table, assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
