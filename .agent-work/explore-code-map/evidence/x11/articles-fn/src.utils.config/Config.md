# src.utils.config:Config
class, src/utils/config.py:17, 313 lines

```python
class Config
```

Configuration manager for F1Brainz system

```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / 'configs'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
CACHE_DIR = PROJECT_ROOT / 'data' / 'telemetry'
DATA_RAW_DIR = OUTPUTS_DIR / 'data_raw'
DATA_PROC_DIR = OUTPUTS_DIR / 'data_proc'
LOGS_DIR = OUTPUTS_DIR / 'logs'
FIGURES_DIR = OUTPUTS_DIR / 'figs'
DATABASE_PATH = PROJECT_ROOT / 'data' / 'f1_data.db'
TEST_DATABASE_PATH = PROJECT_ROOT / 'data' / 'f1_data_test.db'
ERGAST_BASE_URL = 'https://ergast.com/api/f1'
FASTF1_CACHE_DIR = CACHE_DIR
MAX_RETRIES = 3
REQUEST_DELAY = 0.5
_config_data: Optional[Dict[str, Any]] = None
_config_source: Optional[str] = None
```

- [db_path_for_year](Config.db_path_for_year.md) class method: Return the per-season SQLite path: data/f1_data_{year}.db
- [load_config](Config.load_config.md) class method: Load and validate configuration from YAML file.
- [get](Config.get.md) class method: Get configuration value by key (supports nested keys with dot notation)
- [get_seasons](Config.get_seasons.md) class method: Get list of seasons to analyze
- [get_sessions](Config.get_sessions.md) class method: Get list of sessions to analyze
- [get_topk](Config.get_topk.md) class method: Get top-K value for rank error calculation
- [get_objective_weights](Config.get_objective_weights.md) class method: Get objective function weights
- [get_weight_bounds](Config.get_weight_bounds.md) class method: Get weight optimization bounds
- [get_random_seed](Config.get_random_seed.md) class method: Get random seed for reproducibility
- [get_data_config](Config.get_data_config.md) class method: Get data processing configuration
- [get_feature_config](Config.get_feature_config.md) class method: Get feature engineering configuration
- [get_paths](Config.get_paths.md) class method: Get all system paths
- [_setup_logging](Config._setup_logging.md) class method: Setup logging configuration
- [_setup_fastf1_cache](Config._setup_fastf1_cache.md) class method: Setup FastF1 cache configuration
- [ensure_directories](Config.ensure_directories.md) class method: Ensure all required directories exist
- [_validate_config](Config._validate_config.md) class method: Validate configuration schema and required fields.
- [reload_config](Config.reload_config.md) class method: Reload configuration from file.

calls stdlib: pathlib.Path
reads internal: Config.PROJECT_ROOT x5, Config.OUTPUTS_DIR x4, Config.CACHE_DIR
reads stdlib: builtins.classmethod x17, builtins.str x10, typing.Any x6, typing.Dict x6, builtins.int x3, builtins.list x2, pathlib.Path x2, typing.Optional x2, builtins.float, builtins.tuple
writes internal: Config.CACHE_DIR, Config.CONFIG_DIR, Config.DATABASE_PATH, Config.DATA_PROC_DIR, Config.DATA_RAW_DIR, Config.ERGAST_BASE_URL, Config.FASTF1_CACHE_DIR, Config.FIGURES_DIR, Config.LOGS_DIR, Config.MAX_RETRIES, Config.OUTPUTS_DIR, Config.PROJECT_ROOT, Config.REQUEST_DELAY, Config.TEST_DATABASE_PATH, Config._config_data, Config._config_source
unresolved: 3 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 10 sites in 3 modules (src.data.collector, src.data.load_fastf1)
