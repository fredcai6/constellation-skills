<!-- episode-state: schema=1 id=tc1-worktree-identity-004 status=active -->

# episode: tc1-worktree-identity-004

## Mechanical
- run: tc1-worktree-identity
- project: constellation-skills
- role: commander
- spine-step: context
- context-manifest-ref: tc1-worktree-identity-context@453f8492
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: map/INDEX.md
- artifact-ref: map/ids.jsonl

## Agent-supplied

### assertion:tc1-worktree-identity-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Resolve the map-first orientation input at the context step via `scripts/map_orient.py orient`, before reading any source file.

### assertion:tc1-worktree-identity-004.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: map_orient.py would either resolve a docs/architecture packet map, or clearly report none exists so a substitute could be declared.

### assertion:tc1-worktree-identity-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: map_orient.py reported DEGRADED-UNPARSEABLE against this repo's own map/INDEX.md, even though that file is a real, current, useful module index (regenerated via `python -m scripts.code_map build`, listing the exact two modules this run touched). The tool's probe order treats map/INDEX.md as a candidate but rejects its content as carrying 'no citable anchor id' -- it is built for a docs/architecture packet-map's anchor-id format, which this skill-source repo's own code_map output does not use. map/ids.jsonl is also legitimately empty repo-wide (0 decision anchors exist anywhere in this repo yet), which is a separate, correct fact rather than a defect.

### assertion:tc1-worktree-identity-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra command-line round-trip (re-running orient with --substitute/--unmapped/--escalation) to discharge the degraded read before any source read, plus the same declaration repeated at the plan step's c6 gate (waived) -- no wrong output, just process overhead for a gap that will recur on every future run in this repo until it has either a packet map or a map_orient probe that recognizes code_map's own format.

### assertion:tc1-worktree-identity-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Declared map/INDEX.md as the substitute with a content hash, stated the unmapped gap (no packet-map anchor format), and stated no escalation was needed since the LAUNCH_ORDER already named the exact files in scope.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
