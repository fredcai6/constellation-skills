# Reviewer Handoff

## Gate
g1 (issue-99)

## Survey State Location
Create your review survey at `.agent-work/issue-99/crew-handoffs/g1-review/review.json` — deliberately co-located with this handoff and your result (departure from the template's default `<gate>-review/` root path, per lesson `reviewer-handoff-survey-result-paths-split`: one gate directory holds all of a gate's review artifacts).

## What Was Implemented
Design-it-twice generalization: (1) NEW shared fill-in contract `skills/_shared/design-it-twice-brief.md`; (2) new `## Design-it-twice (standard, not optional)` doctrine section in `skills/_shared/global-orchestrator.md`, symmetric with the critical-review section, plus a competitive-critic opt-in bullet added to the critical-review section; (3) commander `SKILL.md` Mission frame paragraph superseding the epic-only critic sentence with a pointer paragraph; (4) `COMMANDER_SPINE.template.json` plan task imperative extension + new `check:null` postcondition `c4`; (5) one-line installer addition (`design-it-twice-brief.md` in `_GLOBAL_ORCHESTRATOR`).

## How to Inspect the Diff
Uncommitted working tree on branch `constellation/issue-99` (nothing committed yet). Use `git status --porcelain` then `git diff` — NOT `git diff --name-only` alone: the new brief is **untracked** and appears only in `git status` (`?? skills/_shared/design-it-twice-brief.md`); `git diff main` shows the other four. This is expected, not a missing deliverable.

## Task Statement
Full implementer handoff at `.agent-work/issue-99/crew-handoffs/g1-implement/IMPLEMENTER_HANDOFF.md` (read it — it is the contract). Summary: generalize design-it-twice into shared doctrine symmetric with the critical-review standard; norm in doctrine, mechanism in the shared brief, pointer in commander SKILL.md; encode human rulings q1/q2/q2b faithfully; add spine c4; ship path via installer tuple.

## Close Criteria (each becomes a review check)
1. **Symmetry read (side-by-side):** the new design-it-twice section vs the critical-review section — structure, register (dense, departures-only, bolded lead-ins), weight scaling, human-only authority, ends on a reusable-contract pointer. Not a mechanical grep — read both.
2. **Ruling fidelity:** verify the ruling-traceability table in IMPLEMENTER_RESULT.md against the actual text (not memory): q1 bias-to-yes + named untaken roads surfaced at approval; q2 critic reads candidate plan + mission frame only, human disposes every finding; q2b panel preferred / single only for fairly-easy / choice surfaced.
3. **COMPETITIVE-CRITIC EROSION GUARD (named focus):** the option's text must preserve human-only triage — competition modulates critic effort only; critics never self-triage; the human disposes every finding. The tension vs never-bias-the-reviewer must be stated, not implied.
4. **Commander SKILL.md internal consistency:** the old epic-only critic sentence must not survive in contradiction; the Mission frame section reads coherently; the paragraph points at doctrine/brief rather than restating rules.
5. **The brief is a genuine spin-out:** covers the excursion type's contract (distinct-constraint parallel agents, axes depth/locality/seam/testability, recommendation-never-menu) plus the three new fields (not-a-proposal framing block, untaken-road record, panel-vs-single record); usable by explorer (design-phase), commander (plan-phase), admiral alike; register matches EXCURSION_BRIEF/CRITIC_HANDOFF.
6. **Spine c4 + JSON:** plan task carries `c4` (`check:null`) covering alternatives-or-loud-skip + critic + surfaced panel choice; imperative names the brief; JSON valid; NO other task or freeze/amend semantics touched.
7. **Scope + non-goals:** diff confined to the five owned files (4 modified + 1 untracked new); no explorer files, no engine/schema change, no per-skill `references/` mirror edits, installer change is the one tuple line only; `--dry-run` passes.

## Allowed Scope (what the implementation was permitted to touch)
`skills/_shared/design-it-twice-brief.md` (new), `skills/_shared/global-orchestrator.md`, `skills/commander/SKILL.md`, `skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/install_constellation.py` (one tuple line).

## Specific Exclusions (flag if touched)
`skills/explorer/**` (owned by gate g2 of this run); per-skill `references/` mirrors; `scripts/checklist_engine.py` / schema docs; any other installer logic.

## Constraints the Implementation Must Respect
- Doctrine register: dense, agent-facing, departures-only.
- Human-only convergence/triage; competitive mode modulates effort, never disposition.
- Layering ruling: norm in doctrine, mechanism in brief, pointer in SKILL.md — flag any rule restated across layers (drift risk) as a finding.
- `execute.json` freeze/amend semantics unchanged.

## Map Anchors (inbound)
- **Structural:** `skills/_shared/global-orchestrator.md` (critical-review section = symmetry model); commander SKILL.md Mission frame; spine `plan` task; installer `_GLOBAL_ORCHESTRATOR` tuple.
- **Capability:** shared orchestrator doctrine baseline; Commander per-issue planning; installer reference bundling.
- **Constraints/assumptions:** as Constraints above.
- **Decision anchors:** shared spun-out contract (human ruling); c4 kept despite critical-review plan-task asymmetry — already a queued triage candidate; do NOT re-derive it as a new blocker, but flag any NEW asymmetry you find.
- **Evidence expectations:** the frozen invariant chain (in the implementer handoff's Verification Commands) must exit 0 in your hands too — re-run it.
- **Map confidence flags:** none.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/issue-99/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`: invariant chain green (`G1-INVARIANT-GREEN`), diff scope exact, ruling-traceability table, installer dry-run pass. Your REVIEW_RESULT becomes the `review-result` evidence artifact matched by `g1-integrate.c2` (requires `verdict: APPROVE` to advance).

## Suggested Model Tier
Stronger — doctrine wording governs every future run; the review is judgment-heavy (symmetry, register, fidelity), not mechanical.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Write REVIEW_RESULT to `.agent-work/issue-99/crew-handoffs/g1-review/REVIEW_RESULT.md`: verdict (APPROVE or BLOCK), per-check findings (one per Close Criterion, pass/fail + note), blockers, out-of-scope observations, workflow feedback. The result file IS the deliverable signal — write it before ending.
