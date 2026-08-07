# tests.test_context_declaration_lint:test_divergent_declaration_is_rejected
function, tests/test_context_declaration_lint.py:40, 28 lines

```python
def test_divergent_declaration_is_rejected()
```

The load-bearing negative test, named and shaped exactly as the gate's

postcondition requires: a bare, module-level pytest function (not nested in
a unittest.TestCase class) so that
`pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected`
resolves it directly -- pytest's `::` node-id selector is an exact match, not
a substring search, so a same-named method nested inside a class does NOT
satisfy that node id.

A lint that only passes over the clean shipped corpus proves the corpus is
clean, not that the lint works: this fixture's declaration and prose
genuinely diverge (`references/narrowed-away.md` is declared but never
named in the task's own imperative), and this asserts the lint's real CLI
entry point, `main()`, rejects it -- and that the rejection is traceable to
the actual offending path, not merely "some check somewhere returned
non-zero" (the exact anti-pattern the gate's handoff calls out by name).

calls internal: load
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, json.dumps, pathlib.Path, tempfile.TemporaryDirectory
reads internal: FIXTURES
reads stdlib: contextlib (module), io (module), json (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
