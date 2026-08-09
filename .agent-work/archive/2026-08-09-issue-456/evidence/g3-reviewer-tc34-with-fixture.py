"""tc34 direct verification, reviewer's OWN fixture (not the implementer's
`_make_schema_repo`). A definition inside a `with` block, built and checked
through the real CLI end to end, confirming: (1) the store has a `contains`
statement for it, (2) a page exists and is linked from its module index, (3)
`check` passes with entity-symbol-join seeing it too (coverage arm)."""
import json
import pathlib
import subprocess
import sys
import tempfile
import os

ROOT = pathlib.Path(__file__).resolve().parents[3]

SOURCE = '''"""A module whose only definition lives inside compound statements."""

import contextlib


with contextlib.suppress(Exception):
    def reviewer_with_block_definition():
        """Defined inside a with block -- the old stage's blind spot."""
        return 1


if True:
    def reviewer_if_block_definition():
        """Defined inside an if block."""
        return 2
'''


def make_repo(tmp):
    (tmp / "pkg2").mkdir()
    (tmp / "pkg2" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg2" / "blocks.py").write_text(SOURCE, encoding="utf-8", newline="\n")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True)
    subprocess.run(["git", "add", "pkg2/__init__.py", "pkg2/blocks.py"],
                    cwd=str(tmp), check=True)


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="g3rev-with-"))
    make_repo(tmp)
    artifacts = tmp / ".code-map"
    out = tmp / "map"
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    b = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build", "--root", str(tmp),
         "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(ROOT), capture_output=True, text=True, env=env)
    print("build exit:", b.returncode)
    if b.returncode != 0:
        print(b.stdout, b.stderr)
        return 1

    with open(artifacts / "statements.jsonl", encoding="utf-8") as f:
        contains = [json.loads(l) for l in f if json.loads(l)["p"] == "contains"]
    syms = {c["o"] for c in contains}
    print("store contains symbols:", sorted(s for s in syms if "pkg2" in s))
    for target in ("pkg2.blocks:reviewer_with_block_definition",
                    "pkg2.blocks:reviewer_if_block_definition"):
        print(f"  {target} in store: {target in syms}")
        page = out / "pkg2.blocks" / (target.split(":", 1)[1] + ".md")
        print(f"  {target} page exists: {page.exists()} ({page})")
        index = (out / "pkg2.blocks" / "INDEX.md").read_text(encoding="utf-8")
        leaf = target.split(":", 1)[1]
        print(f"  {target} linked from module index: {leaf + '.md' in index}")

    c = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "check", "--root", str(tmp),
         "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(ROOT), capture_output=True, text=True, env=env)
    print("\ncheck exit:", c.returncode)
    print(c.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
