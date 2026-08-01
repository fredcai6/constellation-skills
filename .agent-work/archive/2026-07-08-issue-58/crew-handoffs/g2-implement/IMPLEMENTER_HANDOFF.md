# Implementer Handoff

## Gate
g2 — Explorer engine artifacts: spine + cycle + spec templates, verifier↔template cross-check (issue-58)

## Task
Author the constellation-explorer engine artifacts so the enforcement scripts shipped in g1 have real templates to bite on. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (CONFIRMED, read-only) — read "Chosen design 1" (Spine table, Exploration cycles, Critical review paragraph), "Testing pathways" 1b and 2. The spec's Output-contract sections are enumerated in `.agent-work/issue-58/PROBLEM_STATEMENT.md` item 9.

1. **`skills/explorer/templates/EXPLORER_SPINE.template.json`** — gated checklist for `scripts/checklist_engine.py`, steps in order: `init`, `context`, `explore`, `spec`, `review`, `confirm`, `route`. Model the JSON shape on `skills/commander/templates/COMMANDER_SPINE.template.json` (statements, preconditions, postconditions, evidence requirements) and on how `.agent-work/issue-58/execute.json` carries an inline `"config"` block. Requirements:
   - **Inline engine config** with `"rework_cap": 99` (spec Critical-review para: default cap of 3 would hard-block the critic→re-explore loop; explorer is human-synchronous).
   - Script paths use the generic **`<skill-dir>`** token (g1's `resolve_spine` extension), e.g. `python <skill-dir>/scripts/verify_cycles.py <work-id>` — NOT `<commander-skill-dir>`.
   - **explore** step: closes only on (a) an `evidence` postcondition matching `evidence_type: user-decision` (human converge/shelve) AND (b) a `command` postcondition running `verify_cycles.py` against the work area.
   - **review** step: `command` postcondition running `verify_spec_confirmed.py --phase review` against the work area's DESIGN_SPEC.md.
   - **confirm** step: `evidence` postcondition matching `user-decision` AND `command` postcondition running `verify_spec_confirmed.py` (default/confirm phase).
   - **route** step: statement covers the three human routes (hand to to-issues/Commander / file shaped-design issue / shelve with `UNCONFIRMED — DO NOT CUT` header), archive work area, release lease.
   - Other steps (`init`, `context`, `spec`) carry statements/postconditions faithful to the spec Spine table rows (context seeds IDEAS_BOARD.md; spec = crystallize from board, per-section approval, design-it-twice on load-bearing interfaces).
   - Placeholder for the work id: match whatever convention `init_work_area.py` substitutes (inspect it — it already instantiates the commander template; use the same token, e.g. `<work-id>`, that the tested path resolves).
2. **`skills/explorer/templates/CYCLE.template.json`** — per-cycle survey checklist (engine survey shape — see `.agent-work/issue-58/interrogation.json` for a live survey the engine drove, and the commander's survey template if one exists in `skills/*/templates/`). Requirements: a top-level `flavor` field (values: `shotgun` | `compare` | `refine`); item flow point-questions → excursion dispatches → consolidation; a `consolidation` key that is **`null` in the template as shipped** and non-null only once the cycle is consolidated — this is exactly what `verify_cycles.py` keys on (read its source: it globs `cycle-*.json` in `.agent-work/<work-id>/` and fails on `consolidation: null`). The instantiated file naming must be `cycle-<N>.json` in the work-area root.
3. **`skills/explorer/templates/DESIGN_SPEC.template.md`** — the draft-state spec template. Requirements:
   - Draft-state header carries the loud marker line `UNCONFIRMED — DO NOT CUT` such that `verify_spec_confirmed.py` FAILS the shipped/instantiated draft (that is the point: a fresh spec must not pass).
   - `## Confirmation` block with `- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**` (or equivalent that the verifier rejects), `- Confirmed by:` (blank), `- Date:` (blank), and **assumptions-exercised lines**: `- Assumptions exercised:` / `- Assumptions accepted untested:` (see the live `.agent-work/issue-58/DESIGN_SPEC.md` Confirmation block for the confirmed-state shape the template must be editable into).
   - Findings table with fixed header exactly `| ID | Lens | Severity | Finding | Disposition | Reason |` (the verifier is strict on Disposition/Reason, tolerant on Lens/Sev variants — use the canonical fixed columns from the spec review row).
   - Sections per the Output contract (PROBLEM_STATEMENT item 9): intent; exploration-record digest (cycles, excursion answers incl. scoped nulls, rejected approaches with reasons); chosen design (interfaces in deep-module terms, per-section approval marks); testing pathways; out-of-scope; critic findings + dispositions (the table); Confirmation block.
4. **`tests/test_explorer_templates.py`** — the verifier↔template cross-check (spec Testing pathway 1b + 2). Behavioral, real fixtures, no mocks:
   - Instantiate the explorer spine into a tmp work area via `scripts/init_work_area.py --spine skills/explorer/templates/EXPLORER_SPINE.template.json`; assert the engine (`checklist_engine.py`) can `claim` + `start` the first step; assert resolved command postconditions reference real script paths (no unresolved `<skill-dir>` tokens).
   - From `CYCLE.template.json`: build a consolidated and an unconsolidated `cycle-N.json` fixture; assert `verify_cycles.py` passes/fails correctly. Include the zero-cycles red case against a fresh instantiated area.
   - From `DESIGN_SPEC.template.md`: (a) the raw/instantiated DRAFT variant must FAIL both confirm and review-if-table-incomplete phases and trip the UNCONFIRMED marker; (b) a CONFIRMED variant (Status flipped, Confirmed-by + Date filled, all Disposition cells filled) must PASS both phases; (c) **test each Confirmation field's blank case independently, with the other fields filled** (g1 lesson — a combined-blank fixture masked a real bug); (d) a review-phase pass on a DRAFT with complete table.
   - Follow existing test style (unittest, tmp dirs, subprocess or direct import consistent with `tests/test_verify_spec_confirmed.py`).

## Protected Intent
The two halves of the hard gate — verifiers (g1) and templates (this gate) — must be proven against each other in-suite. A template that emits a format the verifier can't parse, or that a fresh draft *passes*, silently guts "no work is cut from an unconfirmed design." The DRAFT template failing the verifier is a feature; the CONFIRMED-variant pass is the proof of editability.

## Test Mode
Test-after allowed; the cross-check test file IS a gate deliverable. Red cases mandatory per the list above.

## Close Criteria
- All three templates exist under `skills/explorer/templates/` and are valid (JSON parses; spine loads and drives through the engine in the test).
- Spine carries inline `config.rework_cap: 99` and uses `<skill-dir>` tokens for every bundled-script path.
- explore/review/confirm postconditions exactly per the spec Spine table (evidence types + command checks as itemized above).
- `verify_spec_confirmed.py` FAILS the shipped DRAFT template variant (both phases where required) and PASSES the CONFIRMED variant built by editing only the fields the template designates.
- `verify_cycles.py` cross-checked against what `CYCLE.template.json` actually emits (green + red).
- `python -m pytest tests/test_explorer_templates.py -q` green; `python -m pytest tests/ -q` green.
- Commit on `constellation/issue-58`.

## Allowed Scope
- NEW: `skills/explorer/templates/EXPLORER_SPINE.template.json`, `skills/explorer/templates/CYCLE.template.json`, `skills/explorer/templates/DESIGN_SPEC.template.md`, `tests/test_explorer_templates.py`

## Specific Exclusions
- Do NOT touch: `scripts/*` (g1 shipped them; if a verifier or `resolve_spine` cannot handle what the spec requires of a template, STOP and surface it — do not patch scripts), `skills/explorer/SKILL.md` or the other four explorer templates (gate g4), `skills/prototyper/**` (g3), `skills/_shared/**`, `scripts/install_constellation.py`, `tests/test_install_constellation.py` (g5), `skills/commander/**`, `.agent-work/issue-58/DESIGN_SPEC.md` (read-only contract).

## Constraints
- Fail visibly: the shipped DRAFT spec template must be REFUSED by the verifier, never tolerated.
- One canonical path: templates are instantiated via the existing `init_work_area.py` path, not a new mechanism.
- Match existing template idiom (compare with `skills/commander/templates/*`).
- Findings-table column names and the marker string are contractual — do not vary them.
- Python 3 stdlib only in tests.

## Map Anchors (inbound)
- **Structural:** skills/explorer/templates/ (NEW dir, 3 files), tests/test_explorer_templates.py (NEW)
- **Capability:** explorer spine instantiation via generic `<skill-dir>` token; hard-gate template side
- **Constraints/assumptions:** spec F1/F3/F4 (refusal semantics), inline rework_cap 99 (Critical-review para), verifier parsing contracts fixed by g1 (`scripts/verify_cycles.py`, `scripts/verify_spec_confirmed.py` — read their source; they are the senior partner in any format dispute)
- **Decision anchors:** DESIGN_SPEC.md findings table F1, F3, F4, F6; Spine table rows explore/review/confirm — surface conflicts, don't improvise
- **Evidence expectations:** `pytest tests/test_explorer_templates.py -q` then full suite green (feeds g2-integrate.c1)

## Deliverable Path Check
- **Committed** — all four paths; verify none is gitignored (`git check-ignore <paths>` exits 1).

## Required Evidence
- Pasted output: targeted pytest run + full-suite run.
- Pasted output: `verify_spec_confirmed.py` refusing the DRAFT template variant and passing the CONFIRMED variant.
- Pasted output: `verify_cycles.py` green + one red case against template-derived fixtures.
- The engine claim/start transcript (or the test assertion proving it) for the instantiated spine.

## Verification Commands

```bash
python -m pytest tests/test_explorer_templates.py -q
python -m pytest tests/ -q
```

## Suggested Model Tier
stronger — multi-artifact contract alignment across engine, verifiers, and templates; format disputes must be detected, not papered over.

## Authority
Design fixed by DESIGN_SPEC.md (human-confirmed). You may choose statement wording, survey item structure, and template prose. You may NOT change: step names/order, evidence types, command-check semantics, the findings-table columns, the marker string, the rework cap value, or anything in `scripts/`. Surface conflicts instead.

## Stop Conditions
Stop and return if: a g1 verifier cannot pass/fail as the spec demands without a script change; the engine rejects the inline config; allowed scope must be exceeded; or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g2-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, test mode satisfied, evidence produced (pasted outputs), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be — a bare `none` is treated as unfilled).
