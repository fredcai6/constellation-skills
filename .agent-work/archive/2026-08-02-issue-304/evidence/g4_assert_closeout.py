"""g4 m4 check: the scratch work area is GONE, the prior gates' artifacts are untouched,
and the result file exists.

Only a cleanup that has been verified may be claimed, so this asserts absence at the
filesystem rather than trusting the rm. Prior-gate artifacts are compared by git **blob
OID**, never raw bytes -- on Windows a CRLF working copy shows a phantom ``M`` in
``git status --porcelain`` while the content is byte-identical to HEAD.
"""

import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".agent-work" / "g4-scratch-run"
RESULT = ROOT / ".agent-work" / "issue-304" / "crew-handoffs" / "g4-result.md"

# HEAD as it stood before any g4 commit, and the TRIPWIRES.md pre-registration commit.
PRE_G4 = "4f9c6d1"
PREREG = "1662b90"

# Prior-gate artifacts that must be byte-identical to the pre-g4 tree. execute.json and
# crew-runs.json are deliberately EXCLUDED: the Commander mutated both in its own working
# tree before this crew started (registering this dispatch, starting the g4 gate), and g4
# swept those pre-existing changes into its m2 commit -- named as a deviation in the
# result rather than hidden here.
FROZEN = [
    ".agent-work/issue-304/TRIPWIRE_OUTCOMES.md",
    ".agent-work/issue-304/TREND_SNAPSHOT.md",
    ".agent-work/issue-304/crew-handoffs/g3-result.md",
    ".agent-work/issue-304/evidence/g3-run-transcript.txt",
    ".agent-work/issue-304/g3-implementer-plan.json",
    ".agent-work/issue-304/spine.json",
    "TRIPWIRES.md",
]

problems = []


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=str(ROOT),
                          capture_output=True, text=True).stdout.strip()


print("scratch work area %s exists: %s" % (SCRATCH, SCRATCH.exists()))
if SCRATCH.exists():
    problems.append("scratch work area %s still exists" % SCRATCH)

for rel in FROZEN:
    before = git("rev-parse", "%s:%s" % (PRE_G4, rel))
    now = git("hash-object", rel)
    same = bool(before) and before == now
    print("%-58s %s  %s" % (rel, before[:12] or "(missing)", "UNCHANGED" if same else "CHANGED"))
    if not same:
        problems.append("%s changed since %s (%s -> %s)" % (rel, PRE_G4, before[:12], now[:12]))

# TRIPWIRES.md is a pre-registration: it must also be identical to the commit that
# registered it, not merely to yesterday's HEAD.
prereg_oid = git("rev-parse", "%s:TRIPWIRES.md" % PREREG)
now_oid = git("hash-object", "TRIPWIRES.md")
print("TRIPWIRES.md vs pre-registration %s: %s" % (PREREG, "IDENTICAL" if prereg_oid == now_oid else "REWRITTEN"))
if prereg_oid != now_oid:
    problems.append("TRIPWIRES.md is not byte-identical to its pre-registration commit")

print("result file %s exists: %s" % (RESULT.name, RESULT.is_file()))
if not RESULT.is_file():
    problems.append("no IMPLEMENTER_RESULT at %s" % RESULT)
else:
    text = io.open(RESULT, encoding="utf-8").read()
    if len(text) < 2000:
        problems.append("result file is implausibly short (%d chars)" % len(text))

if problems:
    for p in problems:
        print("FAIL: %s" % p)
    sys.exit(1)
print("CLEANUP-VERIFIED-PRIOR-GATES-UNTOUCHED-RESULT-WRITTEN")
