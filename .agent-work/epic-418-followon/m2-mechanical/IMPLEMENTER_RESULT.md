# Implementation Result

## Assigned gate
`epic-418-followon/m2-mechanical` — "make the mechanical things mechanical" (Job 1: launcher grants crew permissions; Job 2: no literal interpreter in any shipped path)

## Completed slice
Job 1 — `build_crew_argv` (`scripts/run_crew.py`) now appends `--permission-mode acceptEdits` plus a broad `--allowedTools` grant to every crew dispatch, so a worktree with no hand-written `.claude/settings.local.json` can still do full crew work.

Job 2 — new `scripts/wire_mcp_interpreter.py` reuses `install_constellation.py`'s `resolve_interpreter()` to rewrite `.mcp.json`'s interpreter placeholder to the machine's probed interpreter, hard-stopping when nothing probes. **Not fully landed**: the one-line edit to the committed `.mcp.json` (swap the literal `"python3"` for the placeholder) is blocked — see Stop conditions hit.

## Scope
**Files changed:**
- `scripts/run_crew.py` — `build_crew_argv` grants `--permission-mode`/`--allowedTools`
- `tests/test_crew_launcher.py` — new test for the grant
- `scripts/wire_mcp_interpreter.py` — new: resolves + rewrites `.mcp.json`'s interpreter
- `tests/test_wire_mcp_interpreter.py` — new: 5 tests covering rewrite/noop/hard-stop/both PATH shapes
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`)
- `.agent-work/epic-418-followon/m2-mechanical/` — plan, handoff, crew-runs (durable run artifacts; `.agent-work/` is tracked by this repo's own convention)
- `.mcp.json` — **NOT changed** (blocked; still carries the literal `"python3"` this run set out to remove)

**Specific exclusions touched:** no. `checklist_engine.py::claim`, `_identity_violation`/`from_child` in `mcp_spine_server.py`, `settings.json`, `docs/agents/*` — none touched.

## Behavior changed
Yes. Every crew `run_crew.py` dispatches (`cli` backend, both fresh `dispatch` and `resume`) now carries `--permission-mode acceptEdits` and a fixed `--allowedTools` list. No other runtime behavior changed — `.mcp.json` is unchanged, so the interpreter it hardcodes today is exactly what it hardcoded before this run.

## Map Impact
- **Structural anchors touched:** `scripts.run_crew:build_crew_argv` — argv shape changed (additive only); `scripts.run_crew` gained `DEFAULT_CREW_PERMISSION_MODE`, `CREW_ALLOWED_TOOLS`; new module `scripts.wire_mcp_interpreter` (`rewrite_mcp_config_interpreter`, `main`, `MCP_INTERPRETER_PLACEHOLDER`).
- **Capabilities added/changed/affected:** a dispatched crew now gets working tool permissions without an operator hand-writing `.claude/settings.local.json` first (Job 1, delivered). A per-machine `.mcp.json` interpreter-resolution capability now exists but is not yet wired into the shipped config (Job 2, built not landed).
- **Constraints/assumptions touched:** `resolve_interpreter()`'s "hard-stop when nothing probes, never stamp a guess" contract (#539) is reused unchanged and extended to a second shipped-config consumer.
- **Trust limitations / drift found:** `.mcp.json` still names a literal interpreter (`"python3"`) on `main`/this branch — the map/doc claim "no literal interpreter in any shipped path" is **not yet true** for this file. A future Cartographer pass should flag `.mcp.json`'s `command` field as stale against the placeholder convention until a human applies the one-line edit below.
- **Triage candidates:**
  1. `.mcp.json`'s `command` field needs a human-applied one-line edit (below), then one run of `python scripts/wire_mcp_interpreter.py`, to actually close Job 2.
  2. A stray `.agent-work/epic-418-followon/epic-418-followon/` directory (duplicated path segment) appeared during this run, containing `mechanical/*.json` and `context/*.json` sidecars keyed off this plan's steps — looks like a path-doubling bug in whatever wrote it (likely `agent_work_root.py`/`episode_capture.py`/`context_manifest.py`, not `checklist_engine.py::claim` itself). Left untouched and unstaged; worth a Cartographer/Triage look. Not investigated further — out of this run's scope.

## Test mode
**Required:** test-first (TDD red→green per handoff; global-crew.md doctrine)
**Satisfied:** yes for both jobs' own new tests; Job 2's shipped-file integration has no test because there is nothing to test — the file is unchanged.

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2500 passed, 1 skipped, 1089 subtests passed` (baseline was `2494 passed, 1 skipped`; +6 new tests, 0 regressions).

### Control 1 — before (fails, reproduced on a clean worktree, today's code)
```
git worktree add /tmp/m2-control-check HEAD --detach   # no .claude/settings.local.json present
claude -p "<crew-shaped prompt>. ... use the Write tool to create CONTROL_MARKER.txt ..."
```
Result: file **not created**. Verbatim: *"I wrote the marker as instructed, but the write was blocked by the permission system: ... this session is non-interactive so I can't prompt for approval. I'm not routing around it with a shell command."*

### Control 1 — after (passes, same clean-worktree recipe, `build_crew_argv`'s real argv)
```
git worktree add /tmp/m2-fix-check HEAD --detach
claude -p "<same prompt>" --permission-mode acceptEdits --allowedTools Bash Read Write Edit Glob Grep TodoWrite ToolSearch mcp__spine__spine_status mcp__spine__spine_lease mcp__spine__spine_start mcp__spine__spine_advance mcp__spine__spine_evidence mcp__spine__spine_halt mcp__spine__spine_survey_result
```
Result: `CONTROL_MARKER.txt` created, contents `CONTROL-OK`. Exit 0.

### Control 2 — before AND after (unchanged; still fails — `.mcp.json` could not be edited)
```
which python3   # /usr/bin/python3
python3 -m pytest --version
```
Result both times: `/usr/bin/python3: No module named pytest` (exit 1). `.mcp.json`'s `"command": "python3"` is byte-identical before and after this run.

### Job 2 mechanism, demonstrated against a copy (since the real file is blocked — see below)
```bash
python scripts/wire_mcp_interpreter.py --mcp-config /tmp/copy-of-mcp.json
# wired /tmp/copy-of-mcp.json: command -> 'py' (probed)
```
`"command": "<python-interpreter>"` → `"command": "py"` in the copy (this host's probe order resolves `py` first). Confirms the resolve+rewrite path works end to end; only the shipped file's placeholder-swap is missing.

## TDD evidence, if required

**Job 1**
- Failing: `tests/test_crew_launcher.py::SessionNameTests::test_build_crew_argv_grants_permission_mode_and_allowed_tools` → `AssertionError: '--permission-mode' not found in [...]`
- Passing: same test, after adding the two flags to `build_crew_argv` → `94 passed` in `tests/test_crew_launcher.py`.
- Refactor while green: no refactor needed.

**Job 2**
- Failing: all 5 tests in `tests/test_wire_mcp_interpreter.py` → `FileNotFoundError: scripts/wire_mcp_interpreter.py` (script didn't exist).
- Passing: same 5 tests after writing the script → `5 passed`.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- None. (`.mcp.json`'s intended contract change — dropping the literal interpreter — is documented here but not applied.)

## Assumptions
- `.mcp.json`'s `command` field is the right (and only) place Job 2 needs to change; no other shipped path in this repo hardcodes an interpreter for a live entry point (grepped `scripts/*.py`, `docs/*.md`, `README.md` for `python3`/`"command"` patterns; nothing else stood out as a shipped, machine-agnostic entry point carrying a bare interpreter name).
- The Claude Code "sensitive file" refusal on `.mcp.json` is a harness-level, path-based guard (not a project setting) — confirmed by three independent refusals (Edit ×2, Write ×1) all producing the identical message regardless of my session's own broad tool permissions.

## Stop conditions hit
**Job 2's shipped-file edit is blocked**, not a no-go from the handoff's list but a genuine authority boundary: both the `Edit` and `Write` tools refuse `.mcp.json` outright — *"Claude requested permissions to edit `.mcp.json` which is a sensitive file"* — independent of my `.claude/settings.local.json` permissions (which grant unrestricted `Edit`/`Write` and were used successfully on every other file in this run). I did not attempt a `Bash`-based file-write workaround; that would be routing around a deliberate refusal, the same posture Control 1's own transcript demonstrates ("I'm not routing around it with a shell command"), and this guard specifically exists to stop an agent from silently expanding its own MCP-server trust — exactly what a `.mcp.json` edit would do.

**A human needs to apply this one-line diff**, then run the wiring script once per machine:

```diff
--- a/.mcp.json
+++ b/.mcp.json
@@ -1,7 +1,7 @@
 {
   "mcpServers": {
     "spine": {
-      "command": "python3",
+      "command": "<python-interpreter>",
       "args": [
         "scripts/mcp_spine_server.py"
       ],
```

```bash
python scripts/wire_mcp_interpreter.py   # resolves + rewrites the placeholder for this machine
```

## Out-of-scope observations
- The stray `.agent-work/epic-418-followon/epic-418-followon/` directory noted under Map Impact — a Cartographer/Triage candidate, not fixed here (out of scope, and `checklist_engine.py` beyond `::claim` is not itself a no-go but touching its evidence-writing machinery on a hunch, mid-run, was judged too risky for this task's bound).

## Workflow Feedback

- **Handoff gaps:** none — task, scope, evidence, no-gos, test mode, and stop conditions were all present and sufficient to plan the work.
- **Context rediscovered:** the exact shape of "what a crew needs" (the `--allowedTools`/`--permission-mode` grant list) wasn't named in the handoff; I derived it from the `.claude/settings.local.json` that was hand-written to launch *this very session* (still present, gitignored, in this worktree) and from `run_skill_eval.py`'s already-established `build_eval_argv`/`EXEC_ALLOWED_TOOLS`/`DEFAULT_PERMISSION_MODE` precedent (issue #115) — both were the right sources but neither was pointed to by the handoff; a Map Anchor into `run_skill_eval.py`'s precedent would have saved the search.
- **Instructions improvised around:** the handoff's Job 2 wording ("no literal interpreter in any shipped path... reuse the resolution... rather than inventing a second one") reads as a request to fix `.mcp.json` directly. I discovered mid-run that Claude Code's own tooling structurally refuses to edit `.mcp.json` (a harness-level "sensitive file" guard, not a project setting), which the handoff had no way to anticipate. I built and fully tested the resolve+rewrite mechanism against a copy of the file instead of the real one, and documented the exact human step needed — this is the closest compliant thing available, per `global-crew.md`'s "stop and report, don't improvise" for a case where required evidence (a landed `.mcp.json`) genuinely cannot be produced by this role.
- **What would have made this easier:** a note in the handoff (or in project doctrine) that `.mcp.json` is off-limits to agent Edit/Write tools would have let me design Job 2 around that constraint from the start (e.g. scoping it explicitly as "build the mechanism; a human lands the one-line diff") instead of discovering it after building the full change.

## Return status
`partial` — Job 1 complete and verified end-to-end (control fails-before/passes-after, full suite green). Job 2's mechanism is complete and tested, but the shipped `.mcp.json` edit itself is blocked by a tool-level guard outside this session's authority; missing portion and next action are the one-line diff + `wire_mcp_interpreter.py` run documented above.
