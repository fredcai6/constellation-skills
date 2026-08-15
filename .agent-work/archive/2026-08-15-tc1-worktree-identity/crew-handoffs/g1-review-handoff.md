# Reviewer Handoff

## Gate
g1

## Survey State Location
Create your review survey checklist at `.agent-work/tc1-worktree-identity/g1-review/review.json`.

## What Was Implemented
The Admiral ruling at
`/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`
(read it in full first). `checklist_engine.origin_worktree_refusal` now compares
worktree identity by **equality**, not containment (`is_relative_to`), and fails
**closed** when the call site cannot resolve a git worktree toplevel for the
engine's cwd. The single call site in `main()` resolves `engine_cwd` to its git
worktree toplevel via the existing `_git` helper before calling the predicate.
`tests/test_spine_origin_isolation.py` migrated per the ruling's one authorized
exception: the subdirectory-passes property moved from a synthetic
predicate-level assertion to a real-git-repo assertion through `main()`. Seven
new test methods added (fail-closed at both the predicate and `main()` levels;
the nested-worktree regression with a real `git worktree add` fixture). One
file outside the original Allowed Scope was touched:
`tests/test_explorer_templates.py`, a 1-line fixture repair (`git init` a bare
tempdir that the new fail-closed rule correctly started refusing) — flagged
by the implementer as a judgment call, not silently included.

## How to Inspect the Diff
Working tree in this worktree (not a branch/commit range — the change is
uncommitted). Run `git status --porcelain` then `git diff` from
`/home/tommy/projects/constellation-skills/.worktrees/tc1-worktree-identity`.
Expect exactly 4 files: `map/INDEX.md`, `scripts/checklist_engine.py`,
`tests/test_explorer_templates.py`, `tests/test_spine_origin_isolation.py` —
all modifications, no new/untracked files (the evidence files under
`.agent-work/tc1-worktree-identity/evidence/` are local-only, gitignored,
not part of this diff).

## Task Statement
Implement the ruling's three binding parts exactly:
1. Resolve the cwd to a git worktree toplevel at the single impure call site in `main()`.
2. The predicate (`origin_worktree_refusal`) stays pure and compares by equality, not containment; `test_it_is_pure` must stay green, byte-identical.
3. Fail closed: an origin-carrying spine with no resolvable git toplevel for cwd is refused; origin-less/malformed-origin spines keep the existing fallback and never raise.
Plus the one authorized test migration: the subdirectory-passes property moves from the pure predicate (synthetic paths) to a `main()`-level assertion against a real temporary git repo — moved, not deleted.

## Close Criteria
- `origin_worktree_refusal`'s comparison is `here == root` (not `is_relative_to`), same `os.path.normcase` folding as before.
- `cwd` parameter type is `str | None`; `cwd=None` refuses for an origin-carrying spine, falls back (no refusal) for origin-less/malformed spines, exactly as the pre-change fallback did.
- The call site in `main()` (~L3427-3441) resolves `engine_cwd` via `_git(["rev-parse", "--show-toplevel"], base_dir=Path.cwd())`, passing `None` on any non-zero returncode. No second subprocess-git invocation path was added elsewhere.
- `tests/test_spine_origin_isolation.py::OriginRefusalPredicate::test_it_is_pure` — **byte-identical** to `git show HEAD:tests/test_spine_origin_isolation.py` for that method (verify with `git diff` scoped to the method — zero lines).
- `OriginRefusalFallback` — every malformed/absent origin shape still falls back without raising; intent unchanged from before this diff.
- The synthetic subdirectory case in `OriginRefusalPredicate` now asserts **refusal** (equality semantics) with a docstring pointing to where the real property lives; the real property is asserted through `main()` against a real git repo in `RefusesAGuardedVerbFromAForeignTree::test_the_same_verb_from_a_subdirectory_of_the_worktree_succeeds`.
- `_SpineOnDisk.setUp` git-inits BOTH `self.worktree` and `self.foreign` as two distinct real repos.
- A new permanent regression test (class `NestedWorktreeRegression`) reproduces the ruling's exact scenario: primary real git repo, spine stamped to the primary, driven from inside a real nested worktree created via `git worktree add` under `<primary>/.worktrees/<slug>` — refused.
- Fail-closed tests exist at both the predicate level (`cwd=None` directly) and the `main()` level (a real non-git tempdir cwd).
- Cache-clean full suite (`find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +` then `python -m pytest tests/ -q`, run with `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT` — see Evidence Produced for why) is **>= the measured baseline at `453f8492`**: 3002 passed, 7 skipped, 0 failed, 1130 subtests passed. 0 failures is non-negotiable; a skip-count delta must be explained mechanically, not eyeballed.
- Map regenerated (`python -m scripts.code_map build --root .`); if `map/INDEX.md`/`map/ids.jsonl` moved, they are part of the diff (they are — `map/INDEX.md` moved, `map/ids.jsonl` did not).

## Allowed Scope
- `scripts/checklist_engine.py` — the `origin_worktree_refusal` predicate and its one call site in `main()` only.
- `tests/test_spine_origin_isolation.py` — full file, including new test classes/methods and the one named migration.
- `map/INDEX.md`, `map/ids.jsonl` — regenerated output only.

## Specific Exclusions
- `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py` (esp. `_standing_in_the_bound_spines_worktree`), `.mcp.json`, anything under `.worktrees/epic-568-441/` — must be untouched. Confirm via `git status --porcelain` showing none of these paths.
- `test_it_is_pure` — must not be edited, in any way, for any reason.
- No `origin.worktree` value migration/backfill anywhere.
- `tests/test_explorer_templates.py` was **not** pre-authorized in the original plan. It IS flagged honestly in `IMPLEMENTER_RESULT`'s "Stop conditions hit" section as a judgment call, not silently smuggled in. Judge whether the 1-line fix (`git init` a bare tempdir fixture the new fail-closed rule correctly now refuses) is the right minimal repair, in the same class as the `_SpineOnDisk` git-init this gate's own plan ordered — or whether it should have been a BLOCK-and-rescope instead. This is the one judgment call this review should weigh most carefully.

## Constraints the Implementation Must Respect
- All impurity (the git call) lives at the one call site in `main()`; the predicate itself calls no filesystem/clock/subprocess/ambient-cwd function — verify against `test_it_is_pure`'s own forbidden-name list, which is unmodified.
- The 'no toplevel resolved' signal reaches the predicate as `cwd=None` — confirm `main()` does not re-derive or shortcut the origin-shape interpretation a second time outside the predicate (grep for any new `origin.get` or `.get("worktree")` call outside `origin_worktree_refusal`).

## Map Anchors (inbound)
- **Structural:** `scripts/checklist_engine.py::origin_worktree_refusal` (~L102-180); `scripts/checklist_engine.py::main` call site (~L3427-3441); `scripts/checklist_engine.py::_git` (~L701); `tests/test_spine_origin_isolation.py`.
- **Capability:** engine-native worktree isolation (#315/#568).
- **Constraints/assumptions:** `test_it_is_pure` byte-identical; `OriginRefusalFallback` intent-unchanged; no `origin.worktree` migration.
- **Decision anchors:**
  - decision:git-not-lexical — call site resolves cwd via git worktree toplevel.
    `@grade: settled/human · leans g1-implement`
  - decision:forgery-stays-open — chdir-into-the-stamped-worktree still passes; confirm no door test broke (`test_mcp_door_engine_cwd.py`, `test_mcp_lifecycle.py`, `test_mcp_adoption.py`).
    `@grade: settled/human · leans g1-implement`
  - decision:test-migration-authorized — subdirectory-passes property migration, scoped exactly as described above.
    `@grade: settled/human · leans g1-implement`
- **Evidence expectations:** nested-worktree regression red/green pair (reproduce both, not just read); `test_it_is_pure` unmodified; cache-clean full suite >= baseline (reproduce, don't trust the reported numbers).
- **Map confidence flags:** none — `map/ids.jsonl` is empty repo-wide, not specific to this area.

## Evidence Produced
From `IMPLEMENTER_RESULT` (`.agent-work/tc1-worktree-identity/crew-handoffs/g1-implement-implementer-result.md`), already independently re-verified once by the Commander:
- Red (`.agent-work/tc1-worktree-identity/evidence/g1-red.txt`) / Green (`.agent-work/tc1-worktree-identity/evidence/g1-green.txt`) for the two `NestedWorktreeRegression` tests. **Reproduce both yourself**: `git stash` the diff, run the two tests (expect 2 failed), `git stash pop`, run again (expect 2 passed). This is the single most load-bearing piece of evidence in this gate.
- `python -m pytest tests/test_spine_origin_isolation.py -v` → 37 passed, 1 skipped, 16 subtests passed.
- Cache-clean full suite (`.agent-work/tc1-worktree-identity/evidence/g1-fullsuite.txt`): 3010 passed, 6 skipped, 1135 subtests passed, 0 failed. Baseline: 3002/7/0/1130. The skip-count delta (7→6) is claimed to be workspace-state-dependent, not diff-dependent — the implementer says stashing the diff and re-running every skip-capable file yields the identical 6-skip list. Spot-check this claim if time allows; it is not load-bearing for APPROVE (0 failures is what matters) but a wrong explanation would be worth flagging.
- Run the suite with `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT` — the implementer found `test_mcp_identity.py::DC3InheritanceMechanismTests` fails inside any crew-dispatched process (ambient `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`) with zero relation to this diff; confirm this independently (same test fails with those vars set, passes without, on an UNCHANGED tree too — i.e. not caused by this diff).
- Wiring grep: `grep -n "_git(\[\"rev-parse\", \"--show-toplevel\"\]" scripts/checklist_engine.py` → exactly one match, in `main()`.

## Suggested Model Tier
stronger — the fixture-migration correctness (real git repos, `git worktree add`, fail-closed at two levels) and the out-of-scope `test_explorer_templates.py` judgment call both need careful, skeptical reading, not a fast skim.

## Stop Conditions
Return BLOCK if: the red/green pair does not reproduce; `test_it_is_pure` is not byte-identical; any Specific Exclusion was touched; the cache-clean suite shows any failure; the `test_explorer_templates.py` fix looks like scope creep beyond the minimal repair it claims to be.

## Return Format
Return REVIEW_RESULT (APPROVE or BLOCK) to
`.agent-work/tc1-worktree-identity/crew-handoffs/g1-review-reviewer-result.md`
before ending your turn.
