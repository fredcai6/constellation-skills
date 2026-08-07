# tests.test_checklist_engine:RecoveryRunnabilityAudit
class, tests/test_checklist_engine.py:2320, 232 lines

```python
class RecoveryRunnabilityAudit(TestCase)
```

Reviewer ask #3 (g3-review rework 1): a general regression test that

would have caught BOTH original defects -- for every branch
`recovery_for()` can emit, actually invoke the command(s) it names
against a tmp fixture in the originating state, and assert none of them
raise `EngineError`. Where a branch is a genuine two-step recovery
(resume/reopen, THEN retry the original op), both steps run in sequence
against the SAME persisted file and the retry is asserted to SUCCEED,
not just that the first step didn't raise. A branch that prints no
command at all (the honest "no verb" statements) is asserted to name
none of the runnable verbs, so a future edit can't quietly reintroduce a
fabricated command there either.

- [test_blocked_restorable_prior_resume_runs](RecoveryRunnabilityAudit.test_blocked_restorable_prior_resume_runs.md) method: HOLE: no docstring
- [test_blocked_no_restorable_prior_only_skip_is_named_and_it_runs](RecoveryRunnabilityAudit.test_blocked_no_restorable_prior_only_skip_is_named_and_it_runs.md) method: HOLE: no docstring
- [test_complete_reopen_runs](RecoveryRunnabilityAudit.test_complete_reopen_runs.md) method: HOLE: no docstring
- [test_skipped_status_names_no_runnable_command](RecoveryRunnabilityAudit.test_skipped_status_names_no_runnable_command.md) method: HOLE: no docstring
- [test_unmet_null_precondition_attest_then_start_runs](RecoveryRunnabilityAudit.test_unmet_null_precondition_attest_then_start_runs.md) method: HOLE: no docstring
- [test_unmet_artifact_postcondition_attest_evidence_then_advance_runs](RecoveryRunnabilityAudit.test_unmet_artifact_postcondition_attest_evidence_then_advance_runs.md) method: HOLE: no docstring
- [test_unmet_command_precondition_fix_and_retry_runs](RecoveryRunnabilityAudit.test_unmet_command_precondition_fix_and_retry_runs.md) method: HOLE: no docstring
- [test_unknown_cond_id_attest_with_a_real_id_runs](RecoveryRunnabilityAudit.test_unknown_cond_id_attest_with_a_real_id_runs.md) method: HOLE: no docstring
- [test_amend_drop_blocked_pending_prior_resume_then_retry_runs](RecoveryRunnabilityAudit.test_amend_drop_blocked_pending_prior_resume_then_retry_runs.md) method: HOLE: no docstring
- [test_amend_drop_in_progress_names_no_runnable_command](RecoveryRunnabilityAudit.test_amend_drop_in_progress_names_no_runnable_command.md) method: HOLE: no docstring
- [test_amend_retext_check_complete_reopen_then_retry_runs](RecoveryRunnabilityAudit.test_amend_retext_check_complete_reopen_then_retry_runs.md) method: HOLE: no docstring
- [test_amend_retext_check_blocked_in_progress_prior_resume_then_retry_runs](RecoveryRunnabilityAudit.test_amend_retext_check_blocked_in_progress_prior_resume_then_retry_runs.md) method: HOLE: no docstring
- [test_amend_retext_check_skipped_names_no_runnable_command](RecoveryRunnabilityAudit.test_amend_retext_check_skipped_names_no_runnable_command.md) method: HOLE: no docstring

referenced by: none found
