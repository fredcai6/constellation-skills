# Independent review

Verdict: APPROVE for the bounded offline first version. No remaining blocker was found in the reviewed scope. This is not approval of live provider behavior or the full installed Commander workflow.

Reviewed README, all four TypeScript source files, the Python transport, all three test files, and the Pi Commander client skill. No model requests were made. The engine transport calls the existing engine unchanged; its tests compare the structured projection with the original engine and reproduce CLI, lease, and failed-condition behavior.

## Verification

- `node --import tsx --test test/*.test.ts`: 22 passed, 0 failed. Tests use real engine processes and mocked model calls; one test initializes the real Pi SDK without calling a model.
- `npm run typecheck`: passed.
- Python subprocess tests required sandbox escalation because the restricted environment reports `Failed to create stream fd: Operation not permitted`. The successful run was offline.

The checks cover separate role sessions, role tools, external plan acceptance, final human acceptance, BLOCK refusing advancement, repair with reviewer findings, persisted call limits, known incremental usage on errors, explicit overrides, controller exclusion, session binding before model work, completed-child reconciliation after interrupted parent advancement, and fresh work following explicit reopen.

## Findings

Initial blockers found during review were corrected: completed children stranded parent recovery; reviewer BLOCK had no usable repair path; the initial repair attempted to reopen an in-progress child; repair omitted reviewer findings; explicit parent reopen could recycle stale child success; and session identity was saved only after the model invocation settled. The final checks exercise these corrections.

The final recovery observation was corrected: attempting to reopen an active review used to delete reviewer findings before the parent engine refused the operation. Preflight now rejects active/future parent gates before child mutation. The new regression test verifies that BLOCK findings survive and ordinary repair still succeeds.

Residual limits are acceptable for this slice: bash tools follow role conventions rather than sandboxing; early `finish_crew` does not advance a failed model invocation; request limits are not dollar caps; hard process termination can leave a lock requiring inspection. There is also a small no-provider-work window between saving a newly allocated session path and Pi persisting its first user message; a crash there leaves a clear missing-session error requiring local metadata recovery. No Claude authentication or successful hosted-model run was verified.

## Code-smell pass

Long functions and dense formatting are present in workflow orchestration and CLI parsing; observation only. Splitting pure checklist construction or override handling is reasonable when another workflow requires it. Large class, duplicated code, feature envy, data clumps, primitive obsession, long parameter list, shotgun surgery, divergent change, message chains, speculative generality, and comments-as-deodorant were assessed; none warrants a change for this bounded integration. No documented-standard overrides were needed.

## Workflow feedback

The handoff permitted only this report to be written and provided no bound SPINE environment. The installed reviewer skill requires an engine-owned survey and a separate Fowler record before reviewing. Those artifacts would exceed that explicit handoff, so this was a bounded independent review, not a claimed engine-driven reviewer survey. No original engine files were edited.

## Checked source snapshot

SHA-256 at final deterministic verification:

```text
e3a9ff42b51e0cf2943121941653243a6e210a84248910c10d102a0696fb1e72 src/cli.ts
623e17da7e869958a264823c6a11c4333b0a815f34e88cf847452ec04ffebeb9 src/engine.ts
f08992c1790883f0ab888350ec97cb53d1dfa7160e208aa37793e33be1f4fc42 src/pi-runtime.ts
94ce19a518270bf63a1f34d89c216caec436f142f183b280a93e680e8b95871a src/workflow.ts
1accc0cae89bf49c0db991601eade83b2d8bd32979e387193896861a6ebae814 python/engine_bridge.py
48f3d85116a42c95a686a90c9ce5c25e56025ed80609554fc90b9a8b470be8e2 skills/pi-commander/SKILL.md
```
