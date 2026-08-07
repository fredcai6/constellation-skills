# scripts.hooks.spine_rail:_scan_active_spine
function, scripts/hooks/spine_rail.py:605, 24 lines

```python
def _scan_active_spine(project_dir: Path)
```

Best-effort fallback: EVERY .agent-work/*/spine.json with an active

lease and a non-None active id, as a list of `(spine_dict, spine_path)`
tuples in glob order (session->spine binding is preferred; this is the
last-resort discovery path). Empty list if none found.

Returning every match (not just the first) is deliberate: the caller
needs a COUNT to tell an unambiguous single active spine from an
ambiguous multi-spine scan (#261 bind-on-resume), while still wanting
the same "first match" spine for the advisory-context injection it did
before this match ever mattered. One glob pass serves both.

calls internal: _agent_work, active_id, load_spine
calls stdlib: builtins.str x2, builtins.isinstance
reads stdlib: builtins.Exception, builtins.dict
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
