# tests.test_run_skill_eval
tests/test_run_skill_eval.py, 1350 lines, 104 holes

Agent-free unit layer for scripts/run_skill_eval.py (#106, gate g2).

This suite launches NO real agent, ever. The one real subprocess seam
(`launch_agent`) is an inert stub until g3; every test here either injects a
fake launcher (`--dry-run`/`--dry-run-fail`) or exercises pure logic. An autouse
guard hard-fails if any test attempts to spawn a real `claude` subprocess, so the
agent-free guarantee is mechanically enforced rather than trusted.

imports stdlib: __future__.annotations, importlib.util, io, json, os, pathlib.Path, subprocess, sys, threading, time
imports third-party: pytest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
RUN_SKILL_EVAL = ROOT / 'scripts' / 'run_skill_eval.py'
rse = load_module('run_skill_eval', RUN_SKILL_EVAL)
PASS_CHECK = "import sys, pathlib\nrun_dir = pathlib.Path(sys.argv[1])\nart = run_dir / 'workspace' ...
FAIL_CHECK = "import sys\nprint('this check always fails')\nsys.exit(1)\n"
ANSWER_CHECK = "import sys\nprint('advisory answer check (never gates)')\nsys.exit(1)\n"
EXEC_TAIL = ['--allowedTools', *rse.EXEC_ALLOWED_TOOLS]
FOO_SKILL_MD = '---\nname: constellation-foo\ndescription: throwaway eval-runner fixture skill\n---\n#...
REAL_CHECKS_DIR = ROOT / 'evals' / 'euler-1-multiples' / 'checks'
```

- [load_module](load_module.md) function: HOLE: no docstring
- [_no_real_agent](_no_real_agent.md) function: Fail LOUDLY if any test spawns a real `claude` agent subprocess. Check
  - [_no_real_agent._assert_not_claude](_no_real_agent._assert_not_claude.md) method: HOLE: no docstring
  - [_no_real_agent.guarded_run](_no_real_agent.guarded_run.md) method: HOLE: no docstring
  - [_no_real_agent.guarded_popen](_no_real_agent.guarded_popen.md) method: HOLE: no docstring
- [make_scenario](make_scenario.md) function: HOLE: no docstring
- [canned_run_dir](canned_run_dir.md) function: A run-dir whose workspace does (or does not) contain the completion stub.
- [cr](cr.md) function: HOLE: no docstring
- [completed_pass](completed_pass.md) function: HOLE: no docstring
- [completed_fail](completed_fail.md) function: HOLE: no docstring
- [fenced](fenced.md) function: HOLE: no docstring
- [test_build_eval_argv_with_model](test_build_eval_argv_with_model.md) function: HOLE: no docstring
- [test_build_eval_argv_without_model](test_build_eval_argv_without_model.md) function: HOLE: no docstring
- [test_build_eval_argv_with_permission_mode](test_build_eval_argv_with_permission_mode.md) function: HOLE: no docstring
- [test_build_eval_argv_omits_permission_mode_when_none](test_build_eval_argv_omits_permission_mode_when_none.md) function: HOLE: no docstring
- [test_exec_allowlist_always_present](test_exec_allowlist_always_present.md) function: HOLE: no docstring
- [test_default_model_is_pinned_low_and_explicit](test_default_model_is_pinned_low_and_explicit.md) function: HOLE: no docstring
- [test_default_permission_mode_is_least_powerful_write_mode](test_default_permission_mode_is_least_powerful_write_mode.md) function: HOLE: no docstring
- [test_cli_permission_mode_defaults_to_pinned](test_cli_permission_mode_defaults_to_pinned.md) function: HOLE: no docstring
- [test_cli_permission_mode_overridable](test_cli_permission_mode_overridable.md) function: HOLE: no docstring
- [test_load_scenario_defaults](test_load_scenario_defaults.md) function: HOLE: no docstring
- [test_load_scenario_toml_overrides](test_load_scenario_toml_overrides.md) function: HOLE: no docstring
- [test_load_scenario_timeout_floor_clamps_below_minimum](test_load_scenario_timeout_floor_clamps_below_minimum.md) function: HOLE: no docstring
- [test_load_scenario_missing_task_is_config_error](test_load_scenario_missing_task_is_config_error.md) function: HOLE: no docstring
- [test_load_scenario_zero_process_checks_is_config_error](test_load_scenario_zero_process_checks_is_config_error.md) function: HOLE: no docstring
- [test_load_scenario_answer_checks_excluded_from_process_glob](test_load_scenario_answer_checks_excluded_from_process_glob.md) function: HOLE: no docstring
- [test_load_scenario_fixture_detected](test_load_scenario_fixture_detected.md) function: HOLE: no docstring
- [test_run_check_known_good_passes](test_run_check_known_good_passes.md) function: HOLE: no docstring
- [test_run_check_known_bad_fails](test_run_check_known_bad_fails.md) function: HOLE: no docstring
- [test_run_check_marks_answer](test_run_check_marks_answer.md) function: HOLE: no docstring
- [test_is_infra_marker_true](test_is_infra_marker_true.md) function: HOLE: no docstring
- [test_is_infra_marker_false](test_is_infra_marker_false.md) function: HOLE: no docstring
- [test_is_permission_denial_true](test_is_permission_denial_true.md) function: HOLE: no docstring
- [test_is_permission_denial_false](test_is_permission_denial_false.md) function: HOLE: no docstring
- [test_classify_completed_pass](test_classify_completed_pass.md) function: HOLE: no docstring
- [test_classify_completed_fail_when_process_check_fails](test_classify_completed_fail_when_process_check_fails.md) function: HOLE: no docstring
- [test_classify_exit_zero_no_spine_terminal_is_completed](test_classify_exit_zero_no_spine_terminal_is_completed.md) function: HOLE: no docstring
- [test_classify_timeout_is_inconclusive_fenced](test_classify_timeout_is_inconclusive_fenced.md) function: HOLE: no docstring
- [test_classify_timeout_with_all_checks_green_is_pass](test_classify_timeout_with_all_checks_green_is_pass.md) function: HOLE: no docstring
- [test_classify_timeout_with_a_failing_check_stays_fenced](test_classify_timeout_with_a_failing_check_stays_fenced.md) function: HOLE: no docstring
- [test_classify_usage_limit_marker_is_inconclusive_fenced](test_classify_usage_limit_marker_is_inconclusive_fenced.md) function: HOLE: no docstring
- [test_classify_launch_error_is_errored_fenced](test_classify_launch_error_is_errored_fenced.md) function: HOLE: no docstring
- [test_classify_corpus_mismatch_is_errored_fenced](test_classify_corpus_mismatch_is_errored_fenced.md) function: HOLE: no docstring
- [test_classify_nonzero_exit_no_marker_no_completion_is_errored](test_classify_nonzero_exit_no_marker_no_completion_is_errored.md) function: HOLE: no docstring
- [test_classify_permission_blocked_is_errored_fenced](test_classify_permission_blocked_is_errored_fenced.md) function: HOLE: no docstring
- [test_classify_exit_zero_unchanged_without_denial_marker_stays_completed_fail](test_classify_exit_zero_unchanged_without_denial_marker_stays_completed_fail.md) function: HOLE: no docstring
- [test_classify_denial_marker_but_workspace_changed_stays_completed_fail](test_classify_denial_marker_but_workspace_changed_stays_completed_fail.md) function: HOLE: no docstring
- [test_verdict_two_of_three_passes](test_verdict_two_of_three_passes.md) function: HOLE: no docstring
- [test_verdict_one_of_three_fails](test_verdict_one_of_three_fails.md) function: HOLE: no docstring
- [test_verdict_one_completed_two_fenced_is_inconclusive_not_fail](test_verdict_one_completed_two_fenced_is_inconclusive_not_fail.md) function: HOLE: no docstring
- [test_verdict_all_fenced_is_inconclusive](test_verdict_all_fenced_is_inconclusive.md) function: HOLE: no docstring
- [make_corpus](make_corpus.md) function: HOLE: no docstring
- [test_compute_corpus_id_is_stable_and_sensitive](test_compute_corpus_id_is_stable_and_sensitive.md) function: HOLE: no docstring
- [test_write_marker_and_assert_corpus](test_write_marker_and_assert_corpus.md) function: HOLE: no docstring
- [test_answer_only_failure_still_passes](test_answer_only_failure_still_passes.md) function: HOLE: no docstring
- [throwaway_worktree](throwaway_worktree.md) function: A worktree whose `skills/` holds one valid throwaway skill — the source
- [fake_pass_launch](fake_pass_launch.md) function: Agent-free fake: writes the completion artifact a finished run leaves, so
- [fake_fail_launch](fake_fail_launch.md) function: Agent-free fake: exits 0 (so the run COMPLETED) but leaves a broken
- [test_temp_install_real_installs_corpus](test_temp_install_real_installs_corpus.md) function: HOLE: no docstring
- [test_end_to_end_pass_with_real_temp_install_and_fake_launch](test_end_to_end_pass_with_real_temp_install_and_fake_launch.md) function: HOLE: no docstring
- [_tokened_worktree](_tokened_worktree.md) function: Like `throwaway_worktree` but the skill body carries a `<skill-dir>` token, so
- [test_corpus_id_install_path_invariant](test_corpus_id_install_path_invariant.md) function: #153: two byte-identical corpora installed at DIFFERENT absolute temp roots must
- [test_end_to_end_fail_with_real_temp_install_and_fake_launch](test_end_to_end_fail_with_real_temp_install_and_fake_launch.md) function: HOLE: no docstring
- [test_launch_agent_timeout_maps_to_fenced_inconclusive](test_launch_agent_timeout_maps_to_fenced_inconclusive.md) function: HOLE: no docstring
- [test_launch_agent_spawn_failure_maps_to_fenced_errored](test_launch_agent_spawn_failure_maps_to_fenced_errored.md) function: HOLE: no docstring
- [_BlockingPipe](_BlockingPipe.md) class: A pipe double whose read() blocks until the child is 'killed', then EOF.
  - [_BlockingPipe.__init__](_BlockingPipe.__init__.md) method: HOLE: no docstring
  - [_BlockingPipe.read](_BlockingPipe.read.md) method: HOLE: no docstring
- [_HangingPopen](_HangingPopen.md) class: A subprocess.Popen double that NEVER exits on its own: poll() stays None and
  - [_HangingPopen.__init__](_HangingPopen.__init__.md) method: HOLE: no docstring
  - [_HangingPopen.poll](_HangingPopen.poll.md) method: HOLE: no docstring
  - [_HangingPopen.wait](_HangingPopen.wait.md) method: HOLE: no docstring
  - [_HangingPopen._die](_HangingPopen._die.md) method: HOLE: no docstring
- [test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout](test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout.md) function: HOLE: no docstring
  - [test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout.spy_tree_kill](test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout.spy_tree_kill.md) method: HOLE: no docstring
- [test_meta_json_written_incrementally_launch_then_final](test_meta_json_written_incrementally_launch_then_final.md) function: HOLE: no docstring
  - [test_meta_json_written_incrementally_launch_then_final.checking_launch](test_meta_json_written_incrementally_launch_then_final.checking_launch.md) method: HOLE: no docstring
- [test_all_fenced_run_scenario_is_inconclusive_not_fail](test_all_fenced_run_scenario_is_inconclusive_not_fail.md) function: HOLE: no docstring
  - [test_all_fenced_run_scenario_is_inconclusive_not_fail.fake_timeout_launch](test_all_fenced_run_scenario_is_inconclusive_not_fail.fake_timeout_launch.md) method: HOLE: no docstring
- [test_permission_blocked_run_scenario_is_inconclusive_not_fail](test_permission_blocked_run_scenario_is_inconclusive_not_fail.md) function: HOLE: no docstring
  - [test_permission_blocked_run_scenario_is_inconclusive_not_fail.fake_permission_denied_launch](test_permission_blocked_run_scenario_is_inconclusive_not_fail.fake_permission_denied_launch.md) method: HOLE: no docstring
- [_canned_workspace_run_dir](_canned_workspace_run_dir.md) function: HOLE: no docstring
- [test_sentinel_only_workspace_now_fails_strict_checks](test_sentinel_only_workspace_now_fails_strict_checks.md) function: HOLE: no docstring
- [test_real_solution_and_green_test_pass_strict_checks](test_real_solution_and_green_test_pass_strict_checks.md) function: HOLE: no docstring
- [test_dry_run_passes_real_scenario_checks_strictly](test_dry_run_passes_real_scenario_checks_strictly.md) function: HOLE: no docstring
- [test_dry_run_fail_fails_real_scenario_checks_strictly](test_dry_run_fail_fails_real_scenario_checks_strictly.md) function: HOLE: no docstring
- [test_permission_mode_reaches_launcher_argv](test_permission_mode_reaches_launcher_argv.md) function: HOLE: no docstring
  - [test_permission_mode_reaches_launcher_argv.recording_launch](test_permission_mode_reaches_launcher_argv.recording_launch.md) method: HOLE: no docstring
- [test_agent_free_guard_still_bites_on_launch_agent](test_agent_free_guard_still_bites_on_launch_agent.md) function: HOLE: no docstring
- [test_dry_run_exits_zero](test_dry_run_exits_zero.md) function: HOLE: no docstring
- [test_dry_run_fail_exits_one](test_dry_run_fail_exits_one.md) function: HOLE: no docstring
- [test_dry_run_fail_is_completed_fail_not_fenced](test_dry_run_fail_is_completed_fail_not_fenced.md) function: HOLE: no docstring
- [test_zero_process_checks_via_cli_is_schema_error](test_zero_process_checks_via_cli_is_schema_error.md) function: HOLE: no docstring
- [_seed_run_dir](_seed_run_dir.md) function: Seed a run-<index>/ with a meta.json and (optionally) a passing workspace,
- [test_stamp_meta_heartbeat_updates_only_launched_meta](test_stamp_meta_heartbeat_updates_only_launched_meta.md) function: HOLE: no docstring
- [_BrieflyAlivePopen](_BrieflyAlivePopen.md) class: A Popen double that reports alive for a few polls then exits 0, with pipes
  - [_BrieflyAlivePopen.__init__](_BrieflyAlivePopen.__init__.md) method: HOLE: no docstring
  - [_BrieflyAlivePopen.poll](_BrieflyAlivePopen.poll.md) method: HOLE: no docstring
  - [_BrieflyAlivePopen.wait](_BrieflyAlivePopen.wait.md) method: HOLE: no docstring
- [test_launch_agent_stamps_heartbeat_into_launch_meta](test_launch_agent_stamps_heartbeat_into_launch_meta.md) function: HOLE: no docstring
- [test_adjudicate_orphan_green_workspace_is_completed_pass](test_adjudicate_orphan_green_workspace_is_completed_pass.md) function: HOLE: no docstring
- [test_adjudicate_orphan_broken_workspace_is_fenced_inconclusive](test_adjudicate_orphan_broken_workspace_is_fenced_inconclusive.md) function: HOLE: no docstring
- [test_adopt_existing_runs_counts_terminal_and_adjudicates_orphan](test_adopt_existing_runs_counts_terminal_and_adjudicates_orphan.md) function: HOLE: no docstring
- [test_adopt_existing_runs_routes_corrupt_meta_through_adjudicate_orphan_and_continues](test_adopt_existing_runs_routes_corrupt_meta_through_adjudicate_orphan_and_continues.md) function: HOLE: no docstring
- [test_resume_recovers_killed_runner_mid_measurement](test_resume_recovers_killed_runner_mid_measurement.md) function: HOLE: no docstring
  - [test_resume_recovers_killed_runner_mid_measurement._refuse_installer](test_resume_recovers_killed_runner_mid_measurement._refuse_installer.md) method: HOLE: no docstring
- [test_max_new_runs_caps_new_launches_this_invocation](test_max_new_runs_caps_new_launches_this_invocation.md) function: HOLE: no docstring
- [test_sequential_one_run_resumes_accumulate_to_pass](test_sequential_one_run_resumes_accumulate_to_pass.md) function: HOLE: no docstring
- [test_final_meta_preserves_launch_liveness_fields](test_final_meta_preserves_launch_liveness_fields.md) function: HOLE: no docstring
  - [test_final_meta_preserves_launch_liveness_fields.hb_launch](test_final_meta_preserves_launch_liveness_fields.hb_launch.md) method: HOLE: no docstring
- [test_launch_agent_records_subject_pid](test_launch_agent_records_subject_pid.md) function: HOLE: no docstring
- [test_per_run_isolation_one_run_exception_does_not_sink_the_loop](test_per_run_isolation_one_run_exception_does_not_sink_the_loop.md) function: HOLE: no docstring
  - [test_per_run_isolation_one_run_exception_does_not_sink_the_loop.flaky_launch](test_per_run_isolation_one_run_exception_does_not_sink_the_loop.flaky_launch.md) method: HOLE: no docstring
- [_write_hang_cmd](_write_hang_cmd.md) function: A `.cmd` shim whose subject sleeps 600s, so a runner that spawns it as its
- [_confirm_hang_primitive](_confirm_hang_primitive.md) function: Handoff stop-condition guard: independently re-confirm the `.cmd` subject
- [_await_launched_runner](_await_launched_runner.md) function: Bounded poll: discover the runner's `--keep-temp` temp dir (created under the
- [test_real_runner_process_death_leaves_resumable_state](test_real_runner_process_death_leaves_resumable_state.md) function: HOLE: no docstring
  - [test_real_runner_process_death_leaves_resumable_state._refuse_installer](test_real_runner_process_death_leaves_resumable_state._refuse_installer.md) method: HOLE: no docstring
