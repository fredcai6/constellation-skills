# scripts.verify_skip_guard:find_disallowed_skips
function, scripts/verify_skip_guard.py:85, 4 lines

```python
def find_disallowed_skips(report_root: ET.Element) -> list[tuple[str, str, str]]
```

Return every skip whose (classname, name, message) triple is not on the

allow-tuple list. Empty means the report is clean.

calls internal: iter_skips
reads internal: ALLOWED_SKIPS

referenced by: 1 sites, this module only
