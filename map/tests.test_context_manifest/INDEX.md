# tests.test_context_manifest
tests/test_context_manifest.py, 1131 lines, 82 holes

Tests for `scripts/context_manifest.py` — the deterministic projection substrate.

The manifest answers *what was made available to an agent, at which revision* —
delivery, not use. These tests are deliberately adversarial: a suite that only
parses the real shipped corpus proves the corpus is clean, not that the tool is
correct, so most fixtures below are authored to make the producer return a
*wrong* answer.

imports stdlib: ast, hashlib, importlib.util, json, os, pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
cm = load('context_manifest')
REAL_SPINE_TEMPLATES = sorted((p for p in (ROOT / 'skills').glob('*/templates/*.json') if _is_gated_checklist(...
FIXTURES = json.loads((ROOT / 'tests' / 'fixtures' / 'context_declarations.json').read_text(encodi...
```

- [load](load.md) function: HOLE: no docstring
- [_is_gated_checklist](_is_gated_checklist.md) function: HOLE: no docstring
- [RevIsGitBlobOid](RevIsGitBlobOid.md) class: `rev` is the git blob OID of the LF-normalised bytes, computed in-process.
  - [RevIsGitBlobOid._git](RevIsGitBlobOid._git.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_equals_git_hash_object_for_real_tracked_files](RevIsGitBlobOid.test_rev_equals_git_hash_object_for_real_tracked_files.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_equals_git_rev_parse_head_for_tracked_clean_files](RevIsGitBlobOid.test_rev_equals_git_rev_parse_head_for_tracked_clean_files.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_of_crlf_and_lf_twins_is_identical](RevIsGitBlobOid.test_rev_of_crlf_and_lf_twins_is_identical.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_crlf_twin_written_to_disk_matches_git_hash_object](RevIsGitBlobOid.test_rev_crlf_twin_written_to_disk_matches_git_hash_object.md) method: HOLE: no docstring
  - [RevIsGitBlobOid._raw_blob_oid](RevIsGitBlobOid._raw_blob_oid.md) method: Git's blob OID of exactly these bytes, with no normalisation. The second
  - [RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise](RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_gitattributes_exempts_no_path_from_lf_normalisation](RevIsGitBlobOid.test_gitattributes_exempts_no_path_from_lf_normalisation.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_of_empty_bytes_is_the_git_empty_blob](RevIsGitBlobOid.test_rev_of_empty_bytes_is_the_git_empty_blob.md) method: HOLE: no docstring
  - [RevIsGitBlobOid.test_rev_is_sensitive_to_content_change](RevIsGitBlobOid.test_rev_is_sensitive_to_content_change.md) method: HOLE: no docstring
- [checklist](checklist.md) function: A minimal real-shaped checklist. `declaration=None` means the task carries
- [_dirty_key_paths](_dirty_key_paths.md) function: Every JSON-pointer-ish path at which a key named `dirty` occurs, at any
- [ManifestEnvelope](ManifestEnvelope.md) class: HOLE: no docstring
  - [ManifestEnvelope.setUp](ManifestEnvelope.setUp.md) method: HOLE: no docstring
  - [ManifestEnvelope.build](ManifestEnvelope.build.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_envelope_has_exactly_five_keys](ManifestEnvelope.test_envelope_has_exactly_five_keys.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_row_is_exactly_root_path_rev](ManifestEnvelope.test_row_is_exactly_root_path_rev.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_required_lives_in_the_declaration_not_the_manifest](ManifestEnvelope.test_required_lives_in_the_declaration_not_the_manifest.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_absent_file_yields_null_rev_and_keeps_the_row](ManifestEnvelope.test_absent_file_yields_null_rev_and_keeps_the_row.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_present_but_unreadable_raises_so_null_means_one_thing](ManifestEnvelope.test_present_but_unreadable_raises_so_null_means_one_thing.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_path_escaping_its_root_raises](ManifestEnvelope.test_path_escaping_its_root_raises.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_a_drive_letter_path_is_rejected_not_silently_folded](ManifestEnvelope.test_a_drive_letter_path_is_rejected_not_silently_folded.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_unknown_root_token_or_unmapped_root_raises](ManifestEnvelope.test_unknown_root_token_or_unmapped_root_raises.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_malformed_entries_fail_visibly](ManifestEnvelope.test_malformed_entries_fail_visibly.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_a_declaration_that_is_not_a_list_raises_rather_than_projecting_nothing](ManifestEnvelope.test_a_declaration_that_is_not_a_list_raises_rather_than_projecting_nothing.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_declaration_order_is_content_and_a_permutation_is_a_difference](ManifestEnvelope.test_declaration_order_is_content_and_a_permutation_is_a_difference.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_duplicate_declared_paths_are_both_retained](ManifestEnvelope.test_duplicate_declared_paths_are_both_retained.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_no_absolute_root_path_appears_in_content](ManifestEnvelope.test_no_absolute_root_path_appears_in_content.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_content_excludes_exactly_the_run_subtree](ManifestEnvelope.test_content_excludes_exactly_the_run_subtree.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_the_envelope_is_exactly_the_content_allowlist_plus_run](ManifestEnvelope.test_the_envelope_is_exactly_the_content_allowlist_plus_run.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content](ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content.md) method: HOLE: no docstring
    - [ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content.leaky_content](ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content.leaky_content.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_manifest_never_carries_file_contents](ManifestEnvelope.test_manifest_never_carries_file_contents.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_reader_is_the_single_injected_impure_edge](ManifestEnvelope.test_reader_is_the_single_injected_impure_edge.md) method: HOLE: no docstring
    - [ManifestEnvelope.test_reader_is_the_single_injected_impure_edge.fake_reader](ManifestEnvelope.test_reader_is_the_single_injected_impure_edge.fake_reader.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_stale_record_does_not_silently_pass](ManifestEnvelope.test_stale_record_does_not_silently_pass.md) method: HOLE: no docstring
  - [ManifestEnvelope.test_untracked_vs_absent_disagreement_is_confined_to_rev](ManifestEnvelope.test_untracked_vs_absent_disagreement_is_confined_to_rev.md) method: HOLE: no docstring
- [SelectionUsesTheEnginesOwnSelector](SelectionUsesTheEnginesOwnSelector.md) class: `active_id()` is THE selector. A second one would drift silently.
  - [SelectionUsesTheEnginesOwnSelector.test_producer_imports_the_engines_selector_and_defines_no_second_one](SelectionUsesTheEnginesOwnSelector.test_producer_imports_the_engines_selector_and_defines_no_second_one.md) method: HOLE: no docstring
  - [SelectionUsesTheEnginesOwnSelector.test_step_tracks_active_id_as_items_complete](SelectionUsesTheEnginesOwnSelector.test_step_tracks_active_id_as_items_complete.md) method: HOLE: no docstring
  - [SelectionUsesTheEnginesOwnSelector.test_real_spine_templates_produce_a_manifest_without_crashing](SelectionUsesTheEnginesOwnSelector.test_real_spine_templates_produce_a_manifest_without_crashing.md) method: HOLE: no docstring
- [CommanderSpineDeclaration](CommanderSpineDeclaration.md) class: The first real declaration in the corpus. (Pinning the declaration against
  - [CommanderSpineDeclaration.setUp](CommanderSpineDeclaration.setUp.md) method: HOLE: no docstring
  - [CommanderSpineDeclaration.test_the_declaration_is_exactly_the_pinned_root_path_required_list](CommanderSpineDeclaration.test_the_declaration_is_exactly_the_pinned_root_path_required_list.md) method: HOLE: no docstring
  - [CommanderSpineDeclaration.test_declaration_is_ordered_wellformed_and_non_empty](CommanderSpineDeclaration.test_declaration_is_ordered_wellformed_and_non_empty.md) method: HOLE: no docstring
  - [CommanderSpineDeclaration.test_declaration_projects_one_row_per_entry_in_declared_order](CommanderSpineDeclaration.test_declaration_projects_one_row_per_entry_in_declared_order.md) method: HOLE: no docstring
  - [CommanderSpineDeclaration.test_only_the_context_step_carries_a_declaration](CommanderSpineDeclaration.test_only_the_context_step_carries_a_declaration.md) method: HOLE: no docstring
  - [CommanderSpineDeclaration.test_the_context_imperative_prose_is_not_replaced_by_the_declaration](CommanderSpineDeclaration.test_the_context_imperative_prose_is_not_replaced_by_the_declaration.md) method: HOLE: no docstring
- [Written](Written.md) class: HOLE: no docstring
  - [Written.test_produce_writes_under_agent_work_workid_context](Written.test_produce_writes_under_agent_work_workid_context.md) method: HOLE: no docstring
- [AdversarialDeclarations](AdversarialDeclarations.md) class: Fixtures authored to make the producer return a *wrong* answer.
  - [AdversarialDeclarations.setUp](AdversarialDeclarations.setUp.md) method: HOLE: no docstring
  - [AdversarialDeclarations.build](AdversarialDeclarations.build.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_every_rejected_fixture_raises_rather_than_degrading](AdversarialDeclarations.test_every_rejected_fixture_raises_rather_than_degrading.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_declaration_order_permutation_registers_as_a_difference](AdversarialDeclarations.test_declaration_order_permutation_registers_as_a_difference.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_absent_fixture_is_retained_with_a_null_rev](AdversarialDeclarations.test_absent_fixture_is_retained_with_a_null_rev.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_duplicate_declared_paths_are_two_rows](AdversarialDeclarations.test_duplicate_declared_paths_are_two_rows.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_crlf_and_lf_twins_materialised_on_disk_agree](AdversarialDeclarations.test_crlf_and_lf_twins_materialised_on_disk_agree.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_changed_bytes_never_silently_revalidate_a_recorded_rev](AdversarialDeclarations.test_changed_bytes_never_silently_revalidate_a_recorded_rev.md) method: HOLE: no docstring
  - [AdversarialDeclarations.test_untracked_vs_absent_does_not_change_the_content_shape](AdversarialDeclarations.test_untracked_vs_absent_does_not_change_the_content_shape.md) method: HOLE: no docstring
- [ProducerGuards](ProducerGuards.md) class: Standing invariants of the producer's source and its writes.
  - [ProducerGuards.own_files](ProducerGuards.own_files.md) property: The producer plus every test module written against it — discovered, so a
  - [ProducerGuards._names_used](ProducerGuards._names_used.md) static method: Every identifier and attribute actually *used as code* in a module.
  - [ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer](ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.md) method: HOLE: no docstring
  - [ProducerGuards.test_every_manifest_write_is_newline_pinned](ProducerGuards.test_every_manifest_write_is_newline_pinned.md) method: HOLE: no docstring
  - [ProducerGuards.test_producer_and_its_tests_are_py312_compatible](ProducerGuards.test_producer_and_its_tests_are_py312_compatible.md) method: HOLE: no docstring
  - [ProducerGuards.test_producer_shells_out_to_nothing](ProducerGuards.test_producer_shells_out_to_nothing.md) method: HOLE: no docstring
  - [ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing](ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.md) method: HOLE: no docstring
    - [ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode](ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode.md) method: HOLE: no docstring
- [Serialisation](Serialisation.md) class: HOLE: no docstring
  - [Serialisation.test_encode_is_the_one_canonical_encoder](Serialisation.test_encode_is_the_one_canonical_encoder.md) method: HOLE: no docstring
  - [Serialisation.test_written_manifest_has_lf_endings_on_every_platform](Serialisation.test_written_manifest_has_lf_endings_on_every_platform.md) method: HOLE: no docstring
  - [Serialisation.test_manifest_path_is_agent_work_workid_context_step_json](Serialisation.test_manifest_path_is_agent_work_workid_context_step_json.md) method: HOLE: no docstring
- [RepoRevContent](RepoRevContent.md) class: `repo_rev` -- Tommy's doctrine-version stamp (#300 g5): the repo revision,
  - [RepoRevContent.setUp](RepoRevContent.setUp.md) method: HOLE: no docstring
  - [RepoRevContent.build](RepoRevContent.build.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_rev_is_admitted_into_content_keys](RepoRevContent.test_repo_rev_is_admitted_into_content_keys.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_rev_is_a_content_field_not_a_run_field](RepoRevContent.test_repo_rev_is_a_content_field_not_a_run_field.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_rev_shape_is_exactly_commit](RepoRevContent.test_repo_rev_shape_is_exactly_commit.md) method: HOLE: no docstring
  - [RepoRevContent.test_dirty_appears_nowhere_in_the_manifest](RepoRevContent.test_dirty_appears_nowhere_in_the_manifest.md) method: HOLE: no docstring
  - [RepoRevContent.test_content_is_unaffected_by_dirty_when_commit_is_equal](RepoRevContent.test_content_is_unaffected_by_dirty_when_commit_is_equal.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_rev_does_not_replace_the_per_file_blob_oid](RepoRevContent.test_repo_rev_does_not_replace_the_per_file_blob_oid.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_state_is_injectable_as_the_second_impure_edge](RepoRevContent.test_repo_state_is_injectable_as_the_second_impure_edge.md) method: HOLE: no docstring
    - [RepoRevContent.test_repo_state_is_injectable_as_the_second_impure_edge.fake_repo_state](RepoRevContent.test_repo_state_is_injectable_as_the_second_impure_edge.fake_repo_state.md) method: HOLE: no docstring
  - [RepoRevContent.test_default_repo_state_on_a_non_git_directory_yields_no_commit](RepoRevContent.test_default_repo_state_on_a_non_git_directory_yields_no_commit.md) method: HOLE: no docstring
  - [RepoRevContent.test_default_repo_state_with_no_repo_root_mapped_yields_no_commit](RepoRevContent.test_default_repo_state_with_no_repo_root_mapped_yields_no_commit.md) method: HOLE: no docstring
  - [RepoRevContent.test_default_repo_state_against_the_real_repo_matches_the_commit_oracle](RepoRevContent.test_default_repo_state_against_the_real_repo_matches_the_commit_oracle.md) method: HOLE: no docstring
  - [RepoRevContent.test_repo_rev_survives_json_round_trip_untransformed](RepoRevContent.test_repo_rev_survives_json_round_trip_untransformed.md) method: HOLE: no docstring
  - [RepoRevContent.test_doctrine_version_is_the_repo_rev_field](RepoRevContent.test_doctrine_version_is_the_repo_rev_field.md) method: HOLE: no docstring
- [EpisodeContextFieldShape](EpisodeContextFieldShape.md) class: The manifest must be assignable to an episode `context` field with **no
  - [EpisodeContextFieldShape.test_produced_manifest_is_assignable_to_episode_context_field_untransformed](EpisodeContextFieldShape.test_produced_manifest_is_assignable_to_episode_context_field_untransformed.md) method: HOLE: no docstring
