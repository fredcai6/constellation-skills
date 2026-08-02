"""g4 m2 check: the context gate REPORTED degraded and was then discharged HONESTLY.

Asserts, against the scratch spine the engine actually drove:

1. the ``context`` task reached ``complete``;
2. the orientation receipt records a DEGRADED verdict carrying hash-pinned substitutes,
   a named unmapped gap AND an escalation (the three things the contract owes);
3. the discharge used no ``waive`` and no ``--force`` -- the spine journal carries neither
   verb, so the gate was passed on its own terms rather than around them;
4. re-running the materialized check now exits 0.

A gate that can only be passed with a waiver would be worse than the silence it replaced;
this check is what makes that claim falsifiable rather than asserted.
"""

import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK_ID = "g4-scratch-run"
AREA = ROOT / ".agent-work" / WORK_ID
SPINE = AREA / "spine.json"
RECEIPT = AREA / "map-orientation.json"

problems = []

spine = json.loads(io.open(SPINE, encoding="utf-8").read())
ctx_status = spine["tasks"]["context"]["status"]
print("context task status: %s" % ctx_status)
if ctx_status != "complete":
    problems.append("context did not reach complete (got %r)" % ctx_status)

def receipt_is_degraded(receipt: dict) -> bool:
    """Read the receipt's STRUCTURED verdict field, never the document as a string.

    This assertion was originally ``"DEGRADED" in json.dumps(receipt).upper()``, which
    the g4 reviewer showed is satisfied by the agent's OWN escalation prose
    ("...structurally degraded until a map exists") and so evaluates True even on a
    ``mode: RESOLVED`` receipt -- a check that cannot fail, the #300 class, inside the
    very gate whose job was to prove that checks fire. ``build_receipt`` writes the
    verdict to ``mode``; that field, and only that field, is the oracle.
    ``g4_assert_harness_discriminates.py`` pins the discrimination.
    """
    return str(receipt.get("mode", "")).upper().startswith("DEGRADED")


receipt = json.loads(io.open(RECEIPT, encoding="utf-8").read())
verdict = receipt.get("mode") or ""
degraded = receipt_is_degraded(receipt)
subs = receipt.get("substitutes") or []
print("receipt degraded: %s   substitutes: %d   unmapped: %d   escalation: %s"
      % (degraded, len(subs), len(receipt.get("unmapped") or []),
         bool(receipt.get("escalation"))))
if not degraded:
    problems.append("receipt does not record a degraded verdict (%r)" % verdict)
if not subs:
    problems.append("receipt declares no substitutes")
for s in subs:
    if not s.get("content_hash"):
        problems.append("substitute %r is not hash-pinned" % s.get("path"))
    print("  substitute %s hash=%s source=%s"
          % (s.get("path"), (s.get("content_hash") or "")[:16], s.get("source")))
if not (receipt.get("unmapped") or []):
    problems.append("receipt names no unmapped gap")
if not receipt.get("escalation"):
    problems.append("receipt carries no escalation")

journal = io.open(SPINE.with_suffix(".json.journal"), encoding="utf-8").read()
verbs = sorted({json.loads(l)["verb"] for l in journal.splitlines() if l.strip()})
print("spine journal verbs: %s" % verbs)
if "waive" in verbs:
    problems.append("the gate was passed with a waive")
if '"force": true' in journal.lower() or "--force" in journal:
    problems.append("the gate was passed with --force")

proc = subprocess.run(
    [sys.executable, "scripts/map_orient.py", "verify-orientation",
     "--root", ROOT.as_posix(), "--work-id", WORK_ID],
    cwd=str(ROOT), capture_output=True, text=True,
)
print("verify-orientation re-run exit: %d" % proc.returncode)
if proc.returncode != 0:
    problems.append("verify-orientation now exits %d, not 0" % proc.returncode)

if problems:
    for p in problems:
        print("FAIL: %s" % p)
    sys.exit(1)
print("DEGRADED-REPORTED-AND-DISCHARGED-WITHOUT-FORCE-OR-WAIVER")
