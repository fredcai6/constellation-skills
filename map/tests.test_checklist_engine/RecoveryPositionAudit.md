# tests.test_checklist_engine:RecoveryPositionAudit
class, tests/test_checklist_engine.py:2631, 126 lines

```python
class RecoveryPositionAudit(TestCase)
```

Reviewer ask (g3-review rework 2), the load-bearing half: parameterize

the recovery-family tests over ACTIVE vs NON-active position, not just
status -- a single-task fixture makes the refusing task trivially always
active by construction, so it structurally cannot exercise this axis
(which is exactly how the position hole shipped unnoticed). Re-runs every
OTHER refusal family against a NON-active version of its fixture and
proves the named recovery command still runs clean -- confirming, by
actually running them, that `resume`/`reopen`/`attest`/`skip`/`amend`
genuinely have no active-gate dependency, rather than taking that on
faith from source inspection alone.

- [test_blocked_restorable_prior_resume_runs_when_non_active](RecoveryPositionAudit.test_blocked_restorable_prior_resume_runs_when_non_active.md) method: HOLE: no docstring
- [test_blocked_no_restorable_prior_skip_runs_when_non_active](RecoveryPositionAudit.test_blocked_no_restorable_prior_skip_runs_when_non_active.md) method: HOLE: no docstring
- [test_complete_reopen_runs_when_non_active](RecoveryPositionAudit.test_complete_reopen_runs_when_non_active.md) method: HOLE: no docstring
- [test_unmet_precondition_recovery_is_unreachable_while_non_active](RecoveryPositionAudit.test_unmet_precondition_recovery_is_unreachable_while_non_active.md) method: HOLE: no docstring
- [test_unmet_postcondition_attest_runs_when_non_active](RecoveryPositionAudit.test_unmet_postcondition_attest_runs_when_non_active.md) method: HOLE: no docstring
- [test_unknown_cond_id_attest_runs_when_non_active](RecoveryPositionAudit.test_unknown_cond_id_attest_runs_when_non_active.md) method: HOLE: no docstring
- [test_amend_drop_blocked_pending_prior_resume_runs_when_non_active](RecoveryPositionAudit.test_amend_drop_blocked_pending_prior_resume_runs_when_non_active.md) method: HOLE: no docstring

referenced by: none found
