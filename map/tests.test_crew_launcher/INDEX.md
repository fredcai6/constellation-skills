# tests.test_crew_launcher
tests/test_crew_launcher.py, 1132 lines, 83 holes

HOLE: no docstring

imports stdlib: contextlib, datetime.datetime, datetime.timezone, importlib.util, io, json, os, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
RUN_CREW = ROOT / 'scripts' / 'run_crew.py'
RECOVER = ROOT / 'scripts' / 'recover_crews.py'
RC = load_module('run_crew', RUN_CREW)
REC = load_module('recover_crews', RECOVER)
```

- [iso](iso.md) function: ISO-8601 UTC string for a POSIX timestamp — used to build `started_at`
- [write_result_with_mtime](write_result_with_mtime.md) function: Write a result artifact and stamp its mtime deterministically into the
- [load_module](load_module.md) function: HOLE: no docstring
- [write_handoff](write_handoff.md) function: HOLE: no docstring
- [result_rel](result_rel.md) function: HOLE: no docstring
- [fake_launch](fake_launch.md) function: Replace the single subprocess seam with a fake that records the argv,
  - [fake_launch.fake](fake_launch.fake.md) method: HOLE: no docstring
- [SessionNameTests](SessionNameTests.md) class: HOLE: no docstring
  - [SessionNameTests.test_session_name_is_deterministic](SessionNameTests.test_session_name_is_deterministic.md) method: HOLE: no docstring
  - [SessionNameTests.test_build_crew_argv_is_pure_and_carries_role_handoff_session_in_prompt](SessionNameTests.test_build_crew_argv_is_pure_and_carries_role_handoff_session_in_prompt.md) method: HOLE: no docstring
  - [SessionNameTests.test_build_crew_argv_emits_no_legacy_flags](SessionNameTests.test_build_crew_argv_emits_no_legacy_flags.md) method: HOLE: no docstring
  - [SessionNameTests.test_build_crew_argv_omits_model_when_absent](SessionNameTests.test_build_crew_argv_omits_model_when_absent.md) method: HOLE: no docstring
- [CliDriftHintTests](CliDriftHintTests.md) class: HOLE: no docstring
  - [CliDriftHintTests.test_unknown_option_stderr_yields_actionable_hint](CliDriftHintTests.test_unknown_option_stderr_yields_actionable_hint.md) method: HOLE: no docstring
  - [CliDriftHintTests.test_unrecognized_arguments_yields_hint](CliDriftHintTests.test_unrecognized_arguments_yields_hint.md) method: HOLE: no docstring
  - [CliDriftHintTests.test_ordinary_crew_failure_yields_no_hint](CliDriftHintTests.test_ordinary_crew_failure_yields_no_hint.md) method: HOLE: no docstring
- [LaunchTests](LaunchTests.md) class: HOLE: no docstring
  - [LaunchTests.test_missing_handoff_is_refused](LaunchTests.test_missing_handoff_is_refused.md) method: HOLE: no docstring
  - [LaunchTests.test_records_entry_before_launch_and_completes](LaunchTests.test_records_entry_before_launch_and_completes.md) method: HOLE: no docstring
  - [LaunchTests.test_nonzero_child_exit_returns_nonzero_and_marks_failed](LaunchTests.test_nonzero_child_exit_returns_nonzero_and_marks_failed.md) method: HOLE: no docstring
  - [LaunchTests.test_missing_result_artifact_returns_nonzero](LaunchTests.test_missing_result_artifact_returns_nonzero.md) method: HOLE: no docstring
  - [LaunchTests.test_duplicate_active_lock_is_refused](LaunchTests.test_duplicate_active_lock_is_refused.md) method: HOLE: no docstring
  - [LaunchTests.test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned](LaunchTests.test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned.md) method: HOLE: no docstring
  - [LaunchTests.test_resume_uses_stored_session_and_handoff](LaunchTests.test_resume_uses_stored_session_and_handoff.md) method: HOLE: no docstring
  - [LaunchTests.test_resume_unknown_session_is_refused](LaunchTests.test_resume_unknown_session_is_refused.md) method: HOLE: no docstring
- [ExternalDispatchTests](ExternalDispatchTests.md) class: --dispatch external: record the durable registry entry + duplicate-guard
  - [ExternalDispatchTests.test_external_dispatch_records_without_spawning](ExternalDispatchTests.test_external_dispatch_records_without_spawning.md) method: HOLE: no docstring
  - [ExternalDispatchTests.test_external_missing_handoff_is_refused](ExternalDispatchTests.test_external_missing_handoff_is_refused.md) method: HOLE: no docstring
  - [ExternalDispatchTests.test_external_duplicate_active_lock_is_refused](ExternalDispatchTests.test_external_duplicate_active_lock_is_refused.md) method: HOLE: no docstring
  - [ExternalDispatchTests.test_verify_result_absent_then_present_marks_completed](ExternalDispatchTests.test_verify_result_absent_then_present_marks_completed.md) method: HOLE: no docstring
- [ResultFreshnessTests](ResultFreshnessTests.md) class: The canonical freshness gate: a result artifact must exist AND be at/after
  - [ResultFreshnessTests.test_missing_file_is_not_fresh](ResultFreshnessTests.test_missing_file_is_not_fresh.md) method: HOLE: no docstring
  - [ResultFreshnessTests.test_result_after_dispatch_is_fresh](ResultFreshnessTests.test_result_after_dispatch_is_fresh.md) method: HOLE: no docstring
  - [ResultFreshnessTests.test_stale_result_before_dispatch_is_not_fresh](ResultFreshnessTests.test_stale_result_before_dispatch_is_not_fresh.md) method: HOLE: no docstring
  - [ResultFreshnessTests.test_same_second_is_not_falsely_stale](ResultFreshnessTests.test_same_second_is_not_falsely_stale.md) method: Sub-second `started_at` after the file mtime within the SAME whole
  - [ResultFreshnessTests.test_verify_result_stale_refuses_and_leaves_running](ResultFreshnessTests.test_verify_result_stale_refuses_and_leaves_running.md) method: --verify-result on a STALE leftover prints a STALE refusal, returns 1,
  - [ResultFreshnessTests.test_verify_result_missing_refuses_with_absent_message](ResultFreshnessTests.test_verify_result_missing_refuses_with_absent_message.md) method: HOLE: no docstring
  - [ResultFreshnessTests.test_launch_finding_only_stale_result_marks_failed](ResultFreshnessTests.test_launch_finding_only_stale_result_marks_failed.md) method: A spawn that exits 0 but leaves only a STALE prior-attempt result at the
  - [ResultFreshnessTests.test_recover_default_predicate_rejects_stale_uses_started_at](ResultFreshnessTests.test_recover_default_predicate_rejects_stale_uses_started_at.md) method: HOLE: no docstring
- [ProcessAliveTests](ProcessAliveTests.md) class: HOLE: no docstring
  - [ProcessAliveTests.test_pid_zero_or_none_is_dead](ProcessAliveTests.test_pid_zero_or_none_is_dead.md) method: HOLE: no docstring
  - [ProcessAliveTests.test_current_process_is_alive](ProcessAliveTests.test_current_process_is_alive.md) method: HOLE: no docstring
- [ClassificationTests](ClassificationTests.md) class: HOLE: no docstring
  - [ClassificationTests._entry](ClassificationTests._entry.md) static method: HOLE: no docstring
  - [ClassificationTests.test_completed_with_result_is_complete](ClassificationTests.test_completed_with_result_is_complete.md) method: HOLE: no docstring
  - [ClassificationTests.test_running_with_live_pid_is_active](ClassificationTests.test_running_with_live_pid_is_active.md) method: HOLE: no docstring
  - [ClassificationTests.test_running_dead_pid_missing_result_is_resumable](ClassificationTests.test_running_dead_pid_missing_result_is_resumable.md) method: HOLE: no docstring
  - [ClassificationTests.test_running_dead_pid_with_result_is_complete](ClassificationTests.test_running_dead_pid_with_result_is_complete.md) method: HOLE: no docstring
  - [ClassificationTests.test_not_running_not_resumable_needs_abandon](ClassificationTests.test_not_running_not_resumable_needs_abandon.md) method: HOLE: no docstring
  - [ClassificationTests.test_abandoned_is_ignored](ClassificationTests.test_abandoned_is_ignored.md) method: HOLE: no docstring
  - [ClassificationTests.test_unknown_status_live_pid_is_conflict](ClassificationTests.test_unknown_status_live_pid_is_conflict.md) method: HOLE: no docstring
  - [ClassificationTests.test_two_active_attempts_same_target_become_conflict](ClassificationTests.test_two_active_attempts_same_target_become_conflict.md) method: HOLE: no docstring
  - [ClassificationTests.test_report_signals_unresolved_with_nonzero](ClassificationTests.test_report_signals_unresolved_with_nonzero.md) method: HOLE: no docstring
  - [ClassificationTests.test_report_clean_when_all_resolved](ClassificationTests.test_report_clean_when_all_resolved.md) method: HOLE: no docstring
  - [ClassificationTests.test_recover_cli_reads_registry_and_classifies](ClassificationTests.test_recover_cli_reads_registry_and_classifies.md) method: HOLE: no docstring
- [BuildEntryTests](BuildEntryTests.md) class: The ONE consolidated entry constructor shared by both backends.
  - [BuildEntryTests._kwargs](BuildEntryTests._kwargs.md) method: HOLE: no docstring
  - [BuildEntryTests.test_cli_entry_carries_backend_cli_and_pid_no_dispatch](BuildEntryTests.test_cli_entry_carries_backend_cli_and_pid_no_dispatch.md) method: HOLE: no docstring
  - [BuildEntryTests.test_external_entry_keeps_dispatch_marker_pidless_and_model](BuildEntryTests.test_external_entry_keeps_dispatch_marker_pidless_and_model.md) method: HOLE: no docstring
  - [BuildEntryTests.test_falsy_model_is_not_stored](BuildEntryTests.test_falsy_model_is_not_stored.md) method: HOLE: no docstring
- [FinalizeFromExitCodeTests](FinalizeFromExitCodeTests.md) class: The ONE finalize tail both CliBackend.dispatch and .resume call — no forked
  - [FinalizeFromExitCodeTests.test_exit0_and_fresh_result_completes](FinalizeFromExitCodeTests.test_exit0_and_fresh_result_completes.md) method: HOLE: no docstring
  - [FinalizeFromExitCodeTests.test_nonzero_exit_fails_and_returns_that_code](FinalizeFromExitCodeTests.test_nonzero_exit_fails_and_returns_that_code.md) method: HOLE: no docstring
  - [FinalizeFromExitCodeTests.test_exit0_but_stale_result_fails_with_code_1](FinalizeFromExitCodeTests.test_exit0_but_stale_result_fails_with_code_1.md) method: HOLE: no docstring
- [EntryBackendTests](EntryBackendTests.md) class: Legacy entries without a `backend` field are inferred; explicit wins.
  - [EntryBackendTests.test_explicit_backend_wins](EntryBackendTests.test_explicit_backend_wins.md) method: HOLE: no docstring
  - [EntryBackendTests.test_legacy_external_dispatch_infers_external](EntryBackendTests.test_legacy_external_dispatch_infers_external.md) method: HOLE: no docstring
  - [EntryBackendTests.test_legacy_no_marker_infers_cli](EntryBackendTests.test_legacy_no_marker_infers_cli.md) method: HOLE: no docstring
- [BackendEquivalenceTests](BackendEquivalenceTests.md) class: The backends carry the behavior; the module functions are thin wrappers.
  - [BackendEquivalenceTests.test_cli_dispatch_matches_launch_crew_and_tags_backend](BackendEquivalenceTests.test_cli_dispatch_matches_launch_crew_and_tags_backend.md) method: HOLE: no docstring
  - [BackendEquivalenceTests.test_cli_dispatch_missing_handoff_refuses_with_launch_wording](BackendEquivalenceTests.test_cli_dispatch_missing_handoff_refuses_with_launch_wording.md) method: HOLE: no docstring
  - [BackendEquivalenceTests.test_external_dispatch_records_without_spawning_returns_none](BackendEquivalenceTests.test_external_dispatch_records_without_spawning_returns_none.md) method: HOLE: no docstring
  - [BackendEquivalenceTests.test_external_dispatch_missing_handoff_refuses_with_record_wording](BackendEquivalenceTests.test_external_dispatch_missing_handoff_refuses_with_record_wording.md) method: HOLE: no docstring
  - [BackendEquivalenceTests.test_verify_is_uniform_across_backends](BackendEquivalenceTests.test_verify_is_uniform_across_backends.md) method: CrewBackend.verify (used by both backends) finalizes on a fresh result
  - [BackendEquivalenceTests.test_cli_resume_relaunches_and_finalizes](BackendEquivalenceTests.test_cli_resume_relaunches_and_finalizes.md) method: HOLE: no docstring
  - [BackendEquivalenceTests.test_external_resume_is_unrecoverable_by_wrapper](BackendEquivalenceTests.test_external_resume_is_unrecoverable_by_wrapper.md) method: HOLE: no docstring
- [SelectBackendTests](SelectBackendTests.md) class: Decision 4: explicit override always wins; None/auto auto-detects from PATH
  - [SelectBackendTests._found](SelectBackendTests._found.md) static method: HOLE: no docstring
  - [SelectBackendTests._absent](SelectBackendTests._absent.md) static method: HOLE: no docstring
  - [SelectBackendTests.test_explicit_cli_wins_even_when_cli_absent](SelectBackendTests.test_explicit_cli_wins_even_when_cli_absent.md) method: HOLE: no docstring
  - [SelectBackendTests.test_explicit_external_wins_even_when_cli_present](SelectBackendTests.test_explicit_external_wins_even_when_cli_present.md) method: HOLE: no docstring
  - [SelectBackendTests.test_auto_detects_cli_when_launcher_on_path](SelectBackendTests.test_auto_detects_cli_when_launcher_on_path.md) method: HOLE: no docstring
  - [SelectBackendTests.test_auto_detects_external_when_launcher_absent](SelectBackendTests.test_auto_detects_external_when_launcher_absent.md) method: HOLE: no docstring
  - [SelectBackendTests.test_none_auto_detects_like_auto](SelectBackendTests.test_none_auto_detects_like_auto.md) method: HOLE: no docstring
  - [SelectBackendTests.test_auto_detect_uses_the_launcher_argument](SelectBackendTests.test_auto_detect_uses_the_launcher_argument.md) method: HOLE: no docstring
    - [SelectBackendTests.test_auto_detect_uses_the_launcher_argument.which](SelectBackendTests.test_auto_detect_uses_the_launcher_argument.which.md) method: HOLE: no docstring
  - [SelectBackendTests.test_unknown_token_fails_visibly](SelectBackendTests.test_unknown_token_fails_visibly.md) method: HOLE: no docstring
- [BackendFlagRoutingTests](BackendFlagRoutingTests.md) class: Decision 5: --backend resolves + dispatches through the right backend;
  - [BackendFlagRoutingTests._launch_argv](BackendFlagRoutingTests._launch_argv.md) method: HOLE: no docstring
  - [BackendFlagRoutingTests.test_backend_cli_spawns_through_the_cli_backend](BackendFlagRoutingTests.test_backend_cli_spawns_through_the_cli_backend.md) method: HOLE: no docstring
  - [BackendFlagRoutingTests.test_backend_external_records_without_spawning](BackendFlagRoutingTests.test_backend_external_records_without_spawning.md) method: HOLE: no docstring
  - [BackendFlagRoutingTests.test_backend_wins_over_conflicting_dispatch](BackendFlagRoutingTests.test_backend_wins_over_conflicting_dispatch.md) method: --backend external overrides --dispatch spawn (explicit override wins).
  - [BackendFlagRoutingTests.test_default_no_backend_flag_resolves_to_cli_without_autodetect](BackendFlagRoutingTests.test_default_no_backend_flag_resolves_to_cli_without_autodetect.md) method: No --backend + default --dispatch spawn -> cli, regardless of PATH
- [ExternalResumeRefusalTests](ExternalResumeRefusalTests.md) class: Decision 6: --resume routes by the recorded entry's backend. An external
  - [ExternalResumeRefusalTests.test_external_resume_refuses_and_never_spawns](ExternalResumeRefusalTests.test_external_resume_refuses_and_never_spawns.md) method: HOLE: no docstring
  - [ExternalResumeRefusalTests.test_legacy_external_dispatch_marker_also_refuses_resume](ExternalResumeRefusalTests.test_legacy_external_dispatch_marker_also_refuses_resume.md) method: A legacy external entry (dispatch marker, no `backend` field) still routes
  - [ExternalResumeRefusalTests.test_cli_entry_resume_still_relaunches](ExternalResumeRefusalTests.test_cli_entry_resume_still_relaunches.md) method: A cli entry keeps today's resume behavior (relaunch + finalize).
- [BackendInvariantContractTests](BackendInvariantContractTests.md) class: Decision 2: the result contract is backend-invariant — both backends verify
  - [BackendInvariantContractTests._entry_for](BackendInvariantContractTests._entry_for.md) method: HOLE: no docstring
  - [BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically](BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically.md) method: HOLE: no docstring
- [RecoverBackendActionTests](RecoverBackendActionTests.md) class: Decision 6: recover classification stays uniform; only the RESUMABLE
  - [RecoverBackendActionTests._resumable_entry](RecoverBackendActionTests._resumable_entry.md) static method: HOLE: no docstring
  - [RecoverBackendActionTests._report_lines](RecoverBackendActionTests._report_lines.md) method: HOLE: no docstring
  - [RecoverBackendActionTests.test_cli_resumable_action_names_run_crew_resume](RecoverBackendActionTests.test_cli_resumable_action_names_run_crew_resume.md) method: HOLE: no docstring
  - [RecoverBackendActionTests.test_external_resumable_action_names_sendmessage_or_relaunch](RecoverBackendActionTests.test_external_resumable_action_names_sendmessage_or_relaunch.md) method: HOLE: no docstring
  - [RecoverBackendActionTests.test_legacy_external_marker_infers_external_action](RecoverBackendActionTests.test_legacy_external_marker_infers_external_action.md) method: A legacy external entry (dispatch marker, no `backend`) still gets the
