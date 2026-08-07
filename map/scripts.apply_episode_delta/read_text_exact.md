# scripts.apply_episode_delta:read_text_exact
function, scripts/apply_episode_delta.py:75, 12 lines

```python
def read_text_exact(path: Path) -> str
```

Read a store file with newline translation DISABLED, so bytes survive the round trip.

Deliberately NOT `path.read_text(encoding=..., newline="")`: pathlib only gained the
`newline` kwarg in Python 3.13, and CI pins 3.12, so that form raises TypeError there.
`Path.open()` has accepted `newline` on every supported version. The `newline=""` is
load-bearing rather than cosmetic — it is what keeps the bytes the parser sees identical
to the bytes on disk, which is what `_reject_newline` and the byte-for-byte-unchanged
assertions both depend on.

unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
