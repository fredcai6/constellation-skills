# Crash-resume state note — cmdr-603

- **step:** execute · gate g1-collect (about to launch OS-detached collection: Austria R8 first, then Great Britain R9)
- **slug:** cmdr-603, no branch (main checkout per launch order), C:/Programs/f1Brainz
- **next command:** `powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath py -ArgumentList 'scripts/collect_evo_data.py --seasons 2026 --gp Austria --sessions FP1 FP2 FP3 Q R --report-json .agent-work/cmdr-603/collect-report-austria.json --report-md .agent-work/cmdr-603/collect-report-austria.md' -PassThru | Select-Object -ExpandProperty Id"` (dry-run superseded: script now requires --worklist for --dry-run; session sets confirmed instead via `get_weekend_sessions(2026, 'Austria'/'Great Britain')` = FP1/FP2/FP3/Q/R and FP1/SQ/S/Q/R respectively). Then repeat for `--gp "Great Britain" --sessions FP1 SQ S Q R --report-json .agent-work/cmdr-603/collect-report-gb.json` once Austria's report-json shows completion.
- **pid:** Austria (PID 1304) COMPLETE — 5/5 sessions success. Great Britain (PID 63740) RUNNING now (FP1/SQ/S/Q/R).
- **expected artifact:** .agent-work/cmdr-603/collect-report-austria.json DONE. .agent-work/cmdr-603/collect-report-gb.json IN PROGRESS.

_Updated: 2026-07-12T18:33:00Z_
