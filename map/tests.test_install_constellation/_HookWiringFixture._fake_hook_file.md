# tests.test_install_constellation:_HookWiringFixture._fake_hook_file
method, tests/test_install_constellation.py:1974, 7 lines

```python
def _fake_hook_file(self, tmp) -> Path
```

A resolvable gauge_writer_hook.py that no install created -- lets the

detector be exercised without paying for a full install.

calls stdlib: pathlib.Path
reads internal: _HookWiringFixture.WRITER
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 6 sites, this module only
