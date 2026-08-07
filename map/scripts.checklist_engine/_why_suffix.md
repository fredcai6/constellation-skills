# scripts.checklist_engine:_why_suffix
function, scripts/checklist_engine.py:1140, 18 lines

```python
def _why_suffix(cl: dict, aid: str | None) -> str
```

The why-capture lines appended to `current`: a `DIGEST:` line carrying the

live understanding, and a `REFRESH REQUESTED:` line when a pending
refresh-request targets the active gate/item. Empty when neither applies. No new
verb — these ride the read-only `current`. Renders for BOTH gated and survey
checklists (#189): a survey never accumulates a `why_trail` (`_append_why` only
fires on `advance`, which refuses surveys), so `_digest` is None and NO `DIGEST:`
line appears — only the `REFRESH REQUESTED:` line, which is the reach-up target
for survey roles (reviewer). Gated output is unchanged.

calls internal: _digest, _latest_why_record, has_pending_refresh_request

referenced by: 1 sites, this module only
