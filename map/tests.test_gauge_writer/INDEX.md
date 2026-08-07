# tests.test_gauge_writer
tests/test_gauge_writer.py, 1347 lines, 21 holes

Unit tests for scripts/hooks/gauge_writer_hook.py.

Fixture-based against tests/fixtures/golden_transcript.jsonl (a hand-built
transcript modeled on a real Claude Code session transcript captured and
inspected live during implementation -- see docs/GAUGE_WRITER_HOOK.md for the
exact schema this depends on). No real filesystem paths outside tmp_path; no
network; no dependency on a live harness.

imports stdlib: importlib.util, inspect, json, os, pathlib.Path, threading, time
imports third-party: pytest
imported by: none found

```python
_HOOKS_DIR = Path(__file__).resolve().parents[1] / 'scripts' / 'hooks'
_FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'golden_transcript.jsonl'
sr = _load('spine_rail', _HOOKS_DIR / 'spine_rail.py')
gw = _load('gauge_writer_hook', _HOOKS_DIR / 'gauge_writer_hook.py')
EXPECTED_MODEL = 'claude-opus-4-8'
EXPECTED_FILL = (3 + 1200 + 158000) / 1000000
_REAL_SUBAGENT_FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'real_subagent_transcript.jsonl'
_PARENT_AGENT_ID = 'af45cec63b2835a40'
_MAINCHAIN_TAIL_FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'subagent_transcript_with_mainchain_tail...
_REAL_SUBAGENT_TOKENS = 4823 + 1088 + 15111
_REAL_SUBAGENT_OBSERVED_AT = '2026-07-07T05:30:40.581Z'
_TAIL_TOKENS = 7 + 3000 + 300000
_IDENTITY_BUDGET_MS = 100.0
```

- [_load](_load.md) function: HOLE: no docstring
- [proj](proj.md) function: HOLE: no docstring
- [_bind](_bind.md) function: Write a NEW-shape (#202 nested) binding entry for `session_id`, keyed
- [_hook_data](_hook_data.md) function: HOLE: no docstring
- [test_golden_fixture_produces_well_formed_record](test_golden_fixture_produces_well_formed_record.md) function: HOLE: no docstring
- [test_golden_fixture_picks_latest_main_chain_usage_not_sidechain](test_golden_fixture_picks_latest_main_chain_usage_not_sidechain.md) function: The fixture's trailing lines 5-6 (a subagent's own context, isSidechain:
- [test_parse_failure_leaves_prior_gauge_file_untouched](test_parse_failure_leaves_prior_gauge_file_untouched.md) function: HOLE: no docstring
- [test_transcript_with_no_usable_usage_leaves_prior_file_untouched](test_transcript_with_no_usable_usage_leaves_prior_file_untouched.md) function: HOLE: no docstring
- [test_missing_transcript_path_skips_no_write](test_missing_transcript_path_skips_no_write.md) function: HOLE: no docstring
- [test_nonexistent_transcript_file_skips_no_write](test_nonexistent_transcript_file_skips_no_write.md) function: HOLE: no docstring
- [test_no_binding_skips_no_write](test_no_binding_skips_no_write.md) function: No session->spine binding (e.g. no engine claim has run yet this
- [test_spine_outside_agent_work_skips_no_write](test_spine_outside_agent_work_skips_no_write.md) function: A binding whose spine path resolved to a CHECKOUT ROOT rather than a
- [test_spine_directly_in_agent_work_root_skips_no_write](test_spine_directly_in_agent_work_root_skips_no_write.md) function: `.agent-work/spine.json` (no <work_id> dir) is also outside the
- [test_worktree_local_agent_work_outside_project_dir_still_writes](test_worktree_local_agent_work_outside_project_dir_still_writes.md) function: Containment checks the `.agent-work/<work_id>/` SHAPE, not containment
- [test_resolve_gauge_path_returns_list_of_every_bound_spine](test_resolve_gauge_path_returns_list_of_every_bound_spine.md) function: HOLE: no docstring
- [test_resolve_gauge_path_empty_list_when_unbound](test_resolve_gauge_path_empty_list_when_unbound.md) function: HOLE: no docstring
- [test_multiple_bindings_skips_writes_neither_spine](test_multiple_bindings_skips_writes_neither_spine.md) function: One session_id bound to TWO spines, ONE PostToolUse event with a
- [test_multiple_bindings_skips_and_leaves_existing_gauge_files_untouched](test_multiple_bindings_skips_and_leaves_existing_gauge_files_untouched.md) function: Same 2-binding ambiguity, but each spine already carries a prior
- [test_single_binding_still_writes_normally](test_single_binding_still_writes_normally.md) function: No-regression check: exactly ONE bound spine must still write the real
- [test_multiple_bindings_uncalibrated_flag_path_also_skips](test_multiple_bindings_uncalibrated_flag_path_also_skips.md) function: The uncalibrated-flag path is a second write path inside the same
- [test_containment_drops_one_bad_path_writes_the_remaining_single_candidate](test_containment_drops_one_bad_path_writes_the_remaining_single_candidate.md) function: One session_id bound to two spines -- one whose resolved spine path is
- [test_real_subagent_transcript_finds_no_usage_and_writes_nothing](test_real_subagent_transcript_finds_no_usage_and_writes_nothing.md) function: Adversarial confirmation of decision:gauge-write-fans-out-on-ambiguity's
- [_unknown_model_transcript](_unknown_model_transcript.md) function: HOLE: no docstring
- [_bound_work](_bound_work.md) function: HOLE: no docstring
- [test_uncalibrated_model_writes_no_reading](test_uncalibrated_model_writes_no_reading.md) function: The #252 regression. An unknown model previously divided its token count
- [test_uncalibrated_model_raises_a_visible_flag](test_uncalibrated_model_raises_a_visible_flag.md) function: Silence alone would be a regression of a different kind — a blind
- [test_uncalibrated_flag_does_not_clobber_an_existing_reading](test_uncalibrated_flag_does_not_clobber_an_existing_reading.md) function: A good reading already on disk must survive; it ages into staleness on
- [test_flag_is_cleared_once_the_model_resolves](test_flag_is_cleared_once_the_model_resolves.md) function: Adding the missing row must actually silence the warning — otherwise the
- [test_ambiguous_binding_writes_skip_flag_to_every_candidate](test_ambiguous_binding_writes_skip_flag_to_every_candidate.md) function: Two genuinely different top-level agents sharing one session_id (#202/
- [test_ambiguous_binding_with_three_candidates_fans_out_to_all_three](test_ambiguous_binding_with_three_candidates_fans_out_to_all_three.md) function: N candidates, not just two -- the fan-out is unbounded in N.
- [test_no_usable_record_single_candidate_writes_skip_flag_no_candidate_count](test_no_usable_record_single_candidate_writes_skip_flag_no_candidate_count.md) function: Single resolved candidate, transcript exists and is readable, but
- [test_corrupt_transcript_single_candidate_also_writes_no_usable_record_flag](test_corrupt_transcript_single_candidate_also_writes_no_usable_record_flag.md) function: Unparseable transcript lines are also a compute_record (None, None)
- [test_zero_candidates_never_writes_a_skip_flag_anywhere](test_zero_candidates_never_writes_a_skip_flag_anywhere.md) function: No binding at all -- genuinely unlocatable, no known path to write a
- [test_missing_transcript_path_never_writes_a_skip_flag](test_missing_transcript_path_never_writes_a_skip_flag.md) function: Missing/unreadable transcript_path is checked BEFORE gauge_paths is
- [test_clean_write_clears_a_prior_skip_flag_at_that_path](test_clean_write_clears_a_prior_skip_flag_at_that_path.md) function: A path that was flagged no-usable-record on one call and then resolves
- [test_uncalibrated_outcome_clears_a_prior_skip_flag_at_that_path](test_uncalibrated_outcome_clears_a_prior_skip_flag_at_that_path.md) function: The uncalibrated-flag write is also a 'resolved' outcome for this
- [test_ambiguous_binding_skip_flags_do_not_clobber_existing_gauge_files](test_ambiguous_binding_skip_flags_do_not_clobber_existing_gauge_files.md) function: Same 'byte-identical survival' proof the existing multi-binding tests
- [_agent_hook_data](_agent_hook_data.md) function: A payload as the harness delivers it for a DISPATCHED agent: the
- [test_binding_key_helper_returns_none_when_spine_rail_failed_to_load](test_binding_key_helper_returns_none_when_spine_rail_failed_to_load.md) function: The `_spine_rail is None` guard lives at the binding-key call site, NOT
- [test_binding_key_helper_delegates_to_spine_rail](test_binding_key_helper_delegates_to_spine_rail.md) function: It is spine_rail's binding_key that composes the key -- this module
- [test_resolve_gauge_path_keys_on_the_composite_key_not_the_session](test_resolve_gauge_path_keys_on_the_composite_key_not_the_session.md) function: A parent and its dispatched agent share a session_id but hold DISTINCT
- [test_subagent_payload_never_writes_to_the_parents_gauge](test_subagent_payload_never_writes_to_the_parents_gauge.md) function: THE misattribution this gate exists to prevent. The parent holds the
- [test_unresolvable_identity_writes_nothing](test_unresolvable_identity_writes_nothing.md) function: The issue's own named negative control. An agent_id the key composer
- [test_spine_rail_missing_writes_nothing_and_does_not_raise](test_spine_rail_missing_writes_nothing_and_does_not_raise.md) function: End-to-end companion to the guard unit test above: with the sibling
- [test_local_allowlist_is_stricter_than_spine_rails_denylist](test_local_allowlist_is_stricter_than_spine_rails_denylist.md) function: g1's rejection is a hand-maintained DENYLIST (`#`, `/`, `\`, `..`) and
- [test_local_allowlist_admits_the_real_observed_id_shape](test_local_allowlist_admits_the_real_observed_id_shape.md) function: The guard must not be so tight it rejects the ids the harness actually
- [test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound](test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound.md) function: A rejected value means WRITE NOTHING -- never a repaired or sanitized
- [test_derived_subagent_transcript_shape](test_derived_subagent_transcript_shape.md) function: The acting agent's transcript is DERIVED from payload fields, never
- [test_derive_subagent_transcript_refuses_an_unusable_id](test_derive_subagent_transcript_refuses_an_unusable_id.md) function: The derivation re-validates at its own boundary too: a rejected value
- [_bound_subagent_work](_bound_subagent_work.md) function: Bind the composite key `session_id#agent_id` to its own work dir.
- [_parent_transcript](_parent_transcript.md) function: A copy of a fixture transcript at a path INSIDE tmp_path, so the
- [_plant_derived_transcript](_plant_derived_transcript.md) function: Materialize the acting agent's own transcript where the derivation
- [test_subagent_with_missing_derived_transcript_leaves_gauge_untouched](test_subagent_with_missing_derived_transcript_leaves_gauge_untouched.md) function: THE fail-closed case. agent_id present, its own transcript absent: the
- [test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all](test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all.md) function: Same branch with no prior reading on disk -- the strongest form of
- [test_subagent_reading_is_computed_from_its_own_transcript_only](test_subagent_reading_is_computed_from_its_own_transcript_only.md) function: There must be NO code path that hands the parent's transcript to
- [test_missing_derived_transcript_never_calls_compute_record](test_missing_derived_transcript_never_calls_compute_record.md) function: The fail-closed branch returns BEFORE any reading is computed -- it
- [test_top_level_payload_still_reads_the_session_transcript](test_top_level_payload_still_reads_the_session_transcript.md) function: The other half of the same invariant: with no agent_id, nothing is
- [_reaching](_reaching.md) function: Run find_latest_usage and report how many transcript lines the reverse
  - [_reaching.counting](_reaching.counting.md) method: HOLE: no docstring
- [test_fixture_premises_hold](test_fixture_premises_hold.md) function: Pin the premises the assertions below rest on, so a fixture edit
- [test_find_latest_usage_takes_one_agent_id_parameter](test_find_latest_usage_takes_one_agent_id_parameter.md) function: One parameter, not two. 'This is agent X's own transcript' is a single
- [test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id](test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id.md) function: Given the fixture's OWN agentId the inverted filter returns the real
- [test_real_subagent_transcript_returns_none_for_a_different_agent_id](test_real_subagent_transcript_returns_none_for_a_different_agent_id.md) function: A wrong derived path must fail CLOSED, not produce a confident wrong
- [test_default_polarity_reaches_every_line_and_still_returns_none](test_default_polarity_reaches_every_line_and_still_returns_none.md) function: The existing assertion (test_real_subagent_transcript_finds_no_usage_
- [test_matching_agent_id_on_a_main_chain_line_is_skipped](test_matching_agent_id_on_a_main_chain_line_is_skipped.md) function: THE falsifier. The tail line carries the matching agentId, sits LAST so
- [test_the_skipped_tail_line_is_itself_perfectly_usable](test_the_skipped_tail_line_is_itself_perfectly_usable.md) function: Control for the test above: the tail line is skipped because of the
- [test_compute_record_carries_the_agent_id_through](test_compute_record_carries_the_agent_id_through.md) function: compute_record takes the same single parameter and forwards it.
- [test_dispatched_agent_writes_its_own_reading_to_its_own_binding](test_dispatched_agent_writes_its_own_reading_to_its_own_binding.md) function: End to end, the whole point of the gate: a dispatched agent and its
- [test_a_wrong_derived_transcript_fails_closed_rather_than_misattributing](test_a_wrong_derived_transcript_fails_closed_rather_than_misattributing.md) function: If the derived path existed but belonged to a DIFFERENT agent, the
- [_SlowRail](_SlowRail.md) class: spine_rail with a deliberate delay on binding_key -- the lever that
  - [_SlowRail.__init__](_SlowRail.__init__.md) method: HOLE: no docstring
  - [_SlowRail.binding_key](_SlowRail.binding_key.md) method: HOLE: no docstring
  - [_SlowRail.__getattr__](_SlowRail.__getattr__.md) method: HOLE: no docstring
- [_write_a_subagent_reading](_write_a_subagent_reading.md) function: HOLE: no docstring
- [test_identity_resolution_duration_is_recorded_within_budget](test_identity_resolution_duration_is_recorded_within_budget.md) function: Identity is an O(1) payload lookup plus a derived path, so the 100ms
- [test_identity_resolution_duration_tracks_a_deliberately_slowed_step](test_identity_resolution_duration_tracks_a_deliberately_slowed_step.md) function: A constant would satisfy the assertion above. Slow the identity step by
- [test_top_level_record_keeps_exactly_the_frozen_four_fields](test_top_level_record_keeps_exactly_the_frozen_four_fields.md) function: The fifth field is additive and OPTIONAL, and it appears only on the
- [test_the_four_required_fields_keep_their_meaning_alongside_the_fifth](test_the_four_required_fields_keep_their_meaning_alongside_the_fifth.md) function: gauge_reader validates the presence of its four required fields and
- [test_no_default_window_constant_remains](test_no_default_window_constant_remains.md) function: The 200k default IS the bug — guard against a well-meaning reintroduction
- [test_claude_opus_5_is_calibrated](test_claude_opus_5_is_calibrated.md) function: Verified against platform.claude.com Models overview, 2026-07-25:
- [test_concurrent_reads_never_observe_a_torn_record](test_concurrent_reads_never_observe_a_torn_record.md) function: Hammer writes and reads of the same gauge.json concurrently. Every
  - [test_concurrent_reads_never_observe_a_torn_record.writer](test_concurrent_reads_never_observe_a_torn_record.writer.md) method: HOLE: no docstring
  - [test_concurrent_reads_never_observe_a_torn_record.reader](test_concurrent_reads_never_observe_a_torn_record.reader.md) method: HOLE: no docstring
- [test_atomic_write_uses_tmp_then_replace](test_atomic_write_uses_tmp_then_replace.md) function: Direct check of the write primitive: the target is only ever touched
- [test_main_never_prints_and_always_exits_zero](test_main_never_prints_and_always_exits_zero.md) function: HOLE: no docstring
- [test_main_malformed_stdin_fails_open](test_main_malformed_stdin_fails_open.md) function: HOLE: no docstring
