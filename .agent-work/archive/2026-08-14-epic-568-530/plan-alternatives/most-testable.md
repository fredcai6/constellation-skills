# Plan alternative: most-testable

## Recommendation

Implement the narrow attribution fix in `scripts/hooks/spine_rail.py` and prove
it with one end-to-end linked-worktree regression in `tests/test_spine_rail.py`.
The resolved, validated spine path is the authority: for a checklist at
`<worktree>/.agent-work/<work-id>/<name>.json`, derive and normalize
`<worktree>` from the path itself. Do not use the hook payload `cwd`, the
observed `cd`, or the engine command's `--worktree` value for the stored
worktree. Keep release target resolution and the binding schema unchanged.

## Concrete implementation surface

1. Add a small pure helper near `_same_path` / the worktree-attribution section,
   e.g. `_owning_worktree(abs_spine)`. It should recognize the supported
   `.agent-work/<work-id>/<file>.json` shape, return a normalized absolute
   parent of `.agent-work`, and fail safely when the shape is not recognizable.
   This gives the fix a directly unit-testable contract without involving git
   or the engine.
2. In `handle_post_tool_use`, after `resolve_spine_candidate` returns a
   validated `abs_spine` for a claim, populate the binding entry's `worktree`
   from the helper. Preserve the current path-source and all other fields. A
   release still resolves/removes the recorded absolute entry first and keeps
   its existing behavior; do not re-derive or rewrite release records.
3. In `decide_session_start`, when the unambiguous `_scan_active_spine` path
   is bound, use the same helper for `worktree` rather than `data["cwd"]`.
   Existing bindings are read as-is, so this does not migrate or rewrite old
   records. If derivation cannot be made from a validated path, retain the
   hook's fail-open behavior (no crash/no blocking); do not guess from cwd.

## Discriminating test topology

Extend the focused helpers in `tests/test_spine_rail.py` only. Add pure cases
for the helper (a real absolute `.agent-work/work/spine.json`, a non-matching
path, and normalization) and assert that a claim entry records the owning
checkout even when payload `cwd` is deliberately different.

The acceptance case should be a real topology, not a hand-built binding:

* `_make_repo_with_worktree(tmp_path)` creates a committed git main checkout
  and a real linked worktree beside it. Put an active parent checklist only in
  main and an active child checklist only in the linked worktree (the existing
  `put_checklist` and `make_spine` helpers can create the state files).
* Feed production `handle_post_tool_use`/`PostToolUse` paths for both claims
  using one shared harness `session_id` but distinct `agent_id` values. The
  child payload's `cwd` must be the main checkout, with no `cd` and no
  `--worktree`; this forces resolution through `git_worktree_roots` and makes
  the old implementation store the demonstrably wrong main path. Assert the
  child composite key (`sid#child`) points to the child spine and records the
  linked worktree; assert the parent key records main.
* Drive the production Stop handler with a parent payload whose cwd is main.
  With both leases active, it must block for the parent's own spine while
  ignoring the child's foreign-worktree spine. Release only the parent through
  the production PostToolUse path, leave the child active, and invoke Stop
  again: it must now be non-blocking, while the child binding remains present
  and the child spine remains active. Include assertions on binding keys and
  the absence/presence of nudge records so the foreign-worktree guard—not an
  accidental missing binding—is what discriminates the result.
* Prefer a fresh subprocess invocation of `spine_rail.py` for the claim and
  Stop hook entry points (as the existing rung-4 test does), with
  `CLAUDE_PROJECT_DIR` set to main and no environment variable leaking the
  linked-worktree path. In-process assertions may inspect the resulting JSON
  and call pure readers, but the binding must be written by the production
  handler. On non-Windows, a failed real-worktree setup or regression is a
  failure; Windows may be recorded according to the launch order.

The test must assert both absolute spine paths differ and that the child path
is not the main decoy. It should run with `pytest -q tests/test_spine_rail.py`
and remain independent of engine JSON or checklist-engine CLI invocation.

## Risks and boundaries

* `Path.resolve()` and case/drive normalization differ across platforms; use
  the module's existing `_same_path` semantics and avoid changing path-source
  resolution. Keep the helper limited to the validated two-level
  `.agent-work` layout so unrelated absolute/release paths are not relabeled.
* The binding store's load-modify-save race, identity unification, reaping,
  schema migration, and all #441 behavior remain explicitly out of scope.
* A test that supplies the child worktree through payload fields, env, `cd`,
  `--worktree`, or a prewritten binding is non-discriminating and must be
  rejected in review. The old code must fail the new assertion by storing main
  as the child's worktree.
* Do not touch `.agent-work/epic-568-530/spine.json`, any engine/spine JSON,
  or use the checklist-engine CLI. Do not broaden changes beyond the rail and
  its focused tests.

## Expected result

READY-FOR-REVIEW when the real linked-worktree test is red on the base revision
and green with only the rail/test changes, the focused suite is green, and the
binding JSON demonstrates parent/child separation through Stop and release.
Return FLOAT (with the exact topology and failed assertion) if the base cannot
reproduce the wrong stored worktree; do not weaken the test into a synthetic
fixture.
