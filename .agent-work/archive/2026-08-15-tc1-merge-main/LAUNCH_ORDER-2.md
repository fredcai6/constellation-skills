# Launch Order: `tc1-merge-main` — attempt 2, the merge is done; push it

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER.md`; it still binds except where corrected here.

## The merge is complete and correct. Do not redo it.

Commit `3c040009` (`Merge: 5992b936 6947b15e`) is in your local branch, tree clean. I verified the
resolution myself: the diff against `origin/main` is exactly #588's own changes —
`scripts/checklist_engine.py` +50, `tests/test_spine_origin_isolation.py` +212,
`tests/test_explorer_templates.py` +5, `map/INDEX.md` +6. Nothing dropped, nothing extra.

**Do not merge again. Do not regenerate the map again. Do not touch any source file.**

## Why you stopped, and the exact command that prevents it

Your turn ended with:

> The full clean-env pytest suite is running in the background; I'll resume once it completes.

You are the **fifth** Commander today to end a turn this way, and the first to do it *after* an order that
warned about it by name. So the warning is not enough, and I am replacing it with a mechanism.

The problem: `python -m pytest -q` takes ~2 minutes, and the harness auto-backgrounds a bash command that
runs that long. Once backgrounded, nothing will ever wake you — your process exits when your turn ends.

**The fix is to run a command that blocks until the result exists, instead of one you have to wait on.**
Use this exact shape — the `until` loop is itself a single foreground command, and it does not return
until the suite has written its summary line:

```bash
rm -f /tmp/tc1-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/tc1-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/tc1-suite.log; do sleep 15; done
tail -5 /tmp/tc1-suite.log
```

If that itself gets backgrounded, **poll `/tmp/tc1-suite.log` with `tail`** until the summary line
appears. Either way you stay in your turn. **Do not end your turn while anything is pending.**

## The two steps that remain

1. **Verify the suite** with the command above. **Bar: `0 failed`, and `tests/test_code_map.py` green.**
   The passed count will exceed the old 3010 because the merge brought #587's tests in — that rise is
   expected and is not a problem. Only failures matter.
2. **Push** `tc1/worktree-identity`, then confirm with
   `gh pr view 588 --json mergeable,mergeStateStatus` that it no longer reports `CONFLICTING`/`DIRTY`.
   That is the whole point of this lane: while the PR conflicts, GitHub cannot compute a merge commit and
   **never runs CI at all**, which is why #588's last five pushes produced no checks.

Then drive your spine to terminal.

## Unchanged

**Not yours:** `scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py`,
`tests/test_explorer_templates.py`, `episodes/`, `scripts/hooks/spine_rail.py` (#589 open),
`scripts/run_crew.py`, `.mcp.json`. `spine_status` must describe `tc1-merge-main` — if not, stop and
report. Branch `tc1/worktree-identity` only; no second PR. **Fenced from merging the PR.**

**Do not dispatch a crew.** Everything here is yours, in this turn.

## Stop Conditions

- The clean-env suite shows any failure.
- `tests/test_code_map.py` fails — that would mean the map is stale despite the regeneration.
- The push is rejected, or #588 still reports `CONFLICTING` afterward.
- You find yourself about to end your turn with anything pending.

## Return Shape

What `spine_status` resolved to, named explicitly; the suite summary line; confirmation of the push; and
#588's `mergeable`/`mergeStateStatus` after pushing.
