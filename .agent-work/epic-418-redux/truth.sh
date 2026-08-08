#!/usr/bin/env bash
# truth.sh — derive the run's real state by command. Never cite a status from memory or a note.
#
# WHY THIS EXISTS. Rule 2 of STATE_NOTE.md says "re-derive every status claim from its source
# before citing it." I wrote that rule, about a mistake I had just made, and then broke it three
# more times the same day — once while describing that very failure. A rule you must REMEMBER to
# consult gets read past. A rule you must RUN cannot be. This file is rule 2 converted from the
# first kind into the second.
#
# Usage:  bash .agent-work/epic-418-redux/truth.sh
set -u
REPO="C:/Programs/constellation-skills"
WT="C:/Programs/constellation-skills-wt/epic418-a2-467"
WORK="$WT/.agent-work/issue-467-trip-semantics"
BR="epic-418/a2-467-trip-semantics"

echo "=============== DERIVED $(date -u +%Y-%m-%dT%H:%M:%SZ) ==============="

echo "--- gates (source: execute.json, not any note) ---"
python - "$WORK/execute.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    print("  UNREADABLE:", e); raise SystemExit
t = d.get("tasks") or {}
done = sum(1 for v in t.values() if (v or {}).get("status") == "complete")
print(f"  {done}/{len(t)} complete   amendments: {len(d.get('amendments') or [])}")
for k, v in t.items():
    s = (v or {}).get("status")
    if s and s not in ("complete", "pending"):
        print(f"    ACTIVE: {k} = {s}")
s = d.get("engine_session") or {}
print(f"  lease: {s.get('status')} by {s.get('claimed_by')}")
PY

echo "--- context fill (its own gauge) ---"
python - "$WORK/gauge.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    print(f"  {round(d['fill_fraction']*100, 1)}%  at {d['observed_at']}  ({d['model']})")
    print("  NOTE: a successor reads its predecessor's value until its own first tool call.")
except Exception as e:
    print("  UNREADABLE:", e, "-- treat as UNKNOWN, never as safe")
PY

echo "--- liveness (two channels; neither alone is sufficient) ---"
for m in 3 10 20; do
  printf "  files written last %2smin: %s\n" "$m" \
    "$(find "$WT" -path "$WT/.git" -prune -o -newermt "-${m} minutes" -type f -print 2>/dev/null | wc -l)"
done
echo "  ^ crew writes look identical to Commander writes. A Commander waiting on a crew is QUIET AND ALIVE."
echo "  ^ authoritative channel is the harness IDLE NOTIFICATION. No notification = still running."

echo "--- source touched by the fix yet ---"
n=$(git -C "$WT" diff --name-only -- scripts tests 2>/dev/null | wc -l)
echo "  $n file(s)"; git -C "$WT" diff --stat -- scripts tests 2>/dev/null | tail -3

echo "--- branch (ask git, never infer) ---"
echo "  HEAD:  $(git -C "$WT" log --oneline -1 2>/dev/null)"
echo "  dirty: $(git -C "$WT" status --porcelain 2>/dev/null | wc -l) lines"
echo "  main drift since base (non-.agent-work): $(git -C "$REPO" diff --name-only d376b786..origin/main -- . ':(exclude).agent-work' 2>/dev/null | wc -l) files"

echo "--- forge (ASK IT; squash-merge makes ancestry lie) ---"
pr=$(gh pr list --head "$BR" --state all --json number,state -q '.[] | "#\(.number):\(.state)"' 2>/dev/null | tr '\n' ' ')
echo "  PR for branch: ${pr:-none}"
echo -n "  #467: "; gh issue view 467 --json state -q .state 2>/dev/null || echo "?"
echo -n "  CI runs in_progress on main: "
gh run list --branch main --limit 10 --json status -q '[.[] | select(.status=="in_progress")] | length' 2>/dev/null || echo "?"

echo -n "  unpushed commits: "; git -C "$REPO" rev-list --count origin/main..HEAD 2>/dev/null
echo "=============== END DERIVED ==============="
