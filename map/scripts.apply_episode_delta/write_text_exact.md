# scripts.apply_episode_delta:write_text_exact
function, scripts/apply_episode_delta.py:89, 9 lines

```python
def write_text_exact(path: Path, text: str) -> None
```

Write a store file emitting exactly `text`, with no platform newline translation.

Same portability reason as `read_text_exact`, and the same load-bearing semantics: on
Windows the default would translate every `\n` to `\r\n`, making the store's bytes
depend on which OS wrote them.

unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
