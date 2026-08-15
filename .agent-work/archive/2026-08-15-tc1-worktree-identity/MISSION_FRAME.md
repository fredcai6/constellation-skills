# Mission Frame

Shrunk deliberately. This run implements a fully-specified Admiral ruling
(`/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`),
not an open design question — the map adds nothing a source read of the two
named files (`scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py`)
does not already give directly, and `map/INDEX.md` carries no citable anchor
ids for this repo (context step: map orientation is DEGRADED-UNPARSEABLE,
discharged with `map/INDEX.md` as substitute — see
`.agent-work/tc1-worktree-identity/map-orientation.json`). Design-it-twice and
the cold plan critic are both skipped as **named untaken roads**: the ruling
already forecloses the alternatives (options a/b in `decision:git-not-lexical`
are explicitly rejected) and specifies the implementation to the level of the
exact comparison operator and call site line.

## Intent
Replace containment (`here.is_relative_to(root)`) with git-worktree-identity
equality in `checklist_engine.origin_worktree_refusal`'s single call site, so a
primary-stamped spine is no longer drivable from inside any nested worktree
(the regression introduced by #585's `<root>/.worktrees/<slug>` layout).
Migrate exactly one test property (subdirectory-passes) up from the pure
predicate to a `main()`-level real-git-repo assertion, per the ruling's
authorized deviation. Everything else in the test file is unaffected in intent.

## Affected Capabilities
- `scripts/checklist_engine.py::origin_worktree_refusal` (predicate, ~L102-161) — stays pure, comparison changes from containment to equality.
- `scripts/checklist_engine.py::main` (call site, ~L3393-3416) — gains the one impure git-toplevel resolution this predicate now needs.
- `tests/test_spine_origin_isolation.py` — synthetic predicate-level tests move to equality semantics; the subdirectory property re-asserted through `main()` against a real temp git repo; new regression test for the nested-worktree case; new test for the fail-closed no-git-toplevel case.

## Structural Anchors
- `scripts/checklist_engine.py` — single impure call site at `main()`, confirmed via `grep -n origin_worktree_refusal` (exactly two hits: def + call).
- `tests/test_spine_origin_isolation.py` — three-part test file (write side / pure predicate / call-site-through-`main()`), read in full at `understand`.
- `scripts/checklist_engine.py::_git` (~L701) — existing subprocess-git helper, reused for the new toplevel resolution rather than adding a second git-invocation path.

## Governing Constraints / Assumptions
- `test_it_is_pure` (co_names-based) must stay green **unmodified** — the predicate takes no new forbidden name.
- `OriginRefusalFallback` must stay green — every malformed/absent origin shape still falls back without raising, regardless of the new `cwd: str | None` type.
- Fail-closed: no git toplevel resolvable for cwd + spine carries `origin.worktree` ⇒ refused (ruling part 3).
- No migration of `origin.worktree` values themselves (pre-ruling 3, `decision:no-migration`).
- `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, `.mcp.json`, `.worktrees/epic-568-441/` are NOT to be edited (File Ownership, LAUNCH_ORDER).

## Decision Anchors & Decision Pressure
- decision:git-not-lexical — the call site resolves cwd via git worktree toplevel, not lexical containment or an exported `--from`.
  @grade: settled/human · leans g1-implement · settle: n/a, ruled by the human 2026-08-15 ("c is cool")
- decision:forgery-stays-open — chdir-into-the-stamped-worktree still passes; not closed by this change.
  @grade: settled/human · leans g1-implement
- decision:no-migration — `origin.worktree` values are immutable; no rewriting/backfill.
  @grade: settled/human · leans g1-implement
- decision:test-migration-authorized — the subdirectory-passes property is authorized to move from the pure predicate to a `main()`-level real-git-repo assertion; this is the one authorized exception to "test intent never changes".
  @grade: settled/human · leans g1-implement

No decision pressure — the ruling leaves no open choice within this run's scope.

## Claims / Evidence Surfaces
- claim: nested-worktree regression — a primary-stamped spine driven from inside a nested worktree is refused after the change and was allowed before. Checked by a new permanent regression test plus a manually-captured red/green pair reported in this run's evidence.
- claim: `test_it_is_pure` unmodified and green — checked by `git diff` showing zero changes to that test method, plus a green run.
- claim: cache-clean full suite matches or exceeds the measured baseline (3002 passed, 7 skipped, 0 failed, 1130 subtests passed at `453f8492`) — checked by a cache-clean full-suite run after the change.

## Map Confidence / Staleness / Disputes
- `map/ids.jsonl` is empty repo-wide (0 decision anchors) and `map/INDEX.md` carries no citable anchor id format `map_orient.py` recognizes — this is a genuine repo-wide gap, not specific to this run's area, already surfaced at `context` via the DEGRADED-UNPARSEABLE receipt. Does not alter this plan: the ruling document is the authoritative spec here, not the map.

## Out of Scope
- `scripts/hooks/spine_rail.py` lexical/git split — documentation-only per the ruling, recorded in findings, not code (and explicitly not-mine to edit).
- Closing the forgery hole (`decision:forgery-stays-open`) — separate design change, out of scope.
- Any change to `scripts/mcp_spine_server.py`, `.mcp.json`, or `.worktrees/epic-568-441/`.
