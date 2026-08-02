# Implementer Handoff (REWORK — attempt 2)

## Gate
g1-implement (rework)

## Task
Fix a simplification_limits BLOCKER from the g1 review: two test functions in `tests/unit/physics/layer2/test_grip_store.py` exceed the repo's cyclomatic-complexity limit (`<20`):
- `test_error_record_never_loses_a_failure`: CC=20
- `test_load_roundtrips_field_values`: CC=22

Verify yourself first: `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_store.py src/physics/layer2/grip_store.py` (note: plain `py` on this sandbox's PATH resolves to a broken shim missing scipy/fastf1 — always use this full WindowsApps path).

## Protected Intent
Do not weaken test coverage — the additive-migration and round-trip/error-record assertions must stay equally rigorous, just restructured so no single function's cyclomatic complexity exceeds the limit. `grip_store.py` itself already passes cleanly — do not touch it.

## Test Mode
Test-after — refactor existing tests, re-run to confirm still green + limits pass.

## Close Criteria
- `py -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_store.py src/physics/layer2/grip_store.py` exits 0 (no violations).
- `py -m pytest tests/unit/physics/layer2/test_grip_store.py -q` still shows the same or greater number of assertions passing (splitting a long flat assert sequence into a small helper function or a `@pytest.mark.parametrize` table is the natural fix — pick whichever reads most naturally for each function).
- No change to `src/physics/layer2/grip_store.py`.

## Allowed Scope
`tests/unit/physics/layer2/test_grip_store.py` only.

## Specific Exclusions
Do not touch `src/physics/layer2/grip_store.py` or any other file.

## Constraints
- Keep the additive-migration test's actual mechanism (hand-crafted legacy table + pre-existing row, migrate, confirm row survives + new columns present) — only restructure the ASSERTION shape, not the test's substance.

## Map Anchors (inbound)
Same as the original g1-implement handoff (`.agent-work/663-grip-g/crew-handoffs/g1-implement-handoff.md`) — this is a narrow rework, not a new design.

## Deliverable Path Check
- **Committed** — `tests/unit/physics/layer2/test_grip_store.py`; already tracked as untracked-new from attempt 1, still not gitignored.

## Required Evidence
- `simplification_limits` clean output (paste it).
- `pytest -q` full output (paste it), same coverage as before.

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_store.py src/physics/layer2/grip_store.py
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_store.py -q
```

## Suggested Model Tier
Simple bounded — narrow, mechanical refactor.

## Authority
This is a rework of a reviewer BLOCK — the fix scope above is already decided; do not redesign the store or its tests beyond this narrow complexity fix.

## Stop Conditions
Stop and return if the fix requires touching `grip_store.py` (it shouldn't) or reduces test coverage.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g1-implement-result.md`, overwriting the attempt-1 result, and return as your final message text): completed slice, evidence produced (paste both command outputs), assumptions used.
