"""Reviewer g4 evidence: synthesize two corpus shapes the crew's cross-corpus
proof never tried, to stress the tier predicate `len(m.split("."))>=3`
directly and in isolation. Both are built fresh under a temp dir (never
touching f1Brainz/superCoolSpaceSim/this repo's tracked tree) and torn down
after. Run from the repo root:

    python .agent-work/issue-456/evidence/g4_reviewer_synth_corpora.py
"""
import pathlib
import subprocess
import sys
import tempfile

HOST = pathlib.Path(__file__).resolve().parents[3]  # repo root


def make_git_repo(root):
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=str(root), check=True)
    subprocess.run(["git", "config", "user.name", "a"], cwd=str(root), check=True)
    subprocess.run(["git", "add", "-A"], cwd=str(root), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "synthetic"], cwd=str(root), check=True)


def build(root, scratch):
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build",
         "--root", str(root),
         "--artifacts", str(scratch / "artifacts"),
         "--out", str(scratch / "map")],
        cwd=str(HOST), capture_output=True, text=True,
    )
    return proc, scratch / "map" / "INDEX.md"


def shape_flat_single_package(base):
    """Shape A: ONE top-level package, N modules, ZERO nesting -- every module
    is exactly two dotted segments (`flat.modNN`). This is not contrived: it
    is the default pytest layout (tests/test_*.py, one directory, no
    subpackages), and IS this repo's own `tests/` package shape."""
    root = base / "shape-a-flat-single-package"
    pkg = root / "flat"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for i in range(30):
        (pkg / f"mod{i:02d}.py").write_text(
            f'"""Module {i}."""\n\ndef fn_{i}():\n    """Do thing {i}."""\n    return {i}\n',
            encoding="utf-8")
    make_git_repo(root)
    return root


def shape_loose_top_level(base):
    """Shape B: NO packages at all -- every module is a single loose .py file
    directly at the repo root, one dotted segment each. Named explicitly in
    the handoff as a shape to try."""
    root = base / "shape-b-loose-top-level"
    root.mkdir(parents=True)
    for i in range(30):
        (root / f"mod{i:02d}.py").write_text(
            f'"""Loose module {i}."""\n\ndef fn_{i}():\n    """Do thing {i}."""\n    return {i}\n',
            encoding="utf-8")
    make_git_repo(root)
    return root


def main():
    with tempfile.TemporaryDirectory(prefix="g4-reviewer-synth-") as tmp:
        base = pathlib.Path(tmp)
        for name, maker in [
            ("A: flat single package (30 modules, no nesting)", shape_flat_single_package),
            ("B: loose top-level modules (30 files, no packages)", shape_loose_top_level),
        ]:
            print("=" * 70)
            print(name)
            root = maker(base)
            scratch = base / (root.name + "-scratch")
            proc, index_path = build(root, scratch)
            print("build exit:", proc.returncode)
            if proc.returncode != 0:
                print("STDERR:", proc.stderr[-2000:])
                continue
            text = index_path.read_text(encoding="utf-8")
            lines = text.splitlines()
            print(f"INDEX.md: {len(lines)} lines total")
            print("--- first 40 lines ---")
            for ln in lines[:40]:
                print(ln)
            n_h2 = sum(1 for ln in lines if ln.startswith("## "))
            n_h3 = sum(1 for ln in lines if ln.startswith("### "))
            n_bullets = sum(1 for ln in lines if ln.startswith("- ["))
            print(f"--- counts: ## headings={n_h2} ### headings={n_h3} bullet lines={n_bullets} ---")


if __name__ == "__main__":
    main()
