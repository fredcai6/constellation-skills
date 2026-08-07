[map index](../INDEX.md)

# `src.utils.f1_calendar`

> F1 calendar integration for race scheduling.
>
> Provides utilities for tracking upcoming races, race weekends, and scheduling
> automated predictions.

*(everything after the first line above is [s].)*

`src/utils/f1_calendar.py` · 390 lines [s] · 19 entities · 19 documented, 0 **holes**

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

- [`RaceInfo`](RaceInfo.md) — *class* [s] — Information about an F1 race weekend.
- [`F1Calendar`](F1Calendar.md) — *class* [s] — F1 calendar manager for race scheduling.
  - [`F1Calendar.__init__`](F1Calendar.__init__.md) — *method* [s] — Initialize calendar manager.
  - [`F1Calendar._naive_datetime`](F1Calendar._naive_datetime.md) — *static method* [s] — Normalize timezone-aware datetimes for safe calendar comparison.
  - [`F1Calendar.get_season_calendar`](F1Calendar.get_season_calendar.md) — *method* [s] — Get full calendar for a season.
  - [`F1Calendar._get_fallback_calendar`](F1Calendar._get_fallback_calendar.md) — *method* [s] — Fallback calendar when FastF1 unavailable.
  - [`F1Calendar.get_race_by_number`](F1Calendar.get_race_by_number.md) — *method* [s] — Get race info by race number.
  - [`F1Calendar.get_race_by_name`](F1Calendar.get_race_by_name.md) — *method* [s] — Get race info by GP name.
  - [`F1Calendar.get_upcoming_races`](F1Calendar.get_upcoming_races.md) — *method* [s] — Get upcoming races within specified days.
  - [`F1Calendar.get_next_race`](F1Calendar.get_next_race.md) — *method* [s] — Get the next race after reference date.
  - [`F1Calendar.is_race_weekend`](F1Calendar.is_race_weekend.md) — *method* [s] — Check if date falls on a race weekend.
  - [`F1Calendar.get_current_race_weekend`](F1Calendar.get_current_race_weekend.md) — *method* [s] — Get race info if currently on a race weekend.
  - [`F1Calendar.format_race_info`](F1Calendar.format_race_info.md) — *method* [s] — Format race info for display.
- [`get_calendar`](get_calendar.md) — *function* [s] — Get singleton calendar instance.
- [`get_upcoming_races`](get_upcoming_races.md) — *function* [s] — Get upcoming races. See F1Calendar.get_upcoming_races.
- [`get_next_race`](get_next_race.md) — *function* [s] — Get next race. See F1Calendar.get_next_race.
- [`get_race_by_number`](get_race_by_number.md) — *function* [s] — Get race by number. See F1Calendar.get_race_by_number.
- [`get_race_by_name`](get_race_by_name.md) — *function* [s] — Get race by name. See F1Calendar.get_race_by_name.
- [`is_race_weekend`](is_race_weekend.md) — *function* [s] — Check if it's a race weekend. See F1Calendar.is_race_weekend.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
