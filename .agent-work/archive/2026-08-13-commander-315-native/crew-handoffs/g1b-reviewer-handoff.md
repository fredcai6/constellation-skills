# Reviewer Handoff — g1 combined closeout after the ruled follow-up

## Gate
`g1-review` of `.agent-work/commander-315-native/execute.json`, fresh attempt named `g1b-review` in the crew registry to avoid colliding with the completed pre-ruling review.

Work only in `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`. Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315` and never write the main checkout.

## Survey State Location
Create and drive the review survey at `.agent-work/commander-315-native/g1b-review/review.json` through the MCP door bound by `run_crew.py`. Write the result before returning.

## What Was Implemented
The committed engine-native origin/worktree guard from the original g1 plus the human-ruled follow-up:

1. `run_crew.launch_process` launches CLI crews in the registry's assigned worktree.
2. `mcp_spine_server.run_engine` stands in the bound spine's worktree for exactly one in-process engine call and restores cwd in `finally`.
3. Tests pin spawn cwd, lifecycle recovery, cwd restoration, and the door's single-threaded premise; cwd-independence prose was reconciled. `map/INDEX.md` was regenerated for the two new symbols.

Read `.agent-work/commander-315-native/crew-handoffs/g1b-implementer-result.md` as a claim index, not as proof. The original review at `g1-reviewer-result.md` predates the follow-up and is context only.

## How to Inspect the Diff
This target includes committed and uncommitted work. Run `git status --porcelain`, inspect untracked additions explicitly, and use `git diff 9bb8c1b6 --` plus `git diff -- scripts/run_crew.py scripts/mcp_spine_server.py tests/test_crew_launcher.py map/INDEX.md`. Do not use `git diff main...HEAD`.

Deliverable Path Check: `.agent-work/commander-315-native/crew-handoffs/g1b-reviewer-result.md` is not ignored (`git check-ignore` exits 1) and may be committed with the run.

## Task Statement
Independently decide whether the full g1 change now closes the worktree-origin enforcement gate without weakening it: the engine still refuses guarded verbs from a foreign tree without writing, while real CLI crews and the in-process MCP lifecycle door deliberately run engine calls from their assigned/bound worktree. The prior `{tests/test_mcp_lifecycle.py}` failure-set difference must be empty.

## Close Criteria

- Re-run the original gate's seven jobs: the comparison is not tautological; both original halves are armed; every malformed/missing-origin fallback is unchanged; all no-gos hold; no non-forwardability overclaim appears; origin-carrying match and mismatch coverage is real; and the in-process MCP caller is deliberately handled rather than exempted.
- Review change 1 through the production seam: assert dispatch and resume pass an absolute assigned worktree to `subprocess.run`, relative worktrees resolve against `--root`, legacy entries without `worktree` retain inherited cwd, and missing/non-directory targets fail by name before spawn.
- Review change 2 through the real door: an origin-carrying foreign-worktree spine can be claimed through stdio, cwd is restored after success, `SystemExit`, ordinary refusal, and exception, and an unresolvable worktree degrades to no move rather than blocking the server.
- Establish that process-global `chdir` is safe under the server's current synchronous one-request-at-a-time loop, and that tests will fail if concurrency is introduced without redesign.
- Confirm `tests/test_mcp_lifecycle.py` passes untouched. No assertion may have been adjusted to observed output.
- Reproduce the full-suite mechanical distribution and state its failing-file set against main's stated `2934 passed, 5 skipped, 0 failed` Linux baseline. APPROVE requires an empty failing-file difference.
- Confirm `map/INDEX.md` changes are exactly attributable to the two added production symbols and the map freshness test is green.
- Run wiring greps for `crew_cwd` and `_standing_in_the_bound_spines_worktree`; each must have a non-test production call site. Zero is BLOCK.

## Allowed Scope
Review the full diff from `9bb8c1b6`, including committed original-gate files and the follow-up in `scripts/run_crew.py`, `scripts/mcp_spine_server.py`, `tests/test_crew_launcher.py`, `tests/test_crew_worktree_cwd.py`, `tests/test_mcp_door_engine_cwd.py`, and `map/INDEX.md`. Reviewer writes are limited to its survey/result artifacts and temporary reversible mutations used for arming; restore every mutation.

## Specific Exclusions
Production changes to `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py`, `scripts/spine_lifecycle.py`, `scripts/checklist_engine.py`, `scripts/init_work_area.py`, or the already-reviewed origin tests are forbidden during review. Do not merge, push, or edit assertions to match output.

## Constraints the Implementation Must Respect

- Human ruling: options 1 + 2 both land. Do not relitigate or substitute one for the other.
- The engine guard keeps no env override, flag, caller exemption, or other off switch.
- `chdir` is scoped to the one in-process engine call, restoration is unconditional, and identity containment checks remain outside the moved window.
- CLI dispatch and resume use the same registry worktree value; external backend spawns nothing and is not falsely claimed to gain this guarantee.
- The known transient live-`.agent-work` gauge-chain test must be rerun alone if it fires before being reported as a regression.
- No claim of non-forwardability. Certify coverage, unbypassability from the spine, and an independent expected side only.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py::origin_worktree_refusal/main`; `scripts/run_crew.py::crew_cwd/launch_process/CliBackend.dispatch/resume`; `scripts/mcp_spine_server.py::run_engine/_standing_in_the_bound_spines_worktree/main`; `scripts/spine_lifecycle.py::build_origin` read-only.
- **Capability:** spine origin enforcement; CLI crew placement; stdio MCP lifecycle engine drive.
- **Constraints:** origin-less fallback; refusal-without-persistence; synchronous-door premise; full-suite failure-set difference empty.
- **Decision:** options 1 + 2 are the ruled collision fix. `@grade: settled/human · leans g1-review,g1-integrate`
- **Evidence:** `repro_native.py`; `tests/test_spine_origin_isolation.py`; `tests/test_crew_worktree_cwd.py`; `tests/test_mcp_door_engine_cwd.py`; `tests/test_mcp_lifecycle.py`; full suite.
- **Confidence flags:** process-global chdir; relative-worktree resolution; generated map delta; external backend deliberately outside the spawn guarantee.

## Evidence Produced
Implementer reports `2979 passed, 6 skipped, 0 failed, 1130 subtests`, 42 focused tests plus 1 skipped, and `GATE ARMED: True`. Independently reproduce the focused suite and full distribution. Treat those numbers as untrusted until rerun.

Required commands:

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_lifecycle.py -q -p no:randomly
python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_lifecycle.py -q -p no:randomly
python .agent-work/commander-315-native/repro_native.py
python -m pytest tests/ -q -p no:randomly
```

## Suggested Model Tier
Stronger (`opus`): this is a cross-process/cwd isolation change with a prior independently discovered lifecycle regression.

## Stop Conditions
Return BLOCK if the diff or untracked tests cannot be inspected, any required evidence is stale/unreproducible, either ruled half is ineffective, cwd is not restored, a new failure remains, a no-go is breached, or a policy choice is needed.

## Return Format
Return `REVIEW_RESULT`: `APPROVE` or `BLOCK`, per-check findings, blockers, out-of-scope observations, and workflow feedback. Write it to `.agent-work/commander-315-native/crew-handoffs/g1b-reviewer-result.md` before ending; that artifact is delivery.
