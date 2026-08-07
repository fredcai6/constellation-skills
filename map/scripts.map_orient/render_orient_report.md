# scripts.map_orient:render_orient_report
function, scripts/map_orient.py:905, 16 lines

```python
def render_orient_report(orientation: Orientation, receipt_rel: str | None) -> list[str]
```

PURE. stdout lines; line 0 is always the reserved verdict literal.

calls internal: candidate_outcome
reads internal: Orientation.anchor_count, Orientation.candidates, Orientation.entrypoint, Orientation.mode, Orientation.root, Orientation.root_evidence
unresolved: 7 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
