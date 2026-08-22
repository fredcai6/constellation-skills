# Review Result

## Assigned Gate
g2 (g2-review)

## Result
`APPROVE`

## Handoff compliance
Full: `resolve_git_hooks_dir(repo_root) -> Path | None` and `install_git_precommit_hook(repo_root, *,
dry_run, out) -> None` are implemented and wired into `main()` via keyword-only
`install_git_pre_commit_hook: bool = False` / `git_repo_root: Path | None = None`, gated
`install_git_pre_commit_hook and (git_repo_root is not None or is_self_install(args))` — the identical
shape to the pre-existing `wire_repo_mcp_config and (mcp_config_path is not None or
is_self_install(args))` guard it was asked to mirror. The `__main__` block passes
`install_git_pre_commit_hook=True` alongside `wire_repo_mcp_config=True`. All Close Criteria and Stop
Conditions satisfied; no policy decision was required.

## Scope drift
None. `git diff --name-only` lists exactly three tracked files: `scripts/code_map/cli.py` (gate 1's
already-approved `_build` delegation — content diffed and confirmed to match
`g1-implement-implementer-result.md`'s own description, unchanged since gate 1),
`scripts/install_constellation.py`, `tests/test_install_constellation.py` — both in Allowed Scope. No
Specific Exclusion touched (`generate_spine.py`, `specs/`, `scripts/checklist_engine.py`, any shipped
spine template — zero matches). No real `git commit`/`.git/hooks` install against this repo's own
state: confirmed the shared hooks dir (`/home/tommy/projects/constellation-skills/.git/hooks`) still
has no `pre-commit` file. `wire_hooks`/`HOOK_SETS`/`report_hook_wiring` — zero lines touched (grepped
the diff directly).

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:
- `python -m pytest tests/test_install_constellation.py -k GitPreCommitHookWiringTests -q` → **14
  passed** (matches claim).
- `python -m pytest tests/test_install_constellation.py -q` → **230 passed, 519 subtests passed**
  (matches claim exactly; full pre-existing suite green).
- Diffed `tests/test_install_constellation.py`: the entire change is a pure insertion (one new class +
  one helper function) after `RepoMcpConfigWiringTests`'s close — zero changes to any existing test
  body.
- `resolve_git_hooks_dir(REPO_ROOT)` run live against **this actual checkout**: resolves to
  `/home/tommy/projects/constellation-skills/.git/hooks`, matching a direct `git rev-parse
  --path-format=absolute --git-path hooks` call and consistent with `git worktree list` showing 8+
  sibling worktrees sharing that same `.git`.
- Read `_git_precommit_hook_wrapper_text()`'s actual return value directly: resolves `toplevel` at run
  time via `git rev-parse --show-toplevel` inside the wrapper and execs
  `"$toplevel/scripts/hooks/code_map_precommit.py"` — no absolute path from this install baked in.
- `SCRIPT_SOURCE_SUBDIRS` fix confirmed genuinely load-bearing, not incidental: removed the added line,
  reran `ScriptsPackageBundlingTests`, got the exact predicted failure (`AssertionError: ... scripts/hooks/
  is neither in NON_INSTALLABLE_PACKAGES nor fully declared`), restored, reran green, and diffed the
  restored file byte-identical to the original — a check that can fail, shown failing.
- Grepped `skills/**/SKILL.md` and every `required_scripts` reference for `code_map_precommit.py`: zero
  matches, confirming the fix changes no installed output (implementer's inertness claim verified, not
  assumed).

## Code/doc quality
Minimal, maintainable, matches surrounding style. Constraints independently checked, not just read:
`resolve_git_hooks_dir` never raises on a git failure (catches `OSError`/`TimeoutExpired`, returns
`None` on nonzero exit — test-covered); `install_git_precommit_hook` reports and returns before
touching the filesystem when the hooks dir can't be resolved; the diff adds **zero new imports**
(`subprocess`/`Path`/`Callable` already present) — stdlib-only holds. Docstrings are dense and
WHY-focused (non-obvious invariants: worktree/`core.hooksPath` resolution, run-time vs install-time
path resolution), consistent with this project's documented "agent-facing, dense by design" doctrine
(`docs/agents/CREW_CONTEXT.md`).

**Fowler refactoring pass** (full record: `.agent-work/w2-reindex/FOWLER_PASS.json`, verified by
`verify_fowler_pass.py` exit 0): 10 of 12 baseline smells absent. **Flagged** (non-blocking):
`long-parameter-list` — `main()` grows from 7 to 9 params; all keyword-only (no positional-confusion
risk), matches the established one-pair-per-wiring-target pattern; worth a config-object refactor only
if a third pair arrives. **Overridden**: `duplicated-code` — the new git-hook wiring block in `main()`
structurally mirrors the pre-existing `.mcp.json` wiring block immediately above it. Override reason:
the handoff's own Map Anchors section names that block as "the precedents this gate mirrors," and
`global-everyone.md`'s "no speculative abstraction" posture argues against extracting a helper for only
two instances (rule of three not crossed) — extracting now would also obscure the deliberate
line-by-line mirroring the handoff asked for as its own verification path.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim in
  `g2-implement-implementer-result.md` was independently checked against the diff and re-run, not taken
  on the report's word.
- **Constraints not violated:** yes — self-install-only verified to hold for the real CLI entry point
  (`git_repo_root` defaults `None` there, so the guard reduces to `is_self_install(args)` alone); the
  `git_repo_root` override is a test-only decoupling knob, exercised only by
  `GitPreCommitHookWiringTests`, never by the real entry point.
- **Notes match the diff:** yes — structural anchors, capability claim, and constraint claim all match
  what the diff actually touches; no missing or overstated impact.
- **Decision candidates surfaced:** none were needed — the wiring shape was already decided in the
  handoff's Authority section and followed as specified.
- **Durable context routed:** yes — the `ScriptsPackageBundlingTests` gap left by gate 1 (fixed here,
  in-scope) was correctly routed as an out-of-scope observation rather than silently absorbed into this
  gate's own claimed work.

## Reconciliation check
No divergence from recorded architecture. The capability is additive only (two new opt-in `main()`
params, both default off); every one of the ~230 pre-existing tests is unaffected. Nothing here requires
Commander adjudication.

## Blockers
- none

## Out-of-scope observations
- (Restated from the implementer, independently confirmed worth passing on): gate 1's
  `scripts/hooks/code_map_precommit.py` left `scripts/hooks/` incompletely declared in
  `SCRIPT_SOURCE_SUBDIRS`, invisible to gate 1's own evidence because that gate's required evidence only
  ran `test_code_map_precommit.py`/`test_code_map.py`, never the full `tests/test_install_constellation.py`.
  Fixed here (one line, verified inert). Worth noting for whoever tracks gate 1's closeout record, and as
  a general note that a gate whose diff touches `scripts/<subdir>/` should include
  `ScriptsPackageBundlingTests` in its own required evidence going forward.
- Fowler pass's `long-parameter-list` finding on `main()` (see Code/doc quality above) — non-blocking,
  worth a config-object refactor if a third `wire_X`/`X_path`-shaped pair is ever added.

## Workflow Feedback
- **Handoff gaps:** none — Close Criteria, Allowed Scope, Specific Exclusions, and Constraints were all
  concrete and directly checkable; no ambiguity encountered.
- **Context rediscovered:** none beyond what the handoff already pointed at — the g1/g2-implement result
  files and the actual checkout's own worktree topology (`git worktree list`) were exactly where the
  handoff said to look.
- **Instructions improvised around:** confirmed the crew's `crew-runs.json` entry carries `"spine": null`
  (same shape as prior confirmed instances on this same work-id, per memory
  `crew-dispatch-spine-null` and this gate's own implementer's identical note) — the inherited
  `SPINE_FILE`/`SPINE_SESSION` env belongs to the Commander, not this crew. Authored and drove an own
  survey (`.agent-work/w2-reindex/g2-review/review.json`) through `checklist_engine.py`'s CLI instead of
  the MCP door, per the skill's own documented branch for this case, rather than touching the parent's
  bound spine.
- **What would have made this easier:** nothing concrete — this gate's handoff was unusually
  self-contained (close criteria mapped 1:1 onto checkable commands).

## Return status
`complete`
