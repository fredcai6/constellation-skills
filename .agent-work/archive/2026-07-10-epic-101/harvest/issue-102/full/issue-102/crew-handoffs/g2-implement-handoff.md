# Implementer Handoff

Concise fragments.

## Gate
g2-implement (issue #102, Move 2 — engine-invocation string)

## Task
Single-source the **generic engine-invocation string** (the drifted "drive X through the engine one
step at a time" statement) so it lives once, with the canonical engine MECHANISM detail referenced
from `skills/workbench/references/checklist-engine.md` rather than re-explained per skill.

IMPORTANT reconcile context (verify, don't just trust): Move 1 (already merged) consolidated the
compliance boilerplate — whose sentence WAS "drive its workflow to completion through the engine and
dispatch each step it names" — into `skills/_shared/global-everyone.md` §"Engine-drive compliance".
So the GENERIC engine-invocation clause may already be single-sourced. Your FIRST step determines
what generic duplication actually remains.

## FIRST STEP (required) — command-derived residual survey
Grep the current tree (post-move-1) for engine-invocation strings and CLASSIFY each hit:
`grep -rn "through the engine\|one step at a time\|drive the gated\|drive a controller\|gate by gate" skills/*/SKILL.md`
For each hit decide: (a) GENERIC duplicate of "how you invoke the engine" → consolidate; or
(b) ROLE-SPECIFIC workflow instruction (names that role's OWN spine template + its own steps, e.g.
commander's 10-step spine, explorer's instantiate-at-init) → KEEP local, it is not drift; or
(c) the canonical mechanism source (workbench, which already points at checklist-engine.md) → leave.
Paste the command + output + your classification as the before-state.

## Expected honest outcome (either is a COMPLETE deliverable)
- If a genuine GENERIC engine-invocation duplicate survives outside role-specific contexts:
  consolidate it into global-everyone.md (point at checklist-engine.md for the mechanism), carriers
  keep a pointer. Per-move before/after grep.
- If move 1 already subsumed the generic clause (likely): report Move 2 as SUBSTANTIALLY SUBSUMED by
  Move 1 with grep proof, and make the NARROW completing edit — add to global-everyone.md's
  "Engine-drive compliance" section a one-clause pointer that the canonical engine MECHANISM lives in
  the workbench engine reference (`references/checklist-engine.md`), honoring the ruling "canonical
  detail already in workbench references/checklist-engine.md". This is an honest-null-flavored partial,
  NOT a failure — report it with full rigor.

Do NOT force-merge role-specific spine instructions (commander/explorer naming their own templates and
steps) into global-everyone — that would delete real role-specific workflow content (semantic loss).

## Protected Intent
Doctrine lives once; the engine mechanism is explained once (in checklist-engine.md) and pointed at,
not re-explained. Role-specific workflow instructions stay where they belong.

## Test Mode
Inspection-only; suite stays green (`py -m pytest tests/ -q`). g7 adds content-pin/residual later.

## Close Criteria
- global-everyone.md's engine-drive doctrine points at the canonical engine mechanism
  (checklist-engine.md) exactly once; no new global-*.md filename.
- Any genuine generic engine-invocation duplicate is consolidated with carrier pointers; OR the
  subsumed-by-move-1 finding is reported with grep proof.
- Role-specific spine instructions preserved (commander/explorer untouched in substance).
- Before/after grep (command + output) pasted; classification recorded.
- Full suite green.

## Allowed Scope
skills/_shared/global-everyone.md; any carrier SKILL.md that proves to hold a genuine generic
duplicate. Do NOT rewrite commander's/explorer's role-specific spine sections beyond adding a pointer.

## Specific Exclusions
Banners (g3), prototyper, manifest.json/ROADMAP/repo-root stray (#105), the compliance paragraph
(g1, done). Do not re-open move 1's carriers except to add a pointer if genuinely needed.

## Constraints
- Append into existing global-everyone.md only; never a new global-*.md filename.
- Point at checklist-engine.md for mechanism; do not duplicate its content.
- Register: dense, agent-facing.

## Map Anchors (inbound)
- Structural: global-everyone.md; workbench/references/checklist-engine.md; commander/explorer SKILL.md.
- Constraint: bundle glob stays green.
- Decision: engine-invocation generic string -> global-everyone; mechanism stays in checklist-engine.md.

## Deliverable Path Check
- Committed — skills/_shared/global-everyone.md (+ any carrier touched); not gitignore (exit 1).
- Local-only — .agent-work/issue-102/crew-handoffs/g2-implement-result.md (.agent-work gitignored).

## Required Evidence
Before/after grep with classification; quote of the added pointer; suite tail.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rn "through the engine\|one step at a time\|drive the gated\|drive a controller" skills/*/SKILL.md
grep -n "checklist-engine" skills/_shared/global-everyone.md
py -m pytest tests/ -q
```

## Suggested Model Tier
stronger — reconcile judgment (drift vs role-specific) is the crux here.

## Authority
Destination (global-everyone) + mechanism home (checklist-engine.md) ruled. You decide whether a hit
is generic-duplicate vs role-specific, and the pointer wording. Report subsumption honestly if that
is what the grep shows — do not manufacture a consolidation that would delete role-specific content.

## Stop Conditions
Stop and return if consolidating would require deleting role-specific spine instructions, or if the
grep contradicts the subsumed-by-move-1 reading in a way that needs a scope decision.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g2-implement-result.md AND as
your final message): completed slice (consolidation OR subsumption finding), files changed, grep
evidence + classification, added-pointer quote, suite tail, assumptions, stop conditions, out-of-scope
observations, workflow feedback. Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT.
