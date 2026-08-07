# scripts.hooks.gauge_writer_hook:derive_subagent_transcript
function, scripts/hooks/gauge_writer_hook.py:184, 19 lines

```python
def derive_subagent_transcript(transcript_path, agent_id)
```

The ACTING agent's own transcript, derived from the payload:

`<parent transcript minus .jsonl>/subagents/agent-<agent_id>.jsonl`.

Derived, never searched for. The harness hands over `agent_id` directly,
so resolving WHO is an O(1) payload lookup and this path follows from it
by construction -- which is why the identical-command race a search-based
identity would have to defend against cannot arise here at all. The shape
was confirmed on disk for both agents of a live two-subagent probe.

Returns None -- never a repaired path -- when the id fails
`_is_usable_agent_id` or the parent path is unusable.

calls internal: _is_usable_agent_id
calls stdlib: pathlib.Path
reads stdlib: builtins.Exception
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
