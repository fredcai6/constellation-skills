<!-- episode-state: schema=1 id=epic-418-followon-002 status=active -->

# episode: epic-418-followon-002

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/transitions/w6x-generate-the-spine/REPLAN_RESULT.json

## Agent-supplied

### assertion:epic-418-followon-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Hand-author the work spines and review surveys for six parallel workstreams, so each crew arrived with a gated plan rather than prose.

### assertion:epic-418-followon-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: An Admiral authoring its own gates would produce checks that do their job, since the author knows the epic better than any crew does.

### assertion:epic-418-followon-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Roughly ten work spines and seven review surveys were hand-authored in one wave, and four carried checks that could not do their job: an unquoted pytest selector, a probe importing a module that needs a bound spine, a call using a parameter name the signature does not have, and a population filter wrong twice. Each was caught downstream by a crew, a reviewer or argparse. None was caught by its author.

### assertion:epic-418-followon-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Four rework rounds that existed only because the check was wrong, and a wave of evidence that the epic's own thesis applies one tier above where it was aimed: a hand-authored check is only as good as the hand that wrote it, and that hand was the unchecked link.

### assertion:epic-418-followon-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The generator built later in the epic compiles the spine from a typed spec whose check kinds are a closed vocabulary and refuses to write anything the oracle would reject, which took hand-typed shell strings out of the authoring path that produced these four faults.
- history: restated — Restated as an observation. The original was written in the imperative and read as a rule for a future agent to follow; an episode records what happened, and a rule belongs in docs/agents/*. Caught by scripts/verify_episode_observations.py at the epic's closeout. — original statement was: Compile the spine from a typed spec whose check kinds are a closed vocabulary, and refuse to write anything the oracle would reject; a check is never a shell string typed from memory.

## Diagnosis (optional)

### assertion:epic-418-followon-002.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Authoring a check and running it are separated by a dispatch, so the author never sees the failure their own text produces.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
