## Summary

PENDING — this PR delivers half of the lane's two-issue mission and floats the rest.

- **#595 (Stop hook vs context-trip advisory authority): delivered.** `scripts/hooks/spine_rail.py`'s Stop-hook refusal (`_mid_flight_reason`) now states explicitly that the Stop hook outranks the context-trip advisory, and names `spine_halt block` as the sanctioned mid-run exit. `skills/commander/references/crew-dispatch.md` states the same precedence next to its existing `spine_halt block` guidance. Net-deletion: the old duplicated "don't stop" phrasing was trimmed, not just grown around.
- **#442 (RAIL banner + HARD refusal readability): not delivered — fenced out.** Both problem instances (the `RAIL:` banner text and the HARD refusal's `attach ... refresh-request` remedy string) are authored in `scripts/checklist_engine.py`, which this wave's launch order fences to a concurrent lane (Lane A, #559) and which the file itself marks FROZEN/verbatim (a measurement precondition for #145). This lane's sole-owned file contains none of that text. Floated to the Admiral per the launch order's own anticipated-collision clause; recorded as triage candidates and a `blocks_current_wave_exit` discrepancy rather than guessed past.

Full account: `RETURN.md` and `notes-c.md` at the worktree root.

## Test plan
- [x] Implementer + independent reviewer crew cycle on the diff (`.agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-{implementer,reviewer}-result.md`), reviewer re-verified diff/parse/exclusions/trigger-condition independently.
- [x] Fresh-process validation: new OS subprocess, `CLAUDE_PROJECT_DIR` set to this worktree, synthetic mid-flight fixture — confirmed new wording renders (in-session observation does not count per #269).
- [x] `python3 -c "import ast; ast.parse(...)"` on `scripts/hooks/spine_rail.py` — parses.
- [ ] Cold-agent measurement of #442's rewrite — not applicable; no rewrite exists to measure (see above).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_016uJF7RrPLJwEy9PLwf9bGz
