# tests.test_episode_store:RelocatedSilentOmissionTests
class, tests/test_episode_store.py:2182, 247 lines

```python
class RelocatedSilentOmissionTests(QueryTestCase)
```

Option A relocated the silent-omission class; it did not remove it. One fixture per

relocated trap, each run against the SAME store as the real primitive, so the naive
answer's shortness is demonstrated rather than asserted.

- [test_trap1_a_flat_glob_misses_the_subdirectory_and_says_nothing](RelocatedSilentOmissionTests.test_trap1_a_flat_glob_misses_the_subdirectory_and_says_nothing.md) method: HOLE: no docstring
- [test_trap2_history_inclusive_that_forgets_the_union_returns_half](RelocatedSilentOmissionTests.test_trap2_history_inclusive_that_forgets_the_union_returns_half.md) method: HOLE: no docstring
- [test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped](RelocatedSilentOmissionTests.test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped.md) method: The real migration hazard, and the one most likely to be missed.
- [test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident](RelocatedSilentOmissionTests.test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident.md) method: `episodes/README.md` already lives at the flat root, so the stray check above
- [test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused](RelocatedSilentOmissionTests.test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused.md) method: The mirror image of trap 3, and the one that actually shipped.
- [test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted](RelocatedSilentOmissionTests.test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted.md) method: Every scan in this store is one level deep, so anything a level further down
- [test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames](RelocatedSilentOmissionTests.test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames.md) method: The mechanism behind trap 4, asserted directly.
- [test_the_original_trap_a_disputed_episode_is_not_a_retired_one](RelocatedSilentOmissionTests.test_the_original_trap_a_disputed_episode_is_not_a_retired_one.md) method: The fixture that started this whole thread, carried forward. An episode whose
- [test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets](RelocatedSilentOmissionTests.test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets.md) method: Under the rejected Option B this needed a defense (a line-anchored filter, plus

referenced by: none found
