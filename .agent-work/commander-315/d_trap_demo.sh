set -u
WT=/home/tommy/projects/constellation-skills-wt/epic-568-315
T=$(mktemp -d)
git init -q "$T/main"; cd "$T/main"; git config user.email t@t; git config user.name t
mkdir -p scripts; cp "$WT/scripts/verify_worktree_isolation.py" scripts/
echo x > f.txt; git add -A; git commit -qm init
git worktree add -q "$T/wt" -b b1 >/dev/null 2>&1
mkdir -p "$T/wt/.agent-work/w1"

# A spine carrying an ORIGIN block, exactly as direction D specifies, and the
# shipped init.c0 check whose EXPECTED is <repo-root> substituted at init time.
cat > "$T/wt/.agent-work/w1/spine.json" <<JSON
{"work_id":"w1","type":"gated","items":["init"],
 "origin":{"work_id":"w1","branch":"b1","worktree":"$T/wt","base":"HEAD",
           "opened_at":"2026-08-12","opened_by":"spine_open","parent":"admiral"},
 "tasks":{"init":{"id":"init","status":"pending","imperative":"isolation",
  "preconditions":[{"id":"c0","statement":"in the provisioned worktree",
    "check":{"kind":"command","command":"python scripts/verify_worktree_isolation.py --here $T/wt"},
    "satisfied":false}],
  "postconditions":[],"evidence":[]}},
 "triage_candidates":[],"blockers":[],"refusals":[]}
JSON

py - "$T" <<'PY'
import json,sys,pathlib
T=sys.argv[1]
d=json.load(open(f"{T}/wt/.agent-work/w1/spine.json"))
stored=d["origin"]["worktree"]
expected=d["tasks"]["init"]["preconditions"][0]["check"]["command"].split("--here ")[1].strip()
print(f"  origin.worktree stored in the spine : {stored}")
print(f"  EXPECTED inside the check text      : {expected}")
print(f"  IDENTICAL? {stored == expected}")
PY
echo
echo "  So an engine that sets cwd = origin.worktree runs the check FROM the very"
echo "  path the check asserts it is standing in. Demonstrating, launcher in the"
echo "  WRONG worktree (the main checkout):"
echo
echo -n "  cwd = launcher's own (today)        : "
( cd "$T/main" && py "$WT/scripts/verify_worktree_isolation.py" --here "$T/wt" >/dev/null 2>&1 && echo "PASS (gate disarmed)" || echo "REFUSED (gate works)" )
echo -n "  cwd = origin.worktree (direction D) : "
( cd "$T/wt" && py "$WT/scripts/verify_worktree_isolation.py" --here "$T/wt" >/dev/null 2>&1 && echo "PASS (gate disarmed)" || echo "REFUSED (gate works)" )
cd /; rm -rf "$T"
