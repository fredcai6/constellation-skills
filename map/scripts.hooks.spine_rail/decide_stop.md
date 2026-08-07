# scripts.hooks.spine_rail:decide_stop
function, scripts/hooks/spine_rail.py:544, 57 lines

```python
def decide_stop(data: dict, project_dir: Path) -> dict
```

Block the Stop if ANY non-foreign bound entry for this session_id is

genuinely mid-flight (same per-entry semantics as the pre-#202 single-
entry version, just applied across every abs_spine_path entry now bound
under `sid`). The nudge-tracking / 3-strike escape hatch stays keyed by
`sid` ALONE -- never fragmented per-entry, which would weaken the escape
hatch.

calls internal: _entry_mid_flight_view, _mid_flight_reason, journal_seq, load_binding, load_nudges, reconstruct_current, save_nudges, session_view
calls stdlib: builtins.sorted, builtins.sum
reads internal: STUCK_MSG
reads stdlib: builtins.Exception
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
