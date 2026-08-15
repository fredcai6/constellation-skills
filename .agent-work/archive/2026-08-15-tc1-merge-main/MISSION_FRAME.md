# Mission Frame

Shrunk per template guidance: this is a trivial, mechanical change with a single fixed
procedure fully specified by `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`, and the map is
unavailable for this run (context step returned DEGRADED-UNPARSEABLE — see
`.agent-work/tc1-merge-main/map-orientation.json`). This frame is built from the two
substitutes that receipt hash-pinned: `.agent-work/tc1-merge-main/LAUNCH_ORDER.md` and
`docs/agents/ORCHESTRATOR_CONTEXT.md`.

## Intent
Per `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`: merge `origin/main` into
`tc1/worktree-identity`, resolve the single expected conflict in the generated file
`map/INDEX.md` by regenerating it (never hand-editing), run the full clean-env suite to
green, push, and confirm PR #588 is no longer `CONFLICTING`. No source code, tests, or
episode content are touched — this run's only originated diff is the merge commit and the
regenerated map.

## Affected Capabilities
None in the ordinary sense — this is a git-hygiene operation (merge + regenerate a
generated artifact), not a behavior change to any capability. Not applicable per
`docs/agents/ORCHESTRATOR_CONTEXT.md`'s subsystem table either: this run touches neither
"workflow mechanisms and verifiers" nor "post-job feedback" as a behavior change.

## Examples / Events
Not applicable.

## Structural Anchors
Not applicable — the map is DEGRADED-UNPARSEABLE for this repo state; the code map files
are themselves the regeneration target of this run, not a readable input.

## Governing Constraints / Assumptions
Fully stated in `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`'s "File Ownership" and
"Pre-Rulings" sections: a closed set of files this run must not originate edits to, and
three settled rulings (merge main now; regenerate the generated map rather than
hand-merging it; #588's substantive content is finished and not to be revisited).

## Decision Anchors & Decision Pressure
All three governing decisions are pre-ruled settled in
`.agent-work/tc1-merge-main/LAUNCH_ORDER.md` ("Pre-Rulings — settled"); none are this run's
to make, and none are open pressure. No new decision is forced by this run.

## Claims / Evidence Surfaces
Two claims from `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`, both this run re-confirms
live rather than takes on faith: exactly one file (the generated map) conflicts on merge,
and the suite's own code-map freshness check is what proves a regeneration correct.

## Map Confidence / Staleness / Disputes
Map is DEGRADED-UNPARSEABLE for the whole repo at this run's starting commit (not just the
affected area) — see `.agent-work/tc1-merge-main/map-orientation.json`. This is expected:
regenerating the map is this run's own deliverable, not a precondition readable in advance.
No scout/verify step is warranted; the suite is the check that the regenerated map is
correct.

## Out of Scope
- Any edit to files under `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`'s File Ownership fence.
- Revisiting the predicate, call site, assertions, or episode wording #588 already settled.
- Merging PR #588 itself — fenced to the Admiral per `.agent-work/tc1-merge-main/LAUNCH_ORDER.md`.
