# Reviewer Handoff

## Gate
g1-implement (reviewing)

## Survey State Location
`.agent-work/567-j/g1-review/review.json`

## What Was Implemented
`scripts/install_constellation.py`'s real (non-`--dry-run`) CLI install no
longer rewrites the installer checkout's own tracked `.mcp.json` when the run
declares a destination elsewhere (`--dest`, or `--project` pointing somewhere
other than this checkout's own default). A plain self-install (no
`--dest`/`--project`) still wires it automatically, exactly as before. Fixes
the confirmed bug from #619 where `--dest /tmp/...` (entirely outside the
repo) still mutated the calling checkout's own `.mcp.json`.

## How to Inspect the Diff
This worktree's **uncommitted working tree** — not `git diff main...HEAD`.
`git status --porcelain` then `git diff scripts/install_constellation.py
tests/test_install_constellation.py` (both files were modified, not added, so
`git diff --name-only` would suffice here too, but use the untracked-safe
form as a habit).

## Task Statement
Add a pure `is_self_install(args) -> bool` predicate
(`args.dest is None and args.project is None`); gate the
`apply_repo_mcp_config_wiring(...)` call in `main()`'s tail so the **entire
call is skipped** (not just its path argument changed) unless
`mcp_config_path is not None or is_self_install(args)`; add a regression test
proving a real `--dest`-elsewhere run leaves a fixture `.mcp.json` (standing
in for "this checkout's own file") byte-identical; update only the docstring
of `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`
(its assertion body must stay unchanged, since `default_mcp_config_path()`
itself is untouched and still pure).

## Close Criteria
- `is_self_install` exists, is pure (no I/O), and returns exactly
  `args.dest is None and args.project is None`.
- `apply_repo_mcp_config_wiring` is **never called with `mcp_config_path=None`**
  anywhere in `main()` — confirm by reading the exact guard line, not by
  running the tests alone (a guard that merely swaps the *value* passed while
  still always calling the function would still pass a naive test but crash
  on a real `--dest`-elsewhere run with no `mcp_config_path` override).
- Every pre-existing `RepoMcpConfigWiringTests` case is present, unmodified,
  and green (they all pass an explicit `mcp_config_path` fixture, so the new
  guard's `mcp_config_path is not None` branch must be what keeps them
  passing).
- The new byte-identical test genuinely exercises the **real** CLI-entry-point
  code path (`main()` with `wire_repo_mcp_config=True`, **no**
  `mcp_config_path` override — the shape `if __name__ == "__main__":` uses) —
  not a version that passes an explicit `mcp_config_path` and would therefore
  pass regardless of whether the fix works.
- `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`'s
  **assertion** (`installer.REPO_ROOT / ".mcp.json" == installer.default_mcp_config_path()`)
  is byte-for-byte unchanged; only its docstring was edited.
- Full suite: `py -m pytest tests/test_install_constellation.py -q` green.

## Allowed Scope
- `scripts/install_constellation.py` — `is_self_install` addition and the
  `wire_repo_mcp_config` guard in `main()`'s tail only.
- `tests/test_install_constellation.py` — new tests plus the one docstring
  edit named above.

## Specific Exclusions
- `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  any `*SPINE*.template.json`, `specs/` — fenced to lane K this wave; flag if
  touched (not expected).
- `default_mcp_config_path()`'s own signature/behavior — must be unchanged.

## Constraints the Implementation Must Respect
- `apply_repo_mcp_config_wiring`'s first positional parameter is a `Path`,
  never `None`, at any call site.
- No new file created; both files are modifications to existing tracked
  files (confirm via `git status --porcelain` showing `M`, not `??`, for
  both).

## Map Anchors (inbound)
No architecture map exists in this repo — DEGRADED-UNPARSEABLE, waived by the
Admiral this wave (evidence `e-plan-1` on the parent spine,
`decision:map-index-is-admiral-owned`). Read `scripts/install_constellation.py`
directly starting at `default_mcp_config_path`, `apply_repo_mcp_config_wiring`,
and `main()`'s tail.
- **Decision anchor:** `decision:map-index-is-admiral-owned` — do not
  regenerate/hand-edit `map/INDEX.md`. `@grade: settled/doctrine`

## Evidence Produced
See `.agent-work/567-j/crew-handoffs/g1-implement-result.md` for the full
IMPLEMENTER_RESULT: `py -m pytest tests/test_install_constellation.py -q` ->
206 passed, 506 subtests passed; a TDD red/green proof (guard reverted to
unconditional, new test fails with the exact wrong-.mcp.json assertion error;
guard restored, full suite green); a wiring grep showing `is_self_install`'s
one non-test call site. This evidence targets `g1-integrate.c1`.

## Suggested Model Tier
sonnet — bounded verification task, existing test patterns to check against.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, the evidence in
IMPLEMENTER_RESULT does not reproduce when you re-run it, or
`apply_repo_mcp_config_wiring` is ever reachable with `mcp_config_path=None`.

## Return Format
Return REVIEW_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g1-reviewer-result.md` before
ending your turn.
