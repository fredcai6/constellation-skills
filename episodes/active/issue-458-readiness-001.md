<!-- episode-state: schema=1 id=issue-458-readiness-001 status=active -->

# episode: issue-458-readiness-001

## Mechanical
- run: issue-458-readiness
- project: constellation-skills
- role: commander
- spine-step: context
- context-manifest-ref: .agent-work/issue-458-readiness/context/context.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/issue-458-readiness/gauge.json

## Agent-supplied

### assertion:issue-458-readiness-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Watch the context governor's own gauge to know when to hand off, per the launch order's own Budget section.

### assertion:issue-458-readiness-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: gauge.json is refreshed periodically by a PostToolUse writer hook as the session makes tool calls, so its fill_fraction reading tracks the session's real, current context usage.

### assertion:issue-458-readiness-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: gauge.json's fill_fraction (0.190464) and observed_at (2026-08-08T23:18:53.944Z) never changed across dozens of tool calls spanning context, understand, plan, and execute -- the same single reading, inherited from a predecessor session, was read by every HARD-band advisory this whole run until the engine itself finally flagged it as too stale to trust (CONTEXT GAUGE SILENT).

### assertion:issue-458-readiness-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Every gate this run hit the HARD advisory on the same frozen reading and required filing a refresh-request to release the begin, even though no genuine context pressure existed in this fresh session -- resolved each time via the engine's documented release path (a matching pending refresh-request lets `start` proceed), so no gate was actually blocked, but the signal itself was never live.

### assertion:issue-458-readiness-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: File the refresh-request at the gate about to be started (same session, immediately) rather than waiting for a relaunch, since the underlying reading was never going to refresh on its own in this environment.

## Diagnosis (optional)

### assertion:issue-458-readiness-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The gauge-writer PostToolUse hook is not wired in this environment's settings.json -- consistent with this run's own launch order Mission section, which independently reports 'Context Governor hooks: UNWIRED' from an install_constellation.py --dry-run run minutes before this dispatch.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
