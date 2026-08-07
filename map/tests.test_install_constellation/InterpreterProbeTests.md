# tests.test_install_constellation:InterpreterProbeTests
class, tests/test_install_constellation.py:978, 196 lines

```python
class InterpreterProbeTests(TestCase)
```

Issue #228: real host probe (py -> python3 -> python) + fallback chain +

per-skill sidecar, threaded through install_skills() as an explicit
parameter (never a module-level global/cache).

- [test_probe_resolves_a_real_invocable_interpreter_on_this_host](InterpreterProbeTests.test_probe_resolves_a_real_invocable_interpreter_on_this_host.md) method: HOLE: no docstring
- [test_probe_falls_through_to_next_candidate_when_py_is_unresolvable](InterpreterProbeTests.test_probe_falls_through_to_next_candidate_when_py_is_unresolvable.md) method: HOLE: no docstring
- [test_probe_prefers_py_over_python3_when_both_succeed](InterpreterProbeTests.test_probe_prefers_py_over_python3_when_both_succeed.md) method: HOLE: no docstring
- [test_probe_timeout_candidate_falls_through_without_hanging](InterpreterProbeTests.test_probe_timeout_candidate_falls_through_without_hanging.md) method: HOLE: no docstring
- [test_resolve_interpreter_falls_back_to_os_default_on_total_failure](InterpreterProbeTests.test_resolve_interpreter_falls_back_to_os_default_on_total_failure.md) method: HOLE: no docstring
- [test_probe_invoked_exactly_once_total_across_multi_skill_install](InterpreterProbeTests.test_probe_invoked_exactly_once_total_across_multi_skill_install.md) method: HOLE: no docstring
- [test_sidecar_records_resolved_via_for_probe_success_and_fallback](InterpreterProbeTests.test_sidecar_records_resolved_via_for_probe_success_and_fallback.md) method: HOLE: no docstring

referenced by: none found
