"""scripts/code_map/precommit.py -- the index-snapshot pre-commit mechanism.

Owns the mechanism end to end: snapshot the git INDEX (never the working
tree) into a throwaway worktree, `build()` the map there, copy the two
managed files back into the real repo with plain file I/O, and stage exactly
the paths that changed. `scripts/hooks/code_map_precommit.py` is a thin shim
around `main()` below -- it resolves `repo_root` dynamically per invocation
and dynamically imports THIS module from that resolved root (so a hook
shared across sibling worktrees on different branches always runs each
worktree's own copy), then calls `main()`, which is already fail-open on its
own.

Snapshotting the index rather than the working tree is what makes this
correct on every commit shape: a `git commit -m` with nothing else staged, a
pathspec-restricted `git add <one-file>`, or a hunk-restricted `git add -p`
all leave the *working tree* holding content that is not what is about to be
committed. `extract.py` reads file bodies straight off disk
(`os.path.join(root, rel)`), so running `build()` against the real working
tree would bake in whatever is sitting there, staged or not. Materializing
`git write-tree`'s result as a real worktree makes "what is about to be
committed" a real, buildable directory instead of something only git's
plumbing understands.

Every git call takes an injectable `runner` (default `subprocess.run`) so a
test can substitute a recording or a raising/sleeping fake without a real git
binary in play for the fail-open/timeout paths. There is no bare
module-level `subprocess.run` call anywhere in this file.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# The two files this mechanism ever reads, builds, or stages -- naming them
# once here is what makes "never any other path" true by construction: no
# function in this module accepts or derives a third path.
MANAGED_PATHS = ("map/INDEX.md", "map/ids.jsonl")

_TIMEOUT = 10


class PrecommitError(Exception):
    """Any mechanism-level failure -- caught by `main`'s fail-open wrapper."""


def _run(runner, args, cwd):
    """Every git call in this module goes through here: fixed `timeout=10`,
    bytes (never text-mode) so a copy-back comparison never has to round-trip
    through a text codec, and `cwd` always the real repo (the ephemeral
    worktree is a `git` positional argument, never a `cwd` switch)."""
    return runner(list(args), cwd=str(cwd), capture_output=True, timeout=_TIMEOUT)


def _check(result, args):
    if result.returncode != 0:
        stderr = result.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        raise PrecommitError("{cmd} failed: {err}".format(cmd=" ".join(args), err=(stderr or "").strip()))
    return result


def _read_staged_blob(runner, repo_root, rel):
    """The bytes `rel` holds in the index right now, or `b""` if it is not in
    the index at all (a brand-new managed file on the very first build)."""
    result = _run(runner, ["git", "show", ":{rel}".format(rel=rel)], repo_root)
    if result.returncode != 0:
        return b""
    return result.stdout


def run_precommit(repo_root, *, runner=subprocess.run):
    """Run the index-snapshot mechanism against `repo_root`. Returns
    `{"staged": [<managed paths that changed>]}` -- an empty list on the
    fresh/no-op path. Raises `PrecommitError`, or lets a `runner` exception
    (e.g. `subprocess.TimeoutExpired`) propagate, on any failure; `main`
    below is what turns that into a fail-open exit.
    """
    repo_root = Path(repo_root)

    # Step 1: self-heal admin residue from any prior crashed run. Best
    # effort -- a prune failure here must not block the mechanism it is only
    # trying to tidy up after.
    try:
        _run(runner, ["git", "worktree", "prune"], repo_root)
    except Exception:
        pass

    worktree_path = None
    try:
        # Step 2: snapshot the INDEX, never the working tree. A unique
        # `tempfile.mkdtemp` target every call is what makes two concurrent
        # invocations collision-free -- each gets a distinct worktree-admin
        # entry, and `git worktree add` with distinct target paths does not
        # collide even under concurrent load.
        tree = _check(_run(runner, ["git", "write-tree"], repo_root), ["git", "write-tree"]).stdout
        tree = tree.decode("ascii").strip() if isinstance(tree, bytes) else str(tree).strip()

        commit_args = ["git", "commit-tree", tree, "-p", "HEAD", "-m", "code-map-precommit: index snapshot"]
        commit = _check(_run(runner, commit_args, repo_root), commit_args).stdout
        commit = commit.decode("ascii").strip() if isinstance(commit, bytes) else str(commit).strip()

        worktree_path = tempfile.mkdtemp(prefix="code-map-precommit-")
        add_args = ["git", "worktree", "add", "--detach", worktree_path, commit]
        _check(_run(runner, add_args, repo_root), add_args)

        # Step 3: build() against the ephemeral worktree -- an in-process
        # call, not a subprocess, so no separate timeout site applies here.
        from .build import build
        status = build(worktree_path)
        if status:
            raise PrecommitError("build() against {path} exited {status}".format(path=worktree_path, status=status))

        # Step 4: plain file I/O copy-back, diffed against the staged blobs
        # (never the real working tree's current content on disk).
        staged = []
        for rel in MANAGED_PATHS:
            built_path = Path(worktree_path) / rel
            built_bytes = built_path.read_bytes() if built_path.exists() else b""
            current_bytes = _read_staged_blob(runner, repo_root, rel)
            if built_bytes != current_bytes:
                real_path = repo_root / rel
                real_path.parent.mkdir(parents=True, exist_ok=True)
                real_path.write_bytes(built_bytes)
                staged.append(rel)

        # Step 5: stage only the paths that actually changed -- never a
        # directory or glob add, so no other path can ever be swept in.
        if staged:
            _check(_run(runner, ["git", "add", "--"] + staged, repo_root), ["git", "add"])

        return {"staged": staged}
    finally:
        # Step 6: always remove the ephemeral worktree, even on the
        # fail-open path -- a cleanup failure is itself swallowed and
        # logged, never allowed to propagate or mask the real outcome.
        if worktree_path is not None:
            try:
                _run(runner, ["git", "worktree", "remove", "--force", worktree_path], repo_root)
            except Exception as exc:
                print(
                    "code-map-precommit: cleanup failed for {path}: {exc!r}".format(path=worktree_path, exc=exc),
                    file=sys.stderr,
                )


def main(repo_root, *, runner=subprocess.run) -> int:
    """The fail-open entry point `scripts/hooks/code_map_precommit.py` calls
    once it has resolved `repo_root` and imported this module. Always
    returns 0. Prints nothing on the no-op path, one line naming the staged
    paths on the fixed-staleness path, and one diagnostic line naming what
    was swallowed on any exception (including a `subprocess.TimeoutExpired`
    from a hung git call) -- the shim's own stderr is what a normal
    `git commit` shows without failing it, so this costs zero UX.
    """
    try:
        result = run_precommit(repo_root, runner=runner)
        staged = result.get("staged") or []
        if staged:
            print("code-map-precommit: staged {paths}".format(paths=", ".join(staged)), file=sys.stderr)
        return 0
    except Exception as exc:
        print("code-map-precommit: fail-open, swallowed: {exc!r}".format(exc=exc), file=sys.stderr)
        return 0
