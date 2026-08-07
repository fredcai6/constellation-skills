[map index](../INDEX.md)

# `src.utils`

> Utility Functions Module
>
> This module provides utility functions and configuration management
> for the F1Brainz system.
>
> Key components:
>     - config: Configuration management with YAML validation
>     - constants: Centralized constants (calendars, thresholds, etc.)
>     - ids: Driver ID mapping between FastF1 and Ergast
>
> Example:
>     from src.utils.config import Config
>     from src.utils.constants import F1_CALENDARS
>
>     config = Config.load_config()
>     seasons = Config.get_seasons()
>     calendar = F1_CALENDARS[2024]

*(everything after the first line above is [s].)*

`src/utils/__init__.py` · 19 lines [s] · 0 entities · 0 documented, 0 **holes**

## Dependencies


**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Contents

*No classes or functions — module-level definitions only.*
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
