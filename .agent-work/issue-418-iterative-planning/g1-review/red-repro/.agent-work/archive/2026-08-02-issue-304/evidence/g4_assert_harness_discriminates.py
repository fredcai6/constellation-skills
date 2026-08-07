"""g4 m5 check: the corrected harness predicate can actually FAIL.

The g4 reviewer found a real weakness inside g4's own evidence harness:
``g4_assert_discharged.py`` asserted the degraded verdict with
``"DEGRADED" in json.dumps(receipt).upper()``, a substring scan over the whole
document -- satisfied by the agent's own escalation prose ("...structurally degraded
until a map exists") while the structured verdict was fetched and discarded. It
therefore returned True on a ``mode: RESOLVED`` receipt: a check that cannot fail, the
#300 class, inside the very gate whose job was to prove that checks fire.

This pins the repair by exhibiting the discriminator the old predicate lacked. It loads
the CORRECTED ``receipt_is_degraded`` out of ``g4_assert_discharged.py`` **by source**
(the module's top level reads a scratch spine that no longer exists, so it cannot simply
be imported) and asserts, over the reviewer's own adversarial receipt:

- the OLD substring predicate accepts a RESOLVED receipt   -- the defect, reproduced;
- the NEW structured predicate REJECTS it                  -- the repair;
- the NEW predicate still accepts a genuine DEGRADED receipt -- no over-correction.

A repair that only ever returns the answer we want would be the same defect wearing a
fix's clothes, so all three directions are asserted, not just the middle one.
"""

import ast
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "g4_assert_discharged.py"

# The reviewer's adversarial case: a RESOLVED receipt whose ESCALATION PROSE -- written
# by the agent, not by the tool -- happens to contain the word "degraded".
RESOLVED_WITH_DEGRADED_PROSE = {
    "mode": "RESOLVED",
    "substitutes": [],
    "unmapped": [],
    "escalation": "every Commander run in this repo is structurally degraded until a map exists",
}
GENUINELY_DEGRADED = {
    "mode": "DEGRADED-NO-MAP",
    "substitutes": [{"path": "README.md", "content_hash": "abc", "source": "known-fallback"}],
    "unmapped": ["skills/ has no structural map"],
    "escalation": "escalated to the Commander",
}


def old_predicate(receipt: dict) -> bool:
    """The predicate as g4 first shipped it, kept here so the defect stays falsifiable."""
    return "DEGRADED" in json.dumps(receipt).upper()


def load_corrected_predicate():
    """Pull receipt_is_degraded out of the sibling script BY SOURCE, not by import."""
    tree = ast.parse(io.open(SOURCE, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "receipt_is_degraded":
            ns: dict = {}
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), ns)
            return ns["receipt_is_degraded"]
    raise SystemExit("FAIL: receipt_is_degraded is not defined in %s" % SOURCE)


new_predicate = load_corrected_predicate()
problems = []

old_on_resolved = old_predicate(RESOLVED_WITH_DEGRADED_PROSE)
new_on_resolved = new_predicate(RESOLVED_WITH_DEGRADED_PROSE)
new_on_degraded = new_predicate(GENUINELY_DEGRADED)

print("OLD substring predicate on a RESOLVED receipt: %s   <- the defect" % old_on_resolved)
print("NEW structured predicate on the same receipt:  %s   <- the repair" % new_on_resolved)
print("NEW structured predicate on a DEGRADED receipt: %s  <- no over-correction" % new_on_degraded)

if not old_on_resolved:
    problems.append("the old predicate no longer reproduces the defect -- this check has lost its point")
if new_on_resolved:
    problems.append("the corrected predicate STILL accepts a RESOLVED receipt")
if not new_on_degraded:
    problems.append("the corrected predicate rejects a genuinely degraded receipt")

# The substring scan must be gone from the shipped assertion, not merely shadowed.
src = io.open(SOURCE, encoding="utf-8").read()
live = "\n".join(l for l in src.splitlines() if not l.strip().startswith(('"""', "#", "*")))
if 'json.dumps(receipt).upper()' in live.replace('"""', ""):
    # only tolerated inside the docstring that explains the repair
    body_after_doc = src.split('"""', 4)[-1]
    if "json.dumps(receipt).upper()" in body_after_doc:
        problems.append("the substring scan is still live in g4_assert_discharged.py")

if problems:
    for p in problems:
        print("FAIL: %s" % p)
    sys.exit(1)
print("HARNESS-PREDICATE-DISCRIMINATES")
