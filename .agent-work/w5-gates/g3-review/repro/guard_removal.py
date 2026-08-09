"""Are the two NEW refusal legs load-bearing, or decorative? (g3-review re-verify.)

Removes the whitelist guard from the stub source IN THE TEST FILE, re-runs
-k archive_mutation, and reports which subtests fail. If the two new legs can
pass without the guard they are the no-op defect this gate exists to catch.

Restores the file byte-identically under finally, verified by sha256.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
TESTS = ROOT / "tests" / "test_iterative_planning_doctrine.py"

GUARD = """        if flag not in MODELLED_FLAGS:
            refuse("unmodelled flag: " + flag)
"""


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    p = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS), "-q", "-k", "archive_mutation"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    subtests = re.findall(r"\[text=([^\]]*)\]|SubTest.*", p.stdout)
    tail = [l for l in p.stdout.splitlines() if l.strip()][-1:]
    return p.returncode, (tail[0] if tail else ""), p.stdout


def main():
    original = TESTS.read_bytes()
    osha = sha(TESTS)
    text = original.decode("utf-8")
    guard = GUARD
    if guard not in text:                      # the file may be CRLF on this host
        guard = GUARD.replace("\n", "\r\n")
    if guard not in text:
        raise SystemExit("REFUSING: guard literal not found — this probe would be vacuous.")
    print("matched guard with %s line endings"
          % ("CRLF" if "\r\n" in guard else "LF"))
    print("baseline sha256:", osha)
    code, tail, _ = run()
    print("WITH guard      exit=%s  %s" % (code, tail))
    if code != 0:
        raise SystemExit("REFUSING: baseline not green.")
    try:
        TESTS.write_bytes(text.replace(guard, "").encode("utf-8"))
        assert sha(TESTS) != osha
        code, tail, out = run()
        print("WITHOUT guard   exit=%s  %s" % (code, tail))
        print("\n--- which subtests failed ---")
        for line in out.splitlines():
            if "SubTest" in line or "text=" in line or "AssertionError" in line:
                print("   ", line.strip()[:150])
    finally:
        TESTS.write_bytes(original)
        print("\nrestored sha256:", sha(TESTS),
              "IDENTICAL" if sha(TESTS) == osha else "*** MISMATCH ***")


if __name__ == "__main__":
    main()
