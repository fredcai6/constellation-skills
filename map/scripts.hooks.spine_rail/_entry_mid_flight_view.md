# scripts.hooks.spine_rail:_entry_mid_flight_view
function, scripts/hooks/spine_rail.py:516, 26 lines

```python
def _entry_mid_flight_view(data: dict, entry: dict)
```

Per-entry mid-flight check, unchanged in substance from the pre-#202

single-entry logic -- just factored so decide_stop can apply it to every
bound abs_spine_path entry for a session_id, not just one.

Returns None if this entry is NOT a genuine mid-flight blocker (foreign
worktree, unreadable spine, released/inactive lease, or an honest engine
block); else `(spine_path, spine_dict, aid)`.

calls internal: _foreign_worktree, active_id, load_spine
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
