# tests.test_episode_fields:RefusalsCounterTests
class, tests/test_episode_fields.py:660, 45 lines

```python
class RefusalsCounterTests(TestCase)
```

`refusals` had NO engine-state source before this change.

A refusal raises `EngineError`; `main()` catches it and DOES persist the
checklist, but recorded nothing about the refusal, and the journal sidecar is
documented and implemented as success-only (`append_journal_entry` sits after the
`return 1`). So the field was secretly agent-dependent — the exact thing
`decision:zero-agent-effort-is-literal` forbids. These tests pin both directions,
because a counter that incremented on EVERYTHING would pass a one-sided test that
only ever checks it goes up.

- [setUp](RefusalsCounterTests.setUp.md) method: HOLE: no docstring
- [tearDown](RefusalsCounterTests.tearDown.md) method: HOLE: no docstring
- [test_a_real_refusal_increments_the_counter_to_a_specific_value](RefusalsCounterTests.test_a_real_refusal_increments_the_counter_to_a_specific_value.md) method: HOLE: no docstring
- [test_a_successful_verb_does_not_move_the_counter](RefusalsCounterTests.test_a_successful_verb_does_not_move_the_counter.md) method: The case a one-sided test misses entirely.

referenced by: none found
