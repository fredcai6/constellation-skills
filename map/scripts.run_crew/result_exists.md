# scripts.run_crew:result_exists
function, scripts/run_crew.py:166, 7 lines

```python
def result_exists(result: str | os.PathLike[str], root: Path) -> bool
```

Whether the expected result artifact exists. A relative path is resolved

against `root`; an absolute path is honored as-is.

calls stdlib: pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
