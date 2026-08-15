<!-- episode-state: schema=1 id=b441-merge-and-verify-002 status=active -->

# episode: b441-merge-and-verify-002

## Mechanical
- run: b441-merge-and-verify
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/b441-merge-and-verify/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/b441-merge-and-verify/REPLAN_INPUT.json

## Agent-supplied

### assertion:b441-merge-and-verify-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Determine which of three named outcomes (nothing breaks / a fixture is dishonest / a genuine guard collision) applied to #441's spawn tests against #588's new origin_worktree_refusal guard, per LAUNCH_ORDER.md's explicit instruction to distinguish the outcome and report evidence rather than just report green.

### assertion:b441-merge-and-verify-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Going in, it was genuinely open which outcome would hold -- the launch order framed this as the open question the whole lane exists to answer, naming the exact failing shape (a pytest tempdir has no git toplevel) that the guard was built to refuse.

### assertion:b441-merge-and-verify-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Outcome 1 (nothing breaks) held. origin_worktree_refusal() returns None unconditionally when spine.get('origin') is not a dict, before it reaches the cwd/git-toplevel check. #441's spawn-test fixtures (put_checklist/write_spine in tests/test_spine_rail.py) write raw spine JSON with no origin field at all, confirmed by grep across both named test files returning zero '"origin"' hits. A live two-case repro confirmed the mechanism directly: an origin-stamped spine claimed from a bare tempdir cwd was REFUSED by the guard; the same claim against an unstamped spine (matching the fixture's actual shape) succeeded. The two named spawn tests passed directly, and the full clean-env suite passed at 0 failed.

### assertion:b441-merge-and-verify-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: About fifteen minutes of targeted investigation plus one throwaway two-case repro script; no code changes were needed because the fixtures were already honest with respect to this guard.

### assertion:b441-merge-and-verify-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: None needed.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
