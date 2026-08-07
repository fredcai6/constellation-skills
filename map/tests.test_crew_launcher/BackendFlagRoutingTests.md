# tests.test_crew_launcher:BackendFlagRoutingTests
class, tests/test_crew_launcher.py:890, 80 lines

```python
class BackendFlagRoutingTests(TestCase)
```

Decision 5: --backend resolves + dispatches through the right backend;

--dispatch stays backward compatible (no auto-detect unless --backend auto).

- [_launch_argv](BackendFlagRoutingTests._launch_argv.md) method: HOLE: no docstring
- [test_backend_cli_spawns_through_the_cli_backend](BackendFlagRoutingTests.test_backend_cli_spawns_through_the_cli_backend.md) method: HOLE: no docstring
- [test_backend_external_records_without_spawning](BackendFlagRoutingTests.test_backend_external_records_without_spawning.md) method: HOLE: no docstring
- [test_backend_wins_over_conflicting_dispatch](BackendFlagRoutingTests.test_backend_wins_over_conflicting_dispatch.md) method: --backend external overrides --dispatch spawn (explicit override wins).
- [test_default_no_backend_flag_resolves_to_cli_without_autodetect](BackendFlagRoutingTests.test_default_no_backend_flag_resolves_to_cli_without_autodetect.md) method: No --backend + default --dispatch spawn -> cli, regardless of PATH

referenced by: none found
