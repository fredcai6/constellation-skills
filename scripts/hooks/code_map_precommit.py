#!/usr/bin/env python3
"""scripts/hooks/code_map_precommit.py -- fail-open git pre-commit hook shim.

Installed as (or invoked from) `.git/hooks/pre-commit` (installer wiring is
gate 2's job, not this file's). Takes no CLI args. Resolves `repo_root`
dynamically via `git rev-parse --show-toplevel` from `cwd` at run time --
never a path baked in at install time -- so a hook shared across sibling
worktrees on different branches always imports and runs each worktree's own
copy of `scripts/code_map/precommit.py`, not whichever one happened to be
installed.

The whole body, including the dynamic resolve-and-import step, is wrapped in
one broad `try/except Exception` that always exits 0: a hang or a crash in
this shim must never block a commit any more than a crash does. `precommit.
main()` is already fail-open on its own for everything inside the mechanism;
this shim's own try/except exists for the layer `main()` cannot cover --
resolving which repo it is even running in, and importing that repo's own
copy of the module, which may not exist at all (a worktree checked out
before this feature shipped) or may fail to import for any other reason.
"""

import importlib
import subprocess
import sys
from pathlib import Path


def _resolve_repo_root(timeout=10):
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, timeout=timeout,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace") if isinstance(result.stderr, bytes) else result.stderr
        raise RuntimeError("git rev-parse --show-toplevel failed: {err}".format(err=(stderr or "").strip()))
    stdout = result.stdout.decode("utf-8", errors="replace") if isinstance(result.stdout, bytes) else result.stdout
    return Path(stdout.strip())


def _load_precommit_module(repo_root):
    """Import `<repo_root>/scripts/code_map/precommit.py` as
    `scripts.code_map.precommit`, resolved fresh from `repo_root` rather than
    from whatever `scripts.code_map` this process happens to already have on
    `sys.path` -- that is the whole point: each worktree's own copy, not a
    cached or coincidentally-shadowing one. Safe because a real git hook (and
    every test of this shim) runs as its own fresh process, so there is no
    prior import of the same dotted name to collide with."""
    precommit_path = repo_root / "scripts" / "code_map" / "precommit.py"
    if not precommit_path.is_file():
        raise ImportError("{path} does not exist in this worktree".format(path=precommit_path))
    sys.path.insert(0, str(repo_root))
    return importlib.import_module("scripts.code_map.precommit")


def main() -> int:
    try:
        repo_root = _resolve_repo_root()
        precommit = _load_precommit_module(repo_root)
        return precommit.main(repo_root)
    except Exception as exc:
        print("code-map-precommit: fail-open, swallowed: {exc!r}".format(exc=exc), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
