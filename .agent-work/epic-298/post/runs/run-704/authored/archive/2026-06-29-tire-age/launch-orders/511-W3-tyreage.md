# Launch Order: `cmdr-511 — W3 tyre-age grip-evolution + supplant (CAPSTONE)`

Commanders start cold. Paste, don't point.

## Mission
Issue **#511** (epic #509, tire-age wave W3 — the capstone). Pool the per-stint race fits across the fleet, **separate tyre decay `f_tyre(compound, age)` from track evolution `g_track`**, run the **ratified supplant test** (does physics μ(tyre-age) beat lap-time compound estimation?), and land a **per-axis readiness verdict** on a traceable dashboard — to the §4 done-done bar. This is **Phase-C characterization: measured, NOT wired** (no evo wiring — that's Phase-P #450). Deliverable: the separation + supplant + dashboard, merge-ready PR + verdict.

## Gate structure (suggested; you own the plan)
- **Gate 1 — populate + diagnose-first (evidence).** `race_stint_estimates` is **empty** (W2 shipped the path, not the batch). Run the W2 fit path (`src/physics/layer2/stint_estimator.py` via `session_race.py`) over **all clean 2023 race stints** to populate `race_stint_estimates` (`race_stint_store.py`). Verify coverage (how many stints/compound/circuit fitted; covariance sane). This is compute-heavy (≈889 stints × 5 views × bootstrap) — run it as a tracked batch. **Diagnose-first:** confirm the per-stint `(g0, k)` estimates are usable before building the separation. Float to the Admiral if coverage collapses.
- **Gate 2 — separation.** Fit the crossed fractional/log-grip model: `grip = car_envelope(driver,weekend) + f_tyre(compound, age) + g_track + noise`.
  - `f_tyre(compound, age)` = **THE TARGET**, per-axis **vector** (lateral_mech / lateral_aero / traction). **Lateral is primary**; traction speculative (user: "a stretch") — per-axis honest-null OK. **Season-pooled** via physics `pooling.py` (random-effects/two-way); **strong STRUCTURAL prior** (monotone-up compound ordering, k≥0, plausible ranges) via the #496 injectable-(value,σ) pattern. The per-stint `k` from W2 feeds this; W3 produces the pooled per-compound `k`.
  - `g_track` = weekend track-evolution nuisance on the **`cumulative_track_laps`** axis (stored by W2), per-(circuit, weekend) partial-pooled. **Likely NET-NEW** (pooling.py has no within-weekend time term) — build it lightweight. Use the pit-staggered fleet to identify (same cumulative-laps/track-state, different ages → tyre; same age, different track-state → track).
  - `car_envelope` anchored from the **quali envelope** (C1 #510 / `session_estimates`), not re-fit from race noise.
- **Gate 3 — supplant test.** Physics `μ_tyre(age)` vs incumbent set **{absolute-C# floor, `compound_prior` γ model}** on **within-race pairwise ordering accuracy `P`** (use the neutral harness `src/common/pairwise_ordering.py`) + magnitude R² + honest covariance overlap. **#443 empirical sensor** (`src/compound_prior/empirical_sensor.py`, LOO P=0.80) = **independent CROSS-CHECK** (not the incumbent). **CRITICAL anti-circular rule:** the physics fit uses **structural priors ONLY — NO #443 empirical magnitudes** (else the comparison is circular). Use **held-out / leave-one-out** for any residual/calibration/stability diagnostic over the pooled fit (a self-inclusive form is blind to the failure it detects — see the #443 circular-target trap, caught via an LOO<0.95 sanity check; apply the same discipline). **2σ is a reference, not a gate** (F1 is fine-margin, #512 precedent). Judge **degradation-estimation quality, NOT finish-ranking** (#443 POC showed finish-ranking is car-dominated; that's Phase-P #450).
- **Gate 4 — dashboard + verdict.** One tyre-age characterization dashboard (like #512's): coverage map, per-axis `f_tyre(compound, age)` ladders, `g_track` evolution curves, the supplant result, the identifiability map. **Per-axis GO / CONTEXTUAL / NO-GO** verdict (expect lateral strongest; traction/braking may be CONTEXTUAL/NO-GO — fine).

## Inputs — pasted (verify each from source before use)
- **W2 race fits (on main `0290e419`):** `src/physics/layer2/race_stint_store.py` → `race_stint_estimates` table (per-stint: stint_id, compound, tyre-age range, fuel/mass, `session_type`, `cumulative_track_laps`, g0+k per view, cov blobs; reuses `EstimateStore._cov_list`). `src/physics/layer2/stint_estimator.py` → per-stint joint decay fit `g0·exp(-k·age)`, lateral-lead, injectable `k_prior_mu/k_prior_sigma`. `src/physics/layer2/session_race.py` → race loader (mass via `mass_model.race_mass`, real `track_statuses`). **Age covariate is ABSOLUTE `tyre_life`** (W2 verified track_status 100% populated 2023; note tyre_life starts ~4 for some stints = warm-up — confirm semantics if it matters to pooling).
- **Neutral metric harness (on main):** `src/common/pairwise_ordering.py` — within-race pairwise ordering accuracy `P`. Use it for the supplant metric (no physics→evo coupling; it's neutral).
- **#443 cross-check (on main):** `src/compound_prior/empirical_sensor.py` — empirical `μ_tyre(compound,age)`, LOO P=0.8032, relative-rank corner/straight contrast, 2022+. Honest null: no longitudinal channel (TelemetryStore lacks accel channels). Use as the independent comparator ONLY.
- **Pooling:** physics `src/physics/layer2/pooling.py` (random-effects, two-way team×circuit, drift) + `estimate_store._cov_list`. **Do NOT import evo** (`compound_prior`) into the physics separation — `empirical_sensor` is read only as the comparator at the supplant gate, via a neutral boundary.
- **Mass:** `src/physics/mass_model.py` (`quali_mass`, `race_mass`).

## Prior-Wave Verdicts (pasted)
- **W1 (#562, merged):** per-context mass model; `quali_mass(2023)=808.0` preserved; SC/VSC-aware `race_mass` (race ≈ 890 kg vs quali 808).
- **#443 arm (#565/#571, merged):** empirical sensor LOO P=0.8032 (>0.74), monotone-up ladder, perm z=5.22σ; neutral pairwise-P harness in `src/common`. Caught a circular-target bug (target must be independent of the feature) — heed this for the supplant test.
- **W2 (#563, merged):** race fit path; per-stint joint decay (fit-shape B, Admiral-ruled); lateral-lead; absolute tyre_life; cumulative_track_laps stored; injectable k-prior; TrackStatus gate cleared; 889 clean 2023 stints; pit-staggered age-spread mean 17.4, 94% multi-compound (strong identifiability).

## Pre-Rulings (overridable; say so if overriding)
- Physics region only (`src/physics/` + the store + tests + docs + a dashboard script). Read the #443 sensor + neutral harness as comparators; do NOT couple the physics separation to evo.
- 2023 first (matches the pool); structure for multi-season.
- Per-axis vector verdict; lateral primary, traction speculative; braking-null expected/fine.
- Structural priors only in the supplant-test physics fit (anti-circular). Held-out/LOO for diagnostics.
- 2σ = reference not gate. Measured-not-wired (no evo wiring).
- **Reachback to C1 quali utilization (#510): OPTIONAL/overridable** — not required, but if the race-utilization data breakdown looks useful you may add it (user: "wouldn't be mad"); note the reachback on #510 + #511 regardless.
- Honest-null is success: "can't separate tyre from track at usable σ" or "physics doesn't beat the incumbent" is a complete, documented verdict (NO-GO is a valid done-done).

## Honest-Null Clause
A measured negative is a complete, successful deliverable — full rigor. **Posture: build a solid, expandable baseline; the FIRST build is NOT the final answer; take any null/negative result in stride, stay confident we improve it over the long run — do NOT thrash on a negative.** (The epic closeout will produce 25 improvement ideas.)

## Inherited Latitude
- **Delegated to you:** the gate plan, separation model details, pooling structure, the `g_track` term design, dashboard layout, fit hyperparameters, prior strengths (structural).
- **Float to the Admiral:** coverage collapse at gate-1; any need to import evo into the physics separation; any architecture/boundary change; scope beyond physics + store + tests + docs + dashboard; if the supplant test design needs to change materially (the user expects learnings to reshape it — float the reshape, don't silently pivot).

## File Ownership
Sole writer for: the W3 separation/supplant modules + dashboard script + tests + touched docs, and `race_stint_estimates` data population. No other commander is active. Do NOT commit `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md`/your own `.agent-work/<id>/` on the mission branch (return them in your report; Admiral applies centrally). **At archive, PUSH the branch and OPEN the PR via `gh pr create -F <file>`** — prior W-commanders stalled at this step; drive through it (and post your verdict as a comment on #511).

## Workspace
Worktree **`C:/Programs/f1Brainz-511`**, branch **`feat/511-tyre-age-evolution`**, base **`origin/main` `0290e419`** (full foundation). Before any git op: `git -C C:/Programs/f1Brainz-511 rev-parse --show-toplevel` must be `C:/Programs/f1Brainz-511` (NOT shared `C:/Programs/f1Brainz`); `git worktree list`. Paste output. *(verify_worktree_isolation.py not vendored — use this rev-parse check; sanctioned by the Admiral.)*

## Inherited Context (lessons + invariants)
- Python is `py`, never `python`. Crew dispatch via the **Agent tool** (no `claude` CLI); `run_crew.py` registry + `recover_crews.py` before each dispatch. Engine artifact postconditions **attached, not attested** (review-result to BOTH gN-review and gN-integrate). Compact step: skip with reason. **State-note before each detach** (gate-1 batch is long — detach + state-note). Cite exact seams from source.
- **lesson:loo-residual-diagnostic** — any residual/calibration/stability diagnostic over a self-weighted/smoothing/pooled predictor MUST use leave-one-out/out-of-sample, or it's blind to the failure it detects. (This is the #512 + #443 recurring trap.)
- Physics evidence: region suite green; `py -m src.utils.simplification_limits` on touched paths; honest covariance; units/bounds/invariants explicit. **DB/telemetry-store is the ONLY data source.**
- **CI: pyright baseline-diff** — self-verify `py scripts/pyright_baseline_diff.py` shows **`new=0`** before pushing (pyright is non-required so it won't block the merge gate, but the Admiral checks the row — don't slip errors). CI here runs pyright/arch/docs only, **NOT pytest** — tests are a LOCAL gate (run them yourself).

## Data Locations (absolute — worktrees lack untracked inputs)
- Telemetry store (race telemetry 2018–2026, the gate-1 fit inputs): `C:/Programs/f1Brainz/data/telemetry_store.db` (`DEFAULT_STORE_PATH` is this absolute path).
- Per-year DBs (laps, compound, tyre_life, track_status, lap_number, weather): `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- Quali estimate store (for `car_envelope` anchor): `C:/Programs/f1Brainz/data/physics_estimates.db` (table `session_estimates`).
- `race_stint_estimates` store DB: created/written by `race_stint_store.py` — write it to a sensible path under `C:/Programs/f1Brainz/data/` (verify where the W2 code defaults it; do NOT commit the .db).
- Read-only on existing data; do not delete/mutate the FastF1 cache or existing DBs.

## Budget
Model tier **Opus** (the subtle separation). Gate-1 batch is compute-heavy — detach + poll to completion (don't strand the deliverable). Verify crew completion from artifacts, not liveness.

## Stop Conditions
Stop and return (float to the Admiral) when: gate-1 coverage collapses; you'd need to import evo into the physics separation; the supplant design needs a material reshape; scope exceeds physics + store + tests + docs + dashboard; or you need context not covered. Asking up is always sanctioned.

## Return Shape
Final report: **per-axis readiness verdict** (lateral / traction / braking: GO / CONTEXTUAL / NO-GO) + the supplant result (physics μ_tyre(age) `P` vs {absC#, compound_prior γ}, + #443 cross-check agreement) + coverage + honest covariance + the dashboard path + PR URL + map-impact + triage candidates (incl. improvement ideas for the closeout 25-list) + workflow feedback (lessons-delta + friction) + rev-parse isolation confirmation. Post the verdict in your return + a comment on #511. On Windows open the PR via `gh pr create -F <file>`. **Drive through push+PR — do not stall at archive.**
