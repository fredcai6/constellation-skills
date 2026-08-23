# Implementer Handoff

## Gate
g1

## Task
In `scripts/run_crew.py`, make `_crew_door_env` explicitly CLEAR `SPINE_FILE` and
`SPINE_SESSION` when `spine` is `None`, instead of leaving the dispatching process's
ambient pair inherited. Update both affected docstrings. Flip/add/rewrite the tests named
below so the suite documents and enforces the new contract.

## Protected Intent
A crew dispatched without `--spine` must get NO door at all — it must never be able to
silently drive a spine it does not own (its dispatcher's). `decision:clear-both-or-neither`
is fixed: SPINE_FILE and SPINE_SESSION are cleared together, never one alone.

## Test Mode
Test-after allowed — behavior change to an existing, already-tested function; the test
surface (`tests/test_crew_launcher.py`) already exists and is being extended/corrected in
the same gate.

## Close Criteria
- `_crew_door_env`, when `spine is None`, returns an env with neither `SPINE_FILE` nor
  `SPINE_SESSION` present — even when the dispatching process's own ambient environment
  carries both (e.g. `os.environ["SPINE_FILE"]`/`SPINE_SESSION"]` set, as a door-bound
  Commander/Admiral would have).
- `_crew_door_env`'s docstring no longer asserts "the inherited-environment route is
  genuinely untouched... exactly as `crew_env()`'s own contract already promises" — that
  exact trailing clause is deleted and replaced with the new contract: no `spine` means NO
  door, both vars actively cleared.
- `crew_env`'s own docstring drops the parenthetical "(this is what lets the Admiral's own
  bootstrap, which passes `base_env` but no `--spine`, keep working)" and instead states
  that `crew_env`'s own generic "leave inherited when omitted" contract is unchanged, but
  `_crew_door_env` (the crew-dispatch door specifically) no longer relies on it for the
  `spine=None` branch — it actively clears there instead.
- `crew_env` itself is NOT changed (signature, body, or its own direct-caller contract) —
  the fix lives entirely inside `_crew_door_env`.
- `tests/test_crew_launcher.py::DispatchDoorBindingTests::test_dispatch_without_spine_leaves_ambient_pair_untouched`
  is renamed to `test_dispatch_without_spine_gets_no_door` and rewritten to assert
  `SPINE_FILE`/`SPINE_SESSION` are ABSENT from the dispatched child's env (currently it
  asserts they equal the ambient values — the exact old-behavior codification this gate
  overturns).
- `tests/test_crew_launcher.py::DispatchDoorBindingTests::test_dispatch_without_spine_binds_neither_var`'s
  comment (~line 1928) that names the old test by its exact string ("...see
  `test_dispatch_without_spine_leaves_ambient_pair_untouched`") is updated to name the
  renamed test.
- One new test added to `DispatchDoorBindingTests` exercising `CliBackend().resume(...)`
  (not just `launch_crew`/dispatch) with no stored spine on the registry entry: set REAL
  non-empty ambient `SPINE_FILE`/`SPINE_SESSION` first (mirror the flipped dispatch test's
  control shape — do NOT use the `no_ambient_spine_env()` helper to strip them first, since
  stripping-then-asserting-absent would be true both before and after this fix and prove
  nothing about active clearing), then assert both vars are absent from the resumed
  child's env.
- `ParentLeaseHeartbeatTests::test_dispatch_skips_parent_heartbeat_in_shared_spine_case`
  and `test_resume_skips_parent_heartbeat_in_shared_spine_case` (~lines 4525, 4578) are
  rewritten, not merely patched. Both currently dispatch/resume with `spine=None` from a
  door-bound parent and assert the child's env carries the SAME ambient pair as the parent,
  and that no parent-heartbeat thread starts (the "shared spine, skip redundant
  heartbeat" branch of `_parent_lease_heartbeat`). After this fix, a `spine=None` child's
  env can never equal the parent's non-empty ambient pair (it has neither key at all), so
  this "shared spine via spine=None" scenario becomes structurally impossible — and it was
  only ever reachable through the exact defect this gate removes (`assignment_session_name`
  always derives a 4-segment `constellation/<work_id>/<gate>/<role>` session for an
  explicit `--spine`, which can never equal a bare commander-shaped ambient session like
  `constellation/w/commander`; the old "shared" match existed only because `spine=None`
  copied the ambient pair verbatim). Rewrite both tests to assert the NEW correct behavior:
  a `spine=None` dispatch/resume from a door-bound parent now ALWAYS starts the parent
  heartbeat (never skips it), because the child gets no door at all and cannot maintain the
  parent's lease itself. Rename off `..._shared_spine_case` (e.g.
  `test_dispatch_heartbeats_parent_lease_when_spine_is_none` /
  `test_resume_heartbeats_parent_lease_when_spine_is_none`), update docstrings to state
  why, and flip the heartbeat-advanced / thread-liveness assertions to their opposite
  (heartbeat DOES advance past `before`; the heartbeat thread IS alive during the blocked
  call — check the existing `test_dispatch_heartbeats_parent_lease_when_child_pair_differs`
  test right below them, ~line 4626, for the exact assertion shape to mirror for the
  "heartbeats" case).
- Do NOT modify `_parent_lease_heartbeat` itself — its comparison logic is unchanged and
  still generically correct; only the concrete env values flowing into it changed as a
  consequence of the `_crew_door_env` fix.
- Full suite green: `python3 -m pytest -q` at the final commit.

## Allowed Scope
`scripts/run_crew.py` and `tests/test_crew_launcher.py` only — this lane's sole file
ownership this wave (three sibling lanes run concurrently against other files this wave).
The behavior change explicitly invalidates 3 existing test scenarios named above
(`test_dispatch_without_spine_leaves_ambient_pair_untouched`,
`test_dispatch_skips_parent_heartbeat_in_shared_spine_case`,
`test_resume_skips_parent_heartbeat_in_shared_spine_case`) — rewriting them is in scope
and expected, not a break to avoid.

## Specific Exclusions
- No change to `crew_env`'s signature or behavior.
- No change to `--spine`'s meaning, `SPINE_PARENT`, `CREW_SCRATCH_DIR`, or the registry
  schema (these float to the Admiral per the launch order; not this gate's to touch).
- No change to `_parent_lease_heartbeat`'s comparison logic.
- No file outside `scripts/run_crew.py` / `tests/test_crew_launcher.py`. If
  `tests/test_in_harness_crew_isolation.py` (which references `_crew_door_env` by name in
  a mock-patch target string, not by asserting its return value) breaks under the full
  suite run, stop and report rather than editing it — it is out of this gate's file
  ownership.

## Constraints
- Read/write files with `encoding="utf-8"` explicitly.
- Never `git checkout`/`git restore` a file with uncommitted peer work in the tree.
- A mutation battery/assertion must assert the specific named value, never a bare
  non-zero exit or exception.
- Test before committing — do not leave `run_crew.py` broken between commits (three
  sibling lanes run through it concurrently this wave).

## Map Anchors (inbound)
Map is DEGRADED-UNPARSEABLE (`.agent-work/w3-door/map-orientation.json`) — no citable
anchor exists for this symbol. Start directly from the code.
- **Map entry point:** `scripts/run_crew.py` lines 1260-1362 (`crew_env` at 1264,
  `_crew_door_env` at 1323) — read this range first; the two call sites are at ~1946 and
  ~2033 (`CliBackend.dispatch`/`resume`). `_parent_lease_heartbeat` (read-only reference for
  the heartbeat-test rewrite) is at ~1763-1822.
- **Decision anchors:** decision:clear-both-or-neither — clear SPINE_FILE and
  SPINE_SESSION together, never one alone.
  `@grade: settled/admiral · leans g1-implement`
- **Evidence expectations:** `python3 -m pytest -q` (full suite) green at the final commit.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore scripts/run_crew.py` exit 1
  (not ignored), verified 2026-08-22.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore tests/test_crew_launcher.py`
  exit 1 (not ignored), verified 2026-08-22.

## Required Evidence
- Load-bearing: `python3 -m pytest -q tests/test_crew_launcher.py` output (full, not a
  glance at the tail) showing the renamed/rewritten/new tests pass, and the full-suite
  `python3 -m pytest -q` output at the final commit.
- Load-bearing: the exact diff (`git diff`) of the docstring edits, so the reviewer can
  confirm the specific contradictory clauses named above are actually gone, not merely
  supplemented.
- Confirmatory: a real dispatched-child spot-check is expected at review/integrate, not
  required from you here — but if you want to self-verify, dispatching a throwaway
  `run_crew.py` invocation with no `--spine` from a shell with `SPINE_FILE`/`SPINE_SESSION`
  exported, and confirming those vars are absent from the child's actual process
  environment, is a good confirmatory check (not load-bearing for your own return).

## Wiring Grep
`_crew_door_env` is an existing, already-wired private helper (no new symbol added) —
this gate changes its body, not its shape. `none — no new callable symbol added; the two
existing call sites (~1946, ~2033) already exist and are unchanged.`

## Verification Commands
```bash
cd /home/tommy/projects/569-w3-door && python3 -m pytest -q tests/test_crew_launcher.py
cd /home/tommy/projects/569-w3-door && python3 -m pytest -q
```

## Suggested Model Tier
simple bounded — single function, single file pair, fully specified close criteria; sonnet
per launch order Budget (human ruling, latitude contract v2).

## Authority
The clear-both-or-neither shape, the file-ownership scope, and which 3 existing tests must
be rewritten (not just the one named in the mission) are already decided — do not
re-litigate them. How exactly to phrase the new docstring prose and exact test method
bodies is yours to decide within the close criteria above.

## Stop Conditions
Stop and return if: the allowed scope must be exceeded (e.g. `tests/test_in_harness_crew_isolation.py`
turns out to genuinely need an edit), a specific exclusion must be touched (e.g.
`_parent_lease_heartbeat`'s comparison logic turns out to need changing), required
evidence cannot be produced, or a caller is found that legitimately depends on the
inherited pair (the Honest-Null clause — report precisely and stop rather than break it).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback. Return status field lowercase (`complete | partial | blocked | out-of-scope |
failed`). Write the full IMPLEMENTER_RESULT to
`.agent-work/w3-door/crew-handoffs/g1-implement-result.md` before ending your turn.
