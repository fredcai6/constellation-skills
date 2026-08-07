# tests.test_init_work_area:ResolverPlaceholderAssertionTests
class, tests/test_init_work_area.py:377, 70 lines

```python
class ResolverPlaceholderAssertionTests(TestCase)
```

Direct unit coverage of the post-init hard check, independent of

resolve_spine, since under the generalized resolver every real role token
it discovers is (by construction) fully substituted -- this is the
defense-in-depth guard for a future resolver regression or an
out-of-pattern token (e.g. a role name with characters outside
[a-zA-Z0-9-]).

- [test_raises_on_leftover_work_id](ResolverPlaceholderAssertionTests.test_raises_on_leftover_work_id.md) method: HOLE: no docstring
- [test_raises_on_leftover_role_skill_dir](ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_skill_dir.md) method: HOLE: no docstring
- [test_raises_on_leftover_role_session_id](ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_session_id.md) method: HOLE: no docstring
- [test_does_not_raise_on_benign_prose_placeholders](ResolverPlaceholderAssertionTests.test_does_not_raise_on_benign_prose_placeholders.md) method: HOLE: no docstring
- [test_instantiate_spine_leaves_non_resolver_placeholders_alone](ResolverPlaceholderAssertionTests.test_instantiate_spine_leaves_non_resolver_placeholders_alone.md) method: HOLE: no docstring
- [test_instantiate_spine_raises_when_a_resolver_owned_token_cannot_resolve](ResolverPlaceholderAssertionTests.test_instantiate_spine_raises_when_a_resolver_owned_token_cannot_resolve.md) method: HOLE: no docstring

referenced by: none found
