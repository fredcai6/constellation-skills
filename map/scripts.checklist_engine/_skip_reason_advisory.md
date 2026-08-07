# scripts.checklist_engine:_skip_reason_advisory
function, scripts/checklist_engine.py:1273, 35 lines

```python
def _skip_reason_advisory(gauge_path: Path | None) -> str
```

A visible notice that the writer hook POSITIVELY LOCALIZED why no

reading was written at this gauge path (issue #271) — ambiguous session->
spine binding, or a transcript with no usable usage record. Neither cause
is routine silence: the writer hook already knows exactly why it skipped,
so saying nothing here would waste information it already has. Fail-safe
like every other gauge-adjacent advisory — an absent reader, unresolvable
path, or any problem reading the sidecar yields the empty string.

calls internal: _format_age
calls stdlib: datetime.datetime.now
reads internal: _gauge_reader x2
reads stdlib: builtins.Exception, datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
