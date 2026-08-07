# tests.test_state_note
tests/test_state_note.py, 97 lines, 15 holes

HOLE: no docstring

imports stdlib: importlib.util, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
FILLED = '# Crash-resume state note — issue-42\n\n- **step:** execute · gate g2-integrate\n- **s...
FOREGROUND = FILLED.replace('- **pid:** 48121', '- **pid:** none — foreground')
UNFILLED = '# Crash-resume state note — <work-id>\n\n- **step:** <which spine/gate step you are on...
```

- [load](load.md) function: HOLE: no docstring
- [ValidateTests](ValidateTests.md) class: HOLE: no docstring
  - [ValidateTests.setUp](ValidateTests.setUp.md) method: HOLE: no docstring
  - [ValidateTests.test_filled_note_has_no_problems](ValidateTests.test_filled_note_has_no_problems.md) method: HOLE: no docstring
  - [ValidateTests.test_foreground_pid_is_a_valid_value](ValidateTests.test_foreground_pid_is_a_valid_value.md) method: HOLE: no docstring
  - [ValidateTests.test_unfilled_template_flags_every_field](ValidateTests.test_unfilled_template_flags_every_field.md) method: HOLE: no docstring
  - [ValidateTests.test_missing_field_is_flagged](ValidateTests.test_missing_field_is_flagged.md) method: HOLE: no docstring
  - [ValidateTests.test_empty_value_is_flagged](ValidateTests.test_empty_value_is_flagged.md) method: HOLE: no docstring
- [CliTests](CliTests.md) class: HOLE: no docstring
  - [CliTests.setUp](CliTests.setUp.md) method: HOLE: no docstring
  - [CliTests.tearDown](CliTests.tearDown.md) method: HOLE: no docstring
  - [CliTests._write](CliTests._write.md) method: HOLE: no docstring
  - [CliTests.test_missing_file_returns_1](CliTests.test_missing_file_returns_1.md) method: HOLE: no docstring
  - [CliTests.test_filled_note_returns_0](CliTests.test_filled_note_returns_0.md) method: HOLE: no docstring
  - [CliTests.test_unfilled_note_returns_1](CliTests.test_unfilled_note_returns_1.md) method: HOLE: no docstring
