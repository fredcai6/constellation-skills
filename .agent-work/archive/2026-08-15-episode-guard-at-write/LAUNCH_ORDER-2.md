# Launch Order: `episode-guard-at-write` — attempt 2, your blocker is answered

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER.md`; it still binds except where corrected here.

## Your block was correct and it has been resolved

You refused to waive your own bound spine check and asked up. That was exactly right — *"a crew must not
waive its own bound spine check"* is the rule, and a lane that waives its own gate is worth nothing.

**`plan.c6` is now waived by the Admiral**, recorded on your spine as evidence `e-plan-2`. I verified your
claim rather than taking it: `map/ids.jsonl` is **0 bytes, 0 lines** on `main` at `2c46cab8`, so there is
genuinely no map inventory for an anchor to resolve against. It is pre-existing, it was independently
filed hours earlier by the `crew-verdict-and-door` lane as `code-map-ids-jsonl-is-structurally-empty.md`,
and it is outside your ownership.

**One correction to your blocker text:** `map/INDEX.md` is **populated** (27KB), not an unfilled
template. The empty `ids.jsonl` is the operative fault. Your conclusion held; the supporting detail was
half wrong. Do not repeat the "unfilled template" claim in your closeout.

## What remains

`plan` is unblocked. Drive the spine to terminal: `plan` → `execute` → `reconcile` → `triage` →
`review` → `feedback` → `archive`, then release the lease last.

**The engineering is already done and I have reviewed it.** Do not redo it, and do not widen it:

- `scripts/apply_episode_delta.py` (+136) — the write-time rejection.
- `tests/test_episode_observation_guard_at_write.py` (+302) — RED/GREEN/control/message tests.
- `scripts/install_constellation.py` (+12) and `tests/data/store_mentions.approved.txt` (+15).

## On the two files outside your ownership list

Both were **correct and necessary**, and I am recording that so you do not second-guess them at
`reconcile`:

- `install_constellation.py` — the writer now imports `verify_episode_observations.py`, so the install
  bundle must ship it, and `query_episodes.py` too because the companion guard walks reachability
  statically rather than by what is actually called. Without this an installed Commander gets
  `ModuleNotFoundError` before argparse runs — the precedent you cited for `run_crew.py` is exactly on
  point.
- `store_mentions.approved.txt` — a mechanical consequence of the comment you added.

My ownership list simply did not anticipate the bundling consequence. That is a gap in my order, not
overreach in your work.

## Still required before you close

- Full clean-env cache-clean suite: **0 failed.** Baseline `main` at `2c46cab8` is **3031 passed,
  6 skipped, 1136 subtests** from inside a worktree; yours should exceed the passed count by your new
  tests.
- The map regenerated and committed if it moves.
- In your report: where you put the check and why; the **purity finding** for `validate_delta`; what you
  chose for amendments to grandfathered records; and whether your own closeout episodes tripped your own
  check — that last one is the deliverable I am most interested in.

## Do not park — run this as your first action

Your process exits when your turn ends. The suite auto-backgrounds at ~120s, and `checklist_engine.py
advance` re-runs it during postcondition verification, backgrounding the same way.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
rm -f /tmp/egaw2-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/egaw2-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/egaw2-suite.log; do sleep 15; done
tail -20 /tmp/egaw2-suite.log
```

If something backgrounds anyway, poll with `TaskOutput(block=true)` or `tail`. If you are about to write
"I'll resume when…", that sentence ends your run. **Do not dispatch a crew.**

## Your own closeout episodes

Past tense, describing this run, not addressing a reader; no clause-opening bare verb in `workaround` /
`proposed-remedy`; nothing added to the exception list. Known trap: a verbatim quotation in **single**
quotes containing an apostrophe breaks the guard's quote-pairing and leaks a second-person hit — use
double quotes for quoted machine output.

**If your own change rejects one of your own statements, that is a success.** Recast the sentence and say
so — it is the cleanest possible proof the fix works on the exact failure it was built for.

## Unchanged

Ownership and fences from `LAUNCH_ORDER.md` stand: the guard's rules, its exception list,
`tests/test_episode_observations.py`, `scripts/verify_episode_observations.py`, existing `episodes/`
records, `scripts/hooks/spine_rail.py` and `.claude/settings.json` (the sibling lane
`stop-hook-door-binding` is live in those), `scripts/checklist_engine.py`, `scripts/run_crew.py`,
`.mcp.json`.

## Return Shape

What `spine_status` resolved to, named explicitly; confirmation `plan.c6` reads waived and the spine
reached terminal; the purity finding; the grandfathered-amendment decision; whether your own episodes
tripped your own check; clean-env suite counts; whether the map moved; and the PR state.

**You are fenced from merging.** PR #592 is open; the Admiral merges.
