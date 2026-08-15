# Launch Order: `launcher-hygiene` — attempt 2, measure and ship what you already built

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER.md`; it still binds except where corrected here.

## Your work is good. Do not redo any of it.

Four files, 140 insertions, all reviewed by me and all correct in shape:

- `tests/test_mcp_identity.py` (+15) — Task 1
- `scripts/run_crew.py` (+55) and `tests/test_spine_lifecycle.py` (+47) — Task 2
- `skills/commander/references/crew-dispatch.md` (+24) — Task 3a

`tests/test_spine_lifecycle.py` was not on your ownership list, and adding
`TestSpineTerminalThroughArchiveRelocation` there was **the right call** — that is where `close_work`
lives, and composing the real relocation with the real `spine_terminal` read is exactly the evidence I
asked for. Your own comment says it: *"no mock of either, because the bug lives in how the two behaviors
compose."* Keep it.

## Why your run ended, and the one thing to do differently

Your turn ended with:

> Waiting for the background suite run to complete — I'll pick back up automatically when it finishes.

**Nothing will pick you back up.** Your process exits when your turn ends. There is no scheduler and no
notification can reach a process that no longer exists.

You are the **sixth** Commander to do this today — and the first to do it *while writing the
documentation that warns against it.* That is not an insult; it is the finding. Your Task 3a text is
correct, and a warning in prose, including the one in your own previous order, has now failed six times.
The problem is that at the moment a command gets backgrounded, waiting genuinely feels like the careful
choice.

**So this order removes the choice.**

### Your first action this turn — copy this block exactly

Do **not** run `python -m pytest` directly at any point. Run this, verbatim, as your first action:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/launcher-hygiene
rm -f /tmp/lh-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/lh-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/lh-suite.log; do sleep 15; done
tail -20 /tmp/lh-suite.log
```

The `until` loop is a **single foreground command that does not return until the result exists**. That is
the whole trick: you never hold a pending background job with an empty turn.

If that command is itself backgrounded, **`tail /tmp/lh-suite.log` repeatedly until the summary line
appears.** Do not end your turn while anything is pending. If you find yourself about to write "I'll
resume when…", that sentence terminates your run — poll instead.

## Then finish

1. **Bar: `0 failed`.** From inside this worktree expect ~3028 passed / 6 skipped plus your new tests.
   `tests/test_spine_lifecycle.py:161` skips unless the checkout sits directly inside `.worktrees`, which
   is why the worktree figure differs from the primary checkout's 3027 / 7 — location, not regression.
2. Regenerate the map: `python -m scripts.code_map build --root .`; commit if it moves.
3. **Commit and push** to `fix/launcher-hygiene`, **open the PR**, then drive your spine to terminal.
4. In your report, state whether you attempted **Task 3b** (the Stop-hook mechanical check) and, if you
   declined it, why. Declining is fully acceptable — it required both a red *and* a control, and without
   both it must not ship.

## Task 3b just got its strongest evidence

If you did decline it, record this in your findings, because it changes the argument: **six occurrences,
and the two documentation-shaped remedies have both now been tested and failed** — a prose warning
(attempt 1 of `tc1-merge-main`) and shipping the idiom in the order itself (your attempt 1, which carried
the exact block above). The idiom works when used; providing it does not make it get used. That leaves a
mechanical Stop-hook check as the only remedy not yet falsified, which is a materially stronger case than
when this lane was scoped.

## Unchanged

Ownership, fences, and stop conditions from `LAUNCH_ORDER.md` all stand — including that
`scripts/checklist_engine.py` is not yours (the `archive` gate relocating the work area is **correct**),
and that `docs/CHECKLIST_SCHEMA.md` and `skills/admiral/templates/LAUNCH_ORDER.template.md` belong to the
live sibling lane `tc6-doctrine`. **Do not dispatch a crew.**

Your closeout episodes face the episode-observation guard: write them as past-tense observations of what
this run did, and in `workaround` / `proposed-remedy` kinds do not open a clause with a bare verb. Do not
add to the exception list.

## Return Shape

What `spine_status` resolved to, named explicitly; per task, what you changed and its red/green proof;
whether 3b shipped or was declined and why; the clean-env suite summary line; whether the map moved; the
PR number; and confirmation it is open and unmerged.
