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

for W in $(git worktree list --porcelain | awk '/^worktree /{print $2}'); do
  name=$(basename "$W")
  [ "$name" = "constellation-skills" ] && continue
  case "$name" in
    governor-264) tag=" [PROTECTED -- NEVER SWEEP]" ;;
    *) tag="" ;;
  esac
  echo "## $name$tag"

  uncommitted=$(git -C "$W" status --porcelain -- .agent-work/ 2>/dev/null)
  branch_only=$(git -C "$W" diff --name-only main...HEAD -- .agent-work/ 2>/dev/null)

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

  # Retired names are probed ONLY when locally modified -- a tracked retired file present
  # by checkout is main's business, not this worktree's.
  for p in .agent-work/LESSONS.md .agent-work/AGENT_FEEDBACK.md; do
    if echo "$uncommitted$branch_only" | grep -q "$p"; then
      echo "  !! RETIRED NAME locally changed: $p -- #447 removed this; investigate before sweeping"
    fi
  done

  if [ -z "$uncommitted$branch_only" ]; then
    echo "  => NOTHING TO HARVEST -- and this is a real null: both channels were queried and both were empty."
  fi
  echo
done

echo "## Verdict"
echo "Nothing was deleted. Sweep only after every line above is collected, and only for"
echo "worktrees whose work is merged or confirmed dead."
