# Implementer Handoff

## Gate
g2 (g2-implement) — installer wiring: install_constellation.py + git hooks-dir resolution

## Task
Wire `scripts/hooks/code_map_precommit.py` (gate 1's fail-open shim, already shipped and merged)
into `scripts/install_constellation.py` so a real self-install writes it to the git-resolved
`pre-commit` hook path. Gate 1 built the mechanism; this gate gives it its only real caller
(`git commit`). Gate 3 (after this one) proves it fires end to end — you do not run a real
`git commit` against this repo's own state in this gate; every test operates on disposable scratch
git repos.

## Protected Intent
This mechanism is inherently self-host-only: `scripts/code_map/__init__.py` documents that the
package cannot be bundled into an installed skill (flat-copy breaks intra-package imports). This
wiring must **never** fire for any target other than this checkout installing into itself — a
target that installs a skill bundle elsewhere must never touch `.git/hooks`.

## Test Mode
Test-after allowed. Every new function needs a real test against a disposable scratch git repo
(`tempfile.TemporaryDirectory()`) before this gate closes — never this repo's own git state.

## Close Criteria
- `resolve_git_hooks_dir(repo_root) -> Path | None` added to `scripts/install_constellation.py`:
  runs `git rev-parse --path-format=absolute --git-path hooks` with `cwd=repo_root`; returns `None`
  on any git failure (report-only, never raises). Must correctly resolve the **shared** hooks
  directory when `repo_root` is a linked worktree — verify against **this actual checkout**
  directly (it is one; see Map Anchors), not only a synthetic single-worktree fixture — and must
  honor `core.hooksPath` when set.
- `install_git_precommit_hook(repo_root, dry_run, out) -> None` added: resolves the hooks dir; if
  `None`, reports and no-ops. Writes a small executable shell wrapper at `<hooks-dir>/pre-commit`
  that `exec`s the interpreter against `scripts/hooks/code_map_precommit.py` **resolved at run time
  inside the wrapper** via the invoking worktree's own top level (never an absolute path baked in
  at install time — the shim itself already resolves `repo_root` dynamically via
  `git rev-parse --show-toplevel`, so the wrapper's own job is just to invoke `python3
  <toplevel>/scripts/hooks/code_map_precommit.py`, computing `<toplevel>` at run time in the shell
  wrapper too, not embedding this install's own path). Writes an idempotency marker comment inside
  the file; re-running with identical intended content is a byte-identical no-op. If a `pre-commit`
  file already exists and lacks the marker, **refuse and report** — never clobber a foreign hook
  (mirrors this file's own existing `write_template_working_copies` precedent: "never clobber a
  project edit"). `chmod +x` on write. Honors `dry_run` (prints the plan, writes nothing).
- New keyword-only `main()` params: `install_git_pre_commit_hook: bool = False`,
  `git_repo_root: Path | None = None` — same default-off, test-safe shape as the existing
  `wire_repo_mcp_config`/`mcp_config_path` pair (read that pair first; mirror its exact shape).
  Wired at the same call site, guarded by `install_git_pre_commit_hook and (git_repo_root is not
  None or is_self_install(args))`.
- `if __name__ == "__main__":` block gets `install_git_pre_commit_hook=True` alongside the existing
  `wire_repo_mcp_config=True`.
- Zero changes to `wire_hooks`, `HOOK_SETS`, `report_hook_wiring`, or any Claude Code
  `PostToolUse`/`settings.json` code path — this is a separate mechanism sharing no machinery with
  it beyond living in the same file.
- Every existing call to `main()` throughout `tests/test_install_constellation.py` (the pre-existing
  suite) remains unaffected — new params default off; verify by running the full existing file
  green with zero changes to those existing tests.

## Allowed Scope
`scripts/install_constellation.py`, `tests/test_install_constellation.py` only.

## Specific Exclusions
Do not touch `scripts/code_map/`, `scripts/hooks/code_map_precommit.py` (gate 1, already shipped —
read-only reference), `tests/test_code_map.py`, `tests/test_code_map_precommit.py`. Do not run a
real `git commit` or install into this repo's own `.git/hooks/` (gate 3's job). Do not touch
`wire_hooks`/`HOOK_SETS`/Claude Code hook machinery. `generate_spine.py`, `specs/`,
`scripts/checklist_engine.py`, any shipped spine template are out of this mission's scope entirely.

## Constraints
- `resolve_git_hooks_dir` and `install_git_precommit_hook` never raise on a git failure — report
  and no-op, matching the existing style of this file's other report-only detection functions.
- Stdlib only.

## Map Anchors (inbound)
This repo's map is DEGRADED-UNPARSEABLE — path anchors:
- **Map entry point:** `scripts/install_constellation.py` — read `wire_repo_mcp_config`,
  `mcp_config_path`, `is_self_install`, and `write_template_working_copies` first (the four existing
  precedents this gate mirrors), then `wire_hooks`/`HOOK_SETS` only enough to confirm you are NOT
  touching them.
- **Structural:** `scripts/hooks/code_map_precommit.py` (gate 1, shipped — the thing being wired,
  read-only here).
- **Constraints/assumptions:** self-install-only (hard — this feature is inherently repo-source-only
  per `scripts/code_map/__init__.py`'s own docstring); must be installed and proven to fire, not
  merely built (hard, echoes wave 1's `RegistrationLint`/#345).
- **Decision anchors:** self-install-only gating, mirroring the existing `.mcp.json` wiring guard.
  `@grade: settled/measured · leans g2-implement,g2-review · settle: this gate's own
  self-install-only test is the settlement evidence`
- **Evidence expectations:** this repo's own checkout is a linked worktree sharing `.git/hooks` with
  8+ sibling worktrees (confirmed via `git worktree list` during planning) — `resolve_git_hooks_dir`
  must be proven against this exact layout, not only a synthetic single-worktree fixture.
- **Map confidence flags:** none beyond the DEGRADED-UNPARSEABLE state already noted.

## Deliverable Path Check
- **Committed** — `scripts/install_constellation.py` (already tracked; you are editing it, not
  creating it).
- **Committed** — `tests/test_install_constellation.py` (already tracked; you are editing it).

## Required Evidence
New test class `GitPreCommitHookWiringTests` in `tests/test_install_constellation.py`, same fixture
idiom as the existing `RepoMcpConfigWiringTests` (`tempfile.TemporaryDirectory()`, explicit
`git_repo_root=`, never the real repo). Load-bearing (prove rigorously): the worktree case, the
self-install-only case, the refuse-to-clobber case. Confirmatory: default-is-noop, idempotent,
dry-run.

- **Default no-op**: `install_git_pre_commit_hook=False` is a true no-op even with a scratch git
  repo present.
- **Explicit wiring**: writes an executable `pre-commit` referencing
  `scripts/hooks/code_map_precommit.py`.
- **Idempotent**: re-running produces byte-identical output, no error, not appended-to.
- **Refuse-to-clobber**: a pre-existing foreign `pre-commit` (no marker) is left untouched; the run
  reports the refusal rather than raising or silently overwriting.
- **`--dry-run`**: writes nothing.
- **Worktree case**: `git worktree add` a second worktree off the scratch repo, wire from inside it,
  assert the wrapper lands in the **shared** main-checkout hooks dir (matching
  `resolve_git_hooks_dir` computed independently in the test). ALSO run
  `resolve_git_hooks_dir` directly against **this actual repo's own checkout**
  (`/home/tommy/projects/569-w2-reindex`, a real linked worktree) and assert it resolves to the real
  shared `constellation-skills/.git/hooks` — this is the one fact a synthetic fixture alone cannot
  fully stand in for.
- **Self-install-only case**: a target that is not this checkout (`git_repo_root` pointing elsewhere,
  `is_self_install` False) never touches `.git/hooks` at all.
- Full pre-existing `tests/test_install_constellation.py` file green, zero changes to its existing
  test bodies.

## Wiring Grep
```bash
grep -rn "install_git_pre_commit_hook\|install_git_precommit_hook\|resolve_git_hooks_dir" --include=*.py . | grep -v "def "
```
State the count of call sites found outside their own definitions. Expected: `main()`'s own
call-site guard, the `if __name__ == "__main__":` block, and the new test file. Real end-to-end
proof that `git commit` actually reaches this code is gate 3's job — zero real-commit callers at
this gate is expected, not a defect.

## Verification Commands
```bash
python -m pytest tests/test_install_constellation.py -q
```

## Suggested Model Tier
simple bounded — this gate mirrors an existing, well-established pattern in the same file
(`wire_repo_mcp_config`/`mcp_config_path`) closely; the main risk is the worktree-resolution
correctness, which is directly testable against this repo's own real layout.

## Authority
The wiring shape (mirror `wire_repo_mcp_config`, self-install-only guard, refuse-to-clobber,
run-time path resolution in the wrapper) is already decided — see
`.agent-work/w2-reindex/PLAN_ALTERNATIVES.md` and `.agent-work/w2-reindex/PLAN_CRITIC.md`. Do not
re-litigate; implement it. Exact function/helper naming beyond what's specified is yours to decide.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (`Return status` lowercase: complete | partial | blocked | out-of-scope |
failed) to `.agent-work/w2-reindex/crew-handoffs/g2-implement-implementer-result.md` before ending
your turn.
