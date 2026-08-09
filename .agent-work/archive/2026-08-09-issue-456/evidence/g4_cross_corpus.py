"""g4 evidence: prove the top-index second tier is DERIVED, not TUNED, by
running the real pipeline against three corpora of very different shape.

READ-ONLY on the two external repos: --root points at them, --artifacts/--out
point at a scratch directory under THIS repo's own work area. Nothing is
written into f1Brainz or superCoolSpaceSim. Run from the repo root:

    python .agent-work/issue-456/evidence/g4_cross_corpus.py
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HOST = pathlib.Path(__file__).resolve().parents[3]  # repo root
CORPORA = [
    ("constellation-skills", HOST),
    ("f1Brainz", pathlib.Path("C:/Programs/f1Brainz")),
    ("superCoolSpaceSim", pathlib.Path("C:/Programs/superCoolSpaceSim")),
]


def git_status(root):
    out = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                         capture_output=True, text=True, check=True)
    return out.stdout


def build(root, scratch):
    env = {"PATH": __import__("os").environ.get("PATH", "")}
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build",
         "--root", str(root),
         "--artifacts", str(scratch / "artifacts"),
         "--out", str(scratch / "map")],
        cwd=str(HOST), capture_output=True, text=True,
    )
    return proc


def main():
    for name, root in CORPORA:
        print("=" * 70)
        print(name, "--", root)
        before = git_status(root)
        with tempfile.TemporaryDirectory(prefix=f"g4-{name}-") as tmp:
            scratch = pathlib.Path(tmp)
            proc = build(root, scratch)
            print("build exit:", proc.returncode)
            if proc.returncode != 0:
                print("STDERR TAIL:", proc.stderr[-1500:])
                after = git_status(root)
                print("git status unchanged:", after == before)
                continue
            report = json.loads(proc.stdout.strip().splitlines()[-1] if False else
                                (scratch / "artifacts" / "render_report.json").read_text())
            print("report:", json.dumps(report, indent=1))
            top = (scratch / "map" / "INDEX.md").read_text(encoding="utf-8")
            lines = top.splitlines()
            try:
                overview_at = lines.index("## packages")
                overview = []
                for ln in lines[overview_at + 1:]:
                    if not ln.strip():
                        break
                    overview.append(ln)
            except ValueError:
                overview = None
            print("package overview:")
            if overview:
                for ln in overview:
                    print(" ", ln)
            else:
                print(" ", lines[2] if len(lines) > 2 else "(no modules)")
        after = git_status(root)
        print("git status unchanged after build:", after == before)
        if after != before:
            print("WARNING: git status changed!\nbefore:", before, "\nafter:", after)


if __name__ == "__main__":
    main()
