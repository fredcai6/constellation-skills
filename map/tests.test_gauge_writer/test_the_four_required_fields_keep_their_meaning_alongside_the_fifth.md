# tests.test_gauge_writer:test_the_four_required_fields_keep_their_meaning_alongside_the_fifth
function, tests/test_gauge_writer.py:1242, 9 lines

```python
def test_the_four_required_fields_keep_their_meaning_alongside_the_fifth(proj)
```

gauge_reader validates the presence of its four required fields and

does not reject extras, so the fifth costs zero reader change. Pin that
the four are still exactly what they were.

calls internal: _write_a_subagent_reading
calls third-party: pytest.approx
reads internal: _REAL_SUBAGENT_OBSERVED_AT, _REAL_SUBAGENT_TOKENS
reads third-party: pytest (module)

referenced by: none found
