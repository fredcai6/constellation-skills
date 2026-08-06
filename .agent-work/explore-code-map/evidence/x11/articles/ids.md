# `src.utils.ids`

> Driver ID Mapping Utility
>
> This module handles mapping between FastF1 and Ergast driver identifiers,
> including manual overrides for edge cases and name mismatches.

*(everything after the first line above is [s].)*

`src/utils/ids.py` · 325 lines [s] · 1 top-level, 10 entities total · 10 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `logging`, `typing.Dict`, `typing.List`, `typing.Optional`
**Imports (third-party)**: `pandas`, `yaml`

**Imported by**: no importer inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, so this is *not* evidence the module is unused).

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `logger` | — | `logging.getLogger(__name__)` | 14 | name only |

## Contents

- [`DriverMapper`](#drivermapper) — *class* — Maps driver identifiers between FastF1 and Ergast systems

---

## `DriverMapper`
*class* [s] · [`src/utils/ids.py:16`](C:/Programs/f1Brainz/src/utils/ids.py#L16) · 310 lines [s]

```python
class DriverMapper
```

> Maps driver identifiers between FastF1 and Ergast systems
>
> Handles:
> - FastF1 DriverNumber/Abbreviation ↔ Ergast driverId/code
> - Manual override mappings for edge cases
> - Driver aliases and name variations

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Members**

- [`DriverMapper.__init__`](#drivermapper--init--) — *method* — Initialize driver mapper
- [`DriverMapper._load_manual_mappings`](#drivermapper-load-manual-mappings) — *method* — Load manual override mappings from YAML file
- [`DriverMapper.map_driver_code`](#drivermappermap-driver-code) — *method* — Map driver code between systems
- [`DriverMapper.map_driver_name`](#drivermappermap-driver-name) — *method* — Map driver name to standard format
- [`DriverMapper.create_mapping_table`](#drivermappercreate-mapping-table) — *method* — Create a comprehensive mapping table between FastF1 and Ergast drivers
- [`DriverMapper.get_driver_consistency_score`](#drivermapperget-driver-consistency-score) — *method* — Calculate consistency score between FastF1 and Ergast driver data
- [`DriverMapper.suggest_mappings`](#drivermappersuggest-mappings) — *method* — Suggest potential driver mappings based on name similarity
- [`DriverMapper.export_mappings`](#drivermapperexport-mappings) — *method* — Export driver mappings to a file
- [`DriverMapper.validate_mapping`](#drivermappervalidate-mapping) — *method* — Validate if a driver mapping is correct

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.str` x17, `typing.Dict` x4, `typing.Optional` x3, `builtins.bool`, `builtins.float`, `typing.List` |
| reads | third-party | `pandas (module)` x9, `pandas.DataFrame` x9 |

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper.__init__`
*method* [s] · [`src/utils/ids.py:26`](C:/Programs/f1Brainz/src/utils/ids.py#L26) · 34 lines [s]

**Signature** [s]

```python
def __init__(self, override_file: Optional[str] = None)
```

> Initialize driver mapper
>
> Args:
>     override_file: Path to YAML file with manual override mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `override_file` — override_file: Path to YAML file with manual override mappings [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper._load_manual_mappings` |
| writes | internal | `DriverMapper.driver_aliases`, `DriverMapper.manual_mappings`, `DriverMapper.override_file` |

*Not shown: 5 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper._load_manual_mappings`
*method* [s] · [`src/utils/ids.py:61`](C:/Programs/f1Brainz/src/utils/ids.py#L61) · 15 lines [s]

**Signature** [s]

```python
def _load_manual_mappings(self) -> Dict[str, Dict[str, str]]
```

> Load manual override mappings from YAML file

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.isinstance`, `builtins.len`, `builtins.open` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `DriverMapper.override_file` x2, `logger` x2 |
| reads | stdlib | `builtins.Exception`, `builtins.dict` |
| reads | third-party | `yaml (module)` |

*Not shown: 6 local-variable reads, 2 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `DriverMapper.map_driver_code`
*method* [s] · [`src/utils/ids.py:77`](C:/Programs/f1Brainz/src/utils/ids.py#L77) · 25 lines [s]

**Signature** [s]

```python
def map_driver_code(self, driver_code: str, source: str = 'fastf1') -> Optional[str]
```

> Map driver code between systems
>
> Args:
>     driver_code: Driver code to map
>     source: Source system ('fastf1' or 'ergast')
>
> Returns:
>     Mapped driver code or None if no mapping found

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `driver_code` — driver_code: Driver code to map [a]
- `source` — source: Source system ('fastf1' or 'ergast') [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.manual_mappings` x3, `DriverMapper.driver_aliases` x2 |

*Not shown: 14 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper.map_driver_name`
*method* [s] · [`src/utils/ids.py:103`](C:/Programs/f1Brainz/src/utils/ids.py#L103) · 25 lines [s]

**Signature** [s]

```python
def map_driver_name(self, first_name: str, last_name: str, source: str = 'fastf1') -> Optional[str]
```

> Map driver name to standard format
>
> Args:
>     first_name: Driver's first name
>     last_name: Driver's last name
>     source: Source system
>
> Returns:
>     Standardized driver name or None if no mapping found

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `first_name` — first_name: Driver's first name [a]
- `last_name` — last_name: Driver's last name [a]
- `source` — source: Source system [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.driver_aliases` |

*Not shown: 4 local-variable reads, 3 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper.create_mapping_table`
*method* [s] · [`src/utils/ids.py:129`](C:/Programs/f1Brainz/src/utils/ids.py#L129) · 59 lines [s]

**Signature** [s]

```python
def create_mapping_table(self, fastf1_drivers: pd.DataFrame, ergast_drivers: pd.DataFrame) -> pd.DataFrame
```

> Create a comprehensive mapping table between FastF1 and Ergast drivers
>
> Args:
>     fastf1_drivers: DataFrame with FastF1 driver data
>     ergast_drivers: DataFrame with Ergast driver data
>
> Returns:
>     DataFrame with driver mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_drivers` — fastf1_drivers: DataFrame with FastF1 driver data [a]
- `ergast_drivers` — ergast_drivers: DataFrame with Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.len` |
| calls | third-party | `pandas.DataFrame` x2 |
| reads | internal | `logger` x2 |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `pandas (module)` x2 |

*Not shown: 21 local-variable reads, 11 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 11 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


### `DriverMapper.get_driver_consistency_score`
*method* [s] · [`src/utils/ids.py:189`](C:/Programs/f1Brainz/src/utils/ids.py#L189) · 33 lines [s]

**Signature** [s]

```python
def get_driver_consistency_score(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> Dict[str, float]
```

> Calculate consistency score between FastF1 and Ergast driver data
>
> Args:
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data
>
> Returns:
>     Dictionary with consistency metrics

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table` |
| calls | stdlib | `builtins.len` x2 |
| reads | internal | `logger` |
| reads | stdlib | `builtins.Exception` |

*Not shown: 13 local-variable reads, 4 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper.suggest_mappings`
*method* [s] · [`src/utils/ids.py:223`](C:/Programs/f1Brainz/src/utils/ids.py#L223) · 50 lines [s]

**Signature** [s]

```python
def suggest_mappings(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> List[Dict[str, str]]
```

> Suggest potential driver mappings based on name similarity
>
> Args:
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data
>
> Returns:
>     List of suggested mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table` |
| calls | stdlib | `builtins.len` |
| reads | internal | `logger` x2 |
| reads | stdlib | `builtins.Exception` |

*Not shown: 21 local-variable reads, 11 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 14 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


### `DriverMapper.export_mappings`
*method* [s] · [`src/utils/ids.py:274`](C:/Programs/f1Brainz/src/utils/ids.py#L274) · 28 lines [s]

**Signature** [s]

```python
def export_mappings(self, output_file: str, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame)
```

> Export driver mappings to a file
>
> Args:
>     output_file: Output file path
>     fastf1_data: FastF1 driver data
>     ergast_data: Ergast driver data

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `output_file` — output_file: Output file path [a]
- `fastf1_data` — fastf1_data: FastF1 driver data [a]
- `ergast_data` — ergast_data: Ergast driver data [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper.create_mapping_table`, `DriverMapper.suggest_mappings` |
| calls | third-party | `pandas.DataFrame` |
| reads | internal | `logger` x3 |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `pandas (module)` |

*Not shown: 7 local-variable reads, 4 local-variable writes; 9 reads of its own parameters.*

**Unresolved by the extractor**: 6 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


### `DriverMapper.validate_mapping`
*method* [s] · [`src/utils/ids.py:303`](C:/Programs/f1Brainz/src/utils/ids.py#L303) · 23 lines [s]

**Signature** [s]

```python
def validate_mapping(self, fastf1_code: str, ergast_code: str) -> bool
```

> Validate if a driver mapping is correct
>
> Args:
>     fastf1_code: FastF1 driver code
>     ergast_code: Ergast driver code
>
> Returns:
>     True if mapping is valid, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `fastf1_code` — fastf1_code: FastF1 driver code [a]
- `ergast_code` — ergast_code: Ergast driver code [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `DriverMapper.manual_mappings` x3, `DriverMapper.driver_aliases` x2 |

*Not shown: 13 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
