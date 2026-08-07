# tests.test_episode_fields:ZeroAgentEffortTests
class, tests/test_episode_fields.py:753, 66 lines

```python
@unittest.skipUnless(GIT, 'git not available on PATH')
class ZeroAgentEffortTests(TestCase)
```

The acceptance property, end to end and through the CLI: a run in which the

agent records NOTHING still yields the full mechanical field group.

The completeness assertion is delegated to `apply_episode_delta.validate_delta()`
— the real writer's own validator, which requires every mechanical scalar field —
rather than to a list retyped here, which could drift from the contract silently.
Note carefully what that does and does not prove: it proves the group is COMPLETE
and writer-ready. It does not prove any value is RIGHT; that is what every
tracking test above is for. Presence and truth are different checks and this file
keeps them apart on purpose.

- [setUp](ZeroAgentEffortTests.setUp.md) method: HOLE: no docstring
- [tearDown](ZeroAgentEffortTests.tearDown.md) method: HOLE: no docstring
- [snapshot_file](ZeroAgentEffortTests.snapshot_file.md) method: HOLE: no docstring
- [test_claim_and_start_alone_emit_the_full_group](ZeroAgentEffortTests.test_claim_and_start_alone_emit_the_full_group.md) method: HOLE: no docstring
- [test_the_snapshot_refreshes_when_the_step_is_reopened](ZeroAgentEffortTests.test_the_snapshot_refreshes_when_the_step_is_reopened.md) method: Unlike the manifest, the snapshot OVERWRITES: it carries counters, and a
- [test_a_refused_field_is_named_rather_than_silently_missing](ZeroAgentEffortTests.test_a_refused_field_is_named_rather_than_silently_missing.md) method: Fail-soft is not fail-silent, inherited from g1: an absent field and a

referenced by: none found
