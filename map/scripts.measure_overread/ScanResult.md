# scripts.measure_overread:ScanResult
class, scripts/measure_overread.py:133, 11 lines

```python
@dataclass(frozen=True)
class ScanResult
```

One transcript's (one agent run's) structural-read counts.

```python
transcript: Path
state_reads: int
engine_source_reads: int
skipped_lines: int
```

- [structural_reads](ScanResult.structural_reads.md) property: HOLE: no docstring

reads stdlib: builtins.int x4, builtins.property, pathlib.Path
writes internal: ScanResult.engine_source_reads, ScanResult.skipped_lines, ScanResult.state_reads, ScanResult.transcript

referenced by: 5 sites, this module only
