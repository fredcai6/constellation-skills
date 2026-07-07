# Debt Sweep Cadence

How to keep the Loop 4 cross-project feedback sweep (`scripts/collect_feedback.py`) from going dormant.
This doc is descriptive of policy already enforced by the script itself (its dry-run-by-default,
human-gated issue filing) — it is not a new enforcement mechanism, just the recipe so the cadence isn't
rediscovered or re-guessed each time it's run.

## Dogfood project roots

The current set of consuming repos swept for feedback:

- `C:/Programs/f1Brainz`
- `C:/Programs/network_elo`
- `C:/Programs/story_time`

This list is durable and expected to grow as new dogfood projects adopt Constellation — add a repo here
the first time it gains a `.agent-work/CONSTELLATION_FEEDBACK.md` export worth sweeping.

## Sweep invocation

From this repo's root, with the roots above as positional arguments. See `scripts/collect_feedback.py`'s
own module docstring for the collection/fingerprinting/dedup mechanism — it is not repeated here.

Bookkeeping sweep (marks current entries as collected, no issue-filing side effects):

```
python scripts/collect_feedback.py C:/Programs/f1Brainz C:/Programs/network_elo C:/Programs/story_time --mark
```

Human-gated backlog sync (dry run by default — prints what it would file/comment and touches nothing
until `--confirm` is added):

```
python scripts/collect_feedback.py C:/Programs/f1Brainz C:/Programs/network_elo C:/Programs/story_time --file-issues
python scripts/collect_feedback.py C:/Programs/f1Brainz C:/Programs/network_elo C:/Programs/story_time --file-issues --confirm
```

Issue filing stays human-gated: `--confirm` is a separate, deliberate step from the sweep itself, and
this doc doesn't change that — it's already how `collect_feedback.py` defaults.

## Scheduled-run recipe (not wired live by this doc)

To run the bookkeeping sweep on a cadence (e.g. weekly) instead of relying on someone remembering, a human
can wire it through this harness's `schedule` skill (`CronCreate`/`CronList`/`CronDelete`):

- **Command:** the `--mark` invocation above, run from this repo's root.
- **Interval:** e.g. weekly — a cron expression such as `17 9 * * 1` (Monday ~9am, off the `:00` mark).
- **Output:** redirect to a dated report file, e.g. `python scripts/collect_feedback.py <roots...> --mark --out .agent-work/debt-sweeps/<date>.md`, so each run leaves a durable artifact instead of only console output.
- **Caveat:** this harness's cron jobs are session-scoped and auto-expire after 7 days (see the `schedule`
  skill's own doctrine) — they re-arm cheaply from a live session but are not a substitute for an
  unattended, always-on scheduler. For durability without a human re-arming it weekly, wire the same
  command into an OS-level scheduler instead (cron on Linux/macOS, Task Scheduler on Windows) pointed at
  the invocation above.

This recipe is for the human to invoke when ready — writing this doc does not itself create any
scheduled or cron job.
