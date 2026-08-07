# tests.test_to_issues
tests/test_to_issues.py, 268 lines, 25 holes

Tests for the constellation-to-issues cut-work skill's scripts.

Covers the refuse-malformed RAIL (scripts/verify_issue_set.py) and the
ports-and-adapters FILER (scripts/file_issue_set.py):

  * RailTests        -- the four locked refusal rules + the well-formed pass.
  * FilerTests       -- markdown adapter files offline; the rail blocks a
                        malformed set from ever being filed.
  * IdempotencyTests -- crash-injection at before-file / after-file-before-
                        receipt / after-receipt; each re-run yields NO dupe epic.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CONFIRMED_SPEC = '# Design Spec — toy\n\n## Confirmation\n\n- **Status: CONFIRMED**\n- Confirmed by: fre...
UNCONFIRMED_SPEC = '# Design Spec — toy\n\n## Confirmation\n\n- **Status: DRAFT**\n- Confirmed by:\n- Date...
```

- [load](load.md) function: HOLE: no docstring
- [well_formed_manifest](well_formed_manifest.md) function: A minimal well-formed issue set: two issues, one dependency edge, both
- [_write](_write.md) function: HOLE: no docstring
- [RailTests](RailTests.md) class: HOLE: no docstring
  - [RailTests.setUp](RailTests.setUp.md) method: HOLE: no docstring
  - [RailTests.test_unconfirmed_spec_refused](RailTests.test_unconfirmed_spec_refused.md) method: HOLE: no docstring
  - [RailTests.test_missing_dependency_edge_refused](RailTests.test_missing_dependency_edge_refused.md) method: HOLE: no docstring
  - [RailTests.test_untyped_issue_refused](RailTests.test_untyped_issue_refused.md) method: HOLE: no docstring
  - [RailTests.test_bad_type_value_refused](RailTests.test_bad_type_value_refused.md) method: HOLE: no docstring
  - [RailTests.test_hitl_without_reason_refused](RailTests.test_hitl_without_reason_refused.md) method: HOLE: no docstring
  - [RailTests.test_dangling_edge_refused](RailTests.test_dangling_edge_refused.md) method: HOLE: no docstring
  - [RailTests.test_well_formed_set_passes](RailTests.test_well_formed_set_passes.md) method: HOLE: no docstring
  - [RailTests.test_cli_refuses_unconfirmed_nonzero](RailTests.test_cli_refuses_unconfirmed_nonzero.md) method: HOLE: no docstring
  - [RailTests.test_cli_accepts_well_formed_zero](RailTests.test_cli_accepts_well_formed_zero.md) method: HOLE: no docstring
- [FilerTests](FilerTests.md) class: HOLE: no docstring
  - [FilerTests.setUp](FilerTests.setUp.md) method: HOLE: no docstring
  - [FilerTests._adapter](FilerTests._adapter.md) method: HOLE: no docstring
  - [FilerTests.test_markdown_files_offline](FilerTests.test_markdown_files_offline.md) method: HOLE: no docstring
  - [FilerTests.test_epic_body_is_wave_ordered](FilerTests.test_epic_body_is_wave_ordered.md) method: HOLE: no docstring
  - [FilerTests.test_rail_blocks_malformed_filing](FilerTests.test_rail_blocks_malformed_filing.md) method: HOLE: no docstring
  - [FilerTests.test_unconfirmed_spec_blocks_filing](FilerTests.test_unconfirmed_spec_blocks_filing.md) method: HOLE: no docstring
- [IdempotencyTests](IdempotencyTests.md) class: Crash-injection at the three named points (DESIGN_SPEC TF7). Each: crash
  - [IdempotencyTests.setUp](IdempotencyTests.setUp.md) method: HOLE: no docstring
  - [IdempotencyTests._run_with_crash_then_complete](IdempotencyTests._run_with_crash_then_complete.md) method: HOLE: no docstring
  - [IdempotencyTests.test_crash_before_file](IdempotencyTests.test_crash_before_file.md) method: HOLE: no docstring
  - [IdempotencyTests.test_crash_after_file_before_receipt](IdempotencyTests.test_crash_after_file_before_receipt.md) method: HOLE: no docstring
  - [IdempotencyTests.test_crash_after_receipt](IdempotencyTests.test_crash_after_receipt.md) method: HOLE: no docstring
