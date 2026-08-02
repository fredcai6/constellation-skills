# Reviewer Handoff — G3 separation (f_tyre vs g_track)

## Gate
g3 (issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`. `py`, never `python`. Suggested model tier: **stronger (Opus-class)** — the anti-circular + LOO + identifiability checks are subtle.

## Survey State Location
`.agent-work/511/g3-review/review.json` (NOT worktree root).

## What Was Implemented
New evo-free `src/physics/layer2/tyre_separation.py` (525 lines) + `tests/unit/physics/layer2/test_tyre_separation.py`. Separates per-compound tyre decay f_tyre(compound,age) from within-weekend track evolution g_track over the 1,040-stint race_stint_estimates store, in a crossed log-grip model with a quali-anchored relative car envelope. Per-axis: lateral_mech (primary), lateral_aero (honest-null), traction (speculative).

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-511
git status
git diff --stat
git show HEAD --stat   # G1 commit (race_stint_batch) is already committed; G3 files are untracked
git diff -- src/physics/layer2/tyre_separation.py   # (untracked: read the file directly)
```
G3 files are NEW/untracked: `src/physics/layer2/tyre_separation.py`, `tests/unit/physics/layer2/test_tyre_separation.py`. Read them directly. IMPLEMENTER_RESULT: `.agent-work/511/crew-handoffs/g3-implementer-result.md`.

## Task Statement
Implement the crossed log-grip separation `grip_axis = car_envelope(driver→constructor, gp) [from quali, relative] + f_tyre(compound) [base + decay k] + g_track(gp, cumulative_track_laps) + noise`. Season-pool per-compound k via pooling.pool_random_effects with a STRUCTURAL-ONLY monotone prior; per-circuit g_track slope partial-pooled; report identifiability + leave-one-circuit-out LOO. Per-axis vector, lateral primary.

## Close Criteria (each a review check)
- **evo-free**: `tyre_separation.py` imports NO `evo_predictor`/`latent_power`/`compound_prior` (verify by reading imports / AST, not just the implementer's assertion).
- **ANTI-CIRCULAR (the critical check)**: the physics fit uses STRUCTURAL priors ONLY — NO #443 empirical magnitudes are baked in. Verify the DEFAULT prior bakes no compound magnitude (the `test_default_prior_is_noop_anticircular` test asserts the default is a no-op and only an INJECTED tight prior moves k) — re-run it and read the code path. The monotone/k≥0/range prior is structural and OK; a hard-coded SOFT/MEDIUM/HARD k *value* sourced from #443 would NOT be OK.
- **car_envelope from QUALI not race**: confirm the car anchor reads `physics_estimates.db` `session_estimates` (per-constructor `lateral_mech_grip_g`), mapped driver→constructor via the `drivers` list, used RELATIVE/centered — not re-fit from race data.
- **g_track genuine**: a real within-weekend term on `cumulative_track_laps` (per-circuit slope, partial-pooled), not a constant or a relabeled tyre term. Mexico (thin, 4 lateral) is down-weighted/shrunk.
- **LOO discipline**: every residual/stability/covariance-honesty number is leave-one-(circuit)-out / out-of-sample, NOT self-inclusive (`lesson:loo-residual-diagnostic`). Confirm the LOO helper is actually out-of-sample (the fit excludes the held-out fold).
- **planted-recovery**: `test_planted_recovery_lateral` actually recovers a KNOWN planted base/k/track within tolerance (read the fixture — confirm the planted values are non-trivial and the assertion is tight).
- **per-axis vector**: lateral_mech (primary), lateral_aero, traction each produced; honest-null where the signal is absent (lateral_aero; traction level).
- **honest covariance**: per-compound k sigma is real (from the pool), not fabricated.
- `simplification_limits --paths` clean; `py -m pytest tests/unit/physics/layer2/test_tyre_separation.py -q` green on YOUR re-run (expect 9 passed); no W2/quali/pooling/store mutation (`git status` shows only the 2 new files + work area).

## Allowed Scope
The 2 new files. Read-only consumption of stores + pooling.py.

## Specific Exclusions (flag if touched)
Any edit to W2 modules, quali path, pooling.py, the stores; any evo import; any committed .db.

## Constraints (each a review check)
- `constraint:physics_region_no_evo_import`. STRUCTURAL priors only (anti-circular). LOO for self-weighted diagnostics. 2σ = reference not gate. `py` not `python`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `tyre_separation.py` (new); `pooling.py`; the two stores.
- **Constraints:** `constraint:physics_region_no_evo_import`; `lesson:loo-residual-diagnostic-over-self-weighted-predictor`.
- **Decision:** `decision:regime_readiness_rubric` (#512) — per-axis vector posture; the new g_track term is a decision candidate (don't block on it — note it).

## Evidence Produced (re-verify; do not trust blind)
- 9/9 unit tests pass (re-run). evo-free ok. simplification PASS. Layer2 regression 404 passed.
- Real-data smoke: lateral k monotone HARD 0.00121 < MEDIUM 0.00273 < SOFT 0.00327 (σ ≤ 3.9e-4); base contrasts pinned to 0 (raw SOFT −0.05, inverted → null); g_track +0.00749 log-grip/100 laps; identifiability cond 1050, alias 0.191 (LOW) separates=True; LOO oos_rmse 0.1886 ≈ in-sample, k-stability std ≤ 2.8e-4. Traction k monotone, base honest-null. lateral_aero honest-null.

## Reviewer notes
- The fresh-grip BASE not separating (compound signal in DECAY k, not the age-0 level) is an EXPECTED, honest finding — do NOT block on it. It is the correct physics (soft tyres rarely run fresh-and-long → noisy g0 extrapolation).
- The store-read nuance: `RaceStintStore.__init__` runs CREATE TABLE IF NOT EXISTS (write-mode); the implementer read via a `file:…?mode=ro` helper to honor read-only-canonical. This is acceptable (honors the DB-read-only rule). Confirm no canonical DB was actually mutated.

## Suggested Model Tier
Stronger (Opus-class) — anti-circular + LOO-correctness + identifiability are the load-bearing checks.

## Stop Conditions
Return BLOCK if: an evo import is present; #443 empirical magnitudes are baked into the fit (circular); the car anchor is re-fit from race not quali; a "LOO" diagnostic is actually self-inclusive; the planted-recovery test is trivial/non-recovering; a W2/pooling/store module was mutated; or a canonical DB was written.

## Return Format
REVIEW_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g3-reviewer-result.md`: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, Workflow Feedback.
