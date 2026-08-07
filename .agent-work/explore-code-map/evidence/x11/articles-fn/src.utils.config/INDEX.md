# src.utils.config
src/utils/config.py, 381 lines

Configuration management for F1Brainz Advanced ML System

This module handles loading configuration from YAML files and provides
easy access to all system settings.

imports stdlib: logging, pathlib.Path, typing.Any, typing.Dict, typing.Optional
imports third-party: fastf1, yaml
imports internal: src.models.exceptions:ConfigurationError
imported by: src.data.collector, src.data.database, src.data.database._ingest, src.data.database._results, src.data.database._telemetry_store, src.data.load_fastf1, src.physics.physics_config

```python
PROJECT_ROOT = Config.PROJECT_ROOT
DATABASE_PATH = Config.DATABASE_PATH
TEST_DATABASE_PATH = Config.TEST_DATABASE_PATH
```

- [Config](Config.md) class: Configuration manager for F1Brainz system
  - [Config.db_path_for_year](Config.db_path_for_year.md) class method: Return the per-season SQLite path: data/f1_data_{year}.db
  - [Config.load_config](Config.load_config.md) class method: Load and validate configuration from YAML file.
  - [Config.get](Config.get.md) class method: Get configuration value by key (supports nested keys with dot notation)
  - [Config.get_seasons](Config.get_seasons.md) class method: Get list of seasons to analyze
  - [Config.get_sessions](Config.get_sessions.md) class method: Get list of sessions to analyze
  - [Config.get_topk](Config.get_topk.md) class method: Get top-K value for rank error calculation
  - [Config.get_objective_weights](Config.get_objective_weights.md) class method: Get objective function weights
  - [Config.get_weight_bounds](Config.get_weight_bounds.md) class method: Get weight optimization bounds
  - [Config.get_random_seed](Config.get_random_seed.md) class method: Get random seed for reproducibility
  - [Config.get_data_config](Config.get_data_config.md) class method: Get data processing configuration
  - [Config.get_feature_config](Config.get_feature_config.md) class method: Get feature engineering configuration
  - [Config.get_paths](Config.get_paths.md) class method: Get all system paths
  - [Config._setup_logging](Config._setup_logging.md) class method: Setup logging configuration
  - [Config._setup_fastf1_cache](Config._setup_fastf1_cache.md) class method: Setup FastF1 cache configuration
  - [Config.ensure_directories](Config.ensure_directories.md) class method: Ensure all required directories exist
  - [Config._validate_config](Config._validate_config.md) class method: Validate configuration schema and required fields.
  - [Config.reload_config](Config.reload_config.md) class method: Reload configuration from file.
- [load_config](load_config.md) function: Load configuration from YAML file.
- [get_config_value](get_config_value.md) function: Get configuration value by key.
