#!/bin/sh
# Verify each claimed RED commit actually fails AT THAT COMMIT.
# The tree at the commit is exported with `git archive` into a throwaway dir and
# re-inited as its own git repo, so `git ls-files` (which discover_corpus uses)
# sees exactly that commit's tracked set. The issue-456 worktree is never
# checked out, stashed or otherwise touched.
set -e
REPO="C:/Programs/constellation-skills/.claude/worktrees/issue-456"
commit="$1"
selector="$2"
work="$(mktemp -d)"
cd "$REPO"
git archive "$commit" | tar -x -C "$work"
cd "$work"
git init -q .
git add -A >/dev/null 2>&1
git -c user.email=r@r -c user.name=r commit -qm snapshot >/dev/null 2>&1
set +e
unset FORCE_COLOR PYTHONIOENCODING
python -m pytest tests/test_code_map.py -q --color=no -k "$selector" > out.txt 2>&1
echo "EXIT=$?"
tail -12 out.txt
echo "WORK=$work"
