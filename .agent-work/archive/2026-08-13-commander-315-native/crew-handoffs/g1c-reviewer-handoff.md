# Reviewer Handoff — g1 re-review after absolute-cwd repair

## Gate
`g1-review` of `.agent-work/commander-315-native/execute.json`, fresh crew-registry attempt `g1c-review`.

Work only in `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`. Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`; do not merge, push, commit, or modify production.

## Survey State Location
Use the already-instantiated `.agent-work/commander-315-native/g1c-review/review.json` through the manually bound stdio MCP door named in the dispatch instruction. Do not create another survey.

## What Was Implemented
The previous independent review BLOCKed because `crew_cwd('.', Path('.'))` returned relative `Path('.')`, despite the contract requiring an absolute assigned worktree. The rework resolves a relative root before joining/resolving a relative worktree and adds default-dot dispatch/resume tests. Read `g1b-reviewer-result.md` for the blocker and `g1c-implementer-result.md` as a claim index.

## How to Inspect the Diff
Run `git status --porcelain`; inspect untracked tests explicitly; compare the current two-file repair against the pre-rework shape described in the BLOCK result. For the full gate use `git diff 9bb8c1b6 --` plus untracked-safe reads. Do not use `git diff main...HEAD`.

Deliverable Path Check: `.agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md` is not ignored (`git check-ignore` exits 1).

## Task Statement
Independently verify that the sole `rc8-absolute-cwd` blocker is genuinely closed without regressing the already-approved engine guard, MCP door behavior, legacy `None` fallback, or full-suite empty failure set. Return a fresh APPROVE/BLOCK for the combined g1 change.

## Close Criteria

- Drive the actual default boundary: `crew_cwd('.', Path('.'))` is absolute and equals the current repo root; legacy `crew_cwd(None, root)` remains `None`.
- Independently exercise `CliBackend.dispatch` and `CliBackend.resume` with root/worktree `.` and observe the launch seam receive an absolute cwd. Confirm the new tests would fail on the pre-repair one-line implementation, then restore byte-identically.
- Re-run `tests/test_crew_worktree_cwd.py` plus `tests/test_crew_launcher.py`; all pass.
- Confirm the rework touched only `scripts/run_crew.py` and `tests/test_crew_worktree_cwd.py` beyond prior run artifacts, and the production change is the minimal resolver normalization. No policy, registry, external-backend, MCP-door, or engine behavior changed.
- Re-run the focused original gate suite and `repro_native.py`; the origin guard remains armed and untouched lifecycle flow remains green.
- Re-run the full suite and state the mechanical failing-file set. APPROVE requires it empty.
- Re-run map freshness; if normalization changes no symbol/entity surface, `map/INDEX.md` remains fresh without regeneration.
- Confirm prior review checks `rc1`–`rc7` and constraints `cr1`–`cr6` remain valid on this tree; do not merely trust the prior verdict where the one-line repair could affect them.

## Allowed Scope
Reviewer writes only its survey/Fowler/result artifacts and reversible temporary mutation for arming. Production is read-only. Review the full gate, with repair focus on `scripts/run_crew.py` and `tests/test_crew_worktree_cwd.py`.

## Specific Exclusions
No production/test edits. Restore arming mutations. Do not enter the sibling `epic-568-315`, merge, push, or commit.

## Constraints the Implementation Must Respect

- Human ruling options 1 + 2 still both land; this rework refines option 1 only.
- Every non-legacy `crew_cwd` return is absolute; legacy missing-worktree stays `None`.
- Relative worktrees resolve under the addressed root after that root is established absolutely.
- External backend spawns nothing and is not falsely claimed to gain cwd placement.
- No non-forwardability overclaim; no engine off switch; MCP chdir window remains synchronous and restored.

## Map Anchors (inbound)

- **Structural:** `scripts/run_crew.py::crew_cwd/CliBackend.dispatch/CliBackend.resume/launch_process`; original `checklist_engine` guard and `mcp_spine_server` chdir are regression surfaces only.
- **Capability:** CLI crew placement and end-to-end origin isolation.
- **Constraint:** legacy `None`; empty failure-set difference; two-file repair scope.
- **Decision:** options 1 + 2 settled by human; repair absolute-path contract within option 1. `@grade: settled/human · leans g1-review,g1-integrate`
- **Evidence:** prior BLOCK `rc8`; g1c TDD result; focused launcher/origin/MCP tests; full suite; map freshness.

## Evidence Produced
Implementer claims default-dot tests red 2/green 2; 171 focused tests green; direct resolver absolute/equal; two production call sites. Reproduce rather than trust.

Required commands:

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py -q -p no:randomly
python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_lifecycle.py -q -p no:randomly
python .agent-work/commander-315-native/repro_native.py
python -m pytest tests/ -q -p no:randomly
python -m pytest tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -q -p no:randomly
```

## Suggested Model Tier
Stronger: narrow repair, but it closes a blocker discovered only after an earlier green full suite.

## Stop Conditions
Return BLOCK if default-dot dispatch or resume is still relative, legacy behavior changes, arming cannot be reproduced/restored, scope expands, any original guard invariant regresses, or the failing-file set is nonempty.

## Return Format
Write `REVIEW_RESULT` with verdict, per-check findings, blockers, observations, and workflow feedback to `.agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md`. That artifact is delivery.
