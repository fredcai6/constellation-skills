[map index](../INDEX.md)

# `src.utils.simplification_limits`

> Machine-checkable simplification limits for Python under src/ and tests/.
>
> Canonical entry: verify_simplification_limits()
> CLI: py -m src.utils.simplification_limits [--baseline] [--paths ...]

*(everything after the first line above is [s].)*

`src/utils/simplification_limits.py` · 317 lines [s] · 15 entities · 1 documented, 14 **holes**

## Dependencies

**Imports (stdlib)**: `__future__.annotations`, `argparse`, `ast`, `dataclasses.asdict`, `dataclasses.dataclass`, `json`, `pathlib.Path`, `sys`, `typing.Iterable`, `typing.List`, `typing.Optional`, `typing.Sequence`, `typing.Tuple`
**Imports (third-party)**: `radon.complexity.cc_visit`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `MAX_CYCLOMATIC_COMPLEXITY` | — | `19` | 19 | name only |
| `MAX_FUNCTION_LINES` | — | `99` | 20 | name only |
| `MAX_FILE_LINES` | — | `999` | 21 | name only |
| `DEFAULT_ROOTS` | — | `('src', 'tests')` | 23 | name only |
| `EXCLUDED_ROOT_PARTS` | — | `frozenset({'data', 'archive', '.venv', '__pycache__', '.git', 'node...` | 25 | name only |
| `PROJECT_ROOT` | — | `Path(__file__).resolve().parent.parent.parent` | 27 | name only |
| `DEFAULT_BASELINE_PATH` | — | `PROJECT_ROOT / 'config' / 'simplification_baseline.json'` | 28 | name only |

## Contents

- [`Violation`](Violation.md) — *class* [s] — **[HOLE] undocumented**
  - [`Violation.format_message`](Violation.format_message.md) — *method* [s] — **[HOLE] undocumented**
- [`SimplificationLimitsResult`](SimplificationLimitsResult.md) — *class* [s] — **[HOLE] undocumented**
  - [`SimplificationLimitsResult.to_dict`](SimplificationLimitsResult.to_dict.md) — *method* [s] — **[HOLE] undocumented**
- [`_is_excluded_path`](_is_excluded_path.md) — *function* [s] — **[HOLE] undocumented**
- [`iter_python_files`](iter_python_files.md) — *function* [s] — **[HOLE] undocumented**
- [`_function_spans`](_function_spans.md) — *function* [s] — **[HOLE] undocumented**
- [`_file_line_violations`](_file_line_violations.md) — *function* [s] — **[HOLE] undocumented**
- [`_function_line_violations`](_function_line_violations.md) — *function* [s] — **[HOLE] undocumented**
- [`_radon_complexity_violations`](_radon_complexity_violations.md) — *function* [s] — **[HOLE] undocumented**
- [`load_baseline_config`](load_baseline_config.md) — *function* [s] — **[HOLE] undocumented**
- [`load_baseline_allowlist`](load_baseline_allowlist.md) — *function* [s] — **[HOLE] undocumented**
- [`verify_simplification_limits`](verify_simplification_limits.md) — *function* [s] — Check simplification limits on Python under the given roots.
- [`_print_result`](_print_result.md) — *function* [s] — **[HOLE] undocumented**
- [`main`](main.md) — *function* [s] — **[HOLE] undocumented**
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
