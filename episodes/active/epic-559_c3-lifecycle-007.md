<!-- episode-state: schema=1 id=epic-559_c3-lifecycle-007 status=active -->

# episode: epic-559_c3-lifecycle-007

## Mechanical
- run: epic-559/c3-lifecycle
- project: constellation-skills
- role: commander
- spine-step: g5-integrate
- context-manifest-ref: LAUNCH_ORDER-C3@293b7721
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-implementer-result.md

## Agent-supplied

### assertion:epic-559_c3-lifecycle-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Commit g5's work area artifacts, staging by name, under the launch order's hard constraint 'Stage by name. Never git add -A.'

### assertion:epic-559_c3-lifecycle-007.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Expected a pathspec-scoped 'git add -A -- .agent-work/epic-559/c3-lifecycle/' to be a safe narrowing of the forbidden bare form, since the pathspec bounds what it can reach.

### assertion:epic-559_c3-lifecycle-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It swept in .agent-work/epic-559/c3-lifecycle/epic-559/c3-lifecycle/, a nested duplicate work directory produced by episode_capture.manifest_root() doubling the work-id segment, and committed it. Separately, because that same command's pathspec excluded scripts/ and tests/, the commit message described the not_yet_written guard while the guard itself was still unstaged.

### assertion:epic-559_c3-lifecycle-007.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Two corrections in a follow-up commit: untracking the stray directory and committing the code the previous message had already claimed. A commit whose message and contents disagree is worse than a missing commit, because it reads as done.

### assertion:epic-559_c3-lifecycle-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Untracked the directory with git rm --cached, committed the actual code, and stated both mistakes in that commit's own message rather than amending them away. Went back to naming every path explicitly.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
