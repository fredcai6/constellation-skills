# Mission Frame — issue #688 (grip-fit rain exclusion too aggressive)

Map-first frame, authored from `docs/architecture/packets/physics.md` + `packets/data.md` and from
read-only measurement over `data/f1_data_{2022,2023,2024,2025}.db`. **Planning engagement only** —
this frame and `execute.json` are the deliverable; no source is modified this run.

## Intent

Recover the dry session coverage the grip pipeline currently throws away, by replacing the
`any wet sample in the session` bool with a **graded wet severity read from the signal this repo
already uses for exactly this job**, and by giving consumers **one named production selection
predicate** instead of each reinventing the rule.

The frame is NOT skipped: the run crosses the `physics → data` region boundary, changes a stored
record contract, and invalidates a frozen measured-null baseline. The map is load-bearing here.

**The issue's premise is reframed by evidence — flag this to the owner.** #688 attributes an
over-aggressive rain *exclusion* to `grip_baseline.py`. There is no exclusion there: `run_grip_batch`
stores **every** session and `rain_flag` is used only to multiply `session_offset_sigma` by a flat
4.0. The 20-of-36 weekend drop happened inside the #678 spike's own (never-committed)
candidate-weekend selection. So the defect is real but sits one level over: **no production
selection predicate exists, and the only wet signal available to a consumer that wants one is the
any-wet-sample bool.** The issue's own first-named remedy — a fraction-of-wet-*samples* threshold —
is measurably the wrong instrument (see Claims below).

## Affected Capabilities

- `capability: grip-baseline fit (module G)` — today: fits a saturating rubber-in curve per
  `(year, gp_name, session_type)` on dry clean laps, stores a curve + offset + honest sigma, flags
  rain as a bool and widens sigma 4×. This run: makes the wet signal graded, guards the
  drying-track case, and grades the widening.
- `capability: grip-record consumption / cross-weekend pooling` — today: no selection rule exists;
  the #678 spike wrote its own. This run: one named predicate + a severity filter on `GripStore.load`.
- `capability: per-session wet-lap feature derivation (data region)` — today: computes a graded
  `wet_lap_fraction` from `lap_times.compound`, populated for **races only**. This run: extends to
  every session type and repopulates.
- `capability: dry fuel-burn baseline (physics)` — **not changed**, but it is the precedent this
  run copies: a named threshold over the stored fraction, DB-mediated.

## Examples / Events

- **The recovery case.** 2022 Hungary R: 46 of 167 weather samples wet (27.5%) — and **zero** laps
  on a wet compound. A dry race the current rule flags. Same shape: 2022 Miami R, 2022 Great
  Britain R, 2023 Austria R, 2024 Hungary Q (76.2% of samples wet, not one wet lap).
- **The must-still-exclude case.** 2023 Belgium Q: **one** wet weather sample of 95 (1.1%) but
  212 of 341 laps on wet tyres (62.2%). A fraction-of-*samples* rule at any sane threshold would
  keep a soaked qualifying session. This single row is why acceptance option A is rejected.
- **The borderline case (why a threshold alone is not enough).** 2023 Monaco R at 29.3% wet laps:
  its surviving dry laps sit on a **drying** track, whose falling lap times are drying — not rubber
  accumulation. That is a direct violation of the monotone rubber-in model `_saturating()` encodes.
- **The coverage-hole case.** 2024 Canada R carries a nonzero `sessions.rainfall` count and **zero**
  rows in the `weather` table — a sample-fraction rule silently reads 0/0 and resolves to "dry".

## Structural Anchors

- `struct: src/physics/layer2/grip_baseline.py` — module leaf; `rain_flag_from_raw` :256-263,
  the two sigma-inflation sites :481-482 / :548-549, the dry-compound clean-lap filter :215,
  `MIN_STINTS_FOR_FIT` :103, `RAIN_SIGMA_INFLATION` :120.
- `struct: src/physics/layer2/grip_store.py` — `GripEstimateRecord` (frozen dataclass),
  `_migrate_missing_columns` :123-135 (additive ALTER-ADD, "Never drops or renames"),
  `load()` :155-175, `get_grip_at` :220 — the consumer seam a predicate sits beside.
- `struct: src/physics/layer2/grip_batch.py` — `run_grip_batch` :48-96; `force` governs re-fit.
- `struct: src/data/weather_features.py` — `session_wet_lap_features` :187-207,
  `populate_wet_features_for_db` :210-231 (**races-only at :224** — the coverage hole).
- `struct: src/physics/burn_rate_calibration.py` — `WET_EXCLUDE_THRESHOLD` :698,
  `session_wet_fraction` :709 — **the pattern this run copies, not a file it changes.**
- `struct: src/physics/pilot/pipeline.py` :753-781 — the live `run_grip_batch` +
  held-out-score consumer; a read/verify dependency, not a change target.

## Governing Constraints / Assumptions

- `constraint: DB-only analysis` (ORCHESTRATOR_CONTEXT §Canonical Data Constraint) — physics reads
  the **stored** wet fraction; it never recomputes compounds and never calls FastF1/Open-Meteo.
  This is what rules out computing a wet fraction inside `grip_baseline`.
- `constraint: physics→data region crossing needs an explicit design decision + doc update`
  (ORCHESTRATOR_CONTEXT §Architecture Boundaries). Satisfied by **reusing** the crossing already
  sanctioned at `packets/physics.md:2833`, plus a new decision anchor at reconcile.
- `constraint: GripEstimateRecord migration is additive-only` (`grip_store.py:130-131`) — no column
  may be dropped or renamed; every change arrives as a new nullable column.
- `constraint: thresholds and heuristics belong in named constants, not inline literals`
  (ORCHESTRATOR_CONTEXT §Planning Invariants).
- `constraint: never falsely confident` (the Protected Intent `grip_baseline.py:6-9` was built
  under, and #560's failure) — absent coverage must resolve to a **widened unknown**, never a
  silent "dry".
- `assumption: monotone rubber-in` — `_saturating()` assumes the track only gets faster as rubber
  accumulates. A drying track satisfies "gets faster" for a completely different reason; this is
  the assumption the drying-window guard exists to protect.
- `assumption: physics-model change needs truth-anchored evidence at the highest applicable L1-L4`
  (ORCHESTRATOR_CONTEXT §Evidence Requirements).

## Decision Anchors & Decision Pressure

- decision:grip-wet-severity-instrument — the wet criterion is the stored WET/INTERMEDIATE **lap** fraction, not the weather-sample fraction; severity is graded `dry | mixed | wet | unknown`, and absent coverage resolves to `unknown` (widened), never `dry`.
  @grade: settled/measured · leans g2-implement,g4-implement · settle: already settled — probe over 2022-2024 shows the sample-fraction instrument fails in both directions (2023 Belgium Q kept at 1 wet sample / 62% wet laps; 2022 Hungary R dropped at 27.5% samples / 0% wet laps)
- decision:grip-wet-thresholds — `dry` below 0.05 wet-lap fraction, `wet` at or above 0.50, `mixed` between; grip owns its own named constants seeded at the fuel subsystem's 0.05 rather than importing that module's constant.
  @grade: guess · leans g2-implement · settle: run the frozen q12 corpus — 0.05/0.50 must classify every zero-wet-lap session dry (incl. 2023 Great Britain Q at 0.013), every ≥0.6 session wet, and leave the 0.23-0.34 band mixed
- decision:grip-rain-flag-additive — `rain_flag` survives as a non-Optional bool redefined as `severity != dry`; graded fields arrive as new nullable columns.
  @grade: settled/inherited · leans g4-implement · settle: n/a — inherited from the store's additive-only migration contract
- decision:grip-selection-predicate-placement — the usable-for-pooling predicate lives beside `get_grip_at` in `grip_store.py`, as one function plus one `load()` filter argument; no policy framework, no config surface.
  @grade: settled/human · leans g4-implement
- decision:grip-sigma-inflation-graded — `RAIN_SIGMA_INFLATION` becomes severity-graded with 4.0 preserved as the full-wet ceiling and 1.0 at fully dry.
  @grade: guess · leans g3-implement · settle: OWNER CALL PENDING — isolated in its own gate so it can be dropped whole without disturbing g1/g2/g4/g5; ask the owner whether #688 stays strictly to selection
- decision pressure: whether the **drying-window** guard (fit a recovered `mixed` session only on laps after its last wet lap, falling to the thin path when that window is too short) belongs in #688 or is filed as a follow-on. Planned IN, because acceptance explicitly requires the monotone-grip assumption to survive — but it is the largest single piece of new logic here and the owner may want it split.
- decision pressure: whether a one-consumer seam is justified. The predicate ships with **no live
  consumer** (#664 is closed; #678 defers wiring). Global doctrine calls a single-adapter boundary
  "a hypothetical seam." Planned IN and kept deliberately minimal, because the known next consumer
  is #678's sharpening pass, which names this issue as coverage item 5.

## Claims / Evidence Surfaces

- `claim: the current rule is over-aggressive` — 37 of 166 timed sessions (22.3%) across 2022-2024
  carry `sessions.rainfall > 0`, and **27 of 68 weekends** have at least one flagged timed session.
  Verified by `.agent-work/issue-688/probe_rain.py` (read-only).
- `claim: the sample-fraction instrument is wrong in both directions` — the 2023 Belgium Q and
  2022 Hungary R rows above. Must become a **committed parametrized test**, not a scratch finding.
- `claim: the lap-fraction seam has no non-race coverage` — zero non-race `wet_lap_fraction` rows
  in every season 2022-2025. Verified by `.agent-work/issue-688/probe_coverage.py`. Re-confirm as
  a post-repopulate row count.
- `claim: genuinely wet running is still excluded` — the frozen 12-session must-exclude corpus
  (2022 Japan R, 2022 Great Britain Q, 2022 Canada Q, 2023 Belgium S/SQ/Q, 2024 Belgium Q,
  2023 Canada Q, 2023 Netherlands Q, 2023 Austria S, 2024 Canada R, 2022 Singapore R).
- `claim: usable coverage is recovered` — the frozen 16-session must-recover corpus.
- `claim: the #663 measured-null baseline moves honestly` — `tests/unit/physics/layer2/test_grip_heldout.py`
  is #678's frozen g4 acceptance harness. Changing which sessions fit **changes its numbers**. The
  delta must be re-run and **reported**, never silently rebaselined.

## Map Confidence / Staleness / Disputes

- `packets/physics.md` grip leaf (:1513-1520) — **current but thin**: it names the three grip
  modules and the session-level PK decision, and says nothing about the rain rule or any selection
  semantics. Plan impact: the map cannot be trusted to describe the wet behaviour, so every wet-path
  fact in this frame was re-derived from source, and a reconcile gate must add the missing semantics.
- `packets/data.md:88-93` wet-columns node — **stale on scope**: it says the wet columns are
  "Populated 2019-2026" without qualifying that this means **races only**. Measured contradiction
  recorded above. Plan impact: the doc line must be corrected as part of the run, not just extended.
- `docs/architecture/decisions/` carries **no** anchor for any wet/rain rule anywhere in the repo —
  the fuel subsystem's 0.05 threshold lives only in a docstring. Plan impact: this run files the
  first one rather than adding a second undocumented threshold.
- #678's own status is **live and contested** (its latest comment, 2026-08-01, reports V1
  reparameterization results). Plan impact: this run must not touch the fit's functional form —
  strictly coverage and selection — so the two threads cannot collide.

## Out of Scope

- Any change to the saturating curve's functional form, parameterization, or identifiability
  (#678's thread; V1/V2 reparameterization on `proto/x2-grip-sigma`).
- The `fit_status='ok'` sigma sanity bound (**#687** — a sibling coverage/quality hole, explicitly
  a different issue; do not fold it in).
- Wiring G into any live consumer (#678 defers it deliberately).
- The fuel subsystem's own `WET_EXCLUDE_THRESHOLD` and `session_wet_fraction` — read as precedent,
  never edited; grip gets its own constants.
- Backfilling missing `weather` table rows for 2024 (a real data gap surfaced here → triage, not
  this run).
- `session_surface_features.session_rain_flag` / `dry_laps_*`, owned by the heavy
  `derive_surface_features_for_event` pipeline that has not been run since 2023 → triage.
