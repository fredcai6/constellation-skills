<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-012 status=active -->

# episode: cleanup-f-derive-worktree-012

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework2-result.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Record a Fowler pass as a reviewer, without overwriting a predecessor reviewer's record (tc7, raised at g2-review).

### assertion:cleanup-f-derive-worktree-012.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The review survey template and the reviewer handoff were expected to agree on where a Fowler record goes.

### assertion:cleanup-f-derive-worktree-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The survey template resolves the Fowler record to one fixed path, .agent-work/<work-id>/FOWLER_PASS.json, shared by every reviewer on the work-id, while reviewer handoffs forbid overwriting a predecessor's record. Three FOWLER_PASS records already sit at variant paths on this work-id.

### assertion:cleanup-f-derive-worktree-012.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Every reviewer after the first must amend the survey to re-point it at a per-crew filename before it can comply with its own handoff; the g2 rework-2 reviewer used `amend --delta` with a retext-check on r6-fowler.c1.

### assertion:cleanup-f-derive-worktree-012.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each reviewer amended the survey to a per-crew filename, which is why the variant paths exist and are the visible symptom.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-012.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The template's path is keyed by work-id while the artifact it names is per-crew, so a second crew on the same work-id has no compliant destination without editing the template's own output.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
