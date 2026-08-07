# Implementer Handoff

## Gate
g3 — constellation-prototyper skill: SKILL.md + 3 reference files + handoff/result templates (issue-58)

## Task
Author the constellation-prototyper skill in full. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (CONFIRMED, read-only) — the governing section is ALL of "Chosen design 2", plus the explorer→prototyper seam paragraph under "Interfaces, in the vocabulary this spec adopts". Model file layout and SKILL.md idiom on an existing crew-tier skill (`skills/triage/` is the named exemplar: doctrine + templates, handoff-driven, no engine checklist of its own).

1. **`skills/prototyper/SKILL.md`** — frontmatter `name: constellation-prototyper` (check a sibling SKILL.md for the exact frontmatter fields the installer expects). Content requirements:
   - Role: crew-tier, handoff-driven, no engine checklist; dispatchable as an explorer excursion, by a Commander, or standalone by the human.
   - Core doctrine (after Pocock, adapted): a prototype is **throwaway code that answers one named question — the question decides the shape**; question stated in writing before any code; one command to run; no tests, no persistence, no polish; surface full state after every action; delete or absorb when done — the answer is the only thing worth keeping.
   - **Scoped-nulls doctrine text, verbatim-greppable**: the SKILL.md must contain the word "scoped" in a scoped-nulls doctrine passage (the integrate gate greps for it): a negative result kills *that specific test under those conditions*, never the idea class; every verdict states what was and was NOT tested; the default next move after a null is another variant.
   - Branch pick logic: which of the three branches (logic / ui / measurement) fits which question, with the one-line decision rule per branch.
   - Location split by driver: human-driven prototypes (logic TUI, UI variants) in-repo next to real code, clearly marked, one command to run; agent-driven spikes in throwaway worktrees. The handoff states which.
   - Closeout rule: a recorded disposition is MANDATORY — **deleted** / **absorbed** (with commit ref) / **parked-with-owner**. No silent rot.
   - Attribution note: adapted from mattpocock/skills' prototype skill.
2. **`skills/prototyper/references/logic.md`** — interactive terminal app over a **pure, portable logic module** (reducer / state machine / pure functions; NO I/O in the module); the TUI shell is throwaway, the validated module is liftable into real code. For "does this state model / data shape feel right?"
3. **`skills/prototyper/references/ui.md`** — 3–5 **structurally different** variants on one route; `?variant=` switcher; floating cycle bar; strongly prefer mounting inside a real existing page ("an empty route hides design problems a populated one exposes"); fold the winner, delete the losers; hidden in production. For "what should this look like?"
4. **`skills/prototyper/references/measurement.md`** — **THIN POINTER, not a restatement**: scoreboard defines the metric first; each spike implements one mechanism; the output is a number on the board — then POINT to the inherited global-orchestrator spike doctrine (find where the existing spike doctrine lives in `skills/_shared/` / installed references and cite that location) rather than duplicating it. Keep this file short; duplication is a review finding.
5. **`skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md`** — fields: the one named question; branch (logic|ui|measurement); host-project conventions (runtime, task runner, routing); location (in-repo vs worktree, per the driver split); stop conditions; return format. **These field names are a downstream contract**: g4's `EXCURSION_BRIEF.template.md` must carry an identical prototype-section field set, so keep the fields cleanly enumerable (one heading or bullet per field, no prose-buried fields).
6. **`skills/prototyper/templates/PROTOTYPE_RESULT.template.md`** — fields: the answer; **what was tested AND what was NOT tested** (the literal phrase "NOT tested" must appear — integrate gate greps for it); what it taught beyond the question; surviving pure module (if any) and where it lives; **disposition** (deleted / absorbed-with-commit / parked-with-owner — the word "disposition" must appear; also grepped).

## Protected Intent
The prototyper's interface is `PROTOTYPE_HANDOFF` in → `PROTOTYPE_RESULT` out; the prototype artifact itself is NOT part of the interface — it is implementation, disposed at closeout. Deep by construction: one question in, one scoped answer out. The RESULT template is where scoped-nulls enforcement lives — its NOT-tested and disposition fields are the mechanical residue of the doctrine; do not soften them into optional prose.

## Test Mode
No new test files this gate (spec Testing pathway 4's template/doctrine invariant checks are owned by g5's install-test extension; the integrate gate's grep checks cover the g3 invariants). Your verification = the integrate command below.

## Close Criteria
- All six files exist with the content requirements above.
- Frontmatter name is exactly `constellation-prototyper` and matches installer discovery conventions (compare against a sibling skill's frontmatter).
- Grep invariants pass: `NOT tested` and `disposition` in PROTOTYPE_RESULT.template.md; `scoped` (in the scoped-nulls doctrine) in SKILL.md.
- measurement.md is a thin pointer (points to the shared spike doctrine's actual location; does not restate it).
- PROTOTYPE_HANDOFF fields cleanly enumerable for g4 alignment.
- Full suite status: run `python -m pytest tests/ -q` and report the failure distribution BY ROOT CAUSE with per-file counts (derive from `grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`, not a glance). Expected: the known missing-`skills/explorer/SKILL.md` transient persists (g4), and install-test expectations may shift because `constellation-prototyper` now EXISTS but is not yet in the expected-skills list (g5). Both classes are covered by the human waiver recorded at g2 (scoped by root cause, through g5). ANY failure outside those two root-cause classes = stop condition.
- Commit on `constellation/issue-58`.

## Allowed Scope
- NEW only: `skills/prototyper/SKILL.md`, `skills/prototyper/references/logic.md`, `skills/prototyper/references/ui.md`, `skills/prototyper/references/measurement.md`, `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md`, `skills/prototyper/templates/PROTOTYPE_RESULT.template.md`

## Specific Exclusions
- Do NOT touch: `scripts/**`, `tests/**` (g5 owns install-test changes), `skills/explorer/**` (g2/g4), `skills/_shared/**` (g5 owns the vocabulary addition), `skills/commander/**`, `skills/triage/**` and other existing skills (read-only exemplars), `.agent-work/issue-58/DESIGN_SPEC.md`.

## Constraints
- Concise doctrine over exhaustive prose — match the register and length of existing SKILL.md files (read 2–3 siblings first).
- measurement.md: pointer, not restatement (spec is explicit; a duplicate of spike doctrine is a defect).
- The three grep-invariant strings are contractual; so are the disposition value names and the field lists in both templates.
- No engine checklist, no scripts, no spine for this skill — its statelessness is a design decision (crew-tier).

## Map Anchors (inbound)
- **Structural:** skills/prototyper/ (NEW: SKILL.md, references/ x3, templates/ x2); exemplar skills/triage/
- **Capability:** prototype excursion adapter for explorer (g4 aligns EXCURSION_BRIEF to your HANDOFF fields); standalone/Commander dispatch
- **Constraints/assumptions:** handoff/result field contract (spec "Interface (templates)" bullets); closeout disposition mandatory; scoped-nulls in RESULT
- **Decision anchors:** DESIGN_SPEC "Chosen design 2" in full; findings table F-rows touching prototyper — surface conflicts, don't improvise
- **Evidence expectations:** integrate-gate grep/file checks + full-suite distribution report (feeds g3-integrate.c1, which carries the human waiver for the known transients)

## Deliverable Path Check
- **Committed** — all six paths; verify none is gitignored.

## Required Evidence
- Pasted output of the integrate-gate file/grep checks (run them via bash: `test -f ... && grep -qi 'NOT tested' ...` etc. — see Verification Commands).
- Pasted full-suite run with the per-file failure distribution and root-cause attribution.
- The exact PROTOTYPE_HANDOFF field list (enumerated) for g4's alignment.

## Verification Commands

```bash
test -f skills/prototyper/SKILL.md && test -f skills/prototyper/references/measurement.md && test -f skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md && grep -qi 'NOT tested' skills/prototyper/templates/PROTOTYPE_RESULT.template.md && grep -qi 'disposition' skills/prototyper/templates/PROTOTYPE_RESULT.template.md && grep -qi 'scoped' skills/prototyper/SKILL.md && echo INVARIANTS-OK
python -m pytest tests/ -q
```

## Suggested Model Tier
simple bounded — well-specified documentation artifacts; the care point is contract fidelity (field names, grep strings, pointer-not-restatement), not ambiguity.

## Authority
Design fixed by DESIGN_SPEC.md (human-confirmed). You may choose prose wording, section ordering, and exemplar-matched formatting. You may NOT change: branch names, disposition value names, template field sets, the grep-invariant strings, or the thin-pointer rule. Surface conflicts instead.

## Stop Conditions
Stop and return if: any full-suite failure falls outside the two waived root-cause classes (missing explorer SKILL.md; expected-skills-list drift from the new prototyper); an exclusion must be touched; the shared spike doctrine cannot be located for measurement.md to point at; or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g3-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, evidence produced (pasted outputs incl. failure distribution by root cause), the enumerated HANDOFF field list, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (run-specific; a bare `none` is treated as unfilled).
