# tests.test_map_orient:SubstituteLabels.test_the_label_never_upgrades_the_pin
method, tests/test_map_orient.py:981, 11 lines

```python
def test_the_label_never_upgrades_the_pin(self)
```

A label is a provenance note, not a discharge: an absent substitute

still refuses, whatever it is called.

calls internal: RepoFixture, SubstituteLabels.assertEqual, SubstituteLabels.assertIsNone, SubstituteLabels.assertNotEqual, orient, receipt_of, run_cli
calls stdlib: builtins.str
reads internal: RepoFixture.root x3, mo
unresolved: 4 reads (dispatch-unknown-base)

referenced by: none found
