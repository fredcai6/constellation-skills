# REVIEW_RESULT

Verdict: **APPROVE**

Reviewed commit: `97eb5d34` (`fix(530): derive binding worktree from spine path`)

## Per-check findings

1. **Scoped diff and helper contract — PASS**
   - `git show`/`git diff` confirms the commit changes only the allowed files:
     `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`.
   - `_worktree_from_spine(abs_spine)` is lexical and uses only `abs_spine`.
     It requires a string, an absolute path, a nonempty `.json` filename, one
     work-id directory, and an immediate `.agent-work` parent; invalid and
     out-of-layout inputs return `None` with no cwd fallback.
   - The helper derives the owner as the parent of `.agent-work`, preserving
     usefulness after checklist archival/deletion.

2. **Writer wiring — PASS**
   - The claim writer derives `worktree` from the resolved `abs_spine` and
     returns without binding if attribution is invalid.
   - The unambiguous SessionStart scan writer derives `worktree` from its
     discovered absolute spine path and returns without binding if attribution
     is invalid.
   - Neither writer uses payload cwd or `project_dir` as an ownership fallback.

3. **Real linked-worktree regression — PASS**
   - The regression creates a real repository plus linked worktree, shares one
     harness session between parent and child, and uses distinct parent/child
     agent ids.
   - The child payload deliberately carries stale main-checkout cwd. Its
     relative claim contains neither the child path, `cd`, nor `--worktree`, so
     the production git-worktree resolution rung must discover the child.
   - The recorded child binding identifies the linked worktree, not stale cwd.
   - Parent Stop blocks while the same-worktree parent binding is active. After
     the parent releases, parent Stop is non-blocking while the child spine is
     still active and its binding is foreign. SessionStart against the child
     worktree also records the child owner from the discovered spine path.

4. **Negative helper coverage — PASS**
   - Tests accept an absolute `.agent-work/<work-id>/<name>.json` path and reject
     non-string, relative, non-JSON, missing-work-id, and wrong-layout inputs.

5. **Independent test evidence — PASS**
   - `python -m pytest -q -vv tests/test_spine_rail.py -k
     'worktree_from_spine_accepts_only_absolute_agent_work_json_layout or
     binding_worktree_comes_from_resolved_spine_in_real_linked_worktree'`
     -> `2 passed, 110 deselected in 0.05s`.
   - `python -m pytest -q tests/test_spine_rail.py`
     -> `111 passed, 1 skipped in 0.28s`.
   - `git diff --check 97eb5d34^ 97eb5d34 -- scripts/hooks/spine_rail.py
     tests/test_spine_rail.py` produced no errors.

## Blockers

None.

## Out-of-scope observations

- No changes were made to release-target resolution, binding schema, locking,
  identity, reaping, lifecycle policy, or #441 behavior.
- I did not inspect or modify engine/spine JSON and did not edit source/tests.

## Workflow feedback

- The handoff was sufficient for a source-level and independently reproduced
  review; no review survey was needed.
- The required test command is reliably available as `python -m pytest` in this
  environment.
