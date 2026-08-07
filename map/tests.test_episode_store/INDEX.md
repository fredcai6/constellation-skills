# tests.test_episode_store
tests/test_episode_store.py, 2924 lines, 110 holes

Tests for the episode store (docs/EPISODE_STORE.md): scripts/apply_episode_delta.py,

the validated all-or-nothing writer (gate g2), and scripts/query_episodes.py, the
deterministic retrieval surface plus issue #301's cross-session / cross-worktree
acceptance exercise (gate g3).

Every test writes to a throwaway temp store root (mirroring
tests/test_apply_lessons_delta.py's tempfile.TemporaryDirectory shape), never the real
episodes/ directory, so the repo stays clean and the suite is order-independent.

imports stdlib: contextlib, importlib.util, io, json, os, pathlib.Path, re, shutil, stat, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests' / 'fixtures' / 'episodes'
STORE_TEMPLATE = ROOT / 'episodes'
WRITER_SCRIPT = ROOT / 'scripts' / 'apply_episode_delta.py'
QUERY_SCRIPT = ROOT / 'scripts' / 'query_episodes.py'
_CLASSIFIER = None
```

- [load](load.md) function: HOLE: no docstring
- [load_query](load_query.md) function: HOLE: no docstring
- [episode_path](episode_path.md) function: The on-disk path of an episode under the layout ratified at g4: `active/` for the
- [read_exact](read_exact.md) function: Read a store file with newline translation disabled, as the store itself does.
- [classifier](classifier.md) function: The store's own episode classifier (`episode_id_for`), loaded once.
- [episode_files](episode_files.md) function: Every episode file in the store, by name, across BOTH directories. Replaces the
- [copy_store_scaffolding](copy_store_scaffolding.md) function: Reproduce the REAL tracked store's non-episode files inside a throwaway store
- [create_op](create_op.md) function: HOLE: no docstring
- [EpisodeStoreTestCase](EpisodeStoreTestCase.md) class: Shared setup: a fresh temp store root per test, module loaded fresh.
  - [EpisodeStoreTestCase.setUp](EpisodeStoreTestCase.setUp.md) method: HOLE: no docstring
  - [EpisodeStoreTestCase.tearDown](EpisodeStoreTestCase.tearDown.md) method: HOLE: no docstring
  - [EpisodeStoreTestCase.run_delta](EpisodeStoreTestCase.run_delta.md) method: HOLE: no docstring
  - [EpisodeStoreTestCase.run_fixture](EpisodeStoreTestCase.run_fixture.md) method: HOLE: no docstring
- [RoundTripTests](RoundTripTests.md) class: HOLE: no docstring
  - [RoundTripTests.test_create_writes_well_formed_episode_and_round_trips](RoundTripTests.test_create_writes_well_formed_episode_and_round_trips.md) method: HOLE: no docstring
  - [RoundTripTests.test_artifact_ref_with_trailing_whitespace_round_trips](RoundTripTests.test_artifact_ref_with_trailing_whitespace_round_trips.md) method: HOLE: no docstring
  - [RoundTripTests.test_second_create_same_run_increments_sequence](RoundTripTests.test_second_create_same_run_increments_sequence.md) method: HOLE: no docstring
  - [RoundTripTests.test_create_rejects_explicit_id_in_op](RoundTripTests.test_create_rejects_explicit_id_in_op.md) method: HOLE: no docstring
- [PartitionEnforcementTests](PartitionEnforcementTests.md) class: C2 — a per-bin field-name allowlist rejects a misfiled field from EITHER
  - [PartitionEnforcementTests.test_misfiled_field_fixture_rejected](PartitionEnforcementTests.test_misfiled_field_fixture_rejected.md) method: HOLE: no docstring
  - [PartitionEnforcementTests.test_mechanical_field_under_agent_supplied_rejected](PartitionEnforcementTests.test_mechanical_field_under_agent_supplied_rejected.md) method: HOLE: no docstring
  - [PartitionEnforcementTests.test_agent_supplied_missing_a_required_kind_rejected](PartitionEnforcementTests.test_agent_supplied_missing_a_required_kind_rejected.md) method: HOLE: no docstring
  - [PartitionEnforcementTests.test_unknown_mechanical_field_rejected](PartitionEnforcementTests.test_unknown_mechanical_field_rejected.md) method: HOLE: no docstring
- [ContentGuardTests](ContentGuardTests.md) class: C3 — retire requires a non-empty reason (a); no agent-supplied value may embed a
  - [ContentGuardTests.test_missing_retire_reason_fixture_rejected](ContentGuardTests.test_missing_retire_reason_fixture_rejected.md) method: HOLE: no docstring
  - [ContentGuardTests.test_retire_with_absent_reason_field_rejected](ContentGuardTests.test_retire_with_absent_reason_field_rejected.md) method: HOLE: no docstring
  - [ContentGuardTests.test_newline_injection_fixture_rejected](ContentGuardTests.test_newline_injection_fixture_rejected.md) method: HOLE: no docstring
  - [ContentGuardTests.test_newline_in_task_intent_statement_rejected](ContentGuardTests.test_newline_in_task_intent_statement_rejected.md) method: HOLE: no docstring
  - [ContentGuardTests.test_newline_in_amend_history_rejected](ContentGuardTests.test_newline_in_amend_history_rejected.md) method: HOLE: no docstring
- [LineBoundaryGuardTests](LineBoundaryGuardTests.md) class: REWORK (g2 review BLOCK, defect 1): _reject_newline() must reject every
  - [LineBoundaryGuardTests.test_reject_newline_unit_rejects_every_splitlines_boundary_character](LineBoundaryGuardTests.test_reject_newline_unit_rejects_every_splitlines_boundary_character.md) method: HOLE: no docstring
  - [LineBoundaryGuardTests.test_reject_newline_unit_rejects_trailing_separator](LineBoundaryGuardTests.test_reject_newline_unit_rejects_trailing_separator.md) method: HOLE: no docstring
  - [LineBoundaryGuardTests.test_reject_newline_unit_still_accepts_a_genuinely_single_line_value](LineBoundaryGuardTests.test_reject_newline_unit_still_accepts_a_genuinely_single_line_value.md) method: HOLE: no docstring
  - [LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_create_rejected](LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_create_rejected.md) method: HOLE: no docstring
  - [LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_amend_history_rejected](LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_amend_history_rejected.md) method: HOLE: no docstring
- [AllOrNothingAtomicTests](AllOrNothingAtomicTests.md) class: C4 — an invalid op ANYWHERE in a multi-op delta leaves the store byte-for-byte
  - [AllOrNothingAtomicTests.test_atomic_invalid_op_in_multi_op_delta_leaves_files_unchanged](AllOrNothingAtomicTests.test_atomic_invalid_op_in_multi_op_delta_leaves_files_unchanged.md) method: HOLE: no docstring
  - [AllOrNothingAtomicTests.test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged](AllOrNothingAtomicTests.test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged.md) method: HOLE: no docstring
- [WritePhaseAtomicityTests](WritePhaseAtomicityTests.md) class: REWORK (g2 review BLOCK, defect 2): AllOrNothingAtomicTests above proves
  - [WritePhaseAtomicityTests._snapshot](WritePhaseAtomicityTests._snapshot.md) method: Every file under the store root, by path, as raw bytes -- content AND
  - [WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged](WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged.md) method: HOLE: no docstring
    - [WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged.flaky_write](WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged.flaky_write.md) method: HOLE: no docstring
- [RetirementSeamTests](RetirementSeamTests.md) class: C8 — the retire op's CONTENT effect routes only through apply_retirement() and its
  - [RetirementSeamTests.test_retire_field_diff_matches_worked_example](RetirementSeamTests.test_retire_field_diff_matches_worked_example.md) method: HOLE: no docstring
  - [RetirementSeamTests.test_retire_moves_the_file_from_active_into_retired](RetirementSeamTests.test_retire_moves_the_file_from_active_into_retired.md) method: HOLE: no docstring
- [_assertion_block](_assertion_block.md) function: Extract one "### assertion:<id>.<aid>" block's raw text, up to (not including)
- [SurgicalDisputeTests](SurgicalDisputeTests.md) class: C6 — amend-assertion disputes exactly ONE named field, changing only its
  - [SurgicalDisputeTests.test_dispute_changes_only_the_named_assertion_sibling_untouched](SurgicalDisputeTests.test_dispute_changes_only_the_named_assertion_sibling_untouched.md) method: HOLE: no docstring
  - [SurgicalDisputeTests.test_dispute_targets_a_retired_episode_via_resolve_episode_path](SurgicalDisputeTests.test_dispute_targets_a_retired_episode_via_resolve_episode_path.md) method: HOLE: no docstring
- [QueryTestCase](QueryTestCase.md) class: Adds the retrieval module and a seeding helper to the writer's temp-store setup.
  - [QueryTestCase.setUp](QueryTestCase.setUp.md) method: HOLE: no docstring
  - [QueryTestCase.seed](QueryTestCase.seed.md) method: Write one episode through the ONLY write path (g2's validated delta writer)
  - [QueryTestCase.retire](QueryTestCase.retire.md) method: Retire one episode through the only write path, and return its id.
  - [QueryTestCase.run_query](QueryTestCase.run_query.md) method: Drive query_episodes.py's CLI in-process and return its parsed JSON envelope.
- [QueryFetchTests](QueryFetchTests.md) class: Fetch by id — EPISODE_STORE.md section 8's first primitive, routed through the
  - [QueryFetchTests.test_fetch_by_id_returns_the_whole_record](QueryFetchTests.test_fetch_by_id_returns_the_whole_record.md) method: HOLE: no docstring
  - [QueryFetchTests.test_fetch_calls_the_resolve_episode_path_seam_rather_than_building_a_path](QueryFetchTests.test_fetch_calls_the_resolve_episode_path_seam_rather_than_building_a_path.md) method: HOLE: no docstring
    - [QueryFetchTests.test_fetch_calls_the_resolve_episode_path_seam_rather_than_building_a_path.spy](QueryFetchTests.test_fetch_calls_the_resolve_episode_path_seam_rather_than_building_a_path.spy.md) method: HOLE: no docstring
  - [QueryFetchTests.test_fetch_unknown_id_is_a_visible_failure_not_an_empty_answer](QueryFetchTests.test_fetch_unknown_id_is_a_visible_failure_not_an_empty_answer.md) method: HOLE: no docstring
  - [QueryFetchTests.test_fetch_cli_emits_a_deterministic_json_envelope](QueryFetchTests.test_fetch_cli_emits_a_deterministic_json_envelope.md) method: HOLE: no docstring
- [PathTraversalGuardTests](PathTraversalGuardTests.md) class: Issue #321 — resolve_episode_path() is the ONE seam every id-taking reader
  - [PathTraversalGuardTests.setUp](PathTraversalGuardTests.setUp.md) method: HOLE: no docstring
  - [PathTraversalGuardTests.tearDown](PathTraversalGuardTests.tearDown.md) method: HOLE: no docstring
  - [PathTraversalGuardTests.test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it](PathTraversalGuardTests.test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it.md) method: HOLE: no docstring
- [QueryEnumerateTests](QueryEnumerateTests.md) class: Enumerate every episode — routed through the iter_episode_ids() seam, never a
  - [QueryEnumerateTests.test_enumerate_returns_every_seeded_episode](QueryEnumerateTests.test_enumerate_returns_every_seeded_episode.md) method: HOLE: no docstring
  - [QueryEnumerateTests.test_enumerate_calls_the_iter_episode_ids_seam](QueryEnumerateTests.test_enumerate_calls_the_iter_episode_ids_seam.md) method: HOLE: no docstring
    - [QueryEnumerateTests.test_enumerate_calls_the_iter_episode_ids_seam.spy](QueryEnumerateTests.test_enumerate_calls_the_iter_episode_ids_seam.spy.md) method: HOLE: no docstring
  - [QueryEnumerateTests.test_enumerate_on_an_absent_store_root_is_empty_not_an_error](QueryEnumerateTests.test_enumerate_on_an_absent_store_root_is_empty_not_an_error.md) method: HOLE: no docstring
  - [QueryEnumerateTests.test_enumerate_cli_envelope](QueryEnumerateTests.test_enumerate_cli_envelope.md) method: HOLE: no docstring
- [naive_select_dict_collapse](naive_select_dict_collapse.md) function: A NAIVE select, written the way a reasonable person writes one: read each
- [naive_select_substring](naive_select_substring.md) function: A second naive select: a bare substring search over the file text. This one does
- [QuerySelectTests](QuerySelectTests.md) class: Select by exact field value / set membership — EPISODE_STORE.md section 8. Exact
  - [QuerySelectTests.test_select_matches_a_scalar_field_exactly](QuerySelectTests.test_select_matches_a_scalar_field_exactly.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_is_set_membership_over_several_values](QuerySelectTests.test_select_is_set_membership_over_several_values.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_on_a_list_field_matches_on_intersection](QuerySelectTests.test_select_on_a_list_field_matches_on_intersection.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_matches_whole_values_not_prefixes](QuerySelectTests.test_select_matches_whole_values_not_prefixes.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_on_an_unknown_field_fails_visibly_rather_than_returning_nothing](QuerySelectTests.test_select_on_an_unknown_field_fails_visibly_rather_than_returning_nothing.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_with_no_matches_is_an_empty_set_not_an_error](QuerySelectTests.test_select_with_no_matches_is_an_empty_set_not_an_error.md) method: HOLE: no docstring
  - [QuerySelectTests.test_select_cli_envelope_carries_the_query_and_matched_ids](QuerySelectTests.test_select_cli_envelope_carries_the_query_and_matched_ids.md) method: HOLE: no docstring
- [SilentOmissionTests](SilentOmissionTests.md) class: The failure mode this store's whole design fears: not a crash, not an error — a
  - [SilentOmissionTests.seed_ref_position_fixture](SilentOmissionTests.seed_ref_position_fixture.md) method: Three episodes that all genuinely carry TARGET as an artifact-ref — first,
  - [SilentOmissionTests.test_naive_dict_collapse_silently_omits_two_of_three_matching_episodes](SilentOmissionTests.test_naive_dict_collapse_silently_omits_two_of_three_matching_episodes.md) method: HOLE: no docstring
  - [SilentOmissionTests.test_field_values_returns_every_artifact_ref_not_just_the_last](SilentOmissionTests.test_field_values_returns_every_artifact_ref_not_just_the_last.md) method: HOLE: no docstring
  - [SilentOmissionTests.test_a_bare_string_is_refused_rather_than_matched_character_by_character](SilentOmissionTests.test_a_bare_string_is_refused_rather_than_matched_character_by_character.md) method: HOLE: no docstring
  - [SilentOmissionTests.test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss](SilentOmissionTests.test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss.md) method: HOLE: no docstring
  - [SilentOmissionTests.test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped](SilentOmissionTests.test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped.md) method: A third shape, found by sweeping for the class rather than by a review note.
- [naive_neighbours_first_key_wins](naive_neighbours_first_key_wins.md) function: A NAIVE neighbour enumeration: try each join key in turn and return as soon as
- [QueryNeighbourTests](QueryNeighbourTests.md) class: Enumerate neighbours — for episode E, every OTHER episode sharing at least one
  - [QueryNeighbourTests.test_neighbours_by_shared_artifact_ref](QueryNeighbourTests.test_neighbours_by_shared_artifact_ref.md) method: HOLE: no docstring
  - [QueryNeighbourTests.test_neighbours_by_shared_role_and_spine_step_pair](QueryNeighbourTests.test_neighbours_by_shared_role_and_spine_step_pair.md) method: HOLE: no docstring
  - [QueryNeighbourTests.test_an_episode_is_never_its_own_neighbour](QueryNeighbourTests.test_an_episode_is_never_its_own_neighbour.md) method: HOLE: no docstring
  - [QueryNeighbourTests.test_neighbours_of_an_unknown_episode_fails_visibly](QueryNeighbourTests.test_neighbours_of_an_unknown_episode_fails_visibly.md) method: HOLE: no docstring
  - [QueryNeighbourTests.test_naive_first_key_wins_silently_omits_the_other_join_key](QueryNeighbourTests.test_naive_first_key_wins_silently_omits_the_other_join_key.md) method: HOLE: no docstring
  - [QueryNeighbourTests.test_neighbours_cli_envelope](QueryNeighbourTests.test_neighbours_cli_envelope.md) method: HOLE: no docstring
- [SeparateProcessMixin](SeparateProcessMixin.md) class: Launch a real, separately-booted Python interpreter and observe its OS pid.
  - [SeparateProcessMixin.run_in_separate_process](SeparateProcessMixin.run_in_separate_process.md) method: HOLE: no docstring
  - [SeparateProcessMixin.seed_in_separate_process](SeparateProcessMixin.seed_in_separate_process.md) method: HOLE: no docstring
- [CrossSessionRetrievalTests](CrossSessionRetrievalTests.md) class: C2 — the issue's headline acceptance criterion, EXERCISED: an episode seeded in
  - [CrossSessionRetrievalTests.test_episode_seeded_in_one_process_is_retrievable_in_a_freshly_booted_one](CrossSessionRetrievalTests.test_episode_seeded_in_one_process_is_retrievable_in_a_freshly_booted_one.md) method: HOLE: no docstring
  - [CrossSessionRetrievalTests.test_the_cross_session_exercise_is_not_vacuous](CrossSessionRetrievalTests.test_the_cross_session_exercise_is_not_vacuous.md) method: Falsification guard. The test above would be worthless if the retrieving
  - [CrossSessionRetrievalTests.test_a_third_session_enumerates_what_the_first_two_never_told_it_about](CrossSessionRetrievalTests.test_a_third_session_enumerates_what_the_first_two_never_told_it_about.md) method: HOLE: no docstring
- [force_rmtree](force_rmtree.md) function: shutil.rmtree with the Windows read-only escape hatch. Git marks objects under
  - [force_rmtree.on_error](force_rmtree.on_error.md) method: HOLE: no docstring
- [CrossWorktreeSharingTests](CrossWorktreeSharingTests.md) class: C3 — cross-worktree sharing, exercised THROUGH GIT (EPISODE_STORE.md section 9).
  - [CrossWorktreeSharingTests.setUp](CrossWorktreeSharingTests.setUp.md) method: HOLE: no docstring
  - [CrossWorktreeSharingTests.cleanup_repo](CrossWorktreeSharingTests.cleanup_repo.md) method: HOLE: no docstring
  - [CrossWorktreeSharingTests.git](CrossWorktreeSharingTests.git.md) method: HOLE: no docstring
  - [CrossWorktreeSharingTests.query_in](CrossWorktreeSharingTests.query_in.md) method: Run retrieval in a freshly booted interpreter whose CWD is that worktree,
  - [CrossWorktreeSharingTests.test_episode_committed_in_one_worktree_is_retrievable_from_another](CrossWorktreeSharingTests.test_episode_committed_in_one_worktree_is_retrievable_from_another.md) method: HOLE: no docstring
  - [CrossWorktreeSharingTests.test_working_tree_bytes_are_not_the_cross_worktree_identity](CrossWorktreeSharingTests.test_working_tree_bytes_are_not_the_cross_worktree_identity.md) method: A finding, pinned as a test rather than left as prose.
  - [CrossWorktreeSharingTests.test_the_two_worktrees_do_not_share_a_directory](CrossWorktreeSharingTests.test_the_two_worktrees_do_not_share_a_directory.md) method: Falsification guard for the exercise above. If the two worktrees were secretly
- [NonForeclosureTests](NonForeclosureTests.md) class: C4 — the priority-1 obligation, exercised by retrieval.
  - [NonForeclosureTests.assertion_block](NonForeclosureTests.assertion_block.md) method: The exact bytes of one `### assertion:<id>.<aid>` block, from its heading up
  - [NonForeclosureTests.test_disputing_one_assertion_leaves_its_siblings_byte_identical](NonForeclosureTests.test_disputing_one_assertion_leaves_its_siblings_byte_identical.md) method: HOLE: no docstring
  - [NonForeclosureTests.test_the_mechanical_bin_and_retirement_block_are_untouched_by_a_dispute](NonForeclosureTests.test_the_mechanical_bin_and_retirement_block_are_untouched_by_a_dispute.md) method: HOLE: no docstring
  - [NonForeclosureTests.test_a_disputed_episode_is_still_retrievable_and_reports_its_standing](NonForeclosureTests.test_a_disputed_episode_is_still_retrievable_and_reports_its_standing.md) method: HOLE: no docstring
- [MechanicalOnlyRetrievalTests](MechanicalOnlyRetrievalTests.md) class: C5 — retrieval is exact-match and set-membership only (EPISODE_STORE.md section
  - [MechanicalOnlyRetrievalTests.test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written](MechanicalOnlyRetrievalTests.test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written.md) method: HOLE: no docstring
    - [MechanicalOnlyRetrievalTests.test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written.build](MechanicalOnlyRetrievalTests.test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written.build.md) method: HOLE: no docstring
  - [MechanicalOnlyRetrievalTests.test_results_carry_no_score_rank_or_similarity_field](MechanicalOnlyRetrievalTests.test_results_carry_no_score_rank_or_similarity_field.md) method: HOLE: no docstring
  - [MechanicalOnlyRetrievalTests.test_the_module_imports_no_ranking_or_embedding_machinery](MechanicalOnlyRetrievalTests.test_the_module_imports_no_ranking_or_embedding_machinery.md) method: HOLE: no docstring
  - [MechanicalOnlyRetrievalTests.test_neighbours_are_not_ordered_by_how_many_join_keys_they_share](MechanicalOnlyRetrievalTests.test_neighbours_are_not_ordered_by_how_many_join_keys_they_share.md) method: HOLE: no docstring
- [RatifiedLayoutTests](RatifiedLayoutTests.md) class: g4 — the retirement layout is RATIFIED and BOUND. Tommy's ruling, verbatim:
  - [RatifiedLayoutTests.test_a_new_episode_is_written_under_active](RatifiedLayoutTests.test_a_new_episode_is_written_under_active.md) method: HOLE: no docstring
  - [RatifiedLayoutTests.test_retiring_moves_the_file_into_retired](RatifiedLayoutTests.test_retiring_moves_the_file_into_retired.md) method: HOLE: no docstring
  - [RatifiedLayoutTests.test_the_layout_adapter_switch_is_gone](RatifiedLayoutTests.test_the_layout_adapter_switch_is_gone.md) method: HOLE: no docstring
  - [RatifiedLayoutTests.test_membership_is_a_directory_fact_not_a_parsed_field](RatifiedLayoutTests.test_membership_is_a_directory_fact_not_a_parsed_field.md) method: HOLE: no docstring
- [RetirementDependentRetrievalTests](RetirementDependentRetrievalTests.md) class: C3 — a retired episode is ABSENT from ordinary retrieval and PRESENT in
  - [RetirementDependentRetrievalTests.test_a_retired_episode_leaves_ordinary_retrieval_and_stays_in_history](RetirementDependentRetrievalTests.test_a_retired_episode_leaves_ordinary_retrieval_and_stays_in_history.md) method: HOLE: no docstring
  - [RetirementDependentRetrievalTests.test_the_archive_is_opt_in_not_opt_out](RetirementDependentRetrievalTests.test_the_archive_is_opt_in_not_opt_out.md) method: The ruling's second half: retired/ is an archive, not a second live search
  - [RetirementDependentRetrievalTests.test_retirement_is_a_move_not_a_deletion](RetirementDependentRetrievalTests.test_retirement_is_a_move_not_a_deletion.md) method: HOLE: no docstring
  - [RetirementDependentRetrievalTests.test_fetch_by_id_reaches_the_archive_because_it_is_a_lookup_not_a_search](RetirementDependentRetrievalTests.test_fetch_by_id_reaches_the_archive_because_it_is_a_lookup_not_a_search.md) method: HOLE: no docstring
  - [RetirementDependentRetrievalTests.test_select_and_neighbours_respect_retirement_in_both_directions](RetirementDependentRetrievalTests.test_select_and_neighbours_respect_retirement_in_both_directions.md) method: HOLE: no docstring
  - [RetirementDependentRetrievalTests.test_the_cli_states_which_universe_it_answered_from](RetirementDependentRetrievalTests.test_the_cli_states_which_universe_it_answered_from.md) method: HOLE: no docstring
  - [RetirementDependentRetrievalTests.test_retiring_the_only_episode_of_a_run_does_not_free_its_sequence_number](RetirementDependentRetrievalTests.test_retiring_the_only_episode_of_a_run_does_not_free_its_sequence_number.md) method: HOLE: no docstring
- [naive_flat_glob_enumeration](naive_flat_glob_enumeration.md) function: Trap 1 — a glob that misses a subdirectory.
- [naive_history_inclusive_forgetting_the_union](naive_history_inclusive_forgetting_the_union.md) function: Trap 2 — a history-inclusive enumeration that forgets to union both directories.
- [naive_layout_listing_as_ids](naive_layout_listing_as_ids.md) function: Trap 4 — a directory listing read as a list of episode ids.
- [naive_status_grep_membership](naive_status_grep_membership.md) function: The ORIGINAL trap, kept and adapted: ordinary search as a content-parsing
- [HalfRetirementSafetyTests](HalfRetirementSafetyTests.md) class: C6 — the store is never left HALF-RETIRED.
  - [HalfRetirementSafetyTests._sets](HalfRetirementSafetyTests._sets.md) method: (ordinary-set ids, archive ids) read straight off the filesystem, without
  - [HalfRetirementSafetyTests.assert_consistent](HalfRetirementSafetyTests.assert_consistent.md) method: The invariant, stated once: an id is in EXACTLY ONE of the two sets, and the
  - [HalfRetirementSafetyTests.test_the_write_plan_cannot_express_a_half_retirement](HalfRetirementSafetyTests.test_the_write_plan_cannot_express_a_half_retirement.md) method: HOLE: no docstring
  - [HalfRetirementSafetyTests.test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired](HalfRetirementSafetyTests.test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired.md) method: HOLE: no docstring
    - [HalfRetirementSafetyTests.test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired.failing_place](HalfRetirementSafetyTests.test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired.failing_place.md) method: HOLE: no docstring
  - [HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole](HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole.md) method: The window binding Option A actually opened, and the one this gate owes.
    - [HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole.failing_remove](HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole.failing_remove.md) method: HOLE: no docstring
  - [HalfRetirementSafetyTests.test_a_half_retired_store_is_reported_rather_than_answered_around](HalfRetirementSafetyTests.test_a_half_retired_store_is_reported_rather_than_answered_around.md) method: Compensation covers every failure the process survives to observe; a hard kill
  - [HalfRetirementSafetyTests.test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan](HalfRetirementSafetyTests.test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan.md) method: The other half of "loud", and the half that was missing.
  - [HalfRetirementSafetyTests.test_a_successful_retirement_is_whole](HalfRetirementSafetyTests.test_a_successful_retirement_is_whole.md) method: HOLE: no docstring
- [RelocatedSilentOmissionTests](RelocatedSilentOmissionTests.md) class: Option A relocated the silent-omission class; it did not remove it. One fixture per
  - [RelocatedSilentOmissionTests.test_trap1_a_flat_glob_misses_the_subdirectory_and_says_nothing](RelocatedSilentOmissionTests.test_trap1_a_flat_glob_misses_the_subdirectory_and_says_nothing.md) method: HOLE: no docstring
  - [RelocatedSilentOmissionTests.test_trap2_history_inclusive_that_forgets_the_union_returns_half](RelocatedSilentOmissionTests.test_trap2_history_inclusive_that_forgets_the_union_returns_half.md) method: HOLE: no docstring
  - [RelocatedSilentOmissionTests.test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped](RelocatedSilentOmissionTests.test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped.md) method: The real migration hazard, and the one most likely to be missed.
  - [RelocatedSilentOmissionTests.test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident](RelocatedSilentOmissionTests.test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident.md) method: `episodes/README.md` already lives at the flat root, so the stray check above
  - [RelocatedSilentOmissionTests.test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused](RelocatedSilentOmissionTests.test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused.md) method: The mirror image of trap 3, and the one that actually shipped.
  - [RelocatedSilentOmissionTests.test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted](RelocatedSilentOmissionTests.test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted.md) method: Every scan in this store is one level deep, so anything a level further down
  - [RelocatedSilentOmissionTests.test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames](RelocatedSilentOmissionTests.test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames.md) method: The mechanism behind trap 4, asserted directly.
  - [RelocatedSilentOmissionTests.test_the_original_trap_a_disputed_episode_is_not_a_retired_one](RelocatedSilentOmissionTests.test_the_original_trap_a_disputed_episode_is_not_a_retired_one.md) method: The fixture that started this whole thread, carried forward. An episode whose
  - [RelocatedSilentOmissionTests.test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets](RelocatedSilentOmissionTests.test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets.md) method: Under the rejected Option B this needed a defense (a line-anchored filter, plus
- [AbsentStoreTests](AbsentStoreTests.md) class: Trap 5 — a store that is not there is REFUSED, never answered as empty.
  - [AbsentStoreTests.test_a_store_root_that_does_not_exist_is_refused](AbsentStoreTests.test_a_store_root_that_does_not_exist_is_refused.md) method: HOLE: no docstring
  - [AbsentStoreTests.test_a_missing_layout_directory_is_refused_rather_than_read_as_empty](AbsentStoreTests.test_a_missing_layout_directory_is_refused_rather_than_read_as_empty.md) method: HOLE: no docstring
  - [AbsentStoreTests.test_a_reader_never_creates_the_store_it_could_not_find](AbsentStoreTests.test_a_reader_never_creates_the_store_it_could_not_find.md) method: HOLE: no docstring
  - [AbsentStoreTests.test_the_writer_bootstraps_a_brand_new_store_root](AbsentStoreTests.test_the_writer_bootstraps_a_brand_new_store_root.md) method: The other half of the rule: a create into a store root that does not exist yet
- [ShippedStoreTests](ShippedStoreTests.md) class: The tests that would have caught the g4 BLOCK, and the reason they did not exist.
  - [ShippedStoreTests.test_the_shipped_stores_own_placeholders_read_end_to_end](ShippedStoreTests.test_the_shipped_stores_own_placeholders_read_end_to_end.md) method: HOLE: no docstring
  - [ShippedStoreTests.test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it](ShippedStoreTests.test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it.md) method: Read-only, against the REAL `episodes/` — no temp store, nothing written.
- [ConsolidationCompanionTests](ConsolidationCompanionTests.md) class: C5 — the #308 companion is not precluded.
  - [ConsolidationCompanionTests.cluster](ConsolidationCompanionTests.cluster.md) method: Three episodes joined on a shared artifact-ref — the join key section 6 already
  - [ConsolidationCompanionTests.test_retiring_one_member_leaves_the_rest_findable_ordinarily](ConsolidationCompanionTests.test_retiring_one_member_leaves_the_rest_findable_ordinarily.md) method: HOLE: no docstring
  - [ConsolidationCompanionTests.test_the_retired_member_stays_reachable_three_ways](ConsolidationCompanionTests.test_the_retired_member_stays_reachable_three_ways.md) method: HOLE: no docstring
  - [ConsolidationCompanionTests.test_walking_back_from_an_archived_member_to_its_live_cluster](ConsolidationCompanionTests.test_walking_back_from_an_archived_member_to_its_live_cluster.md) method: The move #308 actually needs: start from a retired episode (the anchor is
  - [ConsolidationCompanionTests.test_retiring_every_member_loses_nothing](ConsolidationCompanionTests.test_retiring_every_member_loses_nothing.md) method: HOLE: no docstring
- [SeamContainmentTests](SeamContainmentTests.md) class: C2 — the ratified layout is bound at the seam set and NOWHERE else.
  - [SeamContainmentTests.test_query_module_inlines_no_status_check_and_no_directory_check](SeamContainmentTests.test_query_module_inlines_no_status_check_and_no_directory_check.md) method: HOLE: no docstring
  - [SeamContainmentTests.test_retrieval_reaches_the_layout_only_through_the_seams](SeamContainmentTests.test_retrieval_reaches_the_layout_only_through_the_seams.md) method: The direct proof that the binding is contained: move the layout by replacing
  - [SeamContainmentTests.test_the_writer_names_the_directories_only_inside_the_seam_block](SeamContainmentTests.test_the_writer_names_the_directories_only_inside_the_seam_block.md) method: C2's other half. query_episodes.py may not name the directories at all; the
  - [SeamContainmentTests.test_the_membership_seam_answers_for_both_sets](SeamContainmentTests.test_the_membership_seam_answers_for_both_sets.md) method: HOLE: no docstring
- [FloorInterpreterPortabilityTests](FloorInterpreterPortabilityTests.md) class: The store must run on the OLDEST interpreter it claims to support, not merely on
  - [FloorInterpreterPortabilityTests.floor_interpreter](FloorInterpreterPortabilityTests.floor_interpreter.md) method: A launcher that really is the declared floor version, or None.
  - [FloorInterpreterPortabilityTests.test_the_declared_floor_matches_the_version_ci_actually_pins](FloorInterpreterPortabilityTests.test_the_declared_floor_matches_the_version_ci_actually_pins.md) method: HOLE: no docstring
  - [FloorInterpreterPortabilityTests.test_the_store_actually_runs_on_the_floor_interpreter](FloorInterpreterPortabilityTests.test_the_store_actually_runs_on_the_floor_interpreter.md) method: HOLE: no docstring
