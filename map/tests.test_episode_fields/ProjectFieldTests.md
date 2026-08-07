# tests.test_episode_fields:ProjectFieldTests
class, tests/test_episode_fields.py:96, 53 lines

```python
@unittest.skipUnless(GIT, 'git not available on PATH')
class ProjectFieldTests(TestCase)
```

`project` must name the REPOSITORY, identically from every worktree.

It is sourced from repository topology (`git rev-parse --git-common-dir`), never
from the work-area helper, because those answer different questions: topology vs
writability. Under an epic lease the writability answer is the worktree, which is
the wrong answer for this field.

- [setUp](ProjectFieldTests.setUp.md) method: HOLE: no docstring
- [tearDown](ProjectFieldTests.tearDown.md) method: HOLE: no docstring
- [test_plain_checkout_yields_the_checkout_name](ProjectFieldTests.test_plain_checkout_yields_the_checkout_name.md) method: HOLE: no docstring
- [test_linked_worktree_under_an_active_epic_lease_still_names_the_repository](ProjectFieldTests.test_linked_worktree_under_an_active_epic_lease_still_names_the_repository.md) method: HOLE: no docstring
- [test_linked_worktree_agrees_with_the_main_checkout](ProjectFieldTests.test_linked_worktree_agrees_with_the_main_checkout.md) method: The join this field exists for: the same repository, two worktrees, one
- [test_non_repository_refuses_rather_than_guessing](ProjectFieldTests.test_non_repository_refuses_rather_than_guessing.md) method: Refuse, never fabricate. A worktree-derived (or cwd-derived) fallback would

referenced by: none found
