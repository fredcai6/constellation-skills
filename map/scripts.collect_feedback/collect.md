# scripts.collect_feedback:collect
function, scripts/collect_feedback.py:292, 18 lines

```python
def collect(project_roots: list[Path]) -> tuple[Hits, Hits]
```

Return (new, open_unresolved) candidate groups keyed by fingerprint.

calls internal: _in_sidecar, fingerprint, iter_findings, load_sidecar
calls third-party: agent_work_root.durable_root
reads internal: Hits x2
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
