# tests.test_verify_cycles
tests/test_verify_cycles.py, 71 lines, 11 holes

HOLE: no docstring

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CONSOLIDATED_CYCLE = json.dumps({'type': 'survey', 'consolidation': {'verdict': 'converge'}})
UNCONSOLIDATED_CYCLE = json.dumps({'type': 'survey', 'consolidation': None})
```

- [load](load.md) function: HOLE: no docstring
- [VerifyCyclesTests](VerifyCyclesTests.md) class: HOLE: no docstring
  - [VerifyCyclesTests.setUp](VerifyCyclesTests.setUp.md) method: HOLE: no docstring
  - [VerifyCyclesTests.tearDown](VerifyCyclesTests.tearDown.md) method: HOLE: no docstring
  - [VerifyCyclesTests.write_cycle](VerifyCyclesTests.write_cycle.md) method: HOLE: no docstring
  - [VerifyCyclesTests.verify](VerifyCyclesTests.verify.md) method: HOLE: no docstring
  - [VerifyCyclesTests.test_pass_with_consolidated_cycles](VerifyCyclesTests.test_pass_with_consolidated_cycles.md) method: HOLE: no docstring
  - [VerifyCyclesTests.test_fail_zero_cycles](VerifyCyclesTests.test_fail_zero_cycles.md) method: HOLE: no docstring
  - [VerifyCyclesTests.test_fail_unconsolidated_cycle](VerifyCyclesTests.test_fail_unconsolidated_cycle.md) method: HOLE: no docstring
  - [VerifyCyclesTests.test_fail_unparseable_json](VerifyCyclesTests.test_fail_unparseable_json.md) method: HOLE: no docstring
  - [VerifyCyclesTests.test_fail_not_a_survey](VerifyCyclesTests.test_fail_not_a_survey.md) method: HOLE: no docstring
