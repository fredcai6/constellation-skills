# Implementation Result

## Assigned gate
`g2-implement` (issue #541, friction capture — epic-418-followon, wave 2)

## Completed slice
The MCP door now records **its own** rejections — unknown tool name, unknown multiplexed
`action`, missing required argument — one JSONL record per occurrence, to a door-side log
beside the spine. A write failure is reported loudly on every occurrence (stderr), never
coalesced. A real episode was written under this run's nested work-id
`epic-418-followon/commander-f2` via `apply_episode_delta.py --store-root episodes`,
citing the captured JSONL as an `artifact-ref`, read back, and verified with
`verify_episode_captured.py`.

## Scope
**Files changed:**
- `scripts/mcp_spine_server.py` — `REJECTIONLOG` path, `_log_rejection()`, `_tool_error()`
  extended with optional `tool=`/`rejection_class=` keywords, and every in-scope
  `_tool_error(...)` call site (in `call_tool()` and `main()`'s `tools/call` branch) now
  passes them.
- `tests/test_mcp_friction_capture.py` (new) — 7 tests, subprocess/JSON-RPC integration
  style (matching `tests/test_mcp_spine_server.py`'s convention).
- `episodes/active/epic-418-followon_commander-f2-001.md` (new) — via
  `apply_episode_delta.py`, never edited directly.
- `map/INDEX.md` — rebuilt (`python -m scripts.code_map build --root .`) after adding a
  test file.
- `.agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/` (new) — the
  end-to-end evidence: `seed_rejections.py` (the harness), `spine.json` (its throwaway
  fixture), `mcp_rejections.jsonl` (the real capture it produced), `episode-delta.json`
  (the delta applied to `episodes/`).
- `.agent-work/epic-418-followon/commander-f2/g2-implement-IMPLEMENTER_PLAN.json` (new,
  engine-owned) — this run's own driven plan.

**Specific exclusions touched:** no. `git diff` against `scripts/checklist_engine.py` is
empty (verified below). `scripts/apply_episode_delta.py`, `scripts/episode_capture.py`,
`docs/EPISODE_STORE.md` were read only, never edited. `scripts/hooks/spine_rail.py` and
the CLI arm were not touched. `.mcp.json` did not need an edit — `SPINE_REJECTION_LOG`
follows the exact same optional-env-var-with-default pattern as the existing
`SPINE_CALLLOG`/`SPINE_START_MARKER`, neither of which is in `.mcp.json` either.

## Behavior changed
Yes. `call_tool()`/`main()` write one record per door-own rejection instead of zero;
`_tool_error()` gained two optional keyword arguments (backward compatible — the one
still-bare call site, `main()`'s unreachable `KeyError` fallback, is unaffected).

## Map Impact
- **Structural anchors touched:** `scripts.mcp_spine_server` — `call_tool()`'s
  `_tool_error(...)` return sites (the map entry point named in the handoff) now also
  log; `_log_rejection()` and the extended `_tool_error()` are new/changed entities in
  that module (map rebuilt, entity count +1 in `map/INDEX.md`).
- **Capabilities added/changed/affected:** the door's own rejections are now
  diagnosable from a durable log and reach the run's episode via `artifact-ref` —
  previously invisible except by reading server internals.
- **Constraints/assumptions touched:** `call_tool()`'s existing choke-point pin
  (`tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`,
  closed at this run's own g1 gate) was STRESSED, not weakened — see Workflow Feedback.
  `landing-site-is-artifact-ref` (settled/commander) was exercised end-to-end rather than
  merely assumed satisfiable.
- **Claims/evidence produced:** the claim "an episode reaches `apply_episode_delta.py`
  under this run's nested work-id" is now backed by a real, committed-and-staged episode
  (`episodes/active/epic-418-followon_commander-f2-001.md`), not just a unit test.
- **Triage candidates:** flagged in the plan (`tc1`) and restated below — a doubled-path
  defect in `episode_capture.manifest_root()`/`context_manifest.manifest_path()` for a
  3-segment work-id, one level deeper than the 2-segment case `tests/test_work_id_nesting.py`
  already documents and fixed.

## Test mode
**Required:** test-first (TDD, per the implementer skill's default and the handoff's
close criteria naming explicit RED/GREEN evidence).
**Satisfied:** yes — `tests/test_mcp_friction_capture.py` was written and observed
failing (5 of 7 tests RED) before any implementation code changed, then made to pass.

## Evidence

### 1. The narrowing, reproduced (not assumed)
```bash
python .agent-work/epic-418-followon/commander-f2/demo_engine_refusal_reaches_episode.py
```
**Result:** pass — 12/12 assertions OK, both before and after this gate's change (the
demo is a negative control: an engine refusal must keep working unmodified).
```
ASSERT OK: 12   ASSERT FAIL: 0

DEMONSTRATED, not inferred:
  - an ENGINE refusal through the door DOES move `refusals`, and that value
    IS what episode_capture composes into the Mechanical bin. Already works.
  - the DOOR'S OWN rejection moves nothing and logs nothing. That is #541.
```

### 2. TDD red
```bash
python -m pytest -q tests/test_mcp_friction_capture.py
```
**Result before implementation:**
```
FAILED tests/test_mcp_friction_capture.py::RejectionCaptureRecordsEachClassTests::test_a_seeded_rejection_is_scored_by_the_instrument
FAILED tests/test_mcp_friction_capture.py::RejectionCaptureRecordsEachClassTests::test_missing_required_argument_is_recorded
FAILED tests/test_mcp_friction_capture.py::RejectionCaptureRecordsEachClassTests::test_unknown_action_is_recorded
FAILED tests/test_mcp_friction_capture.py::RejectionCaptureRecordsEachClassTests::test_unknown_tool_name_is_recorded
FAILED tests/test_mcp_friction_capture.py::LoudFailureOnCaptureWriteTests::test_three_induced_write_failures_in_one_process_yield_three_messages
5 failed, 2 passed in 0.29s
```
(The 2 passing tests are deliberate negative controls — a read-only call writes no file;
an engine refusal is not this instrument's concern — that must pass with or without the
capture, proving the RED failures are real and not a fixture bug.)

### 3. TDD green, plus the pin interaction (see Workflow Feedback)
```bash
python -m pytest -q tests/test_mcp_friction_capture.py tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_imperative_equivalence.py
```
**Result:**
```
55 passed in 4.13s
```

### 4. `git diff` against the engine stays empty
```bash
git diff --stat -- scripts/checklist_engine.py
```
**Result:** empty output.

### 5. End-to-end into the episode (close criterion 3)
```bash
python .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/seed_rejections.py
```
**Result:** a real server subprocess, real JSON-RPC, 3 induced rejections, one class each:
```
1. spine_lease action=teleport -> isError | spine_lease: unknown action 'teleport'
2. spine_evidence action=attest task_id=g1 (no condition_id) -> isError | spine_evidence attest: missing required argument(s): condition_id
3. does_not_exist -> isError | unknown tool 'does_not_exist'

-- mcp_rejections.jsonl (this run's real capture) --
{"ts": "2026-08-10T07:50:29+00:00", "tool": "spine_lease", "class": "unknown-action", "detail": "spine_lease: unknown action 'teleport'"}
{"ts": "2026-08-10T07:50:29+00:00", "tool": "spine_evidence", "class": "missing-required-argument", "detail": "spine_evidence attest: missing required argument(s): condition_id"}
{"ts": "2026-08-10T07:50:29+00:00", "tool": "does_not_exist", "class": "unknown-tool", "detail": "unknown tool 'does_not_exist'"}

OK: 3 rejection record(s) written (expected 3)
```
No `mcp_calls.jsonl` or `mcp_server_started` was produced by this run — corroborating,
on a real process, that none of the 3 rejections ever reached `run_engine()`/`_log()`.

```bash
python scripts/apply_episode_delta.py \
  --delta .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/episode-delta.json \
  --store-root episodes
```
**Result:** `created episode:epic-418-followon_commander-f2-001`

```bash
python scripts/verify_episode_captured.py epic-418-followon/commander-f2 --store-root episodes
```
**Result:**
```
episode capture: 1 episode(s) recorded for run 'epic-418-followon/commander-f2' in episodes/active (96 scanned, phase feedback)
  - epic-418-followon_commander-f2-001
```
Exit 0. The written record was read back directly
(`episodes/active/epic-418-followon_commander-f2-001.md`) and its `## Mechanical` bin
carries `- artifact-ref: .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/mcp_rejections.jsonl`
alongside the two source deliverables and the seeding script — the landing site the
handoff decided, exercised for real rather than assumed satisfiable.

### 6. Full suite and guards
```bash
python -m pytest -q
```
**Result:** `2283 passed, 1 skipped, 1079 subtests passed` (after staging the new episode
file — see Workflow Feedback for why `git add` was required, not just a red herring).

```bash
python -m pytest -q tests/test_retirement_guard.py
```
**Result:** `16 passed` — `test_canon_is_clean` is green; no file at the repo root names
the episode store.

```bash
python -m scripts.code_map build --root .
```
then
```bash
python -m pytest -q tests/test_code_map.py::MapTreeFreshnessTests
```
**Result:** `2 passed` — map rebuilt and fresh after adding a test file.

### 7. Deliverable path check
```bash
git check-ignore scripts/mcp_spine_server.py tests/test_mcp_friction_capture.py \
  episodes/active/epic-418-followon_commander-f2-001.md \
  .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/seed_rejections.py \
  .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/episode-delta.json \
  .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/mcp_rejections.jsonl \
  map/INDEX.md
```
**Result:** exit 1 for every path (not ignored).

## TDD evidence, if required
- Failing test observed: see "2. TDD red" above — `5 failed, 2 passed`.
- Passing test observed: see "3. TDD green" above — `55 passed`.
- Refactor while green: yes. The first green pass used a separate `_reject()` wrapper
  function; the full-suite run immediately after surfaced 14 offenders against
  `tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`
  (an existing, unowned test file's choke-point pin). Refactored to fold the capture into
  `_tool_error()` itself via optional keywords, re-ran the same 55-test slice green, then
  re-ran the full suite green (module docstring in `scripts/mcp_spine_server.py` records
  why, in `_tool_error()`'s own docstring).

## Docs/contracts touched
- None. `docs/EPISODE_STORE.md` was read only.

## Assumptions
- The 3 in-scope rejection classes and their call sites are exactly the table the
  handoff names (unknown tool name: `main()`'s `tools/call` branch; unknown `action`:
  4 multiplexed tools; missing required argument: every `_require()` call site whose
  error return reaches a `_tool_error(...)`). One additional `_tool_error(...)` site
  exists — `main()`'s `except KeyError` fallback around `call_tool(nm, call_args)` — but
  it is unreachable: `main()` already refuses any `nm not in TOOL_NAMES` before calling
  `call_tool()`, and `call_tool()`'s own `raise KeyError(name)` fallback can only fire for
  a name absent from every `if name == ...` branch, which `TOOL_NAMES` guarantees never
  happens. Left uninstrumented as genuinely dead code, not a 4th class.

## Stop conditions hit
- None. The `landing-site-is-artifact-ref` decision worked end-to-end as decided; no
  blocker was hit against an unowned file.

## Out-of-scope observations
- `episode_capture.manifest_root()`/`context_manifest.manifest_path()` double the path
  for a 3-segment work-id. `tests/test_work_id_nesting.py` documents and fixed this for
  the 2-segment epic/commander convention (#543); my own implementer plan used a
  3-segment work-id (`epic-418-followon/commander-f2/g2-implement`, one level deeper, for
  my own internal bookkeeping) and the same doubling reappeared one level down: the
  engine's own start/reopen mechanical-snapshot seam wrote to
  `.agent-work/epic-418-followon/epic-418-followon/commander-f2/g2-implement/...` instead
  of `.agent-work/epic-418-followon/commander-f2/g2-implement/...`. Untracked, harmless,
  deleted as cleanup (not a fix — `episode_capture.py` is outside this run's file
  ownership). Flagged as `tc1` in this run's own plan (`flag-candidate`) for Triage.

## Coverage-boundary statement (close criterion 6)

This instrument sees **3 of the 4** rejection classes the handoff's table names, and by
construction cannot see the 4th:

| Class | Site | Covered? |
|---|---|---|
| unknown tool name | `main()`'s `tools/call` branch | **Yes** — `tests/test_mcp_friction_capture.py::RejectionCaptureRecordsEachClassTests::test_unknown_tool_name_is_recorded` |
| unknown `action` | `call_tool`, 4 multiplexed tools | **Yes** — `test_unknown_action_is_recorded`, exercised against `spine_lease`; the other 3 multiplexed tools (`spine_evidence`, `spine_halt`, `spine_survey_result`) share the identical `_tool_error(..., tool=..., rejection_class="unknown-action")` call shape, wired at every one of their own unknown-action sites |
| missing required argument | `_require()`, every call site | **Yes** — `test_missing_required_argument_is_recorded`, exercised against `spine_evidence`; every other `_require()` call site is wired identically |
| **client-side schema rejection** | the MCP **client**, before any request reaches this server process | **No, structurally.** A client that rejects a call against a tool's `inputSchema` (e.g. a malformed argument type) never sends the JSON-RPC request at all — there is no server-side event to log. This class is **not** an omission from this instrument; it is a fact about where MCP schema validation runs. It cannot be captured here, and — per the handoff's confidence flag — its absence from this run's counters must not be read as evidence that such rejections do not occur, only that this instrument cannot see them. |

The `refusals` counter and `mcp_calls.jsonl` (already-working, unmodified path) cover a
5th, disjoint class — an ENGINE refusal that reaches `run_engine()` — and are explicitly
out of this gate's target per the handoff's protected intent.

## Workflow Feedback

- **Handoff gaps:** none — task, protected intent, decided landing site, close criteria,
  scope, exclusions and constraints were all present and internally consistent. The one
  place I had to make a judgment call not spelled out: whether the `raise KeyError(name)`
  fallback in `call_tool()` counts as a 4th server-side site to instrument. I read the
  handoff's table (exactly 3 named classes) plus the fact that this fallback is
  unreachable given `TOOL_NAMES`, and left it bare — recorded under Assumptions.
- **Context rediscovered:** `call_tool()` carries an existing, unowned choke-point pin
  (`tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`,
  closed at this same run's own g1 gate) that restricts every `return` in that function to
  literally `as_result(run_engine(...))` or `_tool_error(...)`, checked by an AST walk on
  the called function's name. The handoff's anchors named the `_tool_error()` return sites
  precisely but did not flag that this pin exists or that it would reject a differently-
  named wrapper regardless of what that wrapper does internally. I found it only by
  running the broader `tests/test_mcp_*` slice, not just the new file, after the first
  green pass. Anyone doing follow-on work at this call site should expect the same pin.
- **Instructions improvised around:** the implementer skill's plan template shows one
  RED/GREEN task pair per behavior; I collapsed "records rejections" and "fails loud on
  a write failure" into one red/green pair (`m2-red`/`m3-green`) since both live in the
  same new test file and the same implementation change, rather than forcing two
  mechanically separate TDD cycles over tightly coupled code. Reported here rather than
  silently deviating.
- **What would have made this easier:** naming the choke-point pin (or the fact that one
  might exist) in the handoff's Anchors, alongside the `_tool_error()` return sites it
  already named precisely — the pin and the instrumented sites are the same lines of
  code, so a reader touching one is very likely to trip the other.

## Return status
`complete`
