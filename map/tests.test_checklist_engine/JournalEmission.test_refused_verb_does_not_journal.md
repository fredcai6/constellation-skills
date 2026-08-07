# tests.test_checklist_engine:JournalEmission.test_refused_verb_does_not_journal
method, tests/test_checklist_engine.py:1758, 7 lines

```python
def test_refused_verb_does_not_journal(self)
```

HOLE: no docstring

calls internal: JournalEmission.assertEqual x2, JournalEmission._journal_lines, JournalEmission._save, gate, gated
calls stdlib: builtins.str, tempfile.TemporaryDirectory
reads internal: E, FAIL_COMMAND
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
