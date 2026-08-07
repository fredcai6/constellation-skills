# scripts.file_issue_set:key_marker
function, scripts/file_issue_set.py:67, 4 lines

```python
def key_marker(key: str) -> str
```

The hidden marker embedded in a filed body so an adapter can find the

item again by key after a crash (before the receipt recorded it).

reads internal: KEY_PREFIX

referenced by: 4 sites, this module only
