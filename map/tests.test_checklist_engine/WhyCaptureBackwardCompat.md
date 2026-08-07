# tests.test_checklist_engine:WhyCaptureBackwardCompat
class, tests/test_checklist_engine.py:2984, 41 lines

```python
class WhyCaptureBackwardCompat(TestCase)
```

Pre-ruling: the new engine must drive existing-shape spines (NO `why_trail`

key, NO `why_exempt` on tasks) — missing why_exempt => not exempt; a why-less
advance REFUSES cleanly (never throws); why_trail is created on first write.

- [test_existing_shape_non_exempt_refused_then_passes_with_why](WhyCaptureBackwardCompat.test_existing_shape_non_exempt_refused_then_passes_with_why.md) method: HOLE: no docstring
- [test_existing_shape_exempt_task_advances_silently](WhyCaptureBackwardCompat.test_existing_shape_exempt_task_advances_silently.md) method: HOLE: no docstring
- [test_cli_legacy_spine_refuses_cleanly_never_crashes](WhyCaptureBackwardCompat.test_cli_legacy_spine_refuses_cleanly_never_crashes.md) method: HOLE: no docstring

referenced by: none found
