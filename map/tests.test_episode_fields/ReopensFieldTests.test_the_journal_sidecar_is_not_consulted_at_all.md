# tests.test_episode_fields:ReopensFieldTests.test_the_journal_sidecar_is_not_consulted_at_all
method, tests/test_episode_fields.py:385, 16 lines

```python
def test_the_journal_sidecar_is_not_consulted_at_all(self)
```

The journal is NOT a witness, and this pins that it has not crept back in.

It once was, reconciled by `max()` on the claim that neither witness could
over-count. That claim was false — an escalated `reopen` journals a line
without incrementing `rework_count` — so the journal witness was removed
rather than compensated for. Deleting the sidecar outright must therefore
leave the field completely unmoved, at a real non-zero value.

calls internal: ReopensFieldTests.assertEqual x3, load
reads internal: ReopensFieldTests.spine x5
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
