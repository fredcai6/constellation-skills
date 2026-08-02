# Implementer Handoff

## Gate
g1 (g1-implement)

## Task
Build a read-only telemetry-instrument characterization script at
`scripts/characterize_telemetry_instruments.py` that, over a documented set of
**>=6 FastF1 sessions spanning >=2 seasons** (2022-2025 deep cache; mix race + quali +
**>=1 wet or red-flagged session**), loads RAW per-driver streams ONLY and measures, PER
STREAM, the instrument characteristics below. Emit per-session JSON to
`.agent-work/issue-447/evidence/`.

## Protected Intent
This produces the empirical instrument numbers that feed the epic's GO/NO-GO on whether
FastF1 telemetry is correlatable enough for trajectory estimation. Numbers must be real,
reproducible, and traceable to a script + session — they go straight into a human decision
brief. No estimator, no filtering — characterization only.

## Test Mode
Inspection-only for the analysis script itself (it is a `scripts/` measurement tool, not a
shipping `src/` module), BUT: the script must RUN end-to-end on the real cache and produce
real numbers — "it runs and the numbers are on disk" is the evidence. If you add any helper
under `src/preprocessing/`, that needs a unit test (test-after allowed). Prefer keeping it
all in `scripts/` for this gate.

## Close Criteria
- `scripts/characterize_telemetry_instruments.py` exists, is read-only, imports the 0a
  `offline_loader` for raw streams, and runs on the real offline cache.
- Per-session JSON written under `.agent-work/issue-447/evidence/` (one file per session,
  names containing `char`), so a continuation can resume. Each carries the measured numbers.
- A summary JSON or table aggregating across sessions.
- For EACH stream (`car_data`, `pos_data`), per session, you have measured:
  1. **Sampling-interval distribution**: median dt, IQR / percentiles, max gap, dropout
     rate, and a per-`Source` breakdown (the Source column tags which subsystem emitted
     each batch — pos vs car vs interpolated; report the mix).
  2. **Position quantization step**: the least-significant increment of X / Y / Z (the GCD
     or modal diff of sorted unique values), reported in **decimetres AND metres**.
  3. **Z-channel quality verdict**: range, variance, fraction-constant, plausibility vs a
     near-flat-track expectation; a one-line PASS/MARGINAL/UNUSABLE verdict per session.
  4. **Per-channel noise covariance**: for the smooth channels (Speed, X, Y, Z), the
     residual variance against a LOCAL smooth fit (e.g. low-order Savitzky-Golay or rolling
     polynomial) over straight/steady segments — i.e. the measurement noise, not the
     dynamics. Report per channel, with units.
- Session selection and its rationale documented (in a module docstring + the summary).

## Allowed Scope
- `scripts/characterize_telemetry_instruments.py` (new).
- `.agent-work/issue-447/evidence/*.json` (outputs).
- Read-only reuse of `src/preprocessing/trajectory_grading/offline_loader.py`.
- OPTIONAL: a small read-only helper in `src/preprocessing/` IF genuinely reusable across
  gates — with a unit test and `py -m src.utils.simplification_limits` on it. Otherwise
  keep everything in `scripts/`.

## Specific Exclusions
- NO `get_telemetry()` / merged/interpolated product (raw `car_data`/`pos_data` only).
- NO network fetch (offline cache only; a cache miss must raise, not fetch).
- NO estimator / filter / smoother as a deliverable (a local smooth fit purely to MEASURE
  residual noise is fine; it is not an output).
- NO evo imports; NO DB writes; do not touch evo or data-collection code.
- Do NOT decide GO/NO-GO.

## Constraints
- Raw streams only via `offline_loader.load_session_offline`; offline cache at
  `C:/Programs/f1Brainz/outputs/cache` (untracked, in the MAIN checkout — absolute path).
- **pos_data X/Y/Z are in DECIMETRES** — multiply by 0.1 for metres. Report both.
- Analysis code in `scripts/` (pre-ruling 5). Read-only.
- `py` not `python`. Set `PYTHONUTF8=1` / utf-8 in any subprocess env you capture.
- Long compute runs FOREGROUND (never background a `-p` task).
- Season DBs for any sector/lap truth: open `file:<path>?mode=ro` sqlite, NOT
  DatabaseManager (it writes on init). DBs at `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- DB GP naming is "Belgium" while FastF1 says "Belgian Grand Prix" — the 0a
  `db_truth_loader` handles the mapping; check before assuming a new session resolves.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` (`src/preprocessing/trajectory_grading/`, physics
  region); `scripts/` (non-map analysis).
- **Capability:** instrument characterization upstream of trajectory grading.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; offline-cache +
  raw-streams sanctioned exception (telemetry is NOT in the DB).
- **Decision anchors:** 0a established cross-residual is a diagnostic, not a gate; this
  characterization feeds gate calibration downstream (do not re-litigate).
- **Evidence expectations:** sampling-interval distributions, quantization steps, Z verdict,
  per-channel covariances — every number traceable to script + session.

## Suggested Session Set (you may adjust within pre-ruling 6; document any change)
- 2023 Belgian GP Q and R (Spa — used by 0a; lets you cross-check decimetre scaling).
- 2022 Spanish GP R (used by 0a).
- A 2024 dry race + quali at a different circuit (e.g. 2024 Bahrain or Italy).
- **>=1 messy session**: a known WET or red-flagged session (e.g. 2023 Dutch GP / a 2024
  wet quali) — instrument pathologies hide in messy sessions. Confirm it is cached first.
- Aim for >=6 sessions, >=2 seasons. Verify each is cached (offline_loader raises if not);
  if a chosen session is not cached, swap it and note the swap.

## Required Evidence
- The per-session JSON files on disk + an aggregate summary.
- Captured stdout of one full run showing the script executing against the real cache.
- A short note confirming raw-streams-only (grep your own script for `get_telemetry` → none)
  and the decimetre handling.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
py scripts/characterize_telemetry_instruments.py   # or its documented invocation
py -c "import glob; print(glob.glob('.agent-work/issue-447/evidence/*char*'))"
# if any src/ touched:
py -m src.utils.simplification_limits src/preprocessing/<file>
```

## Authority
Session selection within pre-ruling 6, statistical method for each measurement, and output
JSON shape are YOURS to decide — document them. You must NOT: decide GO/NO-GO, build an
estimator, cross into evo/data regions, or use `get_telemetry`.

## Stop Conditions
Stop and return if: the cache lacks raw per-stream data for the required session spread
(report what IS there); a required measurement is impossible to produce; allowed scope must
be exceeded; a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, evidence produced (list the JSON
paths + headline numbers per stream), session set used + rationale, assumptions, any stop
conditions hit, out-of-scope observations, and workflow feedback (what in this handoff or
the workflow made the work harder than needed).
