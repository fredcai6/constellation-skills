# Crash-resume state note — commander-315-native

Refresh relaunch. A fresh Commander re-claimed the SAME session id (`commander-315-native`)
after the previous agent tripped the context HARD gate at `start execute` and idled by design.
The job file persisted; only the agent changed. `init`, `context`, `understand`, `plan` are
complete and the plan is frozen in `execute.json`.

- **step:** execute · gate `g1-implement` of `execute.json`
- **slug:** commander-315-native · branch `epic-568/c2-native-isolation` · worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`
- **next command:** `cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native && py /home/tommy/projects/constellation-skills/scripts/checklist_engine.py --file .agent-work/commander-315-native/execute.json current`
- **pid:** none yet — foreground Commander; updated per crew detach
- **expected artifact:** `.agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md`

## Plan amendment applied this session

`execute.json` was amended through the engine (`amend`, authority: Admiral, LAUNCH_ORDER
AMENDED 2026-08-13). Three frozen constraints were superseded:

1. **init.c0 deletion is AUTHORIZED**, not floated. Delete the check AND retire
   `scripts/verify_worktree_precondition_coverage.py` plus its three enumeration tests.
2. **A new origin-carrying test is an exit criterion** — `tests/test_spine_origin_isolation.py`,
   both match and mismatch. The merged `test_worktree_precondition_wiring.py` is green by
   construction and blind to the change.
3. **`scripts/mcp_spine_server.py:361`** calls `checklist_engine.main()` in-process without
   chdir — the one real cross-tree caller. Must be handled deliberately.

The withdrawn "non-forwardability" claim must not be restated. Certify coverage,
unbypassability from the spine, and an independent expected side.

## Known-in-advance

`tests/test_explorer_templates.py:342-360` goes red once the stamp lands; reconciling it is
pre-authorized. `main`'s Linux baseline is 2934 passed, 5 skipped, 0 failed.

_Updated: 2026-08-13T05:22:00Z_
