# evals.euler-2-even-fibonacci.checks.spine_completed:_parse_iso
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:85, 15 lines

```python
def _parse_iso(value)
```

Parse an ISO-8601 timestamp (tolerating a trailing 'Z'), or None. Naive

timestamps are assumed UTC so comparisons never raise on tz-mixing.

calls stdlib: builtins.isinstance, datetime.datetime.fromisoformat
reads stdlib: builtins.ValueError, builtins.str, datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 7 sites, this module only
