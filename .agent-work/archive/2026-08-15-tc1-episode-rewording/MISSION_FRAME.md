# Mission Frame

**Shrunk deliberately.** No `docs/architecture` map exists in this skill-source repo (`map_orient.py
orient` returned `DEGRADED-UNPARSEABLE`, discharged at context with `ORCHESTRATOR_CONTEXT.md` +
`GLOSSARY.md` substitutes). The change is a two-statement wording restatement inside an existing,
already-designed episode store, using its one sanctioned write path
(`scripts/apply_episode_delta.py`, `restate-assertion` op — confirmed present and exercised by a
prior run's `episode-delta-restate.json`). The map would add nothing a direct read of the two
target files and the guard test does not already give. Full frame skipped; this section states
that judgement per the template's own instruction.

## Intent
Reword `tc1-windows-path-form-002.a5` and `tc1-windows-path-form-003.a5` from imperative
advice-to-a-future-reader into past-tense observations of what the `tc1-windows-path-form` run did
and found, substance preserved, via `restate-assertion` deltas only. No exception-list addition, no
deletion, no guard-file edit.

## Governing Constraints / Assumptions
- `decision:reword-not-except` — settled/human (LAUNCH_ORDER Pre-Ruling 1). Restate as observation;
  exception list not available to this lane.
- `decision:content-survives` — settled (LAUNCH_ORDER Pre-Ruling 2). Voice changes, substance
  doesn't.
- File ownership fence (LAUNCH_ORDER "File Ownership"): only the two named episode files are
  writable; the guard test, engine, spine_rail, run_crew.py, `.mcp.json`, and the four
  `tc1-worktree-identity-00*.md` episodes are out of bounds.

## Claims / Evidence Surfaces
- `tests/test_episode_observations.py` — the guard; must go green without exception-list or
  deletion.
- Full Linux suite, cache-clean, `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT` — target
  3010 passed / 6 skipped / 0 failed / 1136 subtests (LAUNCH_ORDER "Evidence required").

## Out of Scope
Everything outside the two named `a5` statements: the other assertions in both episodes, the four
`tc1-worktree-identity-00*` episodes, the guard's exception list, `scripts/checklist_engine.py`,
`tests/test_spine_origin_isolation.py`, `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`,
`.mcp.json`.
