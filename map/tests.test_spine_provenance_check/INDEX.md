# tests.test_spine_provenance_check
tests/test_spine_provenance_check.py, 388 lines, 32 holes

Provenance hardening for the eval `spine_completed` process check (issue #127).

The check must demand ENGINE-WRITTEN provenance, not just agent-written JSON state:
a spine passes only when it is the gated `tasks` form with every task complete AND
it carries a plausible `engine_session` lease (monotonic claim -> heartbeat ->
release) AND its evidence matches engine grammar. These tests pin the boundary the
issue names -- fabrication cost above doing-the-work cost -- by proving the genuine
engine shape passes while the cheap fabrication shapes (template copy, stripped
lease, non-monotonic lease, hand-written evidence, bare `{"status": "done"}`) fail.

The check ships identically in every eval scenario; we exercise the euler-1 copy.

imports stdlib: __future__.annotations, copy, datetime.datetime, datetime.timedelta, datetime.timezone, hashlib, importlib.util, json, pathlib.Path, sys
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = ROOT / 'evals' / 'euler-1-multiples' / 'checks' / 'spine_completed.py'
TEMPLATE = ROOT / 'skills' / 'commander' / 'templates' / 'COMMANDER_SPINE.template.json'
chk = load_module('spine_completed_check', CHECK_PATH)
_T0 = datetime(2026, 7, 10, 18, 15, 17, tzinfo=timezone.utc)
```

- [load_module](load_module.md) function: HOLE: no docstring
- [genuine_spine](genuine_spine.md) function: HOLE: no docstring
- [write_run_dir](write_run_dir.md) function: HOLE: no docstring
- [test_genuine_engine_spine_passes](test_genuine_engine_spine_passes.md) function: HOLE: no docstring
- [test_genuine_engine_spine_passes_end_to_end](test_genuine_engine_spine_passes_end_to_end.md) function: HOLE: no docstring
- [test_active_unreleased_lease_passes](test_active_unreleased_lease_passes.md) function: HOLE: no docstring
- [test_template_copy_all_pending_fails](test_template_copy_all_pending_fails.md) function: HOLE: no docstring
- [test_hand_marked_complete_without_lease_fails](test_hand_marked_complete_without_lease_fails.md) function: HOLE: no docstring
- [test_stripped_lease_fails](test_stripped_lease_fails.md) function: HOLE: no docstring
- [test_missing_lease_field_fails](test_missing_lease_field_fails.md) function: HOLE: no docstring
- [test_nonmonotonic_lease_fails](test_nonmonotonic_lease_fails.md) function: HOLE: no docstring
- [test_released_before_heartbeat_fails](test_released_before_heartbeat_fails.md) function: HOLE: no docstring
- [test_unparseable_timestamp_fails](test_unparseable_timestamp_fails.md) function: HOLE: no docstring
- [test_hand_written_evidence_id_fails](test_hand_written_evidence_id_fails.md) function: HOLE: no docstring
- [test_non_engine_produced_evidence_fails](test_non_engine_produced_evidence_fails.md) function: HOLE: no docstring
- [test_command_condition_without_backing_evidence_fails](test_command_condition_without_backing_evidence_fails.md) function: HOLE: no docstring
- [test_bare_status_done_form_fails](test_bare_status_done_form_fails.md) function: HOLE: no docstring
- [test_waived_engine_check_with_human_waiver_passes](test_waived_engine_check_with_human_waiver_passes.md) function: HOLE: no docstring
- [test_waived_engine_check_without_waiver_record_fails](test_waived_engine_check_without_waiver_record_fails.md) function: HOLE: no docstring
- [_jhash](_jhash.md) function: Re-derive an entry hash exactly as the engine + check do.
- [chain_journal](chain_journal.md) function: Build a valid hash-chained journal from (ts, verb, task, evidence_ids) rows.
- [genuine_rows](genuine_rows.md) function: HOLE: no docstring
- [write_spine_and_journal](write_spine_and_journal.md) function: HOLE: no docstring
- [test_journal_absent_is_grandfathered](test_journal_absent_is_grandfathered.md) function: HOLE: no docstring
- [test_genuine_journal_passes](test_genuine_journal_passes.md) function: HOLE: no docstring
- [test_genuine_journal_passes_end_to_end](test_genuine_journal_passes_end_to_end.md) function: HOLE: no docstring
- [test_journal_present_but_empty_fails](test_journal_present_but_empty_fails.md) function: HOLE: no docstring
- [test_journal_tampered_hash_fails](test_journal_tampered_hash_fails.md) function: HOLE: no docstring
- [test_journal_broken_chain_fails](test_journal_broken_chain_fails.md) function: HOLE: no docstring
- [test_journal_seq_out_of_order_fails](test_journal_seq_out_of_order_fails.md) function: HOLE: no docstring
- [test_journal_non_monotonic_ts_fails](test_journal_non_monotonic_ts_fails.md) function: HOLE: no docstring
- [test_journal_ts_outside_lease_fails](test_journal_ts_outside_lease_fails.md) function: HOLE: no docstring
- [test_journal_missing_advance_for_complete_task_fails](test_journal_missing_advance_for_complete_task_fails.md) function: HOLE: no docstring
- [test_journal_unreferenced_engine_evidence_fails](test_journal_unreferenced_engine_evidence_fails.md) function: HOLE: no docstring
