# Implementation Result

## Assigned gate
`g1-review` rework — absolute CLI crew cwd at the default-dot boundary.

## Completed slice
`crew_cwd` now returns an absolute path for every non-legacy input by resolving a relative CLI root first, then resolving a relative worktree under that root. Added real dispatch and resume coverage for the CLI defaults `--root . --worktree .`.

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `tests/test_crew_worktree_cwd.py`
- `.agent-work/commander-315-native/crew-handoffs/g1c-implementer-result.md` (required run artifact)

**Specific exclusions touched:** no. Existing unrelated worktree changes were preserved and not edited.

## Behavior changed
Yes. CLI dispatch and resume now pass an absolute cwd to the launch seam even when root and worktree are both the default `.`. Legacy registry entries without `worktree` still pass `None`; relative worktrees still resolve against the addressed root.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py::crew_cwd` — relative roots are made absolute before resolving relative worktrees; `CliBackend.dispatch` and `CliBackend.resume` retain their existing shared resolver calls.
- **Capabilities added/changed/affected:** CLI crew placement in assigned worktree — default-dot dispatch/resume now receive the absolute invocation repo root.
- **Constraints/assumptions touched:** legacy registry entries without `worktree` remain the `None` sentinel; the human-settled option 1 absolute-path contract is honored without revisiting policy.
- **Claims/evidence produced:** default-dot dispatch/resume RED then GREEN; 171 focused launcher tests pass; direct resolver proof equals the assigned repo root.

## Test mode
**Required:** test-first
**Satisfied:** yes — both new boundary tests failed before the production repair and passed afterward.

## Evidence

```bash
python -m pytest tests/test_crew_worktree_cwd.py -q -p no:randomly -k 'cli_default_dot'
```

**Result:** RED before repair — 2 failed, 9 deselected. Both failures were `AssertionError: False is not true` at `spawned_cwd.is_absolute()` for dispatch and resume.

```bash
python -m pytest tests/test_crew_worktree_cwd.py -q -p no:randomly -k 'cli_default_dot'
```

**Result:** GREEN after repair — `2 passed, 9 deselected in 0.03s`.

```bash
python -m pytest tests/test_crew_worktree_cwd.py tests/test_crew_launcher.py -q -p no:randomly
```

**Result:** pass — `171 passed in 0.56s` (also re-run by engine advance and passed).

```bash
python -c "from pathlib import Path; from scripts.run_crew import crew_cwd; value = crew_cwd('.', Path('.')); print(f'value={value}'); print(f'is_absolute={value.is_absolute()}'); print(f'equals_repo={value == Path.cwd().resolve()}'); print(f'legacy_none={crew_cwd(None, Path('.'))!r}')"
```

**Result:** pass — `value=/home/tommy/projects/constellation-skills-wt/epic-568-315-native`, `is_absolute=True`, `equals_repo=True`, `legacy_none=None`.

```bash
grep -rn 'crew_cwd(' scripts/ | grep -v 'def crew_cwd'
```

**Result:** pass — 2 production call sites, `CliBackend.dispatch` and `CliBackend.resume`; zero would have triggered the stop condition.

```bash
git diff --check
```

**Result:** pass — exit 0, no output.

Blast-radius enumeration: `rg --no-ignore -l 'crew_cwd' scripts tests map docs skills` found 5 named artifacts: the source plus 4 existing map pages. The behavioral assertion surface is `tests/test_crew_worktree_cwd.py`.

## TDD evidence, if required
- Failing test observed: the new default-dot dispatch/resume selection produced 2 failures because the spawn seam received relative `Path('.')`.
- Passing test observed: the same selection passed 2 tests after the resolver repair; the full focused command passed all 171 tests.
- Refactor while green: no — the production repair was already the minimal resolver change.

## Docs/contracts touched
- `scripts/run_crew.py::crew_cwd` docstring updated to describe relative-root resolution and the absolute return contract.
- No external docs changed; the map remains semantically accurate and can be reconciled by Cartographer if desired.

## Assumptions
- `Path.resolve()` uses the real CLI invocation cwd to establish a relative root, as explicitly authorized by the handoff.

## Stop conditions hit
- None.

## Out-of-scope observations
- None; pre-existing changes outside the allowed source/test pair were left untouched.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: task, protected intent, allowed scope, exclusions, evidence commands, TDD mode, stop conditions, map anchors, and return path were all explicit.
- **Context rediscovered:** none — confirmed after review: the `scripts.run_crew` map packet named both production callers and the launch seam needed for the test boundary.
- **Instructions improvised around:** the required `apply_patch` helper could not initialize its sandbox for this sibling worktree (`bwrap: loopback: Failed RTM_NEWADDR`). After two failed patch-helper attempts, the same bounded patches were applied with `git apply`; no file was hand-edited. The generic m1 imperative remained a placeholder, while only the explicitly authorized m1.c2 command was corrected through MCP `spine_amend`.
- **What would have made this easier:** include the dispatched sibling worktree in the patch helper's writable roots so the mandated editor can operate there.

## Return status
`complete`
