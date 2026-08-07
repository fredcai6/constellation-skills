# tests.test_init_work_area:RepoRootPlaceholder
class, tests/test_init_work_area.py:449, 51 lines

```python
class RepoRootPlaceholder(TestCase)
```

`<repo-root>` -- a ROBUSTNESS token, not a repair.

Command checks receive no `cwd` and inherit the launcher's, so a relative
check works only while the launcher sits at the repo root: fragile, not
broken. `<repo-root>` lets a template author write a check that does not
depend on where the launcher happened to be. (The five already-shipped
relative checks are tracked separately as #341 and are NOT touched here.)

- [test_repo_root_resolves_to_the_absolute_root](RepoRootPlaceholder.test_repo_root_resolves_to_the_absolute_root.md) method: HOLE: no docstring
- [test_repo_root_is_json_safe_on_windows](RepoRootPlaceholder.test_repo_root_is_json_safe_on_windows.md) method: A backslash value would break instantiate_spine's own json.loads guard.
- [test_instantiate_spine_writes_an_absolute_repo_root_check](RepoRootPlaceholder.test_instantiate_spine_writes_an_absolute_repo_root_check.md) method: HOLE: no docstring
- [test_an_unresolved_repo_root_token_fails_loudly](RepoRootPlaceholder.test_an_unresolved_repo_root_token_fails_loudly.md) method: The guard owns the token, so a regressed resolver cannot ship it.
- [test_the_guard_still_ignores_prose_placeholders](RepoRootPlaceholder.test_the_guard_still_ignores_prose_placeholders.md) method: HOLE: no docstring

referenced by: none found
