# scripts.gauge_reader
scripts/gauge_reader.py, 380 lines

Gauge reader -- fail-safe read of the context-fullness gauge file.

Module 2 (read side) of the Context Governor (epic-178). A harness-specific
writer (issue #180) drops a small JSON record at
`.agent-work/<work_id>/gauge.json` on every tool call; the Trip policy (issue
#182) reads it at each gate through `read()` below. The file format is the
whole portability seam -- this reader never branches on which harness wrote
it, and it never raises: every failure mode (absent file, corrupt JSON,
malformed record, stale-by-`observed_at`, clock-skew) collapses to a single
`None`. A `Reading` that reaches the caller is fresh and well-formed by
construction, so a caller structurally cannot act on stale or bad data.

See the epic-178 DESIGN_SPEC ("2. Gauge") for the full rationale.

imports stdlib: __future__.annotations, dataclasses.dataclass, datetime.datetime, datetime.timedelta, datetime.timezone, json, pathlib.Path
imported by: none found

```python
REQUIRED_FIELDS = ('schema_version', 'fill_fraction', 'model', 'observed_at')
DEFAULT_MAX_AGE = timedelta(minutes=30)
CLOCK_SKEW_TOLERANCE = timedelta(minutes=2)
_PROFILES: dict[str, tuple[int, int, int]] = {'claude-opus-5': (1000000, 80000, 150000), 'claude-opus-4-8': (1000000, 80000, 150000)...
_DEFAULT_PROFILE: tuple[int, int, int] = (200000, 80000, 130000)
DEFAULT_THRESHOLDS: tuple[float, float] = (_DEFAULT_PROFILE[1] / _DEFAULT_PROFILE[0], _DEFAULT_PROFILE[2] / _DEFAULT_PROFILE[0])
UNCALIBRATED_FILENAME = 'gauge-uncalibrated.json'
SKIP_FILENAME = 'gauge-skip.json'
```

- [Reading](Reading.md) class: A fresh, well-formed gauge sample.
- [thresholds_for](thresholds_for.md) function: Return the (soft, hard) fill FRACTIONS for `model`.
- [_parse_observed_at](_parse_observed_at.md) function: Parse an `observed_at` value into a tz-aware datetime, or None if it
- [_parse_fields](_parse_fields.md) function: Validate an already-decoded record dict's required fields, types, and
- [_parse_record](_parse_record.md) function: Validate an already-decoded record dict and convert it to a Reading.
- [read](read.md) function: Read the gauge file at `path` and return a fresh Reading, or None.
- [raw_record](raw_record.md) function: The gauge file's own facts -- `fill_fraction`, `model`, `observed_at`
- [skip_reason](skip_reason.md) function: Why the writer hook wrote NO reading at this gauge path, if it knows --
- [uncalibrated_model](uncalibrated_model.md) function: The model name the writer could not calibrate, or None.
