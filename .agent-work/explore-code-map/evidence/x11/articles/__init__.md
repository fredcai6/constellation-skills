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

`src/utils/__init__.py` · 19 lines [s] · 0 top-level, 0 entities total · 0 documented, 0 **holes**

## Dependencies


**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Contents

*No classes or functions — module-level definitions only.*

---

---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
