<!-- episode-state: schema=1 id=cleanup-g-crew-tier-003 status=active -->

# episode: cleanup-g-crew-tier-003

## Mechanical
- run: cleanup-g-crew-tier
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-g-crew-tier/MISSION_FRAME.md
- artifact-ref: .agent-work/cleanup-g-crew-tier/map-orientation.json

## Agent-supplied

### assertion:cleanup-g-crew-tier-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a DEGRADED-mode mission frame (no packet map exists) that would pass map_orient.py verify-frame's anchor-resolution check against the hash-pinned substitute paths declared at the context step.

### assertion:cleanup-g-crew-tier-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The template's own suggested Decision Anchors syntax (e.g. 'decision:md-decision-is-a-list-item -- ...') was assumed safe to use verbatim, since the template itself shows it as the intended format.

### assertion:cleanup-g-crew-tier-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: verify-frame's ANCHOR_RE matches any 'word:identifier' token for seven specific keywords (struct/capability/event/constraint/assumption/claim/decision), and in DEGRADED mode ANY matched anchor is treated as a hard failure ('cannot resolve: this run oriented DEGRADED, so no map was read') regardless of whether the frame also cites valid substitute paths elsewhere. The template's own worked example for Decision Anchors uses exactly this colon-identifier syntax, which would have refused the gate if used verbatim in a degraded-mode frame.

### assertion:cleanup-g-crew-tier-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught before writing the frame, by reading the check's source rather than trusting the template's example was universally safe. Had it not been caught, the c6 gate would have refused with a confusing 'cannot resolve' message pointing at a decision id that had nothing to do with a real map -- a plausible source of a stuck Commander re-writing the frame repeatedly without understanding why a syntactically-fine decision bullet was failing.

### assertion:cleanup-g-crew-tier-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Described decisions in the DEGRADED-mode frame using plain prose (naming the decision by its slug in a sentence) rather than the colon-identifier anchor syntax, and cited only plain file paths as anchors -- matching what verify-frame's degraded-mode branch actually checks against (declared_substitute_paths), not the RESOLVED-mode anchor-id branch the template's example illustrates.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
