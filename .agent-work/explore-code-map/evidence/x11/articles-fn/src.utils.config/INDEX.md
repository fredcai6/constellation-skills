[map index](../INDEX.md)

# `src.utils.config`

> Configuration management for F1Brainz Advanced ML System
>
> This module handles loading configuration from YAML files and provides
> easy access to all system settings.

*(everything after the first line above is [s].)*

`src/utils/config.py` · 381 lines [s] · 20 entities · 20 documented, 0 **holes**

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

- [`Config`](Config.md) — *class* [s] — Configuration manager for F1Brainz system
  - [`Config.db_path_for_year`](Config.db_path_for_year.md) — *class method* [s] — Return the per-season SQLite path: data/f1_data_{year}.db
  - [`Config.load_config`](Config.load_config.md) — *class method* [s] — Load and validate configuration from YAML file.
  - [`Config.get`](Config.get.md) — *class method* [s] — Get configuration value by key (supports nested keys with dot notation)
  - [`Config.get_seasons`](Config.get_seasons.md) — *class method* [s] — Get list of seasons to analyze
  - [`Config.get_sessions`](Config.get_sessions.md) — *class method* [s] — Get list of sessions to analyze
  - [`Config.get_topk`](Config.get_topk.md) — *class method* [s] — Get top-K value for rank error calculation
  - [`Config.get_objective_weights`](Config.get_objective_weights.md) — *class method* [s] — Get objective function weights
  - [`Config.get_weight_bounds`](Config.get_weight_bounds.md) — *class method* [s] — Get weight optimization bounds
  - [`Config.get_random_seed`](Config.get_random_seed.md) — *class method* [s] — Get random seed for reproducibility
  - [`Config.get_data_config`](Config.get_data_config.md) — *class method* [s] — Get data processing configuration
  - [`Config.get_feature_config`](Config.get_feature_config.md) — *class method* [s] — Get feature engineering configuration
  - [`Config.get_paths`](Config.get_paths.md) — *class method* [s] — Get all system paths
  - [`Config._setup_logging`](Config._setup_logging.md) — *class method* [s] — Setup logging configuration
  - [`Config._setup_fastf1_cache`](Config._setup_fastf1_cache.md) — *class method* [s] — Setup FastF1 cache configuration
  - [`Config.ensure_directories`](Config.ensure_directories.md) — *class method* [s] — Ensure all required directories exist
  - [`Config._validate_config`](Config._validate_config.md) — *class method* [s] — Validate configuration schema and required fields.
  - [`Config.reload_config`](Config.reload_config.md) — *class method* [s] — Reload configuration from file.
- [`load_config`](load_config.md) — *function* [s] — Load configuration from YAML file.
- [`get_config_value`](get_config_value.md) — *function* [s] — Get configuration value by key.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
