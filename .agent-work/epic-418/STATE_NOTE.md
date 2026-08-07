# Crash-resume state note — epic-418

**Wave 1 is nearly closed. #440 is MERGED. #447 is at g4 review. The epic's spec has been
revised, cold-panelled and fully triaged, and is awaiting Tommy's confirm.**

- **step:** `execute` — in progress. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418` · main checkout `C:/Programs/constellation-skills` · local `main` is
  **~30 commits ahead of `origin/main`, UNPUSHED**
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418/spine.json current`
  — then poll `constellation-skills-wt/epic418-h-447` for its g4 verdict and `RETURN.md`
- **pid:** none — Commanders are harness subagents, not detached OS processes
- **expected artifact:** #447's `RETURN.md` with a g4 verdict, then a four-file conflict
  resolution (below), then wave-1 closeout

## In flight

| Issue | State | Notes |
|---|---|---|
| #447 | **g4 review**, lease `g4-reviewer-447` live | g1–g3 approved; g4 implementer done, its four-file prune ratified |
| #440 | **MERGED** at `90f0343` | main green: 1764 passed, 2 skipped, real exit 0 |

## Merging #447 — READ THIS FIRST

Four files conflict, enumerated by command (`comm -12` over
`git diff --name-only cbd9aee...epic-418/h-447-episodes-retirement` and `...HEAD`):

```
scripts/install_constellation.py
skills/admiral/templates/ADMIRAL_SPINE.template.json
skills/commander/templates/COMMANDER_SPINE.template.json
tests/test_install_constellation.py
```

**The dangerous one is not a text conflict.** The iterative-planning merge POPULATED the
`directives` field on the Admiral and Commander spines with wave-transition wiring. On #447's
base (`cbd9aee`) that key exists but is `null`. #447 edits those templates as raw text by
constraint, so an edit written against the null version **merges cleanly and is silently
wrong**. It has been asked to name its edited spans by gate id (not line number) and to flag any
edit that assumed `directives` was empty. Check both before accepting the merge.

## Live defect affecting this session — do not be fooled by it

**The spine rail attributes a DESCENDANT's gate to its ancestor.** #447's crew inherit this
session's id with their own agent ids, so the rail resolves this Admiral onto a spine a
descendant is driving and orders it to work that gate. Eight firings so far, across
`g4-impl-447` and `g4-reviewer-447`. **Never run one.** Two agents in one spine is forbidden and
the lease is live every time.

The three-strike escape hatch cannot save you: `spine_rail.py:897` resets the counter on the
*watched spine's* progress, so a productive descendant resets its ancestor's strikes forever.
The better the descendant works, the more relentless the nudging. Unfiled; belongs with #441/#452.

## Settled — do NOT re-derive

- **`py` is not the test runner** and **`FORCE_COLOR=3` produces false reds for `python` too**
  (#454, fixed and merged). `_COMMON.md` said "Both `py` and `python` work" — the inverse of the
  ruling — and now carries both warnings. Four agents hit the FORCE_COLOR trap in one day.
- **#180 is CLOSED.** The governor's gauge writer is wired only in untracked
  `.claude/settings.local.json`, so it ships nowhere. Tracked project settings wire `spine_rail`
  and not the gauge writer. This is workstream **R** (constellation-readiness), new this session.
- **Multi-spine attribution is #452**, filed. Not unfiled.
- **#422/#329/#328 are OPEN** though D's code merged — tracker and tree disagree.
- Two Commander departures ratified this run (#447's 6→8 rescope, its four-file prune). Both the
  same shape: a frozen artifact's specifics went stale, the agent applied the governing rule and
  said so. Five instances epic-wide. Expect it; it is the mode, not the exception.

## Spec revision — done, awaiting confirm

`.agent-work/epic-418/spec-revision/REVISED_SPEC.md`, 882 lines. Six workstreams re-cut plus new
**R**. Order: **B → A2 → F → C → E**, with A's remainder and D's #436 debt off-chain. Cold panel
of four arms returned 81 findings (12 BLOCKING / 46 MAJOR / 23 MINOR); **all 81 dispositioned**.
Two new lenses were added for this panel — `done-condition fidelity` and `claim accuracy` — and
produced 41 of the 81, including six factual errors in the draft.

Still marked `UNCONFIRMED — DO NOT CUT`. **Confirming it is Tommy's.** Note #428: the
review-phase gate will refuse this document by construction, not for its content — do not
"fix" that by pulling the marker early.

_Updated: 2026-08-07T17:40:00Z_
