# Reviewer Handoff

## Gate
g3 — constellation-prototyper skill (issue-58)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-58/g3-review/review.json`.

## What Was Implemented
The complete constellation-prototyper crew-tier skill: `skills/prototyper/SKILL.md` (frontmatter `constellation-prototyper`; one-named-question doctrine; scoped-nulls passage; branch pick logic; location-by-driver split; mandatory disposition closeout; Pocock attribution), `references/logic.md` / `ui.md` / `measurement.md` (measurement is a THIN POINTER to the shared spike doctrine, not a restatement), and `templates/PROTOTYPE_HANDOFF.template.md` + `PROTOTYPE_RESULT.template.md`. Six NEW files, no edits elsewhere.

## How to Inspect the Diff
Commit `b54a1eb` on branch `constellation/issue-58`: `git show b54a1eb --stat` then `git show b54a1eb`. Also `git status --porcelain` for unexplained extras.

## Task Statement
The implementer handoff at `.agent-work/issue-58/crew-handoffs/g3-implement/IMPLEMENTER_HANDOFF.md` is the contract (items 1–6). Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (read-only) — verify against ALL of "Chosen design 2" line by line, plus the prototyper bullet under "Interfaces, in the vocabulary this spec adopts".

## Close Criteria
- **Spec fidelity, line by line against "Chosen design 2"**: role/tier (crew-tier, handoff-driven, no engine checklist, three dispatch contexts); core doctrine complete (question-decides-shape, question in writing first, one command to run, no tests/persistence/polish, surface full state, delete-or-absorb); three branches each matching their spec bullet (logic: pure portable module + throwaway TUI; ui: 3–5 structurally different variants, `?variant=` switcher, floating bar, real-page mounting preference; measurement: scoreboard-first, one mechanism per spike, number on the board); location split by driver; closeout rule with the three disposition values (deleted / absorbed-with-commit / parked-with-owner).
- **Measurement-as-pointer constraint**: `references/measurement.md` must POINT to the shared spike doctrine's real location and not restate it — verify the pointed-at file exists and actually contains the spike/scoreboard doctrine, and that measurement.md does not duplicate its content (duplication is a finding).
- **Grep invariants, run yourself**: `grep -qi 'NOT tested' skills/prototyper/templates/PROTOTYPE_RESULT.template.md`, `grep -qi 'disposition'` same file, `grep -qi 'scoped' skills/prototyper/SKILL.md` — and confirm the scoped-nulls passage is genuine doctrine (scoped verdicts, what-was-NOT-tested, next-move-is-another-variant), not a token word planted to satisfy the grep.
- **RESULT template fields**: answer; what was tested AND what was NOT tested; what it taught beyond the question; surviving pure module + location; disposition. The NOT-tested and disposition fields must be structural (real fields), not optional prose.
- **HANDOFF template fields cleanly enumerable** (one heading/bullet per field): Question / Branch / Host-project conventions / Location / Stop conditions / Return format — g4's EXCURSION_BRIEF must mirror these; flag anything prose-buried or ambiguous NOW, because after g3 closes these names freeze.
- **Frontmatter/installer conventions**: compare frontmatter against 2 sibling skills; name exactly `constellation-prototyper`.
- **Register match**: SKILL.md length/tone consistent with existing crew-tier skills (triage is the exemplar).
- **Full-suite status, reproduce yourself**: `python -m pytest tests/ -q`; confirm the failure set matches the implementer's claim — all failures carrying the single signature `InstallError: source skill is missing SKILL.md: skills/explorer` (waived class 1; class 2 masked until g4). ANY failure outside the two waived root-cause classes is a BLOCK. The waiver (human, recorded at g2-integrate, through g5) covers exactly: installer missing-SKILL.md refusal wherever it surfaces + expected-skills-list drift.
- Diff touches ONLY the six new files; commit on constellation/issue-58.

## Allowed Scope
NEW only: skills/prototyper/SKILL.md, skills/prototyper/references/{logic,ui,measurement}.md, skills/prototyper/templates/{PROTOTYPE_HANDOFF,PROTOTYPE_RESULT}.template.md.

## Specific Exclusions
scripts/**, tests/**, skills/explorer/**, skills/_shared/**, skills/commander/**, skills/triage/**, .agent-work/issue-58/DESIGN_SPEC.md — flag if the diff touches any.

## Constraints the Implementation Must Respect
- Thin-pointer rule for measurement.md (spec-explicit).
- Contractual strings: branch names, disposition value names, template field sets, grep-invariant strings.
- No engine checklist/scripts/spine for this skill — statelessness is the design.
- Doctrine register matched to siblings; concision over exhaustiveness.

## Map Anchors (inbound)
- **Structural:** skills/prototyper/ (NEW, 6 files); exemplar skills/triage/; pointed-at spike doctrine in skills/_shared/
- **Capability:** prototype excursion adapter for explorer; standalone/Commander dispatch
- **Constraints/assumptions:** HANDOFF field set freezes at g3 close (g4 EXCURSION_BRIEF alignment); scoped-nulls lives in the RESULT template
- **Decision anchors:** DESIGN_SPEC "Chosen design 2" in full — flag contradictions
- **Evidence expectations:** grep/file invariants + full-suite distribution scoped to waived classes (feeds g3-integrate.c1, which carries the human waiver)

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g3-implement/IMPLEMENTER_RESULT.md`: INVARIANTS-OK; full suite 31/389/1 with single-signature attribution and the masking note (class 2 hidden until g4 because discovery aborts); enumerated HANDOFF field list. Verify the attribution and the masking claim yourself, not just the outputs.

## Suggested Model Tier
simple bounded — doctrine/contract fidelity review of documentation artifacts; the care points are spec line-coverage, the pointer-not-restatement check, and the failure-set reproduction.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, any full-suite failure falls outside the two waived root-cause classes, or a policy decision beyond the recorded waiver is required.

## Return Format
Return REVIEW_RESULT at `.agent-work/issue-58/crew-handoffs/g3-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK) stated unambiguously near the top, per-check findings, blockers, out-of-scope observations, workflow feedback (mandatory, run-specific). The run is only complete when that file exists.
