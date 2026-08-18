<!-- episode-state: schema=1 id=epic-567-door-031 status=active -->

# episode: epic-567-door-031

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 2
- failed-commands: 0
- artifact-ref: .mcp.json
- artifact-ref: scripts/install_constellation.py

## Agent-supplied

### assertion:epic-567-door-031.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Reinstalling the corpus onto the human's machine so the wave-3 deliverables would be live rather than inert.

### assertion:epic-567-door-031.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The installer-writes-into-the-calling-repo defect was fixed and closed one wave earlier, so a self-install should leave the tracked tree clean.

### assertion:epic-567-door-031.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The install rewrote the tracked .mcp.json, replacing python3 with a probed machine-local py. It happened on this session's install and on the previous session's, and was reverted both times.

### assertion:epic-567-door-031.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A tracked file dirtied on every self-install, carrying an interpreter name that is correct only on the machine that ran the installer.

### assertion:epic-567-door-031.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: git checkout -- .mcp.json after each install. Recorded rather than reopened, under the standing ruling against minting new tracking mid-epic.

## Diagnosis (optional)

### assertion:epic-567-door-031.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The closed fix stopped the installer targeting the wrong checkout. It did not stop it writing a machine-local interpreter into a tracked file when the target checkout is the right one, which is the remaining half.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
