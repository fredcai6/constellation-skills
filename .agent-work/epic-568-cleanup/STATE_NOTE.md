# State note — epic-568 cleanup

Two goals, set by the human 2026-08-16: **(1) the MCP door is usable; (2) every noted blocker is cleared.**
The orrery Admiral was this fleet's first outside tester; its defect report and the epic-568 closeout
audit are the two inputs.

## Landed before dispatch

- `209642c4` — launch-order doctrine: `cd` before the isolation check; arriving over the context HARD
  band is not a stop condition. Installed to `~/.claude/skills/`.
- `a69bbac4` — **#601**, the keystone: a re-claim re-stamps `claimed_at`, so #477's relaunch guard can
  actually fire. Installed. `claim --force` is no longer needed for a routine relaunch.

`main` at `a69bbac4`, clean, suite **3057 passed / 7 skipped / 0 failed**. That is the baseline every
lane re-measures against at gate time.

## Lanes, dispatched in parallel

| Lane | Worktree / branch | Issues | Tier |
|---|---|---|---|
| **A — the door becomes usable** | `.worktrees/cleanup-a-door` · `cleanup/a-door` | #604 crash, #603 bind-on-open + fail closed, #605 demo spine, then door-vs-CLI detection in the commander template | Opus 5 |
| **B — relaunch and context identity** | `.worktrees/cleanup-b-context-identity` · `cleanup/b-context-identity` | #600 gauge ownership (measurement first), #500 refresh-request consume | Opus 5 |
| **C — who is alive, whose gate** | `.worktrees/cleanup-c-liveness-rail` · `cleanup/c-liveness-rail` | #599 registry liveness, #549 keep the block drop the imperative | Sonnet 5 |

All three provisioned from `a69bbac4`; `verify_worktree_isolation.py` over all three paths exited 0.

**File ownership is disjoint by design.** A owns the door and `.mcp.json`; B owns the gauge and the
engine's trip/refresh regions; C owns `run_crew.py` and `spine_rail.py`. The one place they meet is
stated in both orders: C's #549 fix removes candidate 2 of B's open measurement, so **C reports the
moment it lands and B re-measures**.

## Lane D — unassigned filler

Small, safe, no dependencies. Give it to whichever lane frees up first, or run it here.

- **#602** — `verify_worktree_isolation --here` reports git's "not a git repository" verbatim, which
  reads as an isolation failure. ~5 lines.
- **#598** — tc5's uncovered default worktree layout: `tests/test_spine_lifecycle.py:161` skips from
  the primary checkout, so the case runs nowhere anyone measures.
- **#597** — the stale-`__pycache__` trap. Worth doing early rather than late: it fabricates phantom
  failures during exactly the measurement every lane's merge gate depends on.

## Merge gate

As epic 568 settled it, three times amended: local Linux green, an independent APPROVE, and a
failure-set difference against a `main` baseline **re-measured at gate time** — empty, or with every
addition carrying an error signature already on the baseline. Clear `__pycache__` before every
measurement. CI is one `windows-latest` job, red from pre-existing breakage; there is no Linux CI.

## Standing hazards for this wave

- **Every lane changes tooling it is running on.** `CLAUDE_PROJECT_DIR` resolves once at session launch,
  so a Commander in a worktree still executes the main checkout's hook code (#269). Validation goes in
  a fresh process. This bites C hardest (`spine_rail.py` fires on its own turns) and B next
  (`gauge_writer_hook.py`).
- **The door is bound to the demo spine** until A lands. Every lane drives its spine through the engine
  CLI with an explicit `--session-id` this wave. That is a disclosed exception to #559, not a
  reinterpretation of it.
- **Keep your shell out of a subordinate's worktree** until #549 lands.

## Open, not in any lane

#315 (cwd threading — blocked with a measured reason, needs design), #552 (lease reaper; C is
explicitly forbidden from reaping as a side effect), #567's remaining doctrine sweep, #482
(dogfooding conflict, which this wave is a live instance of).

_Written 2026-08-16 at dispatch._
