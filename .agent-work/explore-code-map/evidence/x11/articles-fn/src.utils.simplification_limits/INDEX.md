# src.utils.simplification_limits
src/utils/simplification_limits.py, 317 lines, 14 holes

Machine-checkable simplification limits for Python under src/ and tests/.

Canonical entry: verify_simplification_limits()
CLI: py -m src.utils.simplification_limits [--baseline] [--paths ...]

imports stdlib: __future__.annotations, argparse, ast, dataclasses.asdict, dataclasses.dataclass, json, pathlib.Path, sys, typing.Iterable, typing.List, typing.Optional, typing.Sequence, typing.Tuple
imports third-party: radon.complexity.cc_visit
imported by: none found (scripts/ and tests/ not indexed)

```python
MAX_CYCLOMATIC_COMPLEXITY = 19
MAX_FUNCTION_LINES = 99
MAX_FILE_LINES = 999
DEFAULT_ROOTS = ('src', 'tests')
EXCLUDED_ROOT_PARTS = frozenset({'data', 'archive', '.venv', '__pycache__', '.git', 'node_modules'})
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BASELINE_PATH = PROJECT_ROOT / 'config' / 'simplification_baseline.json'
```

- [Violation](Violation.md) class: HOLE: no docstring
  - [Violation.format_message](Violation.format_message.md) method: HOLE: no docstring
- [SimplificationLimitsResult](SimplificationLimitsResult.md) class: HOLE: no docstring
  - [SimplificationLimitsResult.to_dict](SimplificationLimitsResult.to_dict.md) method: HOLE: no docstring
- [_is_excluded_path](_is_excluded_path.md) function: HOLE: no docstring
- [iter_python_files](iter_python_files.md) function: HOLE: no docstring
- [_function_spans](_function_spans.md) function: HOLE: no docstring
- [_file_line_violations](_file_line_violations.md) function: HOLE: no docstring
- [_function_line_violations](_function_line_violations.md) function: HOLE: no docstring
- [_radon_complexity_violations](_radon_complexity_violations.md) function: HOLE: no docstring
- [load_baseline_config](load_baseline_config.md) function: HOLE: no docstring
- [load_baseline_allowlist](load_baseline_allowlist.md) function: HOLE: no docstring
- [verify_simplification_limits](verify_simplification_limits.md) function: Check simplification limits on Python under the given roots.
- [_print_result](_print_result.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
