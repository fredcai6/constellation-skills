# tests.test_episode_fields:ZeroAgentEffortTests.test_a_refused_field_is_named_rather_than_silently_missing
method, tests/test_episode_fields.py:810, 9 lines

```python
def test_a_refused_field_is_named_rather_than_silently_missing(self)
```

Fail-soft is not fail-silent, inherited from g1: an absent field and a

field nobody tried to read must stay tellable apart.

calls internal: LiveSpine, LiveSpine.verb, ZeroAgentEffortTests.assertIn, ZeroAgentEffortTests.assertNotIn
calls stdlib: json.loads, pathlib.Path
reads internal: LiveSpine.dir, ZeroAgentEffortTests.tmp
reads stdlib: json (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
