# Candidate gate plan — constraint: most-testable

Repo: `/home/tommy/projects/569-w2-reindex` (worktree of `constellation-skills`,
branch `epic-569/w2-reindex`, base `9d5aac6d`, green: 3622 passed / 6 skipped).

## 0. Investigation notes that shape this design (evidence, not presumption)

**Seam already there / not there.** `scripts/code_map/cli.py` exposes
`main(argv)` and `HANDLERS["build"] -> _build(args)`, both driven from an
`argparse.Namespace`. There is **no** plain `build(root, artifacts=None,
out=None) -> int` function callable without constructing a Namespace — the
first thing this plan adds is that seam (small, in `scripts/code_map/`),
because every other gate's testability depends on being able to call "build
into this path" from Python without an `argparse` detour or a subprocess.

**Discovery is git-mediated.** `scripts/code_map/discovery.py:
tracked_python_files()` shells out to `git ls-files -z -- *.py` with
`cwd=root`. That means `root` must be a real git working directory (a `.git`
present, directly or via worktree indirection) — `code_map build --root
<arbitrary checked-out dir with no .git>` will not enumerate anything. This
directly shapes the partial-commit mechanism below: I cannot satisfy
"build reflects exactly what's about to be committed" by `git
checkout-index`-ing files into a bare temp directory, because `discover.py`
would find zero files there. It has to be a real worktree.

**`git commit -p` / `git commit <path>` and the pre-commit hook — measured,
not assumed.** I built scratch repos and instrumented `.git/hooks/pre-commit`
to print `git diff --cached --name-only` / `git diff --cached` at hook time:

- `git commit <path>` (pathspec-restricted): hook fires once, `git diff
  --cached --name-only` shows **only** the named path. A second dirty tracked
  file and an untracked file are both invisible to `--cached` at hook time and
  remain dirty/untracked afterward. Verified.
- `git commit -p` (hunk-restricted): hook fires **once**, after the
  interactive selection has already re-written the index to contain only the
  accepted hunks. `git diff --cached` at hook time shows exactly the accepted
  hunk; the rejected hunk is provably absent from the index and remains in the
  working tree as an unstaged diff after the commit. Verified with a
  file split into two hunks, accepting only the first.

  **The hazard is real and specific**: `code_map build` reads *working-tree
  bytes* via `open()`, not index blobs. At the moment the hook runs during a
  `-p` commit, the working tree still contains the *rejected* hunk (my
  `CHANGED-BOTTOM` experiment showed this directly). A hook that ran `build`
  against the live working tree would bake the rejected hunk's effect into
  `map/INDEX.md`, then stage that file into the very commit that was supposed
  to exclude it — corrupting exactly what the author asked to leave out. This
  is the mechanism the human's hazard warning names; the fix below is chosen
  specifically to close it, with a positive test proving the closure.

- **Git hooks are not per-worktree.** `git rev-parse --git-path hooks` in this
  very checkout resolves to `/home/tommy/projects/constellation-skills/.git/hooks`
  — the directory is **shared** across every linked worktree of this repo
  (verified: `git worktree list` currently shows seven sibling worktrees,
  including two other live epic-569 lanes). Installing the hook from this
  worktree makes it fire for real commits made from any of them. This is not
  automatically wrong — hook `cwd` at invocation time is the *invoking*
  worktree's top level (standard git behavior, and separately confirmed here:
  `git worktree add --detach <tmp> <commit>` from inside a worktree cleanly
  produces an independent, self-contained worktree), so hook logic that
  resolves paths from `cwd`/`git rev-parse --show-toplevel` rather than a
  baked-in absolute path operates correctly per-worktree even though the file
  is shared. But it is a blast-radius fact worth a named test rather than a
  silent assumption, and worth calling out to the Commander as a side effect
  of "wired into install_constellation.py" in a worktree checkout.

**Existing installer idiom.** `install_constellation.py` wires Claude Code
hooks by writing `hooks.<event>` array entries into a JSON `settings.json`
(`HookSpec`, `wire_hooks`, `HOOKS_FROM_SOURCE`/`HOOKS_FROM_INSTALLED`,
`report_hook_wiring`, all guarded by `--wire-hooks`, opt-in, additive, never
silently clobbering). A git hook is a different mechanism entirely (an
executable file at a git-resolved path, not a JSON array entry), but the
**idiom** — read-only detection always on, mutation only under an explicit
opt-in flag, refuse rather than clobber unrecognized existing state, additive
never destructive — is the one this plan reuses. Also load-bearing:
`scripts/code_map/__init__.py` states the package **cannot** be bundled into
an installed skill (flat-copy breaks intra-package imports) — so this feature
is inherently self-host-only, wired only when `hooks_from ==
HOOKS_FROM_SOURCE` against a target that IS this checkout (mirrors the
existing `is_self_install` guard already used for `.mcp.json` wiring). No
target that installs a skill bundle elsewhere ever gets this hook, and that
scoping is itself a required test.

**`MapTreeFreshnessTests` (`tests/test_code_map.py:~4656`).** It rebuilds into
a scratch `--out`/`--artifacts` pair from `ROOT`'s current tracked source and
byte-compares (text-normalized) against the *working-tree* `map/INDEX.md` /
`map/ids.jsonl`. It knows nothing about hooks, staging, or the index — it is
purely "does the working tree match a fresh build of the working tree's
tracked source." It stays exactly as-is: no gate below imports it, patches
it, mocks around it, or makes it conditional. Its job (backstop for
`--no-verify`, fresh clones, contributors without the hook, and CI) is
precisely the job a hook-dependent test cannot do, which is the reason it is
named as untouched in the mission brief. One gate below runs it unmodified
as regression evidence.

## Mechanism summary

1. A pure, importable `scripts/code_map/build.py: build(root, *, artifacts=None,
   out=None) -> int` seam wraps the existing extract→render pipeline (thin
   wrapper around the same calls `cli._build` makes) so nothing downstream
   needs `argparse`.
2. A pure, importable `scripts/code_map/precommit.py` module owns all
   staleness-check / regenerate / stage-boundary logic as small functions
   taking explicit paths and an injectable `runner` (defaults to
   `subprocess.run`) for git plumbing calls — no filesystem or subprocess call
   is hidden inside a function that can't be pointed at a scratch repo or a
   fake runner. Its central function snapshots **the index, not the working
   tree**, by: `git write-tree` (the index as a tree object, ignoring
   unstaged working-tree diffs) → `git commit-tree <tree> -p HEAD -m
   <marker>` (a dangling, non-ref-touching commit) → `git worktree add
   --detach <scratch dir> <that commit>` (a real, self-contained worktree, so
   `discovery.py`'s `git ls-files` works) → `build(scratch_dir)` → compare the
   two built files against the **currently staged** blobs (`git show
   :map/INDEX.md`, `git show :map/ids.jsonl`) → on difference, copy the fresh
   bytes over the real working-tree `map/INDEX.md` / `map/ids.jsonl` and `git
   add` exactly those two paths → remove the scratch worktree. This is what
   closes the partial-commit hazard: the build input is provably the
   about-to-be-committed tree, never the live working tree.
3. A thin fail-open shim `scripts/hooks/code_map_precommit.py`
   (`.git/hooks/pre-commit`-shaped: no args, exit code only) that imports
   `scripts.code_map.precommit` and calls its entry point inside a bare
   `try/except Exception`, printing a one-line warning and always exiting 0 —
   mirrors `gauge_writer_hook.py`'s documented "fail-open, never block the
   caller" contract.
4. `install_constellation.py` gets a new, narrow wiring function
   `install_git_precommit_hook(...)` alongside `wire_hooks`, called only when
   `hooks_from == HOOKS_FROM_SOURCE` and the target is this checkout
   (self-install), gated by the existing `--wire-hooks` flag plus a new
   `--hooks` member (`"git-precommit"`, opt-in like `"rail"`) so a plain
   `--wire-hooks` run's existing behavior (Claude Code JSON entries only)
   is unchanged for every other consumer of this installer.

## Gate sequence

### Gate 1 — `build()` seam and precommit module skeleton
**Task.** Add `scripts/code_map/build.py::build(root, *, artifacts=None,
out=None) -> int`, a direct wrapper around the same two calls `cli._build`
makes (`extract.run`, `render.run`), with defaults matching `cli`'s
(`<root>/.code-map`, `<root>/map`). Add `scripts/code_map/precommit.py` with
its function signatures and docstrings (staged_map_blobs, snapshot_index_tree,
build_snapshot, compare_and_stage) but stub bodies — this gate is about the
seam, not the logic.
**Close criteria.** `build()` produces byte-identical output to `cli.main(["build", ...])`
for this repo's own tree. `cli._build` is refactored to call the new `build()`
(no behavior change) so there is exactly one build path, not two that can
drift.
**Required evidence.** New unit test:
`tests/test_code_map.py::BuildSeamTests` — call `build()` directly, diff its
`map/INDEX.md` against `cli.main`'s output for the same root, byte-identical.
Full `tests/test_code_map.py` green (no regression to the CLI's existing
tests, which now run through the wrapped path).
**Constraints.** File ownership: `scripts/code_map/`, `tests/` only. No
changes to `discovery.py`/`extract.py`/`render.py` internals.

### Gate 2 — snapshot-from-index mechanism, isolated and unit-tested
**Task.** Implement `precommit.snapshot_index_tree(repo_root, runner=subprocess.run) ->
Path` (write-tree → commit-tree → worktree add, returns the scratch
worktree path) and `precommit.remove_snapshot(repo_root, scratch, runner=...)`
(worktree remove --force). Implement `precommit.staged_blob_text(repo_root, path, runner=...) ->
str | None` (`git show :<path>`, `None` if not staged/absent — distinguishing
"no such staged blob" from "empty file").
**Close criteria.** Round-trips correctly against a real scratch git repo:
snapshot of a clean index reproduces the same file bytes as `HEAD`; snapshot
of an index with staged-but-uncommitted changes reflects those changes;
snapshot leaves zero residue in `git worktree list` after `remove_snapshot`,
even mid-way through a repo that is *itself* a linked worktree (this
checkout).
**Required evidence.** New `tests/test_code_map_precommit.py` (in-process,
each test builds its own throwaway `git init` repo in `tempfile.TemporaryDirectory()`,
no subprocess `git commit` against the shim): snapshot-of-clean-index test,
snapshot-of-staged-changes test, snapshot-and-remove-leaves-no-worktree test,
snapshot-from-within-a-worktree test (init a second worktree of the scratch
repo and snapshot from there, proving the mechanism the repo itself relies on
in dev — the finding in section 0 — actually holds, not just in theory).
**Constraints.** `scripts/code_map/`, `tests/` only. Every git call goes
through the injectable `runner` parameter — no bare module-level
`subprocess.run` call in this module — so a later test can substitute a
recording/failing fake without a real git binary.

### Gate 3 — staleness compare + stage-boundary logic, unit-tested
**Task.** Implement `precommit.build_and_compare(repo_root, runner=...) ->
StalenessResult` (dataclass: `stale: bool`, `fresh_index_md: str`,
`fresh_ids_jsonl: str`) using Gate 1's `build()` against Gate 2's snapshot,
compared against `staged_blob_text` for `map/INDEX.md` and `map/ids.jsonl`.
Implement `precommit.stage_fresh_map(repo_root, result, runner=...) -> tuple[str, ...]`
that writes the fresh bytes to the real working-tree paths and calls `git
add map/INDEX.md map/ids.jsonl` (nothing else — never a glob, never `-A`),
returning exactly which of the two paths it touched (only the ones that were
actually stale, so a fresh `ids.jsonl` next to a stale `INDEX.md` doesn't get
a needless re-stage).
**Close criteria.** For an index built from this repo's own current HEAD
(no drift), `build_and_compare` reports `stale=False`. For an index with a
staged source change that would change map output, `stale=True` and the
fresh text differs from the staged blob byte-for-byte from what a real
`code_map build` would produce.
**Required evidence.**
- `test_fresh_index_reports_not_stale` — real scratch repo seeded to mirror
  a trivial mappable corpus with correct committed map output; asserts
  `stale is False` and `git status --porcelain` is empty after the call (no
  spurious stage).
- `test_stale_index_reports_stale_and_stage_writes_exactly_two_paths` — seed a
  source change with a deliberately stale `map/INDEX.md`/`ids.jsonl`; after
  `stage_fresh_map`, `git diff --cached --name-only` is exactly
  `{map/INDEX.md, map/ids.jsonl}` and nothing else, even with an unrelated
  dirty tracked file and an unrelated untracked file present in the same
  working tree (this is the required auditable-boundary proof, driven
  in-process, no real `git commit`).
- `test_stage_fresh_map_never_touches_a_file_that_is_already_fresh` — only
  `ids.jsonl` was stale; `map/INDEX.md`'s mtime/bytes are untouched and it is
  never passed to `git add`.
**Constraints.** `scripts/code_map/`, `tests/` only.

### Gate 4 — partial-commit hazard closed and proven
**Task.** No new production code beyond what Gates 2–3 already built (the
snapshot-from-index design *is* the fix); this gate is dedicated to proving
the fix against exactly the two partial-commit shapes measured in section 0.
**Close criteria.** `build_and_compare`/`stage_fresh_map`, driven against an
index that has been restricted by pathspec or by hunk-selection relative to
the working tree, produce map content matching the **restricted** (staged)
state, never the excluded working-tree content, and stage only the two map
paths.
**Required evidence.**
- `test_pathspec_restricted_index_excludes_unstaged_sibling_file` — two
  tracked files change; only one is staged (mirrors the `git commit <path>`
  experiment in section 0, but driven at the library level via `git add
  <one file>` then calling `build_and_compare` directly — no `git commit`
  subprocess needed); asserts the built map reflects only the staged file's
  effect.
- `test_hunk_restricted_index_excludes_the_rejected_hunk` — one file with two
  hunks, only one hunk staged via `git apply --cached` (the same net index
  state `git commit -p` produces, reachable without spawning the interactive
  prompt); asserts the built map does not reflect the unstaged hunk's effect.
- One real end-to-end companion in Gate 6 that actually drives `git commit
  -p` end to end (subprocess, `printf 'y\nn\n' | git commit -p`) against the
  installed shim, as the single true-interaction-shape proof — kept to one
  case because Gates 2–4 already cover the index-state space directly.
**Constraints.** `tests/` only (uses Gates 1–3's production code unchanged).
**Honest-null trigger.** If either unit test above fails and cannot be made
to pass by adjusting the snapshot mechanism within Gates 2–3's design (i.e.,
`write-tree`/`commit-tree`/`worktree add` turns out not to isolate the index
as measured), this gate's evidence becomes a documented negative: the
partial-commit hazard is not safely closable with this approach, and the
plan converts to "detect-and-warn, never silently stage" for the partial-commit
case specifically, rather than shipping a hook that can corrupt an
intentionally-partial commit. My section-0 measurements found no such
failure, so this is a contingency the gate must still leave room for, not
the expected outcome.

### Gate 5 — fail-open shim
**Task.** `scripts/hooks/code_map_precommit.py`: no CLI args, resolves
`repo_root` via `git rev-parse --show-toplevel` from `cwd` (never a baked-in
path — required for the shared-hooks-across-worktrees finding in section 0),
calls `precommit.build_and_compare` then `stage_fresh_map` inside one
`try/except Exception`, prints a one-line message on either the fixed-silently
path or an internal failure, and unconditionally exits `0`.
**Close criteria.** The shim never raises past its own boundary; a forced
internal exception (mock `precommit.build_and_compare` to raise) still exits 0
and leaves whatever was already staged for the two map paths untouched (no
partial/corrupt write).
**Required evidence.** `tests/test_code_map_precommit.py::ShimFailOpenTests`:
run the shim as a subprocess with `PYTHONPATH` pointed at a fake
`scripts.code_map.precommit` that raises — asserts exit code 0 and stderr
carries a diagnostic. A second test asserts a genuinely clean run (no
staleness) also exits 0 with no stage. This is the one place a subprocess
invocation of the *shim* is warranted before Gate 6, because "does this
process, as a whole, always exit 0" is not expressible as a plain function
call.
**Constraints.** `scripts/hooks/` only for production code; `tests/` for
tests.

### Gate 6 — installer wiring
**Task.** Add `install_git_precommit_hook(target_root, *, dry_run, out,
runner=subprocess.run) -> str` to `install_constellation.py`, called from
`main()` alongside `wire_hooks` only when `args.wire_hooks and
args.hooks_from == HOOKS_FROM_SOURCE and hooks in {"git-precommit", "all"} and
is_self_install(...)` (reusing the existing self-install guard already used
for `.mcp.json`). Resolves the real hooks directory via `git rev-parse
--git-path hooks` run with `cwd=<project root>` (never `<root>/.git/hooks`
literally — required per the worktree finding in section 0). Writes
`scripts/hooks/code_map_precommit.py`'s absolute source path into a tiny
shell shim at `<hooks-dir>/pre-commit` (executable bit set) that just execs
the interpreter against it — same "absolute path, probed interpreter" idiom
`wire_hooks` already uses for JSON entries. Refuses (reports, does not
overwrite) if a `pre-commit` file already exists there and does not carry
this feature's own marker comment; re-running is idempotent (recognizes its
own marker, rewrites only if the source path changed).
**Close criteria.** A fresh scratch git repo with no `.git/hooks/pre-commit`
gets one installed, executable, pointing at the correct absolute shim path.
Re-running is a no-op (byte-identical file, no report of a change). A repo
with a foreign pre-commit hook is left untouched and the run reports the
conflict rather than silently clobbering it.
**Required evidence.** `tests/test_install_constellation.py`, following the
existing `wire_hooks` test idiom exactly (real scratch dirs, no mocks for the
filesystem/git parts): `test_git_precommit_hook_is_installed_executable_and_correct`,
`test_git_precommit_hook_install_is_idempotent`,
`test_git_precommit_hook_refuses_to_clobber_a_foreign_hook`,
`test_git_precommit_hook_is_only_wired_for_self_install_from_source`
(asserts a `--hooks-from installed` or non-self-install run never touches
`.git/hooks` at all — the non-installable-package boundary from section 0),
`test_git_precommit_hook_resolves_the_shared_worktree_hooks_dir` (install
from one linked worktree of a two-worktree scratch repo, assert the file
lands in the common `.git/hooks`, matching `git rev-parse --git-path hooks`
computed independently in the test).
**Constraints.** `scripts/install_constellation.py`, `tests/` only.

### Gate 7 — end-to-end red proof (real `git commit`, minimal count)
**Task.** No new production code. A small, deliberately short list of true
subprocess-level tests that actually run `install_constellation.py` then a
real `git commit` against a scratch clone/worktree, proving the hook fires
as installed rather than merely as a unit-tested function.
**Close criteria / required evidence** (`tests/test_install_constellation.py`
or a new `tests/test_code_map_precommit_e2e.py`, each its own scratch repo):
1. `test_stale_commit_is_silently_fixed_and_succeeds` — install, seed a stale
   map, real `git commit -am ...`; commit succeeds (exit 0), `git show
   HEAD:map/INDEX.md` matches a fresh build, `git status --porcelain` clean
   after.
2. `test_fresh_commit_is_a_true_noop` — same, but map already fresh; commit
   succeeds, no `map/*` diff in the resulting commit versus the parent beyond
   what the author staged.
3. `test_unrelated_dirty_file_survives_untouched` — an unrelated tracked file
   is dirty and NOT staged; after a stale-map commit, the unrelated file is
   still dirty and was never part of the commit (`git show --stat HEAD`
   excludes it).
4. `test_partial_pathspec_commit_excludes_the_unstaged_sibling` — real `git
   commit <path>` (not `-am`), the Gate 4 pathspec scenario, driven for real
   this time.
5. `test_partial_hunk_commit_excludes_the_rejected_hunk` — real `git commit
   -p` with `y`/`n` piped in, the one true end-to-end proof of the hunk case.
6. `test_second_worktree_of_the_same_repo_also_fires_correctly` — two linked
   worktrees of one scratch repo, install once, real commit from each,
   asserts each only ever touches its own `map/` tree (closes the
   shared-hooks finding from section 0 with a real commit, not just the
   snapshot-mechanism unit test from Gate 2).
**Constraints.** `tests/` only. This is intentionally the *smallest* tier —
six cases, each chosen because it cannot be faithfully expressed as a plain
function call (real hook file, real git subprocess, real interactive `-p`
input) — everything else in this plan is pushed down to Gates 1–6's
in-process unit tests on purpose, per the most-testable constraint.

### Gate 8 — regression backstop, unmodified
**Task.** No production changes. Run `tests/test_code_map.py::MapTreeFreshnessTests`
unmodified and the full suite, to close the loop on "the existing backstop is
exactly as strong as before."
**Close criteria.** `MapTreeFreshnessTests` passes with zero diff to its
source. Full `pytest` run green at the same or higher pass count than the
`3622 passed, 6 skipped` baseline, plus this plan's new tests.
**Required evidence.** `git diff` on `tests/test_code_map.py` for this whole
plan is empty. Full suite run log.
**Constraints.** No files touched in this gate beyond running tests.

## How each hard constraint is satisfied

- **Git pre-commit hook, not Claude Code PostToolUse.** Gate 5's shim is
  installed at the git-resolved hooks path (Gate 6), invoked by `git commit`
  itself, not by any Claude Code tool-call event; nothing in this plan touches
  `.claude/settings.json` or `HOOK_EVENT`/`HOOK_SPECS`.
- **Never blocks the commit.** Gate 5's shim always exits 0, proven by a
  forced-exception unit test, not just by inspection of the source.
- **`MapTreeFreshnessTests` untouched.** Gate 8 pins a zero-diff on the file
  and a green run; Gates 1–7 never import or reference it.
- **Installed by `install_constellation.py`, proven firing.** Gate 6 wires it
  (guarded by `--wire-hooks --hooks git-precommit --hooks-from source`,
  self-install only); Gate 7 proves it fires with real `git commit` calls in
  scratch repos, including a worktree-of-a-worktree case matching this dev
  environment.
- **Auditable staging boundary.** Gate 3's
  `test_stale_index_reports_stale_and_stage_writes_exactly_two_paths` proves
  `git diff --cached --name-only` is exactly the two map paths even with
  unrelated dirty/untracked files present; Gate 7's case 3 repeats the proof
  through a real commit.
- **Out-of-scope files respected.** No gate touches `generate_spine.py`,
  `specs/`, `scripts/checklist_engine.py`, or shipped spine templates; file
  ownership stays inside `scripts/hooks/`, `scripts/install_constellation.py`,
  `scripts/code_map/`, `tests/` throughout.
- **Partial-commit hazard.** Investigated with real scratch-repo experiments
  (section 0, both `git commit <path>` and `git commit -p` shapes), closed by
  building from an index snapshot (`write-tree`/`commit-tree`/`worktree add`)
  rather than the live working tree, and proven at both the unit level
  (Gate 4) and the true end-to-end level (Gate 7, cases 4–5) — not asserted,
  measured.
- **Honest-null path.** Named explicitly at Gate 4: if the index-snapshot
  approach cannot be made to pass the two partial-commit unit tests, the
  plan's deliverable becomes a documented "detect-and-warn, never
  silently-stage on a restricted commit" negative result instead of a shipped
  silent-stage hook for that case. Section 0's measurements did not find such
  a failure, so this is a contingency this plan is structured to reveal early
  (Gate 4, before the installer work in Gates 6–7), not a currently-expected
  outcome.

## Finding on the partial-commit hazard (evidence, restated)

Measured directly in scratch repos (commands and output in section 0):
`git commit <path>` and `git commit -p` both invoke `pre-commit` with the
index already reduced to exactly what will be committed; `git diff --cached`
at hook time is a faithful, git-native signal for "what is about to be
committed" in both cases. The danger is not in reading that signal (which is
easy and correct) but in what `code_map build` reads by default: live
working-tree bytes, which for a `-p` commit still contain the rejected hunk.
The fix is to make the build's *input* the index (via `write-tree` +
`commit-tree` + `worktree add`, since `discovery.py` needs a real `.git` to
run `git ls-files` against — a bare checked-out directory does not work,
confirmed by reading `discovery.py`), not to try to filter the build's
*output*. This also incidentally produces a second, git-native answer to
"which two files may this hook ever stage": `git add` is called with exactly
`map/INDEX.md` and `map/ids.jsonl` as literal arguments, never a glob or `-A`,
so the auditable-boundary constraint and the partial-commit fix share one
mechanism rather than needing two.

## Axis notes

**Depth.** Shallow at the boundaries, deep at the one place correctness lives.
The seam (`build()`) and the shim (`code_map_precommit.py`) are both
deliberately thin pass-throughs; almost all logic — including the
partial-commit fix — concentrates in one module (`precommit.py`) with an
injectable `runner`, so "how much can be tested without a real `git commit`"
is maximized by construction: nearly the whole behavior surface is reachable
by calling four functions in `precommit.py` against a scratch repo.

**Locality.** New code lands beside its closest sibling: `build.py` next to
`cli.py` in `scripts/code_map/`; `precommit.py` also in `scripts/code_map/`
(it is fundamentally a code-map concern — "is the map fresh" — not a git-hook
concern, which is why the git-hook *file* is a two-line shim and not where
the logic lives); the shim in `scripts/hooks/`, matching
`gauge_writer_hook.py`'s and `spine_rail.py`'s existing precedent exactly;
the installer change is additive inside the existing `HookSpec`/`wire_hooks`
neighborhood rather than a parallel mechanism bolted on elsewhere.

**Seam placement.** The single highest-leverage seam is the injectable
`runner` parameter on every `precommit.py` function that shells out to git.
It is what lets Gate 2/3/4 tests run against *real* scratch git repos (chosen
over mocking `subprocess` outright, because git's actual behavior — index
semantics, `write-tree` isolation, worktree mechanics — is exactly the thing
under test and a mock would have to reimplement git to be trustworthy) while
still leaving room for Gate 5's shim-level test to substitute a raising fake
without touching git at all.

**Testability.** Explicit count by tier: ~10-12 in-process unit tests (Gates
1-3) needing only a scratch `git init` repo and direct function calls; ~5
partial-commit-shape tests (Gate 4) at the same in-process tier; ~3 shim-level
subprocess tests (Gate 5, testing the shim process's exit-code contract, not
git); ~5 installer-wiring tests (Gate 6, filesystem/git-plumbing but no real
commit); exactly 6 true end-to-end tests that spawn a real `git commit` or
`git commit -p` (Gate 7) — the minimum needed to prove the shim-as-installed
fires and that the two measured partial-commit shapes hold through the real
interactive mechanism, not just through the library calls that emulate their
index state. Every pathway named in the constraint (fresh / stale / partial
commit / unrelated dirty file) has at least one in-process test *and* is
covered end-to-end at least once, so the true-subprocess tier is corroboration
rather than the only evidence for any pathway.
