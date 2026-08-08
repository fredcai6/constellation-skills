"""Break the STORE derivation and run `check` against the REAL repository.

The mutation lives in a throwaway copy of scripts/code_map; the worktree's own
package is never touched. The real repo is read-only input to the build, which
writes its map into the copy's --root ... which IS the worktree, so the build
output goes to <worktree>/map -- the same tree a clean build produces, and it is
rebuilt clean immediately after.
"""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import attack  # noqa: E402

REPO = "C:/Programs/constellation-skills/.claude/worktrees/issue-456"

MUT = sys.argv[1] if len(sys.argv) > 1 else "D2_RESTORE"

with tempfile.TemporaryDirectory() as host, tempfile.TemporaryDirectory() as scratch:
    edits = {} if MUT == "NONE" else {"extract.py": getattr(attack, MUT)}
    h = attack.mutate(host, edits)
    art = str(pathlib.Path(scratch) / "artifacts")
    out = str(pathlib.Path(scratch) / "map")
    where = ("--root", REPO, "--artifacts", art, "--out", out)
    b = attack.run_map(h, "build", *where)
    print("BUILD", b.returncode)
    if b.returncode:
        print(b.stdout[-2000:], b.stderr[-2000:])
    c = attack.run_map(h, "check", *where)
    print("CHECK", c.returncode)
    print(c.stdout[-4000:])
