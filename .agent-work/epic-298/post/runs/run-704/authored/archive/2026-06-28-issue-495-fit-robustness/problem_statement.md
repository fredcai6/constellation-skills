# Problem Statement — #495 Physics fit robustness (+ fit-robustness dashboard)

## Capability being changed

The **per-session physics fit pipeline** (`src/physics/session_fit.py` driving
`src/preprocessing/trajectory/calibration.py`) currently aborts ~4% of
single-session fits with raw exceptions instead of either recovering them or
recording an honest typed skip. This run makes that pipeline **robust** (no raw
crashes; recover where physically sound; clean typed-skip otherwise) and adds a
**reproducible visual dashboard** of the fit-success/failure landscape.

## Origin and current-state caveat (load-bearing)

- The named failures (18 errors + 1 `no_laps`, ~96% success) were measured on the
  **OLD** `data/physics_fits.db` before PR #548. **PR #548 (509-w3, the "#495
  cluster") already hardened part of this area**: flying-lap-union HP calibration
  windows (`calibrate_session_hp(..., windows=)`), an empty-speed-stream early-exit
  guard in `fit_stint_hp`, and a `no_accel_samples` typed skip.
- Therefore the *current* failure population on `main` is **unknown** and must be
  re-measured before any fix is planned. Two patterns are still live in code:
  `interleaved requires n>=1; got n=0` (`calibration.py:133`) and the
  `'NoneType' object is not subscriptable` edge (3 cases: ALO/HAM Bahrain, HUL
  Canada).

## Resolved decisions (human-confirmed 2026-06-28)

1. **Success bar.** Re-measure current failures first; then **fix real bugs and
   recover fits only where physically sound; convert genuinely-unfittable sessions
   to clean typed-skip rows** (no crashes, honest accounting). NOT "force 100%" —
   forcing a fit from sparse/non-overlapping data would poison the cross-session
   pool.
2. **Recover-vs-skip philosophy** (physics doctrine: fail visibly, no hidden
   fallback, no plausible-wrong output):
   - `NoneType` edge → **bug, fix it**.
   - `interleaved n=0` → **recover where pos/speed streams truly overlap** (widen /
     re-pick the window); where they genuinely don't, **skip-clean with a typed
     reason**. A recovered fit must meet the same fit-quality bar — no second-class
     fits enter the pool.
3. **Diagnose-first.** Gate-1 is **evidence-only**: reproduce the failing sessions
   on current `main`, classify each (already-fixed / real-bug / genuinely-
   unfittable), locate exact fix loci. Then a **decide-fix human checkpoint** before
   any fix code; freeze the fix gates from that evidence.
4. **Dashboard — DROPPED** (human reversed 2026-06-28: "nix the dashboard on
   second thought"). Replaced by a **lean real-data validation** (G3): re-fit the
   previously-failing cases on the fixed code, confirm recover-or-typed-skip,
   no-regression spot-check on previously-ok fits, and a short markdown before/after
   accounting note under `reports/physics/`. No HTML/SVG/PNG. (The standalone vs
   `html_reports` integration question is moot now; a future dashboard would be a
   fresh triage item.)

## Affected map anchors

- `struct:physics` → `session_fit.py` (`fit_driver`, `fit_session_full`,
  `load_quali_session`, `record_from_params`), `fit_store.py`
  (`FitRecord.fit_status` sentinels), `fit_batch.py` (`run_batch`),
  `fit_evidence.py` (dashboard precedent).
- `struct:preprocessing` → `trajectory/calibration.py` (`interleaved`,
  `fit_stint_hp`, `calibrate_session_hp`, `session_offset`), `trajectory/loaders.py`
  (stream loading), `trajectory/smoother.py`.
- Edges: `physics → preprocessing`, `physics → data` (telemetry store first),
  `physics → utils`. Constraint: `physics_region_no_evo_import`.

## Out of scope

- Wiring fit diagnostics into the live `html_reports` dashboard (region-crossing;
  triage candidate).
- Changing the fit *method* / capability-axis modeling (pooling, frontier fits) —
  this is robustness + accounting + visualization only.
- Re-deriving braking/aero/ceiling identifiability conclusions from P0.

## Evidence bar (physics region: rigorous)

Truth-anchored L1–L4 where applicable; units/bounds/invariants explicit; focused
`py -m pytest tests/unit/physics` + `tests/unit/preprocessing` region suites green;
typed-skip reasons enumerated and tested; recovered fits validated to the same
quality bar; dashboard regenerable from a committed script.
