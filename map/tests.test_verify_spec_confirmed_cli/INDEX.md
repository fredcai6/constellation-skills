# tests.test_verify_spec_confirmed_cli
tests/test_verify_spec_confirmed_cli.py, 108 lines, 6 holes

CLI-level regression coverage for verify_spec_confirmed.py's confirm-gate refusal.

tests/test_verify_spec_confirmed.py already exercises verify_spec_confirmed() as a direct
function call for these same three cases. This module is the adversarial-fixture half named
by issue #303 (epic-298 element E): it invokes the script as an actual subprocess and asserts
on the real process exit code and stderr, so the refusal is proven at the interface a human or
another tool would actually observe -- "the gate refuses" stays proven at the CLI boundary, not
just at the internal function boundary.

Fixture text is embedded inline (not a fixture file on disk) so this test has no dependency on
any file under the gitignored .agent-work/ tree.

imports stdlib: pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'verify_spec_confirmed.py'
FULL_TABLE = '\n| ID | Lens(es) | Sev | Finding | Disposition | Reason |\n|---|---|---|---|---|---|\...
CASE1_PARTIAL_CONFIRMATION = f'# Throwaway CLI fixture -- case 1: partially-filled Confirmation block\n\n## Confirma...
CASE2_EMPTY_DISPOSITION = '# Throwaway CLI fixture -- case 2: empty Disposition cell\n\n## Confirmation\n\n- **St...
CASE3_DELETED_MARKER_DRAFT = f'# Throwaway CLI fixture -- case 3: deleted marker, Status still DRAFT\n\n## Confirmat...
```

- [_run_cli](_run_cli.md) function: HOLE: no docstring
- [VerifySpecConfirmedCliRefusalTests](VerifySpecConfirmedCliRefusalTests.md) class: Each case: the real subprocess must exit non-zero and name the reason.
  - [VerifySpecConfirmedCliRefusalTests.setUp](VerifySpecConfirmedCliRefusalTests.setUp.md) method: HOLE: no docstring
  - [VerifySpecConfirmedCliRefusalTests.tearDown](VerifySpecConfirmedCliRefusalTests.tearDown.md) method: HOLE: no docstring
  - [VerifySpecConfirmedCliRefusalTests.test_case1_partial_confirmation_block_refuses](VerifySpecConfirmedCliRefusalTests.test_case1_partial_confirmation_block_refuses.md) method: HOLE: no docstring
  - [VerifySpecConfirmedCliRefusalTests.test_case2_empty_disposition_cell_refuses](VerifySpecConfirmedCliRefusalTests.test_case2_empty_disposition_cell_refuses.md) method: HOLE: no docstring
  - [VerifySpecConfirmedCliRefusalTests.test_case3_deleted_marker_draft_status_refuses](VerifySpecConfirmedCliRefusalTests.test_case3_deleted_marker_draft_status_refuses.md) method: HOLE: no docstring
