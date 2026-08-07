# tests.test_init_work_area
tests/test_init_work_area.py, 503 lines, 35 holes

HOLE: no docstring

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest, unittest.mock
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SPINE_FIXTURE = json.dumps({'work_id': '<work-id>', 'session_id': '<commander-session-id>', 'tasks': {'...
GENERIC_SPINE_FIXTURE = json.dumps({'work_id': '<work-id>', 'tasks': {'init': {'postconditions': [{'check': {'k...
```

- [load](load.md) function: HOLE: no docstring
- [write_fixture](write_fixture.md) function: HOLE: no docstring
- [write_generic_fixture](write_generic_fixture.md) function: HOLE: no docstring
- [InitWorkAreaTests](InitWorkAreaTests.md) class: HOLE: no docstring
  - [InitWorkAreaTests.test_creates_structure](InitWorkAreaTests.test_creates_structure.md) method: HOLE: no docstring
  - [InitWorkAreaTests.test_idempotent](InitWorkAreaTests.test_idempotent.md) method: HOLE: no docstring
  - [InitWorkAreaTests.test_refuses_a_root_that_is_already_the_agent_work_dir](InitWorkAreaTests.test_refuses_a_root_that_is_already_the_agent_work_dir.md) method: HOLE: no docstring
  - [InitWorkAreaTests.test_refusal_names_the_parent_as_the_intended_root](InitWorkAreaTests.test_refusal_names_the_parent_as_the_intended_root.md) method: HOLE: no docstring
  - [InitWorkAreaTests.test_a_root_merely_containing_agent_work_is_fine](InitWorkAreaTests.test_a_root_merely_containing_agent_work_is_fine.md) method: HOLE: no docstring
- [SpineInstantiationTests](SpineInstantiationTests.md) class: HOLE: no docstring
  - [SpineInstantiationTests.test_bare_init_writes_no_spine](SpineInstantiationTests.test_bare_init_writes_no_spine.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_instantiate_resolves_all_placeholders_with_explicit_skill_dir](SpineInstantiationTests.test_instantiate_resolves_all_placeholders_with_explicit_skill_dir.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_autodetect_collapses_skill_dir_scripts_to_top_level](SpineInstantiationTests.test_autodetect_collapses_skill_dir_scripts_to_top_level.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_no_clobber_without_force](SpineInstantiationTests.test_no_clobber_without_force.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_force_overwrites](SpineInstantiationTests.test_force_overwrites.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_generic_skill_dir_token_resolves_with_explicit_skill_dir](SpineInstantiationTests.test_generic_skill_dir_token_resolves_with_explicit_skill_dir.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_generic_skill_dir_token_autodetects_without_skill_dir](SpineInstantiationTests.test_generic_skill_dir_token_autodetects_without_skill_dir.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_generic_skill_dir_token_bare_falls_back_to_root_without_scripts_dir](SpineInstantiationTests.test_generic_skill_dir_token_bare_falls_back_to_root_without_scripts_dir.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_explicit_skill_dir_without_scripts_fails_visibly](SpineInstantiationTests.test_explicit_skill_dir_without_scripts_fails_visibly.md) method: HOLE: no docstring
  - [SpineInstantiationTests.test_commander_token_byte_identical_alongside_generic_token](SpineInstantiationTests.test_commander_token_byte_identical_alongside_generic_token.md) method: HOLE: no docstring
- [ShippedSpineTemplatesTests](ShippedSpineTemplatesTests.md) class: Every shipped spine template must materialize with no residual work-id
  - [ShippedSpineTemplatesTests._materialize](ShippedSpineTemplatesTests._materialize.md) method: HOLE: no docstring
  - [ShippedSpineTemplatesTests.test_admiral_spine_resolves_work_id_cleanly](ShippedSpineTemplatesTests.test_admiral_spine_resolves_work_id_cleanly.md) method: HOLE: no docstring
  - [ShippedSpineTemplatesTests.test_admiral_spine_resolves_admiral_skill_dir_and_session_id_cleanly](ShippedSpineTemplatesTests.test_admiral_spine_resolves_admiral_skill_dir_and_session_id_cleanly.md) method: HOLE: no docstring
  - [ShippedSpineTemplatesTests.test_commander_and_explorer_spines_resolve_work_id_cleanly](ShippedSpineTemplatesTests.test_commander_and_explorer_spines_resolve_work_id_cleanly.md) method: HOLE: no docstring
- [GenericRoleTokenTests](GenericRoleTokenTests.md) class: resolve_spine discovers <role-skill-dir>/<role-session-id> tokens by
  - [GenericRoleTokenTests.test_admiral_role_tokens_resolve_with_explicit_skill_dir](GenericRoleTokenTests.test_admiral_role_tokens_resolve_with_explicit_skill_dir.md) method: HOLE: no docstring
  - [GenericRoleTokenTests.test_hyphenated_role_name_skill_dir_token_resolves](GenericRoleTokenTests.test_hyphenated_role_name_skill_dir_token_resolves.md) method: HOLE: no docstring
- [ResolverPlaceholderAssertionTests](ResolverPlaceholderAssertionTests.md) class: Direct unit coverage of the post-init hard check, independent of
  - [ResolverPlaceholderAssertionTests.test_raises_on_leftover_work_id](ResolverPlaceholderAssertionTests.test_raises_on_leftover_work_id.md) method: HOLE: no docstring
  - [ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_skill_dir](ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_skill_dir.md) method: HOLE: no docstring
  - [ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_session_id](ResolverPlaceholderAssertionTests.test_raises_on_leftover_role_session_id.md) method: HOLE: no docstring
  - [ResolverPlaceholderAssertionTests.test_does_not_raise_on_benign_prose_placeholders](ResolverPlaceholderAssertionTests.test_does_not_raise_on_benign_prose_placeholders.md) method: HOLE: no docstring
  - [ResolverPlaceholderAssertionTests.test_instantiate_spine_leaves_non_resolver_placeholders_alone](ResolverPlaceholderAssertionTests.test_instantiate_spine_leaves_non_resolver_placeholders_alone.md) method: HOLE: no docstring
  - [ResolverPlaceholderAssertionTests.test_instantiate_spine_raises_when_a_resolver_owned_token_cannot_resolve](ResolverPlaceholderAssertionTests.test_instantiate_spine_raises_when_a_resolver_owned_token_cannot_resolve.md) method: HOLE: no docstring
- [RepoRootPlaceholder](RepoRootPlaceholder.md) class: `<repo-root>` -- a ROBUSTNESS token, not a repair.
  - [RepoRootPlaceholder.test_repo_root_resolves_to_the_absolute_root](RepoRootPlaceholder.test_repo_root_resolves_to_the_absolute_root.md) method: HOLE: no docstring
  - [RepoRootPlaceholder.test_repo_root_is_json_safe_on_windows](RepoRootPlaceholder.test_repo_root_is_json_safe_on_windows.md) method: A backslash value would break instantiate_spine's own json.loads guard.
  - [RepoRootPlaceholder.test_instantiate_spine_writes_an_absolute_repo_root_check](RepoRootPlaceholder.test_instantiate_spine_writes_an_absolute_repo_root_check.md) method: HOLE: no docstring
  - [RepoRootPlaceholder.test_an_unresolved_repo_root_token_fails_loudly](RepoRootPlaceholder.test_an_unresolved_repo_root_token_fails_loudly.md) method: The guard owns the token, so a regressed resolver cannot ship it.
  - [RepoRootPlaceholder.test_the_guard_still_ignores_prose_placeholders](RepoRootPlaceholder.test_the_guard_still_ignores_prose_placeholders.md) method: HOLE: no docstring
