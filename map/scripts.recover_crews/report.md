# scripts.recover_crews:report
function, scripts/recover_crews.py:198, 21 lines

```python
def report(entries: list[tuple[dict, str]], out: Callable[[str], object] = print) -> int
```

Print one human-readable line per entry plus a summary. Returns a nonzero

exit code when any unresolved (active/resumable/conflict) attempt remains, so
Commander can gate a new launch on a zero exit.

calls internal: report.out x3, _behavior_for
calls stdlib: builtins.len
reads internal: UNRESOLVED_STATES
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
