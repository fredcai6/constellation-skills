# scripts.checklist_engine:_trip_advisory
function, scripts/checklist_engine.py:1360, 38 lines

```python
def _trip_advisory(cl: dict, base_dir: Path | None) -> str
```

The Trip advisory suffix for the read-only `current` at a gate boundary

(gated checklists only). Empty for surveys, a missing/stale reading, or when
below `soft`. SOFT band: a stop-by-default question (advisory — never forces).
HARD band: the same escalated to the exact remedy; the refusal itself is
enforced on `advance` by `_trip_hard_gate`.

calls internal: _latest_why_record, _no_reading_advisory, _read_gauge, _refresh_attach_hint, active_id, has_pending_refresh_request
reads internal: GATED, _gauge_reader
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
