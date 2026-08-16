Return status: complete

# IMPLEMENTER_RESULT — g1 (issue #607)

## Completed slice
Added a background parent-lease heartbeat to `scripts/run_crew.py`, exactly as
specified in the handoff's Authority section (no re-derivation):

- `PARENT_HEARTBEAT_INTERVAL_SECONDS = 300` (module constant, placed directly
  after `HEARTBEAT_STALE_SECONDS` at the top of the file, with a comment
  distinguishing the two axes — registry-entry heartbeat window vs.
  engine-lease heartbeat cadence).
- `_parent_lease_heartbeat(interval: float | None = None)` — a
  `@contextlib.contextmanager` helper:
  - Reads the dispatching process's own ambient `os.environ.get("SPINE_FILE")`
    / `os.environ.get("SPINE_SESSION")` (never the child's derived env).
  - No-ops (no thread started) if either is unset.
  - If both are set, starts a daemon `threading.Thread` named
    `run_crew-parent-lease-heartbeat` that, every `interval` seconds (default
    the module constant, read at call time so tests can monkeypatch it), calls
    `checklist_engine.load(Path(spine_file))` →
    `checklist_engine.heartbeat(cl, spine_session)` →
    `checklist_engine.save(Path(spine_file), cl)`. Uses `threading.Event.wait`
    for the sleep so `stop_event.set()` wakes it immediately.
  - Any exception during a beat is caught and swallowed (retries next tick);
    never propagates.
  - No self-collision guard, per Authority — `checklist_engine.heartbeat()`'s
    own ownership check makes heartbeating with the child's inherited-same
    pair safe.
  - `finally: stop_event.set(); thread.join()` — thread is always stopped and
    joined before the context exits, i.e. before the caller's next mutating
    call against the same spine file.
- Wired around the single blocking `launch(...)` call in both
  `CliBackend.dispatch` (was `run_crew.py:1392`, now wrapped at the
  post-edit line ~1472) and `CliBackend.resume` (was `:1451`, now wrapped at
  ~1532) — nothing else in either method changed.

## Files changed
- `scripts/run_crew.py` — the two additions above (constant + helper) plus
  the two `with _parent_lease_heartbeat():` wraps at the existing `launch(...)`
  call sites. `git check-ignore -v scripts/run_crew.py` → exit 1 (not ignored).
- `tests/test_crew_launcher.py` — one new class, `ParentLeaseHeartbeatTests`
  (7 tests), appended before the `if __name__ == "__main__":` guard, reusing
  `no_ambient_spine_env()` and the file's existing conventions (flat
  `unittest.TestCase`, tempdir-scoped fixtures, a real `checklist_engine`
  spine built through `claim()` rather than a hand-rolled dict).
  `git check-ignore -v tests/test_crew_launcher.py` → exit 1 (not ignored).

No other file was touched. `scripts/recover_crews.py` was checked, not
edited: `grep -n "checklist_engine\|engine_session\|SPINE_FILE\|SPINE_SESSION\|last_heartbeat" scripts/recover_crews.py`
returns nothing — it is confirmed to be a pure read-side classifier over
`crew-runs.json` with zero engine-lease awareness, exactly as the handoff
predicted. `scripts/checklist_engine.py` was not touched; only its existing
`load`/`heartbeat`/`save` were called. `process_alive`, `entry_liveness`, and
`active_duplicate` are untouched (verified: `git diff scripts/run_crew.py`
contains no reference to any of the three).

## Test mode satisfied
TDD followed: the new `ParentLeaseHeartbeatTests` class was written to drive
the helper before/alongside wiring it into `dispatch`/`resume`, in the same
file, following its conventions (flat `TestCase`, `RC`/`REC` aliases,
`fake_launch`/`no_ambient_spine_env` reused where their shape fit; a small
`slow_launch` local double was written for the two timing-sensitive
integration tests since the shared `fake_launch` never blocks and this gate's
whole point is behavior *during* a block — documented inline).

## Evidence produced

### Required evidence (a)-(e), all in `ParentLeaseHeartbeatTests`
- (a) `test_noop_when_ambient_vars_unset`, `test_noop_when_only_one_ambient_var_set`
- (b) `test_thread_advances_last_heartbeat_while_active`
- (c) `test_thread_is_joined_before_context_manager_returns`
- (d) `test_heartbeat_exception_is_swallowed_not_propagated`
- (e) `test_dispatch_heartbeats_ambient_lease_in_shared_spine_case` (dispatch,
  `spine=None` → child inherits the parent's own ambient pair unchanged —
  asserted directly against the launch double's observed `env`) and
  `test_resume_heartbeats_ambient_lease_in_shared_spine_case` (same coverage
  for `CliBackend.resume`, the second wired call site).

All 7 new tests were run individually 5x in a row with no flakes (real-time
polling via a `_wait_until` helper, not fixed sleeps, guards against
CI-speed flakiness; one transient same-file read/write race between the test's
own poll and the heartbeat thread's non-atomic `checklist_engine.save` was
caught and hardened by treating a transient `JSONDecodeError`/`OSError` in the
poll predicate as "not yet" rather than a failure).

### Wiring grep (handoff's own command)
```
$ grep -rn "_parent_lease_heartbeat\|PARENT_HEARTBEAT_INTERVAL_SECONDS" --include=*.py . | grep -v "def _parent_lease_heartbeat" | grep -v "^\./tests/"
./scripts/run_crew.py:72:PARENT_HEARTBEAT_INTERVAL_SECONDS = 300
./scripts/run_crew.py:1307:# The thread `_parent_lease_heartbeat` starts is named so tests can assert its
./scripts/run_crew.py:1327:    thread every `interval` seconds (default `PARENT_HEARTBEAT_INTERVAL_SECONDS`)
./scripts/run_crew.py:1349:    effective_interval = PARENT_HEARTBEAT_INTERVAL_SECONDS if interval is None else interval
./scripts/run_crew.py:1472:        with _parent_lease_heartbeat():
./scripts/run_crew.py:1532:        with _parent_lease_heartbeat():
```
Of these, exactly **2** are actual call sites (`:1472` in `dispatch`, `:1532`
in `resume`); the rest are the constant definition, a docstring reference, and
the interval-default lookup line. This matches the handoff's expected count.

### Full mechanical distribution (handoff's own command, verbatim output)
```
$ find . -name __pycache__ -exec rm -rf {} +
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
........................................................................ [ 38%]
........................................................................ [ 76%]
............................................                             [100%]
188 passed in 0.77s
```
(188 = 181 pre-existing + 7 new; all pass.)

### Fresh-process integration check
Performed as real, separate OS processes (not reasoned about from inside this
agent's own Python process): the real `checklist_engine.py` CLI to claim +
manually age a lease, then a real `run_crew.py` dispatch run as its own
`py driver.py` subprocess (with only `launch_process` monkeypatched inside
that fresh process, since no real `claude` CLI exists in this environment —
per the handoff's own suggested "monkeypatched or trivially-fast launch"),
then the real CLI again to confirm the result.

1. Built a scratch spine and claimed a lease as the parent's own identity:
```
$ py checklist_engine.py --file /tmp/g1-integration/spine.json claim \
    --session-id constellation/g1-integration/commander --claimed-by commander --worktree .
claimed lease constellation/g1-integration/commander -> active
```
2. Manually aged `engine_session.last_heartbeat` to `now - 2000s` (> the
   engine's 1800s `DEFAULT_LEASE_STALE_SECONDS`) directly in the JSON.
3. Baseline proof the aged lease really does read stale (on a disposable copy,
   different claimant, no `--force`):
```
$ py checklist_engine.py --file spine_baseline_copy.json claim \
    --session-id constellation/g1-integration/prober-baseline --claimed-by prober --worktree .
reclaimed stale lease constellation/g1-integration/commander; constellation/g1-integration/prober-baseline -> active
```
4. Ran a real blocking `run_crew.py` dispatch as a fresh process, with
   `SPINE_FILE`/`SPINE_SESSION` bound to the ORIGINAL (still-aged) spine and
   `PARENT_HEARTBEAT_INTERVAL_SECONDS` set to 0.3s inside that fresh process,
   `launch_process` replaced with a double that blocks 1.5s (>2 heartbeat
   ticks) before returning 0:
```
$ env SPINE_FILE=/tmp/g1-integration/spine.json SPINE_SESSION=constellation/g1-integration/commander \
    py /tmp/g1-integration/driver.py
crew constellation/g1-integration/g1/implementer/attempt-1 -> completed
run_crew.py dispatch exit code: 0
```
   `last_heartbeat` before: `2026-08-16T15:13:47.740305+00:00` (the aged
   value) → after: `2026-08-16T15:47:27.323958+00:00` (fresh, advanced during
   the block).
5. Confirmed `current`/`claim` on the REAL spine no longer read the lease as
   stale afterward (same probe as step 3, now against the real,
   heartbeat-refreshed spine):
```
$ py checklist_engine.py --file spine.json current
LEASE active: constellation/g1-integration/commander (by commander, heartbeat 2026-08-16T15:47:27.323958+00:00)
DONE: no open items.

$ py checklist_engine.py --file spine.json claim \
    --session-id constellation/g1-integration/prober-after --claimed-by prober --worktree .
REFUSED: checklist already owned by active session 'constellation/g1-integration/commander'; use `claim --force --reason ...` to take over
exit code: 1
```
   Contrast with step 3's disposable-copy result (`reclaimed stale lease`,
   exit 0) — the SAME staleness probe now REFUSES, proving the fix. Scratch
   files removed after the check (`rm -rf /tmp/g1-integration`).

## Assumptions used
- `_parent_lease_heartbeat`'s `interval` keyword resolves the module constant
  at CALL time (`PARENT_HEARTBEAT_INTERVAL_SECONDS if interval is None else
  interval`), not at function-definition time, so tests can either pass an
  explicit small interval directly OR monkeypatch the module constant before
  calling `dispatch`/`resume` (which don't themselves take an interval
  parameter — only the helper does, per the handoff's literal wording "a
  keyword parameter with the module constant as default"). This was the
  natural reading that also keeps `dispatch`/`resume`'s signatures unchanged.
- The heartbeat thread is named (`run_crew-parent-lease-heartbeat`) purely so
  tests can assert liveness/absence via `threading.enumerate()` without the
  context manager needing to yield a handle; this is test-observability
  surface only, not a behavior change.
- "Started around the single blocking launch(...) call" was read narrowly:
  only the `exit_code = launch(...)` statement itself is inside the `with`
  block in both methods — nothing before or after it (argv/env construction,
  `finalize_from_exit_code`, `save_registry`) moved.

## Stop conditions hit
None. Scope was not exceeded, `checklist_engine.py` was not touched, all
required evidence was produced, and the specified mechanism (parent-self
heartbeat, no self-collision guard, direct module calls, 300s default,
join-before-return) worked as designed with no unanticipated obstruction.

## Out-of-scope observations
- Running the FULL `tests/` directory (`py -m pytest -q tests/`, 79 files) hit
  a 2-minute timeout in this environment; `tests/test_crew_launcher.py` alone
  (the file this gate owns, and the only one the handoff's Verification
  Commands name) consistently passes in well under 1 second, both before and
  after this change, so the slow/hanging behavior is pre-existing elsewhere in
  the suite and unrelated to this diff. Not investigated further — out of this
  gate's allowed scope.
- `checklist_engine.py`'s CLI prints an unrelated `RAIL: ...` advisory line to
  stdout/stderr on every `claim`/`current` invocation in this installed
  environment (a hook, not part of the engine itself). It appeared
  identically regardless of pass/fail during the integration check and did
  not affect exit codes or JSON state; noted here only so it isn't mistaken
  for a real error if this evidence is re-read later.

## Workflow feedback
The handoff was unusually complete and load-bearing-precise (exact line
numbers, exact ordering requirement for join-before-return, exact rationale
for why the no-self-collision-guard decision was already settled) — there was
no point at which the Authority section's "do not re-derive" actually had to
be tested against an unanticipated obstacle. The one genuine design decision
left open by the handoff (how "interval is injectable" should thread through
`_parent_lease_heartbeat` vs. `dispatch`/`resume`'s own signatures) had a
single natural reading once `PARENT_HEARTBEAT_INTERVAL_SECONDS` was confirmed
mutable in tests; worth stating explicitly in a future handoff of this shape
if a different resolution is intended.
