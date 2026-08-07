# tests.test_checklist_engine:Leasing
class, tests/test_checklist_engine.py:636, 227 lines

```python
class Leasing(TestCase)
```

HOLE: no docstring

- [test_first_claim_creates_active_lease](Leasing.test_first_claim_creates_active_lease.md) method: HOLE: no docstring
- [test_same_session_reclaim_is_idempotent_and_refreshes](Leasing.test_same_session_reclaim_is_idempotent_and_refreshes.md) method: HOLE: no docstring
- [test_different_active_session_claim_refused](Leasing.test_different_active_session_claim_refused.md) method: HOLE: no docstring
- [test_mutating_verb_refused_with_missing_or_wrong_session](Leasing.test_mutating_verb_refused_with_missing_or_wrong_session.md) method: HOLE: no docstring
- [test_mutating_verb_allowed_with_matching_session](Leasing.test_mutating_verb_allowed_with_matching_session.md) method: HOLE: no docstring
- [test_backward_compat_no_lease_allows_mutation_without_session](Leasing.test_backward_compat_no_lease_allows_mutation_without_session.md) method: HOLE: no docstring
- [test_stale_lease_self_heals_for_owner](Leasing.test_stale_lease_self_heals_for_owner.md) method: HOLE: no docstring
- [test_nonowner_against_stale_lease_still_refused](Leasing.test_nonowner_against_stale_lease_still_refused.md) method: HOLE: no docstring
- [test_mutating_verb_stamps_owner_heartbeat](Leasing.test_mutating_verb_stamps_owner_heartbeat.md) method: HOLE: no docstring
- [test_read_only_current_does_not_refresh_owner_heartbeat](Leasing.test_read_only_current_does_not_refresh_owner_heartbeat.md) method: HOLE: no docstring
- [test_no_refresh_on_refused_mutating_call_by_owner](Leasing.test_no_refresh_on_refused_mutating_call_by_owner.md) method: HOLE: no docstring
- [test_refresh_owner_heartbeat_noop_for_nonowner_and_no_lease](Leasing.test_refresh_owner_heartbeat_noop_for_nonowner_and_no_lease.md) method: HOLE: no docstring
- [test_stale_lease_reclaimed_by_force](Leasing.test_stale_lease_reclaimed_by_force.md) method: HOLE: no docstring
- [test_force_takeover_records_audit_trail](Leasing.test_force_takeover_records_audit_trail.md) method: HOLE: no docstring
- [test_force_takeover_requires_reason](Leasing.test_force_takeover_requires_reason.md) method: HOLE: no docstring
- [test_heartbeat_only_by_owner](Leasing.test_heartbeat_only_by_owner.md) method: HOLE: no docstring
- [test_release_closes_lease_and_allows_new_claim](Leasing.test_release_closes_lease_and_allows_new_claim.md) method: HOLE: no docstring
- [test_release_only_by_owner_unless_forced](Leasing.test_release_only_by_owner_unless_forced.md) method: HOLE: no docstring
- [test_current_reports_active_lease_without_session](Leasing.test_current_reports_active_lease_without_session.md) method: HOLE: no docstring
- [test_cli_claim_then_advance_with_session](Leasing.test_cli_claim_then_advance_with_session.md) method: HOLE: no docstring

referenced by: none found
