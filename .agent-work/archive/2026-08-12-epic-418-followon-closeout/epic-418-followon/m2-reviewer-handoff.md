# Cold reviewer handoff — M2: mechanical crew permissions + per-machine interpreter wiring

**Work id:** `epic-418-followon/m2-mechanical` · **Gate:** `g5-review` · **Role:** reviewer
**Worktree:** `/home/tommy/projects/constellation-skills-wt/m2-mechanical` (branch `epic-418/m2-mechanical`)
**Under review:** the **whole branch** against `main`@`724e6f87` — not just the last commit. Read
`IMPLEMENTER_RESULT.md`, `REWORK_RESULT.md` and `REPAIR_RESULT.md` in
`.agent-work/epic-418-followon/m2-mechanical/`.

You are **cold**. You did not plan this and you are not here to agree with it. The human's standing
ruling is that every implementer gets an independent reviewer, and it exists because two review
rounds on a sibling PR were each green through a real user-scope write.

## What the branch was supposed to do

Two jobs, both under the human's ruling *"make the mechanical things mechanical. the goal is as
little thought for running things as possible."*

1. **`scripts/run_crew.py` grants a spawned crew its tools and permission mode.** Before this, a
   crew's permissions came only from a hand-written `.claude/settings.local.json` in its worktree.
   That file was hand-written wrong once and killed two crews on arrival.
2. **`.mcp.json`'s Python interpreter resolves per machine at install time**, reusing
   `install_constellation.py`'s single `resolve_interpreter()` probe rather than a second one.

## The history you need, because it is not obvious from the diff

This branch changed direction twice, and both turns matter to your review.

- It first committed `"command": "<python-interpreter>"` — a placeholder — on the reasoning (#539)
  that a tracked file may never name an interpreter, since no name works on every platform.
- **That broke a real test.** `tests/test_mcp_spine_server.py::McpJsonVarExpansionLaunchTests::
  test_var_expansion_path_launches_a_real_server_and_answers_a_tool_call` launches a real server
  from the committed `.mcp.json`, and a placeholder is not an executable.
- The Admiral then committed `"command": "python3"` (the pre-#553 value; verified by JSON-RPC
  handshake that the door runs on stdlib under `/usr/bin/python3` here), and dispatched `g4-repair`
  to widen the wiring matcher from placeholder-only to **any bare interpreter name**.

The rule that came out of it, recorded on #539: **a tracked config that code also reads directly
cannot hold an unresolvable value.**

## Review criteria — check each, and say which you actually exercised

1. **Did a control reproduce each defect before its fix?** There are three: the permission grant
   (`g1`), the installer never wiring (`g3-rework`), and the placeholder-only matcher (`g4-repair`).
   Re-run them. A command that fails for the wrong reason looks exactly like a guard working — that
   error has already been made once in this epic.
2. **Is `.mcp.json` launchable exactly as committed?** Launch a real server from it and complete an
   `initialize` handshake. This is the defect the whole repair exists for; do not take it on faith.
3. **Does the widened matcher leave a pinned absolute path alone?** A caller who wrote
   `/usr/bin/python3.12` meant it, and stomping that is worse than the bug being fixed. Try an
   absolute path, a relative path with a separator, and a non-Python program name.
4. **Is the predicate defined once?** `wire_mcp_interpreter.py` must alias it from
   `install_constellation.py` by reference. A second copy is the drift this epic exists to stop.
5. **Does the installer actually wire on a real run, and hard-stop when nothing probes?** #539's
   governing requirement is *fail loudly, never silently serve a platform you cannot serve*. Check
   there is no half-written `.mcp.json` on the failure path. Run the installer **as a module from
   the repo root** (`python -m scripts.install_constellation`) — as a copied single file it exits 2
   before reaching any guard, which has already produced one false "the guard worked" result.
6. **Does the crew tool grant actually grant what a crew needs, and nothing gratuitous?** Read
   `CREW_ALLOWED_TOOLS` and `DEFAULT_CREW_PERMISSION_MODE` and judge them. Note for context: the
   human has ruled that the launcher should eventually grant the **door** and withhold the **engine
   CLI**. That is #559's work, **not** this branch's — finding it is fine, blocking on it is not.
7. **Were the hard no-gos respected?** `checklist_engine.py::claim` semantics unmodified;
   `_identity_violation` and the `from_child` path confinement in `mcp_spine_server.py` not
   weakened; `settings.json` untouched; `docs/agents/*` changed only by the merge of M3, which is
   already reviewed and merged; no push to `main`.
8. **Do the new tests fail without the change?** Revert each production hunk in a scratch copy and
   confirm red. A test that passes both ways is not evidence.
9. **Full suite**, with real counts:
   `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
   Unset those three or you inherit the dispatch's spine binding into the suite. Use `python`, not
   `python3` — `/usr/bin/python3` here has no pytest.

## Drive your spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` for you automatically. **Use the
`mcp__spine__*` tools, not the engine CLI** — find them with `ToolSearch`. The human's standing
ruling: *"anything that we want to do for the spine needs to be accessible via mcp. the agents
should not know about the cli. period."*

If a spine verb you need is missing from the door, **say so in your result**. Five are known missing
(`skip`, `reopen`, `append`, `amend`, `flag-candidate`) and #559 is scoped to close them; a sixth
would be news. If `mcp__spine__spine_status` returns a spine that is not yours, stop and say so.

## What is explicitly NOT in scope

Windows launch (#553/#539, ruled: hardcoding for this host is allowed, and it is recorded on #539);
removing the CLI from agent instruction (#559, next wave); `--wire-hooks` (#560). Finding them is
fine; blocking on them is not.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. **An honest partial is acceptable and a
silent gap is not** — say which criteria you exercised and which you only read. If you approve
something you did not test, say that too.

Write your verdict to `.agent-work/epic-418-followon/m2-mechanical/REVIEWER_RESULT.md`, including
its Workflow Feedback section, before ending your turn — that write is the delivery.
