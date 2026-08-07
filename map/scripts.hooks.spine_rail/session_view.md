# scripts.hooks.spine_rail:session_view
function, scripts/hooks/spine_rail.py:200, 23 lines

```python
def session_view(binding: dict, sid) -> dict
```

The merged `{abs_spine_path: entry}` a harness session can see: the bare

`sid` key plus every per-agent key `sid + BINDING_KEY_SEP + <agent_id>`.

Readers (decide_stop, decide_session_start) must keep seeing every spine
they saw before the per-agent split, so they read through this view rather
than `binding[sid]`. The prefix test uses the separator on purpose -- a key
that merely starts with the sid (`<sid>-something`) is a different session,
not a child of this one. Never raises; returns {} on anything unusable.

calls stdlib: builtins.isinstance x2
reads internal: BINDING_KEY_SEP
reads stdlib: builtins.Exception, builtins.dict, builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
