# Review Result — g1c combined closeout

## Assigned Gate

`g1-review` of `.agent-work/commander-315-native/execute.json`, fresh registry attempt `g1c-review`.

## Result

`APPROVE`

## Handoff compliance

The sole prior blocker is closed. `crew_cwd('.', Path('.'))` returns this repository root as an absolute path; real parser-default dispatch and resume deliver that path to the launch seam; legacy missing-worktree entries still deliver `None`. The combined g1 origin guard, CLI placement, MCP chdir, lifecycle, map, and suite requirements all reproduce with no stop condition hit.

## Scope drift

No implementation scope drift found. Relative to the prior g1b tree, the repair changes only `scripts/run_crew.py` and `tests/test_crew_worktree_cwd.py` plus run artifacts. Protected engine/origin/template/schema files have no new uncommitted diff. Reviewer arming changed one resolver line temporarily, restored it to pre-arm SHA-256 `69dae737ec57544194b6869143872eaee82c1deb765effc9f6eac30b6e3b25b0`, and made no production edits.

## Evidence verdict

Evidence is independently reproducible and behavior-focused. The exact pre-repair resolver (`root / path`) makes both default-dot tests fail on `is_absolute`; restoring the repair makes both pass. Focused repair, original gate, native reproducer, full suite, and map freshness all pass. The mechanical full-suite failing-file set is empty.

## Code/doc quality

The repair is the minimal resolver normalization: establish an absolute root before joining/resolving a relative worktree. The shared resolver keeps dispatch and resume aligned, preserves the legacy sentinel, and leaves ExternalBackend record-only. Docstrings accurately state the ambient-cwd limitation and do not overclaim non-forwardability.

## Per-check findings

- `r0-context` — pass: loaded complete Reviewer doctrine, checklist reference, project deltas, handoff, prior blocker, claim index, and map packet without opening survey state.
- `r1-handoff` — pass: default-dot dispatch/resume now satisfy the absolute cwd contract.
- `r2-scope` — pass: two-file rework only; specific exclusions remain untouched by the repair.
- `r3-evidence` — pass: red/green arm, focused suites, native repro, full suite, and map freshness reproduced.
- `r4-quality` — pass: six constraints and nine close-criteria checks appended and visited through MCP.
- `r5-reconciliation` — pass: resolver normalization changes no production symbol/entity surface; map stays fresh.
- `r6-fowler` — pass: all 12 smells visited; verifier exits 0; three observations filed as `tc1`–`tc3`.
- `cr1-ruling` — pass: settled options 1 (CLI cwd) and 2 (MCP scoped chdir) both remain implemented.
- `cr2-off-switch` — pass: engine-native guard has no spine-authored or environment off switch.
- `cr3-window` — pass: MCP chdir is synchronous and restored in `finally`.
- `cr4-backends` — pass: CLI spawns with cwd; ExternalBackend still spawns nothing.
- `cr5-transient` — pass: legacy `None`, resume, and lifecycle behavior remain green.
- `cr6-forwardability` — pass: implementation retains the explicit ambient-cwd spoofability limitation.
- `rc1-origin` — pass: foreign-tree claim refuses without a lease; root, fallback, and subdir cases behave correctly.
- `rc2-cli-cwd` — pass: default-dot, relative, absolute, real-subprocess, legacy, and missing-directory cases pass.
- `rc3-door-cwd` — pass: bound-door cwd selection/restoration and lifecycle behavior pass.
- `rc4-sync` — pass: single-threaded door premise remains mechanically pinned.
- `rc5-lifecycle` — pass: original open-drive-close coverage remains green.
- `rc6-suite` — pass: 2,981 passed, 6 skipped, 1,130 subtests; failing-file set empty.
- `rc7-map-wiring` — pass: map freshness passes and exactly two production resolver call sites exist.
- `rc8-absolute-cwd` — pass: direct/default dispatch/default resume are absolute and equal the repo root; legacy is `None`.
- `rc9-red-arm` — pass: exact pre-repair line produces 2 failures; byte-identical restoration produces 2 passes.

## Map impact verdict

- **Evidence supports claimed change:** yes; the direct probe, dispatch/resume seam assertions, real subprocess check, and red arm demonstrate the capability change.
- **Constraints not violated:** yes; both human-ruled options, legacy `None`, relative-under-root behavior, backend boundary, synchronous MCP window, and claim limitations are preserved.
- **Notes match the diff:** yes; the repair touches the existing `crew_cwd` structural anchor and adds test coverage without adding a production symbol.
- **Decision candidates surfaced:** none; the repair implements the existing settled/human ruling and needs no new authority.
- **Durable context routed:** map freshness is green and Fowler maintenance findings are filed as triage candidates.

## Reconciliation check

No reconciliation blocker. `map/INDEX.md` remains fresh without regeneration because the repair changes only an existing function body. The pre-existing degraded map-orientation packet (zero citable anchors) remains outside this repair and was already escalated.

## Blockers

- None.

## Out-of-scope observations

- Fowler duplicated-code: the origin guarantee and ambient-cwd limitation are manually repeated across engine code, schema docs, and tests.
- Fowler divergent-change: `checklist_engine.py` carries another independent concern in an already broad module.
- Fowler speculative-generality: `ORIGIN_EXEMPT_VERBS` has no production consumer; runtime consults only the guarded set.

## Verification run

```text
python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py -q -p no:randomly
171 passed in 0.55s

pre-repair arm: python -m pytest tests/test_crew_worktree_cwd.py -q -p no:randomly -k cli_default_dot
2 failed, 9 deselected in 0.04s

restored: python -m pytest tests/test_crew_worktree_cwd.py -q -p no:randomly -k cli_default_dot
2 passed, 9 deselected in 0.03s

python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_lifecycle.py -q -p no:randomly
52 passed, 1 skipped, 10 subtests passed in 0.47s

python .agent-work/commander-315-native/repro_native.py
GATE ARMED: True; foreign refusal took no lease

python -m pytest tests/ -q -p no:randomly
2981 passed, 6 skipped, 1130 subtests passed in 124.29s

python -m pytest tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -q -p no:randomly
1 passed in 2.35s

python scripts/verify_fowler_pass.py .agent-work/commander-315-native/g1c-review/FOWLER_PASS.json
fowler pass ok: smells=12, flagged=[duplicated-code, divergent-change, speculative-generality], overridden=[]
```

Linux behavior was exercised. Windows-only cases account for skipped tests and were not executed on this host.

## Workflow Feedback

- **Handoff gaps:** the close criteria name prior checks `rc1`–`rc7` and `cr1`–`cr6` but do not restate their imperatives; I reconstructed explicit appended checks from the prior result and current source.
- **Context rediscovered:** manual newline-delimited MCP startup still required reconstructing the JSON-RPC initialize/tools-call envelopes; the handoff supplies bindings but no protocol example.
- **Instructions improvised around:** the mandated patch helper cannot enter this sibling worktree because its sandbox fails at loopback setup. I used bounded `git apply` patches for the reversible one-line arm and review artifacts, restored production by reversing the exact patch, and verified the pre/post SHA-256 match.
- **What would have made this easier:** include one manual-stdio JSON-RPC example and a compact table restating the prior check IDs and imperatives in re-review handoffs.

## Return status

`complete`

