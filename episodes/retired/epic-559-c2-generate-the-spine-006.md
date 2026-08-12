<!-- episode-state: schema=1 id=epic-559-c2-generate-the-spine-006 status=retired -->

# episode: epic-559-c2-generate-the-spine-006

## Mechanical
- run: epic-559-c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/execute.json.journal
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/triage-candidates/RECOMMENDATIONS.md

## Agent-supplied

### assertion:epic-559-c2-generate-the-spine-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive the Commander's own `execute.json` through the MCP door, as the human's ruling requires -- the agents should not know about the CLI.

### assertion:epic-559-c2-generate-the-spine-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Every verb needed to drive a checklist is reachable through the door.

### assertion:epic-559-c2-generate-the-spine-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The door binds exactly one file at import time -- `SPINE = Path(os.environ['SPINE_FILE']).resolve()` in mcp_spine_server.py -- and exposes no per-call spine addressing on any of its nine tools, while the Commander spine's own `execute` step requires driving a second checklist. No door verb can name it. The four unresolvable `<engine>` tokens the launch order flags in the orchestrator-tier templates are the same defect's symptom; no token substitution reaches this.

### assertion:epic-559-c2-generate-the-spine-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Every engine call against execute.json in this run went through the CLI. One of those calls lost part of its recorded `--why` text: it contained backticks, which bash consumed as command substitution, printing a syntax error while the verb still succeeded. A door tool takes a JSON string and cannot do that.

### assertion:epic-559-c2-generate-the-spine-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: execute.json was driven through checklist_engine.py directly, with every call journaled to execute.json.journal so the work stayed engine-driven and auditable, and the gap was recorded as a triage candidate and a float rather than worked around silently.

## Retirement
- status: retired
- retired-reason: Mechanical field written wrong at capture: `run` was recorded as the kebab-cased 'epic-559-c2-generate-the-spine' rather than the work-id verbatim, 'epic-559/c2-generate-the-spine'. The store's own capture gate (verify_episode_captured.py) matches `- run: <work-id>` exactly, so these eight record a run no reader can resolve. Superseded by re-created equivalents in the same delta; retired rather than hand-edited because this writer is the only write path into the store.
- retired-at: 
- consolidated-into: 
- superseded-by: 
