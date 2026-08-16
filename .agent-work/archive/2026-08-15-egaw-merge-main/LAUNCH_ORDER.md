# Launch Order: `egaw-merge-main` — one generated-file conflict, then #592 is done

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

Mechanical and final. PR #592's content is finished, reviewed and verified green (3040 passed, 6 skipped,
0 failed, cache-clean, measured by the Admiral independently). This is the last step before merge.

## Mission

#592 is `CONFLICTING` with `main`, so GitHub cannot compute a merge commit and **never runs CI**. Exactly
one file conflicts — measured with `git merge-tree` before this order was written:

```
map/INDEX.md
CONFLICT (content): Merge conflict in map/INDEX.md
Auto-merging scripts/install_constellation.py     <- merges cleanly, no action needed
```

`main` moved to `3c35e857` (#593, the Stop-hook door binding) and regenerated the map. `map/INDEX.md` is
**generated**, so two independent regenerations conflict by construction. This is issue **#544**, a known
structural tax, not a mistake by anyone.

## Do this

```
git merge origin/main            # expect map/INDEX.md as the ONLY conflict
python -m scripts.code_map build --root .
git add map/INDEX.md && git commit
```

**Do not hand-merge the map, do not pick hunks, do not take one side.** Regenerate it.
`tests/test_code_map.py` reds on a stale map, so a correct regeneration is verifiable rather than a
matter of taste.

**If any file other than `map/INDEX.md` conflicts, stop and report.**

## After the merge, confirm nothing was lost

#592's own changes against `main` should still be: `scripts/apply_episode_delta.py` (the write-time
guard, in the *apply* phase), `tests/test_episode_observation_guard_at_write.py` (RED/GREEN/control,
git-free), `scripts/install_constellation.py` (bundling the guard),
`tests/data/store_mentions.approved.txt`, and `map/INDEX.md`. **If the merge appears to drop any of it,
stop and report.**

## Then

1. Full clean-env cache-clean suite. **Bar: `0 failed`** and `tests/test_code_map.py` green. The passed
   count will rise above 3040 as #593's tests arrive — expected, not a problem. Only failures matter.
2. Push to `fix/episode-guard-at-write`.
3. Confirm `gh pr view 592 --json mergeable` no longer reports `CONFLICTING`.
4. Drive your spine to terminal.

## Do not park — run this as your first action

Your process exits when your turn ends. The suite auto-backgrounds at ~120s, and `checklist_engine.py
advance` re-runs it during postcondition verification, backgrounding the same way.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
rm -f /tmp/egawm-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/egawm-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/egawm-suite.log; do sleep 15; done
tail -20 /tmp/egawm-suite.log
```

If something backgrounds anyway, poll with `TaskOutput(block=true)` or `tail`. If you are about to write
"I'll resume when…", that sentence ends your run. **Do not dispatch a crew.**

Note: `main` now carries #593, which lets the Stop hook see a spine claimed through the MCP door. If you
try to end your turn mid-spine you may be **refused outright**. That is the fix working, not an error —
keep driving the gate.

## Your own closeout episodes

Your branch enforces the episode guard **at write time**, so your own writer will refuse an
instruction-shaped statement as you author it. Past tense, describing this run, not addressing a reader;
no clause-opening bare verb in `workaround` / `proposed-remedy`. If your own writer refuses one of your
statements, say so — that is the fix working on its intended target. Use double quotes for quoted machine
output (a single-quoted apostrophe breaks the guard's quote-pairing).

## File Ownership

**Yours:** `map/INDEX.md` (by regeneration), the merge commit, your work area.

**NOT yours — do not edit while resolving:** `scripts/apply_episode_delta.py`,
`tests/test_episode_observation_guard_at_write.py`, `scripts/install_constellation.py`,
`scripts/verify_episode_observations.py`, `tests/test_episode_observations.py`,
`scripts/hooks/spine_rail.py`, `.claude/settings.json`, `.github/workflows/ci.yml`, `.mcp.json`. Taking
main's side for files only main touched is a normal merge outcome, not editing them.

## Stop Conditions

- Any file other than `map/INDEX.md` conflicts.
- The merge appears to drop any of #592's listed changes.
- The clean-env suite shows any failure.
- You find yourself hand-editing `map/INDEX.md`, dispatching, or ending your turn with work pending.

## Return Shape

What `spine_status` resolved to, named explicitly; the merge result and which files conflicted; the
clean-env suite summary line; the commit SHA; and #592's `mergeable` status after pushing.

**You are fenced from merging the PR.** The Admiral merges.
