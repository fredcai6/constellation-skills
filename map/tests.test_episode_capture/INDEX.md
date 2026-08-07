# tests.test_episode_capture
tests/test_episode_capture.py, 530 lines, 20 holes

Tests for `scripts/episode_capture.py` — the assembly seam that makes the

context manifest a *byproduct* of starting a spine step.

The point of the seam is that nobody can forget it: `checklist_engine.advance()`
refuses a task that is not `in-progress`, and `start()`/`reopen()` are what put a
task there, so every gate that ever advances has passed the emit.

These tests are deliberately adversarial rather than round-trip. A suite that only
starts a step and finds *a* manifest proves almost nothing here, because the two
failure modes this seam actually has are both **silent**:

* `context_manifest.read_bytes` returns `None` for a missing file and `rows()`
  records `rev: null` without raising — so a wrong root ships a plausible-looking
  manifest with every revision null and every naive assertion green. The root
  tests below therefore assert the **resolved absolute path**, never the code that
  produced it, and one of them resolves a `durable` declaration end to end to prove
  the double-nesting trap is not merely avoided by luck. That declaration is
  synthetic since #308 cut the lessons read path and left the corpus shipping no
  `durable` declaration at all — the trap is a property of `resolve_roots`, not of
  whichever file happens to be declared.
* The emit is fail-soft by design (it must never change a verb's exit code), so a
  broken emit looks exactly like a working one from the caller's side. The
  fail-soft tests therefore pin the exit code *and* the failure stub, because
  "no manifest" and "manifest failed" have to stay tellable apart.

imports stdlib: importlib.util, json, os, pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'scripts' / 'checklist_engine.py'
ec = load('episode_capture')
cm = load('context_manifest')
awr = load('agent_work_root')
```

- [load](load.md) function: HOLE: no docstring
- [norm](norm.md) function: Compare paths the way the filesystem does, not the way strings do.
- [checklist](checklist.md) function: A minimal gated checklist. `declaration` lands on the first item.
- [work_area](work_area.md) function: Lay a checklist out the way a real run does — `<agent-work>/<work-id>/spine.json`
- [engine](engine.md) function: Run the real engine CLI the way an agent does, and return the CompletedProcess.
- [git_repo](git_repo.md) function: HOLE: no docstring
- [RootResolution](RootResolution.md) class: Every assertion here is on a RESOLVED ABSOLUTE PATH, never on the helper
  - [RootResolution.test_roots_are_exactly_the_three_declared_tokens](RootResolution.test_roots_are_exactly_the_three_declared_tokens.md) method: HOLE: no docstring
  - [RootResolution.test_roots_skill_is_the_parent_of_the_scripts_directory](RootResolution.test_roots_skill_is_the_parent_of_the_scripts_directory.md) method: HOLE: no docstring
  - [RootResolution.test_roots_repo_is_the_worktree_root_where_docs_agents_resolves](RootResolution.test_roots_repo_is_the_worktree_root_where_docs_agents_resolves.md) method: HOLE: no docstring
  - [RootResolution.test_roots_durable_is_the_checkout_root_not_the_agent_work_directory](RootResolution.test_roots_durable_is_the_checkout_root_not_the_agent_work_directory.md) method: The silent trap: `durable_agent_work()` returns `<root>/.agent-work`, which
  - [RootResolution.test_roots_durable_resolves_a_declaration_without_double_nesting](RootResolution.test_roots_durable_resolves_a_declaration_without_double_nesting.md) method: Resolve a `durable`-rooted declaration through the real producer and assert
  - [RootResolution.test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory](RootResolution.test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory.md) method: `durable_root(start)` redirects to the main checkout ONLY for a linked
  - [RootResolution.test_roots_outside_a_git_repository_fall_back_visibly_and_never_raise](RootResolution.test_roots_outside_a_git_repository_fall_back_visibly_and_never_raise.md) method: HOLE: no docstring
  - [RootResolution.test_roots_from_a_nonexistent_base_never_raise](RootResolution.test_roots_from_a_nonexistent_base_never_raise.md) method: HOLE: no docstring
- [Emit](Emit.md) class: HOLE: no docstring
  - [Emit.test_emit_writes_a_manifest_carrying_a_non_null_rev](Emit.test_emit_writes_a_manifest_carrying_a_non_null_rev.md) method: Guards against the all-null manifest: a wrong root produces a structurally
  - [Emit.test_emit_lands_beside_the_spine_at_the_manifest_path_contract](Emit.test_emit_lands_beside_the_spine_at_the_manifest_path_contract.md) method: HOLE: no docstring
  - [Emit.test_emit_never_overwrites_an_already_present_manifest](Emit.test_emit_never_overwrites_an_already_present_manifest.md) method: A per-step *delivery snapshot*. If a later call rewrote it, the record
  - [Emit.test_emit_writes_lf_line_endings_on_every_platform](Emit.test_emit_writes_lf_line_endings_on_every_platform.md) method: HOLE: no docstring
  - [Emit.test_emit_records_the_step_the_engine_would_be_activating](Emit.test_emit_records_the_step_the_engine_would_be_activating.md) method: The step is chosen by the engine's own `active_id()`, so the seam must be
  - [Emit.test_emit_without_a_checklist_directory_writes_nothing_at_all](Emit.test_emit_without_a_checklist_directory_writes_nothing_at_all.md) method: No spine location means no work area; inventing one would write the record
- [Seam](Seam.md) class: HOLE: no docstring
  - [Seam.test_seam_start_emits_the_manifest_as_a_byproduct](Seam.test_seam_start_emits_the_manifest_as_a_byproduct.md) method: HOLE: no docstring
  - [Seam.test_seam_reopen_emits_the_manifest_too](Seam.test_seam_reopen_emits_the_manifest_too.md) method: `reopen` is the second and only other door to `in-progress`; a seam wired
  - [Seam.test_seam_a_task_declaring_nothing_still_gets_a_manifest](Seam.test_seam_a_task_declaring_nothing_still_gets_a_manifest.md) method: An empty `files` list is a real reading: "this step was delivered nothing
  - [Seam.test_seam_a_refused_start_emits_nothing](Seam.test_seam_a_refused_start_emits_nothing.md) method: The manifest records delivery to a step that actually activated. A refused
- [FailSoft](FailSoft.md) class: The emit runs inside every `start`, on an engine two other commanders are live
  - [FailSoft.test_failsoft_a_fully_terminal_checklist_does_not_change_any_exit_code](FailSoft.test_failsoft_a_fully_terminal_checklist_does_not_change_any_exit_code.md) method: HOLE: no docstring
  - [FailSoft.test_failsoft_an_unmapped_root_token_does_not_change_the_exit_code](FailSoft.test_failsoft_an_unmapped_root_token_does_not_change_the_exit_code.md) method: HOLE: no docstring
  - [FailSoft.test_failsoft_a_directory_that_is_not_a_git_repo_does_not_change_the_exit_code](FailSoft.test_failsoft_a_directory_that_is_not_a_git_repo_does_not_change_the_exit_code.md) method: HOLE: no docstring
  - [FailSoft.test_failsoft_a_malformed_declaration_does_not_change_the_exit_code](FailSoft.test_failsoft_a_malformed_declaration_does_not_change_the_exit_code.md) method: HOLE: no docstring
  - [FailSoft.test_stub_records_the_failure_instead_of_leaving_silence](FailSoft.test_stub_records_the_failure_instead_of_leaving_silence.md) method: A non-reading must be visibly distinct from an uncollected one. "No file"
  - [FailSoft.test_stub_is_distinguishable_from_a_real_manifest_by_a_later_reader](FailSoft.test_stub_is_distinguishable_from_a_real_manifest_by_a_later_reader.md) method: HOLE: no docstring
  - [FailSoft.test_stub_does_not_overwrite_a_manifest_that_was_already_taken](FailSoft.test_stub_does_not_overwrite_a_manifest_that_was_already_taken.md) method: HOLE: no docstring
  - [FailSoft.test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence](FailSoft.test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence.md) method: Broad-except is the deliberate choice here, so prove it against something
  - [FailSoft.test_stub_files_null_is_not_the_same_reading_as_empty_files](FailSoft.test_stub_files_null_is_not_the_same_reading_as_empty_files.md) method: `files: []` and `files: null` are the two readings that must never
- [SeamPremise](SeamPremise.md) class: The gate rests on a claim about the engine's status machine, not on agent
  - [SeamPremise.test_seam_advance_refuses_a_task_that_was_never_started](SeamPremise.test_seam_advance_refuses_a_task_that_was_never_started.md) method: HOLE: no docstring
  - [SeamPremise.test_seam_only_start_and_reopen_assign_the_in_progress_status](SeamPremise.test_seam_only_start_and_reopen_assign_the_in_progress_status.md) method: HOLE: no docstring
