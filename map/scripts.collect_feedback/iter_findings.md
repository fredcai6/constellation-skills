# scripts.collect_feedback:iter_findings
function, scripts/collect_feedback.py:185, 5 lines

```python
def iter_findings(text: str) -> list[dict[str, str]]
```

Findings in either export shape (content-less blocks dropped).

calls internal: _is_finding, _is_prose_finding, parse_entries, parse_prose_findings

referenced by: 2 sites, this module only
