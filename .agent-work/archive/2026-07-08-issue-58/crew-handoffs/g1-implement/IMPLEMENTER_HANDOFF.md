# Implementer Handoff

## Gate
g1 — Enforcement scripts + spine resolution (issue-58)

## Task
Build the mechanical enforcement layer for the constellation-explorer skill (spec: `.agent-work/issue-58/DESIGN_SPEC.md`, CONFIRMED — read sections "Headline doctrine 3", the Spine table rows explore/review/confirm, "Scripts bundled", "Install and test integration", "Testing pathways" 1–2):

1. **`scripts/verify_cycles.py`** — verifies exploration cycles in a work area. Args: work-id (like the other verify_* scripts in scripts/; follow their CLI conventions, e.g. `verify_agent_feedback.py`). PASS (exit 0) iff ≥1 `cycle-*.json` file exists in `.agent-work/<work-id>/` AND every such file is a survey with a non-null `consolidation` block. FAIL (nonzero, printed reason) on: zero cycle files, unparseable JSON, or any cycle with `consolidation: null`.
2. **`scripts/verify_spec_confirmed.py`** — verifies a design spec file (path argument; also accept a work-id form if convenient, but path is primary). The spec is a Markdown file containing:
   - a `## Confirmation` section with lines `- **Status: <CONFIRMED|DRAFT...>**`, `- Confirmed by: <name>`, `- Date: <date>` (see the live example at `.agent-work/issue-58/DESIGN_SPEC.md`)
   - a findings table with header columns exactly `ID | Lens(es) or Lens | Sev or Severity | Finding | Disposition | Reason` — be tolerant of the Lens/Sev header variants shown, strict on `Disposition` and `Reason` being present; a Disposition cell is EMPTY if blank or whitespace.
   - `--phase review`: PASS iff a findings table exists and has no empty Disposition cell (Status may still be DRAFT).
   - default / `--phase confirm`: PASS iff Status is CONFIRMED, Confirmed-by and Date are non-empty, AND no empty Disposition cells.
   - Any phase: if the text `UNCONFIRMED — DO NOT CUT` (or `UNCONFIRMED - DO NOT CUT`, hyphen variant) appears, print a loud refusal line naming it and FAIL.
   - A spec with NO findings table: FAIL for both phases with a clear "no findings table" message (a critical review is mandatory; absence must not pass silently).
3. **`scripts/init_work_area.py`** — extend `resolve_spine()` with a generic `<skill-dir>` token: when `--skill-dir` is given, `<skill-dir>` resolves to it; when omitted, same auto-detect as the commander token (`<skill-dir>/scripts` → `scripts` when `<root>/scripts` exists, remaining bare token → `.`). `<commander-skill-dir>` behavior MUST remain byte-identical (existing commander spines depend on it).
4. **Tests** (behavioral, green AND red cases): new `tests/test_verify_cycles.py` (pass case; zero-cycles fail; unconsolidated-cycle fail), new `tests/test_verify_spec_confirmed.py` (CONFIRMED+full-table pass; DRAFT fail on confirm phase but pass on review phase when table complete; empty-Disposition fail both phases; UNCONFIRMED-marker fail; no-findings-table fail), extend `tests/test_init_work_area.py` (generic token resolves with and without --skill-dir; commander token unchanged). Follow the existing test style in tests/ (unittest, tmp dirs).

## Protected Intent
"No work is cut from an unconfirmed design" must be mechanically enforceable — these scripts are the teeth. Fail visibly; a parse problem is a FAIL with a reason, never a silent pass. NOTE: g2 (next gate) will run your verifiers against templates it authors — keep parsers tolerant of surrounding prose, strict on the table columns and Confirmation fields.

## Test Mode
Test-after allowed (behavioral unit tests are a gate deliverable either way; red cases mandatory).

## Close Criteria
- Both verifier scripts exist, are single-purpose, and exit nonzero with a printed reason on every fail path listed above.
- `verify_spec_confirmed.py` run against the live `.agent-work/issue-58/DESIGN_SPEC.md` PASSES (default phase) — it is CONFIRMED with a complete findings table. (Note: that file's prose *mentions* the UNCONFIRMED marker inside a doctrine sentence — your marker detection must key on the marker as a status/header line, not any prose mention; this live-file pass is the guard.)
- `resolve_spine` handles `<skill-dir>` generically; `<commander-skill-dir>` byte-identical behavior.
- `python -m pytest tests/test_verify_cycles.py tests/test_verify_spec_confirmed.py tests/test_init_work_area.py -q` green; `python -m pytest tests/ -q` green.

## Allowed Scope
- NEW: `scripts/verify_cycles.py`, `scripts/verify_spec_confirmed.py`, `tests/test_verify_cycles.py`, `tests/test_verify_spec_confirmed.py`
- EDIT: `scripts/init_work_area.py` (resolve_spine + its docstring/help only), `tests/test_init_work_area.py` (additive)

## Specific Exclusions
- Do NOT touch `scripts/checklist_engine.py`, `scripts/install_constellation.py`, `tests/test_install_constellation.py` (owned by gate g5), any `skills/` content (gates g2–g5), or `.agent-work/issue-58/DESIGN_SPEC.md` (read-only contract).

## Constraints
- Fail visibly, no silent fallback; no hidden defaults.
- One canonical path: two single-purpose scripts, no shared parsing framework/module between them.
- Match the CLI/exit-code/print style of the existing `verify_*.py` scripts.
- Python 3, stdlib only (match existing scripts).

## Map Anchors (inbound)
- **Structural:** scripts/verify_cycles.py (NEW), scripts/verify_spec_confirmed.py (NEW), scripts/init_work_area.py::resolve_spine, tests/ (3 files)
- **Capability:** work-area/spine instantiation; hard-gate mechanical enforcement
- **Constraints/assumptions:** explore cannot close without ≥1 consolidated cycle (spec F3); confirm refuses on empty Disposition cells or DRAFT status (spec F1/F4); `<commander-skill-dir>` back-compat
- **Decision anchors:** DESIGN_SPEC.md findings table F1, F3, F4, F6 — do not contradict; surface conflicts, don't improvise
- **Evidence expectations:** targeted new-test files green, then full suite green

## Deliverable Path Check
- **Committed** — scripts/*.py, tests/*.py; verified: `git check-ignore scripts/init_work_area.py tests/test_init_work_area.py` exits 1 (not ignored).

## Required Evidence
- Command output of the targeted pytest run and the full-suite run (paste into result).
- Command output of `python scripts/verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md` (must PASS).
- One pasted example of each verifier's failure output (any red case).

## Verification Commands

```bash
python -m pytest tests/test_verify_cycles.py tests/test_verify_spec_confirmed.py tests/test_init_work_area.py -q
python -m pytest tests/ -q
python scripts/verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md
```

## Suggested Model Tier
simple bounded — well-specified scripts + tests, low ambiguity.

## Authority
Design fixed by DESIGN_SPEC.md (human-confirmed) and the plan-critic resolutions. You may choose internal parsing details (regexes vs line scans) and CLI arg names consistent with sibling scripts. You may NOT change the table column contract, phase semantics, marker string, or token names — surface a conflict instead.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, an exclusion must be touched, the live DESIGN_SPEC.md cannot pass without weakening a fail path (surface it — do not weaken), or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, test mode satisfied, evidence produced (pasted outputs), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
