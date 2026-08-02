# Constellation Feedback (staged) — 662-segment-map (2026-07-25)

Staged upstream-queue exports for constellation-scope recurrence-debt lessons re-observed this run. The
Admiral harvests these into the shared `.agent-work/CONSTELLATION_FEEDBACK.md` at epic closeout (carrying
each entry's `Lesson:` id so the upstream sweep groups recurrences on stable identity).

---

## 2026-07-25 — f1Brainz — cmdr-662 (662-segment-map)
Lesson: lesson:engine-artifact-attest

**Recurrence (19th unfixed).** Every artifact-checked postcondition in the commander spine + execute.json
was satisfied by `attach`, never `attest` — user-decision at understand/plan/triage/review, and
implementer-result/review-result attached to BOTH `gN-review` and `gN-integrate` (the integrate gate's
`review-result{match:APPROVE}` check needs the artifact present on the integrate task) across g1–g6 + the
g3 re-review. `attest` was correct only for `check:null` conditions. The attach-required mechanism is
unchanged.
**Upstream fix proposal:** either (a) let `gN-integrate`'s artifact check resolve a matching
`review-result` already attached to the sibling `gN-review` in the same gate group (so it need not be
re-attached), or (b) have the engine's `attest` refusal on an artifact check emit the exact `attach`
command to run. Until then this logs debt on every commander run.

---

## 2026-07-25 — f1Brainz — cmdr-662 (662-segment-map)
Lesson: lesson:from-child-refuses-on-gated-checklist

**Recurrence (1st, on the exact spine step it predicted).** At the spine `execute` step, whose
`child_checklist` is the GATED `execute.json`, `advance execute --from-child` is the wrong tool
(`--from-child` reads a survey child's `consolidation`, which a gated child never populates). Navigated
correctly by `attest execute --cond c1` directly once execute.json reported DONE — but only because this
lesson was in the playbook. A fresh commander without it would hit the same surprise.
**Upstream fix proposal (unchanged from 624-phase0's export):** the COMMANDER_SPINE template's `execute`
imperative should say "do NOT use `--from-child` for a gated child_checklist; attest c1 directly once the
child is DONE," or the engine's `--from-child` refusal on a gated child should hint at the survey-only
restriction. This run is the first re-observation confirming it recurs on the standard spine shape.

---

## 2026-07-25 — f1Brainz — cmdr-662 (662-segment-map)
Lesson: lesson:crew-idle-strands-deliverable

**Recurrence (5th).** The resumed g3-rework implementer applied the code fix, added the catching test,
and went 18/18 green — but STRANDED on rewriting its `IMPLEMENTER_RESULT.md` (the deliverable was done;
only the echo was missing). Because the commander's completion-waiter was keyed to the result-md mtime,
it never fired, and the run looked idle until the commander ground-truthed from the artifacts (code diff
+ new test + green suite) and appended the rework note itself. Distinct wrinkle vs prior sightings: a
RESUMED (SendMessage-continued) crew stranded on the result-write specifically at the END of an otherwise
complete rework.
**Upstream fix proposal:** a commander's crew-completion waiter should key on the actual deliverable
signal (changed source files + green targeted suite), not solely the result-md freshness, since the crew
routinely finishes the work but strands the md echo. Alternatively, `run_crew.py --verify-result` could
accept a "deliverable-present" mode (source+tests changed) as an alternative freshness signal to the
result artifact alone.
