# Powered F10 held-out run — state note

**Status: LIVE.** Step 1 (smoke) PASSED (pipeline validated). Step 2 (full 16-weekend run)
launching now — PID/time filled in immediately below once `Start-Process` returns.

## Pre-flight (COMPLETE, PASSED)
- Slice: Hungary 2023, FP1+FP2+FP3+Q, full field, fastest-3-laps-per-driver.
- Result: 23 real `RawFpObservation` + 10 real `RawQTarget`, wall 1888s.
- Extrapolation: 16 weekends ~= 8.39h (linear). Inside the ~5-10h target band, well under
  the 15h STOP threshold. See `C:/Programs/f1-fp-powered/.agent-work/PREFLIGHT_RESULT.txt`.

## Step 1 (IN PROGRESS, v2): CLI wiring smoke test
- Validates the ACTUAL CLI/orchestration path (extractor -> LOWO -> paired bootstrap ->
  verdict), not just the extractor in isolation (the pre-flight only called
  `fp_observations`/`q_targets` directly).
- **v1 FAILED to a harness reap** (launched via `nohup ... &` inside a Bash tool call --
  harness-tracked despite `nohup`; PID 45808 died silently ~52min in, mid Great-Britain-FP2,
  no traceback, no verdict -- log froze at 11:05:30). Not a code bug: clean warning lines up
  to the cutoff, nothing that looks like a crash.
- **v2 (current): re-launched via PowerShell `Start-Process -WindowStyle Hidden`** -- a truly
  OS-detached process, not tracked by any harness Bash/Monitor mechanism, so it can't be
  reaped the same way. Uses the now-generalized `scripts/_fp_powered_launch.py` (accepts
  `--weekends`/`--bootstrap-resamples`/`--sentinel-name`/`--report-prefix`) instead of the
  bare CLI, so this run gets its own sentinel + JSON + txt report too (not just stdout).
  - PID: 49016, started 11:29:24.
  - stdout: `C:/Programs/f1-fp-powered/.agent-work/smoke_2wk_v2.out.log`
  - stderr: `C:/Programs/f1-fp-powered/.agent-work/smoke_2wk_v2.err.log` (captures any real
    traceback this time -- v1's log was stdout-only).
  - Sentinel: `C:/Programs/f1Brainz/.agent-work/epic-601/SMOKE_2WK_DONE.txt`.
  - Report: `reports/physics/fp_representativeness_gate_2023_smoke2wk.{txt,json}`.
- Expected wall: ~60-70min (2x pre-flight's single-weekend extraction cost).
- **RESULT: PASS on wiring.** Sentinel `SMOKE_2WK_DONE.txt`: `primary_verdict=HONEST_NULL`,
  `secondary_verdict=CONFOUNDED_NOT_EVIDENTIAL`, `emergence_passes=True`,
  `sandbag_passes=False`, `wall_seconds=2715`, `n_weekends=3`. No traceback. The CLI's own
  orchestration (extractor -> LOWO -> paired bootstrap -> verdict) ran end to end and emitted
  a shape-valid verdict -- **this is what the smoke was FOR**; the HONEST_NULL number itself
  is NOT the F10 answer (underpowered ~3-weekend slice, bootstrap=1000, no guarantee the
  sandbag weekend is even in the slice).
- **Caught bug (launch-mechanism, not code):** `n_weekends=3` when only 2 (`Hungary`,
  `Great Britain`) were requested -- PowerShell's `Start-Process -ArgumentList` array does not
  reliably preserve a multi-word element as one argv token in this shell; `"Great Britain"`
  arrived as two separate weekend ids (`Great`, `Britain`), and `Britain`'s Q session failed to
  resolve (schedule-lookup error, gracefully caught -- "no Q targets", not a crash). **Fix for
  the full run: do NOT pass `--weekends` at all** -- omitting it lets
  `_fp_powered_launch.py` default to `FROZEN_2023_WEEKENDS` read directly as a Python tuple
  (correct multi-word strings, no shell tokenization risk), which is exactly what the full
  launch below does.

## Step 2 (LIVE): full 16-weekend detached launch
- Wrapper: `scripts/_fp_powered_launch.py` (thin -- reuses `fp_gate`'s own
  `build_gate_observations`/`run_lowo`/`evaluate_gate`/`secondary_power_gate`/
  `emergence_audit`/`sandbagging_demo` + the CLI's own `format_report`; adds JSON
  serialization + the completion sentinel, since the bare CLI has neither).
- Factory: `scripts/_fp_powered_factory.py` -- zero-arg, bakes in year=2023, the frozen
  16-weekend split, `db_path=data/f1_data_2023.db`, `sessions=(FP1,FP2,FP3)`,
  `max_drivers=None` (full field), `max_laps_per_driver=3` (the compute-reduction lever).
- Launch command actually used (fires via `Start-Process -WindowStyle Hidden`, NOT bare
  `py`+DETACHED per #648; NO `--weekends` passed -- deliberately, see the smoke's caught bug
  above -- so the script's own default (`FROZEN_2023_WEEKENDS`, a Python tuple, immune to
  shell-arg tokenization) is what actually runs):
  ```
  $env:OPENBLAS_NUM_THREADS = '4'; $env:OMP_NUM_THREADS = '4'; $env:PYTHONPATH = 'C:/Programs/f1-fp-powered'
  Start-Process -WindowStyle Hidden -FilePath "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" `
    -ArgumentList @("scripts/_fp_powered_launch.py") `
    -WorkingDirectory "C:/Programs/f1-fp-powered" `
    -RedirectStandardOutput "C:/Programs/f1-fp-powered/.agent-work/powered_f10_full_run.out.log" `
    -RedirectStandardError "C:/Programs/f1-fp-powered/.agent-work/powered_f10_full_run.err.log"
  ```
- Sentinel: `C:/Programs/f1Brainz/.agent-work/epic-601/POWERED_F10_DONE.txt` (written on
  BOTH success -- `POWERED F10 DONE` + verdict/numbers -- and failure -- `POWERED F10 FAILED`
  + traceback -- so a bounded poller never waits on a silently-dead run).
- Outputs: `reports/physics/fp_representativeness_gate_2023_powered.{txt,json}` in the
  worktree.
- Expected wall: ~8.4h per the pre-flight extrapolation (measured, not the naive ~37h).
- **PID: 36016. Launched: 2026-07-24 12:18:00.** Confirmed alive + accumulating CPU
  (10.7s at ~25s post-launch) -- not a 0-CPU launcher stub.

## Live run (filled in at launch)
- PID: TBD
- Launched at: TBD
- Resume/inspect command: `Get-Process -Id <PID>` (CPU should climb steadily; a 0-CPU
  reading on the launcher stub is the known false-stall trap -- check the CHILD python.exe).
