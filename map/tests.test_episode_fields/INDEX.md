# tests.test_episode_fields
tests/test_episode_fields.py, 872 lines, 55 holes

Tests for the MECHANICAL FIELD COMPOSER — `episode_capture.mechanical_fields()`

and the snapshot it emits at the g1 seam (#305 gate g2).

**Why these tests are shaped the way they are.** The composer's output is handed to
`apply_episode_delta.validate_delta()`, and it is tempting to treat that validator as
the oracle. It is not one. `_validate_create` is `isinstance(str) and value.strip()`
for the scalars and `isinstance(int) and >= 0` for the counters — so a composer that
reads no engine state at all and returns nine plausible constants passes it cleanly,
and so does a "red proof" that deletes one key, because deleting a key from a dict is
independent of how the dict was filled. `validate_delta()` is a shape check on the way
to the writer.

So every field here is proven by **tracking**, not by presence: each test constructs a
run whose true value is NON-DEFAULT — a work id nothing would guess, an active step
that is not the first item, a real `rework_count`, a real engine `reopen`, a real
failing command check, a real refusal — and asserts the composer follows it. A constant
cannot pass two of these at once, which is the property presence checks lack.

The `project` tests carry an extra obligation, spelled out because it is the exact way
the defect they cover was nearly shipped. `project` must be stable for a repository
across every worktree and every epic, and the natural-looking source (`durable_root()`)
returns the *worktree unchanged* whenever an active Admiral epic lease exists — which is
the condition every commander in an epic runs under. A test that exercises only a plain
checkout **passes on the broken formula**. `ProjectFieldTests` therefore builds a real
linked worktree under a real active epic lease, asserts the wrong-formula condition is
genuinely reproduced (`durable_root(linked) == linked`), and only then asserts the
composer still yields the MAIN checkout's name.

imports stdlib: importlib.util, json, os, pathlib.Path, shutil, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'scripts' / 'checklist_engine.py'
GIT = shutil.which('git')
ec = load('episode_capture')
awr = load('agent_work_root')
```

- [load](load.md) function: HOLE: no docstring
- [norm](norm.md) function: Compare paths the way the filesystem does, not the way strings do.
- [git](git.md) function: HOLE: no docstring
- [init_repo](init_repo.md) function: A git repo with one commit, so `git worktree add` has a valid HEAD.
- [write_epic_lease](write_epic_lease.md) function: An ACTIVE Admiral epic lease in the MAIN checkout — the exact condition under
- [ProjectFieldTests](ProjectFieldTests.md) class: `project` must name the REPOSITORY, identically from every worktree.
  - [ProjectFieldTests.setUp](ProjectFieldTests.setUp.md) method: HOLE: no docstring
  - [ProjectFieldTests.tearDown](ProjectFieldTests.tearDown.md) method: HOLE: no docstring
  - [ProjectFieldTests.test_plain_checkout_yields_the_checkout_name](ProjectFieldTests.test_plain_checkout_yields_the_checkout_name.md) method: HOLE: no docstring
  - [ProjectFieldTests.test_linked_worktree_under_an_active_epic_lease_still_names_the_repository](ProjectFieldTests.test_linked_worktree_under_an_active_epic_lease_still_names_the_repository.md) method: HOLE: no docstring
  - [ProjectFieldTests.test_linked_worktree_agrees_with_the_main_checkout](ProjectFieldTests.test_linked_worktree_agrees_with_the_main_checkout.md) method: The join this field exists for: the same repository, two worktrees, one
  - [ProjectFieldTests.test_non_repository_refuses_rather_than_guessing](ProjectFieldTests.test_non_repository_refuses_rather_than_guessing.md) method: Refuse, never fabricate. A worktree-derived (or cwd-derived) fallback would
- [checklist](checklist.md) function: A gated checklist with deliberately NON-DEFAULT values, so a composer that
- [ComposerCoreTests](ComposerCoreTests.md) class: Every field is proven by TRACKING a non-default value, never by presence.
  - [ComposerCoreTests.test_run_tracks_the_checklists_own_work_id](ComposerCoreTests.test_run_tracks_the_checklists_own_work_id.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_role_tracks_the_leases_claimed_by](ComposerCoreTests.test_role_tracks_the_leases_claimed_by.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_role_is_refused_when_no_lease_was_ever_claimed](ComposerCoreTests.test_role_is_refused_when_no_lease_was_ever_claimed.md) method: Refuse, never fabricate: a lease-less run has no role to report, and
  - [ComposerCoreTests.test_spine_step_tracks_the_engines_own_selector_not_the_first_item](ComposerCoreTests.test_spine_step_tracks_the_engines_own_selector_not_the_first_item.md) method: The active step is the first NON-TERMINAL item. A composer that returned
  - [ComposerCoreTests.test_spine_step_agrees_with_the_imported_selector_it_must_not_re_derive](ComposerCoreTests.test_spine_step_agrees_with_the_imported_selector_it_must_not_re_derive.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_a_fully_terminal_checklist_refuses_rather_than_naming_a_step](ComposerCoreTests.test_a_fully_terminal_checklist_refuses_rather_than_naming_a_step.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_rework_count_tracks_the_active_steps_own_counter](ComposerCoreTests.test_rework_count_tracks_the_active_steps_own_counter.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_artifact_ref_tracks_the_real_staged_diff](ComposerCoreTests.test_artifact_ref_tracks_the_real_staged_diff.md) method: HOLE: no docstring
  - [ComposerCoreTests.test_project_is_refused_rather_than_defaulted_outside_a_repository](ComposerCoreTests.test_project_is_refused_rather_than_defaulted_outside_a_repository.md) method: HOLE: no docstring
- [LiveSpine](LiveSpine.md) class: A real spine on disk, driven through the engine's own CLI.
  - [LiveSpine.__init__](LiveSpine.__init__.md) method: HOLE: no docstring
  - [LiveSpine.run](LiveSpine.run.md) method: HOLE: no docstring
  - [LiveSpine.verb](LiveSpine.verb.md) method: HOLE: no docstring
  - [LiveSpine.complete](LiveSpine.complete.md) method: HOLE: no docstring
  - [LiveSpine.load](LiveSpine.load.md) method: HOLE: no docstring
  - [LiveSpine.fields](LiveSpine.fields.md) method: HOLE: no docstring
- [ReopensFieldTests](ReopensFieldTests.md) class: `reopens` sums the tasks' own `rework_count`, which only `reopen` writes.
  - [ReopensFieldTests.setUp](ReopensFieldTests.setUp.md) method: HOLE: no docstring
  - [ReopensFieldTests.tearDown](ReopensFieldTests.tearDown.md) method: HOLE: no docstring
  - [ReopensFieldTests.test_reopens_tracks_real_engine_reopens_and_keeps_counting](ReopensFieldTests.test_reopens_tracks_real_engine_reopens_and_keeps_counting.md) method: HOLE: no docstring
  - [ReopensFieldTests.test_reopens_is_run_scoped_where_rework_count_is_step_scoped](ReopensFieldTests.test_reopens_is_run_scoped_where_rework_count_is_step_scoped.md) method: The two fields must be two facts, not one written twice.
  - [ReopensFieldTests.test_the_journal_sidecar_is_not_consulted_at_all](ReopensFieldTests.test_the_journal_sidecar_is_not_consulted_at_all.md) method: The journal is NOT a witness, and this pins that it has not crept back in.
  - [ReopensFieldTests.test_reopens_is_refused_only_when_the_witness_cannot_be_read](ReopensFieldTests.test_reopens_is_refused_only_when_the_witness_cannot_be_read.md) method: Tested on the helper directly: a checklist malformed enough to lose its
- [EscalatedReopenIsNotAReopenTests](EscalatedReopenIsNotAReopenTests.md) class: An ESCALATED `reopen` is journalled as a `reopen` but never was one.
  - [EscalatedReopenIsNotAReopenTests.setUp](EscalatedReopenIsNotAReopenTests.setUp.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.tearDown](EscalatedReopenIsNotAReopenTests.tearDown.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.build](EscalatedReopenIsNotAReopenTests.build.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.verb](EscalatedReopenIsNotAReopenTests.verb.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.say](EscalatedReopenIsNotAReopenTests.say.md) method: The verb's own last line — the engine's message, not our paraphrase.
  - [EscalatedReopenIsNotAReopenTests.complete](EscalatedReopenIsNotAReopenTests.complete.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.rework](EscalatedReopenIsNotAReopenTests.rework.md) method: Reopen, satisfy again, advance — leaving `iid` complete and reopenable.
  - [EscalatedReopenIsNotAReopenTests.escalate](EscalatedReopenIsNotAReopenTests.escalate.md) method: Breach the cap. The engine's OWN message is the ground truth here.
  - [EscalatedReopenIsNotAReopenTests.snapshot](EscalatedReopenIsNotAReopenTests.snapshot.md) method: The record the SEAM emitted, not a value we asked the composer for.
  - [EscalatedReopenIsNotAReopenTests.journal_reopen_lines](EscalatedReopenIsNotAReopenTests.journal_reopen_lines.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.rework_total](EscalatedReopenIsNotAReopenTests.rework_total.md) method: HOLE: no docstring
  - [EscalatedReopenIsNotAReopenTests.test_an_escalation_does_not_inflate_reopens_at_a_start_seam](EscalatedReopenIsNotAReopenTests.test_an_escalation_does_not_inflate_reopens_at_a_start_seam.md) method: ONE real reopen plus one escalation, read at a `start` seam.
  - [EscalatedReopenIsNotAReopenTests.test_escalations_do_not_inflate_reopens_at_a_reopen_seam](EscalatedReopenIsNotAReopenTests.test_escalations_do_not_inflate_reopens_at_a_reopen_seam.md) method: THREE real reopens plus two escalations, read at a `reopen` seam.
- [FailedCommandsFieldTests](FailedCommandsFieldTests.md) class: HOLE: no docstring
  - [FailedCommandsFieldTests.setUp](FailedCommandsFieldTests.setUp.md) method: HOLE: no docstring
  - [FailedCommandsFieldTests.tearDown](FailedCommandsFieldTests.tearDown.md) method: HOLE: no docstring
  - [FailedCommandsFieldTests.test_failed_commands_tracks_real_non_zero_command_checks](FailedCommandsFieldTests.test_failed_commands_tracks_real_non_zero_command_checks.md) method: HOLE: no docstring
  - [FailedCommandsFieldTests.test_a_passing_command_check_does_not_count](FailedCommandsFieldTests.test_a_passing_command_check_does_not_count.md) method: The one-sided test's blind spot: a counter that counted every command
- [ContextManifestRefTests](ContextManifestRefTests.md) class: `context-manifest-ref` is `<manifest-ref>@<revision>` per EPISODE_STORE.md §8,
  - [ContextManifestRefTests.setUp](ContextManifestRefTests.setUp.md) method: HOLE: no docstring
  - [ContextManifestRefTests.tearDown](ContextManifestRefTests.tearDown.md) method: HOLE: no docstring
  - [ContextManifestRefTests.manifest](ContextManifestRefTests.manifest.md) method: HOLE: no docstring
  - [ContextManifestRefTests.test_ref_pins_the_manifests_own_blob_oid](ContextManifestRefTests.test_ref_pins_the_manifests_own_blob_oid.md) method: HOLE: no docstring
  - [ContextManifestRefTests.test_the_pin_equals_git_hash_object_on_that_exact_file](ContextManifestRefTests.test_the_pin_equals_git_hash_object_on_that_exact_file.md) method: HOLE: no docstring
  - [ContextManifestRefTests.test_the_pin_moves_when_the_manifest_bytes_move](ContextManifestRefTests.test_the_pin_moves_when_the_manifest_bytes_move.md) method: A pin that did not follow its own bytes would be a decoration.
  - [ContextManifestRefTests.test_ref_is_refused_when_no_manifest_was_taken](ContextManifestRefTests.test_ref_is_refused_when_no_manifest_was_taken.md) method: Never a plausible `ctx-<run>-<step>@` with an empty or invented revision.
- [RefusalsCounterTests](RefusalsCounterTests.md) class: `refusals` had NO engine-state source before this change.
  - [RefusalsCounterTests.setUp](RefusalsCounterTests.setUp.md) method: HOLE: no docstring
  - [RefusalsCounterTests.tearDown](RefusalsCounterTests.tearDown.md) method: HOLE: no docstring
  - [RefusalsCounterTests.test_a_real_refusal_increments_the_counter_to_a_specific_value](RefusalsCounterTests.test_a_real_refusal_increments_the_counter_to_a_specific_value.md) method: HOLE: no docstring
  - [RefusalsCounterTests.test_a_successful_verb_does_not_move_the_counter](RefusalsCounterTests.test_a_successful_verb_does_not_move_the_counter.md) method: The case a one-sided test misses entirely.
- [AdditiveOnlyTests](AdditiveOnlyTests.md) class: A checklist saved BEFORE the counter existed must still work everywhere.
  - [AdditiveOnlyTests.setUp](AdditiveOnlyTests.setUp.md) method: HOLE: no docstring
  - [AdditiveOnlyTests.tearDown](AdditiveOnlyTests.tearDown.md) method: HOLE: no docstring
  - [AdditiveOnlyTests.test_every_existing_engine_reader_still_works](AdditiveOnlyTests.test_every_existing_engine_reader_still_works.md) method: HOLE: no docstring
  - [AdditiveOnlyTests.test_the_cli_drives_a_pre_counter_checklist_end_to_end](AdditiveOnlyTests.test_the_cli_drives_a_pre_counter_checklist_end_to_end.md) method: HOLE: no docstring
  - [AdditiveOnlyTests.test_the_field_is_refused_rather_than_reported_as_zero](AdditiveOnlyTests.test_the_field_is_refused_rather_than_reported_as_zero.md) method: Absence must not be readable as "no refusals happened" — this checklist was
  - [AdditiveOnlyTests.test_a_manifest_can_still_be_built_from_a_pre_counter_checklist](AdditiveOnlyTests.test_a_manifest_can_still_be_built_from_a_pre_counter_checklist.md) method: HOLE: no docstring
- [ZeroAgentEffortTests](ZeroAgentEffortTests.md) class: The acceptance property, end to end and through the CLI: a run in which the
  - [ZeroAgentEffortTests.setUp](ZeroAgentEffortTests.setUp.md) method: HOLE: no docstring
  - [ZeroAgentEffortTests.tearDown](ZeroAgentEffortTests.tearDown.md) method: HOLE: no docstring
  - [ZeroAgentEffortTests.snapshot_file](ZeroAgentEffortTests.snapshot_file.md) method: HOLE: no docstring
  - [ZeroAgentEffortTests.test_claim_and_start_alone_emit_the_full_group](ZeroAgentEffortTests.test_claim_and_start_alone_emit_the_full_group.md) method: HOLE: no docstring
  - [ZeroAgentEffortTests.test_the_snapshot_refreshes_when_the_step_is_reopened](ZeroAgentEffortTests.test_the_snapshot_refreshes_when_the_step_is_reopened.md) method: Unlike the manifest, the snapshot OVERWRITES: it carries counters, and a
  - [ZeroAgentEffortTests.test_a_refused_field_is_named_rather_than_silently_missing](ZeroAgentEffortTests.test_a_refused_field_is_named_rather_than_silently_missing.md) method: Fail-soft is not fail-silent, inherited from g1: an absent field and a
- [SnapshotIsFailSoftTests](SnapshotIsFailSoftTests.md) class: The seam's hardest constraint, inherited unchanged from g1: the byproduct must
  - [SnapshotIsFailSoftTests.setUp](SnapshotIsFailSoftTests.setUp.md) method: HOLE: no docstring
  - [SnapshotIsFailSoftTests.tearDown](SnapshotIsFailSoftTests.tearDown.md) method: HOLE: no docstring
  - [SnapshotIsFailSoftTests.test_a_throwing_composer_neither_raises_nor_corrupts_the_manifest](SnapshotIsFailSoftTests.test_a_throwing_composer_neither_raises_nor_corrupts_the_manifest.md) method: HOLE: no docstring
  - [SnapshotIsFailSoftTests.test_the_engine_verb_still_exits_zero_when_the_snapshot_cannot_be_written](SnapshotIsFailSoftTests.test_the_engine_verb_still_exits_zero_when_the_snapshot_cannot_be_written.md) method: HOLE: no docstring
- [cm_rev_of](cm_rev_of.md) function: HOLE: no docstring
