# Crash-resume state note — epic-418-followon/commander-424

**Continuation run under `LAUNCH_ORDER-424-continuation.md` (repair `w1-f424-repair`).** Gate order is
**g3 → resolve g1-integrate → g2 → g4**. Both leases are claimed by the session below.

- **step:** execute · gate `g1-integrate` **[blocked]**. g3's implementer has **returned** (result on
  disk, verified fresh, suite `0 failed`) and answered DC3 **YES, measured**. The **next action is the
  `g1` rework loop** that clears the blocker: implementer attempt-2 removes
  `scripts/gen_mcp_config.py`, then reviewer attempt-2 re-reviews, then
  `resume g1-integrate` + `advance`.
- **slug:** epic-418-followon/commander-424 · branch `epic-418/f-424-mcp-door` · worktree
  `/home/tommy/projects/constellation-skills-wt/f-424` · PR #533
- **session / lease:** `86708414-f5d3-40d3-8c9a-2f96d1ccdc14` (active on `spine.json` **and**
  `execute.json`)
- **next command:**
  `cd /home/tommy/projects/constellation-skills-wt/f-424 && python3 /home/tommy/projects/constellation-skills/scripts/checklist_engine.py --file .agent-work/epic-418-followon/commander-424/execute.json current`
  then dispatch the g3 implementer through `run_crew.py --dispatch external` with
  `crew-handoffs/g3-implementer-handoff.md`.
- **pid:** none — the crew is an in-context Agent-tool subagent (backend `external`), not a detached
  process.
- **expected artifact:** `crew-handoffs/g1-implementer-result-rework.md`, then
  `crew-handoffs/g1-reviewer-result-rework.md` with verdict `APPROVE`.

## The g1 decision is MADE — do not reopen it, execute it

`scripts/gen_mcp_config.py` is being **removed as unnecessary**, on two reproduced measurements:

- **M1** a committed project-scope `.mcp.json` with `${VAR}` expansion already gives per-dispatch
  identity from the caller's environment (two dispatches, one directory, no generated file, each
  returned its own nonce; server-side call logs agree). Evidence:
  `evidence/g1-resolve-varexp/`.
- **M2** (g3) an in-session Task-tool subagent inherits its dispatching process's MCP scope wholesale.
  This was the last hypothesis for keeping generation, and it **does not** survive: a generated config
  is also bound at server launch, per process, so it cannot give an in-session subagent its own
  identity either. M2 names a case **neither** mechanism solves, so it does not distinguish them.

Removal is a fully acceptable outcome under the launch order, and the reviewer was **not** overridden
— the BLOCK is being resolved on evidence, through the gate's own rework path.

## Suite baseline: green, not pinned-red

`python -m pytest -q tests` on this tree = `2163 passed, 1 skipped, 1061 subtests passed`. The old
six-failure pin is retired (#531 merged; branch merged origin/main at `05b35a2e`). The gate is
`0 failed`.

## The one question that unblocks `g1-integrate`

Does an in-session Task-tool subagent share its parent's already-launched MCP server? YES ⇒ `${VAR}`
expansion cannot reach that case and `scripts/gen_mcp_config.py` is justified. NO ⇒ generation is
redundant and the committed `.mcp.json` `${VAR}` path is the whole answer, and removing the script is
a fully acceptable outcome. **That question is DC3, and its evidence is gate `g3`.**

`g1-integrate` is blocked **by its own reviewer, not waived**. Do not override the reviewer; resolve
it on g3's evidence.

## Known tooling defect (worked around, not fixed — outside the file fence)

`run_crew.py --verify-result` / `--resume` cannot resolve a **multi-segment** work-id:
`load_registry_for_resume()` takes `session.split("/")[1]` as the whole work id, so
`constellation/epic-418-followon/commander-424/...` resolves to `.agent-work/epic-418-followon/` and
refuses with "no crew recorded". Worked around with an untracked read-side symlink
`.agent-work/epic-418-followon/crew-runs.json -> commander-424/crew-runs.json` (writes still go to
the correct path via `entry["work_id"]`). This is why the two `g1` entries sat `running` with their
results on disk. Logged as a triage candidate; **not** fixed here (`run_crew.py` lives outside this
run's file fence).

_Updated: 2026-08-09T20:55:00+00:00_
