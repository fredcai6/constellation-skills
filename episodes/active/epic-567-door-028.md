<!-- episode-state: schema=1 id=epic-567-door-028 status=active -->

# episode: epic-567-door-028

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
- artifact-ref: launch-orders/LAUNCH_ORDER-567-m-UNSENT.md
- artifact-ref: scripts/install_constellation.py
- artifact-ref: skills/workbench/SKILL.md

## Agent-supplied

### assertion:epic-567-door-028.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Retiring skills/workbench entirely, on the reading that its teaching had been cut to a 20-line stub and the package was dead weight.

### assertion:epic-567-door-028.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A move plus a text update: the launch order was written from a live-referrer census of the repo tree, which showed a stub plus templates.

### assertion:epic-567-door-028.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The human called a corpus reinstall before the lane launched, and the reinstall showed the deletion target does not exist as described. install_constellation.py:229 bundles checklist_engine.py and gauge_writer_hook.py under workbench; :848-849 hard-code HOOK_OWNER_SKILL = 'workbench'; :929 points the installed hook path at constellation-workbench/scripts/. The installed package carries 7 engine scripts and ~/.claude/settings.json wires 5 hook entries plus 1 permission rule there, including the spine_rail.py Stop hook enforcing this very run.

### assertion:epic-567-door-028.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The order as written would have shipped a deletion that unwired the Stop hook, the SessionStart hook, the gauge writer and the engine path on every installed machine. It was caught by the human's sequencing, not by the Admiral's census.

### assertion:epic-567-door-028.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The lane was closed unsent and its order kept unlaunched. The teaching issue closed on what actually shipped; the package coupling was filed separately to be done deliberately with its own settings.json migration path.

## Diagnosis (optional)

### assertion:epic-567-door-028.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The installer only knows how to ship skills -- :322-324 raises InstallError for any skills/* directory without a parseable SKILL.md -- so a script bundle must wear a SKILL.md to be installable at all. The skill is vestigial and the wrapper is load-bearing, which a census of the repo tree cannot distinguish because the coupling lives in the installer's constants rather than in any reference to the files.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
