# Implementer Handoff — g1 reviewer rework: absolute CLI cwd

## Gate
`g1-review` rework, crew-registry attempt `g1c-implement`.

Work only in `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`. Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`; do not merge, push, or commit.

## Task
Fix the one blocker in `.agent-work/commander-315-native/crew-handoffs/g1b-reviewer-result.md`: every non-legacy cwd returned by `scripts.run_crew.crew_cwd` must be absolute, including the real CLI defaults `--root . --worktree .`. Add dispatch and resume coverage at that default-dot boundary.

## Protected Intent
Human-ruled option 1 makes a CLI crew run in its assigned worktree by construction, not by inheriting a dispatcher accident. The registry worktree and spawned cwd describe the same tree. This rework closes the reviewer-found contract/test gap without changing option 2 or the engine guard.

## Test Mode
TDD required. Write the default-dot dispatch/resume tests first and observe them fail because the spawn receives relative `Path('.')`; then make the smallest production repair and re-run green.

## Close Criteria

- `crew_cwd('.', Path('.'))` returns an absolute path resolving to the current repo root; `crew_cwd(None, root)` remains exactly `None` for legacy entries.
- A real `CliBackend.dispatch` with root/worktree defaults records and passes an absolute cwd to the launch seam.
- A real `CliBackend.resume` for a registry entry whose worktree is `.` passes an absolute cwd; a legacy entry without `worktree` still passes `None`.
- Existing absolute and relative-worktree semantics remain green: relative worktree resolves against root, not against some unrelated dispatcher directory.
- No files beyond `scripts/run_crew.py` and `tests/test_crew_worktree_cwd.py` change. In particular, do not touch `mcp_spine_server.py` or any already-reviewed origin-guard file.

## Allowed Scope
`scripts/run_crew.py` and `tests/test_crew_worktree_cwd.py` only.

## Specific Exclusions
All other production/tests, including `scripts/mcp_spine_server.py`, `scripts/checklist_engine.py`, `scripts/init_work_area.py`, `scripts/spine_lifecycle.py`, `tests/test_mcp_door_engine_cwd.py`, and `tests/test_spine_origin_isolation.py`.

## Constraints

- Preserve `None` as the legacy/no-worktree sentinel.
- Return an absolute path for every non-`None` input, including when both root and worktree are relative.
- Do not add a second resolver or alter registry storage. Repair `crew_cwd`, the existing one-caller-family seam.
- `Path.resolve()` may use the actual invocation cwd to turn a relative CLI `--root` into an absolute root; once root is established, worktree remains rooted under it. Do not re-import the unrelated-directory accident the function was added to remove.
- No assertion may be adjusted merely to observed output. The new tests must fail on the current implementation and pass after repair.

## Map Anchors (inbound)

- **Map entry point:** `map/INDEX.md` → `scripts.run_crew`.
- **Structural:** `scripts/run_crew.py::crew_cwd`, `CliBackend.dispatch`, `CliBackend.resume`, `launch_process`.
- **Capability:** CLI crew placement in assigned worktree.
- **Constraint:** legacy registry entries without `worktree` inherit cwd (`None`).
- **Decision:** human ruled option 1; repair its absolute-path contract rather than revisiting it. `@grade: settled/human · leans g1-review,g1-integrate`
- **Evidence:** reviewer `rc8-absolute-cwd`; focused launcher tests; fresh review after this rework.

## Deliverable Path Check

- **Committed** — `scripts/run_crew.py`; `git check-ignore scripts/run_crew.py` exited 1.
- **Committed** — `tests/test_crew_worktree_cwd.py`; currently untracked until staged, and `git check-ignore tests/test_crew_worktree_cwd.py` exited 1.
- **Committed run artifact** — `.agent-work/commander-315-native/crew-handoffs/g1c-implementer-result.md`; `git check-ignore` exited 1.

## Required Evidence

Load-bearing:

1. Paste the red output from the new default-dot dispatch/resume coverage before production repair.
2. Run `python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py -q -p no:randomly` after repair.
3. Directly print `crew_cwd('.', Path('.'))`, its `is_absolute()`, and resolved repo equality.

Confirmatory: `git diff --check`; state exact files changed; run the full suite if time permits, otherwise the fresh reviewer owns the full-suite rerun already required by the gate.

## Wiring Grep
No new symbol. Re-run `grep -rn 'crew_cwd(' scripts/ | grep -v 'def crew_cwd'` and state the production call-site count; zero is a stop condition.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py -q -p no:randomly
git diff --check
```

## Suggested Model Tier
Simple bounded: one pure resolver and two targeted boundary tests, with exact reviewer evidence.

## Authority
Human settled options 1 + 2. Commander authorizes the reviewer-requested implementation repair within option 1. You own only the minimal resolver/test shape; do not alter policy or adjacent modules.

## Stop Conditions
Stop if the two-file scope is insufficient, preserving the legacy `None` behavior conflicts with absolute non-legacy paths, tests require weakening, or any new policy decision appears.

## Return Format
Write `IMPLEMENTER_RESULT` with completed slice, files changed, TDD red/green evidence, assumptions, stop conditions, out-of-scope observations, and workflow feedback to `.agent-work/commander-315-native/crew-handoffs/g1c-implementer-result.md`. `Return status` must be lowercase.
