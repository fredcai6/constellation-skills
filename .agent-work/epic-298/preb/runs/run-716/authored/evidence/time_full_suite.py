"""Size the constellation-skills full suite, so the plan's closing check is scoped honestly."""
import subprocess, time

PY = r"C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe"
ROOT = r"C:\Programs\constellation-skills"

t0 = time.time()
r = subprocess.run([PY, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
print((r.stdout or "").strip()[-1200:])
print((r.stderr or "").strip()[-400:])
print(f"exit={r.returncode} wall={time.time() - t0:.1f}s")
