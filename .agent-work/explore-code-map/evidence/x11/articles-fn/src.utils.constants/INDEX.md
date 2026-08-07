# src.utils.constants
src/utils/constants.py, 364 lines

Constants for F1Brainz.

This module centralizes all hardcoded values that were previously scattered
across the codebase, making them easier to maintain and update.

imports stdlib: typing.Dict, typing.List
imported by: src.data.collector, src.data.database._core, src.data.database._ingest, src.data.database._metadata_circuit, src.data.database._metadata_session, src.data.database._results, src.data.database._telemetry_store, src.data.load_fastf1, src.evo_predictor.data_adapter, src.evo_predictor.data_adapter._assemble, src.evo_predictor.data_adapter._build, src.evo_predictor.data_adapter._config, src.evo_predictor.data_adapter._helpers, src.evo_predictor.data_adapter._memory, src.evo_predictor.data_adapter._quality, src.evo_predictor.gold_cycle.runner, src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.models, src.evo_predictor.models._features, src.evo_predictor.models._genomes, src.evo_predictor.models._pack, src.evo_predictor.models._param_arrays, src.evo_predictor.module_adapters._common, src.evo_predictor.module_adapters._registry, src.evo_predictor.module_adapters._runtime_builders, src.evo_predictor.module_adapters._training_builders, src.evo_predictor.module_training_evidence_modes, src.evo_predictor.module_training_orchestration, src.evo_predictor.pipeline, src.evo_predictor.quali_power_adapter, src.evo_predictor.race_car_channel, src.evo_predictor.race_driver_channel, src.evo_predictor.race_form_channel, src.evo_predictor.recency_features, src.evo_predictor.recent_history_adapter, src.evo_predictor.sampled_backtest, src.evo_predictor.walkforward.pipeline, src.fantasy_scoring.league.attribution, src.fantasy_scoring.league.sqlite_classification, src.fantasy_scoring.scoring_rules, src.physics.fit_batch, src.physics.ideal_lap.residuals, src.physics.layer2.estimate_batch, src.physics.layer2.grip_batch, src.physics.wear.batch, src.utils.f1_calendar

```python
F1_CALENDARS: Dict[int, List[str]] = {2018: ['Australia', 'Bahrain', 'China', 'Azerbaijan', 'Spain', 'Monaco', 'Canada', 'Fr...
SPRINT_WEEKENDS: Dict[int, List[str]] = {2021: ['Great Britain', 'Italy', 'Brazil'], 2022: ['Emilia Romagna', 'Austria', 'Brazi...
SESSION_TYPES = ['FP1', 'FP2', 'FP3', 'Q', 'R', 'S', 'SQ']
PRACTICE_SESSIONS = ['FP1', 'FP2', 'FP3']
RACE_SESSIONS = ['R']
QUALIFYING_SESSIONS = ['Q']
SPRINT_SESSIONS = ['S', 'SQ']
SPRINT_WEEKEND_SESSIONS = ['FP1', 'SQ', 'S', 'Q', 'R']
LEGACY_SPRINT_WEEKEND_SESSIONS = ['FP1', 'Q', 'FP2', 'S', 'R']
NORMAL_WEEKEND_SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'R']
KNOWN_UNAVAILABLE_SESSIONS = {(2020, 'Emilia Romagna', 'FP2'): {'reason': 'Imola 2020 used a compressed COVID-era fo...
DNF_POSITION = 30
MAX_GRID_POSITIONS = 20
MIN_CLEAN_LAPS = 3
LONG_RUN_THRESHOLD = 3
MAX_LAP_TIME_SECONDS = 200
TELEMETRY_SAMPLING_RATE = 10
WEATHER_SAMPLING_RATE = 5
TIRE_COMPOUNDS = ['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET', 'HYPERSOFT', 'ULTRASOFT', 'SUPERSOFT'...
COMPOUND_COLORS = {'SOFT': '#FF0000', 'MEDIUM': '#FFFF00', 'HARD': '#FFFFFF', 'INTERMEDIATE': '#00FF00', ...
DEFAULT_DB_NAME = 'f1_data.db'
DEFAULT_DATA_DIR = 'data'
DB_TIMEOUT = 30.0
DB_CHECK_SAME_THREAD = False
FASTF1_RATE_LIMIT_DELAY = 40.0
FASTF1_RETRY_ATTEMPTS = 3
FASTF1_RETRY_DELAY = 2.0
FASTF1_RATE_LIMIT_BACKOFF = 60.0
FASTF1_CACHE_ENABLED = True
FASTF1_CACHE_MAX_AGE_DAYS = 30
MIN_TRACK_TEMP = -10.0
MAX_TRACK_TEMP = 70.0
MIN_AIR_TEMP = -20.0
MAX_AIR_TEMP = 50.0
MIN_HUMIDITY = 0.0
MAX_HUMIDITY = 100.0
MIN_SPEED = 0.0
MAX_SPEED = 400.0
MIN_RPM = 0.0
MAX_RPM = 20000.0
POSITION_SCORE_POWER = 1.0
RECENT_FORM_RACES = 3
RECENT_FORM_WEIGHTS = [0.5, 0.3, 0.2]
DEFAULT_TOP_K = 10
DEFAULT_RANDOM_SEED = 42
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = 'INFO'
LEGACY_SPRINT_YEARS: frozenset[int] = frozenset({2021})
SPRINT_PRACTICE_SESSIONS: List[str] = ['FP1', 'SQ', 'S']
LEGACY_SPRINT_PRACTICE_SESSIONS: List[str] = ['FP1', 'FP2']
NORMAL_PRACTICE_SESSIONS: List[str] = ['FP1', 'FP2', 'FP3']
```

- [get_calendar](get_calendar.md) function: Get F1 calendar for a specific year.
- [is_sprint_weekend](is_sprint_weekend.md) function: Check if a Grand Prix has a sprint format.
- [is_legacy_sprint_weekend](is_legacy_sprint_weekend.md) function: Sprint weekend using 2021 format: FP1+FP2 practice (no SQ/S sessions exist).
- [is_modern_sprint_weekend](is_modern_sprint_weekend.md) function: Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).
- [get_practice_session_types](get_practice_session_types.md) function: Return the ordered list of practice session types for a race weekend.
- [get_weekend_sessions](get_weekend_sessions.md) function: Get session types for a specific Grand Prix weekend.
- [validate_session_type](validate_session_type.md) function: Validate if session type is recognized.
