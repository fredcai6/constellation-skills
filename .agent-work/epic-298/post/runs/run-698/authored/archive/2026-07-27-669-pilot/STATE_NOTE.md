# Crash-resume state note — 669-pilot

- **step:** execute · gate g3-run (running the 3-circuit pilot offline, detached)
- **slug:** 669-pilot · branch epic659/669-pilot · worktree C:/Programs/f1brainz-wt/epic659-669
- **next command:** C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/run_pilot_669.py --circuits Monaco Belgium "Great Britain" --out-dir .agent-work/669-pilot/artifacts (then verify_pilot_results_669.py on the results JSON; if partial, resume with the missing circuits — pipeline is idempotent/resumable)
- **pid:** see .agent-work/669-pilot/artifacts/run.pid (detached background)
- **expected artifact:** .agent-work/669-pilot/artifacts/pilot_results.json (3 circuits) + docs/physics/pilot_669_report.md

_Updated: 2026-07-26T02:00:00Z_
