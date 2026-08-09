"""Reviewer g4 attack on tc31's check (`checks.page_location_matches_content`),
using relocations the implementer did NOT choose (their RED evidence moved an
ENTITY page `pkg.callee:target.md` cross-module, `pkg.callee/` -> `pkg.far/`).

Attack 1: relocate a MODULE's own INDEX.md page into a sibling module's
directory (a module-page mislocation, not an entity-page one).

Attack 2: relocate an ENTITY page into a SUBDIRECTORY of its OWN correct
module (same module, wrong parent -- not a cross-module move at all).

Both mutate a throwaway scratch build (this repo, --root/--artifacts/--out
all under a temp dir); nothing tracked is touched.

    python .agent-work/issue-456/evidence/g4_reviewer_tc31_attack.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

HOST = pathlib.Path(__file__).resolve().parents[3]


def run_check(root, artifacts, out):
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "check",
         "--root", str(root), "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(HOST), capture_output=True, text=True)
    return proc


def run_build(root, artifacts, out):
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build",
         "--root", str(root), "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(HOST), capture_output=True, text=True)
    return proc


def main():
    with tempfile.TemporaryDirectory(prefix="g4-reviewer-tc31-") as tmp:
        scratch = pathlib.Path(tmp)
        artifacts = scratch / "artifacts"
        out = scratch / "map"
        b = run_build(HOST, artifacts, out)
        print("build exit:", b.returncode)
        assert b.returncode == 0, b.stderr

        c0 = run_check(HOST, artifacts, out)
        print("BASELINE check exit:", c0.returncode)
        print(c0.stdout)
        assert c0.returncode == 0

        # ---- Attack 1: MODULE page relocated into a sibling module's dir ----
        src_mod_dir = out / "scripts.code_map.discovery"
        dst_mod_dir = out / "scripts.code_map.cli"
        assert (src_mod_dir / "INDEX.md").exists()
        assert dst_mod_dir.exists()
        moved_path = dst_mod_dir / "discovery-relocated-INDEX.md"
        shutil.move(str(src_mod_dir / "INDEX.md"), str(moved_path))
        print("=" * 70)
        print("ATTACK 1: moved scripts.code_map.discovery/INDEX.md ->",
              moved_path.relative_to(out))
        c1 = run_check(HOST, artifacts, out)
        print("check exit:", c1.returncode)
        print(c1.stdout)
        # restore for attack 2's clean baseline
        shutil.move(str(moved_path), str(src_mod_dir / "INDEX.md"))

        # ---- Attack 2: ENTITY page relocated into a SUBDIR of its OWN module ----
        mod_dir = out / "scripts.code_map.discovery"
        entity_pages = [p for p in mod_dir.glob("*.md") if p.name != "INDEX.md"]
        assert entity_pages, "no entity page found under scripts.code_map.discovery"
        victim = entity_pages[0]
        subdir = mod_dir / "nested"
        subdir.mkdir()
        moved2 = subdir / victim.name
        shutil.move(str(victim), str(moved2))
        print("=" * 70)
        print("ATTACK 2: moved", victim.relative_to(out), "->", moved2.relative_to(out),
              "(same module, wrong parent dir)")
        c2 = run_check(HOST, artifacts, out)
        print("check exit:", c2.returncode)
        print(c2.stdout)


if __name__ == "__main__":
    main()
