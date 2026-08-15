# Findings — epic-568-530 wave-2 repair

Real things learned that are outside this repair's diff. Recorded here, not in the change.

## F1 — The MCP spine door cannot reach this lane's spine (blocking, floated)

The launch order says "Spine interaction is MCP-only" and instructs me to reopen the gate I need
through MCP. That is not executable from the session I was dispatched into.

- `scripts/mcp_spine_server.py:145-146` binds `SPINE` at module import from the `SPINE_FILE`
  environment variable. `.mcp.json` defaults that variable to
  `examples/mcp-interactive-demo/spine.json`.
- My session's `mcp__spine__` door answered `spine_status` with a foreign scratch spine under
  `/home/tommy/projects/constellation-skills-wt/f-424/.../scratch-mcp/interactive-demo/`, not with
  `.agent-work/epic-568-530/spine.json`.
- This is not a misconfiguration I may repair from inside the session. It is a deliberate,
  test-pinned property: `tests/test_mcp_identity.py:914`
  `test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it` exists precisely because
  three reviewers defeated three weaker pins. `spine_open` only ever creates a spine that does not
  yet exist; it explicitly never rebinds the door.
- `mcp__spine-epic__` returns `MCP error -32000: Connection closed`.

Consequence: I could not take over the predecessor's lease, and could not attach the repair as spine
evidence. I did NOT hand-edit spine state, and I did NOT substitute the `checklist_engine.py`
CLI for the sanctioned door.

What would fix it: dispatch the resuming session with `SPINE_FILE` set to
`/home/tommy/projects/constellation-skills/.worktrees/epic-568-530/.agent-work/epic-568-530/spine.json`
and `SPINE_SESSION` set to the crew session name, so the door binds to this lane at launch.

Note the stale-path echo: the demo spine my door bound to sits under the PRE-RELOCATION
`constellation-skills-wt/` prefix named in pre-ruling 4. The stale prefix is not only in `.pyc`
files; it is still reachable through ambient MCP configuration.

## F2 — The order's note about an uncommitted `tests/test_spine_rail.py` is factually wrong

The order asked me to decide deliberately whether an uncommitted modification to
`tests/test_spine_rail.py` belongs in this lane. There is no such modification.

On arrival, `git status --porcelain` in this worktree reported exactly one line:
`?? .agent-work/epic-568-530/`. `git diff HEAD -- tests/test_spine_rail.py` was empty, and
`git stash list` was empty. The file's 93 lines of tests are already committed at `97eb5d34`
("fix(530): derive binding worktree from spine path"), which is the lane's own implementation commit
and part of the diff that was independently APPROVEd.

There was therefore no decision to make. I invented none, and I did not touch the file.

## F3 — Not a defect: the "new" failure after the reword was the guard working correctly

The first post-reword suite run showed `1 failed, 2981 passed` with
`test_episode_negative_control.py::test_canon_episode_store_untouched` asserting
"canon episode store has unstaged edits". That test requires `episodes/` to carry no unstaged edits
during a run. It was reporting my own in-flight edit, not a regression. Committing cleared it.

Worth knowing for anyone repairing an episode record: the episode store guards make the working tree
itself part of the tested surface, so an episode repair is only measurable once committed. A
mid-edit suite run over `episodes/` will always show this one failure and it should not be chased.
