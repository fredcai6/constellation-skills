# Reviewer Handoff

## Gate
g4 — constellation-explorer SKILL.md + remaining templates + CYCLE config fix (issue-58)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-58/g4-review/review.json`.

## What Was Implemented
`skills/explorer/SKILL.md` (orchestrator-tier, upstream-only, no delegated mode; headline doctrine 1–3; flavors; excursion ramps; ideas board; cold review panel; route) plus four templates (EXPLORER_STARTING_QUESTIONS, IDEAS_BOARD, EXCURSION_BRIEF, CRITIC_HANDOFF), the authorized tc2 edit dropping `config_ref` from `CYCLE.template.json`, and one additive runtime test (engine drives a cycle survey in a config-less directory). Commit `9b89e53`.

## How to Inspect the Diff
`git show 9b89e53 --stat` then `git show 9b89e53` on branch `constellation/issue-58`; `git status --porcelain` for extras.

## Task Statement
The implementer handoff at `.agent-work/issue-58/crew-handoffs/g4-implement/IMPLEMENTER_HANDOFF.md` is the contract (items 1–6). Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (read-only) — verify SKILL.md against ALL of "Chosen design 1", paragraph by paragraph. This file is the epic's doctrinal core; doctrine fidelity IS the review.

## Close Criteria
- **Doctrine coverage, paragraph by paragraph against "Chosen design 1"**: role/tier and upstream-only/no-delegated-mode; headline doctrine in order 1-2-3 (premature convergence THE failure mode + agent never initiates convergence + ripeness only as a standalone message containing nothing else; scoped nulls/optimistic persistence with was-and-was-NOT-tested and impossibility-requires-class-spanning-evidence; hard gate with verifier + marker + honest trust-model statement); spine walk-through; flavors (Shotgun ~20 human-set with sanctioned wild entries and culls-stay-on-board, Compare 2–5 recommendation-led with hybrids, Refine spec-shaped) with the natural arc AND the dead-refine fallback framed as the loop working; Interrogator seam; excursion ramps complete (brief-before-dispatch, background, on-ramp-before-consolidation, either side initiates, run_crew + recover_crews before each dispatch AND before consolidation, slow-excursion never-silently-dropped, one-brief-no-double-entry); ideas board as source of truth (resume from board, mid-exploration shelve files the board); spec phase (per-section approval, delta re-confirmation, design-it-twice with skip-with-stated-reason); critical review (cold/no-record/nothing-sacred/human-filters-noise, panel scaled by weight with when-in-doubt-panel, EDIT/RE-EXPLORE/REJECT triage human-only, confirm opens only on full Disposition column, reopen cascade cost documented); route (three routes, explorer NEVER cuts issues, archive + release). Missing or diluted paragraphs are findings.
- **Marker discipline, verify against the script not by eye**: run `python scripts/verify_spec_confirmed.py` semantics via its `_unconfirmed_marker_hit` — every marker mention in the five files must be inline prose (no standalone marker line anywhere in skills/explorer/), AND the shelve-route doctrine must instruct standalone placement on shelved issues. Suggested check: build a scratch file from any SKILL.md line containing the marker and confirm it does not trip; grep -n "UNCONFIRMED" skills/explorer/ -r and inspect each hit.
- **EXCURSION_BRIEF prototype section**: byte-match the six top-level headings against the real `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md` yourself (Question / Branch / Host-project conventions / Location / Stop conditions / Return format). Only the six top-level headings are the frozen contract — do not over-read sub-bullets (g3 reviewer note). All three excursion types present (research / prototype / design-it-twice with the four named constraint lenses and comparison axes).
- **CRITIC_HANDOFF**: cold-read contract explicit (spec only, no exploration record, nothing sacred); return format matches `| ID | Lens | Severity | Finding | Disposition | Reason |` exactly; Disposition/Reason documented as left EMPTY for human triage — a critic that self-triages is a defect.
- **tc2 fix**: `CYCLE.template.json` no longer references `docs/agents/engine-config.json`; verify the implementer's claim that `load_config` degrades to `{}` and surveys never consult rework_cap (read the engine source at the relevant functions); the new runtime test genuinely drives claim/start/consolidate on an instantiated cycle survey in a directory with NO engine-config file — reproduce it.
- **Frontmatter**: `name: constellation-explorer`, sibling-consistent.
- **Suite inflection, reproduce yourself**: `python -m pytest tests/test_explorer_templates.py -q` (24 expected) and `python -m pytest tests/ -q` — expect exactly the expected-skills-list assertions in `tests/test_install_constellation.py` failing (2), everything else green including all of `test_feedback_tooling.py`. Any other failure is a BLOCK.
- Diff touches ONLY: 5 NEW explorer files + CYCLE.template.json + tests/test_explorer_templates.py (additive); commit on constellation/issue-58.

## Allowed Scope
NEW: skills/explorer/SKILL.md, skills/explorer/templates/{EXPLORER_STARTING_QUESTIONS,IDEAS_BOARD,EXCURSION_BRIEF,CRITIC_HANDOFF}.template.md. EDIT: skills/explorer/templates/CYCLE.template.json (config_ref only), tests/test_explorer_templates.py (additive).

## Specific Exclusions
scripts/**, skills/explorer/templates/EXPLORER_SPINE.template.json + DESIGN_SPEC.template.md (g2 frozen), skills/prototyper/** (g3 frozen), skills/_shared/**, skills/commander/**, tests/test_install_constellation.py (g5), .agent-work/issue-58/DESIGN_SPEC.md — flag if touched.

## Constraints the Implementation Must Respect
- Contractual strings: marker text, flavor names, excursion types, table columns, six HANDOFF headings, EDIT/RE-EXPLORE/REJECT.
- Doctrine order 1-2-3; register consistent with skills/commander/SKILL.md.
- Fail visibly (CYCLE fix must not introduce silent mis-defaulting).

## Map Anchors (inbound)
- **Structural:** skills/explorer/ (SKILL.md + 4 templates NEW, CYCLE edited); tests/test_explorer_templates.py (+1 runtime case); reads frozen PROTOTYPE_HANDOFF + spine
- **Capability:** explorer doctrine operative; excursion/critic contracts; config-less cycle survey runtime
- **Constraints/assumptions:** marker standalone-vs-inline; six-heading freeze; scripts frozen
- **Decision anchors:** DESIGN_SPEC "Chosen design 1" every paragraph; findings F1–F10 — flag contradictions
- **Evidence expectations:** targeted 24 green; full suite exactly 2 expected-skills failures (feeds g4-integrate.c1, human waiver in force through g5)

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g4-implement/IMPLEMENTER_RESULT.md`: heading diff IDENTICAL; marker audit against `_unconfirmed_marker_hit`; inflection 31→2/420 passed; targeted 24 green; tc2 rationale (dangling reference, not crash — load_config degrades to {}). Verify the rationale and the marker audit yourself, not just the outputs.

## Suggested Model Tier
stronger — paragraph-level doctrine fidelity across the epic's core file plus a runtime-behavior verification; dilution and omission are the failure modes, and they don't grep.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, any suite failure outside the expected-skills class, any standalone marker line in skills/explorer/, or a policy decision beyond the recorded waiver is required.

## Return Format
Return REVIEW_RESULT at `.agent-work/issue-58/crew-handoffs/g4-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK) unambiguous near the top, per-check findings, blockers, out-of-scope observations, workflow feedback (mandatory, run-specific). The run is only complete when that file exists.
