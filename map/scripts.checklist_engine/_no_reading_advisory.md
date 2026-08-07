# scripts.checklist_engine:_no_reading_advisory
function, scripts/checklist_engine.py:1333, 25 lines

```python
def _no_reading_advisory(base_dir: Path | None) -> str
```

Dispatch across every localizable "why is there no reading" cause, in

order, returning the FIRST non-empty result — exactly one signal reaches
the caller even when more than one sidecar happens to exist at a path:

1. `_uncalibrated_advisory` (#252) — completely unchanged, called exactly
   as before this gate. A STANDING defect (true until a human edits a
   code table), so it takes priority over the two newer, TRANSIENT causes
   below.
2. `_skip_reason_advisory` (#271) — the writer hook positively localized
   WHY it skipped this exact path (ambiguous binding / no usable record).
3. `_stale_record_advisory` (#271) — last resort: `read()` itself rejected
   the file at this path, so report its raw last-known facts rather than
   staying silent about a frozen number.

Each branch already fails safe to "" on its own (see their docstrings);
this dispatcher adds no new failure surface.

calls internal: _gauge_path, _skip_reason_advisory, _stale_record_advisory, _uncalibrated_advisory

referenced by: 1 sites, this module only
