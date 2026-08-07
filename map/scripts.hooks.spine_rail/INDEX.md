# scripts.hooks.spine_rail
scripts/hooks/spine_rail.py, 734 lines, 12 holes

spine_rail.py -- Claude Code hook suite for the Constellation spine rail.

One script, dispatched by event name (argv[1]): Stop, SessionStart, PostToolUse.
It is a deterrent that refuses dishonest turn-ends mid-spine and re-injects
resume doctrine after compaction, judging the ENGINE'S OWN TRUTH -- the spine
state file plus its journal sidecar -- and NEVER the agent's prose.

Design contract (frozen DESIGN_SPEC #138 channel B, D3):

- Fail-open. Any error anywhere prints nothing and exits 0. A hook must never
  crash or hang a turn. Every handler is wrapped and returns {} on trouble.
- State-file facts ONLY. Decisions read the spine JSON (json.load) and count the
  journal lines. The agent's words (last_assistant_message, etc.) are never
  parsed for a decision.
- Read the spine STATE FILE directly; do NOT subprocess the engine. This is a
  deliberate, spec-accepted LOCALITY COST: this module re-encodes the engine's
  TERMINAL statuses (a second place that knows "what is terminal") in exchange
  for robustness in headless/subagent contexts and clean unit-testability.
- Discovery is the PostToolUse hook's ONLY job: it watches Bash commands for the
  engine's claim/release verbs and maintains a session->spine binding. It is NOT
  a second source of mid-flight truth -- Stop always reads the spine file the
  binding points at.
- Three registrations only (Stop, SessionStart, PostToolUse). No PreCompact.
- 3-strike escape hatch so a genuinely stuck agent is never trapped.

Stdlib only (json, os, sys, shlex, pathlib). Windows-friendly: UTF-8 writes,
native paths, no /tmp literals.

imports stdlib: datetime.datetime, datetime.timezone, json, os, pathlib.Path, shlex, sys
imported by: none found

```python
TERMINAL = {'complete', 'skipped'}
STUCK_MSG = 'SPINE-RAIL: released turn-end after 3 no-progress nudges. The rail is standing down fo...
BINDING_KEY_SEP = '#'
_AGENT_ID_REJECT = (BINDING_KEY_SEP, '/', '\\', '..')
```

- [resolve_project_dir](resolve_project_dir.md) function: HOLE: no docstring
- [_agent_work](_agent_work.md) function: HOLE: no docstring
- [binding_path](binding_path.md) function: HOLE: no docstring
- [nudge_path](nudge_path.md) function: HOLE: no docstring
- [_load_json_map](_load_json_map.md) function: Load a JSON object map; return {} on absent/corrupt/non-object.
- [_save_json_map](_save_json_map.md) function: Atomically write a JSON object map. Never raises.
- [_is_old_shape_binding_entry](_is_old_shape_binding_entry.md) function: True if `entry` looks like the OLD flat per-session binding value
- [load_binding](load_binding.md) function: Load `session_id -> {abs_spine_path: {spine, engine_session, worktree,
- [save_binding](save_binding.md) function: HOLE: no docstring
- [binding_key](binding_key.md) function: The outer key this payload's binding is filed under -- the SINGLE place
- [session_view](session_view.md) function: The merged `{abs_spine_path: entry}` a harness session can see: the bare
- [load_nudges](load_nudges.md) function: HOLE: no docstring
- [save_nudges](save_nudges.md) function: HOLE: no docstring
- [load_spine](load_spine.md) function: json.load the spine state file. Return None on any failure.
- [active_id](active_id.md) function: First item id whose task status is NOT terminal; None if all terminal.
- [journal_seq](journal_seq.md) function: Progress signal: count of non-blank lines in <spine_path>.journal.
- [reconstruct_current](reconstruct_current.md) function: Rebuild the engine's `current` output from the state file (no subprocess).
- [_same_path](_same_path.md) function: True if a and b name the same path after normcase+normpath.
- [_foreign_worktree](_foreign_worktree.md) function: True only when the stopping session's cwd is positively a DIFFERENT
- [_tokenize](_tokenize.md) function: HOLE: no docstring
- [_extract_verb](_extract_verb.md) function: Positional verb after the engine script token, skipping the global
- [_extract_opt](_extract_opt.md) function: Value of `--name value` or `--name=value`; None if absent.
- [_resolve_abs](_resolve_abs.md) function: HOLE: no docstring
- [_now_iso](_now_iso.md) function: HOLE: no docstring
- [handle_post_tool_use](handle_post_tool_use.md) function: Maintain the session->spine binding from engine claim/release commands.
- [_mid_flight_reason](_mid_flight_reason.md) function: HOLE: no docstring
- [_entry_mid_flight_view](_entry_mid_flight_view.md) function: Per-entry mid-flight check, unchanged in substance from the pre-#202
- [decide_stop](decide_stop.md) function: Block the Stop if ANY non-foreign bound entry for this session_id is
- [_scan_active_spine](_scan_active_spine.md) function: Best-effort fallback: EVERY .agent-work/*/spine.json with an active
- [decide_session_start](decide_session_start.md) function: HOLE: no docstring
- [main](main.md) function: Dispatch by event name (argv[1]); print result JSON only if non-empty;
