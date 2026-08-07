# tests.test_map_orient:SubstituteProvenanceIsReported.test_the_report_still_prints_no_anchor_id
method, tests/test_map_orient.py:1107, 10 lines

```python
def test_the_report_still_prints_no_anchor_id(self)
```

The anti-leak rule survives the new output. A substitute path is not

an anchor id -- and it was declared BY the agent, so echoing it back
hands over nothing the agent did not already write.

calls internal: RepoFixture, RepoFixture.file, SubstituteProvenanceIsReported.assertEqual, orient, verify
reads internal: RepoFixture.root x2, mo
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
