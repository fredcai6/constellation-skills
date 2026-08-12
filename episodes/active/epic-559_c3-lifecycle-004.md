<!-- episode-state: schema=1 id=epic-559_c3-lifecycle-004 status=active -->

# episode: epic-559_c3-lifecycle-004

## Mechanical
- run: epic-559/c3-lifecycle
- project: constellation-skills
- role: commander
- spine-step: g1-integrate
- context-manifest-ref: LAUNCH_ORDER-C3@293b7721
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-reviewer-result.md
- artifact-ref: .agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-rework-result.md

## Agent-supplied

### assertion:epic-559_c3-lifecycle-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Integrate g1 after an independent reviewer, per the two-question standard the launch order inherited: does the mechanism work, and is the value it carries correct.

### assertion:epic-559_c3-lifecycle-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Expected an APPROVE. The gate's 28 tests passed, the full suite was green at 2852, the sweep was unchanged at 23, and the rollback and self-verify fixtures were real and mutation-checked.

### assertion:epic-559_c3-lifecycle-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The reviewer returned BLOCK on a write missing newline='\n'. docs/agents/CREW_CONTEXT.md:43 requires it on every write and .github/workflows/ci.yml:23 runs windows-latest, so this would have written a CRLF spine on Windows CI that NO test asserted against. Every green result was genuinely green and the artifact was still wrong.

### assertion:epic-559_c3-lifecycle-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One rework cycle, roughly 25 minutes. Without it a silently-wrong write ships in the module whose whole job is producing a spine other agents read.

### assertion:epic-559_c3-lifecycle-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Verified all three of the reviewer's supporting facts myself before acting, then required the rework to add the test that would have caught it -- not just the one-line fix -- and falsified that new test by mutation before accepting it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
