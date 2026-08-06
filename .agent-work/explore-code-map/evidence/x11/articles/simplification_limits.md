# `src.utils.simplification_limits`

> Machine-checkable simplification limits for Python under src/ and tests/.
>
> Canonical entry: verify_simplification_limits()
> CLI: py -m src.utils.simplification_limits [--baseline] [--paths ...]

*(everything after the first line above is [s].)*

`src/utils/simplification_limits.py` · 317 lines [s] · 13 top-level, 15 entities total · 1 documented, 14 **holes**

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

- [`Violation`](#violation) — *class* — **[HOLE] undocumented**
- [`SimplificationLimitsResult`](#simplificationlimitsresult) — *class* — **[HOLE] undocumented**
- [`_is_excluded_path`](#-is-excluded-path) — *function* — **[HOLE] undocumented**
- [`iter_python_files`](#iter-python-files) — *function* — **[HOLE] undocumented**
- [`_function_spans`](#-function-spans) — *function* — **[HOLE] undocumented**
- [`_file_line_violations`](#-file-line-violations) — *function* — **[HOLE] undocumented**
- [`_function_line_violations`](#-function-line-violations) — *function* — **[HOLE] undocumented**
- [`_radon_complexity_violations`](#-radon-complexity-violations) — *function* — **[HOLE] undocumented**
- [`load_baseline_config`](#load-baseline-config) — *function* — **[HOLE] undocumented**
- [`load_baseline_allowlist`](#load-baseline-allowlist) — *function* — **[HOLE] undocumented**
- [`verify_simplification_limits`](#verify-simplification-limits) — *function* — Check simplification limits on Python under the given roots.
- [`_print_result`](#-print-result) — *function* — **[HOLE] undocumented**
- [`main`](#main) — *function* — **[HOLE] undocumented**

---

## `Violation`
*class* [s] · [`src/utils/simplification_limits.py:32`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L32) · 13 lines [s]

```python
class Violation
```
**Decorators** [s]: `@dataclass(frozen=True)`

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `path` | `str` | — | 33 | name only |
| `symbol` | `Optional[str]` | — | 34 | name only |
| `metric` | `str` | — | 35 | name only |
| `actual` | `int` | — | 36 | name only |
| `limit` | `int` | — | 37 | name only |

**Members**

- [`Violation.format_message`](#violationformat-message) — *method* — **[HOLE] undocumented**

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.str` x4, `builtins.int` x2, `typing.Optional` |
| writes | internal | `Violation.actual`, `Violation.limit`, `Violation.metric`, `Violation.path`, `Violation.symbol` |

**Referenced by**: 10 site(s) across 1 module(s) (all within this module)


### `Violation.format_message`
*method* [s] · [`src/utils/simplification_limits.py:39`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L39) · 6 lines [s]

**Signature** [s]

```python
def format_message(self) -> str
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Violation.symbol` x2, `Violation.actual`, `Violation.limit`, `Violation.metric`, `Violation.path` |

*Not shown: 1 local-variable reads, 1 local-variable writes; 6 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `SimplificationLimitsResult`
*class* [s] · [`src/utils/simplification_limits.py:48`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L48) · 11 lines [s]

```python
class SimplificationLimitsResult
```
**Decorators** [s]: `@dataclass`

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `passed` | `bool` | — | 49 | name only |
| `violations` | `List[Violation]` | — | 50 | name only |
| `files_checked` | `int` | — | 51 | name only |

**Members**

- [`SimplificationLimitsResult.to_dict`](#simplificationlimitsresultto-dict) — *method* — **[HOLE] undocumented**

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Violation` |
| reads | stdlib | `builtins.bool`, `builtins.dict`, `builtins.int`, `typing.List` |
| writes | internal | `SimplificationLimitsResult.files_checked`, `SimplificationLimitsResult.passed`, `SimplificationLimitsResult.violations` |

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


### `SimplificationLimitsResult.to_dict`
*method* [s] · [`src/utils/simplification_limits.py:53`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L53) · 6 lines [s]

**Signature** [s]

```python
def to_dict(self) -> dict
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `dataclasses.asdict` |
| reads | internal | `SimplificationLimitsResult.files_checked`, `SimplificationLimitsResult.passed`, `SimplificationLimitsResult.violations` |

*Not shown: 1 local-variable reads, 1 local-variable writes; 3 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `_is_excluded_path`
*function* [s] · [`src/utils/simplification_limits.py:61`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L61) · 14 lines [s]

**Signature** [s]

```python
def _is_excluded_path(path: Path, root: Path) -> bool
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*
- `root` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.any` |
| reads | internal | `EXCLUDED_ROOT_PARTS` |
| reads | stdlib | `builtins.ValueError` |

*Not shown: 5 local-variable reads, 3 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `iter_python_files`
*function* [s] · [`src/utils/simplification_limits.py:77`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L77) · 26 lines [s]

**Signature** [s]

```python
def iter_python_files(roots: Sequence[str | Path], *, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None) -> List[Path]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `roots` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*
- `extra_paths` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `_is_excluded_path` |
| calls | stdlib | `builtins.list` x2, `builtins.sorted` x2, `builtins.set`, `pathlib.Path` |
| reads | stdlib | `pathlib.Path` x2, `builtins.set`, `typing.List` |

*Not shown: 18 local-variable reads, 9 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_function_spans`
*function* [s] · [`src/utils/simplification_limits.py:105`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L105) · 11 lines [s]

**Signature** [s]

```python
def _function_spans(tree: ast.AST) -> List[Tuple[str, int, int]]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `tree` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `ast.walk` x2, `builtins.isinstance`, `builtins.max` |
| reads | stdlib | `ast (module)` x4, `builtins.int` x2, `ast.AsyncFunctionDef`, `ast.FunctionDef`, `builtins.str`, `typing.List`, `typing.Tuple` |

*Not shown: 13 local-variable reads, 6 local-variable writes; 1 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 2 calls (dynamic), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_file_line_violations`
*function* [s] · [`src/utils/simplification_limits.py:118`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L118) · 14 lines [s]

**Signature** [s]

```python
def _file_line_violations(path: Path, rel: str) -> List[Violation]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*
- `rel` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Violation` |
| calls | stdlib | `builtins.len` |
| reads | internal | `MAX_FILE_LINES` x2 |

*Not shown: 3 local-variable reads, 2 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_function_line_violations`
*function* [s] · [`src/utils/simplification_limits.py:134`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L134) · 15 lines [s]

**Signature** [s]

```python
def _function_line_violations(path: Path, rel: str, tree: ast.AST) -> List[Violation]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*
- `rel` — *[HOLE] undocumented parameter*
- `tree` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Violation`, `_function_spans` |
| reads | internal | `MAX_FUNCTION_LINES` x2, `Violation` |
| reads | stdlib | `typing.List` |

*Not shown: 7 local-variable reads, 5 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_radon_complexity_violations`
*function* [s] · [`src/utils/simplification_limits.py:151`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L151) · 29 lines [s]

**Signature** [s]

```python
def _radon_complexity_violations(paths: List[Path], project_root: Path) -> List[Violation]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `paths` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Violation` |
| calls | stdlib | `builtins.RuntimeError`, `builtins.str` |
| reads | internal | `MAX_CYCLOMATIC_COMPLEXITY` x2, `Violation` |
| reads | stdlib | `builtins.ImportError`, `builtins.SyntaxError`, `typing.List` |

*Not shown: 1 local-variable calls, 11 local-variable reads, 6 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `load_baseline_config`
*function* [s] · [`src/utils/simplification_limits.py:182`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L182) · 9 lines [s]

**Signature** [s]

```python
def load_baseline_config(path: Path = DEFAULT_BASELINE_PATH) -> tuple[frozenset[str], frozenset[str]]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.frozenset` x4, `builtins.str` x2, `json.loads` |
| reads | stdlib | `json (module)` |

*Not shown: 8 local-variable reads, 7 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 5 calls (dispatch-unknown-base)

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


## `load_baseline_allowlist`
*function* [s] · [`src/utils/simplification_limits.py:193`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L193) · 3 lines [s]

**Signature** [s]

```python
def load_baseline_allowlist(path: Path = DEFAULT_BASELINE_PATH) -> frozenset[str]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `load_baseline_config` |

*Not shown: 1 local-variable reads, 2 local-variable writes; 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `verify_simplification_limits`
*function* [s] · [`src/utils/simplification_limits.py:198`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L198) · 61 lines [s]

**Signature** [s]

```python
def verify_simplification_limits(*, roots: Sequence[str | Path] = DEFAULT_ROOTS, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None, use_baseline: bool = False, baseline_path: Optional[Path] = None, metrics: Optional[Sequence[str]] = None) -> SimplificationLimitsResult
```

> Check simplification limits on Python under the given roots.
>
> Returns pass/fail and structured violations (path, symbol, metric, actual, limit).
> With use_baseline=True, paths listed in simplification_baseline.json are skipped.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `roots` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*
- `extra_paths` — *[HOLE] undocumented parameter*
- `use_baseline` — *[HOLE] undocumented parameter*
- `baseline_path` — *[HOLE] undocumented parameter*
- `metrics` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `load_baseline_config` x2, `SimplificationLimitsResult`, `_file_line_violations`, `_function_line_violations`, `_radon_complexity_violations`, `iter_python_files` |
| calls | stdlib | `builtins.frozenset` x4, `ast.parse`, `builtins.len`, `builtins.str` |
| reads | internal | `DEFAULT_BASELINE_PATH`, `Violation` |
| reads | stdlib | `typing.List` x2, `ast (module)`, `builtins.SyntaxError`, `pathlib.Path` |

*Not shown: 30 local-variable reads, 17 local-variable writes; 12 reads of its own parameters.*

**Unresolved by the extractor**: 8 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 3 reads (unbound-name)

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


## `_print_result`
*function* [s] · [`src/utils/simplification_limits.py:261`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L261) · 7 lines [s]

**Signature** [s]

```python
def _print_result(result: SimplificationLimitsResult) -> None
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `result` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.print` x3, `builtins.len` |
| reads | internal | `SimplificationLimitsResult.files_checked` x2, `SimplificationLimitsResult.violations` x2, `SimplificationLimitsResult.passed` |

*Not shown: 1 local-variable reads, 1 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `main`
*function* [s] · [`src/utils/simplification_limits.py:270`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L270) · 44 lines [s]

**Signature** [s]

```python
def main(argv: Optional[Sequence[str]] = None) -> int
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `argv` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `verify_simplification_limits` x2, `_print_result` |
| calls | stdlib | `argparse.ArgumentParser`, `builtins.print`, `json.dumps` |
| reads | stdlib | `argparse (module)`, `builtins.__doc__`, `json (module)` |

*Not shown: 16 local-variable reads, 5 local-variable writes; 1 reads of its own parameters.*

**Unresolved by the extractor**: 6 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
