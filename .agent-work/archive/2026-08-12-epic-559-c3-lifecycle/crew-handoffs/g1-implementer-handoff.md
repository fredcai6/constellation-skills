# Implementer Handoff — g1: open

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g1` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander. Ask up to
it, not past it. It is your reachable tier for anything this handoff does not settle.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g1-implementer-result.md`

## Read first

`.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` — **sections 2 and 3 are your specification.**
Where this handoff and that contract disagree, the contract wins. Read §1b too: four of its decisions came
from a cold critic and the reasons matter.

## Task

Create `scripts/spine_lifecycle.py` and `tests/test_spine_lifecycle.py`. **This gate ships `open_work` and
the pure helpers only. `close_work` is g2 and no door wiring happens here.**

### The pure helpers (no `Path`, no `open`, no `subprocess`)

- `worktree_path_for(work_id, *, wt_root) -> str`
- `branch_name_for(work_id) -> str` — the `work_id` verbatim.
- `archive_name_for(work_id, *, today) -> str` — `<YYYY-MM-DD>-<work_id with "/" replaced by "-">`.
  `today` is a **parameter**, never read inside, so a test never freezes a clock. (g2 uses it; ship it
  here with its tests because it is pure and belongs with its siblings.)
- `build_origin(...) -> dict` — the block in §3.

`worktree_path_for` derives `<wt_root>/<last segment of work_id>`; `wt_root` defaults to a sibling of the
main checkout named `<repo-dir>-wt`. Measured against the live tree: this run's own worktree is
`/home/tommy/projects/constellation-skills-wt/c3-lifecycle` for work id `epic-559/c3-lifecycle`, so the
default must reproduce exactly that.

### `open_work(work_id, spec, *, root, base, parent, wt_root=None)`

The order in §3, and **nothing survives a failure**:

1. Validate `work_id`. **Reuse `run_crew.py`'s existing work-id validator — never write a second one.**
   Refuse an unsafe id by name.
2. Refuse if the derived worktree path already exists on disk.
3. Refuse if any spine for this `work_id` carries an `engine_session` whose `status` is `"active"`.
   **`"active"` and `"released"` are the only two statuses `checklist_engine` ever writes** (`:1033`,
   `:1076`) — there is no "abandoned" `engine_session`; that field belongs to `crew-runs.json`, not here.
   Scan read-only and fully defensively, in the style of `agent_work_root._active_epic_lease`.
4. `git worktree add <worktree> -b <branch> <base>`.
5. Scaffold the work area — reuse `init_work_area.init_work_area`.
6. Compile the spine — reuse `generate_spine`, **imported, never re-implemented**. Write it as
   `spine.json` inside the new work area.
7. Inject the top-level `origin` block into the written spine, then **re-run
   `validate_spine.validate` on the result**, so the record cannot make the spine invalid.
8. **Self-verify**: call `verify_worktree_isolation.check_distinct_real([worktree],
   registered_worktrees(), primary_checkout())` in-process. `git` returning 0 is not evidence.
9. Return the crew-binding values: `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT`, branch, worktree.

**Rollback.** Any failure at or after step 4 removes the worktree (`git worktree remove --force`, then
`git worktree prune`) **and deletes the branch this call created**, then refuses legibly. Rollback is
scoped to what this call created — a pre-existing unrelated worktree or branch is never touched.

## Protected intent

An agent creates work the same way it drives work — in one call. A caller that must already know the
branch and worktree convention has not been given one call. And **a worktree without a spine, or a spine
without a worktree, is the state that produces every mismatch this epic has chased** — so a half-success
is worse than a refusal.

## Test mode

Test-after allowed, but **every guard needs a violating case**. House style:
`tests/test_mcp_adoption.py::_cli_only_verb_violations` — VIOLATING / INNOCENT. A test that exercises
only the happy path measures the mechanism, not the boundary.

Tests must build their own throwaway git repo under `tmp_path` and never touch this worktree's real git
state. Rollback tests must assert against **`git worktree list --porcelain`**, not against an assertion
string the code under test produced.

## Close criteria

- `open_work` refuses an occupied worktree path, by name — VIOLATING fixture.
- `open_work` refuses a work id whose spine carries an `engine_session` with `status == "active"`, by
  name — VIOLATING fixture. An INNOCENT case: the same work id whose only spine is `"released"`.
- A **late** failure after `git worktree add` leaves **no worktree and no branch** — VIOLATING fixture
  that forces the failure at step 6 or 7, then asserts the worktree is absent from
  `git worktree list --porcelain` and the branch is absent from `git branch --list`.
- `check_distinct_real` returning not-ok forces a rollback **even though `git worktree add` exited 0** —
  VIOLATING fixture. This is the property the launch order names explicitly.
- Rollback is scoped: a pre-existing unrelated worktree survives a failed open of a different work id —
  INNOCENT fixture.
- The `origin` block survives a real `claim → start → attest → advance` drive byte-identical.
- The pure helpers are tested directly, with `today`/`wt_root` passed in.
- `worktree_path_for("epic-559/c3-lifecycle", wt_root=<default>)` reproduces this run's own real worktree
  path.
- The whole suite is green and `python scripts/validate_spine.py --sweep --root .` still reports
  **exactly 23** fault lines.
- The code map is regenerated (`python -m scripts.code_map build`) because this gate adds a module.
  **Never hand-edit `map/INDEX.md`.**

## Allowed scope

`scripts/spine_lifecycle.py` (new) · `tests/test_spine_lifecycle.py` (new) · `map/` (regenerated only,
never hand-edited). You may **read** anything.

## Specific exclusions

- **`close_work` is g2's.** Ship `archive_name_for` (pure) and nothing else about closing.
- **No door wiring.** `scripts/mcp_spine_server.py` is g3's and must not be touched here.
- `scripts/generate_spine.py` is g4's and g5's — **import it, do not edit it.**

## Constraints — a violation voids the gate

- `scripts/checklist_engine.py`'s on-disk format is **not** changed. `scripts/validate_spine.py` is
  **not** changed.
- `settings.json`, `.mcp.json` and `docs/agents/*` untouched. **If the harness refuses an `Edit`/`Write`
  on `.mcp.json`, that guard is deliberate — do not route around it with a `Bash` write. Block and ask
  the Commander.**
- `skills/**` untouched. If you find a `skills/` file that must change, **block and say so** — a
  different crew owns that tree and a second writer would collide.
- Never run `scripts/install_constellation.py`.
- No merge and no push to `main`. Commit locally only.
- Never `git add -A` and never a bare `.` — stage by name.
- Never two crews in one worktree.

## Deliverable path check

- **Committed** — `scripts/spine_lifecycle.py`; `git check-ignore scripts/spine_lifecycle.py` exits **1**
  (not ignored), verified before dispatch.
- **Committed** — `tests/test_spine_lifecycle.py`; `git check-ignore` exits **1**, verified.
- **Local-only** — your result artifact under `.agent-work/`; the Commander commits it.

Both source files are **new**, so they appear in `git status`, not in `git diff`, until staged.

## Required evidence

Load-bearing — prove these rigorously, they are what the gate is for:

1. The rollback fixtures, with the **actual `git worktree list --porcelain` output** before and after
   pasted into your result.
2. The `check_distinct_real`-says-no-despite-git-exit-0 fixture.
3. The `origin` round-trip through a real engine drive.

Confirmatory — a spot-check suffices: the pure helpers, the suite total, the sweep count.

Verification commands, POSIX form, absolute paths:

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

**Baseline on this branch before your change: 2824 passed, 3 skipped, 1121 subtests; sweep exactly 23.**
Use `python`, never `python3` — `python3` on this host has no pytest.

## Stop conditions

- A constraint above would have to be violated → **block**, name it, return.
- The `origin` round-trip does not survive → that refutes a load-bearing plan measurement. **Block and
  say so with the output** — a measured negative is a complete deliverable, not a failure.
- Two failed attempts at the same check → block rather than a third.
- **Never waive.** A crew cannot waive its own bound spine check; call `spine_halt` with
  `action=block`, name what you cannot satisfy, and return.

## Return format

Write the result artifact at the path above **before ending your turn** — that write is the delivery. It
must carry a **`Return status`** field whose value is exactly `complete` (lowercase) when the gate is
done, plus what you built, the evidence above pasted verbatim, anything you could not do, and a short
**Workflow Feedback** section. Return thin: the verdict, the deciding evidence, and the path.
