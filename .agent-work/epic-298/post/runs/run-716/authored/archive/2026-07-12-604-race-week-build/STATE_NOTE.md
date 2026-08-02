# Crash-resume state note — 604-race-week-build

- **step:** execute · gate g3-proof (in-progress) — G1 and G2 both complete+integrated (74/74 tests green); running the R9 Great Britain e2e proof now
- **slug:** 604-race-week-build, branch feat/604-race-week-build, worktree C:/Programs/f1Brainz/.claude/worktrees/604-build
- **next command:** `cd C:/Programs/f1Brainz/.claude/worktrees/604-build && py scripts/race_week.py run --year 2026 --race "Great Britain" --db-path C:/Programs/f1Brainz/data/f1_data_2026.db --manifest params/gold/sampled_runtime_manifest.json --compound-prior-root params/gold/compound_prior --lane balanced` (already launched, background task bp694s66r) — if it died, re-run this exact command
- **pid:** background bash task id bp694s66r (harness-tracked, not a raw OS PID)
- **expected artifact:** outputs/race_week/2026/9/{01_sessions,02_prediction,03_lineup}.json + 04_explainer.md in the worktree

_Updated: 2026-07-12T22:30:00+00:00_
