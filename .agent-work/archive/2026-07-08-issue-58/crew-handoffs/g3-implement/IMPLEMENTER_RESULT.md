# Implementer Result

## Gate
g3 — constellation-prototyper skill (issue-58)

## Completed slice
Authored the constellation-prototyper crew-tier skill in full: doctrine SKILL.md, three branch references, and the handoff/result template pair. Crew-tier, handoff-driven, no engine checklist or spine (matches the `skills/triage/` exemplar). Committed on `constellation/issue-58` as **b54a1eb**.

## Files changed (six NEW)
- `skills/prototyper/SKILL.md`
- `skills/prototyper/references/logic.md`
- `skills/prototyper/references/ui.md`
- `skills/prototyper/references/measurement.md` (thin pointer)
- `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md`
- `skills/prototyper/templates/PROTOTYPE_RESULT.template.md`

None gitignored (`git check-ignore` → exit 1, none ignored).

## Evidence

### Integrate-gate invariant check
```
$ test -f skills/prototyper/SKILL.md && test -f skills/prototyper/references/measurement.md && test -f skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md && grep -qi 'NOT tested' skills/prototyper/templates/PROTOTYPE_RESULT.template.md && grep -qi 'disposition' skills/prototyper/templates/PROTOTYPE_RESULT.template.md && grep -qi 'scoped' skills/prototyper/SKILL.md && echo INVARIANTS-OK
INVARIANTS-OK
```
- `NOT tested` present in PROTOTYPE_RESULT.template.md (literal phrase, in the mandatory scoped-nulls field).
- `disposition` present in PROTOTYPE_RESULT.template.md (mandatory closeout field, values `deleted | absorbed | parked-with-owner`).
- `scoped` present in SKILL.md (the "## Scoped nulls" doctrine passage).

### Full suite — `python -m pytest tests/ -q`
Result: **31 failed, 389 passed, 1 skipped, 14 subtests passed**.

Failure distribution by file (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`):
```
      5 FAILED tests/test_feedback_tooling.py
     26 FAILED tests/test_install_constellation.py
```

Root-cause attribution (`grep '^E ' | sed 's/[0-9]//g' | sort | uniq -c`) — a SINGLE signature across all 31:
```
     31 E       SystemExit:
     31 E               install_constellation.InstallError: source skill is missing SKILL.md: C:\...\skills\explorer
```

**All 31 failures = waived root-cause class 1 (missing `skills/explorer/SKILL.md`, g4).** The installer auto-discovers `skills/explorer/` (dir present, SKILL.md absent) and aborts at discovery time, which crashes every test that runs an install. This install-discovery abort happens *before* any expected-skills-list assertion executes, so waived class 2 (expected-skills drift now that `constellation-prototyper` exists — g5) is currently **masked, not yet observable**; it will surface once g4 lands the explorer SKILL.md. Both classes are covered by the g2 human waiver (scoped by root cause, through g5).

**No failure falls outside the two waived classes. No stop condition hit.** Baseline (pre-g3) failure count for the missing-explorer class was already present per the handoff; adding prototyper introduced zero new distinct signatures.

## Enumerated PROTOTYPE_HANDOFF field list (downstream contract for g4)
g4's `EXCURSION_BRIEF.template.md` prototype section must carry an identical field set. The fields, cleanly enumerable (one heading/bullet each, no prose-buried fields):

1. **Question** (heading `## Question`) — the ONE named design question.
2. **Branch** (heading `## Branch`) — value ∈ `logic | ui | measurement`; plus a **Why this branch** one-liner.
3. **Host-project conventions** (heading `## Host-project conventions`) — four bullets: Runtime/language; Task runner; Routing (ui-only, else n/a); Other conventions.
4. **Location** (heading `## Location`) — value ∈ `in-repo | worktree`; plus a **Driver** line (human-driven→in-repo / agent-driven→worktree).
5. **Stop conditions** (heading `## Stop conditions`) — bullets: what "answered" looks like; budget; exclusions.
6. **Return format** (heading `## Return format`) — names `PROTOTYPE_RESULT`.

(PROTOTYPE_RESULT fields, for completeness: Question; Answer; What was tested AND what was NOT tested [Tested / NOT tested / Next variant]; What it taught beyond the question; Surviving pure module; Disposition [`deleted | absorbed | parked-with-owner`] + Detail; One command to run.)

## Assumptions used
- **measurement.md pointer target.** The shared spike/scoreboard doctrine lives only in `skills/_shared/global-orchestrator.md` (decomposition/sequencing section; grep confirmed it is absent from `global-crew.md`). Since prototyper is crew-tier it installs `global-crew.md`, not the orchestrator doctrine — so the pointer cites the source file by path AND notes the dispatching orchestrator (explorer/Commander) already holds it as its installed `references/global-orchestrator.md`. This keeps the file a genuine pointer (no restatement) while being honest that the crew skill does not itself bundle that doctrine.
- **Frontmatter.** Sibling crew SKILL.md files (triage, implementer, reviewer) use only `name` + `description`. Followed that exactly; `name: constellation-prototyper`.
- **In-repo prototype marker.** Spec/handoff say "clearly marked" without prescribing a convention; SKILL.md gives `*.prototype.*` / marked-route as examples, not a mandate.

## Stop conditions hit
None.

## Out-of-scope observations
- The install-discovery abort on a skill directory that lacks SKILL.md is a hard crash of the *entire* install (not a skip). Once g2/g4 land `skills/explorer/SKILL.md` the 31 failures should clear and the g5 expected-skills-list drift (class 2) will become the observable frontier. Flagging only so g3-integrate reads the single-signature distribution correctly — it is expected, not new breakage.
- Did NOT touch `skills/_shared/**` (g5 owns the vocabulary addition), so the deep-module vocabulary the SKILL.md leans on ("adapter", "seam", "deep by construction") is not yet in `global-crew.md`. The SKILL.md uses those terms lightly and self-containedly; when g5 adds the vocabulary section the prototyper's language will align without edits. No action needed this gate.

## Workflow feedback (run-specific)
The handoff's insistence on deriving the failure distribution via `grep '^E '` signature-counting (not a tail glance) paid off concretely here: the tail of the run showed a *mix* of `test_feedback_tooling` and `test_install_constellation` failures that could look like two independent problems, but the signature count proved all 31 collapse to one root cause (missing explorer SKILL.md). Without that step I might have mis-reported class 2 as already active — it is in fact masked by the class-1 install abort. Concrete suggestion for g3-integrate's handoff: state explicitly that class 2 (expected-skills drift) will be **masked until g4 lands**, so the integrator does not treat its absence-from-the-distribution as evidence the prototyper was somehow skipped by discovery. The one-signature result is the correct, expected state at g3, not a sign class 2 was mis-scoped.
