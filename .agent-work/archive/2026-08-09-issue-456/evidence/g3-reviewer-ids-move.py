"""ids.jsonl carries no position under a code MOVE, reviewer-authored (not the
implementer's mint-two-rename-one exercise -- this one MOVES a definition's
whole block to a different place in the file, which the implementer's own
exercise did not do)."""
import pathlib
import subprocess
import sys
import tempfile
import os

ROOT = pathlib.Path(__file__).resolve().parents[3]

BEFORE = '''"""A module carrying two authored anchors, before a move."""

WIDTH = 3


# [widget-spin]
def spin():
    """The first anchored definition."""
    return WIDTH


class Holder:
    """Holds the second anchored definition."""

    # [holder-hold]
    def hold(self):
        """An anchored method."""
        return 2


def filler_one():
    """Padding so the move below actually shifts line numbers."""
    return 10


def filler_two():
    """More padding."""
    return 11


def filler_three():
    """Even more padding."""
    return 12
'''

# `spin` MOVED from right after WIDTH to the bottom of the file, past three
# filler functions -- a genuine relocation, not a rename. Its anchor comment
# moves WITH it (the anchor binds to the next non-blank/non-comment line, so
# it must travel with the definition it names).
AFTER = '''"""A module carrying two authored anchors, after a move."""

WIDTH = 3


class Holder:
    """Holds the second anchored definition."""

    # [holder-hold]
    def hold(self):
        """An anchored method."""
        return 2


def filler_one():
    """Padding so the move below actually shifts line numbers."""
    return 10


def filler_two():
    """More padding."""
    return 11


def filler_three():
    """Even more padding."""
    return 12


# [widget-spin]
def spin():
    """The first anchored definition, now living 20 lines further down."""
    return WIDTH
'''


def make_repo(tmp, source):
    (tmp / "pkg3").mkdir(exist_ok=True)
    (tmp / "pkg3" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg3" / "anchors.py").write_text(source, encoding="utf-8", newline="\n")
    if not (tmp / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True)
    subprocess.run(["git", "add", "pkg3/__init__.py", "pkg3/anchors.py"],
                    cwd=str(tmp), check=True)


def build(tmp, artifacts, out):
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build", "--root", str(tmp),
         "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(ROOT), capture_output=True, text=True, env=env)


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="g3rev-move-"))

    make_repo(tmp, BEFORE)
    art_a, out_a = tmp / "art_a", tmp / "map_a"
    b1 = build(tmp, art_a, out_a)
    print("build BEFORE exit:", b1.returncode)
    ids_before = (out_a / "ids.jsonl").read_bytes()
    print("ids.jsonl BEFORE:\n" + ids_before.decode("utf-8"))

    import json
    with open(art_a / "statements.jsonl", encoding="utf-8") as f:
        for line in f:
            st = json.loads(line)
            if st["p"] == "contains" and st["o"] == "pkg3.anchors:spin":
                print(f"store line for spin BEFORE the move: {st['q']['line']}")

    make_repo(tmp, AFTER)
    art_b, out_b = tmp / "art_b", tmp / "map_b"
    b2 = build(tmp, art_b, out_b)
    print("\nbuild AFTER exit:", b2.returncode)
    ids_after = (out_b / "ids.jsonl").read_bytes()
    print("ids.jsonl AFTER:\n" + ids_after.decode("utf-8"))

    with open(art_b / "statements.jsonl", encoding="utf-8") as f:
        for line in f:
            st = json.loads(line)
            if st["p"] == "contains" and st["o"] == "pkg3.anchors:spin":
                print(f"store line for spin AFTER the move: {st['q']['line']}")

    print("\nids.jsonl BYTE-IDENTICAL before/after the move:", ids_before == ids_after)
    return 0 if ids_before == ids_after else 1


if __name__ == "__main__":
    sys.exit(main())
