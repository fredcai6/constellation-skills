# Implementation Result

## Assigned gate
g2 (g2-implement) — installer wiring: install_constellation.py + git hooks-dir resolution

## Completed slice
Wired `scripts/hooks/code_map_precommit.py` (gate 1's fail-open shim) into `scripts/install_constellation.py` so a real self-install writes it to the git-resolved `pre-commit` hook path. Added `resolve_git_hooks_dir(repo_root) -> Path | None` (report-only `git rev-parse --path-format=absolute --git-path hooks`, correct for linked worktrees and `core.hooksPath`) and `install_git_precommit_hook(repo_root, *, dry_run, out) -> None` (writes a marker-stamped, run-time-resolving shell wrapper; refuses to clobber a foreign hook; idempotent; honors `dry_run`). Wired both into `main()` via new keyword-only `install_git_pre_commit_hook: bool = False` / `git_repo_root: Path | None = None` params, mirroring `wire_repo_mcp_config`/`mcp_config_path` exactly, guarded by `install_git_pre_commit_hook and (git_repo_root is not None or is_self_install(args))`. `if __name__ == "__main__":` now also passes `install_git_pre_commit_hook=True`.

## Scope
**Files changed:**
- `scripts/install_constellation.py`
- `tests/test_install_constellation.py`

**Specific exclusions touched:** no — `scripts/code_map/`, `scripts/hooks/code_map_precommit.py`, `tests/test_code_map.py`, `tests/test_code_map_precommit.py` were read-only references, never edited; `wire_hooks`/`HOOK_SETS`/`report_hook_wiring`/Claude Code hook machinery untouched (confirmed by diff — zero lines changed in those functions).

## Behavior changed
Yes. A real self-install (`python scripts/install_constellation.py ...` with no `--dest`/`--project` override, i.e. `is_self_install(args)` true) now also writes/refreshes `<shared-hooks-dir>/pre-commit` as a side effect, in addition to the pre-existing `.mcp.json` wiring. Every direct/library call to `main()` (the ~230 pre-existing tests) is unaffected since both new params default off.

## Map Impact
- **Structural anchors touched:** `scripts/install_constellation.py` — two new functions (`resolve_git_hooks_dir`, `install_git_precommit_hook`), two new `main()` params, one new `SCRIPT_SOURCE_SUBDIRS` entry, one new `__main__` arg.
- **Capabilities added/changed/affected:** the code-map pre-commit hook (gate 1) now has its only real caller wired — installed but not yet proven to fire against a live `git commit` (that is gate 3's job, per the handoff).
- **Constraints/assumptions touched:** self-install-only is enforced exactly the way `.mcp.json` wiring is enforced (decision anchor in the handoff: "self-install-only gating, mirroring the existing `.mcp.json` wiring guard") — settled, tested (`test_self_install_only_never_touches_git_hooks_when_not_self_install`).
- **Decision candidates / resolved decisions:** none forced; wiring shape was already decided (handoff Authority section) and implemented as specified.
- **Claims/evidence produced:** `resolve_git_hooks_dir` verified correct against a real linked-worktree topology, including THIS actual checkout (`/home/tommy/projects/569-w2-reindex`, resolves to the shared `constellation-skills/.git/hooks`), not only a synthetic fixture.
- **Trust limitations / drift found:** `ScriptsPackageBundlingTests.test_every_scripts_subdirectory_is_declared_one_way_or_the_other` was failing against the pre-existing `main()`/test suite (unrelated to this gate's diff) because gate 1's `scripts/hooks/code_map_precommit.py` was never added to `SCRIPT_SOURCE_SUBDIRS`, leaving `scripts/hooks/` only partially declared. Fixed with a one-line, in-scope, inert addition (`"code_map_precommit.py": "hooks"` — no skill bundles it, so this changes no installed output) so "full pre-existing suite green" holds. Flagging here since it originates from gate 1's file, not this gate's new code.

## Test mode
**Required:** test-after
**Satisfied:** yes — every new function has a real test against a disposable scratch git repo (`tempfile.TemporaryDirectory()` + `git init`), never this repo's own git state for anything that writes; the one test that touches this repo's own checkout (`test_resolve_git_hooks_dir_against_this_actual_checkout`) calls only the read-only `resolve_git_hooks_dir`.

## Evidence

```bash
python -m pytest tests/test_install_constellation.py -k GitPreCommitHookWiringTests -q
```
**Result:** pass — `14 passed, 216 deselected`

```bash
python -m pytest tests/test_install_constellation.py -q
```
**Result:** pass — `230 passed, 519 subtests passed` (full pre-existing suite green, zero changes to existing test bodies — only new tests and the one `SCRIPT_SOURCE_SUBDIRS` entry added).

```bash
grep -rn "install_git_pre_commit_hook\|install_git_precommit_hook\|resolve_git_hooks_dir" --include=*.py . | grep -v "def "
```
**Result:** 3 call sites outside their own definitions in `install_constellation.py` — the `main()` call-site guard (`if install_git_pre_commit_hook and (...)`), the call itself, and the `if __name__ == "__main__":` block — plus the new test file. Zero real-`git commit` callers, as expected (gate 3's job).

## TDD evidence, if required
Not applicable — test-after mode. Function then tests, in that order, for each of `resolve_git_hooks_dir`, `install_git_precommit_hook`, and the `main()` wiring; each was run green immediately after being written (see plan gates m1–m3).

## Docs/contracts touched
- none

## Assumptions
- `code_map_precommit.py` is deliberately never bundled by any skill (its own docstring: dynamically resolved at hook run time, not installer-copied) — so declaring it in `SCRIPT_SOURCE_SUBDIRS` is inert bookkeeping to satisfy `ScriptsPackageBundlingTests`, not a change to what gets installed. Confirmed by grepping `skills/**/SKILL.md` and `required_scripts` for any reference to it (none).

## Stop conditions hit
- none

## Out-of-scope observations
- The `ScriptsPackageBundlingTests` gap above (gate 1's file left `scripts/hooks/` incompletely declared) is worth a note back to whoever tracks gate 1's own closeout evidence: their own required evidence only ran `test_code_map_precommit.py`/`test_code_map.py`, never the full `test_install_constellation.py`, so this gap was invisible to that gate's own verification.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's Close Criteria, Required Evidence, and Authority sections were sufficient to implement without needing a design decision.
- **Context rediscovered:** the exact self-install-only guard semantics took a moment to pin down: `install_git_pre_commit_hook and (git_repo_root is not None or is_self_install(args))` reads as if an explicit `git_repo_root` override could point "elsewhere" and still fire — but the intent (confirmed by studying the `.mcp.json` precedent's own `RepoMcpConfigWiringTests`) is that an explicit override is a *test-only* decoupling knob for exercising the write mechanics directly, while the real self-install-only guarantee holds only for the true CLI entry point, which never passes `git_repo_root`. Spelling this out explicitly in the handoff (as this note now does) would save the next implementer of a sibling `wire_X`/`X_path` pair the same re-derivation.
- **Instructions improvised around:** none.
- **What would have made this easier:** noting in the handoff that gate 1's shipped file might not yet be accounted for in `ScriptsPackageBundlingTests` (a full-suite run was never part of gate 1's own evidence) would have let this gate anticipate the pre-existing-suite failure instead of discovering it fresh.

## Note on engine drive
This crew's `crew-runs.json` entry carries `"spine": null` — the `SPINE_FILE`/`SPINE_SESSION` env inherited from the process environment point at the Commander's own bound `execute` spine (lease held by `commander`), not at a spine bound for this crew. Per prior confirmed instances of this exact shape on this same work-id (`w2-reindex` g1-implement, memory `crew-dispatch-spine-null`), that spine is the parent's and must never be advanced or waived by a dispatched crew. Instead, authored an own `IMPLEMENTER_PLAN.json` under this crew's `scratch_dir` (`.agent-work/w2-reindex/crew-scratch/g2-implement-implementer-attempt-1-cdb4ee2aea69/IMPLEMENTER_PLAN.json`), claimed its lease, and drove it gate-by-gate through `scripts/checklist_engine.py`'s CLI (`claim` → `start`/`attest`/`advance` per item, two `retext-check` amendments to narrow over-broad postcondition checks, `m0-context` through `m4-green-and-report`) to a clean, fully-advanced finish. The parent's `execute` spine was never touched.

## Return status
`complete`
