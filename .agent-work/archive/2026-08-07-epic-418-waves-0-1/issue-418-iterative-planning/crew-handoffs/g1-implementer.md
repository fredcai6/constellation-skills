# Implementer Handoff

## Gate

`g1`

## Task

Implement the canonical `constellation-to-initial-issues` skill and strict shaped-brief/current-wave manifest contract. Use the complete frozen G1 imperative and schema in `.agent-work/issue-418-iterative-planning/execute.json`; it is contractual, including every field/type/cardinality, eight rendered headings, direct Explorer-template seam, edge validation, idempotency crash matrix, installer migration, and rename inventory.

## Protected Intent

Only the current wave becomes runnable tracker issues. Later outcomes remain nonbinding forecast/uncertainty/parked state. Preserve rationale, strict inputs, existing adapters/receipts, and one canonical execution method.

## Test Mode

TDD required. Add/rename focused tests first. Run the identical focused command red and green. The red failure must name intended missing behavior, not import/path/setup failure.

## Close Criteria

- Every G1 schema and mapping in `execute.json` is encoded in template/reference and fail-fast validation.
- A confirmed shaped brief feeds the initial verifier/renderer directly without prose translation.
- Only `current_wave.issues` reaches find/create; forecast entries are structurally non-runnable.
- Zero edges pass; dangling/cyclic edges fail.
- Exactly eight required epic headings render.
- Existing offline Markdown and receipt recovery remain, strengthened for every child crash window and receipt-key mismatch.
- Hard rename and exact installer legacy-destination policy work for no-force, force, dry-run, subset, and full installs.
- Exact rename inventory is completed; archives/legacy/external provenance remain untouched.
- `IMPLEMENTER_RESULT.md` includes `gate_id: g1`, `red_exit: 1`, `green_exit: 0`, diff digest, identical red/green command and outputs, tests-before-production evidence, and rename inventory.

## Allowed Scope

`skills/to-issues/**` renamed to `skills/to-initial-issues/**`; `tests/test_to_issues.py` renamed/rewritten as `tests/test_initial_issues.py`; `scripts/verify_issue_set.py`; `scripts/file_issue_set.py`; `scripts/install_constellation.py`; installer/initial-cut tests; `README.md`; `SKILL_INDEX.md`; `docs/CONSTELLATION_OVERVIEW.md`; `docs/POSITIONING.md`; `skills/write-a-skill/SKILL.md`; Explorer's live route name only where required for canonical registration. Existing tests may be reconciled where the old exhaustive schema is deliberately invalidated.

## Specific Exclusions

Do not implement replanning or broad Explorer/Commander/Admiral contract changes (G2/G3). Do not edit `.agent-work/archive/**`, legacy transcript fixtures, external mattpocock provenance, checklist engine, tracker architecture, or add a compatibility alias. No live GitHub/network writes.

## Constraints

- Read `constellation-implementer` completely and drive its checklist to terminal state.
- Strict inputs; fail fast; no silent compatibility fallback.
- Output `epic.title` copies shaped-brief `title`; output `epic.spec_path` copies `source_path` exactly.
- Preserve unrelated dirty-worktree changes.

## Map Anchors

- **Structural:** `README.md`; `SKILL_INDEX.md`
- **Capability:** initial cut and offline filing
- **Constraints:** single canonical execution path; existing adapter/receipt invariants
- **Decisions:** hard rename; current wave only actionable (`@grade: settled/human`)
- **Evidence:** focused schema/filer/installer/idempotency tests
- **Confidence:** no architecture map; verify public interfaces directly

## Deliverable Path Check

- **Committed** — `skills/to-initial-issues/**`, `tests/test_initial_issues.py`, `scripts/verify_issue_set.py`, `scripts/file_issue_set.py`, `scripts/install_constellation.py`, live docs/indexes; `git check-ignore` returned 1 for representative paths before dispatch.
- **Local-only** — `.agent-work/issue-418-iterative-planning/g1-implement/IMPLEMENTER_RESULT.md`; workflow evidence only.

## Required Evidence

Load-bearing: causal red/green transcript; direct shaped-brief seam test; forecast spy; zero-edge/dangling/cycle tests; every-child crash matrix and receipt mismatch; legacy installer migration matrix. Confirmatory: full focused suite and live-name audit with exact allowlist.

## Wiring Grep

Run a scoped symbol/call-site search for every new public verifier/renderer helper. Zero external call sites is a stop condition unless the symbol is intentionally a CLI entrypoint and its CLI test proves the call.

## Verification Commands

```bash
uv run python -m pytest -q tests/test_initial_issues.py tests/test_install_constellation.py
uv run python scripts/verify_skill_registered.py --skill to-initial-issues
```

## Suggested Model Tier

Stronger — strict schema, rename migration, and idempotency changes interact.

## Authority

Fred approved the frozen four-gate plan and hard rename. Do not choose an alias, loosen required fields, or broaden tracker APIs without returning a decision candidate.

## Stop Conditions

Stop if the frozen schema is internally inconsistent, the existing adapter seam cannot preserve receipts without redesign, a live tracker call is required, or any excluded/historical path must change.

## Return Format

Write `.agent-work/issue-418-iterative-planning/g1-implement/IMPLEMENTER_RESULT.md`, then send the verdict/result to `/root`. Include workflow feedback.
