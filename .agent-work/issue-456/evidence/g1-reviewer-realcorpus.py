"""Reviewer: build THIS repo into scratch and run `check` against it.

Never touches the committed map/ tree or .code-map/. Answers: does `check` exit 1
on this repository, and is it exit 1 for the RIGHT reason (the page-accounting
collision g2 owns) rather than for an unrelated one?
"""
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

env = dict(os.environ)
env.pop("FORCE_COLOR", None)
env.pop("PYTHONIOENCODING", None)

scratch = pathlib.Path(tempfile.mkdtemp(prefix="g1rev-real-"))
art, out = scratch / "artifacts", scratch / "map"

b = subprocess.run([sys.executable, "-m", "scripts.code_map", "build",
                    "--root", str(ROOT), "--artifacts", str(art), "--out", str(out)],
                   cwd=str(ROOT), capture_output=True, text=True, env=env)
print(f"BUILD exit={b.returncode}")
if b.returncode != 0:
    print(b.stderr[-2000:])
    raise SystemExit(2)

c = subprocess.run([sys.executable, "-m", "scripts.code_map", "check",
                    "--root", str(ROOT), "--artifacts", str(art), "--out", str(out)],
                   cwd=str(ROOT), capture_output=True, text=True, env=env)
print(f"CHECK exit={c.returncode}")
print(c.stdout)
if c.stderr.strip():
    print("STDERR:", c.stderr[-1000:])

# Independent measurement of the numbers, not read off the render report.
from scripts.code_map import checks  # noqa: E402

m = checks.MapUnderCheck(ROOT, art, out)
print(f"modules={len(m.modules)} entities={len(m.entities)} pages={len(m.pages)}")
print(f"pages - 1 - modules = {len(m.pages) - 1 - len(m.modules)}   "
      f"entity_pages(by title) = {len(m.entity_pages)}")

groups = {}
for key in m.entities:
    mod, name = key.split(":", 1)
    groups.setdefault((mod, name.lower()), []).append(key)
ci = sorted(tuple(sorted(v)) for v in groups.values() if len(v) > 1)
paths = {}
for key in m.entities:
    mod, name = key.split(":", 1)
    paths.setdefault(f"{mod}/{name}.md", []).append(key)
cs = sorted(tuple(sorted(v)) for v in paths.values() if len(v) > 1)
print(f"case-INSENSITIVE collisions: {len(ci)} {ci}")
print(f"case-SENSITIVE   collisions: {len(cs)} {cs}")
print(f"page_accounting failures: {checks.page_accounting(m)}")
