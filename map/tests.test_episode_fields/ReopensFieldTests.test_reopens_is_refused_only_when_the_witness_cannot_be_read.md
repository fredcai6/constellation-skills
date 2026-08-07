# tests.test_episode_fields:ReopensFieldTests.test_reopens_is_refused_only_when_the_witness_cannot_be_read
method, tests/test_episode_fields.py:402, 7 lines

```python
def test_reopens_is_refused_only_when_the_witness_cannot_be_read(self)
```

Tested on the helper directly: a checklist malformed enough to lose its

`tasks` mapping cannot produce an active step either, so `mechanical_fields`
would never reach this branch. It is kept because a partial read must still
refuse rather than answer 0.

calls internal: ReopensFieldTests.assertEqual, ReopensFieldTests.assertIsNone
reads internal: ec x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
