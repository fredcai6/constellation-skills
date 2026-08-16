Return status: complete

# IMPLEMENTER_RESULT — g2 (issue #525)

## Summary

Added `scratch_dir(work_id, gate, role, worktree, attempt, root) -> Path` to
`scripts/run_crew.py`, placed immediately after `run_log_paths`. It is keyed
on the FULL `(work_id, gate, role, worktree, attempt)` 5-field tuple — the
same tuple `active_duplicate`/`next_attempt` already use — and hashes
`worktree` as the **raw string exactly as recorded** (never resolved to an
absolute path), matching `active_duplicate`'s/`next_attempt`'s own raw-string
equality semantics. Path shape:
`.agent-work/<work_id>/crew-scratch/<gate>-<role>-attempt-<attempt>-<wtkey>/`
where `<wtkey> = hashlib.sha256(worktree.encode("utf-8")).hexdigest()[:12]`.

`CliBackend.dispatch` reserves this directory via
`Path.mkdir(parents=True, exist_ok=False)` **before** `build_entry`/
`entries.append`/`save_registry` run, so a genuine collision (`FileExistsError`)
leaves no partial "running" entry in the registry — it raises `CrewLaunchError`
naming the colliding path and the full tuple, and the child is never spawned.
`CliBackend.resume` only **gets** the path (recomputes via `scratch_dir()`,
never reserves/raises-on-exists) since a resume re-enters the same attempt —
an existing directory there is expected and correct. A legacy entry with no
stored `"worktree"` key degrades to leaving `CREW_SCRATCH_DIR` unbound on
resume (mirrors `crew_cwd`'s existing degrade-to-`None` behavior for the same
case), rather than raising.

`CREW_SCRATCH_DIR` was added to `crew_env`/`_crew_door_env`, assigned the
same way as the `spine_file`/`spine_session` pair (bound when given, inherited
route untouched when omitted) — wired into both `CliBackend.dispatch` and
`CliBackend.resume`, never into `ExternalBackend` (which spawns no process and
builds no environment, matching how it already gets no `SPINE_FILE` today).

`build_entry` gained an optional `scratch: str | None = None` parameter,
recorded on the entry as `"scratch_dir"` (relativized against `root`, same
`_relativize` used for `handoff`/`result`/`spine`) using the "recorded when
present" shape (matches `model`, not `spine`'s "recorded null" shape), since
only the cli backend (the one path that reserves a scratch dir) ever has a
value to give.

`run_log_paths` itself, `scripts/checklist_engine.py`, and
`scripts/recover_crews.py` were left untouched (confirmed `recover_crews.py`
is a pure read-side classifier with no scratch-dir awareness needed; no
change was made there). G1's parent-lease heartbeat code and tests
(`scripts/run_crew.py`, `tests/test_crew_launcher.py`) were left exactly as
found — only added to, never reverted.

## Files changed

- `/home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling/scripts/run_crew.py`
  - `import hashlib` added.
  - New `scratch_dir()` function (near `run_log_paths`).
  - `crew_env()` / `_crew_door_env()` gained a `scratch_dir` parameter, bound
    into `CREW_SCRATCH_DIR` when given.
  - `build_entry()` gained a `scratch` parameter, recorded as `entry["scratch_dir"]`
    when truthy.
  - `CliBackend.dispatch`: reserves the scratch dir (`mkdir(exist_ok=False)`)
    before any registry write; raises `CrewLaunchError` on collision; passes
    the reserved path into `build_entry` and `_crew_door_env`.
  - `CliBackend.resume`: recomputes (gets, does not reserve) the same path
    from the stored entry's tuple; degrades to no `CREW_SCRATCH_DIR` for a
    legacy entry with no stored `worktree`.
- `/home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling/tests/test_crew_launcher.py`
  - `import hashlib` added.
  - Four new `unittest.TestCase` classes appended before `if __name__ == "__main__":`:
    - `ScratchDirPureFunctionTests` (7 tests) — path shape; disjoint on
      differing gate/role/attempt/worktree (including the same-attempt,
      different-worktree regression the handoff calls out by name); raw-string
      hashing (not path resolution); determinism.
    - `ScratchDirReservationTests` (5 tests) — directory created on disk;
      `CREW_SCRATCH_DIR` present in the CLI child's env; registry entry
      records `scratch_dir`; the before/after demonstration (two crews that
      would have shared one generic path now get disjoint reserved paths);
      disjoint reserved directories for same gate/role/attempt but different
      worktree.
    - `ScratchDirCollisionTests` (3 tests) — forced collision raises
      `CrewLaunchError` naming the path and full tuple; leaves no partial
      registry entry; never disturbs the pre-existing directory's contents.
    - `ScratchDirResumeTests` (3 tests) — resume against an existing
      directory does not raise; resume's env carries the same reserved path
      as the original dispatch; legacy entry without a stored `worktree`
      degrades gracefully (no `CREW_SCRATCH_DIR`, no crash).

## Required Evidence

### Test run

```
$ find . -name __pycache__ -exec rm -rf {} +
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
........................................................................ [ 34%]
........................................................................ [ 69%]
..............................................................           [100%]
206 passed in 0.77s
```

(188 from g1 + 18 new tests for this gate = 206.)

### Concrete before/after demonstration

Ran a standalone script (module-loaded `run_crew.py`, real `launch_crew`
calls, fake `launch_process` seam — no real subprocess) that dispatches two
crews sharing `work_id`/`gate`/`worktree`/`attempt` but different `role`:

```
=== BEFORE/AFTER: two crews that used to collide now write disjoint reserved paths ===
OLD scheme (pre-#525-fix): both crews wrote into one generic shared path, e.g. 'SHARED/scratch' -- no per-dispatch namespace existed at all.

NEW scheme (this gate):
  implementer crew scratch_dir  : .agent-work/issue-1/crew-scratch/g2-implementer-attempt-1-cdb4ee2aea69
  reviewer crew scratch_dir     : .agent-work/issue-1/crew-scratch/g2-reviewer-attempt-1-cdb4ee2aea69
  disjoint?                     : True
  implementer CREW_SCRATCH_DIR env: /tmp/tmp419oh0h6/.agent-work/issue-1/crew-scratch/g2-implementer-attempt-1-cdb4ee2aea69
  reviewer CREW_SCRATCH_DIR env   : /tmp/tmp419oh0h6/.agent-work/issue-1/crew-scratch/g2-reviewer-attempt-1-cdb4ee2aea69
  both directories exist on disk: True True
```

### Forced collision — exact `CrewLaunchError` message

```
=== FORCED COLLISION: exact CrewLaunchError message ===
CrewLaunchError message:
  scratch directory collision: /tmp/tmp419oh0h6/.agent-work/issue-2/crew-scratch/g3-implementer-attempt-1-cdb4ee2aea69 already exists for (work_id='issue-2', gate='g3', role='implementer', worktree='.', attempt=1) -- refusing to silently reuse or overwrite another dispatch's evidence (issue #525)
child ever spawned?          : False
pre-existing evidence intact?: True
registry file created despite the collision?: False
```

The message names both the colliding path and the full 5-field tuple; the
child is never spawned; the pre-existing directory's contents are left
untouched; and no registry entry (not even a partial one) is written for the
refused attempt.

## Wiring Grep

```
$ grep -rn "scratch_dir\|CREW_SCRATCH_DIR" --include=*.py . | grep -v "def scratch_dir" | grep -v "^\./tests/"
```

17 matching lines, all in `scripts/run_crew.py`, all inside this gate's own
Allowed Scope:
- 10 are real code sites: the `crew_env`/`_crew_door_env` parameter
  declarations and their `if scratch_dir is not None:` / assignment bodies,
  the two `crew_env(...)` call sites inside `_crew_door_env`, the
  `entry["scratch_dir"] = ...` assignment in `build_entry`, the
  `scratch_dir(...)` call sites in `CliBackend.dispatch` and
  `CliBackend.resume`, and the `scratch_dir=...` kwargs passed into
  `_crew_door_env` from both.
- 7 are docstring/comment prose referencing the new name for context.

Zero references outside `scripts/run_crew.py` and outside the test file —
`scripts/checklist_engine.py`, `scripts/recover_crews.py`, and every other
`.py` file in the repo are untouched by this gate.

## Deliverable Path Check

```
$ git check-ignore -v scripts/run_crew.py; echo "exit=$?"
exit=1
$ git check-ignore -v tests/test_crew_launcher.py; echo "exit=$?"
exit=1
```

Both committed (not git-ignored), as required.

## Scope notes

- `run_log_paths` itself was NOT touched — its narrower, pre-existing,
  out-of-scope asymmetry (it doesn't key on `worktree`) is left exactly as
  found, per the handoff's explicit exclusion.
- `scripts/recover_crews.py` was NOT touched — confirmed (not assumed) it is
  a pure read-side classifier with no scratch-dir awareness needed for this
  gate.
- `ExternalBackend` was NOT wired to `CREW_SCRATCH_DIR` or `scratch_dir()` —
  it spawns no process and builds no environment (same reason it carries no
  `SPINE_FILE` today); the handoff's Close Criteria named only
  `CliBackend.dispatch`/`CliBackend.resume` for this wiring.
- No attempt was made to make any dispatched crew's own skill actually WRITE
  into `CREW_SCRATCH_DIR` — that remains the distinct, unowned follow-up the
  handoff names as out of scope.
- g1's parent-lease heartbeat code and tests (issue #607, already present in
  this worktree before this gate started) were left untouched — only added
  to, never reverted or modified.

## Stop conditions hit

None. The mechanism specified in the handoff (5-field key tuple including
worktree, raw-string hashing, dispatch-reserves/resume-gets,
`CrewLaunchError` on collision, `CREW_SCRATCH_DIR` env var name) was
implementable as decided; no redesign or authority-exceeding decision was
needed.
