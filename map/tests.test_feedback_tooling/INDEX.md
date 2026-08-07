# tests.test_feedback_tooling
tests/test_feedback_tooling.py, 637 lines, 57 holes

HOLE: no docstring

imports stdlib: importlib.util, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_ENTRY = '# Constellation Feedback Export\n\n<!-- collected: never -->\n\n## 2026-06-10 — {proje...
```

- [load](load.md) function: HOLE: no docstring
- [load_installer](load_installer.md) function: HOLE: no docstring
- [CheckSkillFreshnessTests](CheckSkillFreshnessTests.md) class: HOLE: no docstring
  - [CheckSkillFreshnessTests.setUp](CheckSkillFreshnessTests.setUp.md) method: HOLE: no docstring
  - [CheckSkillFreshnessTests.tearDown](CheckSkillFreshnessTests.tearDown.md) method: HOLE: no docstring
  - [CheckSkillFreshnessTests.test_fresh_install_is_up_to_date](CheckSkillFreshnessTests.test_fresh_install_is_up_to_date.md) method: HOLE: no docstring
  - [CheckSkillFreshnessTests.test_upstream_change_detected_and_baseline_promotion](CheckSkillFreshnessTests.test_upstream_change_detected_and_baseline_promotion.md) method: HOLE: no docstring
  - [CheckSkillFreshnessTests.test_local_customization_and_both_changed](CheckSkillFreshnessTests.test_local_customization_and_both_changed.md) method: HOLE: no docstring
- [CollectFeedbackTests](CollectFeedbackTests.md) class: HOLE: no docstring
  - [CollectFeedbackTests.setUp](CollectFeedbackTests.setUp.md) method: HOLE: no docstring
  - [CollectFeedbackTests.tearDown](CollectFeedbackTests.tearDown.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_recurring_candidate_grouped_across_projects](CollectFeedbackTests.test_recurring_candidate_grouped_across_projects.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_collected_entries_move_to_open_until_resolved](CollectFeedbackTests.test_collected_entries_move_to_open_until_resolved.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_partial_collection_is_per_entry](CollectFeedbackTests.test_partial_collection_is_per_entry.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_same_slug_different_prose_is_one_recurring_candidate](CollectFeedbackTests.test_same_slug_different_prose_is_one_recurring_candidate.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_single_project_recurrence_trips_validated_signal](CollectFeedbackTests.test_single_project_recurrence_trips_validated_signal.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_lesson_id_groups_across_slug_drift](CollectFeedbackTests.test_lesson_id_groups_across_slug_drift.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_lesson_id_takes_precedence_over_slug](CollectFeedbackTests.test_lesson_id_takes_precedence_over_slug.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_annotation_stripped_slug_groups_without_lesson_id](CollectFeedbackTests.test_annotation_stripped_slug_groups_without_lesson_id.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_legacy_raw_slug_state_still_matches](CollectFeedbackTests.test_legacy_raw_slug_state_still_matches.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_contentless_section_blocks_are_not_findings](CollectFeedbackTests.test_contentless_section_blocks_are_not_findings.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_template_placeholder_entries_skipped](CollectFeedbackTests.test_template_placeholder_entries_skipped.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_prose_finding_surfaced_network_elo_shape](CollectFeedbackTests.test_prose_finding_surfaced_network_elo_shape.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_prose_finding_fingerprints_on_inline_lesson_id](CollectFeedbackTests.test_prose_finding_fingerprints_on_inline_lesson_id.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_prose_contentless_subblock_not_a_finding](CollectFeedbackTests.test_prose_contentless_subblock_not_a_finding.md) method: HOLE: no docstring
  - [CollectFeedbackTests.test_field_and_prose_not_double_counted](CollectFeedbackTests.test_field_and_prose_not_double_counted.md) method: HOLE: no docstring
- [InboxFilingTests](InboxFilingTests.md) class: The human-gated issue-filing inbox: dry-run by default, --confirm to file,
  - [InboxFilingTests.setUp](InboxFilingTests.setUp.md) method: HOLE: no docstring
  - [InboxFilingTests.tearDown](InboxFilingTests.tearDown.md) method: HOLE: no docstring
  - [InboxFilingTests._write_project](InboxFilingTests._write_project.md) method: HOLE: no docstring
  - [InboxFilingTests._merged](InboxFilingTests._merged.md) method: HOLE: no docstring
  - [InboxFilingTests._fake_filer](InboxFilingTests._fake_filer.md) method: HOLE: no docstring
    - [InboxFilingTests._fake_filer.filer](InboxFilingTests._fake_filer.filer.md) method: HOLE: no docstring
  - [InboxFilingTests.test_dry_run_files_nothing](InboxFilingTests.test_dry_run_files_nothing.md) method: HOLE: no docstring
  - [InboxFilingTests.test_confirm_files_recurring_only](InboxFilingTests.test_confirm_files_recurring_only.md) method: HOLE: no docstring
  - [InboxFilingTests.test_idempotent_no_double_file](InboxFilingTests.test_idempotent_no_double_file.md) method: HOLE: no docstring
  - [InboxFilingTests.test_include_singles_widens](InboxFilingTests.test_include_singles_widens.md) method: HOLE: no docstring
  - [InboxFilingTests.test_issue_spec_carries_substance](InboxFilingTests.test_issue_spec_carries_substance.md) method: HOLE: no docstring
  - [InboxFilingTests.test_issue_spec_title_degrades_without_slug](InboxFilingTests.test_issue_spec_title_degrades_without_slug.md) method: HOLE: no docstring
  - [InboxFilingTests.test_partial_failure_keeps_earlier_filed](InboxFilingTests.test_partial_failure_keeps_earlier_filed.md) method: HOLE: no docstring
    - [InboxFilingTests.test_partial_failure_keeps_earlier_filed.flaky](InboxFilingTests.test_partial_failure_keeps_earlier_filed.flaky.md) method: HOLE: no docstring
  - [InboxFilingTests.test_cli_dry_run_is_default_and_safe](InboxFilingTests.test_cli_dry_run_is_default_and_safe.md) method: HOLE: no docstring
    - [InboxFilingTests.test_cli_dry_run_is_default_and_safe.boom](InboxFilingTests.test_cli_dry_run_is_default_and_safe.boom.md) method: HOLE: no docstring
  - [InboxFilingTests.test_cli_confirm_files_via_injected_filer](InboxFilingTests.test_cli_confirm_files_via_injected_filer.md) method: HOLE: no docstring
- [InboxLifecycleTests](InboxLifecycleTests.md) class: The update-on-recurrence and auto-close-on-resolve lifecycle.
  - [InboxLifecycleTests.setUp](InboxLifecycleTests.setUp.md) method: HOLE: no docstring
  - [InboxLifecycleTests.tearDown](InboxLifecycleTests.tearDown.md) method: HOLE: no docstring
  - [InboxLifecycleTests._project](InboxLifecycleTests._project.md) method: HOLE: no docstring
  - [InboxLifecycleTests._merged](InboxLifecycleTests._merged.md) method: HOLE: no docstring
  - [InboxLifecycleTests._filer](InboxLifecycleTests._filer.md) method: HOLE: no docstring
    - [InboxLifecycleTests._filer.f](InboxLifecycleTests._filer.f.md) method: HOLE: no docstring
  - [InboxLifecycleTests._recorder](InboxLifecycleTests._recorder.md) method: HOLE: no docstring
    - [InboxLifecycleTests._recorder.f](InboxLifecycleTests._recorder.f.md) method: HOLE: no docstring
  - [InboxLifecycleTests._file_once](InboxLifecycleTests._file_once.md) method: HOLE: no docstring
  - [InboxLifecycleTests.test_recurrence_growth_comments_and_watermarks](InboxLifecycleTests.test_recurrence_growth_comments_and_watermarks.md) method: HOLE: no docstring
  - [InboxLifecycleTests.test_dry_run_reports_actions_without_calling_gh](InboxLifecycleTests.test_dry_run_reports_actions_without_calling_gh.md) method: HOLE: no docstring
- [FreshnessPathTokenTests](FreshnessPathTokenTests.md) class: HOLE: no docstring
  - [FreshnessPathTokenTests.test_installed_path_rewritten_template_is_up_to_date](FreshnessPathTokenTests.test_installed_path_rewritten_template_is_up_to_date.md) method: HOLE: no docstring
  - [FreshnessPathTokenTests.test_token_working_copy_up_to_date_against_promoted_baseline](FreshnessPathTokenTests.test_token_working_copy_up_to_date_against_promoted_baseline.md) method: HOLE: no docstring
