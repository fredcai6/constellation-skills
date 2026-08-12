## Current planning truth -- after wave 4

**A2 is complete.** #467 is merged (PR #505, `c875ee23`) and closed; #431 is verified dissolved and closed. Main is
green at 1867 passed / 2 skipped / 829 subtests / real exit 0 on the final merged tree.

**What shipped.** A HARD context reading changes the instruction instead of refusing the verb:
`TRIP_HARD_GUARDED_VERBS = {start, reopen}`, a concrete `why_ref` in place of the `<why-id>` placeholder, an
append-only trip ledger for BEGINs over the line, and an unkeyed historical selector plus a `TRIP HISTORY` line so
the record survives the close the band orders. The glossary no longer claims HARD blocks `advance`, and the fourth
limit is declared in `CHECKLIST_SCHEMA.md` alongside the other three.

**Done-conditions:** DC1, DC3, DC4, DC5 done. DC2 **done by different means** -- the engine draws the line between
verbs, not between two modes of `advance`, so the done-condition's literal text names a distinction the engine does
not have. DC6 **partial** -- both lines were observed live and the historical line survives the mandated close, but
#504 stands: once no gate is active, both go silent at closeout.

**New follow-on cluster, all found while doing something else:** #500 (a refresh-request has no served state and the
compliant handoff erases its own signal), #501 (the wave-launch gate cannot run as the spine instructs -- its guard
accepts the repo because the repo is named `constellation-skills`), #502 (no provenance record names the engine build
that produced a gate, with four builds live), #503 (`--authority` is validated only as non-empty, so human
ratification is enforced by nothing), #504 (the ledger goes silent at closeout).

**Scope decision: SETTLED at the wave-4 checkpoint, 2026-08-08.** The epic runs **one more wave**, then
closes. F (#424), C (#421) and E (#423) become their own efforts afterwards. The decision was taken against a
score of the epic's own five done-conditions rather than against the wave list: **DC3 met; DC2 substantially
met; DC1 mechanism done but shipping not** -- every governor reading this epic ever took came from an untracked
`.claude/settings.local.json` -- **DC4 and DC5 untouched.**

**Wave 5 -- five dispatches, 21 issues, ~8 real fixes.** It buys DC1 and DC2 outright and hands F a
launch/archive gate surface that works instead of three broken gates and a waiver.

| Crew | Issues | Fixes |
|---|---|---|
| 1 -- bookend gates (Opus) | #506, #501+#468, #439+#484+#446 | 3 |
| 2 -- readiness, workstream R (Sonnet) | #458 | 1 |
| 3 -- crew addressing (Sonnet) | #507+#370+#413 | 1 |
| 4 -- `checklist_engine.py` internals (Sonnet) | #474 #475 #476 #479 #480 #427 #503 #493 #495 | ~9 |
| 5 -- docs (Sonnet) | #496+#411 | 2 |

**Three duplicate collapses account for eight of the 21, and none of them is visible from the issue titles.**
#501 and #468 name the same function and line. #439, #484 and #446 are all the same postcondition,
`archive.c2b`. #507, #370 and #413 are one defect filed across three epics. Each was confirmed by reading the
body; a title-level sweep would have missed all three, which is itself a finding parked for E.

**The dogfood dependency, stated up front:** #506's fix is what lets this epic close its own `execute` gate
without a waiver against the human's name. That is a knowingly accepted single point of failure, and it is
**not** a reason for crew 1 to report #506 done when it is not.

**Why E cannot simply be run now.** E is specified to consume "what survives the redux", so its input is
undefined while the redux is still running. 117 issues were open when the spec was written and 156 are open
today -- which the spec predicted and accepted when it retired the issue-count done-condition. Wave 5 is the
last thing that changes E's input.

**What the epic now knows that it did not:** the check-that-cannot-fail defect is not an anecdote, it is a base rate.
Eleven specimens were found in a single wave, by five different actors, all of whom knew the wave was about that
defect -- and the ones the Admiral found all sit in the machinery that judges other work.
