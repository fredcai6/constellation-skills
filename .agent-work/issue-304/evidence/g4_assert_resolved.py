"""g4 m1 check: the MATERIALIZED spine carries resolved placeholders, not literals.

A command check whose materialized text still contains a literal ``<commander-skill-dir>``,
``<repo-root>`` or ``<work-id>`` never ran. This asserts, against the scratch spine that
``init_work_area.py`` actually wrote:

1. zero tokens of the resolver's own placeholder family survive anywhere in the file;
2. the ``context`` c2 command's ``--root`` is an ABSOLUTE path that exists on disk;
3. the ``context`` c2 command's ``--work-id`` is the real scratch work-id.

Exits non-zero, printing what failed, if any of that is untrue.
"""

import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK_ID = "g4-scratch-run"
SPINE = ROOT / ".agent-work" / WORK_ID / "spine.json"

# The exact family init_work_area.py's resolver owns.
RESOLVER_FAMILY = re.compile(
    r"<(work-id|repo-root|[a-zA-Z0-9-]+-skill-dir|[a-zA-Z0-9-]+-session-id|skill-dir)>"
)

problems = []

if not SPINE.is_file():
    sys.exit("FAIL: no materialized spine at %s" % SPINE)

raw = io.open(SPINE, encoding="utf-8").read()

survivors = sorted(set(RESOLVER_FAMILY.findall(raw)))
print("unresolved resolver-family placeholder tokens in the materialized spine: %d %s"
      % (len(survivors), survivors))
if survivors:
    problems.append("resolver-family placeholders survived: %s" % survivors)

spine = json.loads(raw)
cmd = spine["tasks"]["context"]["postconditions"]
c2 = [c for c in cmd if c["id"] == "c2"][0]
command = c2["check"]["command"]
print("materialized context.c2 command: %s" % command)

for literal in ("<commander-skill-dir>", "<repo-root>", "<work-id>"):
    if literal in command:
        problems.append("literal %s survives in the context check command" % literal)

m = re.search(r"--root (\S+)", command)
if not m:
    problems.append("context check command carries no --root")
else:
    root_val = m.group(1)
    p = Path(root_val)
    print("--root value: %s   absolute=%s   exists=%s" % (root_val, p.is_absolute(), p.is_dir()))
    if not p.is_absolute():
        problems.append("--root %r is not absolute" % root_val)
    if not p.is_dir():
        problems.append("--root %r does not exist on disk" % root_val)

m = re.search(r"--work-id (\S+)", command)
if not m or m.group(1) != WORK_ID:
    problems.append("--work-id did not resolve to %s (got %r)" % (WORK_ID, m and m.group(1)))
else:
    print("--work-id value: %s" % m.group(1))

# Informational only: any OTHER angle-bracket token, which the resolver does not own.
others = sorted(set(t for t in re.findall(r"<[a-zA-Z0-9_.\- ]{1,40}>", raw)
                    if not RESOLVER_FAMILY.fullmatch(t)))
print("other angle-bracket tokens (informational, not resolver-owned): %s" % others)

if problems:
    for pr in problems:
        print("FAIL: %s" % pr)
    sys.exit(1)
print("PLACEHOLDERS-RESOLVED")
