<!-- episode-state: schema=1 id=w1-wiring-005 status=active -->

# episode: w1-wiring-005

## Mechanical
- run: w1-wiring
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w1-wiring/PLAN_ALTERNATIVES.md
- artifact-ref: .agent-work/w1-wiring/PLAN_CRITIC.md

## Agent-supplied

### assertion:w1-wiring-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Determine whether real crew dispatch (independent implementer/reviewer/critic subagents, per commander-core.md's design-it-twice and crew-gate doctrine) was available in this dispatched context.

### assertion:w1-wiring-005.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Absence of a Task/Agent tool on the declared tool surface (Bash, Read, Write, Edit, WebFetch, WebSearch, Skill) means no independent crew can be raised at all.

### assertion:w1-wiring-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: That conclusion was incomplete. scripts/run_crew.py -- reachable the whole time via the Bash tool -- has a `--backend cli` mode that spawns a headless `claude` CLI subprocess with its own bound spine door (`_crew_door_env`), needing no Task/Agent tool at all; only its `--backend external` mode needs an Agent-tool subagent. The Admiral confirmed the sibling commander w1-verdict used exactly this path and got real independent implementer and reviewer crews. This run instead self-authored every plan-alternatives candidate, the cold plan critic pass, and g4's disposition work in its own context, each time stating the deviation as 'no Task/Agent tool available' without checking whether run_crew.py's cli backend was a live alternative.

### assertion:w1-wiring-005.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Every place design-it-twice and cold-critic review call for independent context was instead self-authored, weakening exactly the property those mechanisms exist for -- avoidable this run, not a genuine environmental constraint.

### assertion:w1-wiring-005.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None applied retroactively this run -- the Admiral's clean-room review already substituted for the missing independent review, and the mission's substantive findings held up under it. Recorded here so the next Commander dispatched the same way checks run_crew.py's cli backend before concluding no dispatch is possible.

## Diagnosis (optional)

### assertion:w1-wiring-005.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The launch order's own Engine access section named a CLI substitution for spine verbs but never named run_crew.py's cli backend as the crew-dispatch fallback for a context with no Task/Agent tool, so the absence of that tool was read as 'no dispatch is possible' rather than 'use the other backend' -- the Admiral named this as its own gap, not this run's, in the correction that produced this episode.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
