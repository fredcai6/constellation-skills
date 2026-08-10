# Crash-resume state note — epic-418-followon/commander-f2

If this session dies, a fresh Commander resumes from these five lines. Do not
reconstruct state from the transcript; the engine holds it.

- **step:** execute · gate `g2-implement` (g1 CLOSED after four review passes; gate order AMENDED by Admiral ruling to g2 -> g4a -> g4b -> g3) (the identity position; first gate deliberately, per the launch order — it is the fact every later gate writes against)
- **slug:** work-id `epic-418-followon/commander-f2` · branch `epic-418/f2-mcp-adoption` · worktree `/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption` (base `abad896d`; main checkout is FENCED READ-ONLY)
- **next command:** `cd /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption && python scripts/recover_crews.py epic-418-followon/commander-f2 && python scripts/checklist_engine.py --file .agent-work/epic-418-followon/commander-f2/execute.json current` — then do exactly what the active gate's imperative says. Run the suite as `python -m pytest`, never `python3`. Never pipe a command into `head`/`tail` and read the exit code.
- **pid:** none — foreground. No detached process is running. Crews dispatch via `python scripts/run_crew.py --backend external` as Agent-tool subagents, verified with `--verify-result`; `recover_crews.py` classifies any that were in flight.
- **expected artifact:** `.agent-work/epic-418-followon/commander-f2/crew-handoffs/g2-implement-implementer-result.md`, plus `tests/test_mcp_friction_capture.py` passing. Per-gate crew results land at `.agent-work/epic-418-followon/commander-f2/crew-handoffs/<gate>-<role>-result.md` — that write is the delivery, not the crew's completion ping.

**Read before resuming:** `notes-1.md` (the #541 narrowing, the map correction, the
cold-critic triage), `.agent-work/epic-418-followon/commander-f2/execute.json` (the frozen
gate plan — never hand-edit it; use the engine's `amend`/`reopen`), and the frozen
`LAUNCH_ORDER-F2-mcp-adoption.md` in the main checkout.

_Updated: 2026-08-09T00:00:00Z_
