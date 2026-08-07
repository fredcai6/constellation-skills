# tests.test_map_orient:SubstituteProvenanceIsReported.test_a_receipt_with_no_source_key_reports_as_agent_declared
method, tests/test_map_orient.py:1087, 9 lines

```python
def test_a_receipt_with_no_source_key_reports_as_agent_declared(self)
```

Forward compatibility in the CONSERVATIVE direction: a receipt from

before the label existed must never be UPGRADED by omission.

calls internal: RepoFixture, RepoFixture.file, SubstituteProvenanceIsReported.assertIn, SubstituteProvenanceIsReported.assertNotIn, degraded_receipt, verify
reads internal: RepoFixture.root x2, mo x2
unresolved: 4 reads (dispatch-unknown-base)

referenced by: none found
