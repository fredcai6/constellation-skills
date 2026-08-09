#!/usr/bin/env bash
# Harvest probe -- run BEFORE any `git worktree remove`.
#
# WHY (#508): the harvest substep reports "nothing to collect" identically whether a
# worktree genuinely has no export or the doctrine is looking for a retired filename.
# This probe names what it looked for and distinguishes the two. It never deletes.
#
# CORRECTION, 2026-08-08 -- v1 of this script was itself a check that cannot fail.
# It tested `[ -f .agent-work/CONSTELLATION_FEEDBACK.md ]` and reported PRESENT for
# every worktree. But that file is TRACKED (`git ls-files` confirms it, along with 57
# tracked files under .agent-work/staged-feedback/), so EVERY fresh worktree has it by
# checkout. PRESENT was true in the healthy world and the empty world alike -- the exact
# defect the probe exists to remove, reproduced inside the fix for it.
#
# What actually distinguishes a harvest source is that its content is NOT ALREADY ON MAIN:
#   (a) uncommitted in the worktree            -> git status --porcelain
#   (b) committed on the branch since it forked -> git diff --name-only main...HEAD  (three-dot)
# Three-dot matters: two-dot would also list every change MAIN made since the fork, which
# is the Admiral's own commits, not the crew's work.
#
# Usage:  bash .agent-work/epic-418-redux/closeout/harvest_probe.sh

set -u
echo "# Harvest probe -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo
echo "Doctrine of record: the INSTALLED skill on disk, not any loaded copy (#508)."
echo "A harvest source is content NOT already on main. Mere presence proves nothing:"
echo ".agent-work/CONSTELLATION_FEEDBACK.md and staged-feedback/ are TRACKED."
echo

# CORRECTION 2, 2026-08-09 (v4) -- the probe was technically correct and practically unreadable.
# It emitted 5207 lines, of which 4946 came from THREE worktrees that must never be swept
# (`clean` 4067, `issue-456` 545, `explore-code-map` 334). The six trees this epic may actually
# remove accounted for 156 lines, buried past line 1000. An operator scrolling that at the end of a
# long run does not read it -- which makes the probe's real output indistinguishable from noise.
# That is not a check that cannot fail, but it is the same failure at the presentation layer:
# a signal that is technically present and practically unreadable is not a signal.
#
# v4 therefore SUPPRESSES the file lists for do-not-sweep trees and prints counts instead. It does
# not skip them -- an unexpectedly large count on a protected tree is itself information -- but it
# refuses to bury the sweep-eligible trees under them.
#
# The do-not-sweep set is read from SWEEP_LIST.md's own table rather than retyped here, so the two
# documents cannot drift apart. If SWEEP_LIST.md is missing, the probe FAILS rather than silently
# treating every tree as sweepable -- an absent policy file must not read as "everything is fine".
SWEEP_LIST="$(dirname "$0")/SWEEP_LIST.md"
if [ ! -f "$SWEEP_LIST" ]; then
  echo "FATAL: $SWEEP_LIST not found -- refusing to run rather than report every tree as sweepable." >&2
  exit 2
fi
# EVERY backticked name in the DO-NOT-SWEEP table's first cell -- not just the first one.
# v4's initial cut used `s/^| `\([^`]*\)`.*/\1/p`, which stops at the first backticked token per
# row; the two `agent-*` trees share one row, so the second was silently dropped and came back
# UNCLASSIFIED. It failed SAFE (unclassified suppresses rather than sweeps) and it still had to be
# fixed -- found by running the probe and reading which trees it flagged, not by reading the sed.
protected=$(sed -n '/^## DO NOT SWEEP/,/^## Before any removal/p' "$SWEEP_LIST" \
            | sed -n 's/^|\([^|]*\)|.*/\1/p' \
            | grep -o '`[^`]*`' | tr -d '`' | tr -d '\r')
echo "Do-not-sweep set, read from SWEEP_LIST.md (not retyped here):"
echo "$protected" | sed 's/^/  /'
echo

for W in $(git worktree list --porcelain | awk '/^worktree /{print $2}'); do
  name=$(basename "$W")
  [ "$name" = "constellation-skills" ] && continue

  tag=""; quiet=""
  if [ "$name" = "governor-264" ]; then
    tag=" [PROTECTED -- NEVER SWEEP]"; quiet=1
  elif echo "$protected" | grep -qx -- "$name"; then
    tag=" [DO NOT SWEEP -- per SWEEP_LIST.md]"; quiet=1
  fi
  # A worktree on NEITHER list is the dangerous case: unclassified, so no one has decided about it.
  if [ -z "$quiet" ] && ! echo "$name" | grep -q '^epic418-'; then
    tag=" [!! UNCLASSIFIED -- absent from SWEEP_LIST.md; decide before sweeping anything]"; quiet=1
  fi
  echo "## $name$tag"

  uncommitted=$(git -C "$W" status --porcelain -- .agent-work/ 2>/dev/null)
  branch_only=$(git -C "$W" diff --name-only main...HEAD -- .agent-work/ 2>/dev/null)

  if [ -n "$quiet" ]; then
    # Counts only -- enough to notice something surprising, not enough to bury the real targets.
    nu=$(printf '%s' "$uncommitted" | grep -c . || true)
    nb=$(printf '%s' "$branch_only" | grep -c . || true)
    ni=$(git -C "$W" status --porcelain --ignored=matching -- .agent-work 2>/dev/null | grep -c '^!!' || true)
    echo "  not a sweep target -- lists suppressed: uncommitted=$nu branch-only=$nb ignored=$ni"
    echo
    continue
  fi

  if [ -n "$uncommitted" ]; then
    echo "  UNCOMMITTED (would be destroyed by removal):"
    echo "$uncommitted" | sed 's/^/    /'
  else
    echo "  UNCOMMITTED: none"
  fi

  if [ -n "$branch_only" ]; then
    echo "  ON THIS BRANCH ONLY (needs merge or cherry-pick, not file copying):"
    echo "$branch_only" | sed 's/^/    /'
  else
    echo "  ON THIS BRANCH ONLY: none"
  fi

  # (c) IGNORED files -- added in v3. Neither channel above can see them: `git status
  #     --porcelain` omits ignored paths and `git diff main...HEAD` only sees tracked ones.
  #     Found because epic418-a2-467 had 379 files on disk against 371 on main while BOTH
  #     channels reported clean. v1 was blind to trackedness; v2 was blind to ignoredness.
  #     REPORT them, do not judge them: they are usually disposable (gauge.json, __pycache__)
  #     and occasionally not, and this script cannot tell the difference -- the reader can.
  ignored=$(git -C "$W" status --porcelain --ignored=matching -- .agent-work 2>/dev/null | grep '^!!')
  if [ -n "$ignored" ]; then
    echo "  IGNORED (invisible to both channels above; destroyed by removal -- YOU judge these):"
    echo "$ignored" | sed 's/^/    /'
  else
    echo "  IGNORED: none"
  fi

  # Retired names are probed ONLY when locally modified -- a tracked retired file present
  # by checkout is main's business, not this worktree's.
  for p in .agent-work/LESSONS.md .agent-work/AGENT_FEEDBACK.md; do
    if echo "$uncommitted$branch_only" | grep -q "$p"; then
      echo "  !! RETIRED NAME locally changed: $p -- #447 removed this; investigate before sweeping"
    fi
  done

  if [ -z "$uncommitted$branch_only$ignored" ]; then
    echo "  => NOTHING TO HARVEST -- and this is a real null: ALL THREE channels were queried -- uncommitted, branch-only, and ignored -- and all three were empty."
  fi
  echo
done

echo "## Verdict"
echo "Nothing was deleted. Sweep only after every line above is collected, and only for"
echo "worktrees whose work is merged or confirmed dead."
