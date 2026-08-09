"""g1 undesigned-attack harness -- evidence only, not part of the suite.

For each attack it builds a map through a COPY of scripts/code_map (mutated or
not), optionally damages the built artifact, runs `check`, and records the exit
code and which named checks went red. Nothing in the shipped tree is touched.

Run:  python .agent-work/issue-456/evidence/g1_attack_harness.py
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
CODE_MAP = ROOT / "scripts" / "code_map"

WIDGET = '''"""The module other modules point at."""


class Widget:
    """A widget."""

    def spin(self):
        """Spin it."""
        return 1


def helper():
    """Make one."""
    return Widget()
'''

USER = '''"""A module that uses Widget across the module boundary."""
import collections
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap
from pkg.widget import Widget, helper


def use():
    """Call helper twice, then hand Widget itself back."""
    helper()
    helper()
    return Widget


def gather():
    """Name every import, so the extractor records each one."""
    return (collections, json, os, pathlib, re, subprocess, sys, textwrap)
'''

OTHER = '''"""A second module with an entity whose name repeats elsewhere."""


def helper():
    """Same leaf name as pkg.widget:helper -- flattening the tree collides."""
    return 3
'''


def make_repo(tmp):
    tmp = pathlib.Path(tmp)
    (tmp / "pkg").mkdir(parents=True)
    for rel, text in (("pkg/__init__.py", ""), ("pkg/widget.py", WIDGET),
                      ("pkg/user.py", USER), ("pkg/other.py", OTHER)):
        (tmp / rel).write_text(text, encoding="utf-8", newline="\n")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True,
                   capture_output=True, text=True)
    subprocess.run(["git", "add", "pkg/__init__.py", "pkg/widget.py",
                    "pkg/user.py", "pkg/other.py"],
                   cwd=str(tmp), check=True, capture_output=True, text=True)
    return tmp


def package(tmp, module=None, subs=()):
    dest = pathlib.Path(tmp) / "scripts" / "code_map"
    shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
    if module:
        original = (CODE_MAP / module).read_text(encoding="utf-8")
        text = original
        for old, new in subs:
            if original.count(old) != 1:
                raise SystemExit(f"HARNESS ERROR: anchor x{original.count(old)} in "
                                 f"{module}: {old!r}")
            text = text.replace(old, new, 1)
        (dest / module).write_text(text, encoding="utf-8", newline="\n")
    return pathlib.Path(tmp)


def run(host, repo, *args):
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run([sys.executable, "-m", "scripts.code_map", *args,
                           "--root", str(repo)],
                          cwd=str(host), capture_output=True, text=True, env=env)


def failed_checks(stdout):
    return [ln.split(":")[0][len("FAIL "):]
            for ln in stdout.splitlines() if ln.startswith("FAIL ")]


# ---------------------------------------------------------------- mutations

DROP_MODULE_INDEX = ("render.py", (
    ('        (d / "INDEX.md").write_text(module_index(mod), encoding="utf-8", newline="\\n")\n',
     '        pass  # ATTACK: module index never written\n'),))

FLAT_TREE = ("render.py", (
    ('            (d / (key.split(":", 1)[1] + ".md")).write_text(\n',
     '            (out / (key.split(":", 1)[1] + ".md")).write_text(\n'),))

REVERSED_CALLERS = ("render.py", (
    ("    ext = sorted(m for m in callers if m != mod)\n",
     "    ext = sorted((m for m in callers if m != mod), reverse=True)\n"),))

UNSORTED_CALLERS = ("render.py", (
    ("    ext = sorted(m for m in callers if m != mod)\n",
     "    ext = list(m for m in callers if m != mod)\n"),))

TIMESTAMP_IN_A_PAGE = ("render.py", (
    ('    L = [f"# {title} map", ""]\n',
     '    L = [f"# {title} map", f"built at {__import__(\'time\').time()}", ""]\n'),))

EXTRACTOR_DROPS_READS = ("extract.py", (
    ("    def _ref(self, node, pred):\n        s, r, w = self.resolve_expr(node)\n",
     '    def _ref(self, node, pred):\n        if pred == "reads":\n'
     "            return\n        s, r, w = self.resolve_expr(node)\n"),))


# ------------------------------------------------------- artifact damage

def delete_a_page(repo):
    (repo / "map" / "pkg.widget" / "helper.md").unlink()
    return "deleted map/pkg.widget/helper.md"


def swap_two_pages(repo):
    a = repo / "map" / "pkg.widget" / "helper.md"
    b = repo / "map" / "pkg.widget" / "Widget.md"
    at, bt = a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")
    a.write_text(bt, encoding="utf-8", newline="\n")
    b.write_text(at, encoding="utf-8", newline="\n")
    return "swapped the CONTENTS of helper.md and Widget.md (paths now lie)"


def stray_page(repo):
    (repo / "map" / "stray.md").write_text("# stray\n", encoding="utf-8", newline="\n")
    return "added map/stray.md, a page the store never asked for"


def empty_a_page(repo):
    (repo / "map" / "pkg.widget" / "Widget.md").write_text(
        "", encoding="utf-8", newline="\n")
    return "truncated map/pkg.widget/Widget.md to zero bytes"


def rename_a_page(repo):
    d = repo / "map" / "pkg.widget"
    (d / "helper.md").rename(d / "Helper.md")
    return "renamed helper.md -> Helper.md (title unchanged)"


ATTACKS = [
    ("delete-a-page", None, delete_a_page),
    ("swap-two-pages", None, swap_two_pages),
    ("stray-extra-page", None, stray_page),
    ("empty-a-page", None, empty_a_page),
    ("rename-a-page-file", None, rename_a_page),
    ("drop-every-module-index", DROP_MODULE_INDEX, None),
    ("flat-page-tree", FLAT_TREE, None),
    ("reversed-caller-list", REVERSED_CALLERS, None),
    ("unsorted-caller-list", UNSORTED_CALLERS, None),
    ("timestamp-on-a-page", TIMESTAMP_IN_A_PAGE, None),
    ("extractor-never-records-reads", EXTRACTOR_DROPS_READS, None),
]

ALL_CHECKS = ["no-empty-pages", "page-accounting", "refs-line-self-consistent",
              "entity-symbol-join", "inbound-attribution", "deterministic-rebuild"]


def main():
    scratch = tempfile.mkdtemp(prefix="g1-attacks-")
    try:
        # positive control first: an unmutated copy over an undamaged map
        repo = make_repo(pathlib.Path(scratch) / "control-repo")
        host = package(pathlib.Path(scratch) / "control-host")
        assert run(host, repo, "build").returncode == 0, "control build failed"
        proc = run(host, repo, "check")
        print(f"CONTROL  unmutated copy, undamaged map -> exit {proc.returncode}, "
              f"failed={failed_checks(proc.stdout) or 'none'}")
        if proc.returncode != 0:
            print(proc.stdout)
            raise SystemExit("HARNESS ERROR: the control is not green; nothing below "
                             "is evidence")
        print()

        for i, (name, mutation, damage) in enumerate(ATTACKS):
            repo = make_repo(pathlib.Path(scratch) / f"repo-{i}")
            module, subs = mutation if mutation else (None, ())
            host = package(pathlib.Path(scratch) / f"host-{i}", module, subs)
            built = run(host, repo, "build")
            if built.returncode != 0:
                print(f"{name}: BUILD FAILED\n{built.stderr[-800:]}")
                continue
            note = damage(repo) if damage else f"mutated {module}"
            proc = run(host, repo, "check")
            caught = failed_checks(proc.stdout)
            survived = [c for c in ALL_CHECKS if c not in caught]
            print(f"ATTACK   {name}")
            print(f"  what     {note}")
            print(f"  exit     {proc.returncode}")
            print(f"  caught   {', '.join(caught) if caught else 'NOTHING -- SURVIVOR'}")
            print(f"  survived {', '.join(survived)}")
            print()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
