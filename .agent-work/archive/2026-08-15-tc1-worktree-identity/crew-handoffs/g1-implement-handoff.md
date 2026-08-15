# Implementer Handoff

## Gate
g1

## Task
Implement the Admiral ruling at
`/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`
(read it in full first — it is the authority for this task) in
`scripts/checklist_engine.py`: replace containment (`here.is_relative_to(root)`)
with git-worktree-identity equality in `origin_worktree_refusal`, resolving the
call site's cwd to its git worktree toplevel before the predicate ever sees it.
Migrate `tests/test_spine_origin_isolation.py` per the ruling's one authorized
test-intent exception (subdirectory-passes moves from the pure predicate to a
`main()`-level real-git-repo assertion), and add the new tests this gate's
Required Evidence section names.

## Protected Intent
A primary-stamped spine must not be drivable from inside a nested worktree
(the regression `<root>/.worktrees/<slug>` nesting introduced). A spine
correctly stamped to its own worktree — including from a subdirectory of that
worktree — must stay drivable. No shape of malformed/absent `origin` may ever
raise.

## Test Mode
TDD required for the nested-worktree regression specifically: capture red
(current code, real git repos, primary + nested worktree, ALLOWED) before
implementing the fix, then green (same scenario, REFUSED) after. Test-after is
fine for the remaining changes — they are a direct transcription of the ruling.

## Close Criteria
- `origin_worktree_refusal` (scripts/checklist_engine.py:~102-161) compares equality, not containment; stays pure (no filesystem/clock/subprocess/ambient-cwd read); keeps the existing `os.path.normcase` folding.
- The predicate's `cwd` parameter accepts `None` (type `str | None`); when `None`, an origin-carrying spine is refused (fail closed), origin-less/malformed spines still fall back to `None` (no refusal) exactly as today.
- The single call site in `main()` (~L3393-3416) resolves `engine_cwd` to its git worktree toplevel using the existing `scripts/checklist_engine.py::_git` helper (do not add a second subprocess-git invocation path) before calling the predicate; on git-toplevel-resolution failure, passes `None`.
- `tests/test_spine_origin_isolation.py::OriginRefusalPredicate.test_it_is_pure` is **unmodified** (byte-identical) and green.
- `tests/test_spine_origin_isolation.py::OriginRefusalFallback` is green, unmodified in intent (every malformed/absent origin shape still falls back without raising).
- The one authorized test migration lands: the synthetic subdirectory-passes case in `OriginRefusalPredicate` is corrected to assert refusal (equality semantics), with its docstring naming where the real property now lives; the property itself is re-proven through `main()` against a real temporary git repo.
- `_SpineOnDisk.setUp` (and its subclasses `RefusesAGuardedVerbFromAForeignTree`, `TheInProcessMcpDoorShape`) git-init BOTH `self.worktree` and `self.foreign` as two distinct real repos (siblings) — required so the existing pass-path assertions (same-worktree, same-subdirectory) and foreign-tree-refused assertions keep exercising real git-toplevel resolution rather than silently falling into the fail-closed path.
- A new permanent regression test: a spine stamped to a PRIMARY real git repo, driven (through `main()`) from a cwd inside a NESTED real git worktree created via `git worktree add` under `<primary>/.worktrees/<slug>` — refused after the fix.
- A new fail-closed test at the predicate level: `origin_worktree_refusal(spine, cwd=None, verb=...)` against an origin-carrying spine refuses.
- A new fail-closed test at the `main()` level: an origin-carrying spine driven from a cwd with no resolvable git toplevel at all (plain non-git tempdir) — refused, no raise.
- Map regenerated (`python -m scripts.code_map build --root .`); `map/INDEX.md`/`map/ids.jsonl` re-committed only if they moved.
- Cache-clean full suite (clear `__pycache__` first) passes at or above the measured baseline at `453f8492`: 3002 passed, 7 skipped, 0 failed, 1130 subtests passed.

## Allowed Scope
- `scripts/checklist_engine.py` — the `origin_worktree_refusal` predicate and its one call site in `main()` only. Do not touch unrelated code in this large file.
- `tests/test_spine_origin_isolation.py` — full file; pre-authorized to add new test classes/methods and to correct the one named synthetic subdirectory case per the authorized migration.
- New test file, if you find one genuinely cleaner than extending the existing file (not required).
- `map/INDEX.md`, `map/ids.jsonl` — regenerated output only, via the `code_map` tool, never hand-edited.

## Specific Exclusions
- `scripts/hooks/spine_rail.py` — NOT yours. Two reasons: it is the live target of in-flight sibling work on #441, and the ruling deliberately keeps its lexical derivation (see the ruling's "other half of tc3" section). If the lexical/git split needs writing down, that goes in your `IMPLEMENTER_RESULT`'s workflow feedback / findings, never in code here.
- `scripts/mcp_spine_server.py`, specifically `_standing_in_the_bound_spines_worktree` — NOT yours (pre-ruling 2, `decision:forgery-stays-open`). Do not "close" the forgery hole.
- `.mcp.json`, anything under `.worktrees/epic-568-441/` — NOT yours.
- `test_it_is_pure` — do not edit this test method under any circumstance, including to "fix" its docstring.
- No `origin.worktree` value migration/backfill/rewrite anywhere (`decision:no-migration`).

## Constraints
- The predicate's comparison is `here == root`, both sides `Path(os.path.normcase(...))` — same folding as today, just equality instead of `is_relative_to`.
- `cwd` type changes from `str` to `str | None`; when `None` and the spine carries a valid `origin.worktree`, return a refusal message (do not raise, do not return `None`).
- The git-toplevel resolution at the call site must use `_git(["rev-parse", "--show-toplevel"], base_dir=...)` (the existing helper at ~L701), checking `returncode` and stripping `stdout`; on any non-zero returncode, resolve to `None`.
- Do not re-derive or shortcut the origin-shape interpretation a second time in `main()` — the predicate remains the single place that interprets `origin` shape. `main()` only resolves the git toplevel and passes it through.

## Map Anchors (inbound)
- **Map entry point:** none — `map/ids.jsonl` is empty repo-wide (no decision anchors exist yet in this repo); the ruling document is this gate's map.
- **Structural:** `scripts/checklist_engine.py::origin_worktree_refusal` (~L102-161); `scripts/checklist_engine.py::main` call site (~L3393-3416); `scripts/checklist_engine.py::_git` (~L701); `tests/test_spine_origin_isolation.py` (three sections).
- **Capability:** engine-native worktree isolation (#315/#568) — a spine's `origin.worktree` stamp gates every `ORIGIN_GUARDED_VERBS` call at the engine's one call site.
- **Constraints/assumptions:** `test_it_is_pure` stays green unmodified; `OriginRefusalFallback` stays green; no `origin.worktree` migration.
- **Decision anchors:**
  - decision:git-not-lexical — call site resolves cwd via git worktree toplevel, not lexical containment or an exported `--from`.
    `@grade: settled/human · leans g1-implement`
  - decision:forgery-stays-open — chdir-into-the-stamped-worktree still passes; not closed here.
    `@grade: settled/human · leans g1-implement`
  - decision:test-migration-authorized — subdirectory-passes property moves from the pure predicate to a `main()`-level real-git-repo assertion; the one authorized exception to test-intent-never-changes.
    `@grade: settled/human · leans g1-implement`
- **Evidence expectations:** claim: nested-worktree regression refused after, allowed before (red/green pair, both outputs reported verbatim); claim: `test_it_is_pure` unmodified and green; claim: cache-clean full suite >= baseline.
- **Map confidence flags:** none — repo-wide map gap already discharged at Commander's `context` step, not specific to this area.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; verified via `git check-ignore scripts/checklist_engine.py` exiting 1 (not ignored).
- **Committed** — `tests/test_spine_origin_isolation.py`; verified via `git check-ignore tests/test_spine_origin_isolation.py` exiting 1 (not ignored).
- **Committed (conditional)** — `map/INDEX.md`, `map/ids.jsonl`; regenerate via `python -m scripts.code_map build --root .` and `git status` them — commit only if `git diff --stat` shows they moved.

## Required Evidence
Load-bearing (prove rigorously):
- The red/green pair for the nested-worktree regression test: full pytest output (or a standalone repro script's output) run against the UNMODIFIED engine showing the scenario currently ALLOWED (exit 0 / no refusal), then the SAME scenario after your fix showing REFUSED (exit 1, "REFUSED:" on stderr).
- `python -m pytest tests/test_spine_origin_isolation.py -v` full output, all green.
- `git diff -- tests/test_spine_origin_isolation.py | grep -A3 -B3 "def test_it_is_pure"` (or equivalent) showing ZERO lines changed in that method.
- Cache-clean full suite: `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} + && python -m pytest tests/ -q` — paste the final summary line and confirm it is >= the baseline (3002 passed, 7 skipped, 0 failed, 1130 subtests passed at `453f8492`). If any count differs, derive the failure distribution mechanically (`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never eyeballed.

Confirmatory (spot-check suffices):
- `python -m scripts.code_map build --root .` output plus `git status map/` / `git diff --stat map/` showing whether it moved.

## Wiring Grep
This gate changes an existing predicate's internal comparison and adds a private git-resolution helper at the call site; it adds no new public symbol other than that one small call-site helper. Show its one call site:
```bash
grep -n "_git(\[\"rev-parse\", \"--show-toplevel\"\]" scripts/checklist_engine.py
```
Expect exactly one match, inside `main()`, not inside `origin_worktree_refusal` itself (the predicate must stay pure).

## Verification Commands
```bash
python -m pytest tests/test_spine_origin_isolation.py -v
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
python -m pytest tests/ -q
python -m scripts.code_map build --root .
```

## Suggested Model Tier
stronger — the equality/fail-closed change is small, but the test-fixture migration (git-init two real repos, a real `git worktree add` regression fixture) requires careful reasoning about what actually reproduces the ruling's measured scenario, and getting it subtly wrong (e.g. not making `self.foreign` its own repo) silently narrows coverage without failing any check.

## Authority
The ruling document is the frozen design; do not relitigate `decision:git-not-lexical`, `decision:forgery-stays-open`, or `decision:no-migration`. The one test-intent exception (`decision:test-migration-authorized`) is pre-authorized exactly as scoped above — do not extend it to any other test.

## Stop Conditions
Stop and return if: the git-toplevel measurement (`git rev-parse --show-toplevel` from a nested worktree resolving to the nested worktree, not the primary) does not reproduce; green would require editing anything in Specific Exclusions or weakening `test_it_is_pure`; a test case would need to be deleted rather than relocated; a decision outside this handoff's Authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (including the red/green pair verbatim), assumptions used, stop conditions hit, out-of-scope observations (e.g. anything about `spine_rail.py`'s lexical/git split worth writing down, per the ruling), workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/tc1-worktree-identity/crew-handoffs/g1-implement-implementer-result.md`
before ending your turn.
