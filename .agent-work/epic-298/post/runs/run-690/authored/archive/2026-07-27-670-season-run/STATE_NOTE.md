# Crash-resume state note — 670-season-run

- **step:** execute · gate g2-run (detached season compute IN FLIGHT, RELAUNCH after G1 rework added per-round fault isolation). Full 2023 season (22 rounds × per-round 20-driver grid), OFFLINE. Expected: rounds 1-2 PARK (no strictly-prior data for E's car ceiling); rounds 3-22 run.
- **slug:** work-id=670-season-run · branch=epic659/670-season-run · worktree=C:/Programs/f1brainz-wt/epic659-670
- **next command:** if resuming after a crash: check `.agent-work/670-season-run/artifacts/season_results.json`. If present → completed; verify with `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/verify_season_artifacts_670.py` then advance g2-run. If absent and PID (see season_run.pid) dead → relaunch: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/run_season_670.py --year 2023 --budget-s 900 --out-dir .agent-work/670-season-run/artifacts` (detached, Start-Process -WindowStyle Hidden). The runner now isolates per-round failures (parks, never crashes the season), and the shared refutil accumulates idempotently.
- **pid:** SEE .agent-work/670-season-run/artifacts/season_run.pid (rewritten at each launch)
- **expected artifact:** `.agent-work/670-season-run/artifacts/season_results.json` (final; signals completion) + `artifacts/scratch/refutil_season_2023.db` (consolidated slice, grows per covered round). Logs: `artifacts/season_run.out.log` / `.err.log`.

_Updated: 2026-07-27 (g2 relaunch, post per-round-isolation fix)_
