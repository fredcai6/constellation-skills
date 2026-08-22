# Epic summary — `20260820-deficiency-cleanup`

**Closed 2026-08-21.** `main` at `5858a85c`, pushed. Ordinary suite 3472 passed, 6 skipped, 1224 subtests.

## What it was chartered to do, and what happened instead

Reconcile the defect ledger against current main, finish the bounded repairs, and prepare
an independently criticized architecture choice for the #634/#638/#632/#357/#369/#615
cluster.

The repairs shipped. **The architecture choice was retired rather than made** — and that
was the right outcome, not a failure to deliver. The latitude contract named honest
negatives as acceptable when they retire a stale premise; this is one.

## What shipped

| Lane | Outcome |
|---|---|
| #500 | Refresh requests stamped and consumed by the first later claim. **Closed.** |
| #636 | Registry write is a transaction; selection is exact identity **plus** worktree. **Closed.** |
| #638 mechanical | Spine close refuses atomically while still writing rejection telemetry. Open for the archive-move half. |
| #613 | No second heartbeat writer when a child inherits the same spine pair. **Closed.** |
| **A** | The engine stopped telling agents to resume dead runs. |
| **B** | Cross-session waive is one call, not five; `--parent` required and documented. |

Three of six lanes were **blocked by independent review and repaired** before approval.

## The defect the epic actually found

`_is_stale` existed, worked, and had four call sites — **none in any rendering path.** So
`current` on a plan whose owner died 22 days ago printed:

```
RAIL: A working solution is the MIDDLE of this run — you are 7 steps from done.
      Next: the ACTIVE line above. Run it.
LEASE active: charter-refresh-20260728 (heartbeat 2026-07-29T17:52:38)
```

All 58 `active` leases in the checkout were stale. `decide_session_start` injected the same
resume order at SessionStart, unasked, with no staleness check in its path. The system was
not failing to warn an honest agent — it was **instructing one into the mistake.**

Measured cost: stale leases reclaimed **0 times by plain `claim`, 25 times by `--force`.**

## Why no architecture was built

A channel experiment dispatched one wave through the shipped `run_crew --backend cli` path.
**E1, E2, E3 and E5b all failed to reproduce.** The crew drove a seven-gate plan with
`0 claims, 0 releases` — `require_session` permits leaseless operation explicitly. Most of
the cluster was an artifact of the Admiral's own dispatch channel.

The final ballot ranked **minimal intervention first and status quo third**, ahead of two of
three full architecture designs. Option C was investigated and found **dominated**: the Stop
guard is armed by the binding store written by the *act* of `claim`, not by the lease
record, so demoting the lease would not have delivered its own benefit.

## What this run got wrong

Six Admiral claims were wrong. **Every one was caught downstream — none by the Admiral.**

| Claim | Truth | Caught by |
|---|---|---|
| No dispatched crew can be railed | `run_crew` crews are fully railed | Lane C |
| A stranded plan can't be reclaimed | A plain `claim` takes it | Lane A, then measured |
| The hazard is env inheritance | `SPINE_*` were unset; it's a session-keyed file | The experiment |
| Lineage edge empty on both channels | 172 of 545 registry entries carry a parent | Lane D |
| A3 scoped to one renderer | There were two; the Stop hook still lied | The Implementer |
| `git add` then `git commit` | Commits the whole index — swept 275 files | Caught on inspection |

The dossier carrying the first three seeded all three candidate lanes. Two caught the
errors unprompted.

## What the crew got right

The A+B lane declined an Admiral instruction to share a helper, citing a documented
stdlib-only law, and substituted a regression pinning both renderers against each other —
sharing *avoids* drift, the regression *detects* it. It disclosed that its own tests had
re-staled the map instead of quietly regenerating. It ran a doctrine-pinning test unprompted
after editing the file that test guards.

## Disposition

- **Closed:** #500, #613, #636
- **Commented with corrected premises:** #457, #615, #357, #369, #632, #638
- **Recorded as episodes, not filed:** R9/R10 inert on leaseless spines; `origin.parent` never
  populated; `init_work_area --spine` traceback
- **13 episodes** in the store — 3 defects, 10 retrospective

## What remains

**#615's two questions**, which are a human scoping decision rather than further execution:
should reclaiming a stale lease cost as little as it does, and what is the true liveness
signal? `_is_stale` is heartbeat-only at 1800s with no pid; `run_crew.entry_liveness` is
three-state and pid-corroborated at 28800s. **16x apart, and the engine holds the blind one.**
pid was unavailable for 55 of 57 stale leases — which is why the shipped fix renders age and
never a verdict.
