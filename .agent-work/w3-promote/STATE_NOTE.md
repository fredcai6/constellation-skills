# Crash-resume state note — w3-promote

- **step:** execute · gate g9-integrate, final step (g0 through g8 all complete; g1/g3/g4/g5/g7
  committed and integrated — every gate that promotes a check landed, reviewed APPROVE, suite
  green after each commit; g6 and g8 are reasoning gates, both closed with no file edit; g9 is
  commit-remaining-notes, final `python3 -m pytest -q`, open PR, write RESULT.md)
- **slug:** w3-promote · branch epic-569/w3-promote · worktree /home/tommy/projects/569-w3-promote
- **next command:** commit this STATE_NOTE.md + execute.json + notes-1.md + the 3 tracked
  crew-handoff files together, run `python3 -m pytest -q` fresh after that commit, open the PR
  (server-side-merge, do not merge), write `.agent-work/w3-promote/RESULT.md` per the launch
  order's Return Shape, then `advance g9-integrate` to terminal `complete`.
- **pid:** none — foreground
- **expected artifact:** `.agent-work/w3-promote/execute.json` driven to terminal `complete` on
  every task; then `.agent-work/w3-promote/RESULT.md`

_Updated: 2026-08-23T08:20:00-07:00_

## Handoff context for the resuming agent

All promotion gates are closed: g1 (COMMANDER_SPINE, 8/19), g3 (ADMIRAL_SPINE, 3/10), g4
(EXPLORER_SPINE, 3/10), g5 (CHARTER, 1/10), g6 (IMPLEMENTER_PLAN, 0/3, reasoning-only honest-null),
g7 (SCOUT 1/3 promoted + CARTOGRAPHER 0/4, first report-only promotion of the wave), g8
(validate_spine.py wiring — floor confirmed current, no new tightening this wave, floated as
triage). Two real defects were caught and corrected mid-wave: g4's implementer first pass violated
`decision:no-basis-backfill` (caught before review); a g5 reviewer's own `git checkout --` near-miss
reverted the uncommitted file to pre-gate HEAD (self-caught, restored, Commander re-verified
byte-identical). `notes-1.md` carries the full per-template bucket assessment and per-gate outcomes
— read it before re-deriving anything. Only g9 remains: commit the tracked `.agent-work/w3-promote/`
process files, final suite, PR, RESULT.md.
