# Implementation Result

## Assigned gate
`g1-implement` (issue #599)

## Completed slice
Replaced `active_duplicate()`'s raw status-string check with a corroborated three-state liveness query. Added `entry_liveness(entry, now, alive=None) -> str` (three-bucket rule: pid-liveness / external-backend heartbeat-age / uncorroborated-legacy-unknown), added the documented `HEARTBEAT_STALE_SECONDS = 28800` constant, and wired both into `active_duplicate` via new keyword-only `now`/`alive` parameters. A corroborated-dead entry (`"stale"`) now frees the launch slot; an uncorroborated one (`"active"` or `"unknown"`) still blocks (fail-toward-active).

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `tests/test_crew_launcher.py`

**Specific exclusions touched:** no — `scripts/recover_crews.py` unchanged (`git diff --stat` empty, confirmed below); no fenced file (`checklist_engine.py`, `gauge_reader.py`, `hooks/gauge_writer_hook.py`, `mcp_spine_server.py`, `.mcp.json`, `hooks/spine_rail.py`) touched.

## Behavior changed
Yes. `active_duplicate` previously blocked on any entry with `status in {"running","resumable"}` regardless of whether the crew behind it was actually alive. It now additionally corroborates liveness: a `cli`-backend entry with a dead PID, or an `external`-backend entry whose heartbeat is stale past 8h, is skipped (frees the slot) instead of blocking forever. A live PID, a healthy-age external heartbeat, or a legacy entry with neither signal (pid falsy, not external) all still block, unchanged from before in net effect.

## Map Impact
Map orientation for this gate is DEGRADED-UNPARSEABLE at baseline (no map artifact touches this gate per the handoff) — recording candidates only, not authoring the map.

- **Structural anchors touched:** `scripts/run_crew.py:253` region (now `:264-378` after the constant/import additions) — `entry_liveness` (new, `:264`) placed directly above `active_duplicate` (`:330`) per the handoff; `HEARTBEAT_STALE_SECONDS` (new, `:52`) placed near `ACTIVE_STATUSES` (`:48`).
- **Capabilities added/changed/affected:** Crew launch-refusal / duplicate guard (`active_duplicate`) now corroborates liveness instead of trusting a raw status string; a phantom (corroborated-dead) registry entry no longer blocks a fresh launch forever.
- **Constraints/assumptions touched:** `process_alive`'s contract/docstring/seam (`scripts/run_crew.py:958`, unchanged position, confirmed byte-identical below) is reused, not modified. `no-abandonment-by-inference` honored — `entry_liveness` never writes `abandoned`; `active_duplicate`'s `"stale"` branch is a plain `continue`.
- **Decision candidates / resolved decisions:** none — the three-bucket rule, 8h window, and fail-toward-active mapping were pre-decided per the handoff's Decision anchors; none were re-derived. One implementation-mechanics deviation was forced (see Assumptions below), not a design decision.
- **Claims/evidence produced:** `entry_liveness` and `active_duplicate` behave per the three-bucket/fail-toward-active spec, verified by the 9 new tests and the unmodified `test_duplicate_active_lock_is_refused`.
- **Trust limitations / drift found:** none found beyond the pre-declared DEGRADED map state.
- **Triage candidates:** see Out-of-scope observations below (periodic heartbeat-writer for external entries — the handoff explicitly excluded building this, flagging per its instruction).

## Test mode
**Required:** test-after (no TDD requirement in this repo's overlay for this class of change; the two existing named tests must keep passing unmodified).
**Satisfied:** yes — `test_duplicate_active_lock_is_refused` and `ProcessAliveTests` both pass unmodified; 9 new tests added alongside them in a new `EntryLivenessTests` class.

## Evidence

All 6 required-evidence items, in the handoff's numbering. Items 1-4 are load-bearing (the actual behavior change); item 5 is the regression guard (load-bearing); item 6 is confirmatory.

### 1. (load-bearing) cli-backend, dead PID, `status: "running"` → frees the slot

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py -k test_evidence_1_cli_dead_pid_frees_the_slot -v
```
```
tests/test_crew_launcher.py::EntryLivenessTests::test_evidence_1_cli_dead_pid_frees_the_slot PASSED
1 passed, 180 deselected
```
Asserts `RC.active_duplicate(entries, "issue-1", "g1", "reviewer", ".", alive=lambda pid: False)` returns `None` for an entry with `pid=99999`, `status="running"`.

### 2. (load-bearing) same shape, live PID → still blocks (honest-active control)

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py -k test_evidence_2_cli_live_pid_still_blocks -v
```
```
tests/test_crew_launcher.py::EntryLivenessTests::test_evidence_2_cli_live_pid_still_blocks PASSED
1 passed, 180 deselected
```
Asserts the same entry with `alive=lambda pid: True` returns the entry unchanged.

### 3. (load-bearing) external-backend phantom (real `epic-568-441` shape), `now` > 8h past `started_at` → frees the slot

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py -k test_evidence_3_external_phantom_past_8h_frees_the_slot -v
```
```
tests/test_crew_launcher.py::EntryLivenessTests::test_evidence_3_external_phantom_past_8h_frees_the_slot PASSED
1 passed, 180 deselected
```
Entry shape pulled verbatim (field-for-field) from the real archived record `constellation/epic-568-441/g1/implementer/attempt-1` in `.agent-work/archive/2026-08-15-epic-568-441/crew-runs.json` (`backend: "external"`, `pid: null`, `started_at == last_heartbeat == "2026-08-14T18:10:25.409092+00:00"`), status forced to `"running"` so the guard path is live. `now = started_at + 9h`. Returns `None`.

### 4. (load-bearing) same external shape, `now` = 4h past `started_at` → still blocks (proves the fix does not fire on a healthy long-running crew)

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py -k test_evidence_4_external_within_8h_still_blocks -v
```
```
tests/test_crew_launcher.py::EntryLivenessTests::test_evidence_4_external_within_8h_still_blocks PASSED
1 passed, 180 deselected
```

### 5. (load-bearing) `test_duplicate_active_lock_is_refused` — unmodified, green

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py -k test_duplicate_active_lock_is_refused
```
```
.                                                                        [100%]
1 passed, 180 deselected in 0.02s
```
Diff confirms this test's body is byte-unchanged (only new tests were added elsewhere in the file). This fixture (`pid` absent, no `backend`/`dispatch` key) exercises bucket 3 → `entry_liveness` returns `"unknown"` → `active_duplicate` still returns the entry → CLI still refuses with exit code 1, exactly as before.

### 6. (confirmatory) full suite, clean-env

```bash
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
```
```
........................................................................ [ 39%]
........................................................................ [ 79%]
.....................................                                    [100%]
181 passed in 0.57s
```
(172 pre-existing + 9 new, all green.)

### `scripts/recover_crews.py` unchanged

```bash
git diff --stat scripts/recover_crews.py; echo "exit:$?"
```
```
exit:0
```
No output — zero diff, confirmed unchanged.

### `process_alive` byte-identical

```bash
git diff scripts/run_crew.py | grep -n "process_alive"
```
```
49:+    `alive` defaults to the real `process_alive` when omitted (`None`
51:+    value): `process_alive` is defined LATER in this module, and a default
53:+    `def`-time, so writing `alive=process_alive` directly in this signature
87:+        alive = process_alive
126:+    omitted; `alive` defaults to the real `process_alive` (both via a `None`
127:+    sentinel resolved below — `process_alive` is defined later in this
```
Every hit is a new *reference to* the name from the new code; no hunk touches `process_alive`'s own `def` block, docstring, or body.

## TDD evidence, if required

Not applicable — test mode is test-after per the handoff (no TDD requirement for this change class). All new tests were written alongside the implementation and observed green on first run; no RED-then-GREEN transcript was required or produced.

## Wiring Grep

```bash
grep -rn "entry_liveness" --include=*.py . | grep -v "def entry_liveness"
```
13 lines matched (comments, docstring mentions, and actual calls combined). Breaking that down: **1 production call site** — `scripts/run_crew.py:374`, inside `active_duplicate`'s loop (the expected wiring point) — plus **7 test call sites** across the 5 direct `entry_liveness` unit tests in the new `EntryLivenessTests` class (`tests/test_crew_launcher.py:815,816,824,825,832,836,847`); the remaining 5 lines are comments/docstring prose mentioning the function name, not calls. No other reader exists yet, as expected — nothing outside `active_duplicate` and its own tests calls `entry_liveness`.

## Docs/contracts touched
- none — `scripts/run_crew.py`'s module docstring was not touched; the new function and constant carry their own docstrings/comments.

## Assumptions
- **Deviation from the handoff's literal signature suggestion, forced by Python semantics (not a design re-derivation):** the handoff's Close Criteria literally writes `entry_liveness(entry, now, alive=process_alive)` and `active_duplicate(..., *, now=None, alive=process_alive)`. `alive=process_alive` as a *default parameter value* is invalid at the position the handoff specifies: default values are bound at `def`-time (when the `def` statement executes), not lazily at call-time like a name referenced inside a function body — and `process_alive` is defined ~600 lines later in `scripts/run_crew.py` (`:958` after this change), so `alive=process_alive` in that literal position raises `NameError` at import time. Verified with a minimal repro (`def f(x=g): ...; def g(): ...` → `NameError: name 'g' is not defined`) before treating this as settled. Used a `None` sentinel resolved inside each function body instead (`if alive is None: alive = process_alive`), exactly the same pattern the handoff's own `now=None` already specifies — externally observable default behavior is identical (omit `alive` → real `process_alive` is used), purity is preserved (`alive` remains fully caller-injectable), and the change is import-order-safe. This is a mechanical Python-semantics fix, not a reinterpretation of the three-bucket rule, the 8h window, or the fail-toward-active mapping — none of which were touched.
- `now`'s type hint in `entry_liveness` is `datetime` (not `Optional`) since `active_duplicate` always resolves `now` to a real `datetime` before calling it — `entry_liveness` itself never sees `None` for `now`.

## Stop conditions hit
None. `entry_backend` is called inside `entry_liveness`'s function *body* (not as a default value), so it resolves correctly at call-time despite being defined later in the file (`:1118`-equivalent, now `:1217` after the earlier edits) — ordinary Python name resolution, no forward-reference problem there. The only forward-reference problem was the `alive=process_alive` default-value case above, which was fixed rather than treated as a stop condition (it is a mechanical implementation detail, not a question about the three-bucket rule or the 8h number).

## Out-of-scope observations
- Per the handoff's Specific Exclusions, a periodic heartbeat-writer for external entries was explicitly out of scope and not built. Flagging as a triage candidate per the handoff's own instruction: without one, every external-backend entry's `last_heartbeat` is set once at dispatch and never updated again (confirmed by inspecting `scripts/run_crew.py`'s external-backend entry construction), so the 8h window is really measuring "time since dispatch," not "time since last observed sign of life" — a long-running-but-genuinely-healthy external crew nearing 8h would eventually be misread as stale even while actively working, unless it periodically re-touches its own registry entry. This is inherent to the current entry shape, not a defect in this change; the handoff's Constraints/assumptions section already names it as future work, not something this gate builds.

## Workflow Feedback

- **Handoff gaps:** The literal function-signature text in Close Criteria (`alive=process_alive` as a default value) is not valid Python given where the handoff places `entry_liveness` (directly above `active_duplicate` at `:253`, while `process_alive` lives at `:864`). The handoff does say "your call, keep it simple and consistent" about *how* `now` is threaded, which in hindsight covers this too, but the `alive=process_alive` text reads as a literal instruction, not an illustrative default — a small parenthetical noting "resolve via a None sentinel if a literal default isn't legal at this position" would have removed a few minutes of doubt about whether this was a genuine stop-condition-worthy contradiction versus routine implementation.
- **Context rediscovered:** None beyond the ordinary — the handoff's Map Anchors and Required Evidence sections were unusually complete and saved real digging (the real archived phantom shape was already named with its exact file path, so no separate hunting was needed).
- **Instructions improvised around:** The dispatch message stated "external backend — no MCP spine door bound to you, do not attempt spine_* tool calls," and env inspection confirmed `SPINE_FILE`/`SPINE_SESSION` were bound to the parent Commander's own spine (`SPINE_SESSION=constellation/cleanup-c-liveness-rail/execute/commander`), not to this implementer's own plan — exactly the case `skills/workbench/references/checklist-engine.md`'s "MCP door... who it is NOT for" section describes. Per the constellation-implementer skill's own instructions for "nothing bound," built and drove an own `IMPLEMENTER_PLAN.json` (`.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement/IMPLEMENTER_PLAN.json`) through the CLI `checklist_engine.py` instead of the MCP door, claimed/released its own session lease, and recorded the deviation-and-why in the plan's `why_trail` at each gate.
- **What would have made this easier:** none beyond the one parenthetical noted above — this handoff was unusually thorough (Decision anchors with `@grade` tags, the real archived registry shapes named by exact path, the Windows-behavior note already anticipated in Constraints).

## Return status
`complete`
