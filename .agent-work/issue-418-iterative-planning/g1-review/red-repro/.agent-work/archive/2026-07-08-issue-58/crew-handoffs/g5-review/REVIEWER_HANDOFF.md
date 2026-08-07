# Reviewer Handoff

## Gate
g5 — Deep-module vocabulary + Commander intake line + installer wiring + install tests (issue-58; FINAL gate, ends the waiver window)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-58/g5-review/review.json`.

## What Was Implemented
Four tightly-scoped edits: the Deep-module vocabulary section appended to `skills/_shared/global-everyone.md`; a one-line shaped-design intake note in `skills/commander/SKILL.md`'s understand guidance; explorer/prototyper entries in `install_constellation.py`'s two bundle dicts; additive install-test extensions (expected names, explorer script-bundle assertion, vocabulary-ships assertion). Commit `2c8074d`. This gate's claim: full suite fully green, waiver window closed.

## How to Inspect the Diff
`git show 2c8074d --stat` then `git show 2c8074d` on branch `constellation/issue-58`; `git status --porcelain` for extras.

## Task Statement
Implementer handoff: `.agent-work/issue-58/crew-handoffs/g5-implement/IMPLEMENTER_HANDOFF.md` (items 1–5). Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (read-only) — "Chosen design 3", "4. Install and test integration", the Commander-seam paragraph under Chosen design 1, and Testing pathway 3.

## Close Criteria
- **THE exit criterion, reproduce yourself**: `python -m pytest tests/ -q` FULLY green — zero failures. Also `python -m pytest tests/test_install_constellation.py -q` green. This gate has NO override policy; any red is a BLOCK.
- **Vocabulary section vs "Chosen design 3", term by term**: all six terms with their spec-fixed meanings (module scale-agnostic; interface = EVERYTHING a caller must know incl. invariants/ordering/error modes/config/performance; seam placement its own decision; adapter with one-adapter-hypothetical/two-adapters-real; depth/leverage as behavior per unit of interface learned; locality) plus BOTH working rules (interface-is-the-test-surface with the wrong-shape consequence; the deletion test with both outcomes). Register matches the file (dense, departures-only — an essay is a finding). A missing or diluted term/rule is a finding.
- **Commander intake line**: present in the understand-step guidance; one-line-scale (a section or multi-paragraph addition is a finding); semantics per the spec seam paragraph (verify confirmed via verify_spec_confirmed.py / visible CONFIRMED marker before cutting; UNCONFIRMED shaped-design issue never cut); NO other Commander doctrine changed (read the full diff hunk).
- **Marker discipline, verify against the script**: the new marker mention in skills/commander/SKILL.md must be inline prose — confirm it cannot trip `_unconfirmed_marker_hit` (scratch-fixture it if in doubt); confirm no standalone marker line was introduced anywhere in the diff.
- **Installer edits**: exactly the two dict entries; explorer bundle = the six scripts named in the spec (checklist_engine, init_work_area, run_crew, recover_crews, verify_cycles, verify_spec_confirmed); prototyper has NO script bundle and `_GLOBAL_CREW` references; keys match the dicts' consumer convention (verify against `discover_skills` / the `.get(source_path.name, ())` call the implementer cites).
- **Install tests genuine**: the two new test methods assert real installed-tree behavior (files land, section text present in the installed copy), not source-tree tautologies; both installed names in the expected list; run them yourself.
- **Red→green claim**: confirm via git that the 2 previously-failing tests are the ones the expected-list addition fixes (e.g. `git stash`-free check: run the suite at HEAD~1 if cheap, or verify the BEFORE evidence's failure names against the expected-list diff hunk).
- **Dry-run discovery**: run the installer's dry-run yourself; both skills discovered with installed names `constellation-explorer` / `constellation-prototyper`.
- Integrate greps pass: `grep -qi 'deep-module' skills/_shared/global-everyone.md`, `grep -qi 'shaped-design' skills/commander/SKILL.md`.
- Diff touches ONLY the four allowed files; commit on constellation/issue-58.

## Allowed Scope
EDIT only: skills/_shared/global-everyone.md (append), skills/commander/SKILL.md (intake line), scripts/install_constellation.py (two dicts), tests/test_install_constellation.py (additive).

## Specific Exclusions
skills/explorer/**, skills/prototyper/** (frozen g2–g4), scripts/verify_*.py, scripts/checklist_engine.py, scripts/init_work_area.py, scripts/run_crew.py, scripts/recover_crews.py, other tests/ files, .agent-work/issue-58/DESIGN_SPEC.md — flag if touched.

## Constraints the Implementation Must Respect
- Vocabulary content contract (six terms + two rules) and register.
- Installer edits limited to dict entries; no refactors.
- Marker inline-only; contractual strings (`shaped-design`, bundle script names).
- One-line-scale Commander edit.

## Map Anchors (inbound)
- **Structural:** skills/_shared/global-everyone.md, skills/commander/SKILL.md::understand, install_constellation.py::SKILL_SCRIPT_BUNDLES/SKILL_REFERENCE_BUNDLES, tests/test_install_constellation.py
- **Capability:** vocabulary rides the reference-bundle mechanism into every installed skill; Commander downstream refusal; both skills installable
- **Constraints/assumptions:** suite fully green = epic exit criterion, NO waiver at this gate; frozen g2–g4 files; marker inline-only
- **Decision anchors:** DESIGN_SPEC "Chosen design 3" + "Install and test integration" + Commander-seam paragraph — flag contradictions
- **Evidence expectations:** red→green on the 2 expected-skills tests; full suite zero failures (feeds g5-integrate.c1 — command check with no override)

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g5-implement/IMPLEMENTER_RESULT.md`: BEFORE 2 failed/420 passed (named tests), AFTER 424 passed/0 failed; targeted 33 passed; GREPS-OK; dry-run showing both skills; assumptions (dict keys = source dir names, verified against consumer; intake line placement; representative-skill vocabulary assertion). Verify the assumptions and reproduce the numbers yourself.

## Suggested Model Tier
simple bounded — four scoped edits with a mechanical exit criterion; the care points are the term-by-term vocabulary contract and the marker/scope checks.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, any suite failure exists, any exclusion was touched, or a policy decision is required.

## Return Format
Return REVIEW_RESULT at `.agent-work/issue-58/crew-handoffs/g5-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK) unambiguous near the top, per-check findings, blockers, out-of-scope observations, workflow feedback (mandatory, run-specific). The run is only complete when that file exists.
