# tests.test_crew_launcher:SelectBackendTests
class, tests/test_crew_launcher.py:843, 45 lines

```python
class SelectBackendTests(TestCase)
```

Decision 4: explicit override always wins; None/auto auto-detects from PATH

presence via the injectable `which`.

- [_found](SelectBackendTests._found.md) static method: HOLE: no docstring
- [_absent](SelectBackendTests._absent.md) static method: HOLE: no docstring
- [test_explicit_cli_wins_even_when_cli_absent](SelectBackendTests.test_explicit_cli_wins_even_when_cli_absent.md) method: HOLE: no docstring
- [test_explicit_external_wins_even_when_cli_present](SelectBackendTests.test_explicit_external_wins_even_when_cli_present.md) method: HOLE: no docstring
- [test_auto_detects_cli_when_launcher_on_path](SelectBackendTests.test_auto_detects_cli_when_launcher_on_path.md) method: HOLE: no docstring
- [test_auto_detects_external_when_launcher_absent](SelectBackendTests.test_auto_detects_external_when_launcher_absent.md) method: HOLE: no docstring
- [test_none_auto_detects_like_auto](SelectBackendTests.test_none_auto_detects_like_auto.md) method: HOLE: no docstring
- [test_auto_detect_uses_the_launcher_argument](SelectBackendTests.test_auto_detect_uses_the_launcher_argument.md) method: HOLE: no docstring
- [test_unknown_token_fails_visibly](SelectBackendTests.test_unknown_token_fails_visibly.md) method: HOLE: no docstring

reads stdlib: builtins.staticmethod x2

referenced by: none found
