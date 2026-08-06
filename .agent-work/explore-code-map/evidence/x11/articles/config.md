# `src.utils.config`

> Configuration management for F1Brainz Advanced ML System
>
> This module handles loading configuration from YAML files and provides
> easy access to all system settings.

*(everything after the first line above is [s].)*

`src/utils/config.py` · 381 lines [s] · 3 top-level, 20 entities total · 20 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `logging`, `pathlib.Path`, `typing.Any`, `typing.Dict`, `typing.Optional`
**Imports (third-party)**: `fastf1`, `yaml`

**Imports (internal)**: `src.models.exceptions:ConfigurationError`

**Imported by** (7 modules in the extraction window): `src.data.collector`, `src.data.database`, `src.data.database._ingest`, `src.data.database._results`, `src.data.database._telemetry_store`, `src.data.load_fastf1`, `src.physics.physics_config`

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `PROJECT_ROOT` | — | `Config.PROJECT_ROOT` | 332 | name only |
| `DATABASE_PATH` | — | `Config.DATABASE_PATH` | 333 | name only |
| `TEST_DATABASE_PATH` | — | `Config.TEST_DATABASE_PATH` | 334 | name only |

## Contents

- [`Config`](#config) — *class* — Configuration manager for F1Brainz system
- [`load_config`](#load-config) — *function* — Load configuration from YAML file.
- [`get_config_value`](#get-config-value) — *function* — Get configuration value by key.

---

## `Config`
*class* [s] · [`src/utils/config.py:17`](C:/Programs/f1Brainz/src/utils/config.py#L17) · 313 lines [s]

```python
class Config
```

> Configuration manager for F1Brainz system

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `PROJECT_ROOT` | — | `Path(__file__).parent.parent.parent` | 21 | name only |
| `CONFIG_DIR` | — | `PROJECT_ROOT / 'configs'` | 22 | name only |
| `OUTPUTS_DIR` | — | `PROJECT_ROOT / 'outputs'` | 23 | name only |
| `CACHE_DIR` | — | `PROJECT_ROOT / 'data' / 'telemetry'` | 25 | name only |
| `DATA_RAW_DIR` | — | `OUTPUTS_DIR / 'data_raw'` | 26 | name only |
| `DATA_PROC_DIR` | — | `OUTPUTS_DIR / 'data_proc'` | 27 | name only |
| `LOGS_DIR` | — | `OUTPUTS_DIR / 'logs'` | 28 | name only |
| `FIGURES_DIR` | — | `OUTPUTS_DIR / 'figs'` | 29 | name only |
| `DATABASE_PATH` | — | `PROJECT_ROOT / 'data' / 'f1_data.db'` | 32 | name only |
| `TEST_DATABASE_PATH` | — | `PROJECT_ROOT / 'data' / 'f1_data_test.db'` | 33 | name only |
| `ERGAST_BASE_URL` | — | `'https://ergast.com/api/f1'` | 39 | name only |
| `FASTF1_CACHE_DIR` | — | `CACHE_DIR` | 40 | name only |
| `MAX_RETRIES` | — | `3` | 41 | name only |
| `REQUEST_DELAY` | — | `0.5` | 42 | name only |
| `_config_data` | `Optional[Dict[str, Any]]` | `None` | 45 | name only |
| `_config_source` | `Optional[str]` | `None` | 46 | name only |

**Members**

- [`Config.db_path_for_year`](#configdb-path-for-year) — *class method* — Return the per-season SQLite path: data/f1_data_{year}.db
- [`Config.load_config`](#configload-config) — *class method* — Load and validate configuration from YAML file.
- [`Config.get`](#configget) — *class method* — Get configuration value by key (supports nested keys with dot notation)
- [`Config.get_seasons`](#configget-seasons) — *class method* — Get list of seasons to analyze
- [`Config.get_sessions`](#configget-sessions) — *class method* — Get list of sessions to analyze
- [`Config.get_topk`](#configget-topk) — *class method* — Get top-K value for rank error calculation
- [`Config.get_objective_weights`](#configget-objective-weights) — *class method* — Get objective function weights
- [`Config.get_weight_bounds`](#configget-weight-bounds) — *class method* — Get weight optimization bounds
- [`Config.get_random_seed`](#configget-random-seed) — *class method* — Get random seed for reproducibility
- [`Config.get_data_config`](#configget-data-config) — *class method* — Get data processing configuration
- [`Config.get_feature_config`](#configget-feature-config) — *class method* — Get feature engineering configuration
- [`Config.get_paths`](#configget-paths) — *class method* — Get all system paths
- [`Config._setup_logging`](#config-setup-logging) — *class method* — Setup logging configuration
- [`Config._setup_fastf1_cache`](#config-setup-fastf1-cache) — *class method* — Setup FastF1 cache configuration
- [`Config.ensure_directories`](#configensure-directories) — *class method* — Ensure all required directories exist
- [`Config._validate_config`](#config-validate-config) — *class method* — Validate configuration schema and required fields.
- [`Config.reload_config`](#configreload-config) — *class method* — Reload configuration from file.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `pathlib.Path` |
| reads | internal | `Config.PROJECT_ROOT` x5, `Config.OUTPUTS_DIR` x4, `Config.CACHE_DIR` |
| reads | stdlib | `builtins.classmethod` x17, `builtins.str` x10, `typing.Any` x6, `typing.Dict` x6, `builtins.int` x3, `builtins.list` x2, `pathlib.Path` x2, `typing.Optional` x2, `builtins.float`, `builtins.tuple` |
| writes | internal | `Config.CACHE_DIR`, `Config.CONFIG_DIR`, `Config.DATABASE_PATH`, `Config.DATA_PROC_DIR`, `Config.DATA_RAW_DIR`, `Config.ERGAST_BASE_URL`, `Config.FASTF1_CACHE_DIR`, `Config.FIGURES_DIR`, `Config.LOGS_DIR`, `Config.MAX_RETRIES`, `Config.OUTPUTS_DIR`, `Config.PROJECT_ROOT`, `Config.REQUEST_DELAY`, `Config.TEST_DATABASE_PATH`, `Config._config_data`, `Config._config_source` |

**Unresolved by the extractor**: 3 reads (dispatch-unknown-base), 1 reads (unbound-name)

**Referenced by**: 10 site(s) across 3 module(s) — src.data.collector x3, src.data.load_fastf1


### `Config.db_path_for_year`
*class method* [s] · [`src/utils/config.py:36`](C:/Programs/f1Brainz/src/utils/config.py#L36) · 3 lines [s]

**Signature** [s]

```python
def db_path_for_year(cls, year: int) -> Path
```

> Return the per-season SQLite path: data/f1_data_{year}.db

**Parameters**

- `year` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Config.PROJECT_ROOT` |

*Not shown: 2 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.load_config`
*class method* [s] · [`src/utils/config.py:49`](C:/Programs/f1Brainz/src/utils/config.py#L49) · 56 lines [s]

**Signature** [s]

```python
def load_config(cls, config_file: str = 'default.yaml') -> Dict[str, Any]
```

> Load and validate configuration from YAML file.
>
> Args:
>     config_file: Name of config file in configs/ directory
>
> Returns:
>     Validated configuration dictionary
>
> Raises:
>     ConfigurationError: If config file missing or invalid

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Name of config file in configs/ directory [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config._setup_fastf1_cache`, `Config._setup_logging`, `Config._validate_config` |
| calls | cross-module | `src.models.exceptions:ConfigurationError` x3 |
| calls | stdlib | `builtins.str` x4, `builtins.open`, `pathlib.Path` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `Config._config_data` x6, `Config._config_source` x2, `Config.CONFIG_DIR` |
| reads | third-party | `yaml (module)` x2, `yaml.YAMLError` |
| writes | internal | `Config._config_data`, `Config._config_source` |

*Not shown: 12 local-variable reads, 4 local-variable writes; 19 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


### `Config.get`
*class method* [s] · [`src/utils/config.py:107`](C:/Programs/f1Brainz/src/utils/config.py#L107) · 14 lines [s]

**Signature** [s]

```python
def get(cls, key: str, default: Any = None) -> Any
```

> Get configuration value by key (supports nested keys with dot notation)

**Parameters**

- `key` — key (supports nested keys with dot notation) [a]
- `default` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| reads | stdlib | `builtins.KeyError`, `builtins.TypeError` |

*Not shown: 5 local-variable reads, 5 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 9 site(s) across 1 module(s) (all within this module)


### `Config.get_seasons`
*class method* [s] · [`src/utils/config.py:123`](C:/Programs/f1Brainz/src/utils/config.py#L123) · 3 lines [s]

**Signature** [s]

```python
def get_seasons(cls) -> list
```

> Get list of seasons to analyze

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_sessions`
*class method* [s] · [`src/utils/config.py:128`](C:/Programs/f1Brainz/src/utils/config.py#L128) · 3 lines [s]

**Signature** [s]

```python
def get_sessions(cls) -> list
```

> Get list of sessions to analyze

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_topk`
*class method* [s] · [`src/utils/config.py:133`](C:/Programs/f1Brainz/src/utils/config.py#L133) · 3 lines [s]

**Signature** [s]

```python
def get_topk(cls) -> int
```

> Get top-K value for rank error calculation

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_objective_weights`
*class method* [s] · [`src/utils/config.py:138`](C:/Programs/f1Brainz/src/utils/config.py#L138) · 3 lines [s]

**Signature** [s]

```python
def get_objective_weights(cls) -> Dict[str, float]
```

> Get objective function weights

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_weight_bounds`
*class method* [s] · [`src/utils/config.py:143`](C:/Programs/f1Brainz/src/utils/config.py#L143) · 4 lines [s]

**Signature** [s]

```python
def get_weight_bounds(cls) -> tuple
```

> Get weight optimization bounds

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 2 local-variable reads, 1 local-variable writes; 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_random_seed`
*class method* [s] · [`src/utils/config.py:149`](C:/Programs/f1Brainz/src/utils/config.py#L149) · 3 lines [s]

**Signature** [s]

```python
def get_random_seed(cls) -> int
```

> Get random seed for reproducibility

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_data_config`
*class method* [s] · [`src/utils/config.py:154`](C:/Programs/f1Brainz/src/utils/config.py#L154) · 3 lines [s]

**Signature** [s]

```python
def get_data_config(cls) -> Dict[str, Any]
```

> Get data processing configuration

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_feature_config`
*class method* [s] · [`src/utils/config.py:159`](C:/Programs/f1Brainz/src/utils/config.py#L159) · 3 lines [s]

**Signature** [s]

```python
def get_feature_config(cls) -> Dict[str, Any]
```

> Get feature engineering configuration

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config.get_paths`
*class method* [s] · [`src/utils/config.py:164`](C:/Programs/f1Brainz/src/utils/config.py#L164) · 12 lines [s]

**Signature** [s]

```python
def get_paths(cls) -> Dict[str, Path]
```

> Get all system paths

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Config.CACHE_DIR`, `Config.CONFIG_DIR`, `Config.DATA_PROC_DIR`, `Config.DATA_RAW_DIR`, `Config.FIGURES_DIR`, `Config.LOGS_DIR`, `Config.OUTPUTS_DIR`, `Config.PROJECT_ROOT` |

*Not shown: 8 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `Config._setup_logging`
*class method* [s] · [`src/utils/config.py:178`](C:/Programs/f1Brainz/src/utils/config.py#L178) · 23 lines [s]

**Signature** [s]

```python
def _setup_logging(cls)
```

> Setup logging configuration

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `logging.FileHandler`, `logging.StreamHandler`, `logging.basicConfig`, `logging.info`, `pathlib.Path` |
| reads | internal | `Config.LOGS_DIR` x2, `Config._config_data` |
| reads | stdlib | `logging (module)` x5 |

*Not shown: 7 local-variable reads, 5 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 5 calls (dispatch-unknown-base), 1 calls (dynamic), 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `Config._setup_fastf1_cache`
*class method* [s] · [`src/utils/config.py:203`](C:/Programs/f1Brainz/src/utils/config.py#L203) · 28 lines [s]

**Signature** [s]

```python
def _setup_fastf1_cache(cls)
```

> Setup FastF1 cache configuration

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `logging.info` x4, `builtins.callable` x2, `builtins.str`, `logging.warning` |
| reads | internal | `Config.FASTF1_CACHE_DIR`, `Config._config_data` |
| reads | stdlib | `logging (module)` x5, `builtins.ImportError` |

*Not shown: 2 local-variable calls, 10 local-variable reads, 5 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base), 2 calls (dynamic), 2 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `Config.ensure_directories`
*class method* [s] · [`src/utils/config.py:233`](C:/Programs/f1Brainz/src/utils/config.py#L233) · 8 lines [s]

**Signature** [s]

```python
def ensure_directories(cls)
```

> Ensure all required directories exist

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get_paths` |
| calls | stdlib | `logging.debug` |
| reads | stdlib | `logging (module)` |

*Not shown: 5 local-variable reads, 3 local-variable writes; 1 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `Config._validate_config`
*class method* [s] · [`src/utils/config.py:243`](C:/Programs/f1Brainz/src/utils/config.py#L243) · 72 lines [s]

**Signature** [s]

```python
def _validate_config(cls)
```

> Validate configuration schema and required fields.
>
> Raises:
>     ConfigurationError: If required fields are missing or invalid

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | cross-module | `src.models.exceptions:ConfigurationError` x8 |
| calls | stdlib | `builtins.isinstance` x3, `builtins.list`, `builtins.type` |
| reads | internal | `Config._config_data` x2 |
| reads | stdlib | `builtins.int` x2, `builtins.list` x2, `builtins.dict` |

*Not shown: 37 local-variable reads, 12 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `Config.reload_config`
*class method* [s] · [`src/utils/config.py:317`](C:/Programs/f1Brainz/src/utils/config.py#L317) · 13 lines [s]

**Signature** [s]

```python
def reload_config(cls, config_file: str = 'default.yaml')
```

> Reload configuration from file.
>
> Args:
>     config_file: Name of config file to reload
>
> Returns:
>     Reloaded configuration dictionary

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Name of config file to reload [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| writes | internal | `Config._config_data`, `Config._config_source` |

*Not shown: 4 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `load_config`
*function* [s] · [`src/utils/config.py:338`](C:/Programs/f1Brainz/src/utils/config.py#L338) · 27 lines [s]

**Signature** [s]

```python
def load_config(config_file: str = 'default.yaml') -> Dict[str, Any]
```

> Load configuration from YAML file.
>
> Args:
>     config_file: Path to config file or name of file in configs/ directory
>
> Returns:
>     Configuration dictionary

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Path to config file or name of file in configs/ directory [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| calls | stdlib | `builtins.open`, `pathlib.Path` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `Config` x2, `Config.CONFIG_DIR` |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `yaml (module)` x2, `yaml.YAMLError` |

*Not shown: 3 local-variable reads, 2 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `get_config_value`
*function* [s] · [`src/utils/config.py:367`](C:/Programs/f1Brainz/src/utils/config.py#L367) · 15 lines [s]

**Signature** [s]

```python
def get_config_value(key: str, default: Any = None) -> Any
```

> Get configuration value by key.
>
> Args:
>     key: Configuration key (supports dot notation for nested keys)
>     default: Default value if key not found
>
> Returns:
>     Configuration value or default

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `key` — key: Configuration key (supports dot notation for nested keys) [a]
- `default` — default: Default value if key not found [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |
| reads | internal | `Config` |
| reads | stdlib | `builtins.Exception` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.physics.physics_config


---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
