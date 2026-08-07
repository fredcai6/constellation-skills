# tests.test_context_manifest:ProducerGuards._names_used
static method, tests/test_context_manifest.py:730, 18 lines

```python
def _names_used(path)
```

Every identifier and attribute actually *used as code* in a module.

Parsed rather than grepped: a substring scan would trip over the module's
own prose ("no globs", "not sorted()") and report a comment as a violation.

calls stdlib: builtins.isinstance x4, ast.parse, ast.walk, builtins.set
reads stdlib: ast (module) x6, ast.Attribute, ast.Import, ast.ImportFrom, ast.Name
unresolved: 6 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
