# Constellation Feedback — staged (fenced) for 668-instrument-panel

## 2026-07-26 -- f1Brainz -- cmdr-668 (668-instrument-panel)

### Lesson: lesson:engine-artifact-attest (recurrence — standing constellation debt)
Artifact-kind postconditions (`user-decision`, `implementer-result`, `review-result`) still refuse
`attest` and must be satisfied by `attach`; and the same artifact must be attached to BOTH
`gN-review` and `gN-integrate` for the integrate gate's APPROVE-match check to pass. Recurred again
across this entire run (understand/plan/g1-diagnose/g5-f12-signoff/triage/review user-decisions +
implementer-result/review-result at all 5 gates). This is navigated fine by every commander but is
pure friction on every run.

Proposed upstream fix (unchanged from prior exports): either (a) let `attest <gate> --cond <id>
--evidence <existing-id>` satisfy an artifact-kind postcondition by reference (the engine already
verifies the referenced artifact's type + match), removing the "attach to both gates" duplication;
or (b) at minimum, make the refusal message name the attach-to-both-gates recipe so a first-time
driver isn't surprised. NOTE: the 2026-07-24 epic-601 audit flagged that a prior curator
"resolved" claim (2026-07-17) for this lesson may describe a narrower already-shipped improvement
(attest-by-reference via --evidence) rather than eliminating the first-attach requirement -- this
run re-confirms the first-attach-plus-both-gates pattern is STILL required on the installed engine.
Do not mark resolved until verified against the actually-installed `checklist_engine.py`.

### Observation (minor, project-adjacent): reasoning-gate/crew re-verify env split
`src.utils.simplification_limits` needs `radon`, present on the PINNED interpreter but not the bare
`py` launcher. A commander re-verifying a crew's complexity-gate claim must use the same pinned
interpreter the crew used, or it false-fails with a RuntimeError that looks like a gate failure.
This is f1Brainz-specific tooling but the general shape (re-verify with the crew's exact
interpreter, not a sibling one) may be worth a line in crew-dispatch re-verification guidance.
