# Implementer Handoff

Concise fragments. Omit filler.

## Gate
g1-implement (issue #102, cluster A, Move 1)

## Task
Single-source the **mandatory-compliance boilerplate** into `skills/_shared/global-everyone.md`,
then replace each carrier's inline copy with a one-line pointer. This is the "Mandatory, no
exceptions: once loaded, drive the checklist/spine/survey to completion through the engine and
dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit
the work, do the closest compliant thing and report the misfit; reporting misfit is compliance,
not deviation." paragraph, pasted (with drift) across the carriers below.

## FIRST STEP (required before cutting) — command-derived carrier list
Emit the authoritative before-count from a DRIFT-ROBUST stem, not the pristine string (a drifted
copy won't match an exact grep). Run and paste command + output, e.g.:
`grep -rli "reporting misfit is compliance" skills/*/SKILL.md`  and cross-check with
`grep -rln "Mandatory, no exceptions" skills/*/SKILL.md`.
Commander's confirmed carrier list (10): admiral, cartographer, charter, commander, implementer,
interrogator, lessons-auditor, reviewer, scout, workbench. NOTE prototyper's "mandatory" lines are
DIFFERENT doctrine (disposition-mandatory / NOT-tested-mandatory) — NOT this boilerplate; do not
touch them. Confirm your grep matches this set; if it finds more/fewer, report the delta.

## Protected Intent
Doctrine lives once and patches once; a reader of any carrier still learns the rule via the pointer.
Do not weaken the rule's meaning. The drift (spine vs checklist vs survey; "report the misfit" vs
"in your workflow feedback" vs "at the feedback step") is reconciled into ONE canonical wording;
keep only a genuinely role-specific tail line where one carries real role-specific info.

## Test Mode
Inspection-only for the prose move (no runtime surface); the suite must stay green (structural
tests). The g7 gate adds the content-pin/residual tests later — not your job here.

## Close Criteria
- Canonical boilerplate reads cleanly ONCE in `skills/_shared/global-everyone.md` (new subsection,
  agent-facing dense register matching that file), generalized over spine/checklist/survey.
- Each of the 10 carriers' inline copy replaced by a ONE-LINE pointer naming `global-everyone.md`
  (e.g. "Compliance/engine-drive rule: inherited — see `references/global-everyone.md`."), keeping a
  genuine role-specific tail only where one exists (e.g. commander's "surface at the feedback step").
- No new `global-*.md` filename created; append into the existing file only.
- Before/after carrier-count grep pasted (drift-robust stem over `skills/*/SKILL.md`): before = the
  count of carriers with the inline paragraph; after = 0 carriers with the full paragraph (pointers
  only). The rule now lives in global-everyone.md (1).
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
`skills/_shared/global-everyone.md`; the 10 carrier `skills/<name>/SKILL.md` files listed above.
Nothing else.

## Specific Exclusions
- prototyper/SKILL.md (its "mandatory" lines are different doctrine) — issue #102 does not touch it here.
- The `**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**` banner lines — a SEPARATE move (g3)
  owns those; leave them for now.
- manifest.json, docs/ROADMAP.md, the repo-root stray file — fenced (issue #105 owns hygiene).
- Do not touch the engine-invocation operational string (g2's move) if you can separate it; if a
  carrier's boilerplate and engine-string are the same sentence, cut only the compliance paragraph
  and note the overlap for g2.

## Constraints
- Append into existing `global-everyone.md` only; never a new `global-*.md` filename.
- Each carrier keeps a pointer naming the shared file.
- Match register: agent-facing, rule-plus-why, dense (that file says "Agent-facing. Dense by design.").
- Emphasis only at mechanism-backed gates (register rule) — the canonical rule is a plain dense
  statement, not a shouty banner.

## Map Anchors (inbound)
- **Structural:** skills/_shared/global-everyone.md; the 10 carrier SKILL.md; install_constellation.py:94-113 (bundle).
- **Capability:** every role loads global-everyone.md at its context-read step, so the rule reaches all.
- **Constraints:** test_install_constellation.py:196-208 bundle glob must stay green.
- **Decision:** cross-tier compliance rule -> global-everyone (launch-order pre-ruling).
- **Evidence:** before/after carrier-count grep pasted with command output.

## Deliverable Path Check
- **Committed** — skills/_shared/global-everyone.md and the 10 carrier SKILL.md; verified not-ignored
  (`git check-ignore skills/_shared/global-everyone.md` exits 1). Reviewer inspects these in the diff.
- **Local-only** — .agent-work/issue-102/crew-handoffs/g1-implement-result.md (this result; .agent-work is gitignored).

## Required Evidence
- The drift-robust before/after carrier-count grep (command + output).
- A quoted before/after of the canonical text in global-everyone.md and one representative carrier pointer.
- `py -m pytest tests/ -q` tail (green).

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rli "reporting misfit is compliance" skills/*/SKILL.md   # after: pointers only, full para gone
grep -c "Mandatory, no exceptions\|reporting misfit is compliance" skills/_shared/global-everyone.md  # canonical present
py -m pytest tests/ -q
```

## Suggested Model Tier
stronger — register-sensitive product prose + drift reconciliation across 10 files.

## Authority
Destination (global-everyone) and the 10-carrier list are ruled. You decide canonical wording and
pointer phrasing. Do NOT invent a new destination or delete role-specific info without noting it.

## Stop Conditions
Stop and return if: a carrier's boilerplate is entangled with genuinely role-specific rules you can't
cleanly separate; the grep set disagrees materially with the 10-carrier list; or the suite goes red.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g1-implement-result.md AND
as your final message): completed slice, files changed, test mode satisfied, before/after grep
evidence, canonical + pointer quotes, assumptions, stop conditions hit, out-of-scope observations,
workflow feedback. Your final message MUST be the complete IMPLEMENTER_RESULT before you idle.
