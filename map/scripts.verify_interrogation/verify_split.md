# scripts.verify_interrogation:verify_split
function, scripts/verify_interrogation.py:95, 23 lines

```python
def verify_split(record: dict) -> None
```

The facts-vs-decisions split, enforced per resolved question.

Only `resolved` questions are gated — `open` (mid-loop) and `skipped`
(overcome by an earlier answer) questions carry neither obligation.

calls internal: _nonempty x2, _require x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
