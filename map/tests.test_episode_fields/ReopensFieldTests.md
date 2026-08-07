# tests.test_episode_fields:ReopensFieldTests
class, tests/test_episode_fields.py:332, 77 lines

```python
class ReopensFieldTests(TestCase)
```

`reopens` sums the tasks' own `rework_count`, which only `reopen` writes.

Neither of the two obvious alternatives can serve. The checklist's `why_trail`
over-counts: `reopen` appends a marker for the target AND for every cascaded
downstream gate, so gates nobody reopened would report reopens. The journal
sidecar over-counts too, for a subtler reason — see
`EscalatedReopenIsNotAReopenTests`, which is the test that killed it.

- [setUp](ReopensFieldTests.setUp.md) method: HOLE: no docstring
- [tearDown](ReopensFieldTests.tearDown.md) method: HOLE: no docstring
- [test_reopens_tracks_real_engine_reopens_and_keeps_counting](ReopensFieldTests.test_reopens_tracks_real_engine_reopens_and_keeps_counting.md) method: HOLE: no docstring
- [test_reopens_is_run_scoped_where_rework_count_is_step_scoped](ReopensFieldTests.test_reopens_is_run_scoped_where_rework_count_is_step_scoped.md) method: The two fields must be two facts, not one written twice.
- [test_the_journal_sidecar_is_not_consulted_at_all](ReopensFieldTests.test_the_journal_sidecar_is_not_consulted_at_all.md) method: The journal is NOT a witness, and this pins that it has not crept back in.
- [test_reopens_is_refused_only_when_the_witness_cannot_be_read](ReopensFieldTests.test_reopens_is_refused_only_when_the_witness_cannot_be_read.md) method: Tested on the helper directly: a checklist malformed enough to lose its

referenced by: none found
