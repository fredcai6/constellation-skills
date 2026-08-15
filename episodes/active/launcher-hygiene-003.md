<!-- episode-state: schema=1 id=launcher-hygiene-003 status=active -->

# episode: launcher-hygiene-003

## Mechanical
- run: launcher-hygiene
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/launcher-hygiene/REPLAN_INPUT.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/launcher-hygiene/REPLAN_INPUT.json

## Agent-supplied

### assertion:launcher-hygiene-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author .agent-work/launcher-hygiene/REPLAN_INPUT.json to satisfy execute's c2 postcondition, which requires it to pass `verify_iterative_role_artifacts.py commander --work-id launcher-hygiene` (a G2 check).

### assertion:launcher-hygiene-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The bundled REPLAN_INPUT.template.json in .agent-work/templates/ was expected to be sufficient on its own to know the required shape.

### assertion:launcher-hygiene-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The template alone under-specified several structural constraints the actual verifier enforces (e.g. open_current_wave_issue_ids and completed_outcomes must exactly partition current_wave.issues' ids with no overlap; discrepancy classifications are drawn from a fixed enum; current_plan re-validates against the full G1 manifest shape via a reused verify_manifest_shape import) -- these only became visible by reading skills/replan/scripts/verify_replan.py and the installed constellation-to-initial-issues verify_issue_set.py directly, since verify_iterative_role_artifacts.py resolves its verifier module from the installed skills root (~/.claude/skills), not from this repo's own skills/ source tree.

### assertion:launcher-hygiene-003.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: Two extra file reads (both verifier scripts) before authoring the JSON, avoiding a guess-fail-reread cycle against the actual G2 check; the authored file passed verify_iterative_role_artifacts.py on the first run after that reading.

### assertion:launcher-hygiene-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: This run read skills/replan/scripts/verify_replan.py's verify_replan_input and the installed constellation-to-initial-issues verify_issue_set.py's verify_manifest_shape directly before authoring REPLAN_INPUT.json, then filled every field with this run's real completed_outcomes, wave_evidence, and discrepancies (the Stop-hook MCP-door binding gap and the six-occurrence auto-backgrounding pattern) rather than adapting the template's placeholder prose.
- history: restated — Restated to remove a clause-opening bare imperative ('Read') the episode-observation guard flags in workaround kind; substance and detail (including the installed-vs-repo skills root finding) unchanged, subject added to the opening clause. — original statement was: Read skills/replan/scripts/verify_replan.py's verify_replan_input and the installed constellation-to-initial-issues verify_issue_set.py's verify_manifest_shape directly before authoring REPLAN_INPUT.json, then filled every field with this run's real completed_outcomes, wave_evidence, and discrepancies (the Stop-hook MCP-door binding gap and the six-occurrence auto-backgrounding pattern) rather than adapting the template's placeholder prose.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
