# x1: Physics estimate coverage — (season, session-type) matrix

**Question:** Which (season, session-type) cells can the physics pipeline produce per-car
capability estimates for TODAY, and what concretely breaks or is missing outside the
proven 2023-Q slice?

**Method:** read-only. Queried the actual on-disk SQLite stores directly (row counts by
year/session_type/status), read the producing code paths, checked `gh issue view` for the
one blocking issue found, and checked backfill log timestamps. No pipeline was run.

## Headline finding

The "proven 2023-Q slice" framing in prior memory/docs is **stale**. The stores were
backfilled to all of **2019–2026** for both Q (quali) and R (race) some time before this
excursion (orchestrator log timestamp 2026-07-07, ten days before this run). There are
**three separate stores**, not one:

| Store | Table | File | Session type(s) present | Grain |
|---|---|---|---|---|
| Layer-2 five-view estimate store | `session_estimates` | `data/physics_estimates.db` | **Q only** | per (year, gp, constructor) |
| Layer-1 single-channel fit store | `session_fits` | `data/physics_fits.db` | **Q only** | per (year, gp, driver) |
| Race stint estimate store | `race_stint_estimates` | `data/race_stint_estimates.db` | **R only** | per (year, gp, driver, stint, compound) |

Verified by direct query (`data/physics_estimates.db:session_estimates`,
`data/physics_fits.db:session_fits`, `data/race_stint_estimates.db:race_stint_estimates` —
each queried 2026-07-17, this excursion):

```
session_estimates: DISTINCT session_type = ['Q']   (2019..2026, 205-239 ok/season, 1-7 error/season)
session_fits:       all rows session_type='Q'        (2019..2026, ~152-478 ok/season)
race_stint_estimates: DISTINCT session_type = ['R'] (2019..2026, 351-1181 rows/season)
```

The raw-input ceiling (telemetry Parquet/SQLite mirror, `data/telemetry_store.db:tele_sessions`)
already holds **FP1, FP2, FP3, Q, R, S (sprint race), SQ (sprint quali)** for every season
2018–2026 (e.g. 2023: FP1=21, FP2=16, FP3=16, Q=22, R=22, S=6, SQ=6 sessions).  So for every
BLOCKED/UNKNOWN cell below, the gap is **code path / never-run**, not missing raw telemetry.

## Coverage matrix (2022–2026 × FP1/FP2/FP3/Q/SQ/R)

State legend: **WORKS TODAY** (rows exist in a store, code path proven) / **SHOULD WORK**
(loader + estimator plumbing accepts the session type, but the run has never happened and at
least one open correctness question is unresolved) / **BLOCKED** (a named missing piece
blocks it) / **UNKNOWN** (not conclusively tested either way).

| Season | FP1 | FP2 | FP3 | Q | SQ | R |
|---|---|---|---|---|---|---|
| 2022 | BLOCKED | BLOCKED | BLOCKED | **WORKS TODAY** | UNKNOWN | **WORKS TODAY** |
| 2023 | BLOCKED | BLOCKED | BLOCKED | **WORKS TODAY** | UNKNOWN | **WORKS TODAY** |
| 2024 | BLOCKED | BLOCKED | BLOCKED | **WORKS TODAY** | UNKNOWN | **WORKS TODAY** |
| 2025 | BLOCKED | BLOCKED | BLOCKED | **WORKS TODAY** | UNKNOWN | **WORKS TODAY** |
| 2026 | BLOCKED | BLOCKED | BLOCKED | **WORKS TODAY** | UNKNOWN | **WORKS TODAY** |

(2019–2021 were also checked opportunistically and match the same pattern: Q and R
WORKS TODAY, FP/SQ absent from every store. Not shown in the table since the brief scoped
2022–2026.)

### Q — WORKS TODAY

- `data/physics_estimates.db:session_estimates` — one row per (year, gp, constructor),
  `session_type='Q'` for every row. Row counts by year (ok/error), queried live:
  2019: 205/5, 2020: 164/6, 2021: 215/5, 2022: 213/7, 2023: 216/4, 2024: 233/7, 2025: 239/1,
  2026: 77/0 (2026 partial season, in progress).
- `data/physics_fits.db:session_fits` — one row per (year, gp, driver), all `session_type='Q'`.
  2022: 436 ok, 2023: 436 ok, 2024: 478 ok, 2025: 475 ok, 2026: 152 ok (plus small
  `no_laps`/`no_speed_stream`/`no_accel_samples` counts per season — a handful of clean-null
  driver-sessions, not systemic breakage).
- Producing code: `scripts/build_physics_estimates.py` (`src/physics/layer2/estimate_batch.py`
  → `session_estimator.estimate_session`) for the five-view store;
  `scripts/build_physics_fit_store.py` (`src/physics/fit_batch.py`) for the Layer-1 store.
- Pooling/reporting: `scripts/pool_physics_estimates.py --year <Y>` → markdown under
  `reports/physics/`.
- The docs at `docs/architecture/packets/physics.md` still frame everything as
  "2023-Q" (e.g. lines 486, 552, 556, 933, 1629, 1666 — all characterization work done on
  2023-Q specifically). That's a **characterization/validation** scope statement, not a
  store-coverage statement — the doc is accurate about what was *validated*, but the store
  itself now has 8 seasons of Q rows sitting behind it, unflagged in that doc.

### R (race stints) — WORKS TODAY

- `data/race_stint_estimates.db:race_stint_estimates` — one row per
  (year, gp, driver, stint_num, compound), `session_type='R'` for every row. Row counts:
  2019: 1015, 2020: 817, 2021: 1038, 2022: 1149, 2023: 1158, 2024: 1181, 2025: 1131,
  2026: 351 (partial season).
- This is a **separate build** from the Q pipeline (Epic #563, "g4"/"W2 fit path"):
  `src/physics/layer2/race_stint_batch.py` + `race_stint_store.py` + `stint_estimator.py`.
  Doc comment at `src/physics/layer2/race_stint_store.py:9-13`: "completely separate from
  the per-constructor `session_estimates` table."
- Producing code: `scripts/populate_race_stint_estimates.py --year <Y> --db
  data/f1_data_<Y>.db --out data/race_stint_estimates.db` (resumable; `--refit` to force).
- **Concrete constraint found**: `race_stint_batch.py` hard-codes the SQL literal
  `session_type='R'` in its two loader queries (`race_stint_batch.py:156`, `:185` —
  `_load_lap_times_for_race`/stint loader both filter `WHERE ... session_type='R'`), even
  though the *output* schema's `session_type` column is described as "session-agnostic for
  future work" (`race_stint_store.py:20-23`). This means **Sprint race (S) stints cannot be
  produced by pointing this pipeline at S** without a code change to the query — it is not a
  parameter today despite looking like one. Not separately tested against S data; scoped null
  — this establishes the SQL is literal-R, not that S would fail for other physics reasons.

### FP1 / FP2 / FP3 — BLOCKED

- **Cited blocker: issue #513** ("C4: FP-session fits enabler — physics on pre-quali sessions
  for the weekend-local path"), state OPEN, labeled `physics-state-space`, body says
  "**QUEUED** — detail when reached," done-done criterion is still just "Coverage map
  FP1/FP2/FP3 × regime; covariance vs quali baseline → verdict" (i.e. the excursion this very
  file is part of, not yet closed). No PRs reference it.
- No rows for any FP session type exist in `session_estimates` or `session_fits` (both
  queried, `DISTINCT session_type` returns only `['Q']` in each). No FP-related log lines
  found in any `data/*.log` backfill log (grepped `session_type=FP`, `--session-type FP1|2|3`
  across all `data/*.log` — zero hits). Tested: absence of stored output and absence of
  run logs. Not tested: whether someone ran it manually outside logged scripts (no evidence
  either way, treated as not-run).
- **Plumbing exists but is unvalidated and has a known-wrong default**: both batch scripts
  accept a session-type argument (`build_physics_estimates.py --session-type FP1`,
  `build_physics_fit_store.py --sessions FP1`) and the loader
  (`src/physics/session_fit.py:load_quali_session`) takes `session_type` as a plain string
  passed through to the FastF1-cache/telemetry-store seam with no Q-specific branching in the
  loader itself — so at the I/O layer FP1-3 "should" load.
  However `src/physics/layer2/session_estimator.py:125` — `m = quali_mass(year)` — is called
  **unconditionally inside `estimate_session`**, regardless of what `session_type` the batcher
  passed in. `mass_model.py` has `quali_mass()` and `race_mass()` but **no `fp_mass()`**
  (checked `grep def .*mass` in `src/physics/mass_model.py`). FP2/FP3 runs mix quali-sim
  (light fuel) and race-sim (heavy fuel) laps in the same session — applying quali_mass
  uniformly would silently bias CdA/P_max/braking-decel magnitude for any race-sim lap that
  slipped through the flying-lap filter in `session_fit.py:fit_driver` (which only filters by
  lap-time-vs-best, not by run purpose). This is exactly the open question #513 names
  ("FP2/FP3 carry qualifying-simulation flying laps; FP1 is messier") and is the concrete
  reason this is BLOCKED rather than SHOULD WORK — running it today would silently produce
  numbers, not obviously-wrong errors.

### SQ (sprint qualifying) — UNKNOWN

- No rows in `session_estimates` or `session_fits` (only `'Q'` present in either).
- No dedicated tracking issue found: `gh issue list --search "sprint"` and `--search "SQ
  physics"` returned #604 (FP-collect race-week command, not physics fits), #513 (FP only,
  doesn't mention SQ), #450, #509, #601, #566 — none scope SQ specifically.
- Raw data exists: `tele_sessions` has SQ rows every season since 2021 (2021-2025: 3-6/season,
  2026: 3). Format-wise SQ is single-flying-lap like Q (not stint-based), so the race-stint
  pipeline doesn't apply, and the Q-style estimator's flying-lap selection logic
  (`session_fit.py:fit_driver`, lines ~340-347) would plausibly work unchanged. The
  `quali_mass()` fuel assumption is also a much closer match for SQ than for FP2/FP3 (sprint
  quali is a flat-out single-lap format like quali, not a mixed practice session) — so the
  same objection that blocks FP1-3 is weaker here.
- Not tested: never invoked `load_quali_session(year, gp, "SQ", ...)` or
  `estimate_session(..., session_type="SQ")` in this excursion (read-only scope). Genuinely
  don't know if it errors, degenerates, or produces plausible numbers — hence UNKNOWN rather
  than SHOULD WORK or BLOCKED.

## Where estimates are stored (schema summary)

- `data/physics_estimates.db` → table `session_estimates`, PK
  `(year, gp_name, session_type, constructor)`. Five-view (braking/traction/power_drag/
  lateral/coast) params + sigmas + covariance JSON blobs + fit-quality metadata. Schema:
  `src/physics/layer2/estimate_store.py` (`EstimateRecord` dataclass, ~50 columns).
- `data/physics_fits.db` → table `session_fits`, PK-equivalent
  `(year, gp_name, session_type, driver)`. Single-channel per-driver fit (drag, braking,
  traction, lateral scalars). Schema: `src/physics/fit_store.py`.
- `data/race_stint_estimates.db` → table `race_stint_estimates`, PK
  `(year, gp_name, session_type, driver, stint_num, compound)`. Per-stint decay/completeness
  views. Schema: `src/physics/layer2/race_stint_store.py`.

## The single command that produces them (per store)

```
# Layer-2 five-view Q estimates (constructor-level)
py scripts/build_physics_estimates.py --seasons 2023 --refine

# Layer-1 single-channel Q fits (driver-level)
py scripts/build_physics_fit_store.py --seasons 2023 --sessions Q

# Race stint estimates (driver-level, R only — hardcoded)
py scripts/populate_race_stint_estimates.py --year 2023 \
    --db data/f1_data_2023.db --out data/race_stint_estimates.db

# Pooling/report over an existing Q store
py scripts/pool_physics_estimates.py --year 2023
```

## What was NOT tested (scoped nulls)

- Did not run any pipeline (brief is read-only). Every WORKS TODAY verdict is store-row
  evidence, not a fresh execution.
- Did not attempt FP1/FP2/FP3/SQ/S runs to see what actually happens (would violate
  read-only scope) — BLOCKED/UNKNOWN verdicts rest on code inspection + absence of stored
  output + absence of log evidence, not an observed failure.
- Did not check `docs/pipeline/` (the ideal-lap wear pipeline explainer) for physics-estimate
  coverage claims — grepped its README and found no session-type coverage claims to
  reconcile; did not read the full `bundle.json`/`explainer.html` (out of scope, that pipeline
  consumes wear/PVAT data, not `session_estimates`/`race_stint_estimates`).
- Did not audit `.agent-work/archive/` run artifacts for #509/#512 beyond what's already
  cited from `docs/architecture/packets/physics.md`; did not open every archived MISSION_FRAME
  under `.agent-work/archive/2026-06-24-510-*` etc. — time-boxed to the store+code evidence,
  which was sufficient to answer the named question.
- 2019–2021 rows were spot-checked (same query, wider `year` filter) but not written up in
  full detail in the matrix per the brief's 2022–2026 scope.
