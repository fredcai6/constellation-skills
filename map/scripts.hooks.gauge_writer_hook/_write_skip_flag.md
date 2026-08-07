# scripts.hooks.gauge_writer_hook:_write_skip_flag
function, scripts/hooks/gauge_writer_hook.py:471, 24 lines

```python
def _write_skip_flag(gauge_path: Path, reason: str, *, candidate_count: int | None = None, observed_at: str | None = None) -> None
```

Record WHY no reading was written at this gauge path -- a diagnostic

fact about the writer's own decision, never a fabricated/misattributed
reading (unlike gauge.json itself, this is safe to fan out -- see the
ambiguous-binding branch in handle_post_tool_use below).

`observed_at` here is WRITE time, unlike the uncalibrated flag's SAMPLED
moment: neither skip cause reaches a point where a transcript-sampled
timestamp exists to carry through (ambiguous binding never gets far
enough to parse the transcript at all; no-usable-record means parsing
found nothing usable), so "now" is the only honest timestamp available.
A caller (checklist_engine.py's advisory) renders this age raw, exactly
like every other gauge-adjacent timestamp -- never a threshold judgment.

calls internal: _atomic_write_json, _skip_path
calls stdlib: datetime.datetime.now
reads internal: SCHEMA_VERSION
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
writes internal: _write_skip_flag.observed_at
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
