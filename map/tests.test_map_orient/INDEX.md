# tests.test_map_orient
tests/test_map_orient.py, 1125 lines, 87 holes

The falsification floor for scripts/map_orient.py.

The protected intent is the REPORTED degraded mode: degrading is fine,
degrading silently is refused. Degraded is the COMMON case -- this repo has no
`docs/architecture/` at all -- so the degraded arms carry at least as much of
this file as the resolved arm.

This file is run TWICE: once normally, and once per mutation by
tests/test_mutation_floor.py, which points `MAP_ORIENT_MODULE` at a mutated
copy of the module and asserts this floor goes RED. That is why the module
under test is a variable rather than a fixed import.

imports stdlib: hashlib, importlib.util, json, os, pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = Path(os.environ.get('MAP_ORIENT_MODULE', ROOT / 'scripts' / 'map_orient.py'))
SHIPPED_INDEX_TEMPLATE = ROOT / 'skills/cartographer/templates/ARCHITECTURE_INDEX.template.md'
mo = load()
REAL_PACKET = '# Packet: src/physics\n\n```yaml\nid: struct:physics\nlevel: container\n```\n\nOwns `c...
REAL_INDEX = '# Architecture Index\n\n| Node | Level |\n|---|---|\n| `struct:app` | container |\n| `...
REAL_MAP_JSON = json.dumps({'nodes': [{'id': 'struct:app', 'level': 'container'}, {'id': 'struct:app.ap...
COMPLETE_RECORD = {'substitutes': [{'path': 'README.md', 'content_hash': 'a' * 64}], 'unmapped': ['src/en...
GOOD_FRAME = '# Mission Frame\n\n## Intent\nServe the API without breaking the canonical path.\n\n##...
UNKNOWN_ANCHOR_FRAME = '# Mission Frame\n\n## Structural Anchors\n- `struct:app` — real\n- `struct:ghost_modul...
CODE_CUT_FRAME = '# Mission Frame\n\n## Intent\nFix the solver.\n\n## Structural Anchors\n- `src/engine/...
DEGRADED_FRAME = "# Mission Frame\n\n## Intent\nNo map exists; this frame is cut from the doctrine I dec...
UUNDECLARED_FALLBACK_FRAME = '# Mission Frame\n\n## Substituted Reading\n- `README.md` — declared and pinned\n- `CLA...
```

- [load](load.md) function: HOLE: no docstring
- [write](write.md) function: HOLE: no docstring
- [run_cli](run_cli.md) function: HOLE: no docstring
- [orient](orient.md) function: HOLE: no docstring
- [verdict](verdict.md) function: HOLE: no docstring
- [receipt_of](receipt_of.md) function: HOLE: no docstring
- [RepoFixture](RepoFixture.md) class: A tmp directory that is a PROVEN repo root unless asked otherwise.
  - [RepoFixture.__init__](RepoFixture.__init__.md) method: HOLE: no docstring
  - [RepoFixture.file](RepoFixture.file.md) method: HOLE: no docstring
  - [RepoFixture.dir](RepoFixture.dir.md) method: HOLE: no docstring
- [ResolutionMatrix](ResolutionMatrix.md) class: HOLE: no docstring
  - [ResolutionMatrix.test_generated_map_resolves_first](ResolutionMatrix.test_generated_map_resolves_first.md) method: HOLE: no docstring
  - [ResolutionMatrix.test_index_resolves_when_no_generated_map](ResolutionMatrix.test_index_resolves_when_no_generated_map.md) method: HOLE: no docstring
  - [ResolutionMatrix.test_packets_resolve_when_no_index](ResolutionMatrix.test_packets_resolve_when_no_index.md) method: HOLE: no docstring
  - [ResolutionMatrix.test_explicit_entrypoint_is_tried_first](ResolutionMatrix.test_explicit_entrypoint_is_tried_first.md) method: HOLE: no docstring
  - [ResolutionMatrix.test_every_candidate_is_recorded_even_after_a_hit](ResolutionMatrix.test_every_candidate_is_recorded_even_after_a_hit.md) method: The receipt is a delivery record, not a first-hit lookup log.
  - [ResolutionMatrix.test_resolved_reports_the_anchor_count_it_actually_found](ResolutionMatrix.test_resolved_reports_the_anchor_count_it_actually_found.md) method: HOLE: no docstring
- [DegradedReasons](DegradedReasons.md) class: HOLE: no docstring
  - [DegradedReasons.test_no_map_directory_at_all](DegradedReasons.test_no_map_directory_at_all.md) method: HOLE: no docstring
  - [DegradedReasons.test_empty_index_is_empty_map_not_no_map](DegradedReasons.test_empty_index_is_empty_map_not_no_map.md) method: HOLE: no docstring
  - [DegradedReasons.test_scaffolded_map_dir_with_no_content_is_empty_map](DegradedReasons.test_scaffolded_map_dir_with_no_content_is_empty_map.md) method: HOLE: no docstring
  - [DegradedReasons.test_content_without_a_citable_anchor_is_unparseable](DegradedReasons.test_content_without_a_citable_anchor_is_unparseable.md) method: HOLE: no docstring
  - [DegradedReasons.test_broken_generated_map_is_unparseable_not_resolved](DegradedReasons.test_broken_generated_map_is_unparseable_not_resolved.md) method: HOLE: no docstring
  - [DegradedReasons.test_generated_map_without_nodes_does_not_resolve](DegradedReasons.test_generated_map_without_nodes_does_not_resolve.md) method: HOLE: no docstring
  - [DegradedReasons.test_packets_that_are_all_blank_do_not_resolve](DegradedReasons.test_packets_that_are_all_blank_do_not_resolve.md) method: HOLE: no docstring
  - [DegradedReasons.test_a_degraded_repo_never_exits_zero_undischarged](DegradedReasons.test_a_degraded_repo_never_exits_zero_undischarged.md) method: HOLE: no docstring
- [CitableContent](CitableContent.md) class: HOLE: no docstring
  - [CitableContent.test_the_shipped_index_template_itself_does_not_resolve](CitableContent.test_the_shipped_index_template_itself_does_not_resolve.md) method: The scaffold this repo ships must read DEGRADED, verbatim.
  - [CitableContent.test_an_existing_but_empty_index_is_never_resolved](CitableContent.test_an_existing_but_empty_index_is_never_resolved.md) method: HOLE: no docstring
  - [CitableContent.test_placeholder_ids_are_not_citable](CitableContent.test_placeholder_ids_are_not_citable.md) method: HOLE: no docstring
  - [CitableContent.test_this_repo_resolves_degraded](CitableContent.test_this_repo_resolves_degraded.md) method: This repo has no docs/architecture/ -- the honest verdict is DEGRADED.
- [CouldNotLookDiscriminator](CouldNotLookDiscriminator.md) class: HOLE: no docstring
  - [CouldNotLookDiscriminator.test_bare_directory_and_the_same_directory_with_git_differ_in_one_bit](CouldNotLookDiscriminator.test_bare_directory_and_the_same_directory_with_git_differ_in_one_bit.md) method: HOLE: no docstring
  - [CouldNotLookDiscriminator.test_unresolvable_root_is_not_a_degraded_verdict](CouldNotLookDiscriminator.test_unresolvable_root_is_not_a_degraded_verdict.md) method: HOLE: no docstring
  - [CouldNotLookDiscriminator.test_repo_root_proof_is_positive_not_an_absence_test](CouldNotLookDiscriminator.test_repo_root_proof_is_positive_not_an_absence_test.md) method: HOLE: no docstring
- [degraded_receipt](degraded_receipt.md) function: HOLE: no docstring
- [verify](verify.md) function: HOLE: no docstring
- [PartialFillMatrix](PartialFillMatrix.md) class: Each arm omits exactly ONE required field; the other two are present.
  - [PartialFillMatrix.test_positive_control_a_complete_record_passes](PartialFillMatrix.test_positive_control_a_complete_record_passes.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_missing_substitutes_is_refused](PartialFillMatrix.test_missing_substitutes_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_missing_unmapped_is_refused](PartialFillMatrix.test_missing_unmapped_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_missing_escalation_is_refused](PartialFillMatrix.test_missing_escalation_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_filler_escalation_is_refused](PartialFillMatrix.test_filler_escalation_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_filler_unmapped_is_refused](PartialFillMatrix.test_filler_unmapped_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list](PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list.md) method: MULTI-element on purpose.
  - [PartialFillMatrix.test_a_multi_element_unmapped_list_of_real_entries_passes](PartialFillMatrix.test_a_multi_element_unmapped_list_of_real_entries_passes.md) method: Positive control for the case above: an all-real list must pass.
  - [PartialFillMatrix.test_one_unpinned_substitute_poisons_a_multi_element_list](PartialFillMatrix.test_one_unpinned_substitute_poisons_a_multi_element_list.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_filler_substitute_path_is_refused](PartialFillMatrix.test_filler_substitute_path_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_unhashed_substitute_is_refused](PartialFillMatrix.test_unhashed_substitute_is_refused.md) method: HOLE: no docstring
  - [PartialFillMatrix.test_the_completeness_predicate_requires_all_three](PartialFillMatrix.test_the_completeness_predicate_requires_all_three.md) method: Direct assertion on the predicate the mutation targets.
- [UnreadableSubstitute](UnreadableSubstitute.md) class: A substitute that cannot be read must REFUSE, never discharge.
  - [UnreadableSubstitute.test_a_nonexistent_substitute_path_refuses](UnreadableSubstitute.test_a_nonexistent_substitute_path_refuses.md) method: The reviewer's exact reproduction, pinned.
  - [UnreadableSubstitute.test_an_unreadable_substitute_is_not_pinned_with_a_sentinel](UnreadableSubstitute.test_an_unreadable_substitute_is_not_pinned_with_a_sentinel.md) method: HOLE: no docstring
  - [UnreadableSubstitute.test_the_refusal_names_the_offending_substitute](UnreadableSubstitute.test_the_refusal_names_the_offending_substitute.md) method: HOLE: no docstring
  - [UnreadableSubstitute.test_one_real_substitute_still_discharges](UnreadableSubstitute.test_one_real_substitute_still_discharges.md) method: Positive control: the fix must not refuse a genuine declaration.
  - [UnreadableSubstitute.test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses](UnreadableSubstitute.test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses.md) method: HOLE: no docstring
  - [UnreadableSubstitute.test_a_hash_pin_must_be_a_real_sha256](UnreadableSubstitute.test_a_hash_pin_must_be_a_real_sha256.md) method: HOLE: no docstring
- [VerifyOrientation](VerifyOrientation.md) class: HOLE: no docstring
  - [VerifyOrientation.test_resolved_with_a_wellformed_receipt_passes](VerifyOrientation.test_resolved_with_a_wellformed_receipt_passes.md) method: HOLE: no docstring
  - [VerifyOrientation.test_a_missing_receipt_is_reported_not_assumed](VerifyOrientation.test_a_missing_receipt_is_reported_not_assumed.md) method: HOLE: no docstring
  - [VerifyOrientation.test_a_malformed_receipt_is_reported](VerifyOrientation.test_a_malformed_receipt_is_reported.md) method: HOLE: no docstring
  - [VerifyOrientation.test_an_unresolvable_root_receipt_never_passes](VerifyOrientation.test_an_unresolvable_root_receipt_never_passes.md) method: HOLE: no docstring
  - [VerifyOrientation.test_orient_with_a_full_declaration_discharges_the_degraded_record](VerifyOrientation.test_orient_with_a_full_declaration_discharges_the_degraded_record.md) method: HOLE: no docstring
  - [VerifyOrientation.test_substitutes_are_hash_pinned](VerifyOrientation.test_substitutes_are_hash_pinned.md) method: HOLE: no docstring
- [ContractShape](ContractShape.md) class: HOLE: no docstring
  - [ContractShape.test_first_stdout_line_is_always_a_reserved_literal](ContractShape.test_first_stdout_line_is_always_a_reserved_literal.md) method: HOLE: no docstring
  - [ContractShape.test_semantic_exit_codes_avoid_the_argparse_traceback_shell_collision](ContractShape.test_semantic_exit_codes_avoid_the_argparse_traceback_shell_collision.md) method: HOLE: no docstring
  - [ContractShape.test_a_usage_error_exits_two_and_is_not_a_verdict](ContractShape.test_a_usage_error_exits_two_and_is_not_a_verdict.md) method: HOLE: no docstring
  - [ContractShape.test_no_subcommand_is_a_usage_error_not_a_verdict](ContractShape.test_no_subcommand_is_a_usage_error_not_a_verdict.md) method: HOLE: no docstring
  - [ContractShape.test_self_test_floor_passes](ContractShape.test_self_test_floor_passes.md) method: HOLE: no docstring
  - [ContractShape.test_verdict_is_independent_of_the_launcher_cwd](ContractShape.test_verdict_is_independent_of_the_launcher_cwd.md) method: HOLE: no docstring
- [frame](frame.md) function: HOLE: no docstring
- [verify_frame](verify_frame.md) function: HOLE: no docstring
- [resolved_repo](resolved_repo.md) function: A repo with a real map, already oriented -- the RESOLVED baseline.
- [AbsentFrameRefuses](AbsentFrameRefuses.md) class: THE load-bearing negative case of this gate.
  - [AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_resolved_repo](AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_resolved_repo.md) method: HOLE: no docstring
  - [AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_degraded_repo_too](AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_degraded_repo_too.md) method: The degraded arm must not become the vacuous-pass back door.
  - [AbsentFrameRefuses.test_an_empty_frame_file_is_the_same_as_no_frame](AbsentFrameRefuses.test_an_empty_frame_file_is_the_same_as_no_frame.md) method: HOLE: no docstring
  - [AbsentFrameRefuses.test_the_refusal_names_the_path_it_looked_for](AbsentFrameRefuses.test_the_refusal_names_the_path_it_looked_for.md) method: HOLE: no docstring
  - [AbsentFrameRefuses.test_a_frame_without_a_receipt_refuses_rather_than_passing](AbsentFrameRefuses.test_a_frame_without_a_receipt_refuses_rather_than_passing.md) method: No orientation happened at all -- the frame cannot be checked
- [VerifyFrameResolved](VerifyFrameResolved.md) class: HOLE: no docstring
  - [VerifyFrameResolved.test_a_frame_citing_real_map_anchors_passes](VerifyFrameResolved.test_a_frame_citing_real_map_anchors_passes.md) method: HOLE: no docstring
  - [VerifyFrameResolved.test_an_anchor_that_does_not_resolve_refuses_and_names_it](VerifyFrameResolved.test_an_anchor_that_does_not_resolve_refuses_and_names_it.md) method: HOLE: no docstring
  - [VerifyFrameResolved.test_a_frame_cut_from_source_paths_refuses](VerifyFrameResolved.test_a_frame_cut_from_source_paths_refuses.md) method: HOLE: no docstring
  - [VerifyFrameResolved.test_a_frame_with_no_citation_at_all_refuses](VerifyFrameResolved.test_a_frame_with_no_citation_at_all_refuses.md) method: HOLE: no docstring
  - [VerifyFrameResolved.test_placeholder_anchors_do_not_count_as_citations](VerifyFrameResolved.test_placeholder_anchors_do_not_count_as_citations.md) method: An unfilled MISSION_FRAME scaffold must not satisfy the check.
  - [VerifyFrameResolved.test_the_shipped_mission_frame_template_itself_does_not_pass](VerifyFrameResolved.test_the_shipped_mission_frame_template_itself_does_not_pass.md) method: The scaffold this repo ships, verbatim. Uses the real committed file
- [VerifyFrameContractShape](VerifyFrameContractShape.md) class: HOLE: no docstring
  - [VerifyFrameContractShape.test_orient_never_prints_an_anchor_id](VerifyFrameContractShape.test_orient_never_prints_an_anchor_id.md) method: LOAD-BEARING -- do not drop this test.
  - [VerifyFrameContractShape.test_verify_frame_only_echoes_ids_the_frame_itself_cited](VerifyFrameContractShape.test_verify_frame_only_echoes_ids_the_frame_itself_cited.md) method: The same rule for the checker: naming the offending citation is
  - [VerifyFrameContractShape.test_every_verify_frame_first_line_is_a_reserved_literal](VerifyFrameContractShape.test_every_verify_frame_first_line_is_a_reserved_literal.md) method: HOLE: no docstring
  - [VerifyFrameContractShape.test_verify_frame_invents_no_new_exit_codes](VerifyFrameContractShape.test_verify_frame_invents_no_new_exit_codes.md) method: HOLE: no docstring
  - [VerifyFrameContractShape.test_an_unresolvable_root_receipt_never_lets_a_frame_pass](VerifyFrameContractShape.test_an_unresolvable_root_receipt_never_lets_a_frame_pass.md) method: HOLE: no docstring
  - [VerifyFrameContractShape.test_report_only_is_the_flag_flip_between_gating_and_reporting](VerifyFrameContractShape.test_report_only_is_the_flag_flip_between_gating_and_reporting.md) method: The gate-vs-report ruling must be a flag flip, not a rebuild -- and
- [KnownFallbackProbe](KnownFallbackProbe.md) class: HOLE: no docstring
  - [KnownFallbackProbe.test_orient_records_which_known_fallbacks_actually_exist](KnownFallbackProbe.test_orient_records_which_known_fallbacks_actually_exist.md) method: Existence is settled by the filesystem, not by the agent's account.
  - [KnownFallbackProbe.test_a_probed_fallback_that_exists_is_hash_pinned_too](KnownFallbackProbe.test_a_probed_fallback_that_exists_is_hash_pinned_too.md) method: HOLE: no docstring
  - [KnownFallbackProbe.test_the_probe_reports_a_fallback_the_agent_never_declared](KnownFallbackProbe.test_the_probe_reports_a_fallback_the_agent_never_declared.md) method: The oracle's whole point: it answers independently of the agent.
- [SubstituteLabels](SubstituteLabels.md) class: BOTH labels, asserted on real receipts written by the real CLI.
  - [SubstituteLabels._label](SubstituteLabels._label.md) method: HOLE: no docstring
  - [SubstituteLabels.test_a_present_known_fallback_is_labelled_known_fallback](SubstituteLabels.test_a_present_known_fallback_is_labelled_known_fallback.md) method: HOLE: no docstring
  - [SubstituteLabels.test_a_path_outside_the_known_set_is_labelled_agent_declared](SubstituteLabels.test_a_path_outside_the_known_set_is_labelled_agent_declared.md) method: HOLE: no docstring
  - [SubstituteLabels.test_a_declared_but_ABSENT_known_fallback_is_not_labelled_verified](SubstituteLabels.test_a_declared_but_ABSENT_known_fallback_is_not_labelled_verified.md) method: Set membership alone must not earn the verified label -- that would
  - [SubstituteLabels.test_a_docs_index_fallback_is_labelled_known_fallback](SubstituteLabels.test_a_docs_index_fallback_is_labelled_known_fallback.md) method: HOLE: no docstring
  - [SubstituteLabels.test_the_label_never_upgrades_the_pin](SubstituteLabels.test_the_label_never_upgrades_the_pin.md) method: A label is a provenance note, not a discharge: an absent substitute
- [VerifyFrameDegraded](VerifyFrameDegraded.md) class: The degraded arm of verify-frame, against the hash-pinned prior.
  - [VerifyFrameDegraded.degraded_repo](VerifyFrameDegraded.degraded_repo.md) method: HOLE: no docstring
  - [VerifyFrameDegraded.test_a_degraded_frame_citing_a_declared_substitute_passes](VerifyFrameDegraded.test_a_degraded_frame_citing_a_declared_substitute_passes.md) method: HOLE: no docstring
  - [VerifyFrameDegraded.test_a_degraded_frame_citing_an_UNDECLARED_fallback_refuses](VerifyFrameDegraded.test_a_degraded_frame_citing_an_UNDECLARED_fallback_refuses.md) method: The point of pinning: the frame is compared against a COMMITTED
  - [VerifyFrameDegraded.test_a_degraded_frame_citing_map_anchors_refuses](VerifyFrameDegraded.test_a_degraded_frame_citing_map_anchors_refuses.md) method: No map was read, so a map anchor cannot be a member of anything.
  - [VerifyFrameDegraded.test_a_degraded_frame_citing_nothing_declared_refuses](VerifyFrameDegraded.test_a_degraded_frame_citing_nothing_declared_refuses.md) method: HOLE: no docstring
- [SubstituteProvenanceIsReported](SubstituteProvenanceIsReported.md) class: HOLE: no docstring
  - [SubstituteProvenanceIsReported.degraded_with](SubstituteProvenanceIsReported.degraded_with.md) method: Orient a mapless repo declaring `substitutes`, then report on it.
  - [SubstituteProvenanceIsReported.test_a_present_known_fallback_is_REPORTED_as_known_fallback](SubstituteProvenanceIsReported.test_a_present_known_fallback_is_REPORTED_as_known_fallback.md) method: HOLE: no docstring
  - [SubstituteProvenanceIsReported.test_an_agent_declared_substitute_is_REPORTED_as_unverified](SubstituteProvenanceIsReported.test_an_agent_declared_substitute_is_REPORTED_as_unverified.md) method: HOLE: no docstring
  - [SubstituteProvenanceIsReported.test_BOTH_labels_appear_in_one_real_report](SubstituteProvenanceIsReported.test_BOTH_labels_appear_in_one_real_report.md) method: The distinction is only useful if a reader can see both at once.
  - [SubstituteProvenanceIsReported.test_a_receipt_with_no_source_key_reports_as_agent_declared](SubstituteProvenanceIsReported.test_a_receipt_with_no_source_key_reports_as_agent_declared.md) method: Forward compatibility in the CONSERVATIVE direction: a receipt from
  - [SubstituteProvenanceIsReported.test_an_unrecognised_source_value_reports_as_agent_declared](SubstituteProvenanceIsReported.test_an_unrecognised_source_value_reports_as_agent_declared.md) method: HOLE: no docstring
  - [SubstituteProvenanceIsReported.test_the_report_still_prints_no_anchor_id](SubstituteProvenanceIsReported.test_the_report_still_prints_no_anchor_id.md) method: The anti-leak rule survives the new output. A substitute path is not
  - [SubstituteProvenanceIsReported.test_the_provenance_line_is_never_line_zero](SubstituteProvenanceIsReported.test_the_provenance_line_is_never_line_zero.md) method: The reserved-first-line contract outranks the new output.
