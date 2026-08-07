# tests.test_episode_store:NonForeclosureTests.assertion_block
method, tests/test_episode_store.py:1545, 8 lines

```python
def assertion_block(self, raw: bytes, episode_id: str, aid: str) -> bytes
```

The exact bytes of one `### assertion:<id>.<aid>` block, from its heading up

to the next blank-line-separated block. Sliced out of the raw bytes rather than
reconstructed, so what is compared is what is genuinely on disk.

unresolved: 3 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
