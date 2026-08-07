# tests.test_init_work_area:GenericRoleTokenTests
class, tests/test_init_work_area.py:327, 48 lines

```python
class GenericRoleTokenTests(TestCase)
```

resolve_spine discovers <role-skill-dir>/<role-session-id> tokens by

pattern rather than a hardcoded per-role list, so a role invented after
this fix (or one whose skill directory name itself carries a hyphen, e.g.
a hypothetical lessons-auditor) does not recur the #114/#154 defect.

- [test_admiral_role_tokens_resolve_with_explicit_skill_dir](GenericRoleTokenTests.test_admiral_role_tokens_resolve_with_explicit_skill_dir.md) method: HOLE: no docstring
- [test_hyphenated_role_name_skill_dir_token_resolves](GenericRoleTokenTests.test_hyphenated_role_name_skill_dir_token_resolves.md) method: HOLE: no docstring

referenced by: none found
