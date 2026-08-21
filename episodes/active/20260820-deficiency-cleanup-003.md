<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-003 status=active -->

# episode: 20260820-deficiency-cleanup-003

## Mechanical
- run: 20260820-deficiency-cleanup
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/20260820-deficiency-cleanup/evidence/CHANNEL-EXPERIMENT.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Scaffold a reviewer work area so a crew could be dispatched through run_crew --backend cli for the channel experiment.

### assertion:20260820-deficiency-cleanup-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: init_work_area.py --spine takes the path of a spine template. Handing it the repository's own specs/reviewer.spine.toml should either work or say what is wrong.

### assertion:20260820-deficiency-cleanup-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It fails with a raw json.decoder.JSONDecodeError traceback: Expecting value: line 1 column 1 (char 0). It wants the COMPILED JSON that generate_spine.py emits, not the TOML spec. The correct sequence is two commands and nothing says so.

### assertion:20260820-deficiency-cleanup-003.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: One failed command and a detour during provisioning. Small in itself, but it is the exact target class of the standing criterion: an honest agent does the obvious thing with the file that ships in the obvious place, and gets a stack trace instead of guidance.

### assertion:20260820-deficiency-cleanup-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The sequence that worked was generate_spine.py on the .toml spec with --out to a JSON path, then init_work_area.py --spine against that JSON. Recorded rather than filed, per human ruling of 2026-08-21.

## Diagnosis (optional)

### assertion:20260820-deficiency-cleanup-003.d1
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The cheapest available remedy is one branch and one string: a .toml payload recognized before json.loads, refused with the compile command named.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
