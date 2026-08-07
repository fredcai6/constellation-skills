# scripts.verify_skip_guard:_load_report
function, scripts/verify_skip_guard.py:91, 5 lines

```python
def _load_report(path: Path) -> ET.Element
```

HOLE: no docstring

calls internal: SkipGuardError
calls stdlib: xml.etree.ElementTree.parse
reads stdlib: xml.etree.ElementTree (module) x2, builtins.OSError, xml.etree.ElementTree.ParseError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
