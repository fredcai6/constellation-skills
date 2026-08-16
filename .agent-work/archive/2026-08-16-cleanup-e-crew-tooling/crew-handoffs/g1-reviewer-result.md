Verdict: APPROVE

# REVIEW_RESULT — g1 (issue #607)

## Scope confirmation
`git diff --stat` (against the uncommitted working tree, as instructed — this
is a linked worktree, not a `main...HEAD` diff) shows exactly:
```
 scripts/run_crew.py         |  90 ++++++++++++++++-
 tests/test_crew_launcher.py | 238 ++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 324 insertions(+), 4 deletions(-)
```
`git diff --stat -- scripts/checklist_engine.py` is empty — confirmed
untouched. `grep -n "process_alive\|entry_liveness\|active_duplicate"` against
the `run_crew.py` diff returns nothing — confirmed none of the three fenced
functions were touched or referenced. No file outside the allowed scope
changed.

## Per-check findings

**Join-before-return ordering (dispatch and resume, no gap).** Confirmed by
direct diff read: in both `CliBackend.dispatch` and `CliBackend.resume`, the
`with _parent_lease_heartbeat():` block contains *only* the
`exit_code = launch(...)` statement — nothing else moved in or out. The
context manager's `finally: stop_event.set(); thread.join()` runs at
`__exit__`, which completes before the `with` block's suite is exited, which
happens before the subsequent `finalize_from_exit_code(...)` call (outside the
`with`, at the original indentation) runs. `thread.join()` blocks until the
target function (`_beat_loop`) actually returns — including any beat that was
already mid-`load/heartbeat/save` when `stop_event.set()` was called — so
there is no window where a beat can still be in flight, or a new beat can
start, after `join()` returns. I independently exercise this ordering via
`test_thread_is_joined_before_context_manager_returns`, which asserts
`threading.enumerate()` no longer contains the named thread *immediately*
after the `with` exits (no sleep, no polling) — this can only pass if `join()`
genuinely blocked to completion. Holds for both call sites; nothing else in
either method changed (confirmed by diff: only the two lines wrapping
`exit_code = launch(...)` differ).

**No-self-collision-guard reasoning, checked against real
`checklist_engine.heartbeat()` source** (`scripts/checklist_engine.py:1168-1180`):
```python
def heartbeat(cl: dict, session_id: str) -> str:
    lease = _active_lease(cl)
    if lease is None:
        raise EngineError("no active lease to heartbeat; `claim` first")
    if session_id != lease.get("session_id"):
        raise EngineError(...)
    lease["last_heartbeat"] = _now()
    ...
```
This is real, not just asserted by the implementer: `heartbeat()` checks
identity match against the *lease's own* `session_id`, not caller uniqueness
or provenance. In the shared-spine case (no explicit `--spine`, child inherits
the parent's own ambient `SPINE_SESSION` unchanged — confirmed by reading
`crew_env()` at `run_crew.py:903-948`, which only assigns `SPINE_FILE`/
`SPINE_SESSION` into the child env when a distinct value is explicitly given,
otherwise leaving the inherited `base_env` value untouched), the parent's
heartbeat thread calls `heartbeat(cl, spine_session)` where `spine_session`
*is* the value the lease was claimed under — so `session_id ==
lease['session_id']` trivially holds regardless of which process/thread makes
the call. There is no scenario in which the parent's own heartbeat calling
`heartbeat()` with its own owning identity is refused. The claim holds.

**Exception handling.** `_beat_loop`'s `try/except Exception: pass` wraps the
entire `load → heartbeat → save` sequence per tick; nothing inside the `with`
block in `dispatch`/`resume` can observe an exception from the heartbeat
thread since threads don't propagate exceptions to their parent by default in
Python (an uncaught thread exception would only print to stderr via
`threading.excepthook`, not raise in the main thread) — the explicit
`except Exception: pass` additionally suppresses that. Directly verified with
`test_heartbeat_exception_is_swallowed_not_propagated`, which points
`SPINE_FILE` at a path that will never exist (guaranteeing `checklist_engine.load`
raises `FileNotFoundError` on every tick) and asserts the `with` block exits
cleanly. I ran this test in isolation and in the full suite; passes.

**Test non-vacuousness — independently verified, not just re-read.** I did not
trust the pasted evidence at face value. I copied `scripts/run_crew.py` aside,
removed both `with _parent_lease_heartbeat():` wraps (restoring the pre-fix
unwrapped `exit_code = launch(...)` calls) to simulate the bug this gate
fixes, and reran `ParentLeaseHeartbeatTests`:
```
FAILED test_dispatch_heartbeats_ambient_lease_in_shared_spine_case
FAILED test_resume_heartbeats_ambient_lease_in_shared_spine_case
AssertionError: '2026-08-16T15:53:35.945334+00:00' not greater than '2026-08-16T15:53:35.945334+00:00'
5 passed (the 5 unit-level tests, which exercise `_parent_lease_heartbeat` directly and correctly don't depend on wiring)
```
This confirms the two shared-spine/wiring tests (e) genuinely catch the
wiring being absent — not vacuous. I then restored the file from the backup
copy and confirmed `git diff --stat` matched the original exactly and the
full suite was green again (188 passed). The other 5 unit tests
((a) x2, (b), (c), (d)) test `_parent_lease_heartbeat()` directly against real
ambient-env manipulation and a real `checklist_engine`-built spine (via
`claim()`, not a hand-rolled dict) — each assertion (thread-alive booleans,
`last_heartbeat` string inequality/ordering, no-exception-reaches-here) is
tied to genuine, distinguishable before/after state, not something that would
be true with the feature absent.

**Mechanical suite — reproduced green independently, twice, plus 5x reruns of
the new class alone (no flakes).**
```
$ find . -name __pycache__ -exec rm -rf {} +
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
188 passed in 0.77s
```
Matches the IMPLEMENTER_RESULT's pasted count exactly (181 pre-existing + 7
new). Reran after the sabotage/restore cycle above — still 188 passed,
confirming the restore was byte-for-byte faithful (diff stat identical to
pre-sabotage). Ran `ParentLeaseHeartbeatTests` alone 5x in a row — consistent
7 passed each time, ~0.19-0.21s, no flakes observed.

**Wiring grep — reproduced independently, same result:**
```
./scripts/run_crew.py:72:PARENT_HEARTBEAT_INTERVAL_SECONDS = 300
./scripts/run_crew.py:1307:# (comment)
./scripts/run_crew.py:1327:    (docstring)
./scripts/run_crew.py:1349:    effective_interval = PARENT_HEARTBEAT_INTERVAL_SECONDS if interval is None else interval
./scripts/run_crew.py:1472:        with _parent_lease_heartbeat():
./scripts/run_crew.py:1532:        with _parent_lease_heartbeat():
```
Exactly 2 real call sites, matching both the implementer's claim and the
handoff's expectation.

**Constant distinctness and other close criteria.** `PARENT_HEARTBEAT_INTERVAL_SECONDS
= 300` sits right after `HEARTBEAT_STALE_SECONDS = 28800` with an explicit
comment distinguishing the registry-entry-heartbeat axis from the
engine-lease-heartbeat axis — no risk of confusion on read. `_parent_lease_heartbeat`
reads `os.environ.get("SPINE_FILE")`/`SPINE_SESSION"` directly (the
dispatching process's own ambient env), never anything derived from `env =
_crew_door_env(...)` (the child's env, built and used later in each method,
after the heartbeat helper has already captured the parent's own values).
No-op-when-unset is a plain early `yield; return` before any thread is
created — confirmed both by reading and by `test_noop_when_ambient_vars_unset`
/ `test_noop_when_only_one_ambient_var_set`. Interval is injectable via a
keyword defaulting to the module constant, resolved at call time (not
def-time), which is what lets tests monkeypatch `RC.PARENT_HEARTBEAT_INTERVAL_SECONDS`
directly and have it take effect through the real `dispatch`/`resume` call
sites (verified: `effective_interval` is computed inside `_beat_loop`'s
enclosing function body by name lookup against module globals, so the
monkeypatch is visible).

`os.kill`/`process_alive`'s POSIX seam: untouched, confirmed by the diff
containing no reference to `process_alive` at all — the new code only uses
`threading`, stdlib and cross-platform. No reaping/expiry/force-claim anywhere
in the diff — the only new mutating calls are `checklist_engine.heartbeat`
(refresh-only, refuses on identity mismatch) inside a swallowed-exception
loop.

## Blockers
None.

## Out-of-scope observations
- **Not a blocker, but worth a future issue**: in the shared-spine case (the
  common, intended case for this fix), the parent's heartbeat thread and the
  child crew process now both write to the *same* spine JSON file
  concurrently — the parent every `PARENT_HEARTBEAT_INTERVAL_SECONDS`, the
  child via its own engine verbs during its work. `checklist_engine.save()`
  appears to be a plain non-atomic read-modify-write with no file locking (the
  implementer's own evidence section independently surfaces this: a
  "transient same-file read/write race" they had to hardened their test
  polling against). At the 300s production interval this is a narrow window,
  and this is a pre-existing structural property of the file-based engine
  (not something this gate's fenced `checklist_engine.py` scope permits fixing),
  but it is a *new* concurrent-writer this fix introduces into a file that
  previously only the child wrote to during a block. Recommend triaging a
  follow-up to confirm `checklist_engine.save()`'s write is safe under this
  new concurrency pattern (e.g., atomic rename, or a documented "last write
  wins, heartbeat-only fields aren't lost because X" argument) rather than
  leaving it implicit.
- The implementer's evidence section notes the full `tests/` directory (79
  files) times out at 2 minutes in this environment, pre-existing and
  unrelated to this diff. I did not attempt to run the full suite either,
  since the handoff's own Verification Commands and Stop Conditions scope
  the requirement to `tests/test_crew_launcher.py` specifically.
- I did not repeat the implementer's fresh-OS-process integration check
  (claim + manually age a lease + real subprocess dispatch + reconfirm
  non-stale); the handoff marks it optional for review confidence, and my
  independent sabotage-and-restore exercise against the actual wiring already
  gave me a stronger, more targeted signal that the fix (not merely the test
  code) is load-bearing.

## Workflow feedback
The handoff (both g1-implementer.md and g1-reviewer.md) was unusually
precise and load-bearing about the exact things that matter for a
threading/lease correctness change — the join-before-return rationale, the
explicit instruction to re-read `checklist_engine.heartbeat()`'s real source
rather than trust the implementer's restatement of it, and the instruction to
independently re-run rather than trust pasted output. All three of those
specific asks caught real, verifiable ground truth (not just well-argued
prose) when followed literally — I'd keep this level of specificity as the
template for future threading/concurrency gates. The one thing I'd add for
next time: an explicit invitation to do a "remove-the-fix-and-confirm-tests-fail"
sabotage pass, since that was the single highest-signal check I ran and it
wasn't explicitly requested by either handoff (I did it because "do any of
them pass vacuously" pushed me there) — making it a standard requested step
for concurrency-correctness reviews would surface it earlier and consistently.
