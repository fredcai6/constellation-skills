"""g4 evidence, part 2: the SECOND level of grouping (subpackage headings)
on f1Brainz, to show the tier avoids one-giant-bucket even where a corpus
wraps everything under `src/` -- READ-ONLY, scratch out/artifacts only."""
import pathlib
import re
import subprocess
import sys
import tempfile

HOST = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("C:/Programs/f1Brainz")

with tempfile.TemporaryDirectory(prefix="g4-f1brainz-sub-") as tmp:
    scratch = pathlib.Path(tmp)
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build",
         "--root", str(ROOT),
         "--artifacts", str(scratch / "artifacts"),
         "--out", str(scratch / "map")],
        cwd=str(HOST), capture_output=True, text=True,
    )
    print("build exit:", proc.returncode)
    top = (scratch / "map" / "INDEX.md").read_text(encoding="utf-8")
    lines = top.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("## src") or ln.startswith("## tests") or ln.startswith("## scripts"):
            print(ln)
        if ln.startswith("### "):
            print(" ", ln)
    print("total lines in top index:", len(lines))
