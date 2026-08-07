# Problem statement — issue #440 (epic-418 workstream A2)

Reconciled against the frozen `LAUNCH_ORDER` at
`.agent-work/epic-418/launch-orders/A2-440.md` + `_COMMON.md`. No human is reachable;
the Admiral is the reachable tier.

## The ask

Make the context governor fire on real Constellation runs. Concretely: a **HARD trip must fire
from a per-agent gauge reading produced by an agent dispatched into a worktree**, with the reading
landing where the engine actually reads it. Two-arm live fire, byte-identical control.

## The defect, at the code site

`scripts/hooks/spine_rail.py`:

- `handle_post_tool_use` (line 438): `cwd = data.get("cwd") or str(project_dir)`
- `_resolve_abs` (line 390): a relative `--file` is joined onto that `cwd` and `.resolve()`d.

The binding entry is therefore keyed by `<payload cwd>/.agent-work/<work_id>/spine.json`.

## What the payload actually carries — settled from real data, not guessed

Pre-ruling `decision:fix-the-resolution-not-the-caller` asked me to settle this by reading a real
hook payload from a worktree-dispatched agent. Two independent readings, both real:

1. **#419's own capture**, `tests/fixtures/probe_payloads.jsonl` (6 payloads, harness 2.1.222,
   2 concurrent subagents). Every payload's `cwd` is the **headless session's launch directory**,
   byte-identical across the parent and both subagents. The full key set is
   `cwd, duration_ms, effort, hook_event_name, permission_mode, prompt_id, session_id, tool_input,
   tool_name, tool_response, tool_use_id, transcript_path` (+ `agent_id`, `agent_type` on a
   subagent). There is **no per-agent working-directory field.**
2. **This run's own `claim`**, observed live in the main checkout's
   `.agent-work/.spine-rail-binding.json` immediately after I claimed my lease. My Bash command
   was `cd C:/Programs/constellation-skills-wt/epic418-a2-440 && python scripts/checklist_engine.py
   --file .agent-work/issue-440-binding-cwd/spine.json claim ...`, and the entry recorded is
   `C:\Programs\constellation-skills\.agent-work\issue-440-binding-cwd\spine.json` with
   `"worktree": "C:\\Programs\\constellation-skills"` — the **main checkout**, not the worktree
   the command actually ran in. My real spine is at
   `C:\Programs\constellation-skills-wt\epic418-a2-440\.agent-work\issue-440-binding-cwd\spine.json`.

**Ruling on the pre-ruling.** The payload genuinely cannot tell you the right root — `cwd` is
session-scoped, not agent-scoped or command-scoped, and no other field carries a root. That does
**not** overturn `fix-the-resolution-not-the-caller`: it means the resolution must stop treating
`cwd` as authoritative and instead **verify its answer against the filesystem**. The fix stays
inside the resolution, in `spine_rail.py`; no call site is patched.

## The resolution, as designed

Replace "join `--file` onto `cwd` and trust it" with "resolve `--file` against an ordered set of
candidate roots and take the first one where the file **actually exists**":

1. a `cd <dir>` target parsed out of the tool command itself (present whenever an agent cds in the
   same command, which is the common Constellation shape);
2. the payload's `cwd` (preserves today's behaviour wherever today's behaviour is right);
3. every git worktree root registered against the project (`git worktree list --porcelain`),
   which is the only channel that can name a worktree the payload never mentions;
4. `project_dir`.

Nothing exists at any candidate → **bind nothing** (fail closed), consistent with the store's
existing fail-closed doctrine (`binding_key` returning `None`, the gauge writer's
skip-on-uncertainty). A binding pointing at a spine that is not there is precisely this defect;
writing it anyway is not a safer outcome than silence. More than one candidate matches → take the
earliest in the order, which is the most specific signal about *this* command.

## Protected intent

- **#269 is not mine to fix.** `CLAUDE_PROJECT_DIR` stays fixed at session launch; the fix must
  work *with* that, never require it to change. (`decision:not-fixing-269`, settled/human.)
- The binding key **shape** (`session_id` / `session_id#agent_id`) is load-bearing interface and
  is not touched — that is #419's, and changing it would need the Admiral.
- The gauge writer's read side is not touched; it resolves paths through the binding store, so
  fixing the store is what reaches it.
- Scope discipline (settled/human): build the thing that needs to work. Corner cases get a comment
  at the code site and a line in `RETURN.md`, not a gate.

## How the green will be made real

The trap: hook code is not fenced by worktree isolation, so validating from inside this worktree
runs the **main checkout's** hook code and proves nothing. The acceptance run is therefore a
**disposable sandbox pair** — a scratch repo standing in for the main checkout, plus a real
`git worktree` of it — driven by a headless `claude -p` whose `cwd`/`CLAUDE_PROJECT_DIR` is the
sandbox **main** (which is what reproduces the bug's own precondition), with the `PostToolUse`
hook wired by **absolute path** to a specific copy of `spine_rail.py`. That absolute path is the
only difference between the two arms: treatment points at this worktree's fixed hook, control
points at a copy of the base-commit hook. A subagent is dispatched into the sandbox worktree,
claims a spine there, and the run is checked for a fired HARD trip on that subagent's own spine.

Feasibility probed, not assumed: a headless `claude -p ... --permission-mode acceptEdits` wrote
its file (`probe440/hello.txt` = `OK440`, exit 0), so the headless permission model does not
silently deny tool actions.
