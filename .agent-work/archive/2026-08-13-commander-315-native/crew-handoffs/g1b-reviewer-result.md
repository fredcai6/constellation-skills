# Review Result — g1b combined closeout

## Assigned Gate

g1-review of .agent-work/commander-315-native/execute.json, fresh survey g1b-review.

## Result

BLOCK

## Handoff compliance

The engine-origin guard, CLI worktree placement, MCP one-call chdir, lifecycle recovery, map regeneration, and empty full-suite failure set all reproduce. One explicit close criterion is not met: the production CLI default does not pass an absolute assigned worktree to subprocess.run.

## Scope drift

No implementation scope drift found. The follow-up changes are limited to scripts/run_crew.py, scripts/mcp_spine_server.py, tests/test_crew_launcher.py, map/INDEX.md, and the two named untracked tests. The six excluded production files and tests/test_spine_origin_isolation.py have empty uncommitted diffs. Reviewer arming mutations were restored to their pre-mutation SHA-256 values.

## Evidence verdict

Behavioral evidence is otherwise strong and independently reproducible: focused suites pass, both ruled changes were armed on their failing side, repro_native.py reports GATE ARMED: True, map freshness passes, and the full Linux suite has no failing file.

Blocking exception: tests/test_crew_worktree_cwd.py proves the absolute case only by supplying an already-absolute TemporaryDirectory root. It does not cover the CLI defaults --root=. and --worktree=., where crew_cwd returns a relative Path.

## Code/doc quality

The scoped chdir context is narrow, restored in finally, and guarded by a synchronous-loop pin. The CLI spawn seam is cohesive and names invalid targets before spawn. However, crew_cwd's docstring promises an absolute directory while its implementation returns root / path without normalizing a relative root; this contract mismatch is production-observable at the default CLI boundary.

## Per-check findings

- r0-context: pass — loaded inherited doctrine, local deltas, handoff, claim index, bounded diff, and degraded map packet without opening survey state.
- r1-handoff: pass for the ruled behavior; the later appended rc8 check captures the unmet absolute-path subcriterion.
- r2-scope: pass — follow-up and reviewer activity stayed in allowed scope.
- r3-evidence: pass — required evidence and three red-side arming mutations reproduced.
- r4-quality: pass — six handoff constraints were appended and checked.
- r5-reconciliation: pass — schema, docstrings, and generated map reconcile the architecture change.
- r6-fowler: pass — all 12 smells visited; verifier exits 0.
- rc1-origin through rc7-map-wiring: pass — origin jobs, CLI/MCP behavior, synchronous premise, untouched lifecycle test, full suite, map delta, and production wiring all pass.
- cr1-ruling through cr6-forwardability: pass — both human-ruled options landed; no off switch, backend overclaim, forwarded-cwd claim, or transient regression was found.
- rc8-absolute-cwd: fail — the real CLI default returns and forwards a relative cwd.

## Map impact verdict

- **Evidence supports claimed change:** yes for origin enforcement, CLI placement behavior, and MCP lifecycle compatibility.
- **Constraints not violated:** all inbound constraints pass except the explicit absolute-cwd close criterion.
- **Notes match the diff:** yes; the follow-up map delta is exactly two added production symbols.
- **Decision candidates surfaced:** no new authority decision was needed; options 1 + 2 were settled/human and both landed.
- **Durable context routed:** CHECKLIST_SCHEMA, production docstrings, map/INDEX.md, the Fowler record, and three survey triage candidates preserve the durable context.

## Reconciliation check

No additional architecture reconciliation blocks the change. map/INDEX.md freshness is green; its four-line follow-up delta changes total script entities 1169 to 1171 and increments scripts.run_crew and scripts.mcp_spine_server by one each. The pre-existing zero-anchor map-orientation degradation was already escalated in the supplied packet.

## Blockers

- **rc8-absolute-cwd — default CLI path is not absolute.** scripts/run_crew.py:1573 keeps root as Path(args.root); both parser defaults are ".". scripts/run_crew.py:682 therefore returns Path(".") for crew_cwd(".", Path(".")), and launch_process receives cwd="." at scripts/run_crew.py:1184-1185 / 1243-1244.
  - Direct production probe: crew_cwd=.; is_absolute=False.
  - Test gap: tests/test_crew_worktree_cwd.py:84-113 uses an already-absolute TemporaryDirectory root, so its “absolute” assertion never exercises the default CLI boundary.
  - Required repair: normalize the returned non-legacy cwd to an absolute path and add dispatch plus resume coverage with a relative root/worktree, including the actual "." defaults. Preserve None for legacy entries.

## Out-of-scope observations

- Fowler duplicated-code: the three-part guarantee and forwarded-cwd non-claim are manually synchronized across checklist_engine.py, CHECKLIST_SCHEMA.md, and test_spine_origin_isolation.py.
- Fowler divergent-change: checklist_engine.py owns another independent concern atop lease, gauge, rail, journal, trip, and checklist execution.
- Fowler speculative-generality: ORIGIN_EXEMPT_VERBS has no production consumer; runtime consults only ORIGIN_GUARDED_VERBS. These three observations were filed as tc1-tc3 and do not independently block this gate.

## Verification run

    python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_lifecycle.py -q -p no:randomly
    188 passed in 0.75s (exit 0)

    python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_lifecycle.py -q -p no:randomly
    42 passed, 1 skipped, 10 subtests passed in 0.41s (exit 0)

    python .agent-work/commander-315-native/repro_native.py
    A PASS; B REFUSED; C PASS; D PASS; refusal took no lease; GATE ARMED: True (exit 0)

    python -m pytest tests/ -q -p no:randomly
    2979 passed, 6 skipped, 1130 subtests passed in 123.72s (exit 0)

    python -m pytest tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -q -p no:randomly
    1 passed in 2.33s (exit 0)

    python scripts/verify_fowler_pass.py .agent-work/commander-315-native/g1b-review/FOWLER_PASS.json
    fowler pass ok: smells=12, flagged=[duplicated-code, divergent-change, speculative-generality], overridden=[] (exit 0)

Arming: removing CLI cwd threading produced 4 failed / 5 passed; restoring produced 9 passed. Removing the MCP chdir produced 3 failed / 16 passed, including untouched test_mcp_lifecycle.py; restoring produced 19 passed. Adding import threading produced 1 failed / 1 passed in SingleThreadedDoorPinTests; restoring produced 2 passed. All three target hashes matched their pre-mutation values after cleanup.

Scope note: Linux behavior was tested. The Windows-only case-folding test remained skipped. Main's 2934 passed / 5 skipped / 0 failed baseline was supplied by the handoff, not re-measured; the observed failing-file difference is empty.

## Workflow Feedback

- **Handoff gaps:** Survey State Location says to create and drive the survey through a run_crew-bound MCP door, while this external dispatch supplied an already-instantiated survey and required a manually launched stdio door. The direct dispatch instruction resolved the conflict, but the handoff text itself was stale for this launch mode.
- **Context rediscovered:** the handoff supplied MCP environment bindings but not the newline-delimited initialize/tools-call envelopes; I inspected mcp_spine_server.py's schemas and protocol loop to drive the server safely.
- **Instructions improvised around:** the mandated apply_patch helper failed with bwrap loopback errors for both the sibling worktree and /tmp. I used the equivalent patch tool on private temporary copies for arming/artifact creation, restored production files by byte copy, verified SHA-256 equality, and removed the exact temp directory.
- **What would have made this easier:** add a short manual-stdio driver example and mark Survey State Location as “already instantiated” for external wrapper launches; add the actual CLI "." defaults to the required cwd tests.

## Return status

blocked
