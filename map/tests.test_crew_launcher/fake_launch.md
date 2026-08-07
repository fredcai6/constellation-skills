# tests.test_crew_launcher:fake_launch
function, tests/test_crew_launcher.py:58, 25 lines

```python
@contextlib.contextmanager
def fake_launch(RC_mod, exit_code: int, *, write_result_at: Path | None = None)
```

Replace the single subprocess seam with a fake that records the argv,

simulates an exit code, and optionally writes the result artifact — so no
real agent CLI is ever spawned.

- [fake](fake_launch.fake.md) method: HOLE: no docstring

reads stdlib: builtins.dict, builtins.list
unresolved: 1 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: 17 sites, this module only
