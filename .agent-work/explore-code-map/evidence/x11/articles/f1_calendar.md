# `src.utils.f1_calendar`

> F1 calendar integration for race scheduling.
>
> Provides utilities for tracking upcoming races, race weekends, and scheduling
> automated predictions.

*(everything after the first line above is [s].)*

`src/utils/f1_calendar.py` · 390 lines [s] · 8 top-level, 19 entities total · 19 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `dataclasses.dataclass`, `datetime.datetime`, `logging`, `typing.Dict`, `typing.List`, `typing.Optional`
**Imports (third-party)**: `fastf1`

**Imports (internal)**: `src.utils.constants:F1_CALENDARS`, `src.utils.constants:SPRINT_WEEKENDS`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `logger` | — | `logging.getLogger(__name__)` | 17 | name only |
| `_calendar` | — | `None` | 356 | name only |

## Contents

- [`RaceInfo`](#raceinfo) — *class* — Information about an F1 race weekend.
- [`F1Calendar`](#f1calendar) — *class* — F1 calendar manager for race scheduling.
- [`get_calendar`](#get-calendar) — *function* — Get singleton calendar instance.
- [`get_upcoming_races`](#get-upcoming-races) — *function* — Get upcoming races. See F1Calendar.get_upcoming_races.
- [`get_next_race`](#get-next-race) — *function* — Get next race. See F1Calendar.get_next_race.
- [`get_race_by_number`](#get-race-by-number) — *function* — Get race by number. See F1Calendar.get_race_by_number.
- [`get_race_by_name`](#get-race-by-name) — *function* — Get race by name. See F1Calendar.get_race_by_name.
- [`is_race_weekend`](#is-race-weekend) — *function* — Check if it's a race weekend. See F1Calendar.is_race_weekend.

---

## `RaceInfo`
*class* [s] · [`src/utils/f1_calendar.py:21`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L21) · 13 lines [s]

```python
class RaceInfo
```
**Decorators** [s]: `@dataclass`

> Information about an F1 race weekend.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `season` | `int` | — | 23 | name only |
| `race_number` | `int` | — | 24 | name only |
| `gp_name` | `str` | — | 25 | name only |
| `circuit_name` | `str` | — | 26 | name only |
| `country` | `str` | — | 27 | name only |
| `race_date` | `datetime` | — | 28 | name only |
| `quali_date` | `Optional[datetime]` | — | 29 | name only |
| `fp1_date` | `Optional[datetime]` | — | 30 | name only |
| `fp2_date` | `Optional[datetime]` | — | 31 | name only |
| `fp3_date` | `Optional[datetime]` | — | 32 | name only |
| `is_sprint_weekend` | `bool` | — | 33 | name only |

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `datetime.datetime` x5, `typing.Optional` x4, `builtins.str` x3, `builtins.int` x2, `builtins.bool` |
| writes | internal | `RaceInfo.circuit_name`, `RaceInfo.country`, `RaceInfo.fp1_date`, `RaceInfo.fp2_date`, `RaceInfo.fp3_date`, `RaceInfo.gp_name`, `RaceInfo.is_sprint_weekend`, `RaceInfo.quali_date`, `RaceInfo.race_date`, `RaceInfo.race_number`, `RaceInfo.season` |

**Referenced by**: 15 site(s) across 1 module(s) (all within this module)


## `F1Calendar`
*class* [s] · [`src/utils/f1_calendar.py:36`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L36) · 317 lines [s]

```python
class F1Calendar
```

> F1 calendar manager for race scheduling.
>
> Uses FastF1 to get actual race dates and session times.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Members**

- [`F1Calendar.__init__`](#f1calendar--init--) — *method* — Initialize calendar manager.
- [`F1Calendar._naive_datetime`](#f1calendar-naive-datetime) — *static method* — Normalize timezone-aware datetimes for safe calendar comparison.
- [`F1Calendar.get_season_calendar`](#f1calendarget-season-calendar) — *method* — Get full calendar for a season.
- [`F1Calendar._get_fallback_calendar`](#f1calendar-get-fallback-calendar) — *method* — Fallback calendar when FastF1 unavailable.
- [`F1Calendar.get_race_by_number`](#f1calendarget-race-by-number) — *method* — Get race info by race number.
- [`F1Calendar.get_race_by_name`](#f1calendarget-race-by-name) — *method* — Get race info by GP name.
- [`F1Calendar.get_upcoming_races`](#f1calendarget-upcoming-races) — *method* — Get upcoming races within specified days.
- [`F1Calendar.get_next_race`](#f1calendarget-next-race) — *method* — Get the next race after reference date.
- [`F1Calendar.is_race_weekend`](#f1calendaris-race-weekend) — *method* — Check if date falls on a race weekend.
- [`F1Calendar.get_current_race_weekend`](#f1calendarget-current-race-weekend) — *method* — Get race info if currently on a race weekend.
- [`F1Calendar.format_race_info`](#f1calendarformat-race-info) — *method* — Format race info for display.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `RaceInfo` x8 |
| reads | stdlib | `builtins.int` x10, `typing.Optional` x8, `datetime.datetime` x6, `typing.List` x3, `builtins.bool` x2, `builtins.str` x2, `builtins.staticmethod` |

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


### `F1Calendar.__init__`
*method* [s] · [`src/utils/f1_calendar.py:43`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L43) · 3 lines [s]

**Signature** [s]

```python
def __init__(self)
```

> Initialize calendar manager.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `RaceInfo` |
| reads | stdlib | `builtins.int`, `typing.Dict`, `typing.List` |
| writes | internal | `F1Calendar._cache` |

*Not shown: 1 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar._naive_datetime`
*static method* [s] · [`src/utils/f1_calendar.py:48`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L48) · 5 lines [s]

**Signature** [s]

```python
def _naive_datetime(value: datetime) -> datetime
```

> Normalize timezone-aware datetimes for safe calendar comparison.

**Parameters**

- `value` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.hasattr` |

*Not shown: 4 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: 4 site(s) across 1 module(s) (all within this module)


### `F1Calendar.get_season_calendar`
*method* [s] · [`src/utils/f1_calendar.py:54`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L54) · 75 lines [s]

**Signature** [s]

```python
def get_season_calendar(self, season: int, force_refresh: bool = False) -> List[RaceInfo]
```

> Get full calendar for a season.
>
> Args:
>     season: Season year
>     force_refresh: Force reload even if cached
>
> Returns:
>     List of RaceInfo for all races in season

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `force_refresh` — force_refresh: Force reload even if cached [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar._get_fallback_calendar`, `RaceInfo` |
| calls | cross-module | `src.utils.constants:SPRINT_WEEKENDS.get` |
| calls | stdlib | `builtins.int`, `builtins.len` |
| calls | third-party | `fastf1.get_event_schedule` |
| reads | internal | `F1Calendar._cache` x3, `logger` x2 |
| reads | cross-module | `src.utils.constants:SPRINT_WEEKENDS` |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `fastf1 (module)` |
| writes | internal | `F1Calendar._cache[]` |

*Not shown: 37 local-variable reads, 17 local-variable writes; 14 reads of its own parameters.*

**Unresolved by the extractor**: 15 calls (dispatch-unknown-base)

**Referenced by**: 5 site(s) across 1 module(s) (all within this module)


### `F1Calendar._get_fallback_calendar`
*method* [s] · [`src/utils/f1_calendar.py:130`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L130) · 28 lines [s]

**Signature** [s]

```python
def _get_fallback_calendar(self, season: int) -> List[RaceInfo]
```

> Fallback calendar when FastF1 unavailable.
>
> Returns race info without dates.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `RaceInfo` |
| calls | cross-module | `src.utils.constants:F1_CALENDARS.get`, `src.utils.constants:SPRINT_WEEKENDS.get` |
| calls | stdlib | `builtins.enumerate` |
| reads | internal | `logger` |
| reads | cross-module | `src.utils.constants:F1_CALENDARS`, `src.utils.constants:SPRINT_WEEKENDS` |
| reads | stdlib | `datetime.datetime.min`, `datetime.datetime` |

*Not shown: 8 local-variable reads, 6 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `F1Calendar.get_race_by_number`
*method* [s] · [`src/utils/f1_calendar.py:159`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L159) · 16 lines [s]

**Signature** [s]

```python
def get_race_by_number(self, season: int, race_number: int) -> Optional[RaceInfo]
```

> Get race info by race number.
>
> Args:
>     season: Season year
>     race_number: Race number (1-indexed)
>
> Returns:
>     RaceInfo if found, None otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `race_number` — race_number: Race number (1-indexed) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_season_calendar` |

*Not shown: 3 local-variable reads, 2 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar.get_race_by_name`
*method* [s] · [`src/utils/f1_calendar.py:176`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L176) · 23 lines [s]

**Signature** [s]

```python
def get_race_by_name(self, season: int, gp_name: str) -> Optional[RaceInfo]
```

> Get race info by GP name.
>
> Args:
>     season: Season year
>     gp_name: Grand Prix name (e.g., "Monaco", "British")
>
> Returns:
>     RaceInfo if found, None otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `gp_name` — gp_name: Grand Prix name (e.g., "Monaco", "British") [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_season_calendar` |

*Not shown: 6 local-variable reads, 3 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar.get_upcoming_races`
*method* [s] · [`src/utils/f1_calendar.py:200`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L200) · 41 lines [s]

**Signature** [s]

```python
def get_upcoming_races(self, season: int, days_ahead: int = 7, reference_date: Optional[datetime] = None) -> List[RaceInfo]
```

> Get upcoming races within specified days.
>
> Args:
>     season: Season year
>     days_ahead: Number of days to look ahead
>     reference_date: Reference date (default: now)
>
> Returns:
>     List of RaceInfo for upcoming races

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `days_ahead` — days_ahead: Number of days to look ahead [a]
- `reference_date` — reference_date: Reference date (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_season_calendar` |
| calls | stdlib | `builtins.hasattr` x2, `builtins.sorted`, `datetime.datetime.now` |
| reads | stdlib | `datetime.datetime` x2, `datetime.datetime.min` |
| writes | internal | `F1Calendar.get_upcoming_races.reference_date` |

*Not shown: 15 local-variable reads, 8 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base), 1 reads (unbound-name)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `F1Calendar.get_next_race`
*method* [s] · [`src/utils/f1_calendar.py:242`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L242) · 17 lines [s]

**Signature** [s]

```python
def get_next_race(self, season: int, reference_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

> Get the next race after reference date.
>
> Args:
>     season: Season year
>     reference_date: Reference date (default: now)
>
> Returns:
>     Next RaceInfo or None if season is over

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `reference_date` — reference_date: Reference date (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar.get_upcoming_races` |

*Not shown: 2 local-variable reads, 1 local-variable writes; 3 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar.is_race_weekend`
*method* [s] · [`src/utils/f1_calendar.py:260`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L260) · 34 lines [s]

**Signature** [s]

```python
def is_race_weekend(self, season: int, check_date: Optional[datetime] = None) -> bool
```

> Check if date falls on a race weekend.
>
> Args:
>     season: Season year
>     check_date: Date to check (default: now)
>
> Returns:
>     True if it's a race weekend

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `check_date` — check_date: Date to check (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar._naive_datetime` x2, `F1Calendar.get_season_calendar` |
| calls | stdlib | `datetime.datetime.now` |
| reads | stdlib | `datetime.datetime` x2, `datetime.datetime.min` |
| writes | internal | `F1Calendar.is_race_weekend.check_date` |

*Not shown: 4 local-variable reads, 3 local-variable writes; 6 reads of its own parameters.*

**Unresolved by the extractor**: 3 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar.get_current_race_weekend`
*method* [s] · [`src/utils/f1_calendar.py:295`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L295) · 33 lines [s]

**Signature** [s]

```python
def get_current_race_weekend(self, season: int, check_date: Optional[datetime] = None) -> Optional[RaceInfo]
```

> Get race info if currently on a race weekend.
>
> Args:
>     season: Season year
>     check_date: Date to check (default: now)
>
> Returns:
>     RaceInfo if on race weekend, None otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `season` — season: Season year [a]
- `check_date` — check_date: Date to check (default: now) [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar._naive_datetime` x2, `F1Calendar.get_season_calendar` |
| calls | stdlib | `datetime.datetime.now` |
| reads | stdlib | `datetime.datetime` x2, `datetime.datetime.min` |
| writes | internal | `F1Calendar.get_current_race_weekend.check_date` |

*Not shown: 5 local-variable reads, 3 local-variable writes; 6 reads of its own parameters.*

**Unresolved by the extractor**: 3 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `F1Calendar.format_race_info`
*method* [s] · [`src/utils/f1_calendar.py:329`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L329) · 24 lines [s]

**Signature** [s]

```python
def format_race_info(self, race: RaceInfo) -> str
```

> Format race info for display.
>
> Args:
>     race: RaceInfo to format
>
> Returns:
>     Formatted string

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `race` — race: RaceInfo to format [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `RaceInfo.quali_date` x2, `RaceInfo.race_date` x2, `RaceInfo.circuit_name`, `RaceInfo.country`, `RaceInfo.gp_name`, `RaceInfo.is_sprint_weekend`, `RaceInfo.race_number`, `RaceInfo.season` |
| reads | stdlib | `datetime.datetime.min`, `datetime.datetime` |

*Not shown: 7 local-variable reads, 1 local-variable writes; 10 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (chained-attribute), 7 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `get_calendar`
*function* [s] · [`src/utils/f1_calendar.py:359`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L359) · 6 lines [s]

**Signature** [s]

```python
def get_calendar() -> F1Calendar
```

> Get singleton calendar instance.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `F1Calendar` |

*Not shown: 2 local-variable reads, 1 local-variable writes.*

**Referenced by**: 5 site(s) across 1 module(s) (all within this module)


## `get_upcoming_races`
*function* [s] · [`src/utils/f1_calendar.py:368`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L368) · 3 lines [s]

**Signature** [s]

```python
def get_upcoming_races(season: int, days_ahead: int = 7) -> List[RaceInfo]
```

> Get upcoming races. See F1Calendar.get_upcoming_races.

**Parameters**

- `season` — *[HOLE] undocumented parameter*
- `days_ahead` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `get_next_race`
*function* [s] · [`src/utils/f1_calendar.py:373`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L373) · 3 lines [s]

**Signature** [s]

```python
def get_next_race(season: int) -> Optional[RaceInfo]
```

> Get next race. See F1Calendar.get_next_race.

**Parameters**

- `season` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 1 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `get_race_by_number`
*function* [s] · [`src/utils/f1_calendar.py:378`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L378) · 3 lines [s]

**Signature** [s]

```python
def get_race_by_number(season: int, race_number: int) -> Optional[RaceInfo]
```

> Get race by number. See F1Calendar.get_race_by_number.

**Parameters**

- `season` — *[HOLE] undocumented parameter*
- `race_number` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `get_race_by_name`
*function* [s] · [`src/utils/f1_calendar.py:383`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L383) · 3 lines [s]

**Signature** [s]

```python
def get_race_by_name(season: int, gp_name: str) -> Optional[RaceInfo]
```

> Get race by name. See F1Calendar.get_race_by_name.

**Parameters**

- `season` — *[HOLE] undocumented parameter*
- `gp_name` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


## `is_race_weekend`
*function* [s] · [`src/utils/f1_calendar.py:388`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L388) · 3 lines [s]

**Signature** [s]

```python
def is_race_weekend(season: int) -> bool
```

> Check if it's a race weekend. See F1Calendar.is_race_weekend.

**Parameters**

- `season` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `get_calendar` |

*Not shown: 1 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
