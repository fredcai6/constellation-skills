# REVIEW_RESULT — g3 (parallelize the three training loops)

Verdict: **APPROVE**

## Independent verification
- Byte-identity by construction: all 3 builders verified field-by-field vs HEAD originals.
  - Main: module order, key=module_name, identical backtest fields incl retro_root.
  - LOSO: _iter_loso_units is single source of order (sorted-heldout-outer, module-inner), shared by builder AND
    consumer; assembled via zip(units, results); no retro_root. run_jobs returns input-order results.
  - Calibration: module-outer, eval_year=fit_prediction_years[-1], one template PER prediction year.
- CALIBRATION EQUIVALENCE (scrutinized): calibration_fit_split returns [] or [fit_years[-1]] — structurally never
  length>1; AND builder carries all prediction years. No silent output change.
- _finalize_and_write_reports byte-identical to HEAD inline tail (same validate/write order, same return dict). Pure extraction.
- Picklable: worker module-level; job carries only Namespaces of scalars/lists + str key; module imports stdlib-only
  (AST-verified), heavy/circular `run` import deferred into worker; pickle round-trip passes.
- background -> _run_in_process (n_workers<=1); guard test patches ProcessPoolExecutor to raise, LOSO still passes.
- Logging: no print; on_complete completed-count + wall-clock ETA; summary lines preserved.
- Simplification: --paths -> only pre-existing untouched _gold_preflight_coverage (CC=21/114); parallel_jobs.py +
  runner.py pass; _collect_loso_fusion_train_rows now UNDER limits. NO NEW violation.
- `py -m pytest` on the 3 files -> 40 passed. Exclusions (sampled backtest, scripts, schema) untouched.

## Blockers
None.

## Out-of-scope observations
- docs/architecture/index.md should gain a gold_cycle parallelism entry for parallel_jobs.py + the 3 public
  job-builders -> reconcile/closeout scope (cartographer step), not a blocker.
- _gold_preflight_coverage pre-existing over-limit -> aligns with tc1 decomposition follow-up.
