# tests.test_spine_rail
tests/test_spine_rail.py, 1416 lines, 55 holes

Unit tests for scripts/hooks/spine_rail.py.

Every decision branch is exercised through the pure/handler functions with
constructed spine fixtures. No subprocess of the engine; state-file facts only
-- with ONE deliberate exception (lesson:verify-harness-field-and-drive-real-
writer, #261): test_session_start_real_engine_claim_produces_real_binding_
diff below DOES subprocess the real scripts/checklist_engine.py to produce a
genuinely engine-claimed spine, specifically so the bind-on-resume write path
is proven against production machinery, not a hand-built fixture.

imports stdlib: hashlib, importlib.util, json, pathlib.Path, subprocess, sys
imports third-party: pytest
imported by: none found

```python
_REPO_ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'hooks' / 'spine_rail.py'
_spec = importlib.util.spec_from_file_location('spine_rail', _MODULE_PATH)
sr = importlib.util.module_from_spec(_spec)
_PROBE_FIXTURE = _REPO_ROOT / 'tests' / 'fixtures' / 'probe_payloads.jsonl'
_PROBE_FIXTURE_SHA256 = 'b03536865c8c0215939346447ebd196c579cf051228aa5a9bb75898c10a37402'
_PROBE_FIXTURE_NORMALIZED_BYTES = 13155
_ABSENT = object()
```

- [make_spine](make_spine.md) function: Build a minimal spine dict.
- [write_spine](write_spine.md) function: HOLE: no docstring
- [bind](bind.md) function: Write a NEW-shape binding: one nested entry, keyed by spine_path, for
- [proj](proj.md) function: HOLE: no docstring
- [_probe_wrappers](_probe_wrappers.md) function: Every line of the pinned capture as the probe's CAPTURE WRAPPER dict
- [probe_payloads](probe_payloads.md) function: The real hook payloads, UNWRAPPED out of the capture wrapper's `payload`
- [test_probe_fixture_sha256_pin](test_probe_fixture_sha256_pin.md) function: Pin the fixture's content. If someone hand-edits the capture -- adding a
- [test_probe_fixture_decomposition](test_probe_fixture_decomposition.md) function: State what the capture actually holds, measured here rather than
- [_derive](_derive.md) function: Derive an adversarial row by MUTATING a real captured payload.
- [test_binding_key_composition_table_over_the_six_real_payloads](test_binding_key_composition_table_over_the_six_real_payloads.md) function: HOLE: no docstring
- [test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads](test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads.md) function: Fail closed. Every row below is a real captured payload with ONE field
- [test_binding_key_never_raises_on_junk](test_binding_key_never_raises_on_junk.md) function: HOLE: no docstring
- [_real_post_tool_use](_real_post_tool_use.md) function: A PostToolUse payload built from a REAL captured payload: its own
- [_claim_cmd](_claim_cmd.md) function: HOLE: no docstring
- [_release_cmd](_release_cmd.md) function: HOLE: no docstring
- [_abs_spine](_abs_spine.md) function: HOLE: no docstring
- [_real_parent_payloads](_real_parent_payloads.md) function: HOLE: no docstring
- [_real_subagent_payloads](_real_subagent_payloads.md) function: HOLE: no docstring
- [test_post_claim_subagent_writes_composite_key_bare_set_byte_identical](test_post_claim_subagent_writes_composite_key_bare_set_byte_identical.md) function: A claim carrying agent_id files under sid#agent_id and leaves the bare
- [test_post_claim_two_agent_ids_give_two_independent_key_sets](test_post_claim_two_agent_ids_give_two_independent_key_sets.md) function: Two distinct agent_ids on ONE session_id produce two independent key
- [test_post_release_composite_removes_only_that_agents_entry](test_post_release_composite_removes_only_that_agents_entry.md) function: A release carrying agent_id removes only that agent's entry: the other
- [test_post_release_composite_leaves_bare_nudge_ledger_untouched](test_post_release_composite_leaves_bare_nudge_ledger_untouched.md) function: The nudge / three-strike escape-hatch ledger stays keyed by the BARE
- [test_post_release_parent_still_clears_its_own_bare_nudge_ledger](test_post_release_parent_still_clears_its_own_bare_nudge_ledger.md) function: The other half of the same rule: a top-level release still clears the
- [test_post_claim_unusable_agent_id_writes_no_binding_anywhere](test_post_claim_unusable_agent_id_writes_no_binding_anywhere.md) function: An unresolved identity binds NOTHING -- not under a composite key, and
- [test_post_release_empty_set_cleanup_deletes_composite_key_not_bare](test_post_release_empty_set_cleanup_deletes_composite_key_not_bare.md) function: The single line where a wrong substitution deletes a live parent's whole
- [test_session_view_merges_one_bare_and_two_composite_keys](test_session_view_merges_one_bare_and_two_composite_keys.md) function: The settle a cold critic flagged as otherwise vacuous: on a store with
- [test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key](test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key.md) function: The parent's bare key holds nothing mid-flight; the only mid-flight
- [test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key](test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key.md) function: decide_session_start's read goes through session_view too. The spine
- [test_session_start_bind_on_resume_still_writes_under_the_bare_key](test_session_start_bind_on_resume_still_writes_under_the_bare_key.md) function: SessionStart never carries an agent_id, so a resumed session is by
- [test_active_id_first_non_terminal](test_active_id_first_non_terminal.md) function: HOLE: no docstring
- [test_active_id_all_terminal_returns_none](test_active_id_all_terminal_returns_none.md) function: HOLE: no docstring
- [test_active_id_bad_input](test_active_id_bad_input.md) function: HOLE: no docstring
- [test_journal_seq_counts_nonblank](test_journal_seq_counts_nonblank.md) function: HOLE: no docstring
- [test_journal_seq_missing_is_zero](test_journal_seq_missing_is_zero.md) function: HOLE: no docstring
- [test_reconstruct_current_active](test_reconstruct_current_active.md) function: HOLE: no docstring
- [test_reconstruct_current_done](test_reconstruct_current_done.md) function: HOLE: no docstring
- [test_reconstruct_current_no_lease_line_when_released](test_reconstruct_current_no_lease_line_when_released.md) function: HOLE: no docstring
- [test_same_path_fail_safe_returns_true_on_bad_input](test_same_path_fail_safe_returns_true_on_bad_input.md) function: HOLE: no docstring
- [test_same_path_windows_normcase_sep_equivalence](test_same_path_windows_normcase_sep_equivalence.md) function: HOLE: no docstring
- [test_same_path_distinct_paths_differ](test_same_path_distinct_paths_differ.md) function: HOLE: no docstring
- [test_foreign_worktree_requires_both_present](test_foreign_worktree_requires_both_present.md) function: HOLE: no docstring
- [test_foreign_worktree_true_only_on_positive_mismatch](test_foreign_worktree_true_only_on_positive_mismatch.md) function: HOLE: no docstring
- [test_stop_no_binding_allows](test_stop_no_binding_allows.md) function: HOLE: no docstring
- [test_stop_unreadable_spine_allows](test_stop_unreadable_spine_allows.md) function: HOLE: no docstring
- [test_stop_released_lease_allows](test_stop_released_lease_allows.md) function: HOLE: no docstring
- [test_stop_blocked_status_honest_stop_allows](test_stop_blocked_status_honest_stop_allows.md) function: HOLE: no docstring
- [test_stop_mid_flight_blocks_with_substrings](test_stop_mid_flight_blocks_with_substrings.md) function: HOLE: no docstring
- [test_stop_foreign_worktree_parent_not_blocked](test_stop_foreign_worktree_parent_not_blocked.md) function: HOLE: no docstring
- [test_stop_same_worktree_and_no_cwd_still_block](test_stop_same_worktree_and_no_cwd_still_block.md) function: HOLE: no docstring
- [test_stop_aid_none_lease_active_release_nudge](test_stop_aid_none_lease_active_release_nudge.md) function: HOLE: no docstring
- [test_stop_three_strike_block_block_continue](test_stop_three_strike_block_block_continue.md) function: HOLE: no docstring
- [test_stop_progress_resets_counter](test_stop_progress_resets_counter.md) function: HOLE: no docstring
- [test_stop_blocks_when_any_of_two_entries_is_mid_flight](test_stop_blocks_when_any_of_two_entries_is_mid_flight.md) function: One session_id bound to TWO spines: one already complete+released
- [test_stop_does_not_block_when_all_entries_foreign_or_non_mid_flight](test_stop_does_not_block_when_all_entries_foreign_or_non_mid_flight.md) function: One session_id bound to TWO spines: one is genuinely mid-flight but
- [test_session_start_active_binding_injects_resume](test_session_start_active_binding_injects_resume.md) function: HOLE: no docstring
- [test_session_start_fallback_scan_finds_active](test_session_start_fallback_scan_finds_active.md) function: HOLE: no docstring
- [test_session_start_foreign_skip_same_reinject_fallback_reinject](test_session_start_foreign_skip_same_reinject_fallback_reinject.md) function: HOLE: no docstring
- [test_session_start_no_active_spine_returns_empty](test_session_start_no_active_spine_returns_empty.md) function: HOLE: no docstring
- [test_session_start_released_lease_returns_empty](test_session_start_released_lease_returns_empty.md) function: HOLE: no docstring
- [test_session_start_prefers_own_binding_over_scan_with_multiple_active_spines](test_session_start_prefers_own_binding_over_scan_with_multiple_active_spines.md) function: HOLE: no docstring
- [test_session_start_zero_matches_writes_no_binding](test_session_start_zero_matches_writes_no_binding.md) function: No .agent-work/*/spine.json at all -> the existing zero-match
- [test_session_start_ambiguous_scan_injects_context_but_writes_no_binding](test_session_start_ambiguous_scan_injects_context_but_writes_no_binding.md) function: Two real, on-disk, active-leased spines and NO prior binding for the
- [test_session_start_unambiguous_scan_writes_binding](test_session_start_unambiguous_scan_writes_binding.md) function: Exactly ONE real, on-disk, active-leased spine and no prior binding
- [test_session_start_no_bind_when_sid_missing](test_session_start_no_bind_when_sid_missing.md) function: An unambiguous scan (exactly one active-leased spine) but no
- [test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding](test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding.md) function: The bind-on-unambiguous-scan write must not clobber a sibling
- [test_session_start_real_engine_claim_produces_real_binding_diff](test_session_start_real_engine_claim_produces_real_binding_diff.md) function: The single most important proof on this gate
- [_bash](_bash.md) function: HOLE: no docstring
- [test_post_claim_writes_binding](test_post_claim_writes_binding.md) function: HOLE: no docstring
- [test_post_claim_absolute_file_preserved](test_post_claim_absolute_file_preserved.md) function: HOLE: no docstring
- [test_post_release_deletes_binding_and_nudge](test_post_release_deletes_binding_and_nudge.md) function: HOLE: no docstring
- [test_post_claim_two_different_spines_same_worktree_no_clobber](test_post_claim_two_different_spines_same_worktree_no_clobber.md) function: Two claims under the SAME session_id, for two DIFFERENT spines, both
- [test_post_claim_two_different_spines_different_worktrees_no_clobber](test_post_claim_two_different_spines_different_worktrees_no_clobber.md) function: Same session_id, two DIFFERENT spines resolved from two DIFFERENT
- [test_post_claim_same_spine_reclaim_overwrites_only_itself](test_post_claim_same_spine_reclaim_overwrites_only_itself.md) function: A THIRD claim for the SAME spine (same session_id, same abs_spine)
- [test_post_release_removes_only_matching_entry_sibling_intact](test_post_release_removes_only_matching_entry_sibling_intact.md) function: release removes ONLY the entry for the released spine, leaving a
- [test_post_release_last_entry_removes_sid_key_entirely](test_post_release_last_entry_removes_sid_key_entirely.md) function: Releasing the only bound spine for a session_id removes the sid key
- [test_post_non_engine_command_ignored](test_post_non_engine_command_ignored.md) function: HOLE: no docstring
- [test_post_engine_non_claim_verb_ignored](test_post_engine_non_claim_verb_ignored.md) function: HOLE: no docstring
- [test_main_malformed_stdin_prints_nothing](test_main_malformed_stdin_prints_nothing.md) function: HOLE: no docstring
- [test_main_empty_stdin_prints_nothing](test_main_empty_stdin_prints_nothing.md) function: HOLE: no docstring
- [test_main_unknown_event_prints_nothing](test_main_unknown_event_prints_nothing.md) function: HOLE: no docstring
- [test_main_no_argv_event_fail_open](test_main_no_argv_event_fail_open.md) function: HOLE: no docstring
- [test_main_stop_missing_spine_allows_no_output](test_main_stop_missing_spine_allows_no_output.md) function: HOLE: no docstring
- [test_main_stop_block_emits_json](test_main_stop_block_emits_json.md) function: HOLE: no docstring
- [test_main_post_tool_use_never_errors](test_main_post_tool_use_never_errors.md) function: HOLE: no docstring
- [test_load_binding_corrupt_returns_empty](test_load_binding_corrupt_returns_empty.md) function: HOLE: no docstring
- [test_binding_round_trips_new_nested_shape](test_binding_round_trips_new_nested_shape.md) function: HOLE: no docstring
- [test_old_shape_entry_loads_as_absent_real_fixture](test_old_shape_entry_loads_as_absent_real_fixture.md) function: HOLE: no docstring
- [test_load_binding_mixed_old_and_new_shape_sessions](test_load_binding_mixed_old_and_new_shape_sessions.md) function: HOLE: no docstring
