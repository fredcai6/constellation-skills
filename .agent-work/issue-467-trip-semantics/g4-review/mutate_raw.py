"""Re-run named mutations and DUMP every failure line verbatim, so the named-test
question is answered off pytest's own output rather than off a regex."""
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import mutate as MU  # reuses the same anchors

for name in sys.argv[1:]:
    spec = MU.M[name]
    text, crlf = MU.read()
    assert text.count(spec["old"]) == 1
    MU.write(text.replace(spec["old"], spec["new"], 1), crlf)
    assert not MU.clean()
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", MU.TESTFILE],
                       cwd=str(MU.ROOT), capture_output=True, text=True,
                       env={**os.environ, "NO_COLOR": "1", "FORCE_COLOR": ""})
    out = p.stdout + p.stderr
    MU.git("checkout", "--", "scripts/checklist_engine.py")
    print(f"\n########## {name}  (named test: {spec['named']})")
    print(f"reverted clean: {MU.clean()}")
    for line in out.splitlines():
        s = line.strip()
        if s.startswith(("FAILED", "SUBFAILED", "ERROR")) or " failed" in s or " passed" in s:
            print("   ", s[:190])
    print(f"    NAMED TEST APPEARS IN OUTPUT: {spec['named'] in out}")
