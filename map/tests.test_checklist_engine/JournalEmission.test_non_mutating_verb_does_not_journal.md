# tests.test_checklist_engine:JournalEmission.test_non_mutating_verb_does_not_journal
method, tests/test_checklist_engine.py:1744, 6 lines

```python
def test_non_mutating_verb_does_not_journal(self)
```

HOLE: no docstring

calls internal: JournalEmission.assertEqual x2, JournalEmission._journal_lines, JournalEmission._save, gate, gated
calls stdlib: builtins.str, tempfile.TemporaryDirectory
reads internal: E, PASS_COMMAND
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
