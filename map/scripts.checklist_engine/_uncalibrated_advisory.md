# scripts.checklist_engine:_uncalibrated_advisory
function, scripts/checklist_engine.py:1223, 27 lines

```python
def _uncalibrated_advisory(base_dir: Path | None) -> str
```

A visible notice that the context governor is OFF for this run because

the running model has no calibration entry.

Deliberately not a refusal and not a nudge to hand off: with no window we
cannot claim the context is either full or empty, so the honest report is
that the instrument is unavailable, plus the one-line fix. Fail-safe like
everything else on this path -- an absent reader or unresolvable location
yields the empty string.

calls internal: _gauge_path
reads internal: _gauge_reader x2
reads stdlib: builtins.Exception
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
