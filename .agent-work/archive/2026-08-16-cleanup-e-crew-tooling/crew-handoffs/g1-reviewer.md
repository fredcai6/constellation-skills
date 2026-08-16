# Reviewer Handoff

## Gate
g1 (issue #607)

## Survey State Location
Create your review survey checklist at `.agent-work/cleanup-e-crew-tooling/g1-review/review.json`.

## What Was Implemented
A background parent-lease heartbeat in `scripts/run_crew.py`, so a Commander blocked foreground on a dispatched crew never reads as engine-lease-stale to an external liveness reader purely from being blocked. New `PARENT_HEARTBEAT_INTERVAL_SECONDS = 300` constant, new `_parent_lease_heartbeat()` context manager (daemon thread, heartbeats the dispatching process's own ambient `SPINE_FILE`/`SPINE_SESSION` via `checklist_engine.load/heartbeat/save` every interval, no-ops when unset, swallows exceptions, joined before returning), wrapped around the single blocking `launch(...)` call in both `CliBackend.dispatch` and `CliBackend.resume`. New `ParentLeaseHeartbeatTests` (7 tests) in `tests/test_crew_launcher.py`.

## How to Inspect the Diff
This is a linked worktree — inspect the **UNCOMMITTED working tree**, not `git diff main...HEAD`:
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling
git status --porcelain
git diff scripts/run_crew.py tests/test_crew_launcher.py
```

## Task Statement
Full original task, close criteria, allowed scope, exclusions, constraints, and map anchors are in `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-implementer.md` — read it in full; it is the frozen contract this implementation must satisfy.

## Close Criteria
- `PARENT_HEARTBEAT_INTERVAL_SECONDS = 300` exists, distinct from and not confused with `HEARTBEAT_STALE_SECONDS`.
- `_parent_lease_heartbeat()`: reads the DISPATCHING process's own ambient `os.environ["SPINE_FILE"]`/`SPINE_SESSION` (not the child's derived env); no-ops when either unset; starts a daemon thread heartbeating via `checklist_engine.load`/`heartbeat`/`save` directly (no subprocess/CLI round-trip); NO self-collision guard; swallows heartbeat exceptions; `stop_event.set()` + `thread.join()` in a `finally`, before the context exits.
- Wired around the single `launch(...)` call in both `CliBackend.dispatch` and `CliBackend.resume` — nothing else in either method changed.
- `checklist_engine.py` untouched; only its existing public `load`/`heartbeat`/`save` are called. `process_alive`, `entry_liveness`, `active_duplicate` untouched.
- New tests genuinely exercise: no-op-when-unset, thread-advances-heartbeat, join-before-return ordering, exception-swallowing, and the shared-spine (no explicit `--spine`, child inherits parent's ambient pair) case for both `dispatch` and `resume`.
- Full mechanical distribution for `tests/test_crew_launcher.py` green, clean-env cache-cleared.

## Allowed Scope
Read-only review of `scripts/run_crew.py`, `tests/test_crew_launcher.py`. You may also independently re-run the fresh-process integration check described in the IMPLEMENTER_RESULT if you want stronger confidence than re-reading it — optional, not required for APPROVE.

## Specific Exclusions
`scripts/checklist_engine.py` and the other fenced files are outside your worktree's authority to inspect for correctness beyond confirming they were NOT touched (`git diff --stat` should show only the two files above) — do not BLOCK on anything you cannot inspect there.

## Constraints the Implementation Must Respect
- `os.kill(pid, 0)` is POSIX-only; `process_alive`'s cross-platform seam must be unchanged (confirm via diff, not just by not seeing it mentioned).
- No reaping, expiry, or force-claim anywhere in the diff.
- Fail-toward-alive: check that the no-self-collision-guard reasoning actually holds — re-read `checklist_engine.heartbeat()`'s own refusal-on-mismatched-session_id logic (it's read-only reference, `checklist_engine.py` is fenced but readable) and confirm the implementer's claim that a same-identity child heartbeating is safe.

## Map Anchors (inbound)
Same as `g1-implement`'s anchors in `.agent-work/cleanup-e-crew-tooling/execute.json` — structural: `run_crew.py:846-887` `launch_process`, `:1357`/`:1403` the two call sites, `:59` `HEARTBEAT_STALE_SECONDS` (distinct constant). Decision: `registry-before-staleness` (tried-and-floated, not the chosen mechanism) and the no-self-collision-guard reasoning (cold-critic finding #2 from the plan gate) — confirm the implementation actually reflects that finding's fix, not just the pre-fix design.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-implementer-result.md` — read it in full. It claims: 188 tests pass (181 pre-existing + 7 new), a wiring grep confirming exactly 2 call sites, and a real fresh-process integration check (separate OS processes) showing an artificially-staled lease read as genuinely stale before the fix and non-stale after a real blocking dispatch ran with the heartbeat active. Independently re-run at minimum the mechanical test command; treat the integration-check narrative as a claim to spot-check, not accept on its face.

## Suggested Model Tier
stronger — concurrency/threading correctness review rewards careful reasoning.

## Stop Conditions
BLOCK if: the diff touches any file outside the allowed scope, the self-collision reasoning does not actually hold up against `checklist_engine.py`'s real code, the tests don't actually exercise what they claim to, or the mechanical suite does not reproduce green in your hands.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.

**Delivery.** Write the full REVIEW_RESULT to `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-reviewer-result.md` before ending your turn.
