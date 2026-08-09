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
# CORRECTED 2026-08-09: this was hardcoded to WAVE 4 (epic418-a2-467 / issue-467).
# Run during wave 5 it printed "17/17 complete, lease: released" -- wave 4's numbers -- which
# reads exactly like "the run is finished" to a fresh Admiral executing this note's own first
# instruction. Identical output in the done world and the mid-wave world: a check that cannot fail,
# sitting at the entry point of the crash-resume path.
# Wave 5 runs FIVE crews, so there is no single work area to point at. Enumerate them all.
W5="C:/Programs/constellation-skills-wt"
WT="$W5/epic418-w5-gates"
WORK="$WT/.agent-work/w5-gates"
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
echo "--- WAVE 5: all five crews (the wave that is actually running) ---"
for d in gates readiness addressing engine docs; do
  WD="$W5/epic418-w5-$d"
  [ -d "$WD" ] || { echo "  $d: WORKTREE GONE (swept?)"; continue; }
  # v3: print WHICH journal, not just when. The glob matches ~28 journals across every
  # work area checked out in the worktree, so `ls -t | head -1` can silently return a
  # STALE one from an older wave -- it did, reporting 22:47 while the crew was live at
  # 00:33, and I acted on it. Showing the path makes a wrong pick visible instead of
  # resolving it wrongly: the reader sees the work-id and knows if it is not the crew's.
  J=$(ls -t "$WD"/.agent-work/*/*.json.journal 2>/dev/null | head -1)
  JN=$([ -n "$J" ] && basename "$(dirname "$J")" || echo "-")
  C=$(git -C "$WD" rev-list --count main..HEAD 2>/dev/null)
  DY=$(git -C "$WD" status --porcelain 2>/dev/null | wc -l)
  LAST=$([ -n "$J" ] && date -u -r "$J" +%H:%M || echo "none")
  echo "  $d: last-engine-verb=$LAST (in work-area: $JN) commits=$C dirty=$DY"
done
echo "  ^ journal mtime is the ONLY liveness proxy that fires for every crew."
echo "  ^ gauge.json does NOT (see #452); file writes miss a reading agent."
echo "  ^ CHECK THE work-area NAME. If it is not this crew's, the timestamp is a STALE"
echo "    journal from another wave checked out in the same worktree, not the crew's silence."
echo "--- wave-5 PRs (ask the forge) ---"
gh pr list --state open --json number,headRefName --jq '.[]|select(.headRefName|startswith("epic-418/w5"))|"  PR #\(.number) \(.headRefName)"' 2>/dev/null || echo "  (gh unavailable)"
echo "=============== END DERIVED ==============="
