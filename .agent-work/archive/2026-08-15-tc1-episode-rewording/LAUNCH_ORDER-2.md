# Launch Order: `tc1-episode-rewording` — attempt 2, finish the last three steps

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER.md`; it still binds except where corrected here.

## Your rewording is correct. Do not redo it.

Both statements are reworded, staged, and good. I read them. They are records now, not instructions, and
the substance survived — which was the hard part and it is done:

- `-002` now opens *"The run read the verifier source … and that read is what exposed the exact
  required/optional field split"*
- `-003` now opens *"The advance call on this non-exempt gate refused until it carried a `--why` …"*

**Do not rewrite them again.** Do not touch any other episode file.

## Why you stopped, and the thing to not do again

Your turn ended with:

> I'll stop issuing filler commands and wait for the monitor/background-task notification to arrive.

**Waiting is not something you can do.** When your turn ends, your process exits. There is no scheduler
and no notification will ever reach you. This is the **fourth** time a Commander has parked this way
today, and my previous orders warned about it — this one did not, because I judged the lane too small to
need the warning. That was my omission, not your invention.

The specific trap: the full suite takes about two minutes, and **the harness auto-backgrounds a bash
command that runs that long**. The moment that happens, "blocking" stops being true. If a command of
yours gets backgrounded, **poll its output file until it is complete** — do not end your turn waiting for
a notification about it.

## The three steps that remain, all in this turn

1. **Run the full suite, cache-clean, in a clean environment.** Clear caches first:
   `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
   Then run it with the three vars stripped — your own spine lease exports them and
   `tests/test_mcp_identity.py:600` asserts they are absent:

   ```
   env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q
   ```

   **Target: 3010 passed, 6 skipped, 0 failed, 1136 subtests.** If this gets backgrounded, poll for it.
2. **Commit** the two staged episode files to branch `tc1/worktree-identity`.
3. **Push**, so PR #588's CI re-runs. Then drive your spine to terminal.

## When you write your own closeout episodes

They face the same guard that sent you here. Write them as **observations of what this run did**, past
tense, describing the run rather than addressing a reader. Statements in the `workaround` and
`proposed-remedy` kinds must not open a clause with a bare verb — that is exactly what flagged `Read`,
`keep` and `pass` in the records you just fixed. **Do not add anything to the exception list.**

## Unchanged

Ownership: the two `tc1-windows-path-form-00{2,3}.md` files and your work area. **Not yours:**
`tests/test_episode_observations.py` and its exception list, `scripts/checklist_engine.py`,
`tests/test_spine_origin_isolation.py`, `scripts/hooks/spine_rail.py` (#589 open), `scripts/run_crew.py`,
`.mcp.json`, the four `tc1-worktree-identity-00*.md` episodes, and the archived work areas beside yours.

`spine_status` must describe `tc1-episode-rewording` — if not, stop and report. Branch
`tc1/worktree-identity` only; no second PR. **Fenced from merging.**

## Stop Conditions

- The clean-env suite does not reach 3010 / 6 / 0 / 1136.
- Green would require the exception list, deleting a record, or touching the guard.
- You find yourself about to dispatch anything, or about to end your turn waiting on something.

## Return Shape

What `spine_status` resolved to, named explicitly; the clean-env suite counts; the commit SHA;
confirmation you pushed to `tc1/worktree-identity` with #588 still unmerged.
