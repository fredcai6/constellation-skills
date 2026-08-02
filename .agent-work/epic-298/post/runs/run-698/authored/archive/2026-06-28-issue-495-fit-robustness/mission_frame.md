# Mission Frame — #495 Physics fit robustness + fit-robustness dashboard

## Intent
Make the per-session physics fit pipeline robust — no raw exceptions; recover fits
where the streams genuinely overlap; record honest **typed-skip** rows where a
session can't be fit. Diagnose-first: re-measure the current failure population on
`main` (post-#548) before authoring any fix. Close with a lean real-data
**validation** (re-fit previously-failing cases + before/after accounting note).
**Dashboard DROPPED** by the user on 2026-06-28 (was: HTML+SVG fit-status
dashboard).

## Affected Capabilities
- **Per-session physics fit** (`session_fit.fit_driver`/`fit_session_full`): loads a
  quali session (telemetry-store-first, cache fallback), drives the
  preprocessing smoother/calibration, emits a `FitRecord`. Today it lets two
  exception classes escape as `error` rows. This run converts those to
  recover-or-typed-skip.
- **Batch fit-store population** (`fit_batch.run_batch` via
  `scripts/build_physics_fit_store.py`): re-run is both the validation and the
  dashboard's data source.
- **HP calibration / held-out split** (`calibration.fit_stint_hp`,
  `calibrate_session_hp`, `interleaved`, `session_offset`): the
  `interleaved n=0` raise originates here.
- **Fit evidence reporting** (`fit_evidence.py`): markdown precedent the dashboard
  extends with visuals.

## Examples / Events
- `interleaved requires n>=1; got n=0` — 15 cases on the OLD store (Japan Q
  PIA/NOR/LEC/SAI/MAG; Netherlands SAR; Mexico ZHO; Brazil PIA; Las Vegas BOT;
  Abu Dhabi VER; Saudi Arabia DEV; Azerbaijan GAS/DEV; Miami BOT; Canada ALB):
  pos/speed streams have no overlapping samples in the chosen stint window.
- `'NoneType' object is not subscriptable` — 3 cases (Bahrain Q ALO/HAM, Canada Q
  HUL): a telemetry-shape edge in the lifted smoother→adapter→estimator chain.
- `no_laps` — 1 case (Japan Q SAR): already a clean typed skip.
- **Event surface:** a `FitRecord` crossing the store boundary must carry a
  well-typed `fit_status` (a contract for downstream pooling consumers).

## Structural Anchors
- `struct:physics` → `src/physics/session_fit.py` (`fit_driver`,
  `fit_session_full`, `load_quali_session(year,gp,session_type,cache="data/telemetry",offline=True,store=None)`,
  `record_from_params`), component.
- `struct:physics` → `src/physics/fit_store.py` (`FitRecord.fit_status`, table
  `session_fits`), `src/physics/fit_batch.py` (`run_batch`),
  `src/physics/fit_evidence.py`.
- `struct:preprocessing` → `src/preprocessing/trajectory/calibration.py`
  (`interleaved` @ line 133 raises; `fit_stint_hp`, `calibrate_session_hp`,
  `session_offset`), `loaders.py` (`driver_streams`, `RawSessionStreams`),
  `smoother.py`.
- New artifact target: `reports/physics/` (committed text) + a `scripts/` generator.
- Data (untracked, in main checkout): telemetry store
  `C:/Programs/f1Brainz/data/telemetry_store.db`; FastF1 cache `data/telemetry`
  (55 GB); OLD fit store `data/physics_fits.db` (2023 Q: 421 ok / 18 error / 1
  no_laps).

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — fixes + dashboard stay in
  physics/preprocessing/scripts; **no evo-region import**.
- Physics rigor (ORCHESTRATOR_CONTEXT): truth-anchored L1–L4 where applicable;
  units/bounds/invariants explicit; **fail visibly, no hidden fallback, no
  plausible-wrong output**. A recovered fit must meet the same quality bar as any
  other; do NOT manufacture stream overlap.
- Test-led on the promoted path: focused `tests/unit/physics` +
  `tests/unit/preprocessing` region suites green; new tests for each typed-skip
  reason and each recovery path.
- `py` launcher (never `python`); archive deny-globs block `*.parquet`/binary —
  dashboard must be text (HTML+SVG), no PNG.
- Generated artifacts are derived: the **script is canonical**; the HTML is
  regenerable.

## Decision Anchors & Decision Pressure
- No existing decision anchor governs fit-robustness/typed-skip taxonomy.
- **Decision pressure (surface at decide-fix):** the enumerated **typed-skip reason
  set** (e.g. `no_laps`, `no_accel_samples`, `streams_no_overlap`, …) is a durable
  store contract future agents could rediscover/violate → record as a decision
  candidate for Cartographer reconcile.
- **Decision pressure:** the recover-vs-skip boundary for `interleaved n=0` (when is
  a window genuinely recoverable) — ratified by the human at decide-fix.

## Claims / Evidence Surfaces
- `claim` (P0): ~96% single-session success on 2023 Q — the before number; re-run
  measures the after.
- Regression surface: `tests/unit/physics/test_calibration_robustness.py` (#548)
  must stay green; extend it / add a sibling for the new paths.
- `FitRecord.fit_status` valid set — currently enforced loosely; the run must make
  the typed-skip set explicit and tested.

## Map Confidence / Staleness / Disputes
- `packets/physics.md` + `packets/preprocessing.md`: **high confidence**, freshly
  reconciled 2026-06-28 (509-w3/w4). Trust for planning.
- **Minor drift (flag, don't trust blindly):** `fit_store.py:34` comment says
  `fit_status` is `"ok" | "error" | "no_laps"` but `no_accel_samples` is already
  emitted — the typed-skip set is under-documented. The diagnosis gate verifies the
  real current set from source.
- The current failure population post-#548 is **unmeasured** → gate-1 is
  evidence-only (do not author fixes against the stale OLD-store list).

## Out of Scope
- Wiring fit diagnostics into `src/reporting/html_reports/` (region-crossing →
  triage candidate).
- Changing the fit method / capability-axis modeling (pooling, frontier fits).
- Re-deriving P0 identifiability conclusions.
- Deleting/altering the 55 GB FastF1 cache or the telemetry store.
