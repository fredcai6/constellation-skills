[map index](../INDEX.md) / [`src.utils.config`](INDEX.md)

# `Config`
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

- [`Config.db_path_for_year`](Config.db_path_for_year.md) — *class method* — Return the per-season SQLite path: data/f1_data_{year}.db
- [`Config.load_config`](Config.load_config.md) — *class method* — Load and validate configuration from YAML file.
- [`Config.get`](Config.get.md) — *class method* — Get configuration value by key (supports nested keys with dot notation)
- [`Config.get_seasons`](Config.get_seasons.md) — *class method* — Get list of seasons to analyze
- [`Config.get_sessions`](Config.get_sessions.md) — *class method* — Get list of sessions to analyze
- [`Config.get_topk`](Config.get_topk.md) — *class method* — Get top-K value for rank error calculation
- [`Config.get_objective_weights`](Config.get_objective_weights.md) — *class method* — Get objective function weights
- [`Config.get_weight_bounds`](Config.get_weight_bounds.md) — *class method* — Get weight optimization bounds
- [`Config.get_random_seed`](Config.get_random_seed.md) — *class method* — Get random seed for reproducibility
- [`Config.get_data_config`](Config.get_data_config.md) — *class method* — Get data processing configuration
- [`Config.get_feature_config`](Config.get_feature_config.md) — *class method* — Get feature engineering configuration
- [`Config.get_paths`](Config.get_paths.md) — *class method* — Get all system paths
- [`Config._setup_logging`](Config._setup_logging.md) — *class method* — Setup logging configuration
- [`Config._setup_fastf1_cache`](Config._setup_fastf1_cache.md) — *class method* — Setup FastF1 cache configuration
- [`Config.ensure_directories`](Config.ensure_directories.md) — *class method* — Ensure all required directories exist
- [`Config._validate_config`](Config._validate_config.md) — *class method* — Validate configuration schema and required fields.
- [`Config.reload_config`](Config.reload_config.md) — *class method* — Reload configuration from file.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `pathlib.Path` |
| reads | internal | `Config.PROJECT_ROOT` x5, `Config.OUTPUTS_DIR` x4, `Config.CACHE_DIR` |
| reads | stdlib | `builtins.classmethod` x17, `builtins.str` x10, `typing.Any` x6, `typing.Dict` x6, `builtins.int` x3, `builtins.list` x2, `pathlib.Path` x2, `typing.Optional` x2, `builtins.float`, `builtins.tuple` |
| writes | internal | `Config.CACHE_DIR`, `Config.CONFIG_DIR`, `Config.DATABASE_PATH`, `Config.DATA_PROC_DIR`, `Config.DATA_RAW_DIR`, `Config.ERGAST_BASE_URL`, `Config.FASTF1_CACHE_DIR`, `Config.FIGURES_DIR`, `Config.LOGS_DIR`, `Config.MAX_RETRIES`, `Config.OUTPUTS_DIR`, `Config.PROJECT_ROOT`, `Config.REQUEST_DELAY`, `Config.TEST_DATABASE_PATH`, `Config._config_data`, `Config._config_source` |

**Unresolved by the extractor**: 3 reads (dispatch-unknown-base), 1 reads (unbound-name)

**Referenced by**: 10 site(s) across 3 module(s) — src.data.collector x3, src.data.load_fastf1


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
