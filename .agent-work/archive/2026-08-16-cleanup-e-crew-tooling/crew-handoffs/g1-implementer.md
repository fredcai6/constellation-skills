# Implementer Handoff

## Gate
g1 (issue #607)

## Task
`scripts/run_crew.py` blocks foreground while a dispatched crew runs, and issues no mutating engine verb during that block, so a healthy parent's own engine-session lease can go stale purely from being blocked (measured: 53 minutes blocked, engine already read the lease stale). Add a background heartbeat that keeps the *dispatching* process's own ambient lease alive for exactly the duration of the block, with zero change to `checklist_engine.py`.

## Protected Intent
A live, blocked-but-healthy parent must never read as lease-stale to an external liveness reader while its child crew is genuinely still running. Never mark anything `abandoned`, expire a lease, or force-claim — this gate reports/prevents staleness, it does not reap.

## Test Mode
TDD required. `tests/test_crew_launcher.py` has full coverage of `run_crew.py`'s existing dispatch/resume paths (flat `unittest.TestCase` per concern) — new behavior gets new tests in the same file, following its conventions, before or alongside the implementation.

## Close Criteria
- A new constant `PARENT_HEARTBEAT_INTERVAL_SECONDS = 300` (module-level, near `HEARTBEAT_STALE_SECONDS` at `run_crew.py:59` but not confused with it — that constant is the *registry-entry* heartbeat window; this new one is the *engine-lease* heartbeat cadence, well under `checklist_engine.py`'s `DEFAULT_LEASE_STALE_SECONDS = 1800`).
- A context-managed helper (e.g. `_parent_lease_heartbeat()`), started around the single blocking `launch(...)` call in **both** `CliBackend.dispatch` (`:1357`, call at `:1392`) and `CliBackend.resume` (`:1403`, call at `:1451`):
  - Reads the **dispatching process's own** ambient `os.environ.get("SPINE_FILE")` / `os.environ.get("SPINE_SESSION")` — never the child's derived env from `_crew_door_env`/`crew_env`.
  - If either is unset (the common case for a top-level or non-nested dispatch): **no-op**. No thread starts, nothing else changes.
  - If both are set: start a daemon `threading.Thread` that, every `PARENT_HEARTBEAT_INTERVAL_SECONDS`, calls `checklist_engine.load(Path(spine_file))` → `checklist_engine.heartbeat(cl, spine_session)` → `checklist_engine.save(Path(spine_file), cl)` (module already imported at `run_crew.py:43`; no subprocess/CLI round-trip). Use a `threading.Event` for the sleep so the thread wakes immediately on stop rather than waiting out a full interval.
  - **No self-collision guard.** Do not special-case a child whose env happens to carry the same `SPINE_FILE`/`SPINE_SESSION` as the parent — per `crew_env()`'s own documented contract, a handoff-only dispatch with no `--spine` given *inherits* the dispatcher's ambient values unchanged, so that is the common case, not an edge case, and guarding it off would silently disable the fix where it matters most. `checklist_engine.heartbeat()` already refuses a `session_id` that doesn't own the lease, so this is safe.
  - Any exception raised while heartbeating (missing file, refused by the engine, anything) is caught and swallowed — it must never propagate into or abort the blocking dispatch. A heartbeat failure is not a dispatch failure.
  - `stop_event.set()` + `thread.join()` happens in a `finally` around the blocking call, **before** control returns to the caller — this ordering is load-bearing: it prevents the heartbeat thread racing the next mutating call the caller (`finalize_from_exit_code`, `save_registry`) issues against the same file immediately after.
- Interval is injectable (a keyword parameter with the module constant as default) so tests don't sleep 300 real seconds.

## Allowed Scope
`scripts/run_crew.py` (the heartbeat helper + its two call sites), `tests/test_crew_launcher.py` (new tests). `scripts/recover_crews.py` may be touched only if you find it genuinely needs a change for this gate (expected: no change needed — it is a pure read-side classifier over `crew-runs.json` and does not read engine-lease state at all; confirm this rather than assuming it).

## Specific Exclusions
- `scripts/checklist_engine.py` — fenced, do not touch. Call its existing public `load`/`heartbeat`/`save` functions; do not add new ones there or change `_is_stale`/`require_session`.
- `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`, `scripts/install_constellation.py`, `skills/commander/templates/**` — fenced, unrelated to this gate.
- No reaping, expiry, or force-claim of any lease or registry entry.
- Do not touch `process_alive`, `entry_liveness`, or `active_duplicate` — #599's registry-entry liveness logic is correct and unrelated to this gate's engine-lease heartbeat.

## Constraints
- `os.kill(pid, 0)` is POSIX-only; `process_alive`'s existing cross-platform seam must not change (you are not touching it, but do not introduce a new POSIX-only dependency into the new code either — `threading` is stdlib, cross-platform, fine).
- Clear `__pycache__` before every measurement: `find . -name __pycache__ -exec rm -rf {} +`.
- Every ambiguity resolves toward "this thing is running" (fail-toward-alive) — e.g. if unsure whether to start the thread, default to starting it when the ambient vars are present.

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:846-887` `launch_process` (the seam being wrapped, not modified); `scripts/run_crew.py:1357` `CliBackend.dispatch`, `:1403` `CliBackend.resume` (the two call sites); `scripts/run_crew.py:59` `HEARTBEAT_STALE_SECONDS=28800` (a different, unrelated constant — do not confuse).
- **Capability:** crew dispatch — a Commander parent blocking on `run_crew.py` while a child crew runs.
- **Constraints/assumptions:** decision `no-reaping` — nothing marks an entry/lease abandoned, expires it, or force-claims anything; decision `fail-toward-alive` — ambiguity resolves toward alive, never dead.
- **Decision anchors:**
  decision `registry-before-staleness` — tried first; staleness is judged entirely inside fenced `checklist_engine.py`, which no owned file reads today, so this direction has no seam without touching the fence. This is also fix direction 1 named explicitly in GitHub issue #607 itself ("heartbeat from the launcher rather than from the engine's mutating verbs"), not an invented mechanism.
  `@grade: guess · leans g1-implement · settle: tried; floating the parent-self-heartbeat alternative per the pre-ruling's own settle clause`
- **Evidence expectations:** a real `checklist_engine.py`-backed spine with a lease claimed, its `last_heartbeat` artificially aged past 1800s, then a real blocking `run_crew.py` dispatch (interval monkeypatched small) — assert `current`/`claim` no longer reads stale afterward. Plus the no-ambient-vars honest-null case, and the shared-spine (no explicit `--spine`) case.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; verified via `git check-ignore -v scripts/run_crew.py` exiting 1 (not ignored).
- **Committed** — `tests/test_crew_launcher.py`; verified via `git check-ignore -v tests/test_crew_launcher.py` exiting 1 (not ignored).

## Required Evidence
- New test class(es) in `tests/test_crew_launcher.py` covering: (a) no-op when ambient vars unset, (b) thread starts and advances `last_heartbeat` when ambient vars are set, (c) thread stops (joined) before the blocking call's caller returns, (d) a heartbeat exception does not propagate/abort the dispatch, (e) the shared-spine case (no explicit `--spine`, child inherits parent's ambient vars) still heartbeats — this is the case a first draft's now-removed self-collision guard would have silently broken.
- Full mechanical distribution: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py` output pasted verbatim, with pass count.
- One fresh-process integration check per the launch order's Return Shape: a real `checklist_engine.py` spine with a lease claimed and heartbeat aged past staleness, then a real blocking dispatch through `run_crew.py`'s CLI (not reasoned about from inside this handoff's own process), confirming the lease reads non-stale afterward.

## Wiring Grep
```bash
grep -rn "_parent_lease_heartbeat\|PARENT_HEARTBEAT_INTERVAL_SECONDS" --include=*.py . | grep -v "def _parent_lease_heartbeat" | grep -v "^\./tests/"
```
State the count of call sites found outside the definition and outside the test file (expect exactly 2: the `dispatch` and `resume` call sites in `CliBackend`).

## Verification Commands
```bash
find . -name __pycache__ -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
```

## Suggested Model Tier
stronger — threading/concurrency correctness (join ordering, exception swallowing, interval injection) has real failure modes that reward careful reasoning over speed.

## Authority
The mechanism (parent-self-heartbeat, no self-collision guard, direct `checklist_engine` module calls, 300s interval, join-before-return ordering) is already decided — implement it as specified above, do not re-derive or substitute a different mechanism (e.g. do not shell out to the CLI, do not add a registry-consultation path in `checklist_engine.py`). If the specified approach turns out to be unworkable for a reason not anticipated here, stop and report rather than silently substituting.

## Stop Conditions
Stop and return if: the allowed scope must be exceeded, `scripts/checklist_engine.py` must be touched to make this work, required evidence cannot be produced, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

**Delivery.** Write the full IMPLEMENTER_RESULT to `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-implementer-result.md` before ending your turn.
