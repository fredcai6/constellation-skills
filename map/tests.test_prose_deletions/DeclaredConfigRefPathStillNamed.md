# tests.test_prose_deletions:DeclaredConfigRefPathStillNamed
class, tests/test_prose_deletions.py:127, 13 lines

```python
class DeclaredConfigRefPathStillNamed(TestCase)
```

The deleted block mentioned a declared `context_refs` path.

`test_context_declaration_lint.py` requires every declared `context_refs`
path to appear verbatim in its task's imperative. `docs/agents/engine-config.json`
is declared, and the deleted block named it -- so this asserts directly what
that lint would otherwise catch only indirectly: the path survives the
deletion because the intake sentence at the top of the imperative still
names it.

- [test_engine_config_path_still_named_in_context_imperative](DeclaredConfigRefPathStillNamed.test_engine_config_path_still_named_in_context_imperative.md) method: HOLE: no docstring

referenced by: none found
