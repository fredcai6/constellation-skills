<!-- episode-state: schema=1 id=epic-418-followon-001 status=active -->

# episode: epic-418-followon-001

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
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Find out why dispatched crews kept reaching for the engine CLI instead of the MCP door, so the corpus rewrite could target whatever was causing it.

### assertion:epic-418-followon-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Crews reached for the CLI because agent-facing instruction still named it, so removing the instruction would remove the behaviour.

### assertion:epic-418-followon-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Nine of ten dispatch scripts in this epic never set SPINE_FILE. Every crew that 'reached for the CLI' had a door bound to a wave-1 scratch demo spine, so the CLI was the only path to its own spine. The crews were behaving correctly; the environment was broken.

### assertion:epic-418-followon-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: An entire causal story about agent preference was built on the behaviour, and a corpus-wide instruction rewrite was scoped against it. The rewrite was still worth doing, but the evidence cited for it measured the launcher rather than the agents.

### assertion:epic-418-followon-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Bind SPINE_FILE, SPINE_SESSION and SPINE_PARENT at launch and check the child process command line, rather than inferring intent from what a crew did after it arrived.

## Diagnosis (optional)

### assertion:epic-418-followon-001.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A behaviour observed under a broken environment reads as a preference, because the environment is invisible in the transcript and the choice is not.

### assertion:epic-418-followon-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The behaviour was attributed to the agents' judgment before the launcher's own environment was measured. Measuring it showed the agents had no alternative available, so the attribution was describing the dispatch scripts rather than the agents.
- history: restated — Restated as an observation. The original was written in the imperative and read as a rule for a future agent to follow; an episode records what happened, and a rule belongs in docs/agents/*. Caught by scripts/verify_episode_observations.py at the epic's closeout. — original statement was: Before attributing a behaviour to an agent's judgment, verify the agent had the alternative available; the launcher's own environment is the first thing to measure.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
