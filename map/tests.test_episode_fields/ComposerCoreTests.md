# tests.test_episode_fields:ComposerCoreTests
class, tests/test_episode_fields.py:187, 79 lines

```python
class ComposerCoreTests(TestCase)
```

Every field is proven by TRACKING a non-default value, never by presence.

Presence is what `validate_delta()` checks, and nine constants satisfy it. These
tests are the oracle it is not: each asserts the composer followed engine state
that a constant could not have guessed.

- [test_run_tracks_the_checklists_own_work_id](ComposerCoreTests.test_run_tracks_the_checklists_own_work_id.md) method: HOLE: no docstring
- [test_role_tracks_the_leases_claimed_by](ComposerCoreTests.test_role_tracks_the_leases_claimed_by.md) method: HOLE: no docstring
- [test_role_is_refused_when_no_lease_was_ever_claimed](ComposerCoreTests.test_role_is_refused_when_no_lease_was_ever_claimed.md) method: Refuse, never fabricate: a lease-less run has no role to report, and
- [test_spine_step_tracks_the_engines_own_selector_not_the_first_item](ComposerCoreTests.test_spine_step_tracks_the_engines_own_selector_not_the_first_item.md) method: The active step is the first NON-TERMINAL item. A composer that returned
- [test_spine_step_agrees_with_the_imported_selector_it_must_not_re_derive](ComposerCoreTests.test_spine_step_agrees_with_the_imported_selector_it_must_not_re_derive.md) method: HOLE: no docstring
- [test_a_fully_terminal_checklist_refuses_rather_than_naming_a_step](ComposerCoreTests.test_a_fully_terminal_checklist_refuses_rather_than_naming_a_step.md) method: HOLE: no docstring
- [test_rework_count_tracks_the_active_steps_own_counter](ComposerCoreTests.test_rework_count_tracks_the_active_steps_own_counter.md) method: HOLE: no docstring
- [test_artifact_ref_tracks_the_real_staged_diff](ComposerCoreTests.test_artifact_ref_tracks_the_real_staged_diff.md) method: HOLE: no docstring
- [test_project_is_refused_rather_than_defaulted_outside_a_repository](ComposerCoreTests.test_project_is_refused_rather_than_defaulted_outside_a_repository.md) method: HOLE: no docstring

calls stdlib: unittest.skipUnless
reads internal: GIT
reads stdlib: unittest (module)

referenced by: none found
