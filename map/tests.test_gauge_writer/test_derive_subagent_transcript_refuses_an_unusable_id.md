# tests.test_gauge_writer:test_derive_subagent_transcript_refuses_an_unusable_id
function, tests/test_gauge_writer.py:860, 8 lines

```python
def test_derive_subagent_transcript_refuses_an_unusable_id(proj, tmp_path)
```

The derivation re-validates at its own boundary too: a rejected value

yields None, never a repaired path and never an exception that the outer
swallow would turn into indistinguishable silence.

reads internal: gw x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
