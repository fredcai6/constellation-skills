"""tests/test_code_map_precommit_e2e.py -- gate g3-implement (epic #569):
end-to-end proof that gates 1-2's shipped code (the index-snapshot
pre-commit mechanism and its installer wiring) actually works, against real
scratch git repos driven by real subprocess `git` + `pytest`.

This is a proof-only gate: no production code changes. Every case here
exercises a REAL `git commit`, a REAL install via
`scripts/install_constellation.py`'s actual `__main__` entry point, and a
REAL `tests/test_code_map.py::MapTreeFreshnessTests` run -- never an
in-session simulation of any of those.

Topology: every scratch fixture is ONE local bare clone of THIS actual
repo's common `.git` (read-only, via `git rev-parse --git-common-dir`),
followed by one or more `git worktree add` calls off that ONE shared clone
-- never a second clone. That is what makes the shared-hooks-directory
fact (a `pre-commit` hook lives once per repository and is visible from
every linked worktree) real rather than simulated, and it is the real
hazard this repo's own dev layout has (8+ sibling worktrees sharing one
`.git`). Nothing here ever touches THIS repo's own git state -- every
scratch clone/worktree lives under a `tempfile.TemporaryDirectory()` and is
discarded at test end.

The red-proof (case 1) is pinned to this branch's actual `HEAD` at the time
this file was authored: `9d5aac6d` (confirmed via `git rev-parse HEAD` --
gates 1-2 landed as uncommitted working-tree changes on top of it, so this
gate's own commit history had not moved). Each test also asserts the
scratch checkout's `HEAD` actually matches, rather than assuming it.
"""

import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PINNED_SHA_PREFIX = "9d5aac6d"

_GIT_TIMEOUT = 60
_PYTEST_TIMEOUT = 180
_INSTALL_TIMEOUT = 120


# ---------------------------------------------------------------------------
# scratch topology helpers -- one shared clone, worktrees added off it
# ---------------------------------------------------------------------------

def _git(args, cwd, check=True, timeout=_GIT_TIMEOUT, input=None):
    result = subprocess.run(
        ["git"] + list(args), cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout, input=input,
    )
    if check and result.returncode != 0:
        raise RuntimeError("git {args} failed (rc={rc}) in {cwd}:\nSTDOUT:\n{out}\nSTDERR:\n{err}".format(
            args=" ".join(args), rc=result.returncode, cwd=cwd, out=result.stdout, err=result.stderr))
    return result


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _configure_identity(repo):
    _git(["config", "user.email", "e2e@example.com"], repo)
    _git(["config", "user.name", "E2E"], repo)


def _actual_repo_common_git_dir():
    """This actual repo's own common `.git` directory, resolved read-only.
    Cloning from here (never the working copy) means the clone reflects
    committed history only, independent of whatever uncommitted edits sit in
    THIS worktree right now."""
    return Path(_git(["rev-parse", "--git-common-dir"], ROOT).stdout.strip())


def _make_shared_scratch_git(tmp: Path) -> Path:
    """ONE local bare clone of this actual repo's full history into
    `<tmp>/shared.git`. Every worktree a case needs is `git worktree add` off
    THIS one shared `.git` -- never a second clone -- so worktrees genuinely
    share one hooks directory: `<shared>/hooks/pre-commit`, exactly the
    topology this repo's own 8+ sibling worktrees actually have."""
    shared = tmp / "shared.git"
    _git(["clone", "--bare", "--", str(_actual_repo_common_git_dir()), str(shared)], tmp)
    return shared


def _worktree_add(shared_git: Path, path: Path, ref: str) -> Path:
    _git(["worktree", "add", "--detach", str(path), ref], shared_git)
    _configure_identity(path)
    return path


def _resolve_hooks_dir(worktree: Path) -> Path:
    """The hooks directory a real `git commit` in `worktree` actually
    consults -- same `git rev-parse --path-format=absolute --git-path hooks`
    idiom `install_constellation.py`'s own `resolve_git_hooks_dir` uses. A
    linked worktree's `.git` is a file pointer, not a directory, so
    `worktree / ".git" / "hooks"` is NOT this path -- it resolves through to
    the shared bare repo's `hooks/`, which is exactly the point of this
    fixture's shared-hooks-directory topology."""
    return Path(_git(
        ["rev-parse", "--path-format=absolute", "--git-path", "hooks"], worktree,
    ).stdout.strip())


def _gates_1_2_changed_paths():
    """The `scripts/` paths gates 1-2 changed in THIS actual repo's own
    working tree (modified + untracked), read via `git status --porcelain`.
    Gates 1-2 landed as uncommitted working-tree changes on top of the pinned
    SHA (per the handoff), so a scratch worktree `git worktree add`ed off
    that SHA gets none of them from history. Read-only against ROOT."""
    out = _git(
        ["status", "--porcelain", "--",
         "scripts/code_map", "scripts/hooks", "scripts/install_constellation.py"],
        ROOT,
    ).stdout
    return [line[3:].strip() for line in out.splitlines() if line[3:].strip()]


def _snapshot_gates_1_2_onto(worktree):
    """Copy gates 1-2's current (uncommitted) shipped code from THIS actual
    repo onto `worktree` and commit it as a baseline, so a scratch checkout
    can actually install and run the mechanism gates 1-2 already shipped.
    Read-only against ROOT; never any path outside `scripts/code_map`,
    `scripts/hooks`, `scripts/install_constellation.py`. Case 1 (the RED
    proof) deliberately never calls this -- it proves the pre-existing
    backstop's behavior BEFORE gates 1-2 exist at all."""
    changed = _gates_1_2_changed_paths()
    for rel in changed:
        src = ROOT / rel
        dest = worktree / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
    _git(["add", "-A", "--",
          "scripts/code_map", "scripts/hooks", "scripts/install_constellation.py"], worktree)
    _git(["commit", "-q", "-m", "baseline: snapshot gates 1-2 shipped code for e2e proof"], worktree)
    return changed


def _assert_pinned_head(testcase, worktree, ref=PINNED_SHA_PREFIX):
    actual_head = _git(["rev-parse", "HEAD"], worktree).stdout.strip()
    testcase.assertTrue(
        actual_head.startswith(ref),
        "scratch checkout HEAD {h} does not match pinned SHA {s}".format(h=actual_head, s=ref),
    )
    return actual_head


def _fresh_scratch_worktree(tmp: Path, name: str, ref: str = PINNED_SHA_PREFIX, snapshot_gates_1_2=True,
                            testcase=None):
    """A fresh shared clone + one worktree off it, pinned at `ref` -- the
    'own scratch git worktree add pair off one shared scratch .git' every
    independent case gets. Returns `(shared_git, worktree_path)`. Confirms
    the checkout actually landed at `ref` BEFORE any baseline snapshot moves
    HEAD (pass `testcase` to assert it; always at least a plain `assert`).
    By default also snapshots gates 1-2's current shipped code as a baseline
    commit, since it is uncommitted in the real repo and a pinned-SHA
    checkout would otherwise not have it at all; pass
    `snapshot_gates_1_2=False` for the RED proof, which must run without
    it."""
    shared = _make_shared_scratch_git(tmp)
    wt = _worktree_add(shared, tmp / name, ref)
    if testcase is not None:
        _assert_pinned_head(testcase, wt, ref)
    else:
        actual_head = _git(["rev-parse", "HEAD"], wt).stdout.strip()
        assert actual_head.startswith(ref), "scratch checkout HEAD {h} does not match pinned SHA {s}".format(
            h=actual_head, s=ref)
    if snapshot_gates_1_2:
        _snapshot_gates_1_2_onto(wt)
    return shared, wt


def _hand_edit_tracked_file(worktree, marker):
    """Append one small function to a real tracked module -- changes that
    module's entity count in `map/INDEX.md`, which is what makes a
    stale-vs-fresh comparison meaningful. `scripts/code_map/discovery.py` is
    small and unrelated to what this gate is allowed to touch; it is only
    ever edited inside an ephemeral scratch worktree, never in this repo."""
    rel = "scripts/code_map/discovery.py"
    target = worktree / rel
    text = target.read_text(encoding="utf-8")
    text += "\n\ndef _e2e_marker_{marker}():\n    return 1\n".format(marker=marker)
    _write(target, text)
    return rel


def _run_pytest(args, cwd, timeout=_PYTEST_TIMEOUT):
    return subprocess.run(
        [sys.executable, "-m", "pytest"] + list(args), cwd=str(cwd),
        capture_output=True, text=True, timeout=timeout,
    )


def _run_freshness_test(worktree):
    return _run_pytest(["tests/test_code_map.py::MapTreeFreshnessTests", "-q"], worktree)


def _run_real_cli_install(worktree, timeout=_INSTALL_TIMEOUT):
    """The real CLI entry point: `python <scratch>/scripts/install_constellation.py
    --agent claude --scope project --skills charter`, invoked as a real
    subprocess with cwd=<scratch worktree> and NO --dest/--project override.
    `is_self_install(args)` (`args.dest is None and args.project is None`) is
    therefore True, and `REPO_ROOT` inside the SCRATCH copy of the module
    resolves to the scratch worktree itself (`Path(__file__).resolve().parents[1]`)
    -- so this is the scratch checkout's own `__main__` block running,
    `install_git_pre_commit_hook=True` included, never a test-only override of
    `git_repo_root`. `--scope project` keeps every write inside the scratch
    worktree's own `.claude/`, never the real machine's `~/.claude`."""
    installer = worktree / "scripts" / "install_constellation.py"
    return subprocess.run(
        [sys.executable, str(installer), "--agent", "claude", "--scope", "project", "--skills", "charter"],
        cwd=str(worktree), capture_output=True, text=True, timeout=timeout,
    )


def _module_entity_count(map_index_text, module):
    """The per-module entity count for `module` out of the ROOT
    `map/INDEX.md` -- the only granularity that survives the copy-back,
    since `MANAGED_PATHS` never includes the per-module `map/<pkg>/INDEX.md`
    pages (see this module's own docstring)."""
    pattern = r"\[{mod}\]\({mod}/INDEX\.md\) \((\d+) entities".format(mod=re.escape(module))
    match = re.search(pattern, map_index_text)
    assert match, "module {mod} not found in map/INDEX.md".format(mod=module)
    return int(match.group(1))


def _status_porcelain(repo):
    return _git(["status", "--porcelain"], repo).stdout


def _staged_names(repo):
    return set(_git(["diff", "--cached", "--name-only"], repo).stdout.split())


def _stage_single_hunk(repo, relpath, hunk_index):
    """Stage exactly one hunk of `relpath`'s unstaged diff via `git apply
    --cached` -- same net index state `git add -p` produces for a single
    chosen hunk, but scriptable."""
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
        cwd=str(repo), input=patch, capture_output=True, text=True, timeout=_GIT_TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError("git apply --cached failed: {err}\npatch:\n{patch}".format(err=proc.stderr, patch=patch))


# ---------------------------------------------------------------------------
# Case 1 -- RED PROOF, pinned to the shipped SHA
# ---------------------------------------------------------------------------

class RedProofBeforeInstallTests(unittest.TestCase):
    def test_case1_red_without_hook_freshness_test_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared, wt = _fresh_scratch_worktree(tmp, "wt-red", snapshot_gates_1_2=False)
            _assert_pinned_head(self, wt)

            # no hook installed anywhere in this shared topology yet
            self.assertFalse((_resolve_hooks_dir(wt) / "pre-commit").exists())

            _hand_edit_tracked_file(wt, "case1")
            _git(["add", "scripts/code_map/discovery.py"], wt)
            _git(["commit", "-q", "-m", "case1: hand-edit with no hook installed"], wt)

            proc = _run_freshness_test(wt)

            self.assertNotEqual(
                proc.returncode, 0,
                "MapTreeFreshnessTests unexpectedly passed with no hook installed and a "
                "stale map:\nSTDOUT:\n{o}\nSTDERR:\n{e}".format(o=proc.stdout, e=proc.stderr))
            self.assertIn("FAILED", proc.stdout + proc.stderr)


# ---------------------------------------------------------------------------
# Cases 2-3 -- real CLI install, then GREEN PROOF
# ---------------------------------------------------------------------------

class InstallThenGreenProofTests(unittest.TestCase):
    def test_case2_3_real_cli_install_then_green_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared, wt = _fresh_scratch_worktree(tmp, "wt-install", testcase=self)

            # case 2: install via the real CLI entry point, no override
            install_proc = _run_real_cli_install(wt)
            self.assertEqual(
                install_proc.returncode, 0,
                "real CLI install failed:\nSTDOUT:\n{o}\nSTDERR:\n{e}".format(
                    o=install_proc.stdout, e=install_proc.stderr))
            hook_path = _resolve_hooks_dir(wt) / "pre-commit"
            self.assertTrue(hook_path.is_file(), "install did not write a pre-commit hook")
            self.assertIn("scripts/hooks/code_map_precommit.py", hook_path.read_text(encoding="utf-8"))

            # case 3: repeat the hand-edit-and-commit; the hook must fire for real
            _hand_edit_tracked_file(wt, "case3")
            _git(["add", "scripts/code_map/discovery.py"], wt)
            _git(["commit", "-q", "-m", "case3: hand-edit with hook installed"], wt)

            stat = _git(["log", "-1", "--stat"], wt).stdout
            self.assertIn("map/INDEX.md", stat)

            freshness = _run_freshness_test(wt)
            self.assertEqual(
                freshness.returncode, 0,
                "MapTreeFreshnessTests failed after the hook fired:\nSTDOUT:\n{o}\nSTDERR:\n{e}".format(
                    o=freshness.stdout, e=freshness.stderr))


# ---------------------------------------------------------------------------
# Case 4 -- pathspec-restricted partial commit
# ---------------------------------------------------------------------------

class PathspecRestrictedPartialCommitTests(unittest.TestCase):
    def test_case4_pathspec_restricted_commit_excludes_unstaged_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared, wt = _fresh_scratch_worktree(tmp, "wt-pathspec", testcase=self)
            self.assertEqual(_run_real_cli_install(wt).returncode, 0)

            discovery = wt / "scripts" / "code_map" / "discovery.py"
            build = wt / "scripts" / "code_map" / "build.py"
            discovery_text = discovery.read_text(encoding="utf-8")
            build_text = build.read_text(encoding="utf-8")
            _write(discovery, discovery_text + "\n\ndef _e2e_marker_case4a():\n    return 1\n")
            _write(build, build_text + "\n\ndef _e2e_marker_case4b():\n    return 1\n")

            before_map = (wt / "map" / "INDEX.md").read_text(encoding="utf-8")

            # commit ONLY discovery.py -- build.py's edit is deliberately left unstaged
            _git(["add", "--", "scripts/code_map/discovery.py"], wt)
            _git(["commit", "-q", "-m", "case4: pathspec-restricted commit", "--", "scripts/code_map/discovery.py"], wt)

            after_map = (wt / "map" / "INDEX.md").read_text(encoding="utf-8")
            self.assertNotEqual(before_map, after_map, "map/ was not touched by the committed change")

            staged_names = set(_git(["show", "--stat", "--name-only", "HEAD"], wt).stdout.splitlines())
            self.assertNotIn("scripts/code_map/build.py", staged_names)
            self.assertIn("_e2e_marker_case4b", build.read_text(encoding="utf-8"))
            self.assertIn("build.py", _status_porcelain(wt))


# ---------------------------------------------------------------------------
# Case 5 -- hunk-restricted partial commit
# ---------------------------------------------------------------------------

class HunkRestrictedPartialCommitTests(unittest.TestCase):
    def test_case5_hunk_restricted_commit_excludes_rejected_hunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared, wt = _fresh_scratch_worktree(tmp, "wt-hunk", testcase=self)
            self.assertEqual(_run_real_cli_install(wt).returncode, 0)

            discovery = wt / "scripts" / "code_map" / "discovery.py"
            original = discovery.read_text(encoding="utf-8")
            # two well-separated hunks: one inserted right after the
            # EXCLUDED_PREFIXES assignment, the other appended at EOF, with
            # ~20 unchanged original lines between them so git splits them
            # into two hunks rather than merging into one contiguous edit
            # (two pure end-of-file insertions would NOT split, since there
            # is no unchanged context between them).
            updated = original.replace(
                'EXCLUDED_PREFIXES = (".agent-work/",)\n',
                'EXCLUDED_PREFIXES = (".agent-work/",)\n'
                "\n\ndef _e2e_marker_case5_hunk_one():\n    return 1\n",
            ) + "\n\ndef _e2e_marker_case5_hunk_two():\n    return 2\n"
            _write(discovery, updated)

            diff = _git(["diff", "--", "scripts/code_map/discovery.py"], wt).stdout
            hunk_count = diff.count("@@")
            self.assertGreaterEqual(hunk_count, 4, "expected at least two hunks (2 '@@' pairs):\n{d}".format(d=diff))

            _stage_single_hunk(wt, "scripts/code_map/discovery.py", 0)
            staged_diff = _git(["diff", "--cached", "--", "scripts/code_map/discovery.py"], wt).stdout
            self.assertIn("_e2e_marker_case5_hunk_one", staged_diff)
            self.assertNotIn("_e2e_marker_case5_hunk_two", staged_diff)

            before_map = (wt / "map" / "INDEX.md").read_text(encoding="utf-8")
            before_count = _module_entity_count(before_map, "scripts.code_map.discovery")
            _git(["commit", "-q", "-m", "case5: hunk-restricted commit"], wt)
            after_map = (wt / "map" / "INDEX.md").read_text(encoding="utf-8")
            after_count = _module_entity_count(after_map, "scripts.code_map.discovery")

            self.assertNotEqual(before_map, after_map, "map/ was not touched by the committed hunk")
            # +1 for hunk_one only -- +2 would mean the rejected hunk leaked in too
            self.assertEqual(after_count, before_count + 1,
                              "expected exactly hunk_one's new function reflected in the map "
                              "(before={b}, after={a})".format(b=before_count, a=after_count))
            # the rejected hunk's effect never lands in the commit
            committed_discovery = _git(["show", "HEAD:scripts/code_map/discovery.py"], wt).stdout
            self.assertNotIn("_e2e_marker_case5_hunk_two", committed_discovery)
            self.assertIn("_e2e_marker_case5_hunk_two", discovery.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Case 6 -- unrelated dirty file survives untouched
# ---------------------------------------------------------------------------

class UnrelatedDirtyFileSurvivesTests(unittest.TestCase):
    def test_case6_unrelated_unstaged_dirty_file_stays_dirty_and_out_of_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared, wt = _fresh_scratch_worktree(tmp, "wt-unrelated", testcase=self)
            self.assertEqual(_run_real_cli_install(wt).returncode, 0)

            discovery = wt / "scripts" / "code_map" / "discovery.py"
            render = wt / "scripts" / "code_map" / "render.py"
            _write(discovery, discovery.read_text(encoding="utf-8") + "\n\ndef _e2e_marker_case6():\n    return 1\n")
            _git(["add", "scripts/code_map/discovery.py"], wt)

            # unrelated dirty file, deliberately left unstaged and out of scope
            render_text_before = render.read_text(encoding="utf-8")
            _write(render, render_text_before + "\n\n# unrelated dirty edit, never staged\n")

            _git(["commit", "-q", "-m", "case6: stale-map commit with an unrelated dirty sibling"], wt)

            status_after = _status_porcelain(wt)
            self.assertIn("render.py", status_after)
            self.assertNotIn("scripts/code_map/render.py", _staged_names(wt))
            committed_render = _git(["show", "HEAD:scripts/code_map/render.py"], wt).stdout
            self.assertNotIn("unrelated dirty edit", committed_render)
            self.assertIn("unrelated dirty edit", render.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Case 7 -- second worktree off the same shared scratch .git
# ---------------------------------------------------------------------------

class SecondWorktreeSharesInstalledHookTests(unittest.TestCase):
    def test_case7_second_worktree_off_same_shared_git_fires_the_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shared = _make_shared_scratch_git(tmp)
            first = _worktree_add(shared, tmp / "wt-first", PINNED_SHA_PREFIX)
            _assert_pinned_head(self, first)
            _snapshot_gates_1_2_onto(first)
            baseline_sha = _git(["rev-parse", "HEAD"], first).stdout.strip()

            # install once, from the FIRST worktree only
            self.assertEqual(_run_real_cli_install(first).returncode, 0)
            self.assertTrue((_resolve_hooks_dir(first) / "pre-commit").is_file())

            # a second worktree off the SAME shared .git -- never a second clone
            second = _worktree_add(shared, tmp / "wt-second", baseline_sha)
            self.assertEqual(
                _resolve_hooks_dir(first).resolve(), _resolve_hooks_dir(second).resolve(),
                "first and second worktree must resolve to the SAME shared hooks directory")
            self.assertTrue((_resolve_hooks_dir(second) / "pre-commit").is_file(),
                             "the hook installed once from the first worktree must already be "
                             "visible from the second, before it ever commits anything itself")

            # commit for real from the SECOND worktree -- no install step run there
            _hand_edit_tracked_file(second, "case7")
            _git(["add", "scripts/code_map/discovery.py"], second)
            _git(["commit", "-q", "-m", "case7: commit from the second worktree"], second)

            stat = _git(["log", "-1", "--stat"], second).stdout
            self.assertIn("map/INDEX.md", stat, "the hook did not fire from the second worktree")

            freshness = _run_freshness_test(second)
            self.assertEqual(
                freshness.returncode, 0,
                "MapTreeFreshnessTests failed in the second worktree after its own hook-fired "
                "commit:\nSTDOUT:\n{o}\nSTDERR:\n{e}".format(o=freshness.stdout, e=freshness.stderr))

            # touches only the second worktree's own map/ tree -- the first
            # worktree's working copy (and its map/) is untouched by this commit
            self.assertEqual(_status_porcelain(first), "")


# ---------------------------------------------------------------------------
# Case 8 -- timing
# ---------------------------------------------------------------------------

class TimingTests(unittest.TestCase):
    def test_case8_timing_of_a_full_end_to_end_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            start = time.monotonic()

            shared, wt = _fresh_scratch_worktree(tmp, "wt-timing", testcase=self)
            self.assertEqual(_run_real_cli_install(wt).returncode, 0)
            _hand_edit_tracked_file(wt, "case8")
            _git(["add", "scripts/code_map/discovery.py"], wt)
            _git(["commit", "-q", "-m", "case8: timed end-to-end commit"], wt)

            elapsed = time.monotonic() - start

            stat = _git(["log", "-1", "--stat"], wt).stdout
            self.assertIn("map/INDEX.md", stat)
            print(
                "\ncase8 TIMING: worktree-materialization + real-CLI-install + hand-edit + "
                "commit = {elapsed:.2f}s (gate 1 reported 2.9s build-only / "
                "3.25-3.77s full mechanism, build/commit only -- this figure additionally "
                "includes cloning + worktree add + the real installer subprocess)".format(elapsed=elapsed)
            )


if __name__ == "__main__":
    unittest.main()
