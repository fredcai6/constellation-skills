# Implementer Handoff — G1 Diagnose (evidence-only)

## Gate
g1 (execute.json `g1-implement`)

## Task
Re-measure the **current** (`main`, post-PR #548) failure population of the
per-session physics fit pipeline, and produce a diagnosis report that tells the
Commander exactly what still breaks, why, and where to fix it. **EVIDENCE-ONLY —
no committed `src/` changes.** (Temporary local instrumentation you revert before
finishing is fine; nothing under `src/` may remain modified.)

## Protected Intent
A faithful, reproducible diagnosis. The fix gate that follows depends on this being
*correct* — a wrong root cause ships the wrong fix. Do not guess; reproduce.

## Test Mode
inspection-only (diagnosis; no production code change this gate).

## Background (load-bearing)
The named failures (18 errors + 1 `no_laps` on 2023 Q) come from the **OLD** fit
store `data/physics_fits.db`, built **2026-06-23, before PR #548**. PR #548 already
hardened part of this area: flying-lap-union HP windows
(`calibrate_session_hp(..., windows=)`), an empty-speed-stream early-exit guard in
`fit_stint_hp`, and a `no_accel_samples` typed skip. **So an unknown share of the
19 cases may already be fixed.** You must re-run them on current code; do NOT trust
the OLD-store list as the current truth.

The 19 OLD-store failing cases (all 2023, session `Q`):
- **`interleaved requires n>=1; got n=0` (15):** Japan PIA, Japan NOR, Japan LEC,
  Japan SAI, Japan MAG, Netherlands SAR, Mexico ZHO, Brazil PIA, Las Vegas BOT,
  Abu Dhabi VER, Saudi Arabia DEV, Azerbaijan GAS, Azerbaijan DEV, Miami BOT,
  Canada ALB.
- **`'NoneType' object is not subscriptable` (3):** Bahrain ALO, Bahrain HAM,
  Canada HUL.
- **`no_laps` (1):** Japan SAR (already a clean typed skip — confirm it still is).

## Close Criteria (each proven with evidence in the report)
- **Per-case classification** for all 19: one of {already-fixed-ok /
  already-clean-typed-skip / still-raises-exception / genuinely-unfittable}. Show
  the actual current outcome (FitRecord.fit_status + error, or the raised
  traceback) for each.
- **`interleaved n=0` cases:** for each that still fails, establish from the data
  whether the pos and speed streams **truly overlap in time** within the chosen
  stint window (→ recoverable by widening/re-picking the window) or **genuinely do
  not overlap** (→ must skip-clean with a typed reason). Quantify the overlap (e.g.
  count of pos samples and speed samples inside `[st0, st1]`, and the time spans).
  Root-cause *why* `n=0`: which stream is empty in the window, and why
  (red-flag-shortened run? stint-window picker? stream gap?).
- **`NoneType` cases:** trace to the **exact** None-origin line (file:line) in the
  lifted smoother→adapter→estimator chain — the line that subscripts a `None`, and
  *why* that value is `None` for these sessions (the upstream producer that returned
  `None`). A traceback is required; symptom-only is not acceptable.
- **Current `FitRecord.fit_status` valid set** read from source (not the docstring):
  enumerate every status string the code can emit today; confirm/deny that
  `fit_store.py:34`'s comment (`"ok" | "error" | "no_laps"`) is stale.
- **Current failure counts by pattern** on the re-run.
- **Fix loci**: exact file:line spots a fix would touch, per pattern.

## Allowed Scope
- Read/run: `src/physics/session_fit.py`, `src/physics/fit_store.py`,
  `src/physics/fit_batch.py`, `src/preprocessing/trajectory/{calibration,loaders,
  smoother,physics_adapter}.py`, `scripts/build_physics_fit_store.py`.
- Write ONLY: `.agent-work/issue-495-fit-robustness/g1_diagnosis.md` (the report)
  and `.agent-work/issue-495-fit-robustness/g1_implementer_result.md` (your result).
  Throwaway probe scripts may live under `.agent-work/issue-495-fit-robustness/`.

## Specific Exclusions
- No `src/` edits that remain after you finish (revert any temporary instrumentation).
- No fixes — this gate only diagnoses.
- Do not delete/alter the 55 GB FastF1 cache or the telemetry store.

## Constraints
- `py` launcher (never `python`).
- `constraint:physics_region_no_evo_import` — stay in physics/preprocessing.
- Data is in THIS checkout (untracked): telemetry store
  `C:/Programs/f1Brainz/data/telemetry_store.db` (store-first source), FastF1 cache
  `data/telemetry` (fallback), OLD fit store `data/physics_fits.db`.

## Map Anchors (inbound)
- **Structural:** `session_fit.load_quali_session(year, gp, session_type,
  cache="data/telemetry", offline=True, store=None) -> (session, rho,
  rho_is_fallback)`; `session_fit.fit_driver(session, driver, *, year, gp_name,
  round_idx, session_type, constructor, rho, cfg=None) -> FitRecord` (catches
  internally → records an `error` FitRecord; to see the RAW traceback for the
  NoneType cases, call the inner chain directly or temporarily disable the broad
  except locally); `session_fit.fit_session_full(...)` is the per-session batch
  entry that derives round_idx/constructor and loops drivers — use it for faithful
  per-case repro; `calibration.interleaved(n, k, phase=...)` raises at
  `calibration.py:133`; `loaders.driver_streams(session, num) -> (pos_d, spd_d)`
  (dict-likes with keys `t,X,Y` and `t,V`).
- **Capability:** per-session physics fit; HP calibration / held-out split.
- **Constraints:** physics_region_no_evo_import; evidence-only.
- **Decision pressure (report it, don't decide):** what the enumerated typed-skip
  reason set should be; the recover-vs-skip boundary for `interleaved n=0`.
- **Map confidence flags:** `fit_store.py:34` comment is suspected stale — verify;
  current failure population is unmeasured — that's what this gate establishes.

## Required Evidence
- A reproduction transcript (command + outcome) per case, or a table.
- The NoneType traceback(s) with the exact subscripted-None line.
- Stream-overlap numbers for the `interleaved n=0` cases.
- The from-source `fit_status` enumeration.
- All folded into `g1_diagnosis.md`.

## Verification Commands
```bash
# faithful per-case repro (example shape — adapt to fit_session_full / fit_driver):
py -c "from src.physics.session_fit import load_quali_session, fit_driver; ..."
# enumerate current fit_status emissions from source:
grep -rn "fit_status\|_err(" src/physics/session_fit.py
```

## Suggested Model Tier
stronger — multi-file trace through a lifted smoother→adapter→estimator chain with
real telemetry; root-causing a NoneType and a stream-overlap edge demands care.

## Authority
Scope/recover-vs-skip philosophy already ratified by the human (problem_statement.md
decisions 1–3). You produce evidence and recommendations; you do NOT decide the fix
or write fix code — the human ratifies at the decide-fix checkpoint.

## Stop Conditions
Stop and return if: a fix would be required to produce the evidence; scope must be
exceeded; a case cannot be reproduced (report it as such with what you tried).

## Return Format
Return IMPLEMENTER_RESULT (write to
`.agent-work/issue-495-fit-robustness/g1_implementer_result.md`): diagnosis summary,
the report path, per-case classification table, NoneType root cause(s) with file:line,
interleaved recover-vs-skip determinations with overlap numbers, current failure
counts, from-source fit_status set, recommended fix loci, assumptions, stop
conditions hit, out-of-scope observations, and workflow feedback (anything in this
handoff or the workflow that made the work harder than needed).
