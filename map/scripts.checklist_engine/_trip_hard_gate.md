# scripts.checklist_engine:_trip_hard_gate
function, scripts/checklist_engine.py:1400, 28 lines

```python
def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None) -> None
```

Trip HARD backstop at the `advance` gate boundary: REFUSE to advance when

the gauge reads `fill >= hard` and no `refresh-request` is pending for the
gate. No-op for surveys, a missing/stale reading (None), or below `hard` — HARD
never forces on an absent reading. Called BEFORE `advance` mutates state, so a
refusal leaves the gate exactly `in-progress`.

calls internal: EngineError, _latest_why_record, _read_gauge, _refresh_attach_hint, has_pending_refresh_request
reads internal: GATED, _gauge_reader
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
