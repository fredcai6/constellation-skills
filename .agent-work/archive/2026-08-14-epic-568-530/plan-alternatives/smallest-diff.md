# Candidate: smallest-diff

## Recommendation

Implement one narrowly scoped ownership helper in scripts/hooks/spine_rail.py
and use it at the two existing binding-write sites. The helper should accept
the already resolved, validated abs_spine and derive the normalized owning
worktree from the supported .agent-work/<work-id>/ layout (the worktree root
is the parent above .agent-work). This keeps the resolved spine as the sole
source of truth and avoids changing binding shape, candidate resolution,
release lookup, or lifecycle policy.

## Concrete implementation surface

- scripts/hooks/spine_rail.py: add a small private helper near the existing
  worktree-attribution functions, with a name such as
  _worktree_from_spine(abs_spine). Normalize the result using the module's
  existing path conventions (Path(...).resolve()/string form) and fail closed
  or return no ownership if the path does not have the supported
  .agent-work/<work-id>/... ancestry.
- In handle_post_tool_use, after resolve_spine_candidate (or recorded release
  resolution) has produced abs_spine, replace only the claim entry's
  "worktree": cwd value with the helper result. Leave spine,
  engine_session, claimed_at, and path_source unchanged. Do not alter the
  release path: release still resolves against recorded absolute spine keys.
- In decide_session_start, replace only the bind-on-unambiguous-scan entry's
  "worktree": data.get("cwd") or str(project_dir) with the same helper over
  own_spine_path. This makes claim and resume bindings agree without changing
  the SessionStart read/foreign-worktree filtering behavior.
- tests/test_spine_rail.py: retain existing helper fixtures and production
  handler calls; add the smallest regression around _make_repo_with_worktree
  and the real git worktree list path. No engine/spine JSON files are edited
  by this plan, and no files outside the rail and its focused tests are in
  scope.

## Discriminating test topology

Build a real git main checkout plus a real linked worktree using the existing
_make_repo_with_worktree(tmp_path). Put a valid active JSON checklist under
.agent-work/<work-id>/spine.json in the linked worktree and, where needed for
the parent comparison, a separate active checklist in main. Use one shared
session_id, distinct parent/child agent_id values from the pinned payload
fixtures, and deliberately set the child PostToolUse payload cwd to the main
checkout. The command must contain only the relative
.agent-work/<work-id>/spine.json and claim; it must contain neither cd nor
--worktree, and the linked-worktree path must not leak through payload or
environment. Drive handle_post_tool_use (or its fresh-subprocess wrapper) so
the path is resolved by the production candidate ladder, then assert the
binding's absolute spine is the linked file and its stored worktree is the
linked root, not payload cwd.

Exercise the guard through decide_stop: from the main checkout, the parent
Stop must not block on the active child entry because _foreign_worktree sees
the child root; after a parent claim and release, the parent Stop remains
non-blocking while the child entry remains active. Also exercise
decide_session_start with an unambiguous scan/bind-on-resume case (or a
separate minimal linked-worktree fixture) and assert its newly written binding
uses the owning root derived from own_spine_path, not the SessionStart
payload cwd. Keep same-worktree and missing-cwd controls from the existing
tests to prove the guard is not weakened.

The red proof is the pre-fix assertion that the child binding records main
cwd; the green proof is the same production topology asserting the linked
root, followed by Stop/SessionStart/release assertions. Run the focused suite
pytest -q tests/test_spine_rail.py; local/non-Windows failures are blocking.

## Risks and boundaries

- The helper depends on the declared JSON checklist layout. Refuse malformed
  or out-of-layout paths rather than guessing from cwd; this preserves the
  fail-open hook contract while avoiding a new misattribution.
- Deriving from abs_spine must not use observed cd, --worktree text, or
  payload cwd, and must not change the candidate ladder's precedence or
  ambiguity refusal.
- Do not introduce locking, identity unification, reaping, schema migration,
  release-semantic changes, or #441 work. Do not touch engine/spine JSON or use
  checklist-engine CLI.
- The test must prove the linked root is discovered from real git topology,
  rather than injecting it through a payload field, environment variable,
  monkeypatch, or fixture shortcut; otherwise it cannot distinguish the old
  wrong-cwd writer from the corrected one.

## Why this is the smallest diff

It changes one derived value at two existing writers and adds one shared
derivation seam plus a focused regression. It preserves the binding schema and
all read/release behavior, so the blast radius is limited to worktree
attribution for validated claim and bind-on-resume records. Candidate A in
PLAN_ALTERNATIVES.md independently identifies this same one-helper seam;
this candidate makes its exact symbols, topology, and stop conditions
implementable.

