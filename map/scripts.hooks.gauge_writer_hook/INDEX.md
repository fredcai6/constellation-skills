# scripts.hooks.gauge_writer_hook
scripts/hooks/gauge_writer_hook.py, 695 lines, 4 holes

gauge_writer_hook.py -- Claude Code PostToolUse hook: Context Governor gauge

WRITER (Module 2, write side; issue #180).

On every tool call, senses context fill from the session transcript and
atomically writes `.agent-work/<work_id>/gauge.json` for the engine-side
reader (#181) to consume. See docs/GAUGE_WRITER_HOOK.md for the wiring,
the exact transcript shape this depends on, and what breaks it.

Design contract (frozen DESIGN_SPEC #178, Module 2 post-review amendments):

- Fail-open. Any error anywhere is swallowed; the hook never blocks or
  fails the tool call it's attached to. Every handler is wrapped.
- Skip-on-uncertainty, NEVER fabricate. If fill can't be computed
  confidently (missing transcript, no usable usage record, missing
  timestamp, unresolvable work_id), write NOTHING -- the existing gauge
  file is left exactly as it was and ages into staleness naturally. A
  fabricated 0.0 would read as genuine low fill and could suppress a
  nudge that should have fired.
- Record is four REQUIRED fields (identical to #181's reader):
  {schema_version: int, fill_fraction: float 0..1, model: str,
  observed_at: ISO-8601 str -- the SAMPLED moment, not write time},
  plus ONE optional fifth on the dispatched-agent path only (#419):
  {identity_resolution_ms: float}. A top-level agent's record still
  carries exactly the four, byte-identical to before #419. The reader
  validates the four and does not reject extras, which is what makes an
  additive field free on the read side.
- Atomic write: tmp file + os.replace. A concurrent reader of gauge.json
  never observes a torn/partial record -- it always sees either the
  complete prior record or the complete new one.
- Session->spine binding is REUSED, not re-derived: `spine_rail.py`
  (this hook's sibling in the same PostToolUse rail) already maintains
  `.agent-work/.spine-rail-binding.json` mapping session_id -> spine
  path. `<work_id>` is that spine path's parent directory. If no binding
  exists for this session (e.g. no `checklist_engine.py claim` has run
  yet), the work_id is unresolvable and the hook skips -- this is a
  documented coupling, not a new mechanism (see docs/GAUGE_WRITER_HOOK.md).
  Because that binding records an unvalidated `--file` argument, the
  resolved target is CONTAINED to the documented
  `.agent-work/<work_id>/gauge.json` shape before any write (_is_contained);
  anything else skips rather than littering an arbitrary directory.
- The X2 "strategic-compact" technique: the transcript is JSONL; each
  top-level (non-sidechain) assistant message carries a `usage` block.
  Because Claude Code resends the full conversation on every turn, the
  LATEST such record's `input_tokens + cache_creation_input_tokens +
  cache_read_input_tokens` IS the current total context size (not a sum
  across lines/turns). Sidechain entries (subagent turns, `isSidechain:
  true`) are a different context window entirely and are skipped.
- The reading belongs to the AGENT THAT PRODUCED IT (#419). Agent-tool
  subagents share their parent's `session_id`, and their tool calls carry
  the PARENT's `transcript_path`, but the harness hands the acting agent's
  own `agent_id` over directly. So: the binding is keyed on
  `spine_rail.binding_key(payload)` (`session_id#agent_id` for a dispatched
  agent, the bare `session_id` for a top-level one), and the agent's own
  transcript is DERIVED from that id, never searched for. For a dispatched
  agent the sidechain polarity INVERTS -- every line of its own transcript
  is `isSidechain: true` -- and the line's `agentId` must equal the payload's.
  There is NO fallback to the parent's transcript: an absent derived
  transcript writes a `subagent-transcript-missing` skip and nothing else.
  Silence is an acceptable outcome; a confident wrong number is not.
- Stdlib only. Windows-friendly: UTF-8 I/O, native paths, no /tmp literals.

imports stdlib: datetime.datetime, datetime.timezone, importlib.util, json, os, pathlib.Path, re, sys, time
imported by: none found

```python
SCHEMA_VERSION = 1
MODEL_WINDOWS = {'claude-opus-5': 1000000, 'claude-opus-4-8': 1000000, 'claude-sonnet-5': 1000000, 'cla...
TAIL_BYTES = 2000000
_spine_rail = _load_spine_rail()
_AGENT_ID_ALLOWED = re.compile('\\A[A-Za-z0-9_-]{1,64}\\Z')
UNCALIBRATED_FILENAME = 'gauge-uncalibrated.json'
SKIP_FILENAME = 'gauge-skip.json'
```

- [_load_spine_rail](_load_spine_rail.md) function: Load scripts/hooks/spine_rail.py by file path -- robust regardless of
- [_is_contained](_is_contained.md) function: True only for the documented shape `<root>/.agent-work/<work_id>/gauge.json`.
- [_is_usable_agent_id](_is_usable_agent_id.md) function: HOLE: no docstring
- [derive_subagent_transcript](derive_subagent_transcript.md) function: The ACTING agent's own transcript, derived from the payload:
- [_binding_key](_binding_key.md) function: This payload's outer binding key, or None to write NOTHING.
- [resolve_gauge_path](resolve_gauge_path.md) function: `.agent-work/<work_id>/gauge.json` for EVERY spine this BINDING KEY is
- [_iter_tail_lines_reverse](_iter_tail_lines_reverse.md) function: Yield non-blank lines from the tail of `path`, most-recent-first,
- [find_latest_usage](find_latest_usage.md) function: Scan the transcript tail for the most recent assistant message carrying
- [compute_record](compute_record.md) function: Build the four required fields of the record for this transcript.
- [_atomic_write_json](_atomic_write_json.md) function: HOLE: no docstring
- [_uncalibrated_path](_uncalibrated_path.md) function: HOLE: no docstring
- [_write_uncalibrated_flag](_write_uncalibrated_flag.md) function: Record that this model has no window, so no reading could be produced.
- [_clear_uncalibrated_flag](_clear_uncalibrated_flag.md) function: Drop a stale flag once the model resolves again -- otherwise adding the
- [_skip_path](_skip_path.md) function: HOLE: no docstring
- [_write_skip_flag](_write_skip_flag.md) function: Record WHY no reading was written at this gauge path -- a diagnostic
- [_clear_skip_flag](_clear_skip_flag.md) function: Mirror _clear_uncalibrated_flag exactly: drop a stale skip sidecar once
- [handle_post_tool_use](handle_post_tool_use.md) function: Compute the record ONCE, then write it to the session's SOLE bound
- [main](main.md) function: Single-purpose hook (PostToolUse only) -- no event-name dispatch is
