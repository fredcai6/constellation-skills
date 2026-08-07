# tests.test_apply_lessons_delta
tests/test_apply_lessons_delta.py, 849 lines, 88 holes

HOLE: no docstring

imports stdlib: datetime.date, importlib.util, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
```

- [load](load.md) function: HOLE: no docstring
- [add_op](add_op.md) function: HOLE: no docstring
- [ApplyLessonsDeltaTests](ApplyLessonsDeltaTests.md) class: HOLE: no docstring
  - [ApplyLessonsDeltaTests.setUp](ApplyLessonsDeltaTests.setUp.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.tearDown](ApplyLessonsDeltaTests.tearDown.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.run_delta](ApplyLessonsDeltaTests.run_delta.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests._seed_lesson](ApplyLessonsDeltaTests._seed_lesson.md) method: Write a playbook file directly so a lesson can carry a chosen added /
  - [ApplyLessonsDeltaTests.test_creates_playbook_and_adds_lesson](ApplyLessonsDeltaTests.test_creates_playbook_and_adds_lesson.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_round_trip_preserves_lessons](ApplyLessonsDeltaTests.test_round_trip_preserves_lessons.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_confirm_requires_grounding](ApplyLessonsDeltaTests.test_confirm_requires_grounding.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_confirm_updates_counters](ApplyLessonsDeltaTests.test_confirm_updates_counters.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_disconfirm_flags_charter_review](ApplyLessonsDeltaTests.test_disconfirm_flags_charter_review.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_add_past_twenty_succeeds_and_retire_still_deletes](ApplyLessonsDeltaTests.test_add_past_twenty_succeeds_and_retire_still_deletes.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_legacy_cap_header_parses_and_is_dropped_on_render](ApplyLessonsDeltaTests.test_legacy_cap_header_parses_and_is_dropped_on_render.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_tick_auto_deletes_unconfirmed](ApplyLessonsDeltaTests.test_tick_auto_deletes_unconfirmed.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_retire_deletes_and_id_is_reusable](ApplyLessonsDeltaTests.test_retire_deletes_and_id_is_reusable.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_amend_updates_fields_preserving_counters](ApplyLessonsDeltaTests.test_amend_updates_fields_preserving_counters.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_amend_requires_grounding_and_a_field](ApplyLessonsDeltaTests.test_amend_requires_grounding_and_a_field.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_rejects_bad_scope_and_duplicate_id](ApplyLessonsDeltaTests.test_rejects_bad_scope_and_duplicate_id.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests._confirm](ApplyLessonsDeltaTests._confirm.md) method: Support both old signature (lesson_id, work_id) and new signature (n, lid).
  - [ApplyLessonsDeltaTests.test_constellation_confirm_is_debt_not_trust](ApplyLessonsDeltaTests.test_constellation_confirm_is_debt_not_trust.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_constellation_recurrence_accrues_more_debt](ApplyLessonsDeltaTests.test_constellation_recurrence_accrues_more_debt.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_non_constellation_confirm_unchanged](ApplyLessonsDeltaTests.test_non_constellation_confirm_unchanged.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_recurrence_debt_renders_and_round_trips](ApplyLessonsDeltaTests.test_recurrence_debt_renders_and_round_trips.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_constellation_pinned_from_auto_delete](ApplyLessonsDeltaTests.test_constellation_pinned_from_auto_delete.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_constellation_debt_paid_by_retire](ApplyLessonsDeltaTests.test_constellation_debt_paid_by_retire.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_rejects_noop_delta](ApplyLessonsDeltaTests.test_rejects_noop_delta.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_invalid_op_applies_nothing](ApplyLessonsDeltaTests.test_invalid_op_applies_nothing.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_legacy_dormant_section_discarded_on_load](ApplyLessonsDeltaTests.test_legacy_dormant_section_discarded_on_load.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_add_accepts_target_and_round_trips](ApplyLessonsDeltaTests.test_add_accepts_target_and_round_trips.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_thresholds_default_when_absent_and_render_explicit](ApplyLessonsDeltaTests.test_thresholds_default_when_absent_and_render_explicit.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_thresholds_round_trip_custom_values](ApplyLessonsDeltaTests.test_thresholds_round_trip_custom_values.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_defer_requires_reason](ApplyLessonsDeltaTests.test_defer_requires_reason.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_defer_sets_status_and_records_count](ApplyLessonsDeltaTests.test_defer_sets_status_and_records_count.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_requires_applied_evidence](ApplyLessonsDeltaTests.test_apply_requires_applied_evidence.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_deletes_non_constellation_lesson](ApplyLessonsDeltaTests.test_apply_deletes_non_constellation_lesson.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_requires_a_target](ApplyLessonsDeltaTests.test_apply_requires_a_target.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_refuses_constellation](ApplyLessonsDeltaTests.test_apply_refuses_constellation.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_export_requires_grounding](ApplyLessonsDeltaTests.test_export_requires_grounding.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_export_sets_exported_and_pins](ApplyLessonsDeltaTests.test_export_sets_exported_and_pins.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_export_refuses_non_constellation](ApplyLessonsDeltaTests.test_export_refuses_non_constellation.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ripe_selects_confirmed_threshold_with_target](ApplyLessonsDeltaTests.test_ripe_selects_confirmed_threshold_with_target.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ripe_excludes_targetless_non_constellation](ApplyLessonsDeltaTests.test_ripe_excludes_targetless_non_constellation.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ripe_selects_constellation_recurrence](ApplyLessonsDeltaTests.test_ripe_selects_constellation_recurrence.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ripe_suppresses_exported_and_fresh_defer](ApplyLessonsDeltaTests.test_ripe_suppresses_exported_and_fresh_defer.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ripe_refires_when_count_climbs_past_defer](ApplyLessonsDeltaTests.test_ripe_refires_when_count_climbs_past_defer.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_ripe_doctrine_refused_without_drill](ApplyLessonsDeltaTests.test_apply_ripe_doctrine_refused_without_drill.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_ripe_doctrine_accepted_with_drill](ApplyLessonsDeltaTests.test_apply_ripe_doctrine_accepted_with_drill.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_non_ripe_doctrine_exempt_from_drill](ApplyLessonsDeltaTests.test_apply_non_ripe_doctrine_exempt_from_drill.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_ripe_code_target_exempt_from_drill](ApplyLessonsDeltaTests.test_apply_ripe_code_target_exempt_from_drill.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_apply_ripe_template_json_is_doctrine_refused_without_drill](ApplyLessonsDeltaTests.test_apply_ripe_template_json_is_doctrine_refused_without_drill.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_tick_same_work_id_ages_lesson_once](ApplyLessonsDeltaTests.test_tick_same_work_id_ages_lesson_once.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_tick_distinct_work_ids_age_each](ApplyLessonsDeltaTests.test_tick_distinct_work_ids_age_each.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_same_work_id_burst_cannot_expire](ApplyLessonsDeltaTests.test_same_work_id_burst_cannot_expire.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_same_epoch_guard_blocks_expiry_when_added_today](ApplyLessonsDeltaTests.test_same_epoch_guard_blocks_expiry_when_added_today.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_same_epoch_guard_blocks_expiry_when_confirmed_today](ApplyLessonsDeltaTests.test_same_epoch_guard_blocks_expiry_when_confirmed_today.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_expires_on_later_dated_tick](ApplyLessonsDeltaTests.test_expires_on_later_dated_tick.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ticked_work_ids_migrates_and_round_trips](ApplyLessonsDeltaTests.test_ticked_work_ids_migrates_and_round_trips.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_existing_real_header_parses_with_empty_ticked](ApplyLessonsDeltaTests.test_existing_real_header_parses_with_empty_ticked.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_ticked_work_ids_bounded](ApplyLessonsDeltaTests.test_ticked_work_ids_bounded.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_malformed_ticked_work_ids_raises](ApplyLessonsDeltaTests.test_malformed_ticked_work_ids_raises.md) method: HOLE: no docstring
  - [ApplyLessonsDeltaTests.test_work_id_with_comma_or_whitespace_rejected](ApplyLessonsDeltaTests.test_work_id_with_comma_or_whitespace_rejected.md) method: HOLE: no docstring
- [BankReasonTests](BankReasonTests.md) class: `add` must state why the lesson is banked to re-observe (not fixed now). The
  - [BankReasonTests.setUp](BankReasonTests.setUp.md) method: HOLE: no docstring
  - [BankReasonTests.tearDown](BankReasonTests.tearDown.md) method: HOLE: no docstring
  - [BankReasonTests.run_delta](BankReasonTests.run_delta.md) method: HOLE: no docstring
  - [BankReasonTests.test_add_without_bank_reason_refused](BankReasonTests.test_add_without_bank_reason_refused.md) method: HOLE: no docstring
  - [BankReasonTests.test_add_with_blank_bank_reason_refused](BankReasonTests.test_add_with_blank_bank_reason_refused.md) method: HOLE: no docstring
  - [BankReasonTests.test_bank_reason_renders_and_round_trips](BankReasonTests.test_bank_reason_renders_and_round_trips.md) method: HOLE: no docstring
  - [BankReasonTests.test_legacy_lesson_without_bank_reason_still_parses](BankReasonTests.test_legacy_lesson_without_bank_reason_still_parses.md) method: HOLE: no docstring
- [DoctrineApplyAuthorityTests](DoctrineApplyAuthorityTests.md) class: Reshaping doctrine (.md / .template.*) is a human call — apply requires
  - [DoctrineApplyAuthorityTests.setUp](DoctrineApplyAuthorityTests.setUp.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.tearDown](DoctrineApplyAuthorityTests.tearDown.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.run_delta](DoctrineApplyAuthorityTests.run_delta.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.test_doctrine_apply_without_authority_refused](DoctrineApplyAuthorityTests.test_doctrine_apply_without_authority_refused.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.test_doctrine_apply_non_human_authority_refused](DoctrineApplyAuthorityTests.test_doctrine_apply_non_human_authority_refused.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.test_doctrine_apply_with_human_authority_paid](DoctrineApplyAuthorityTests.test_doctrine_apply_with_human_authority_paid.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.test_code_target_apply_needs_no_authority](DoctrineApplyAuthorityTests.test_code_target_apply_needs_no_authority.md) method: HOLE: no docstring
  - [DoctrineApplyAuthorityTests.test_delegated_surface_path_defers_instead_of_applying](DoctrineApplyAuthorityTests.test_delegated_surface_path_defers_instead_of_applying.md) method: HOLE: no docstring
- [ResolveDispositionTests](ResolveDispositionTests.md) class: The `resolve` op → terminal `fixed-upstream` status. Ends the export-every-run
  - [ResolveDispositionTests.setUp](ResolveDispositionTests.setUp.md) method: HOLE: no docstring
  - [ResolveDispositionTests.tearDown](ResolveDispositionTests.tearDown.md) method: HOLE: no docstring
  - [ResolveDispositionTests.run_delta](ResolveDispositionTests.run_delta.md) method: HOLE: no docstring
  - [ResolveDispositionTests._add_constellation](ResolveDispositionTests._add_constellation.md) method: HOLE: no docstring
  - [ResolveDispositionTests._confirm](ResolveDispositionTests._confirm.md) method: HOLE: no docstring
  - [ResolveDispositionTests._resolve](ResolveDispositionTests._resolve.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolve_requires_resolution](ResolveDispositionTests.test_resolve_requires_resolution.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolve_refuses_non_constellation](ResolveDispositionTests.test_resolve_refuses_non_constellation.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolve_sets_fixed_upstream_and_round_trips](ResolveDispositionTests.test_resolve_sets_fixed_upstream_and_round_trips.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolved_lesson_not_ripe](ResolveDispositionTests.test_resolved_lesson_not_ripe.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_confirm_after_resolve_is_ignored_no_churn](ResolveDispositionTests.test_confirm_after_resolve_is_ignored_no_churn.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolve_from_exported_state](ResolveDispositionTests.test_resolve_from_exported_state.md) method: HOLE: no docstring
  - [ResolveDispositionTests.test_resolved_lesson_ages_out_while_unpaid_stays_pinned](ResolveDispositionTests.test_resolved_lesson_ages_out_while_unpaid_stays_pinned.md) method: HOLE: no docstring
