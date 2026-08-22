# Candidate gate plan — smallest-diff

Constraint under design: minimize new moving parts and diff size, while
meeting every hard constraint verbatim. This candidate is a real, shippable
mechanism, not a false-green honest-null: investigation (below) found the
partial-commit hazard is real but fully addressable with one cheap git-native
check, so a negative result is not the correct deliverable here.

## Summary of the mechanism

- **No new code_map machinery.** `python -m scripts.code_map build --root .`
  already writes straight into the real `map/` and `.code-map/` trees, and
  everything under those trees except `map/INDEX.md` and `map/ids.jsonl` is
  already `.gitignore`d (`map/*` + two `!` negations; `.code-map/*` entries).
  So "build to scratch and diff" is unnecessary machinery for this repo: the
  hook can call `build` **in place** and there is nothing else in those trees
  for `git add` to ever pick up by accident. This directly follows the
  brief's steer ("always run the real build" over an incremental
  staleness-detection layer) and drops a whole layer other designs would need.
- **One new file**: `scripts/hooks/pre_commit_code_map.py` — the hook body,
  runnable directly (importable by tests, and exec'd by the installed hook).
  It (1) decides whether it is safe to rebuild-from-disk (see hazard finding
  below), (2) if safe, runs `build`, (3) stages `map/INDEX.md` and
  `map/ids.jsonl` with an explicit two-path `git add -- <path> <path>`
  (never a directory or glob add), (4) always exits 0 — fail-open, wrapped in
  one broad `try/except`, mirroring `scripts/hooks/gauge_writer_hook.py`'s
  existing documented fail-open contract (same directory, same convention,
  no new policy invented).
- **One tiny installer addition**, in `scripts/install_constellation.py`,
  shaped exactly like the existing `wire_repo_mcp_config` keyword-only
  `main()` parameter (this checkout's own `.mcp.json` wiring): a new
  `install_git_pre_commit_hook: bool = False` parameter, `False` for every
  existing test call to `main()`, `True` only from the real
  `if __name__ == "__main__":` entry point (or an explicit
  `git_repo_root=` override, mirroring `mcp_config_path=`). It writes a
  **5-line POSIX shell wrapper** at the git-resolved hooks directory (see
  below) that `exec`s the tracked `scripts/hooks/pre_commit_code_map.py` by
  absolute path resolved at *run time* via `git rev-parse --show-toplevel`
  — so the installed hook never goes stale between installs; there is
  nothing to "reinstall" after editing the hook logic.
- **Hooks-directory resolution is git-native**: `git rev-parse
  --path-format=absolute --git-path hooks` (measured below to also honor
  `core.hooksPath`, and to resolve worktrees to the *shared* hooks dir the
  main checkout uses — this very repo is checked out as a worktree, so this
  is not a hypothetical). No hardcoded `.git/hooks` join anywhere.
- **`tests/test_code_map.py::MapTreeFreshnessTests` is touched by nothing in
  this plan** — zero bytes changed, not even a comment. It stays the
  backstop for `--no-verify`, fresh clones, contributors without the hook,
  and CI, exactly as strong as today. (See "Hard constraints" table below
  for why zero-touch is achievable.)

## Investigation findings that shaped this design

- `scripts/code_map/cli.py` already takes `--root`/`--out`/`--artifacts` per
  subcommand with in-repo defaults; no CLI change needed.
- `scripts/code_map/discovery.py` enumerates the corpus via `git ls-files`
  (tracked-only), but `extract.py` (`extract.py:391`, `:1302`) reads file
  **content from disk** (`open(path).read()`), not from git's index/object
  store. This is the crux of the partial-commit hazard (below): the build
  reflects the *working tree*, not what a given commit invocation will
  actually record.
- `.gitignore` (lines ~55-73): `map/*` is ignored except `!map/INDEX.md` and
  `!map/ids.jsonl`; `.code-map/*` entries are individually ignored. Building
  in place therefore cannot make `git add` touch anything beyond the two
  named files even with a broader add — using the explicit two-path form
  anyway makes that a structural guarantee, not an incidental one, per the
  auditability constraint.
- `install_constellation.py`'s existing `wire_repo_mcp_config` /
  `mcp_config_path` keyword-only `main()` parameters (checked at
  `is_self_install`, tests always pass an explicit path, real CLI sets
  `True` only in `if __name__ == "__main__":`) are the closest existing
  precedent for "wire something into *this checkout's own* repo-level
  config as part of installing" — much closer than `wire_hooks`
  (Claude Code's per-agent `settings.json` `PostToolUse` machinery), which
  this plan does not touch or extend.
- `is_git_tracked()` in the same file is the existing pattern for "ask git,
  don't assume" about repo state from a path — same idiom this plan's
  safety check follows (ask git's index/worktree state, don't assume).
- Empirically confirmed (scratch repos under `/tmp`, git 2.43.0):
  - `git rev-parse --path-format=absolute --git-path hooks` returns the
    **shared main-checkout hooks dir** from inside a `git worktree add`
    worktree (confirmed against this very repo: its own `.git` is a
    `gitdir:` pointer file into
    `/home/tommy/projects/constellation-skills/.git/worktrees/569-w2-reindex`,
    and `git rev-parse --git-path hooks` from here resolves to
    `.../constellation-skills/.git/hooks` — the one hooks dir shared by
    every worktree of that repo). A hardcoded `<root>/.git/hooks` join
    would have silently written into a nonexistent location for this exact
    repo layout.
  - The same command honors `core.hooksPath` when set (tested: set
    `core.hooksPath=custom-hooks`, `git rev-parse --git-path hooks` returned
    `custom-hooks`), so a repo with a custom hooks path is not silently
    mis-wired either.
  - `git commit -- <path>` **does** invoke `pre-commit` the normal way.
  - `git commit -p` **does** invoke `pre-commit` the normal way, once per
    commit invocation (not once per hunk decision).

## Partial-commit hazard — finding, with evidence

**The hazard is real** if the hook rebuilds from disk unconditionally: a
pre-commit hook that runs `git add -- map/INDEX.md map/ids.jsonl` during a
`git commit <pathspec>` gets those additions **swept into the commit even
though the pathspec never named them** — this is standard git behavior
(pathspec-restricted commit takes a snapshot of the *current index*, only
*updating* pathspec-matching paths from the working tree; anything else
already staged rides along unchanged). Reproduced directly:

```
$ echo "c" >> map/INDEX.md            # dirty, unstaged, unrelated to this commit
$ echo "more dirty" >> other.txt
$ git commit -q -m "partial: commit only other.txt" -- other.txt
hook: staging map files
$ git show --stat -1
 map/INDEX.md | 1 +
 other.txt    | 1 +
 2 files changed, 2 insertions(+)
```
map/INDEX.md's unrelated, unreviewed edit landed in a commit whose pathspec
never named it.

**The fix is one cheap git-native check, not scratch-repo simulation or
staging machinery.** Define *safe* as: no tracked path other than the two
map files has any *worktree-vs-index* divergence right now —

```
git status --porcelain=v1 --untracked-files=no -- ':!map/INDEX.md' ':!map/ids.jsonl'
```

— unsafe iff any returned line has a non-space character in the second
("worktree") column. When safe, this condition is exactly the invariant
needed: the working tree agrees with the index for everything the build
reads, so **the resulting commit's tree is identical regardless of pathspec
or `-p` selection**, and building from disk is provably equal to building
from what will actually be committed. When unsafe, the hook does nothing at
all (no build, no write, no stage) — the working tree is left byte-identical
to how the hook found it, and `MapTreeFreshnessTests` remains the backstop
for that commit.

Reproduced both directions with the check installed:

1. `git commit -- other.txt` while `map/INDEX.md` had an *unstaged* edit →
   `status --porcelain` line ` M map/INDEX.md` → **skip** fires, map files
   never touched, commit of `other.txt` proceeds normally.
2. `git commit -p -- multi2.py` with two well-separated hunks, staging only
   the first (`y`) and leaving the second unstaged (`n`) →
   `git status --porcelain` reports `MM multi2.py` (staged *and* worktree
   portions differ) → **skip** fires correctly; only the hunk the author
   chose landed in the commit, and `map/` was untouched:
   ```
   [main 68af92a] partial hunk commit 2
    1 file changed, 1 insertion(+), 1 deletion(-)
   -- status after --
    M map/INDEX.md
    M multi2.py
   ```
   (the ` M map/INDEX.md` here is a pre-existing unrelated dirty line from
   an earlier step in the same scratch session, not something this commit
   touched — confirming the hook made no write.)
3. Control case (nothing else dirty, full `git commit -am`-style state):
   safe fires, `map/INDEX.md` is rebuilt and staged, and lands in the same
   commit as the source edit that made it stale — the motivating scenario.

This finding governs the design: **no temp-worktree checkout of the index,
no `git stash --keep-index` dance.** Both are the standard heavier answers
to "build only what's about to be committed," and both were considered and
rejected under smallest-diff once the porcelain check was shown sufficient
and correct by the above reasoning + reproduction. A stash-based approach
would touch the author's stash list (a real, if usually safe, side effect)
for a guarantee the porcelain check already gives for free.

## Gate sequence

### Gate 1 — hook body: safety check, rebuild, exact-two-path stage, fail-open

**Task**: Add `scripts/hooks/pre_commit_code_map.py`. Responsibilities, in
order, each independently testable:
1. `_is_safe_to_rebuild(cwd) -> bool`: runs the `git status --porcelain=v1
   --untracked-files=no -- ':!map/INDEX.md' ':!map/ids.jsonl'` check above;
   any subprocess failure (not a git repo, git missing) returns `False`
   (fail closed on *this* check specifically — "can't tell" means "don't
   touch it", not "assume safe").
2. `main()`: if unsafe, return 0 immediately, no side effects. If safe, run
   `python -m scripts.code_map build --root .` as a subprocess from the
   repo top-level (`git rev-parse --show-toplevel`); on nonzero exit, log
   one line to stderr and return 0 (fail-open — a broken build must never
   block a commit). On success, `git add -- map/INDEX.md map/ids.jsonl`
   unconditionally (a no-op add when the build produced no change; avoids a
   second git invocation to check for a diff first — smallest diff of git
   calls too). Print one stderr line naming the two paths when the add
   staged real changes (`git diff --cached --name-only` before/after
   comparison), silent otherwise. Whole body wrapped in one
   `try/except Exception` that logs-and-returns-0, mirroring
   `gauge_writer_hook.py`'s stated fail-open contract in the same directory.
3. Script is directly executable (`#!/usr/bin/env python3`, `chmod +x` at
   commit time via the repo's existing file-mode tracking) and directly
   importable by tests without needing an installed git hook.

**Close criteria**:
- New file only; zero changes to `scripts/code_map/*` or
  `tests/test_code_map.py`.
- `_is_safe_to_rebuild` and `main` are separately unit-testable pure-ish
  functions (subprocess calls injectable via `cwd`/`env` args, no hidden
  global state).

**Required evidence** (new file `tests/test_pre_commit_code_map_hook.py`,
operating on **disposable scratch git repos under a temp dir**, never this
repo's own git state — mirrors the `RepoMcpConfigWiringTests` idiom of
"every test passes an explicit throwaway target"):
- Full/clean-commit case: stale map, nothing else dirty → hook rebuilds,
  stages exactly the two paths, commit carries the fresh content.
- No-op case: map already fresh → hook runs, `git status` shows nothing
  staged, no empty diff introduced.
- Auditability: an unrelated dirty tracked file present (staged or
  unstaged) that the safety check does NOT trip on somehow (defense in
  depth — should be unreachable given the design, but assert it directly)
  never appears in the hook's own `git add` invocation or in
  `git diff --cached --name-only` beyond the two map paths. Assert by
  constructing a repo where a third tracked file is dirty and confirming it
  is what makes the run a no-op skip, not by hoping the code happens to be
  narrow.
- Partial-commit hazard, both shapes, reproduced by the test suite (not
  just by hand as in this investigation): `git commit -p` split-hunk case
  and `git commit -- <path>` case both leave `map/` completely untouched.
- Fail-open: a build subprocess forced to fail (e.g. `PYTHONPATH`/`cwd`
  pointed somewhere `-m scripts.code_map` cannot resolve) still exits 0 and
  leaves the working tree otherwise unmodified.
- Hook never exits nonzero under any exercised condition (explicit
  `returncode == 0` assertion in every test above).

**Constraints**: stdlib only (matches `scripts/code_map`'s own constraint;
this script is a sibling concern and should not add a dependency CI would
need to install). No changes outside `scripts/hooks/` and `tests/`.

### Gate 2 — wire it into `install_constellation.py`

**Task**: Add, mirroring the existing `wire_repo_mcp_config` /
`mcp_config_path` pattern exactly (same file, same section, same guard
shape):
- `resolve_git_hooks_dir(repo_root) -> Path | None`: runs
  `git rev-parse --path-format=absolute --git-path hooks` with
  `cwd=repo_root`; returns `None` on any git failure (not a repo, git
  missing) — report-only territory, never raises.
- `install_git_pre_commit_hook(repo_root, dry_run, out)`: resolves the
  hooks dir; if `None`, reports and returns (no-op). Writes the 5-line
  wrapper only if the target is absent OR already carries this installer's
  own marker comment (idempotent reinstall); if it exists and lacks the
  marker, **refuses and reports** — never clobbers a foreign hook (own
  precedent already exists in this file: `write_template_working_copies`
  "never clobber a project edit or a Charter seed"). `chmod +x` on write.
  Honors `dry_run` (prints the plan, writes nothing), matching every other
  `dry_run`-aware function in this file.
- New keyword-only `main()` params: `install_git_pre_commit_hook: bool =
  False`, `git_repo_root: Path | None = None` — same default-off,
  test-safe shape as `wire_repo_mcp_config` / `mcp_config_path`. Wired at
  the same call site, guarded by
  `install_git_pre_commit_hook and (git_repo_root is not None or
  is_self_install(args))`, calling
  `resolve_git_hooks_dir(git_repo_root or REPO_ROOT)` then
  `install_git_pre_commit_hook(...)`.
- `if __name__ == "__main__":` gets `install_git_pre_commit_hook=True`
  alongside the existing `wire_repo_mcp_config=True` — one real run wires
  both, nothing new to remember.

**Close criteria**:
- Every existing call to `main()` throughout `tests/test_install_constellation.py`
  (the ~50+ pre-existing tests) is unaffected — new params default off,
  exactly the guarantee `RepoMcpConfigWiringTests`' own docstring states for
  its sibling parameter, re-verified by running the full existing suite
  green with no changes to those tests.
- No change to `wire_hooks`, `HOOK_SETS`, `report_hook_wiring`, or any
  Claude Code `PostToolUse`/`settings.json` code path — this is a
  genuinely separate mechanism (git-native, not JSON-config-native) and
  shares no machinery with it beyond the file it lives in.

**Required evidence** (new test class `GitPreCommitHookWiringTests` in
`tests/test_install_constellation.py`, same fixture idiom as
`RepoMcpConfigWiringTests` — `tempfile.TemporaryDirectory()`, explicit
`git_repo_root=`, never the real repo):
- Default (`install_git_pre_commit_hook=False`) is a true no-op even when a
  scratch repo is present — mirrors
  `test_a_plain_main_call_never_touches_an_mcp_config_even_when_one_is_given`.
- Explicit wiring writes an executable `pre-commit` at the resolved hooks
  dir, content references `scripts/hooks/pre_commit_code_map.py`.
- Re-running is idempotent (same bytes, no error, not appended-to).
- A pre-existing foreign `pre-commit` (no marker) is left untouched and the
  run reports the refusal rather than raising or silently overwriting.
- `--dry-run` writes nothing.
- **Worktree case**: `git worktree add` a second worktree off the scratch
  repo, wire from inside the worktree, assert the wrapper lands in the
  *shared* main-checkout hooks dir (the concrete failure mode a hardcoded
  `<root>/.git/hooks` join would have hit, reproduced above against this
  very repo's own layout).

**Constraints**: change confined to `scripts/install_constellation.py` and
`tests/test_install_constellation.py`; no change to any `settings.json`
schema, `HOOK_EVENT`, or agent-target machinery.

### Gate 3 — prove it fires once installed (real end-to-end, red then green)

**Task**: No new source files. A scratch clone or `git worktree add` of
*this actual repo* (not a synthetic fixture), used to:
1. **Red proof**: without the hook installed, hand-edit a tracked `.py`
   source file, run the ordinary commit flow (`git add`, `git commit`),
   then run `pytest tests/test_code_map.py::MapTreeFreshnessTests` against
   that scratch checkout at the new commit — show it fails (map is stale),
   confirming the backstop still catches an un-hooked commit exactly as it
   does today.
2. Run `python scripts/install_constellation.py --agent claude --scope
   project ...` with the real CLI entry point (so `install_git_pre_commit_hook=True`
   fires) against that scratch checkout.
3. **Green proof**: repeat the hand-edit-and-commit sequence in the same
   scratch checkout; show `git log -1 --stat` includes `map/INDEX.md` (and
   `map/ids.jsonl` if it changed) alongside the source edit in the *same*
   commit, and `MapTreeFreshnessTests` now passes at that commit with no
   manual rebuild step taken by the operator.
4. Repeat the two partial-commit shapes from the investigation
   (`git commit -- <path>`, `git commit -p` with a split hunk) against the
   installed hook in this same scratch checkout, showing `map/` is left
   untouched in both, and the commit the author asked for is exactly what
   landed (`git show --stat -1` matches the pathspec/hunk selection).

**Close criteria**:
- All evidence is real subprocess `git`/`pytest` output captured from a
  disposable checkout, not asserted from unit-test mocks — this is the one
  gate that has to be end-to-end because gates 1-2 deliberately avoid
  touching a real installed hook or this repo's own git state.
- The scratch checkout is discarded at the end of the gate (temp dir); no
  artifact from it is committed anywhere.

**Required evidence**: the four numbered transcripts above, captured
verbatim (commands + relevant output), attached to the gate's evidence
record.

**Constraints**: read-only with respect to the real repo's tracked files
(the scratch checkout is a separate clone/worktree); no edits to any
`tests/`, `scripts/hooks/`, or `scripts/install_constellation.py` content
in this gate — it is proof-only, using what gates 1-2 built.

## Hard constraints — how each is satisfied

| Constraint | Where satisfied |
|---|---|
| Git pre-commit hook, not Claude Code `PostToolUse` | Gate 1/2: `.git/hooks/pre-commit` via `install_constellation.py`, zero touch to `HOOK_EVENT`/`HOOK_SETS`/`wire_hooks`. |
| Silent stage + commit proceeds on staleness | Gate 1: `git add` on success, no prompt, no nonzero exit ever (fail-open wrapper). |
| `MapTreeFreshnessTests` unchanged, exactly as strong | Zero edits to `tests/test_code_map.py` anywhere in this plan (all three gates). Confirmed compatible: the test rebuilds to a scratch `--out`/`--artifacts` pair and compares to the *tracked* files, independent of whether a hook exists. |
| Installed by `install_constellation.py`, proven to fire | Gate 2 (wiring + unit tests) + Gate 3 (real scratch-checkout `git commit` red/green proof). |
| Auditable staging boundary (exactly the two paths, never an unrelated dirty file) | Gate 1: explicit `git add -- map/INDEX.md map/ids.jsonl` (never a directory/glob add) + dedicated audit test; structurally reinforced by `.gitignore` already excluding everything else under `map/`/`.code-map/`. |
| Partial-commit hazard investigated and addressed | Hazard section above: reproduced the failure, derived and reproduced the fix (`git status --porcelain` worktree-divergence check), Gate 1 tests both partial-commit shapes, Gate 3 reproduces them end-to-end. |
| Out-of-scope files untouched | No gate names `generate_spine.py`, `specs/`, `scripts/checklist_engine.py`, or spine templates. |
| File ownership fence | All edits confined to `scripts/hooks/`, `scripts/install_constellation.py`, `tests/`; `scripts/code_map/` is read, not written. |
| False-green honest-null as legitimate outcome | Considered and rejected here: investigation found a sufficient, low-cost mechanism (git-native porcelain check) rather than infeasibility — the positive deliverable is warranted, not a documented negative result. |

## Axis notes (for convergence against a rival candidate)

- **Depth**: shallowest available — one new leaf script, one new pair of
  keyword-only params on an existing function, zero new abstraction layers.
  No new CLI subcommand, no new "mode" added to `scripts/code_map`, no new
  config file format.
- **Locality**: hook logic is 100% contained in one new file
  (`scripts/hooks/pre_commit_code_map.py`); installer change is additive
  and lives beside its closest existing analog (`wire_repo_mcp_config`)
  rather than beside the unrelated `wire_hooks`/`HOOK_SETS` machinery, so a
  future reader of the Claude Code hook-wiring code path is never touched
  by this change at all.
- **Seam placement**: the safety decision is seamed at the git
  index/working-tree boundary via `git status --porcelain`, which is the
  one existing seam that already carries exactly the fact needed ("does
  disk match what would be committed"). No bespoke staleness-tracking seam
  (hashes, mtimes, a manifest) was introduced — this is the direct
  application of the brief's "always run the real build" steer to the
  safety check as well as to the rebuild itself.
- **Testability**: the two new behaviors (safety check, install wiring) are
  each testable in isolation against disposable scratch git repos, with
  only one gate (Gate 3) requiring a real end-to-end checkout — and that
  gate reuses the exact same repo, not a purpose-built fixture, so its
  proof generalizes directly to "what a contributor will actually
  experience" rather than to a simplified stand-in.
