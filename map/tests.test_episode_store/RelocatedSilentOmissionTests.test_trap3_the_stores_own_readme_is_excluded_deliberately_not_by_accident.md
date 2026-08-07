# tests.test_episode_store:RelocatedSilentOmissionTests.test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident
method, tests/test_episode_store.py:2253, 24 lines

```python
def test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident(self)
```

`episodes/README.md` already lives at the flat root, so the stray check above

would fire on it unless something excludes it. That exclusion is a NAMED
allowlist, not a glob shape — the test asserts the mechanism, because an accident
that currently works is one rename away from either refusing the whole store or
(worse) silently accepting a real stray.

calls internal: RelocatedSilentOmissionTests.assertEqual x3, QueryTestCase.seed, RelocatedSilentOmissionTests.assertIn
calls stdlib: builtins.frozenset
reads internal: RelocatedSilentOmissionTests.m x6, RelocatedSilentOmissionTests.root x4, RelocatedSilentOmissionTests.q
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: none found
