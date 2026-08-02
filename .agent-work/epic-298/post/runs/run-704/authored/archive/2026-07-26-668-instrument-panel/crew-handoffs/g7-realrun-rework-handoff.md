# Implementer Handoff — g7-realrun-implement (REWORK 1)

## Gate
g7-realrun-implement REWORK (#668 instrument panel). Worktree
`C:/Programs/f1brainz-wt/epic659-668`, branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Why reopened (the ONLY thing to fix)
The reviewer confirmed ALL substantive results correct, but the project-mandated gate
`py -m src.utils.simplification_limits` (CREW_CONTEXT.md names it a review blocker for new Python)
FAILS on `scripts/instrument_panel_668_report.py`:
- `instruments_2_3_replication` — cyclomatic complexity 26 (limit 20).
- `render_markdown` — complexity 20 + 125 lines (limit 100 lines).

## Task
Surgically REFACTOR `scripts/instrument_panel_668_report.py` to pass
`py -m src.utils.simplification_limits scripts/instrument_panel_668_report.py` — extract helper
functions to bring both functions under the complexity/length limits. **NO behavior change**: the
report `.md`/`.json` output must remain BYTE-IDENTICAL (the report is deterministic; verify with the
`--check-reproduce` path and by diffing the regenerated output against the committed one). Do not
touch any instrument module, any frozen value, or the report's numbers/content.

## Also fix (non-blocking observations the reviewer logged — do these too, cheaply)
- JSON key-order determinism: if the report `.json` has non-deterministic key order, sort keys on
  emit so re-runs are byte-stable (values already correct).
- Correct the result narrative about WHICH bug was fixed (a doc/narrative nit in the result file).

## Allowed Scope
`scripts/instrument_panel_668_report.py` (refactor only), the report outputs it regenerates
(`docs/physics/instrument_panel_668_gb2023q_report.md` + `.json` — only if byte-content is unchanged
or only key-order stabilized), and `tests/unit/physics/instrument_panel/test_panel_report.py` (only
if a test needs a trivial update for extracted helper names — prefer not touching it).

## Specific Exclusions
- Do NOT change any instrument module, any frozen value, any report NUMBER. Do NOT read/commit
  `data/f1_data_*.db`. Do NOT touch `docs/architecture/*`. No FastF1 online.
- Keep the editable-.pth `_REPO_ROOT` sys.path fix at the top of the script.

## Constraints
- `py -m src.utils.simplification_limits scripts/instrument_panel_668_report.py` must PASS (strict).
- Report output byte-identical (or JSON key-order-only change). pyright-0. Full
  `tests/unit/physics/instrument_panel/` suite green. `git status --porcelain data/` clean at end.

## Required Evidence
- LOAD-BEARING: `py -m src.utils.simplification_limits scripts/instrument_panel_668_report.py` output
  showing PASS (both functions under limits).
- LOAD-BEARING: report reproduces byte-identically (diff the regenerated .md against committed = empty,
  modulo the JSON key-order stabilization).
- LOAD-BEARING: pyright-0; full instrument_panel suite green; `git status --porcelain data/` clean.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits scripts/instrument_panel_668_report.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/instrument_panel_668_report.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/ -q
git status --porcelain data/
```

## Suggested Model Tier
simple-bounded — pure refactor to satisfy a complexity gate, output frozen.

## Authority
Refactor-only. Do NOT change any number, frozen value, or instrument logic. STOP and return if the
refactor cannot preserve byte-identical output.

## Stop Conditions
Stop and return if: the limits gate can't pass without a behavior change, or output can't stay identical.

## Return Format
Return IMPLEMENTER_RESULT (the refactor, the limits-gate PASS output, reproduce proof, evidence). WRITE
it to `.agent-work/668-instrument-panel/crew-results/g7-realrun-implement-result.md` (overwrite) before
ending your turn.
