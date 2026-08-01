# IMPLEMENTER_RESULT — g1-implement (issue #102, cluster A, Move 1)

## Completed slice
Single-sourced the mandatory-compliance / engine-drive boilerplate into `skills/_shared/global-everyone.md`
as ONE canonical rule generalized over spine/checklist/survey, and replaced each of the 10 carriers' inline
copy with a one-line pointer. Doctrine now lives once and patches once; a reader of any carrier still learns
the rule via the pointer.

## Files changed (11)
- `skills/_shared/global-everyone.md` — new `## Engine-drive compliance` subsection (canonical rule), inserted
  after the "Agent-facing. Dense by design." line, before `## Engine verbs`. Plain dense statement (no bold —
  register rule: emphasis only at mechanism-backed gates).
- 10 carriers, inline paragraph → one-line pointer: `admiral`, `cartographer`, `charter`, `commander`,
  `implementer`, `interrogator`, `lessons-auditor`, `reviewer`, `scout`, `workbench` (`skills/<name>/SKILL.md`).

## Test mode satisfied
Inspection-only prose move (no runtime surface). Full structural suite stays green — see tail below. The g7
gate owns the later content-pin/residual tests; not done here.

## Before/after grep evidence (drift-robust stem over `skills/*/SKILL.md`)

BEFORE (command + output):
```
$ grep -rli "reporting misfit is compliance" skills/*/SKILL.md
skills/admiral/SKILL.md
skills/cartographer/SKILL.md
skills/charter/SKILL.md
skills/commander/SKILL.md
skills/implementer/SKILL.md
skills/interrogator/SKILL.md
skills/lessons-auditor/SKILL.md
skills/reviewer/SKILL.md
skills/scout/SKILL.md
skills/workbench/SKILL.md          # 10 carriers

$ grep -rln "Mandatory, no exceptions" skills/*/SKILL.md
(same 10 minus commander = 9 — commander's stem reads "This is mandatory, no exceptions"; cross-checked and
 confirmed commander is the 10th carrier via the "reporting misfit is compliance" stem)
```
Grep set matched the Commander-confirmed 10-carrier list exactly. No delta. prototyper NOT matched (different
doctrine) — left untouched as instructed.

AFTER (command + output):
```
$ grep -rli "reporting misfit is compliance" skills/*/SKILL.md   ; exit=1 (no matches — full para gone)
$ grep -rln "Mandatory, no exceptions" skills/*/SKILL.md         ; exit=1 (no matches in carriers)
$ grep -c "Mandatory, no exceptions\|reporting misfit is compliance" skills/_shared/global-everyone.md
2   (both stems present, in the single canonical paragraph — rule now lives once)
$ grep -rl "Compliance/engine-drive rule: inherited" skills/*/SKILL.md | wc -l
10  (all 10 carriers now carry the pointer)
```
Carrier count: before = 10 with the inline paragraph; after = 0 with the full paragraph (pointers only). The
rule now lives in `global-everyone.md` (1).

## Canonical text (in `skills/_shared/global-everyone.md`)
```
## Engine-drive compliance

Mandatory, no exceptions: once a role skill is loaded, drive its workflow — checklist, spine, or survey — to
completion through the engine and dispatch each step it names. Within a step (question, check), judgment is
yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit at your
workflow's reporting step (closeout, feedback step, or workflow feedback); reporting misfit is compliance, not
deviation.
```
Reconciles the drift dimensions into one wording: workflow noun (spine/checklist/survey), unit
(step/question/check), and reporting location (closeout / feedback step / workflow feedback).

## Representative pointer (before → after)

cartographer (plain, no role tail):
- before: `Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — ... reporting misfit is compliance, not deviation.`
- after:  `Compliance/engine-drive rule: inherited — see \`references/global-everyone.md\`.`

commander (kept genuine role-specific tail):
- after: `When this skill is loaded you own the run: drive every spine step through the engine and dispatch each role. Compliance/engine-drive rule: inherited — see \`references/global-everyone.md\`. Role-specific: you never do another role's work yourself, and you surface the misfit at the feedback step.`

Role-specific tails preserved only where genuinely carrying non-generic info:
- commander: "you never do another role's work yourself" (orchestrator-only doctrine) + feedback-step reporting.
- admiral: report at closeout; implementer/reviewer: report in workflow feedback (kept as short parentheticals
  so each role's own reporting step is named at the point of use — the canonical rule already generalizes it).
- workbench: parenthetical "it binds every role whose checklist Workbench drives" (workbench's original was
  third-person because it drives OTHER roles' checklists; the note preserves that framing).

## Test result (`py -m pytest tests/ -q`, tail)
```
442 passed, 2 skipped, 26 subtests passed in 12.93s
```

## Assumptions
- Pointers name `references/global-everyone.md` (the installed/bundled path each role loads), matching the
  existing in-carrier convention (charter/commander/scout already cite `references/global-everyone.md`), not the
  source path `skills/_shared/global-everyone.md`. Consistent with the handoff's pointer example.
- Canonical inserted as its own `## Engine-drive compliance` section (first behavioral rule, before
  `## Engine verbs`) — no new `global-*.md` file created; appended into the existing file only, as constrained.
- Canonical left un-bolded per the register rule ("emphasis only at mechanism-backed gates"). Note: 5 of the 10
  carriers had bolded the inline paragraph and 5 had not — drift I collapsed to the plain canonical statement.

## Stop conditions hit
None. No boilerplate was entangled with inseparable role-specific rules (commander's separable tail was cleanly
lifted). Grep set matched the 10-carrier list with zero delta. Suite stayed green.

## Out-of-scope observations (triage candidates / fenced per handoff)
- The `**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**` banners remain in carriers (admiral notably
  has NO such banner) — g3's move; left untouched.
- Engine-invocation operational strings ("Drive `templates/X.template.json` ... through the absolute path to
  this installed skill's bundled engine `scripts/checklist_engine.py`") are repeated per carrier with drift —
  that is g2's move. It was a SEPARATE sentence from the compliance paragraph in every carrier, so no overlap to
  flag for g2; the cut was clean.
- `skills/workbench/SKILL.md` line 3 has a typo "managemetn" (→ "management"), adjacent to my edit but not mine
  to fix here — hygiene, issue #105.

## Map Impact
- Structural: `skills/_shared/global-everyone.md` gains the canonical compliance rule (one new subsection);
  the 10 carrier SKILL.md files each shed the inline paragraph for a pointer. No change to
  install_constellation.py bundling — global-everyone.md is already bundled to each skill's `references/`.
- Capability: unchanged — every role still loads global-everyone.md at its context-read step, so the rule
  reaches all; the reach is now via pointer instead of inline duplication.
- Constraint: `test_install_constellation.py:196-208` bundle glob unaffected (file path unchanged) — suite green.
- Decision: cross-tier compliance rule consolidated to global-everyone (launch-order pre-ruling honored).

## Workflow Feedback
- Handoff was strong: the drift-robust FIRST-STEP grep instruction and the explicit 10-carrier list made the
  before-count unambiguous, and calling out the `grep -rln "Mandatory, no exceptions"` cross-check pre-warned me
  that commander's stem differs ("This is mandatory, no exceptions") — without that note the 9-vs-10 mismatch
  would have read as a delta. Good pre-emption.
- Minor ambiguity: "keeping a genuine role-specific tail only where one exists" left the admiral/implementer/
  reviewer reporting-location specifics (closeout / workflow feedback) as a judgment call — the canonical rule
  already generalizes them, so they are arguably redundant. I kept them as terse parentheticals to preserve the
  point-of-use reporting-step name; a reviewer may prefer bare pointers there. Flagging the call, not a blocker.
- The pointer-path convention (`references/` vs `skills/_shared/`) was implied by the example but not stated as
  a rule; I inferred from existing carrier usage. A one-line "pointers use the installed `references/` path"
  note in future handoffs would remove the inference.
