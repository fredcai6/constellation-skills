# tests.test_checklist_engine:Inv3ExclusionCheck
class, tests/test_checklist_engine.py:2175, 50 lines

```python
class Inv3ExclusionCheck(TestCase)
```

The trap's own named examples (issue #227 gate g3 handoff): `waive` on

a complete gate, `block` on an already-blocked gate, `attest` on a
pending task, `skip` on a complete gate -- plus `attach`, the fifth
verb with no status guard. None of these five guards on task status in
its own body -- proven here by actually RUNNING each across every
status, rather than asserted in prose.

Reviewer BLOCK (g3-review rework 1): the previous version of this class
hand-picked 4 of the 10 excluded `MUTATING_VERBS` members and claimed
totality it never checked -- `amend`'s `drop`/`rescope`/`retext-check`
sub-ops turned out to guard on status too (now covered by
`Inv3AmendSubOpEnumeration` below, with recovery wired). The exclusion
set here is now DERIVED from `E.MUTATING_VERBS` itself (an engine-native
constant) minus the buckets covered elsewhere, so a FUTURE verb that
starts guarding on status and isn't sorted into one of those buckets
fails the set-equality assertion below instead of silently vanishing
from coverage the way `amend` did.

```python
STATUS_GUARDED_TOP_LEVEL = {'start', 'advance', 'resume', 'reopen'}
STRUCTURALLY_EXCLUDED = {'record', 'consolidate', 'append', 'flag-candidate'}
PARTIALLY_GUARDED = {'amend'}
```

- [test_exclusion_set_is_derived_and_exhaustive](Inv3ExclusionCheck.test_exclusion_set_is_derived_and_exhaustive.md) method: HOLE: no docstring
- [test_waive_block_attest_skip_attach_never_produce_a_status_caused_refusal](Inv3ExclusionCheck.test_waive_block_attest_skip_attach_never_produce_a_status_caused_refusal.md) method: HOLE: no docstring

writes internal: Inv3ExclusionCheck.PARTIALLY_GUARDED, Inv3ExclusionCheck.STATUS_GUARDED_TOP_LEVEL, Inv3ExclusionCheck.STRUCTURALLY_EXCLUDED

referenced by: none found
