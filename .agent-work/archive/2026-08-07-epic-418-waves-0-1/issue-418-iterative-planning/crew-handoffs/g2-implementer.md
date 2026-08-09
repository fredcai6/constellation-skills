# Implementer Handoff

## Gate

`g2`

## Task

Mint the lean `constellation-replan` skill and its versioned, strict JSON input/result contracts. Apply `constellation-write-a-skill` while executing through `constellation-implementer`. The complete frozen G2 imperative in `.agent-work/issue-418-iterative-planning/execute.json` is contractual; implement every field, type, enum, identity rule, preservation rule, and four-exit behavior named there.

## Protected Intent

Planning is iterative at wave boundaries. Evidence can advance, repair, revise, or stop the plan while launched issue identities and the confirmed intent boundary remain stable. Fixed-intent changes are proposals requiring human authority, never silently applicable output.

## Test Mode

TDD required. Create `tests/test_replan.py` first and run the identical focused command red and green. The red failure must name missing replanning behavior, not an import, path, or setup error.

## Close Criteria

- `REPLAN_INPUT.template.json` and `REPLAN_RESULT.template.json` encode schema version 1 exactly as frozen in G2.
- Pure verifier/renderer code supports `advance`, `repair`, `replan`, and `stop`.
- Every discrepancy and unlaunched item receives exactly one valid disposition.
- Wrong types, unknown enums, duplicate/missing identities, wrong-kind replacements, and wrong-boundary proposed values fail fast.
- `applicable=true` preserves confirmed fixed fields and launched identities; a fixed delta requires a typed escalation and `applicable=false`.
- Repair holds the current wave; evidence-only/drop cannot claim issue creation; `stop` alone may use `current_wave=null`.
- The skill works offline and produces nonempty wave-review and revised-epic Markdown.
- Installer/registration and write-a-skill corpus expectations include the new lean skill.
- `IMPLEMENTER_RESULT.md` records `gate_id: g2`, `red_exit: 1`, `green_exit: 0`, tests-before-code evidence, identical red/green command/output, and an ordinal path+byte diff digest.

## Allowed Scope

`skills/replan/**`; `tests/test_replan.py`; `tests/test_install_constellation.py`; `tests/test_write_a_skill.py`; `scripts/install_constellation.py`; canonical indexes/docs only where registration of the new skill requires it. Reuse G1 contract helpers when a clean import seam exists; otherwise keep validation local and explicit.

## Specific Exclusions

Do not wire Explorer, Commander, or Admiral lifecycle prose yet (G3). Do not create a compatibility alias, modify tracker APIs, edit historical/archive/external provenance, or make live GitHub/network writes. Do not alter the G1 schema.

## Constraints

- Read `constellation-implementer` and `constellation-write-a-skill` completely and drive their required workflow/checklists to terminal state.
- Strict inputs, explicit interfaces, fail-fast errors, one canonical execution path.
- Preserve all unrelated dirty-worktree changes.
- Treat the exact G1 templates in `skills/to-initial-issues/references/` as the source contract for nested current-wave, forecast, uncertainty, parked, good-enough, and issue shapes.

## Map Anchors

- **Structural:** `skills/replan/**`; `skills/to-initial-issues/references/**`; `scripts/install_constellation.py`; `SKILL_INDEX.md`
- **Capability:** evidence-driven wave-boundary replanning
- **Constraints:** stable launched identities; typed human escalation for fixed intent
- **Decisions:** four exits; applicable output cannot mutate fixed fields
- **Evidence:** focused schema/verifier/renderer/installer/write-a-skill tests
- **Confidence:** no architecture map; verify current public interfaces directly

## Deliverable Path Check

- **Committed:** `skills/replan/**`, `tests/test_replan.py`, installer/registration/index changes; representative paths are not ignored.
- **Local-only:** `.agent-work/issue-418-iterative-planning/g2-implement/IMPLEMENTER_RESULT.md`.

## Required Evidence

Load-bearing: causal red/green transcript; tests for all four exits; repair hold; evidence-only/drop issue-created constraint; launched identity stability; complete discrepancy/unlaunched dispositions; wrong discriminators; all five typed escalation boundaries; rendering; offline execution. Confirmatory: focused suite and registration audit.

## Wiring Grep

Run scoped symbol/call-site searches for each new public verifier/renderer helper. Zero call sites is a stop condition unless intentionally exposed as a CLI entrypoint with a proving CLI test.

## Verification Command

```bash
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
```

Use that exact command for both red and green evidence.

## Suggested Model Tier

Stronger — nested strict schemas and preservation invariants interact.

## Authority

Fred approved the frozen four-gate plan. Do not loosen schemas, change fixed boundaries, or broaden scope without returning a decision candidate.

## Stop Conditions

Stop if the frozen schema is internally inconsistent, exact G1 nested shapes cannot be reused without changing G1, a live tracker call is required, or an excluded/historical path must change.

## Return Format

Write `.agent-work/issue-418-iterative-planning/g2-implement/IMPLEMENTER_RESULT.md`, then send the result to `/root`. Include workflow feedback.
