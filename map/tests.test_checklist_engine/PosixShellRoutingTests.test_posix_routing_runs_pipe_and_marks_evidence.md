# tests.test_checklist_engine:PosixShellRoutingTests.test_posix_routing_runs_pipe_and_marks_evidence
method, tests/test_checklist_engine.py:1254, 9 lines

```python
@unittest.skipUnless(E._find_posix_shell(), 'no POSIX shell found')
def test_posix_routing_runs_pipe_and_marks_evidence(self)
```

HOLE: no docstring

calls internal: PosixShellRoutingTests.assertEqual x2, gate, gated
reads internal: E
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
