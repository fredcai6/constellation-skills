# scripts.collect_feedback:mark_collected
function, scripts/collect_feedback.py:312, 18 lines

```python
def mark_collected(root: Path) -> int
```

Record every current entry fingerprint as collected; returns count newly marked.

calls internal: _in_sidecar, fingerprint, iter_findings, load_sidecar, save_sidecar
calls stdlib: datetime.date.today
calls third-party: agent_work_root.durable_root
reads stdlib: datetime.date
unresolved: 3 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: 1 sites, this module only
