[map index](../INDEX.md)

# `src.utils.constants`

> Constants for F1Brainz.
>
> This module centralizes all hardcoded values that were previously scattered
> across the codebase, making them easier to maintain and update.

*(everything after the first line above is [s].)*

`src/utils/constants.py` · 364 lines [s] · 7 entities · 7 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `typing.Dict`, `typing.List`

**Imported by** (46 modules in the extraction window): `src.data.collector`, `src.data.database._core`, `src.data.database._ingest`, `src.data.database._metadata_circuit`, `src.data.database._metadata_session`, `src.data.database._results`, `src.data.database._telemetry_store`, `src.data.load_fastf1`, `src.evo_predictor.data_adapter`, `src.evo_predictor.data_adapter._assemble`, `src.evo_predictor.data_adapter._build`, `src.evo_predictor.data_adapter._config`, `src.evo_predictor.data_adapter._helpers`, `src.evo_predictor.data_adapter._memory`, `src.evo_predictor.data_adapter._quality`, `src.evo_predictor.gold_cycle.runner`, `src.evo_predictor.gold_cycle.runner_support`, `src.evo_predictor.models`, `src.evo_predictor.models._features`, `src.evo_predictor.models._genomes`, `src.evo_predictor.models._pack`, `src.evo_predictor.models._param_arrays`, `src.evo_predictor.module_adapters._common`, `src.evo_predictor.module_adapters._registry`, `src.evo_predictor.module_adapters._runtime_builders`, `src.evo_predictor.module_adapters._training_builders`, `src.evo_predictor.module_training_evidence_modes`, `src.evo_predictor.module_training_orchestration`, `src.evo_predictor.pipeline`, `src.evo_predictor.quali_power_adapter`, `src.evo_predictor.race_car_channel`, `src.evo_predictor.race_driver_channel`, `src.evo_predictor.race_form_channel`, `src.evo_predictor.recency_features`, `src.evo_predictor.recent_history_adapter`, `src.evo_predictor.sampled_backtest`, `src.evo_predictor.walkforward.pipeline`, `src.fantasy_scoring.league.attribution`, `src.fantasy_scoring.league.sqlite_classification`, `src.fantasy_scoring.scoring_rules`, `src.physics.fit_batch`, `src.physics.ideal_lap.residuals`, `src.physics.layer2.estimate_batch`, `src.physics.layer2.grip_batch`, `src.physics.wear.batch`, `src.utils.f1_calendar`

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `F1_CALENDARS` | `Dict[int, List[str]]` | `{2018: ['Australia', 'Bahrain', 'China', 'Azerbaijan', 'Spain', 'Mo...` | 14 | name only |
| `SPRINT_WEEKENDS` | `Dict[int, List[str]]` | `{2021: ['Great Britain', 'Italy', 'Brazil'], 2022: ['Emilia Romagna...` | 82 | name only |
| `SESSION_TYPES` | — | `['FP1', 'FP2', 'FP3', 'Q', 'R', 'S', 'SQ']` | 108 | name only |
| `PRACTICE_SESSIONS` | — | `['FP1', 'FP2', 'FP3']` | 109 | name only |
| `RACE_SESSIONS` | — | `['R']` | 110 | name only |
| `QUALIFYING_SESSIONS` | — | `['Q']` | 111 | name only |
| `SPRINT_SESSIONS` | — | `['S', 'SQ']` | 112 | name only |
| `SPRINT_WEEKEND_SESSIONS` | — | `['FP1', 'SQ', 'S', 'Q', 'R']` | 115 | name only |
| `LEGACY_SPRINT_WEEKEND_SESSIONS` | — | `['FP1', 'Q', 'FP2', 'S', 'R']` | 116 | name only |
| `NORMAL_WEEKEND_SESSIONS` | — | `['FP1', 'FP2', 'FP3', 'Q', 'R']` | 117 | name only |
| `KNOWN_UNAVAILABLE_SESSIONS` | — | `{(2020, 'Emilia Romagna', 'FP2'): {'reason': 'Imola 2020 used a com...` | 119 | name only |
| `DNF_POSITION` | — | `30` | 146 | name only |
| `MAX_GRID_POSITIONS` | — | `20` | 147 | name only |
| `MIN_CLEAN_LAPS` | — | `3` | 150 | name only |
| `LONG_RUN_THRESHOLD` | — | `3` | 151 | name only |
| `MAX_LAP_TIME_SECONDS` | — | `200` | 152 | name only |
| `TELEMETRY_SAMPLING_RATE` | — | `10` | 155 | name only |
| `WEATHER_SAMPLING_RATE` | — | `5` | 156 | name only |
| `TIRE_COMPOUNDS` | — | `['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET', 'HYPERSOFT', 'ULT...` | 163 | name only |
| `COMPOUND_COLORS` | — | `{'SOFT': '#FF0000', 'MEDIUM': '#FFFF00', 'HARD': '#FFFFFF', 'INTERM...` | 171 | name only |
| `DEFAULT_DB_NAME` | — | `'f1_data.db'` | 185 | name only |
| `DEFAULT_DATA_DIR` | — | `'data'` | 186 | name only |
| `DB_TIMEOUT` | — | `30.0` | 189 | name only |
| `DB_CHECK_SAME_THREAD` | — | `False` | 190 | name only |
| `FASTF1_RATE_LIMIT_DELAY` | — | `40.0` | 203 | name only |
| `FASTF1_RETRY_ATTEMPTS` | — | `3` | 204 | name only |
| `FASTF1_RETRY_DELAY` | — | `2.0` | 205 | name only |
| `FASTF1_RATE_LIMIT_BACKOFF` | — | `60.0` | 206 | name only |
| `FASTF1_CACHE_ENABLED` | — | `True` | 209 | name only |
| `FASTF1_CACHE_MAX_AGE_DAYS` | — | `30` | 210 | name only |
| `MIN_TRACK_TEMP` | — | `-10.0` | 218 | name only |
| `MAX_TRACK_TEMP` | — | `70.0` | 219 | name only |
| `MIN_AIR_TEMP` | — | `-20.0` | 220 | name only |
| `MAX_AIR_TEMP` | — | `50.0` | 221 | name only |
| `MIN_HUMIDITY` | — | `0.0` | 222 | name only |
| `MAX_HUMIDITY` | — | `100.0` | 223 | name only |
| `MIN_SPEED` | — | `0.0` | 226 | name only |
| `MAX_SPEED` | — | `400.0` | 227 | name only |
| `MIN_RPM` | — | `0.0` | 230 | name only |
| `MAX_RPM` | — | `20000.0` | 231 | name only |
| `POSITION_SCORE_POWER` | — | `1.0` | 239 | name only |
| `RECENT_FORM_RACES` | — | `3` | 242 | name only |
| `RECENT_FORM_WEIGHTS` | — | `[0.5, 0.3, 0.2]` | 243 | name only |
| `DEFAULT_TOP_K` | — | `10` | 246 | name only |
| `DEFAULT_RANDOM_SEED` | — | `42` | 247 | name only |
| `LOG_FORMAT` | — | `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'` | 254 | name only |
| `LOG_DATE_FORMAT` | — | `'%Y-%m-%d %H:%M:%S'` | 255 | name only |
| `DEFAULT_LOG_LEVEL` | — | `'INFO'` | 256 | name only |
| `LEGACY_SPRINT_YEARS` | `frozenset[int]` | `frozenset({2021})` | 295 | name only |
| `SPRINT_PRACTICE_SESSIONS` | `List[str]` | `['FP1', 'SQ', 'S']` | 297 | name only |
| `LEGACY_SPRINT_PRACTICE_SESSIONS` | `List[str]` | `['FP1', 'FP2']` | 298 | name only |
| `NORMAL_PRACTICE_SESSIONS` | `List[str]` | `['FP1', 'FP2', 'FP3']` | 299 | name only |

## Contents

- [`get_calendar`](get_calendar.md) — *function* [s] — Get F1 calendar for a specific year.
- [`is_sprint_weekend`](is_sprint_weekend.md) — *function* [s] — Check if a Grand Prix has a sprint format.
- [`is_legacy_sprint_weekend`](is_legacy_sprint_weekend.md) — *function* [s] — Sprint weekend using 2021 format: FP1+FP2 practice (no SQ/S sessions exist).
- [`is_modern_sprint_weekend`](is_modern_sprint_weekend.md) — *function* [s] — Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).
- [`get_practice_session_types`](get_practice_session_types.md) — *function* [s] — Return the ordered list of practice session types for a race weekend.
- [`get_weekend_sessions`](get_weekend_sessions.md) — *function* [s] — Get session types for a specific Grand Prix weekend.
- [`validate_session_type`](validate_session_type.md) — *function* [s] — Validate if session type is recognized.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
