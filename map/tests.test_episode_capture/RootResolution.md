# tests.test_episode_capture:RootResolution
class, tests/test_episode_capture.py:126, 98 lines

```python
class RootResolution(TestCase)
```

Every assertion here is on a RESOLVED ABSOLUTE PATH, never on the helper

that produced it. A wrong root does not raise anywhere in the producer — it
yields `rev: null` rows — so asserting "we called the right function" would
pass just as happily with the wrong one wired underneath it.

- [test_roots_are_exactly_the_three_declared_tokens](RootResolution.test_roots_are_exactly_the_three_declared_tokens.md) method: HOLE: no docstring
- [test_roots_skill_is_the_parent_of_the_scripts_directory](RootResolution.test_roots_skill_is_the_parent_of_the_scripts_directory.md) method: HOLE: no docstring
- [test_roots_repo_is_the_worktree_root_where_docs_agents_resolves](RootResolution.test_roots_repo_is_the_worktree_root_where_docs_agents_resolves.md) method: HOLE: no docstring
- [test_roots_durable_is_the_checkout_root_not_the_agent_work_directory](RootResolution.test_roots_durable_is_the_checkout_root_not_the_agent_work_directory.md) method: The silent trap: `durable_agent_work()` returns `<root>/.agent-work`, which
- [test_roots_durable_resolves_a_declaration_without_double_nesting](RootResolution.test_roots_durable_resolves_a_declaration_without_double_nesting.md) method: Resolve a `durable`-rooted declaration through the real producer and assert
- [test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory](RootResolution.test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory.md) method: `durable_root(start)` redirects to the main checkout ONLY for a linked
- [test_roots_outside_a_git_repository_fall_back_visibly_and_never_raise](RootResolution.test_roots_outside_a_git_repository_fall_back_visibly_and_never_raise.md) method: HOLE: no docstring
- [test_roots_from_a_nonexistent_base_never_raise](RootResolution.test_roots_from_a_nonexistent_base_never_raise.md) method: HOLE: no docstring

referenced by: none found
