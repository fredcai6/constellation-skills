# tests.test_to_issues:IdempotencyTests
class, tests/test_to_issues.py:227, 38 lines

```python
class IdempotencyTests(TestCase)
```

Crash-injection at the three named points (DESIGN_SPEC TF7). Each: crash

mid-file, then re-run to completion, and assert NO duplicate epic and no
duplicate issues.

- [setUp](IdempotencyTests.setUp.md) method: HOLE: no docstring
- [_run_with_crash_then_complete](IdempotencyTests._run_with_crash_then_complete.md) method: HOLE: no docstring
- [test_crash_before_file](IdempotencyTests.test_crash_before_file.md) method: HOLE: no docstring
- [test_crash_after_file_before_receipt](IdempotencyTests.test_crash_after_file_before_receipt.md) method: HOLE: no docstring
- [test_crash_after_receipt](IdempotencyTests.test_crash_after_receipt.md) method: HOLE: no docstring

reads stdlib: builtins.str

referenced by: none found
