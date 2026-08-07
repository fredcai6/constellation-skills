# tests.test_episode_store:SilentOmissionTests.test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped
method, tests/test_episode_store.py:1064, 24 lines

```python
def test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped(self)
```

A third shape, found by sweeping for the class rather than by a review note.

enumerate_episodes() turned the scan's ids into records with an `if ep is not
None` filter on the end — so an id the scan returned and fetch could not resolve
left the candidate set between two lines of one function, silently. It means the
store changed underneath the query, or the enumeration and resolution seams
disagree; both are facts, neither is "no match".

calls internal: QueryTestCase.seed x2, SilentOmissionTests.assertEqual, SilentOmissionTests.assertIn, SilentOmissionTests.assertRaises
calls stdlib: builtins.sorted, builtins.str
reads internal: SilentOmissionTests.q x6, SilentOmissionTests.root x2
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 3 reads (unbound-name), 2 writes (dispatch-unknown-base)

referenced by: none found
