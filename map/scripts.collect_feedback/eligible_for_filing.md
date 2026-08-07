# scripts.collect_feedback:eligible_for_filing
function, scripts/collect_feedback.py:429, 16 lines

```python
def eligible_for_filing(merged: Hits, inbox: dict, *, include_singles: bool) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]
```

Open findings worth filing, most-recurring first, skipping already-filed.

Default keeps the backlog high-signal: only findings at or above the
recurrence threshold. `include_singles` widens to every open finding.

calls stdlib: builtins.len x2, builtins.sorted
reads internal: RECURRENCE_THRESHOLD
unresolved: 2 calls (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only
