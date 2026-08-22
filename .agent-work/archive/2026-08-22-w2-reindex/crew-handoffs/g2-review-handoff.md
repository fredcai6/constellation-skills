# Reviewer Handoff

## Gate
g2 (g2-review)

## Survey State Location
`.agent-work/w2-reindex/g2-review/review.json`

## What Was Implemented
`scripts/install_constellation.py` gets `resolve_git_hooks_dir(repo_root) -> Path | None`
(report-only `git rev-parse --path-format=absolute --git-path hooks`) and
`install_git_precommit_hook(repo_root, *, dry_run, out) -> None` (writes a marker-stamped,
run-time-resolving shell wrapper at the resolved hooks path; refuses to clobber a foreign hook;
idempotent; honors `dry_run`), wired into `main()` via new keyword-only
`install_git_pre_commit_hook: bool = False` / `git_repo_root: Path | None = None` params mirroring
the existing `wire_repo_mcp_config`/`mcp_config_path` pair, guarded self-install-only. Also: a
one-line `SCRIPT_SOURCE_SUBDIRS` fix (`"code_map_precommit.py": "hooks"`) for a pre-existing gap
`ScriptsPackageBundlingTests` caught, left behind by gate 1's file.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-reindex` — `git status --porcelain` then
`git diff` (not `--name-only`). Expected changed files this gate: `scripts/install_constellation.py`,
`tests/test_install_constellation.py`. `scripts/code_map/cli.py`,
`scripts/code_map/{build,precommit}.py`, `scripts/hooks/code_map_precommit.py`,
`tests/test_code_map_precommit.py` are gate 1's already-approved diff — present in the working tree
but not this gate's to re-review; confirm they are unchanged since gate 1 (`git log`/timestamps
won't help on an uncommitted tree — diff their content against
`.agent-work/w2-reindex/crew-handoffs/g1-implement-implementer-result.md`'s description if in doubt).

## Task Statement
Wire gate 1's fail-open shim into `install_constellation.py` so a real self-install writes it to
the git-resolved `pre-commit` hook path, self-install-only, never clobbering a foreign hook. Full
original task in `.agent-work/w2-reindex/crew-handoffs/g2-implement-handoff.md`.

## Close Criteria
- `resolve_git_hooks_dir` correct for a linked worktree and `core.hooksPath`; verify it directly
  against **this actual checkout** (a real linked worktree of `constellation-skills`), not only a
  synthetic fixture.
- `install_git_precommit_hook`'s wrapper resolves `scripts/hooks/code_map_precommit.py` **at run
  time** from the invoking worktree's own top level — read the exact wrapper content it writes and
  confirm it does not embed this install's own absolute path.
- Marker-stamped, idempotent, refuses to clobber a foreign (unmarked) `pre-commit`, honors
  `--dry-run`.
- Self-install-only: a target that is not this checkout never touches `.git/hooks` at all.
- Zero changes to `wire_hooks`/`HOOK_SETS`/`report_hook_wiring`/Claude Code hook machinery.
- Full pre-existing `tests/test_install_constellation.py` green, zero changes to existing test
  bodies (only new tests + the one `SCRIPT_SOURCE_SUBDIRS` line added).
- The `SCRIPT_SOURCE_SUBDIRS` fix is genuinely inert (changes no installed output) — verify the
  implementer's claim (no `skills/**/SKILL.md` or `required_scripts` references
  `code_map_precommit.py`) yourself.

## Allowed Scope
`scripts/install_constellation.py`, `tests/test_install_constellation.py` only.

## Specific Exclusions
`scripts/code_map/`, `scripts/hooks/code_map_precommit.py`, `tests/test_code_map.py`,
`tests/test_code_map_precommit.py` (gate 1, already approved — flag as a BLOCK only if this gate's
diff modifies them, not for their mere presence in the working tree). `wire_hooks`/`HOOK_SETS`. No
real `git commit`/hook install against this repo's own `.git/hooks/` (gate 3's job).
`generate_spine.py`, `specs/`, `scripts/checklist_engine.py`, any shipped spine template.

## Constraints the Implementation Must Respect
- `resolve_git_hooks_dir`/`install_git_precommit_hook` never raise on a git failure — report-only.
- Stdlib only.
- **Independently re-verify**: run the full pre-existing `tests/test_install_constellation.py` file
  yourself and confirm the pass count/behavior of every pre-existing test is unchanged (not just
  that the new class passes). Independently reproduce the worktree case against this actual repo's
  own layout — don't trust the implementer's report that it resolves correctly; run
  `resolve_git_hooks_dir` (or the equivalent `git rev-parse` command) yourself against
  `/home/tommy/projects/569-w2-reindex` and confirm it names the real shared
  `constellation-skills/.git/hooks`.

## Map Anchors (inbound)
- **Structural:** `scripts/install_constellation.py` (`wire_repo_mcp_config`, `mcp_config_path`,
  `is_self_install`, `write_template_working_copies` — the precedents this gate mirrors).
- **Constraints/assumptions:** self-install-only (hard — the code_map package cannot be bundled
  into an installed skill); must be installed and proven to fire (hard, gate 3's job next).
- **Decision anchors:** self-install-only gating, mirroring `.mcp.json` wiring.
  `@grade: settled/measured · leans g2-implement,g2-review · settle: this gate's independent
  worktree/self-install-only re-verification is the settlement evidence`

## Evidence Produced
`python -m pytest tests/test_install_constellation.py -k GitPreCommitHookWiringTests -q` → 14
passed. `python -m pytest tests/test_install_constellation.py -q` → 230 passed, 519 subtests
passed (full pre-existing suite, zero changes to existing bodies). Wiring grep: 3 real call sites
in `install_constellation.py` (guard, call, `__main__` block) — zero real-`git commit` callers,
expected at this gate. This evidence targets `g2-integrate.c1`.

## Suggested Model Tier
simple bounded — mirrors an established pattern closely; main risk is worktree-resolution
correctness, directly checkable against this repo's real layout.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, the
self-install-only guard can be shown to fire for a non-self-install target, or a policy decision is
required before a verdict is possible.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK) to
`.agent-work/w2-reindex/crew-handoffs/g2-review-reviewer-result.md` before ending your turn.
