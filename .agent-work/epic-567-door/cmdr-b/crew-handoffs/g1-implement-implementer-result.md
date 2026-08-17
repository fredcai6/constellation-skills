# Implementation Result

## Assigned gate
`g1-implement` — close #432 on the ExternalBackend crew-dispatch path in `scripts/run_crew.py`

## Completed slice
`ExternalBackend.dispatch()` now accepts `--spine` (verification-only, never bound); `ExternalBackend.verify()` is a new override that default-refuses when no spine evidence and no explicit accepted risk exist, replacing the old mtime-only clean pass; two new CLI flags (`--verify-spine`, `--accept-mtime-only-risk`) give a caller a terminal-spine check or a loud, reasoned, recorded escape hatch back to the old behavior.

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `tests/test_crew_launcher.py`

**Specific exclusions touched:** no — `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` untouched; `spine_terminal` reused read-only as directed.

## Behavior changed
yes — an externally-dispatched crew that wrote only a fresh result artifact and drove no spine now REFUSES `--verify-result` by default (exit 1), where it previously returned 0/`completed`. The old behavior is still reachable via `--accept-mtime-only-risk "<reason>"`, printed loudly to both stdout and stderr, and recorded on the entry.

## Map Impact
No `docs/architecture` map exists in this repo (confirmed DEGRADED at `context`, per the handoff's Map Anchors), so there is no map to reconcile against. Noted here per the handoff's own anchor list, using its vocabulary, for whoever eventually builds the map:

- **Structural anchors touched:** `scripts/run_crew.py:ExternalBackend.dispatch` (~L1676, spine refusal removed, new handoff=None guard added), `scripts/run_crew.py:ExternalBackend.verify` (~L1740, NEW override), `scripts/run_crew.py:CrewBackend.verify` (~L1475, read-only, unchanged as directed), `scripts/run_crew.py:verify_external_result` (~L1974, new optional kwargs, back-compat), `scripts/run_crew.py:main`/`build_parser` (~L2093-2183, two new CLI flags + new REFUSED message branch).
- **Capabilities added/changed/affected:** external-backend dispatch can now record a verification-only `--spine`; `--verify-result` can independently check a verify-time `--verify-spine` or accept an explicit `--accept-mtime-only-risk`.
- **Constraints/assumptions touched:** `docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2 ("the result contract is backend-invariant ... never forked") is intentionally NARROWED for `ExternalBackend` only — the base `result_exists`/`result_fresh` exists-AND-fresh contract stays byte-for-byte shared and unforked (proven in the rewritten `BackendInvariantContractTests` step (a)/(b)); the new spine-evidence dimension is an ADDITIONAL gate layered on top of `ExternalBackend` alone, not a fork of the base contract. `CliBackend` is completely unaffected (it never calls `.verify()` in production — confirmed by grep, see Wiring Grep below).
- **Decision candidates / resolved decisions:** all six decision anchors named in MISSION_FRAME.md's "Decision Anchors & Decision Pressure" now have red/green proofs behind them from this gate (default-refuse polarity, verify-time `--verify-spine` precedence over dispatch-time `spine`, AND semantics never OR/rescue, `ExternalBackend`-only override scope) — Commander should regrade these `settled/measured` against this run's evidence.
- **Trust limitations / drift found:** none found beyond the pre-existing DEGRADED map state.
- **Triage candidates:** none identified beyond what's already in MISSION_FRAME.md.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — every new/changed assertion in the Close Criteria was proven red against the shipped `RC.main`/`RC.CrewBackend`/`RC.ExternalBackend` entrypoints before being proven green, per `decision:the-check-must-be-able-to-fail` / `decision:test-the-shipped-path`.

## Evidence

### 1. `dispatch()` accepts `--spine` — `test_external_dispatch_refuses_spine` rewritten

RED (against pre-fix `ExternalBackend.dispatch()`, which still refused `--spine`):
```
$ python -m pytest tests/test_crew_launcher.py -k test_external_dispatch_refuses_spine -q
F                                                                        [100%]
...
>           self.assertEqual(0, code)
E           AssertionError: 0 != 1
...
Captured stderr call:
REFUSED: refusing --spine '.agent-work/issue-1/IMPLEMENTER_PLAN.json' on the external backend: ...
1 failed, 211 deselected in 0.10s
```

GREEN (after removing the refusal block):
```
$ python -m pytest tests/test_crew_launcher.py -k test_external_dispatch_refuses_spine -q
.                                                                        [100%]
1 passed, 211 deselected in 0.04s
```

### 2. Core fix — default-refuse — `test_verify_result_absent_then_present_marks_completed` rewritten

RED (against pre-fix `verify()`, which still returned 0/`completed` on a fresh result with no spine evidence — this IS the #432 bug):
```
$ python -m pytest tests/test_crew_launcher.py -k test_verify_result_absent_then_present_marks_completed -q
F                                                                        [100%]
...
>           self.assertEqual(1, code_present)
E           AssertionError: 1 != 0
...
Captured stderr call:
WARNING: external-backend crew '...' has an UNBOUND MCP door ...
REFUSED: result artifact absent: ... (left running)
1 failed, 211 deselected in 0.10s
```
(The `Captured stderr call` block above is from the FIRST `--verify-result` call in the test, made before the result artifact exists — the test's own local `stderr` capture around the SECOND call, the one that matters, is a separate `io.StringIO()` pytest does not echo. The load-bearing line is the assertion diff itself: `AssertionError: 1 != 0` on `code_present` — the rewritten test expects `1` (REFUSE); pre-fix code actually returned `0` for that second call, i.e. `completed`, confirming the #432 bug.)

GREEN (after adding `ExternalBackend.verify()` override):
```
$ python -m pytest tests/test_crew_launcher.py -k test_verify_result_absent_then_present_marks_completed -q
.                                                                        [100%]
1 passed, 211 deselected in 0.04s
```

### 3. Named-spine evidence paths (`test_verify_named_spine_not_terminal_refuses`, `test_verify_named_spine_terminal_completes`)

The not-terminal test embeds a genuine (not simulated) red-proof: it calls `RC.CrewBackend().verify(...)` directly on the exact not-terminal-spine + fresh-result fixture — `CrewBackend.verify` is the literal pre-fix logic, untouched by this gate — and asserts it WRONGLY returns `fresh=True`/`status=completed`, before asserting `RC.ExternalBackend().verify(...)` on the same fixture correctly refuses, and finally that the real `RC.main` CLI path also refuses.

```
$ python -m pytest tests/test_crew_launcher.py -k "test_verify_named_spine_not_terminal_refuses or test_verify_named_spine_terminal_completes" -q
..                                                                       [100%]
2 passed, 212 deselected in 0.07s
```

### 4. CLI wiring — verify-time override, accepted risk, spine-only no-crash

```
$ python -m pytest tests/test_crew_launcher.py -k "test_verify_time_spine_override_completes or test_verify_accept_mtime_only_risk_completes or test_verify_spine_only_external_dispatch_no_crash" -q
...                                                                      [100%]
3 passed, 214 deselected in 0.07s
```

Crash-prevention evidence (the guard `ExternalBackend.verify()` relies on):
```
$ python3 -c "
entry = {'result': None, 'started_at': '2026-01-01T00:00:00Z'}  # no 'spine' key at all
try:
    spine = entry['spine']
    print('bracket access returned:', spine)
except KeyError as e:
    print('bracket access CRASHES: KeyError:', e)
spine = entry.get('spine')
print('.get access returns safely:', spine)
"
bracket access CRASHES: KeyError: 'spine'
.get access returns safely: None

$ python3 -c "
import sys; sys.path.insert(0, 'scripts'); import run_crew as RC
from pathlib import Path
try:
    RC.result_exists(None, Path('.'))
    print('no crash (unexpected)')
except TypeError as e:
    print('result_exists(None, root) CRASHES: TypeError:', e)
"
result_exists(None, root) CRASHES: TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'
```

### 5. Rewritten backend-invariant tests

```
$ python -m pytest tests/test_crew_launcher.py -k "test_verify_is_uniform_across_backends or test_both_backends_verify_exists_and_fresh_identically" -q
..                                                                       [100%]
2 passed, 215 deselected in 0.07s
```

### 6. Full suite

```
$ python -m pytest tests/test_crew_launcher.py -q
........................................................................ [ 33%]
........................................................................ [ 66%]
........................................................................ [ 99%]
.                                                                        [100%]
217 passed in 0.77s
```

**Result:** all pass.

## TDD evidence, if required

- Failing test observed: yes, three times — see Evidence sections 1 and 2 above (sections 3-5 build directly on the now-green override, so their "pre-fix" comparison is against `CrewBackend.verify`, the literal unchanged base-class logic, embedded as an in-test assertion rather than a separate command run).
- Passing test observed: yes — see Evidence sections 1-6 above.
- Refactor while green: no separate refactor pass was needed; the implementation was written directly to the final shape.

## Docs/contracts touched
- none — `docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2 is referenced and intentionally narrowed in behavior (see Map Impact), but the doc file itself was not edited (out of this gate's `Allowed Scope`); flagging this as a triage candidate below.

## Assumptions
- `--spine`'s CLI help text and the `ExternalBackend` class docstring were rewritten to describe the new verification-only acceptance; the unconditional "UNBOUND MCP door" banner text was left unchanged because it never claimed `--spine` was refused — it only ever said nothing binds `SPINE_FILE`/`SPINE_SESSION`, which stays true (spine is recorded, never bound).
- The `main()` REFUSED-message split (`result_deficient` gate) is an implementation detail not explicitly spelled out in the handoff's pseudocode; I derived it to satisfy the handoff's "checked BEFORE falling back to those" instruction for the NEW cases while keeping the pre-existing STALE/absent tests (`test_verify_result_stale_refuses_and_leaves_running`, `test_verify_result_missing_refuses_with_absent_message` — neither named as an intentional rewrite) green, since a genuinely deficient result artifact is a more specific and direct cause than "no spine evidence" when both are true. Both untouched tests still pass unchanged (see the full-suite run above; 217 passed with no scenario changes to them).

## Stop conditions hit
- none — no edit was needed inside `checklist_engine.py` or `mcp_spine_server.py`; the design built cleanly against `spine_terminal`'s actual contract; no existing test other than the four named below needed a scenario change.

## Out-of-scope observations
- Fixed a genuine regression I introduced and then corrected within this same gate, not left for triage: removing `ExternalBackend.dispatch()`'s old `--spine` refusal exposed a latent crash — `_require_handoff(spec.handoff, ...)` calls `Path(handoff)` with no `None` guard, and it was previously unreachable with `handoff=None` only because the old spine-refusal check always fired first whenever `spine` was given alongside `handoff=None`. Added an explicit `if spec.handoff is None: raise CrewLaunchError(...)` guard in `ExternalBackend.dispatch()` before the `_require_handoff` call, restoring `test_external_backend_refuses_spine_only_with_no_handoff`'s original passing scenario and message contract (that test's assertions were NOT changed — only the crash under it was fixed). This is in-scope (`scripts/run_crew.py`) and necessary for full-suite green, not a separate finding, but noted here for visibility since it was not explicitly anticipated in the handoff's three-change list.
- `docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2's prose ("never forked") is now stale relative to code — the doc itself needs an update to record the `ExternalBackend`-only narrowing this gate introduces. Out of this gate's `Allowed Scope` (only `scripts/run_crew.py` and `tests/test_crew_launcher.py`); flagging for Commander/Triage.

## Wiring Grep
```
$ grep -rn "spine_verified\|verify_spine\|accept_mtime_only_risk\|mtime_only_risk_accepted" scripts/run_crew.py tests/test_crew_launcher.py
```
Counts by symbol:
- `spine_verified`: 4 production sites in `scripts/run_crew.py` (3 writes — L1803, L1806, L1822; 1 read — L2156) vs. 7 test assertion sites in `tests/test_crew_launcher.py`.
- `verify_spine` (parameter/kwarg name): 7 production sites (def params, usage, CLI `dest=`, kwarg threading) vs. 0 test sites matching this exact underscored token — tests invoke it only via the hyphenated CLI flag `--verify-spine`, which this grep pattern (by design, per the handoff's literal string) does not match.
- `accept_mtime_only_risk` (parameter/kwarg name): 8 production sites vs. 3 test sites using the underscored kwarg directly (`test_verify_is_uniform_across_backends`, `BackendInvariantContractTests`); the CLI-flag callers (`test_verify_accept_mtime_only_risk_completes`) similarly use the hyphenated `--accept-mtime-only-risk` string, not matched here.
- `mtime_only_risk_accepted` (the recorded evidence dict key): 1 production write site (L1807) vs. 1 test assertion site (L2417, checking the recorded `reason`).

## Intentional test-scenario changes (not just assertion tweaks)
1. `test_external_dispatch_refuses_spine` — was: asserts `--spine` is REFUSED on the external backend. Now: asserts `--spine` is ACCEPTED and RECORDED (still never bound). Reason: change 1 of the handoff — `--spine` becomes verification-only on this backend.
2. `test_verify_result_absent_then_present_marks_completed` — was: final assertion `code_present == 0` (completed on a fresh result alone). Now: `code_present == 1` (REFUSE). Reason: the #432 core fix — a crew that drove no spine at all must not read as an unqualified clean success by default. This is the single most important test change in this gate.
3. `test_verify_is_uniform_across_backends` — was: asserts `CliBackend().verify()` and `ExternalBackend().verify()` behave identically on a fresh result with no spine evidence. Now: asserts `CliBackend` is unchanged, `ExternalBackend` default-refuses the same fresh result, and the old behavior is reachable via `accept_mtime_only_risk`. Reason: intentional narrowing of Decision 2 for `ExternalBackend`'s new spine-evidence dimension only.
4. `BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically` — was: a single shared per-backend loop asserting identical `completed` on a fresh result for both backends. Now: steps (a)/(b) (missing/stale) stay in the shared loop unchanged; step (c) (fresh) splits per backend, with `ExternalBackend` asserted to default-refuse and then to complete via the explicit override. Reason: same as #3 — the base contract stays shared, only the fresh-result verdict diverges for `ExternalBackend`.

No other existing test's scenario was changed. `test_external_backend_refuses_spine_only_with_no_handoff` kept its original scenario and assertions unchanged (see Out-of-scope observations for the crash-regression fix that kept it passing).

## Workflow Feedback

- **Handoff gaps:** the handoff's pseudocode for `main()`'s new REFUSED message (Close Criteria, change 3) didn't address how to keep the pre-existing STALE/absent-result tests (`test_verify_result_stale_refuses_and_leaves_running`, `test_verify_result_missing_refuses_with_absent_message`) green when `spine_verified` is `False` for those same entries (they also have no spine evidence). I resolved it by gating the new message on the result artifact itself being non-deficient (present AND fresh, or not required at all) — documented as an Assumption above — but a worked example distinguishing "result deficient" from "spine deficient" priority would have saved a design pass.
- **Context rediscovered:** none beyond the ordinary reading of `finalize_from_exit_code`'s OR/rescue precedent and `spine_terminal`'s docstring, both already named in Map Anchors.
- **Instructions improvised around:** the handoff scoped CLI wiring (change 3) as conceptually separate work, but m2's own red/green proof (`test_verify_result_absent_then_present_marks_completed`) needed the new REFUSED-message wording (containing "432") to assert against, which only exists once the CLI wiring is in place. I built the CLI flags/message logic during the "core fix" implementation step rather than deferring it to a later step, and treated the later "CLI wiring" step as tests-plus-crash-repro on top of already-working code. Named explicitly here since a reviewer diffing step-by-step commits (there are none — this was one continuous session) might otherwise expect the wiring to appear only in a later, separate change.
- **What would have made this easier:** none otherwise — the handoff's verdict-logic pseudocode was unusually precise and translated almost directly into code.

## Return status
`complete`
