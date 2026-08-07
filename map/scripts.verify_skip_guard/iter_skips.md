# scripts.verify_skip_guard:iter_skips
function, scripts/verify_skip_guard.py:72, 11 lines

```python
def iter_skips(report_root: ET.Element) -> Iterator[tuple[str, str, str]]
```

Yield (classname, name, message) for every <testcase> that carries a

<skipped> child, across the whole report regardless of <testsuite> nesting.

unresolved: 5 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
