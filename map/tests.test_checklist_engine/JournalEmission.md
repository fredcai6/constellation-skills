# tests.test_checklist_engine:JournalEmission
class, tests/test_checklist_engine.py:1715, 79 lines

```python
class JournalEmission(TestCase)
```

The append-only journal sidecar (#131): one hash-chained line per SUCCESSFUL

mutating verb, written only by main(), never read back by the engine (backward
compatible).

- [_save](JournalEmission._save.md) method: HOLE: no docstring
- [_journal_lines](JournalEmission._journal_lines.md) method: HOLE: no docstring
- [test_mutating_verb_appends_one_journal_line](JournalEmission.test_mutating_verb_appends_one_journal_line.md) method: HOLE: no docstring
- [test_non_mutating_verb_does_not_journal](JournalEmission.test_non_mutating_verb_does_not_journal.md) method: HOLE: no docstring
- [test_dry_run_does_not_journal](JournalEmission.test_dry_run_does_not_journal.md) method: HOLE: no docstring
- [test_refused_verb_does_not_journal](JournalEmission.test_refused_verb_does_not_journal.md) method: HOLE: no docstring
- [test_hash_chain_links_successive_verbs](JournalEmission.test_hash_chain_links_successive_verbs.md) method: HOLE: no docstring
- [test_journal_captures_new_evidence_ids](JournalEmission.test_journal_captures_new_evidence_ids.md) method: HOLE: no docstring
- [test_engine_never_reads_journal_backward_compatible](JournalEmission.test_engine_never_reads_journal_backward_compatible.md) method: HOLE: no docstring

referenced by: none found
