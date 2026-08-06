# `src.utils.constants`

> Constants for F1Brainz.
>
> This module centralizes all hardcoded values that were previously scattered
> across the codebase, making them easier to maintain and update.

*(everything after the first line above is [s].)*

`src/utils/constants.py` · 364 lines [s] · 7 top-level, 7 entities total · 7 documented, 0 **holes**

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

- [`get_calendar`](#get-calendar) — *function* — Get F1 calendar for a specific year.
- [`is_sprint_weekend`](#is-sprint-weekend) — *function* — Check if a Grand Prix has a sprint format.
- [`is_legacy_sprint_weekend`](#is-legacy-sprint-weekend) — *function* — Sprint weekend using 2021 format: FP1+FP2 practice (no SQ/S sessions exist).
- [`is_modern_sprint_weekend`](#is-modern-sprint-weekend) — *function* — Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).
- [`get_practice_session_types`](#get-practice-session-types) — *function* — Return the ordered list of practice session types for a race weekend.
- [`get_weekend_sessions`](#get-weekend-sessions) — *function* — Get session types for a specific Grand Prix weekend.
- [`validate_session_type`](#validate-session-type) — *function* — Validate if session type is recognized.

---

## `get_calendar`
*function* [s] · [`src/utils/constants.py:263`](C:/Programs/f1Brainz/src/utils/constants.py#L263) · 16 lines [s]

**Signature** [s]

```python
def get_calendar(year: int) -> List[str]
```

> Get F1 calendar for a specific year.
>
> Args:
>     year: Season year
>
> Returns:
>     List of GP names in calendar order
>
> Raises:
>     KeyError: If year is not in calendars

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.KeyError`, `builtins.list` |
| reads | internal | `F1_CALENDARS` x3 |

*Not shown: 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 20 site(s) across 14 module(s) — src.evo_predictor.module_training_orchestration x3, src.evo_predictor.pipeline x3, src.data.collector x2, src.evo_predictor.recency_features x2, src.evo_predictor.data_adapter._build, src.evo_predictor.data_adapter._helpers, src.evo_predictor.data_adapter._memory, src.evo_predictor.module_training_evidence_modes, src.evo_predictor.sampled_backtest, src.physics.fit_batch, src.physics.ideal_lap.residuals, src.physics.layer2.estimate_batch, src.physics.layer2.grip_batch, src.physics.wear.batch


## `is_sprint_weekend`
*function* [s] · [`src/utils/constants.py:281`](C:/Programs/f1Brainz/src/utils/constants.py#L281) · 12 lines [s]

**Signature** [s]

```python
def is_sprint_weekend(year: int, gp_name: str) -> bool
```

> Check if a Grand Prix has a sprint format.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     True if sprint weekend, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `SPRINT_WEEKENDS` x2 |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 4 site(s) across 1 module(s) (all within this module)


## `is_legacy_sprint_weekend`
*function* [s] · [`src/utils/constants.py:302`](C:/Programs/f1Brainz/src/utils/constants.py#L302) · 3 lines [s]

**Signature** [s]

```python
def is_legacy_sprint_weekend(year: int, gp_name: str) -> bool
```

> Sprint weekend using 2021 format: FP1+FP2 practice (no SQ/S sessions exist).

**Parameters**

- `year` — *[HOLE] undocumented parameter*
- `gp_name` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| reads | internal | `LEGACY_SPRINT_YEARS` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.evo_predictor.module_training_evidence_modes


## `is_modern_sprint_weekend`
*function* [s] · [`src/utils/constants.py:307`](C:/Programs/f1Brainz/src/utils/constants.py#L307) · 3 lines [s]

**Signature** [s]

```python
def is_modern_sprint_weekend(year: int, gp_name: str) -> bool
```

> Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).

**Parameters**

- `year` — *[HOLE] undocumented parameter*
- `gp_name` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| reads | internal | `LEGACY_SPRINT_YEARS` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.evo_predictor.module_training_evidence_modes


## `get_practice_session_types`
*function* [s] · [`src/utils/constants.py:312`](C:/Programs/f1Brainz/src/utils/constants.py#L312) · 22 lines [s]

**Signature** [s]

```python
def get_practice_session_types(year: int, gp_name: str) -> List[str]
```

> Return the ordered list of practice session types for a race weekend.
>
> Modern sprint weekends (2022+) use FP1 + sprint qualifying (SQ) + sprint race (S).
> Legacy sprint weekends (2021) used FP1 + FP2 — SQ/S session codes did not exist yet.
> Normal weekends use FP1 + FP2 + FP3.
> Q and R are never included — this is the canonical source for practice-only
> session pools used by feature builders and session dropout.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     List of practice session type strings, e.g. ["FP1", "FP2", "FP3"]

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| calls | stdlib | `builtins.list` x3 |
| reads | internal | `LEGACY_SPRINT_PRACTICE_SESSIONS`, `LEGACY_SPRINT_YEARS`, `NORMAL_PRACTICE_SESSIONS`, `SPRINT_PRACTICE_SESSIONS` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 2 site(s) across 2 module(s) — src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.module_training_orchestration


## `get_weekend_sessions`
*function* [s] · [`src/utils/constants.py:336`](C:/Programs/f1Brainz/src/utils/constants.py#L336) · 16 lines [s]

**Signature** [s]

```python
def get_weekend_sessions(year: int, gp_name: str) -> List[str]
```

> Get session types for a specific Grand Prix weekend.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     List of session types for that weekend

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| reads | internal | `LEGACY_SPRINT_WEEKEND_SESSIONS`, `LEGACY_SPRINT_YEARS`, `NORMAL_WEEKEND_SESSIONS`, `SPRINT_WEEKEND_SESSIONS` |

*Not shown: 3 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) — src.data.collector


## `validate_session_type`
*function* [s] · [`src/utils/constants.py:354`](C:/Programs/f1Brainz/src/utils/constants.py#L354) · 11 lines [s]

**Signature** [s]

```python
def validate_session_type(session_type: str) -> bool
```

> Validate if session type is recognized.
>
> Args:
>     session_type: Session type string
>
> Returns:
>     True if valid, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `session_type` — session_type: Session type string [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `SESSION_TYPES` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
