"""Tests for scripts/code_map/precommit.py and scripts/hooks/code_map_precommit.py
(epic #569 gate g1-implement) -- the index-snapshot pre-commit mechanism and its
fail-open git hook shim.

Every case here runs against its own disposable scratch git repo under
`tempfile.TemporaryDirectory()`; none touches this repo's own git state (see
`tests/test_code_map.py::MapTreeFreshnessTests` for the test that guards THIS
repo's own committed `map/INDEX.md`/`ids.jsonl`, which this file leaves
untouched).

Only `map/INDEX.md` and `map/ids.jsonl` are ever tracked/copied back by the
mechanism (`precommit.MANAGED_PATHS`) -- the rest of a built map tree
(per-module pages under `map/<pkg>/`) lives only in the ephemeral worktree and
is never copied to the real repo. Assertions about *which* source changes made
it into a build therefore read the root `map/INDEX.md`'s per-module entity
counts (`(N entities`), the only granularity that survives the copy-back.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.code_map import precommit  # noqa: E402
from scripts.code_map.build import build  # noqa: E402

SHIM_PATH = ROOT / "scripts" / "hooks" / "code_map_precommit.py"

# The subset of scripts/code_map/ the mechanism actually needs at runtime
# (build's own transitive imports) -- see build.py/precommit.py docstrings.
# Vendored into a scratch repo only for the shim tests, which must resolve
# and import THAT repo's own copy, never this dev checkout's.
VENDOR_FILES = ("__init__.py", "discovery.py", "extract.py", "render.py", "build.py", "precommit.py")


# --------------------------------------------------------------------------
# scratch-repo helpers -- every test builds its own throwaway git repo here,
# never touching this repo's own git state.
# --------------------------------------------------------------------------

def _git(args, cwd, check=True, timeout=30):
    result = subprocess.run(["git"] + list(args), cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError("git {args} failed (rc={rc}): {err}".format(
            args=" ".join(args), rc=result.returncode, err=result.stderr))
    return result


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _vendor_code_map(root: Path):
    dest = root / "scripts" / "code_map"
    dest.mkdir(parents=True, exist_ok=True)
    src = ROOT / "scripts" / "code_map"
    for name in VENDOR_FILES:
        shutil.copyfile(src / name, dest / name)


def _init_scratch_repo(root: Path, *, vendor=False):
    """A minimal scratch git repo with one tracked python module, committed."""
    root.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q"], root)
    _git(["config", "user.email", "test@example.com"], root)
    _git(["config", "user.name", "Test"], root)
    _write(root / "pkg" / "__init__.py", "")
    _write(root / "pkg" / "a.py", "def a():\n    return 1\n")
    if vendor:
        _vendor_code_map(root)
    _git(["add", "-A"], root)
    _git(["commit", "-q", "-m", "initial"], root)
    return root


def _stage_single_hunk(repo, relpath, hunk_index):
    """Stage exactly one hunk of `relpath`'s unstaged diff via `git apply
    --cached`, the same net index state `git add -p` produces for a single
    chosen hunk."""
    diff = _git(["diff", "--", relpath], repo).stdout
    lines = diff.splitlines(keepends=True)
    header_end = next(i for i, l in enumerate(lines) if l.startswith("@@"))
    header = lines[:header_end]
    hunks, current = [], []
    for line in lines[header_end:]:
        if line.startswith("@@") and current:
            hunks.append(current)
            current = []
        current.append(line)
    if current:
        hunks.append(current)
    patch = "".join(header + hunks[hunk_index])
    proc = subprocess.run(
        ["git", "apply", "--cached", "--recount", "-"],
        cwd=str(repo), input=patch, capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError("git apply --cached failed: {err}\npatch:\n{patch}".format(err=proc.stderr, patch=patch))


def _staged_names(repo):
    return set(_git(["diff", "--cached", "--name-only"], repo).stdout.split())


def _status_porcelain(repo):
    return _git(["status", "--porcelain"], repo).stdout


def _worktree_count(repo):
    return len([l for l in _git(["worktree", "list"], repo).stdout.splitlines() if l.strip()])


def _run_precommit_then_commit_map(repo):
    """Bring a fresh scratch repo's map fully up to date and committed, so a
    later test starts from a known no-op baseline."""
    result = precommit.run_precommit(repo)
    if result["staged"]:
        _git(["commit", "-q", "-m", "map"], repo)
    return result


# --------------------------------------------------------------------------
# m1: build() seam + cli.py refactor
# --------------------------------------------------------------------------

class BuildSeamTests(unittest.TestCase):
    """build() is a plain-importable seam and cli._build now delegates to it
    -- one build path, not two that can drift. Prove the CLI subcommand and
    the direct library call produce byte-identical output for this repo's
    own tree."""

    def test_cli_build_and_library_build_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            cli_out, cli_artifacts = tmp / "cli-map", tmp / "cli-artifacts"
            lib_out, lib_artifacts = tmp / "lib-map", tmp / "lib-artifacts"

            proc = subprocess.run(
                [sys.executable, "-m", "scripts.code_map", "build", "--root", str(ROOT),
                 "--artifacts", str(cli_artifacts), "--out", str(cli_out)],
                cwd=str(ROOT), capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(proc.returncode, 0, "cli build failed\n{o}\n{e}".format(o=proc.stdout, e=proc.stderr))

            status = build(str(ROOT), artifacts=str(lib_artifacts), out=str(lib_out))
            self.assertEqual(status, 0)

            for name in ("INDEX.md", "ids.jsonl"):
                cli_text = (cli_out / name).read_text(encoding="utf-8")
                lib_text = (lib_out / name).read_text(encoding="utf-8")
                self.assertEqual(lib_text, cli_text, "{name} differs between cli build and library build()".format(name=name))


# --------------------------------------------------------------------------
# m2: precommit.py core mechanism -- fresh/no-op, stale/rebuild-and-stage
# --------------------------------------------------------------------------

class PrecommitCoreTests(unittest.TestCase):
    def test_fresh_no_op_leaves_status_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")
            _run_precommit_then_commit_map(repo)

            result = precommit.run_precommit(repo)

            self.assertEqual(result["staged"], [])
            self.assertEqual(_status_porcelain(repo), "")
            self.assertEqual(_worktree_count(repo), 1)

    def test_stale_rebuild_stages_exactly_the_two_managed_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")
            _run_precommit_then_commit_map(repo)

            _write(repo / "pkg" / "a.py", "def a():\n    return 1\n\n\ndef b():\n    return 2\n")
            _git(["add", "pkg/a.py"], repo)

            result = precommit.run_precommit(repo)

            self.assertEqual(sorted(result["staged"]), ["map/INDEX.md"])
            self.assertEqual(_staged_names(repo), {"map/INDEX.md", "pkg/a.py"})

    def test_cleanup_removes_worktree_on_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")
            precommit.run_precommit(repo)
            self.assertEqual(_worktree_count(repo), 1)
            self.assertNotIn("code-map-precommit-", _git(["worktree", "list"], repo).stdout)


# --------------------------------------------------------------------------
# m3: partial-commit correctness -- the index-snapshot mechanism's whole point
# --------------------------------------------------------------------------

class PartialCommitTests(unittest.TestCase):
    def _repo_with_two_modules(self, tmp):
        repo = _init_scratch_repo(Path(tmp) / "scratch")
        _write(repo / "pkg" / "b.py", "def b():\n    return 2\n")
        _git(["add", "-A"], repo)
        _git(["commit", "-q", "-m", "add pkg.b"], repo)
        _run_precommit_then_commit_map(repo)
        return repo

    def test_pathspec_restricted_partial_commit_excludes_unstaged_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_two_modules(tmp)

            _write(repo / "pkg" / "a.py", "def a():\n    return 1\n\n\ndef a_extra():\n    return 11\n")
            _write(repo / "pkg" / "b.py", "def b():\n    return 2\n\n\ndef b_extra():\n    return 22\n")
            _git(["add", "pkg/a.py"], repo)  # b.py's edit is deliberately left unstaged

            precommit.run_precommit(repo)

            built = (repo / "map" / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("pkg.a](pkg.a/INDEX.md) (2 entities", built)
            self.assertIn("pkg.b](pkg.b/INDEX.md) (1 entities", built)
            self.assertNotIn("pkg.b](pkg.b/INDEX.md) (2 entities", built)
            # the real unstaged sibling on disk is untouched by the mechanism
            self.assertIn("b_extra", (repo / "pkg" / "b.py").read_text(encoding="utf-8"))

    def test_hunk_restricted_partial_commit_excludes_unstaged_hunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")
            # Six functions today (a, 4 spacers, c) -- the spacers exist only
            # to put >3 unchanged lines between the two edit points below, so
            # git splits the diff into two separate hunks instead of one.
            original = (
                "def a():\n    return 1\n\n\n"
                "def spacer_1():\n    return 100\n\n\n"
                "def spacer_2():\n    return 100\n\n\n"
                "def spacer_3():\n    return 100\n\n\n"
                "def spacer_4():\n    return 100\n\n\n"
                "def c():\n    return 3\n"
            )
            _write(repo / "pkg" / "a.py", original)
            _git(["add", "pkg/a.py"], repo)
            _git(["commit", "-q", "-m", "expand a.py"], repo)
            _run_precommit_then_commit_map(repo)

            updated = original.replace(
                "def a():\n    return 1\n\n\n",
                "def a():\n    return 1\n\n\ndef hunk_one():\n    return 11\n\n\n",
            ).replace(
                "def c():\n    return 3\n",
                "def hunk_two():\n    return 22\n\n\ndef c():\n    return 3\n",
            )
            _write(repo / "pkg" / "a.py", updated)
            _stage_single_hunk(repo, "pkg/a.py", 0)  # only the hunk_one insertion

            staged_diff = _git(["diff", "--cached", "--", "pkg/a.py"], repo).stdout
            self.assertIn("hunk_one", staged_diff)
            self.assertNotIn("hunk_two", staged_diff)

            precommit.run_precommit(repo)

            built = (repo / "map" / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("pkg.a](pkg.a/INDEX.md) (7 entities", built)  # 6 + hunk_one only
            self.assertNotIn("pkg.a](pkg.a/INDEX.md) (8 entities", built)  # would mean both hunks leaked in

    def test_unrelated_dirty_file_is_never_staged_by_the_mechanism(self):
        for dirty_mode in ("staged", "unstaged"):
            with self.subTest(dirty_mode=dirty_mode):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = self._repo_with_two_modules(tmp)

                    _write(repo / "pkg" / "c.py", "def c():\n    return 3\n")
                    if dirty_mode == "staged":
                        _git(["add", "pkg/c.py"], repo)
                    # the intended commit only touches a.py
                    _write(repo / "pkg" / "a.py", "def a():\n    return 1\n\n\ndef a_extra():\n    return 11\n")
                    _git(["add", "pkg/a.py"], repo)

                    before = _staged_names(repo)
                    precommit.run_precommit(repo)
                    after = _staged_names(repo)

                    newly_staged = after - before
                    self.assertTrue(
                        newly_staged.issubset({"map/INDEX.md", "map/ids.jsonl"}),
                        "mechanism staged something beyond the managed paths: {s}".format(s=newly_staged),
                    )
                    self.assertNotIn("pkg/c.py", newly_staged)


# --------------------------------------------------------------------------
# m4: concurrent-invocation, forced-timeout, forced-exception
# --------------------------------------------------------------------------

def _spawn_precommit_subprocess(repo):
    """Launch `precommit.run_precommit(repo)` in its OWN fresh interpreter
    process (not a thread) and return the live `Popen`. Real concurrent
    invocations are separate OS processes too -- each `git commit` spawns its
    own hook subprocess -- and `extract.py`'s module-level `TABLES`/`ROOT`
    globals (read-only reference material, not this gate's to change) make
    two `build()` calls sharing ONE interpreter cross-talk on that state.
    Threading would therefore manufacture a hazard concurrent `git commit`s
    never actually hit; separate processes test the real property instead:
    whether `git worktree add`/`remove` collide under genuine concurrent load."""
    # build()'s own stages print progress/diagnostics to stdout, so the
    # result is marked with a sentinel prefix and pulled out of the mixed
    # stream rather than assuming the JSON is the only (or the last) line.
    code = (
        "import sys, json\n"
        "sys.path.insert(0, {root!r})\n"
        "from scripts.code_map import precommit\n"
        "print('RESULT:' + json.dumps(precommit.run_precommit({repo!r})))\n"
    ).format(root=str(ROOT), repo=str(repo))
    return subprocess.Popen(
        [sys.executable, "-B", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


class ConcurrencyTimeoutTests(unittest.TestCase):
    def test_concurrent_invocations_do_not_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = _init_scratch_repo(tmp / "scratch")
            # Bring the repo to a fully fresh, no-op state first.
            _run_precommit_then_commit_map(repo)
            self.assertEqual(precommit.run_precommit(repo)["staged"], [])

            # The real hazard this guards is two SIBLING WORKTREES committing
            # at once (the handoff's own framing throughout), each running
            # the mechanism against its OWN worktree path -- and each with
            # its OWN per-worktree index, exactly as real git worktrees have
            # had since git 2.5. Running two invocations against the SAME
            # worktree path instead would make both processes fight over
            # that one worktree's `.git/index.lock` on `git write-tree` --
            # a real git behavior, but not a hazard two independent `git
            # commit`s in two different worktrees would ever hit, since they
            # never share an index. Two worktrees is the faithful shape.
            sibling = tmp / "sibling-worktree"
            _git(["worktree", "add", "--detach", str(sibling), "HEAD"], repo)

            procs = [_spawn_precommit_subprocess(repo), _spawn_precommit_subprocess(sibling)]
            outcomes = [p.communicate(timeout=30) for p in procs]

            for i, (proc, (stdout, stderr)) in enumerate(zip(procs, outcomes)):
                self.assertEqual(proc.returncode, 0, "invocation {i} failed: {err}".format(i=i, err=stderr))
                line = next(l for l in stdout.splitlines() if l.startswith("RESULT:"))
                result = json.loads(line[len("RESULT:"):])
                self.assertEqual(result["staged"], [], "invocation {i} unexpectedly staged: {r}".format(i=i, r=result))

            # 2 real worktrees (main + sibling), zero leftover
            # `code-map-precommit-*` ephemeral ones from either invocation.
            self.assertEqual(_worktree_count(repo), 2)
            self.assertNotIn("code-map-precommit-", _git(["worktree", "list"], repo).stdout)

    def test_forced_timeout_still_exits_zero_within_bounded_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")

            def fake_runner(args, cwd=None, timeout=None, **kwargs):
                # Only the targeted call hangs -- "a fake runner that sleeps
                # past 10s on ONE subprocess call" (Required Evidence). Every
                # other call behaves normally so this test isolates one
                # timeout rather than stacking several sequential ones.
                if args[:2] == ["git", "write-tree"]:
                    # Model what a real `subprocess.run(..., timeout=10)`
                    # does on a hung child: it blocks for the full budget
                    # before raising. A fake that raised instantly would
                    # prove nothing about the mechanism not adding further
                    # delay of its own.
                    time.sleep(timeout or 0)
                    raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)
                return subprocess.run(args, cwd=cwd, timeout=timeout, **kwargs)

            start = time.monotonic()
            rc = precommit.main(repo, runner=fake_runner)
            elapsed = time.monotonic() - start

            self.assertEqual(rc, 0)
            self.assertLess(elapsed, 15, "fail-open took {s:.1f}s, expected well under 15s".format(s=elapsed))

    def test_forced_exception_after_worktree_created_exits_zero_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch")
            before_status = _status_porcelain(repo)

            def flaky_runner(args, **kwargs):
                if args[:2] == ["git", "show"]:
                    raise RuntimeError("simulated failure during copy-back")
                return subprocess.run(args, **kwargs)

            rc = precommit.main(repo, runner=flaky_runner)

            self.assertEqual(rc, 0)
            self.assertEqual(_status_porcelain(repo), before_status)
            self.assertEqual(_worktree_count(repo), 1)
            self.assertNotIn("code-map-precommit-", _git(["worktree", "list"], repo).stdout)


# --------------------------------------------------------------------------
# m5: the fail-open hook shim + worktree-run-time resolution
# --------------------------------------------------------------------------

class ShimTests(unittest.TestCase):
    def _run_shim(self, cwd):
        # -B: no .pyc bytecode cache written into the vendored scratch
        # package -- that would show up as untracked __pycache__/ noise in
        # git status, which is a test-harness artifact, not mechanism output.
        return subprocess.run(
            [sys.executable, "-B", str(SHIM_PATH)], cwd=str(cwd), capture_output=True, text=True, timeout=30,
        )

    def test_shim_stages_via_a_real_subprocess_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch", vendor=True)

            proc = self._run_shim(repo)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("map/INDEX.md", proc.stderr)
            self.assertEqual(_staged_names(repo), {"map/INDEX.md"})

    def test_shim_no_op_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_scratch_repo(Path(tmp) / "scratch", vendor=True)
            first = self._run_shim(repo)
            self.assertEqual(first.returncode, 0, first.stderr)
            _git(["commit", "-q", "-m", "map"], repo)

            second = self._run_shim(repo)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(second.stderr.strip(), "")
            self.assertEqual(_status_porcelain(repo), "")

    def test_worktree_run_time_resolution_fails_open_when_module_predates_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = _init_scratch_repo(tmp / "scratch", vendor=False)
            old_commit = _git(["rev-parse", "HEAD"], repo).stdout.strip()

            # The feature lands on a LATER commit; a worktree checked out at
            # the old commit lacks scripts/code_map/precommit.py entirely.
            _vendor_code_map(repo)
            _git(["add", "-A"], repo)
            _git(["commit", "-q", "-m", "add precommit feature"], repo)

            old_worktree = tmp / "old-worktree"
            _git(["worktree", "add", "--detach", str(old_worktree), old_commit], repo)
            try:
                proc = self._run_shim(old_worktree)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("fail-open", proc.stderr)
            finally:
                _git(["worktree", "remove", "--force", str(old_worktree)], repo)


if __name__ == "__main__":
    unittest.main()
