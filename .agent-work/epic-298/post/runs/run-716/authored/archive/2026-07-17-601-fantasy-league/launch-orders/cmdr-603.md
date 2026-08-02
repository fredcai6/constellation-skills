# Launch Order: cmdr-603 — #603 data catch-up (Austria R8 + Great Britain R9)

## Mission
Issue #603 (epic #601, Track 1). `data/f1_data_2026.db` has classifications only through R7 (Barcelona-Catalunya). Collect **Austria R8 (2026-06-28)** and **Great Britain R9 (2026-07-05, SPRINT weekend — SQ/Sprint sessions in scope)** into the canonical 2026 DB via the standard collector, then verify. This unblocks the Belgium R10 (2026-07-19) prediction. Deliverable = R8+R9 sessions present and spot-checked; a verification report.

## Prior-Wave Verdicts (pasted)
None — Wave 1.

## Pre-Rulings
Each overridable if evidence contradicts — say so when overriding.
- **You run in the MAIN checkout `C:/Programs/f1Brainz/`, NOT a worktree** — collection writes the canonical DB (single source of truth), and worktree DB copies are the stale committed-small versions. You are therefore **EXEMPT from `verify_worktree_isolation.py`** (it would fail by design in the main checkout); note this exemption in your report instead of running it.
- **Do NOT commit any `data/*.db`.** The tracked DBs are bloated to 550MB–2.3GB in the working tree (telemetry swell = issue #608's debt, out of scope here). Your deliverable is data PRESENT + VERIFIED in the canonical local store, not a commit. **Do not `git add` anything under `data/`.** If you believe a code fix is needed (e.g. a round-mapping bug), STOP and float — that would be a branch+PR, not a main-checkout commit (main-branch commits are forbidden by policy).
- **Collect WITHOUT `--include-telemetry`** (default). Classifications + laps are what the fantasy/decision-metric path needs; telemetry only feeds physics and would grow the swell. Float if you find a concrete downstream need for R8/R9 telemetry.
- **Launch the collection OS-DETACHED, not as a harness-tracked background job.** Use PowerShell `Start-Process -WindowStyle Hidden` (survives your subagent idling); a harness-tracked `&`/background Bash dies when you go idle and strands the run. **Rewrite your own STATE_NOTE (`.agent-work/601-fantasy-league/cmdr-603-STATE_NOTE.md`) with the detached PID + the collector `--report-json` path BEFORE launching.** Then poll the report JSON / DB for completion. `collect_evo_data.py` is idempotent (skips already-present sessions) and rate-limit aware (55s inter-session delay; waits 20 min on a "500 calls/h" error), so it is safe to relaunch/resume.
- **Targeted collection.** There is no `--rounds` arg; use `--gp` to restrict to one GP. Verify the exact FastF1 GP-name strings first (a dry run: `py scripts/collect_evo_data.py --seasons 2026 --dry-run` shows the worklist), then collect Austria and Great Britain. Include the sprint session types for R9 (verify the actual 2026 GB session set — likely FP1, Sprint Qualifying, Sprint, Qualifying, Race).
- **Verify round mapping on ingest:** 2026 dropped Bahrain/Saudi; FastF1 reindexes (Miami=R4, confirmed in the DB). Confirm Austria lands as R8 and Great Britain as R9 — not shifted.
- **Post-run verification (the real deliverable):** `has_session_classification(2026, 8, <type>)` and `(2026, 9, <type>)` for every session type collected; FP positions are derived from best lap time (FastF1 gives Position=NaN in FP results) — confirm they are populated, not null. Spot-check a handful of R8 and R9 finishing positions against published results (you know 2026 results from general knowledge; sanity-check the winner/podium at least).
- **Parquet mirror:** if the telemetry/Parquet mirror backfill is part of the standard path and applies to classifications/laps, note whether it needs running for R8/R9; if it only mirrors telemetry (which you are not collecting), say so. Float if the mirror step is ambiguous rather than guessing.

## Honest-Null Clause
If a session genuinely is not yet available from FastF1/Jolpica (data not published), that is a complete, honestly-reported result — record which sessions are missing and why, do not fabricate. Report partial success precisely.

## Inherited Latitude
You MAY: run collection, read/verify the DB, write your report. You MUST FLOAT: any `data/` commit, any code change (round-mapping fix etc.), closing the issue (Admiral surfaces close to the human), anything needing telemetry. Report up; you cannot reach the human.

## File Ownership
Sole writer this wave of: the canonical `data/f1_data_2026.db` (via the collector) and your report/state files under `.agent-work/601-fantasy-league/`. Do NOT touch `AGENTS.md`, `CLAUDE.md`, or anything in the two sibling worktrees.

## Workspace
**Main checkout: `C:/Programs/f1Brainz/`.** No worktree (see pre-rulings). Do not create a branch unless a floated code fix is approved. Set your cwd to the main checkout for all collector runs (the collector resolves DB paths relative to the repo root).

## Inherited Context
- **Python is `py`, never `python`** (Python 3.14).
- Collector: `scripts/collect_evo_data.py` — timestamps every line; rate-limit detection waits 20 min; `INTER_SESSION_DELAY=55s`. Args: `--seasons`, `--sessions`, `--gp`, `--force`, `--allow-partial`, `--max-failures`, `--dry-run`, `--report-json`, `--report-md`, `--worklist`. FP-position fix derives position from `session.laps` best lap.
- DB API (`src/data/database.py`): `has_session_classification(year, round, session_type) -> bool`, `get_session_classification(year, round, session_type) -> {driver_id: position}`.
- **Never commit `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md`.**
- Untracked-data lesson: DBs/cache live in the main checkout; you are already there, so use repo-relative paths as the collector expects.
- **Windows shell:** you are on PowerShell for `Start-Process`; the Bash tool is also available. For the detached launch use PowerShell `Start-Process -WindowStyle Hidden -FilePath py -ArgumentList '...'` and capture the returned process Id.

## Pre-empted Steps
Intent + scope + collection method established here. Run your commander spine but you may cite this order rather than re-interrogating intent. The state-note discipline is yours to keep current across the detached launch.

## Data Locations
- Canonical 2026 DB: `C:/Programs/f1Brainz/data/f1_data_2026.db` (currently R1–R7).
- FastF1 cache: main-checkout `outputs/cache` (untracked). Collection is the ONE place live FastF1/Jolpica calls are sanctioned.
- Collector report JSON default: whatever `--report-json` resolves to (check `REPORT_JSON_PATH` in the script); pass an explicit `--report-json .agent-work/601-fantasy-league/cmdr-603-collect-report.json` so completion is easy to poll.

## Budget
- **Model tier:** Sonnet.
- Compute/time: the collection may run 15–60+ min with rate limits — that is why it is OS-detached + polled. Do not block a single foreground call on it.

## Stop Conditions
Stop and return when: R8+R9 collected (or honestly reported as partially/not available) AND verified AND the report is written; OR you need a `data/` commit or code change (float); OR collection stalls in a way the resumable/idempotent relaunch cannot fix (float with the collector report + DB state so the Admiral can recover the detached run).

## Return Shape
Final report (`.agent-work/601-fantasy-league/cmdr-603-report.md`; post verdict before idle): verdict (DONE/PARTIAL/BLOCKED), a per-session-type table for R8 and R9 showing `has_session_classification` = present/absent, the round-mapping confirmation (Austria=R8, GB=R9), spot-check results vs published podiums, the detached collection PID + report-JSON path, whether the Parquet mirror needs action, the worktree-isolation EXEMPTION note (why you ran in main checkout), triage candidates, workflow feedback, and proposed lessons-delta (do not apply). Deliver the artifact before going idle — an idle notification with no artifact reads as stalled, not done.
