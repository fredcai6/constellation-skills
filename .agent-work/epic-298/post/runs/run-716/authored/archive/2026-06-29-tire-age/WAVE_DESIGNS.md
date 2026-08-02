# Tire-Age Epic — Settled Wave Designs

Resolved via the latitude/pre-interrogation (18 questions), 2026-06-28. Source for the launch orders.
Sub-epic of #509. All issues filed under #509. Gate W1 dispatch on **#495 landing**.

**Epic-wide posture (every launch order):** build a *solid, expandable base* — the first build is a
baseline, not the answer. Take null/negative results **in stride** (a measured null is a successful
baseline step). Expandability is a first-class design criterion. Phase-C = **measured, not wired**.

---

## W1 — Mass / fuel model  *(foundation; new issue under #509)*

- **Scope:** produce **+ rewire** all fixed-`MASS_KG=808` consumers (`force_residual`, `braking_view`,
  `coast_view`, `decoupled_*`) to take a real per-context mass. *(Decision: b, full rewire.)*
- **Model:** `m(season, team, lap) = base_min(season) + team_offset(season, team) + fuel(...)`.
  - `base_min(season)` = FIA reg minimum car+driver, **per season** (verify 798/798/798/800…).
  - **Quali** = `base_min(season) + nominal_quali_fuel (~10 kg, configurable)` — season-aware, NOT a
    fixed cross-season 808; 2023 reproduces ~808 so the 2023-Q pool/`theta_D` stay comparable.
  - **Fuel** = per-circuit linear, **SC/VSC-aware cumulative burn** (green laps full, SC/VSC reduced),
    cap 110 kg. *Data dep:* per-lap `TrackStatus` in the lap store (verify/ingest).
  - **`team_offset`** = config hook, default 0, anchor (not fitted); applies to quali + race.
- **Validation (tier b):** formula + bounds (monotone, ≤110, end ≥~1 kg, burn∈[1.5,2.2]) + a physical
  sanity check (~0.03 s/lap/kg gut-check plot). No fit.
- **Future issues (file under #509):** (c) full fuel-mass pace-validation; (b) estimate per-team mass offset.

## W2 — Race-session five-view fit path  *(foundation; new issue under #509; needs W1)*

- **Unit:** **(B) per-stint decay fit** — fit each view over a stint, `frontier = g0·exp(−k·age)`,
  recover fresh `g0` + decay `k` per `(driver, race, stint)` with covariance. Single managed laps too
  thin → pool many stints.
- **Layering:** **W2 produces** per-stint grip-vs-age observations (A); **W3 separates** (B-hierarchical).
  Joint-fit fallback if per-stint covariance is hopeless (a checkpoint decision).
- **Views:** lateral-lead (clean instrument), traction-second (vector), braking + power-drag
  characterized (power-drag also = mass/fuel cross-ref), coast diagnostic-only.
- **Lap selection:** reuse cleanliness filters — green-flag committed laps; exclude in/out/lap-1/
  SC/VSC/red-flag/invalid; configurable gap-ahead threshold (~1.5 s) for dirty air; per-channel filter later if needed.
- **Output:** **new `race_stint_estimates` table** in the same store DB (per-stint grain: stint_id,
  compound, tyre-age range, fuel/mass, `session_type`, `cumulative_track_laps`, g0+k per view, cov
  blobs). Reuse `EstimateStore` plumbing; `session_estimates` (`estimate_store.py:335`) untouched.
- **Interface:** built **session-agnostic** now (fits race; schema/interface carry session_type +
  cumulative_track_laps so FP/quali plug in later). FP *fitting* stays #513.
- **Gate 1 = diagnose-first (evidence-only), 2023 first:** coverage counts; per-stint fit viability
  (A vs B); regularizer-style identifiability map (`same_progress_tire_age_spread` /
  `same_age_progress_spread` / `distinct_stint_start_bins`) — are pit-staggered conditions present to
  separate tyre vs track. Ends at a **decide-fix checkpoint** before W2 freezes.

## W3 — Tyre-age grip-evolution + supplant  *(#511; Opus tier; needs W2)*

- **Model (fractional/log grip):** `grip = car_envelope(driver,weekend) + f_tyre(compound,age) +
  g_track + noise`.
  - `f_tyre(compound, age)` = **target**, per-axis **vector** (lateral_mech/lateral_aero/traction;
    lateral primary, traction speculative — "a stretch," per-axis honest-null OK). **Season-pooled**,
    strongest axis (huge N on the same compound), strong **structural** prior (monotone-up ordering,
    γ≥0, ranges) via the #496 injectable-(value,σ) pattern.
  - `g_track` = **weekend track-evolution nuisance**, **session-agnostic** (quali + practice + race all
    measure/feed it; quali = clean probe), axis = **cumulative track-laps run** (rubbering proxy, not
    wall-clock). Per-(circuit, weekend) partial-pooled. **Likely net-new** (pooling.py doesn't do
    within-weekend time terms) — build lightweight; gate on the W2 identifiability map.
  - `car_envelope` anchored from the quali envelope (C1 #510), not re-fit from race noise.
- **Separation:** pit-staggered fleet (same cumulative-lap/track-state, different ages → tyre; same age,
  different track-state → track). Reuse physics `pooling.py` for season-pooled `f_tyre`; **do NOT import
  `compound_prior`** (evo region) — it's the design template, not a dependency.
- **Supplant test (starting point, revisable at checkpoints):** physics `μ_tyre(age)` vs incumbent set
  **{absolute-C# floor, `compound_prior` γ model}** on **within-race pairwise ordering accuracy P**
  (held-out) + magnitude R² + honest covariance overlap. **#443 = independent cross-check** (not
  incumbent). Physics fit uses **structural priors only — NO #443 magnitudes** (anti-circular). 2σ =
  reference not gate. Judges **degradation-estimation quality, NOT finish-ranking** (Phase-P #450).
- **Reachback (optional, overridable):** race-utilization refinement of C1 #510 — not required, but
  W3 may opt in if the data breakdown looks useful; note reachback on #510 + #511.
- **Done-done:** §4 bar; one tyre-age dashboard (coverage, per-axis f_tyre ladders, g_track curves,
  supplant result, identifiability map); **per-axis** GO/CONTEXTUAL/NO-GO verdict.

## #443 arm — Empirical cross-check  *(#443; parallel with W2; evo region)*

- **Deliverable (a):** productionize the validated recipe out of `scratch/` — empirical
  `μ_tyre(compound,age)` estimator (DRS-clean corner/straight contrast, relative-rank, 2022+,
  committed-laps, mass-cancelled) + the **shared within-race pairwise-P metric harness** (a **neutral**
  eval util usable by both physics-W3 and evo-#443 **without a physics→evo import**).
- **Threads (gate composition, new sensors):** → closeout research plan, stay on #443, out of scope
  (W3-triggered exception only).

---

## Wave plan / sequencing

| Wave | Issue | Depends on | Model tier | Checkpoint |
|---|---|---|---|---|
| W1 mass | new #509 child | #495 landed | Sonnet | stop-and-present |
| W2 race-fit | new #509 child | W1 | Sonnet | diagnose-first decide-fix, then stop-and-present |
| #443 arm | #443 | #495 landed (parallel W2) | Sonnet | stop-and-present |
| W3 tyre-age | #511 | W2 (+#443 arm) | **Opus** | contract re-confirm after W2; stop-and-present |

Contract **expiry: re-confirm after W2 merge** (its coverage result reshapes W3).

## Issues to file under #509 (delegated)
1. **W1 mass/fuel model** (new).
2. **W2 race-session fit path** (new).
3. (#511 exists — W3.) (#443 exists — arm.)
4. Future: full fuel-mass pace-validation (c).
5. Future: per-team mass-offset estimation (b).
