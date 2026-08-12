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

**Open scope decision, and it is the human's:** whether the epic continues into F (#424), C (#421) and E (#423), or
closes at A2. Nothing else is blocked on anyone.

**What the epic now knows that it did not:** the check-that-cannot-fail defect is not an anecdote, it is a base rate.
Eleven specimens were found in a single wave, by five different actors, all of whom knew the wave was about that
defect -- and the ones the Admiral found all sit in the machinery that judges other work.
