# scripts.hooks.spine_rail:binding_key
function, scripts/hooks/spine_rail.py:150, 48 lines

```python
def binding_key(payload: dict)
```

The outer key this payload's binding is filed under -- the SINGLE place

the composite per-agent key is composed anywhere in the codebase (the gauge
writer calls this same function through its `_spine_rail` module handle, so
the two hooks cannot drift).

Agent-tool subagents SHARE their parent's `session_id`, so keying on
`session_id` alone piles every crew claim under one key and the gauge writer
-- seeing more than one candidate -- calls it ambiguous and writes nothing.
The harness hands the acting agent's identity over directly as `agent_id`
(measured live on 2.1.222; see tests/fixtures/probe_payloads.jsonl), so the
key is a payload lookup, never a search.

Three-way, deliberately not two-way:

| payload                                     | returns                  |
|---------------------------------------------|--------------------------|
| `session_id`, no `agent_id` (top-level)     | bare `session_id`        |
| `session_id` + well-formed `agent_id`       | `"<session_id>#<agent>"` |
| `agent_id` present but UNUSABLE             | `None`                   |
| `session_id` falsy                          | `None`                   |

`None` means BIND NOTHING -- the caller writes no entry at all. An unusable
`agent_id` must NOT fall back to the bare `session_id`: that would file the
SUBAGENT's entry under the PARENT's key, push the parent to two candidates
and silence the PARENT's gauge, manufacturing exactly the blindness this
keying exists to remove. Failing closed costs that one subagent its binding
and affects nobody else.

A present-but-null `agent_id` reads as unusable, not as absent: it is not a
string, and the probed harness omits the key entirely for a top-level agent
rather than sending null.

calls stdlib: builtins.any, builtins.isinstance
reads internal: BINDING_KEY_SEP, _AGENT_ID_REJECT
reads stdlib: builtins.Exception, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
