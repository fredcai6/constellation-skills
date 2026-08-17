# Fresh-process validation — 567-h (issue #442)

Per the dogfooding hazard (`docs/agents/ORCHESTRATOR_CONTEXT.md`): no source file was changed
this run (honest null at g1-measure-baseline), so there is no rewritten engine copy to prove —
this file exists to satisfy the launch order's Return Shape item 4/5 with real, fresh-subprocess
evidence anyway.

## Full suite, clean detached worktree, Linux

```
$ rm -rf /tmp/567h-suite-check && git -C /home/tommy/projects/constellation-skills/.worktrees/567-h-rail-readability worktree add --detach /tmp/567h-suite-check HEAD
Preparing worktree (detached HEAD f05a3d78)
HEAD is now at f05a3d78 chore(567): reconcile 7 overlay templates from repo source, promote 56 baselines

$ cd /tmp/567h-suite-check && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR python3 -m pytest -q
...
3352 passed, 6 skipped, 1219 subtests passed in 140.60s (0:02:20)

$ grep '^FAILED' /tmp/567h-suite2.log
(no output -- zero failures)
```

Tally matches the launch order's pre-dispatch baseline exactly (3352 passed, 6 skipped, 1219
subtests passed, 0 failed). `tests/test_code_map.py::MapTreeFreshnessTests` is included in this
count and passed (no exception needed — nothing here regenerated or touched `map/`).

**First attempt note (methodology, not a defect):** an initial run in the same detached worktree
without unsetting `CREW_SCRATCH_DIR` produced one failure
(`test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`,
asserting `CREW_SCRATCH_DIR` is absent from a subprocess env) — caused by this Commander's own
dispatched-crew environment variable leaking into the subprocess, not by any code change. Rerun
with `-u CREW_SCRATCH_DIR` (alongside the already-standard `-u SPINE_*` unset) reproduced the
clean baseline tally above. Worktree removed after both runs (`git worktree remove --force`).

Worktree cleaned up: `git worktree remove --force /tmp/567h-suite-check`.

## Rail-mechanism fresh-subprocess check (structural, content-agnostic)

Not gated in `execute.json` (its four crew/validate gates were amended out on g1's honest null,
so `verify_rail_fresh.py` was never wired as a live postcondition) — run here anyway as
corroborating evidence that the (unmodified) rail mechanism still behaves as documented:

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-h-rail-readability && python3 .agent-work/567-h/verify_rail_fresh.py
OK: fresh-subprocess 'early' rail check passed: RAIL: Work the engine never saw did not happen. Run the step's checks, then `attest` and `advance g1`.
```

## Tracked-file diff

```
$ git status --porcelain
?? .agent-work/567-h-execute/
?? .agent-work/567-h/
```

Zero tracked files changed. `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`, and
`docs/CHECKLIST_ENGINE_DESIGN.md` are byte-identical to base commit f05a3d78.
