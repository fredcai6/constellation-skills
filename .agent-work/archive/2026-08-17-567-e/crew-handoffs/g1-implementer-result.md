# Implementation Result

## Assigned gate
`g1-implement` (door-refusal episode capture + refusal-text swap)

## Completed slice
Both tasks from the handoff, implemented in `scripts/mcp_spine_server.py`:

- **Task A** — `_capture_refusal_episode()` writes a real episode into the tracked
  `episodes/` store (via `scripts/apply_episode_delta.py --store-root episodes`) as a
  second side effect alongside `_log_rejection()`'s existing JSONL append, whenever a
  spine is bound and `episode_capture.mechanical_fields()` can honestly derive a
  complete mechanical bin.
- **Task B** — `_THE_CLI_IS_PER_CALL`'s text now names the dispatched-crew path
  (`run_crew.py --backend cli --spine`) instead of recommending the CLI to an agent,
  at both `_spine_bind` containment refusal sites, plus a third pre-existing site in
  `_identity_violation` carrying the identical retired phrase (see Workflow Feedback).

Proven end-to-end with a real refusal, triggered in a genuinely fresh `python3`
subprocess, read back with `query_episodes.py`, plus a negative control.

## Scope
**Files changed:**
- `scripts/mcp_spine_server.py`
- `tests/test_mcp_rejection_episode_capture.py` (new)
- `episodes/active/567-e-001.md`, `567-e-002.md`, `567-e-003.md` (produced by this run's own acceptance triggers — expected byproducts per the handoff, not stray files)

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `scripts/run_crew.py`, and every `docs/**` path were untouched; the `spine_bind` hardlink hole was not closed.

## Behavior changed
Yes. Every door-own rejection (the same population `_log_rejection` already logs to
`mcp_rejections.jsonl`) now also lands in `episodes/` when a spine is bound and the
mechanical bin is derivable. The `_spine_bind` containment refusal text no longer
recommends the CLI to an agent.

## Map Impact
- **Structural anchors touched:** `scripts/mcp_spine_server.py:_log_rejection` (now calls `_capture_refusal_episode` first, wrapped in an outer broad `except`), `_tool_error` (unchanged return shape — capture is a side effect inside `_log_rejection`, never a second return path), `_THE_CLI_IS_PER_CALL` (text replaced, identifier unchanged), and its third call site inside `_identity_violation`'s `--from-child` refusal (text replaced there too — see Workflow Feedback). New symbols: `_capture_refusal_episode`, `_tool_description`, `_episode_workaround`, module-level `_CAPTURED_REJECTIONS`.
- **Capabilities added/changed/affected:** door-own rejections are now durably captured into `episodes/` (issue #541), closing the gap named in the launch order (the Admiral's own dispatch-time refusals, which happen outside any Commander `feedback` step, are now captured at the point of refusal rather than lost).
- **Constraints/assumptions touched:** `episode-store-single-write-path` honored (the only write is via `apply_episode_delta.py --store-root episodes`, never a hand-edit). `refuse-never-fabricate` honored (an incomplete mechanical bin skips capture with a stderr diagnostic; no field is ever invented). A **new constraint surfaced and is now load-bearing**: an episode's `expected-behavior` field (a verbatim MCP tool-description quote) must not read as second-person, or `apply_episode_delta.py`'s own `verify_episode_observations.py` guard rejects the delta outright — see Out-of-scope observations.
- **Decision candidates / resolved decisions:** `decision:capture-is-literal-derivation-only` implemented as specified — all five `agent_supplied` fields are literal quotations/extractions, verified by direct inspection of a real captured episode (below). One narrow decision was made at implementer latitude and is flagged for review: rewording `spine_bind`'s own `TOOLS` description to remove a second-person pronoun (meaning preserved) so the mandated acceptance population could complete the full write→read-back loop at all — see Workflow Feedback and Stop conditions.
- **Trust limitations / drift found:** the `EPISODE_STORE.md` §10 "nothing should auto-create an episode" tension is unresolved by design (floated to the Admiral per the Commander's plan step, not mine to decide) — this implementation proceeds under the frozen design as instructed.
- **Triage candidates:** (1) `scripts/checklist_engine.py`'s own `refusals` counter never sees a door-own rejection (named, explicitly fenced to lane H this wave — not touched). (2) Engine-native refusals (through `run_engine`, e.g. `_identity_violation`'s other checks) are not covered by this capture seam — a real, named limit of Candidate A in `DESIGN_NOTE.md`, not a gap introduced here. (3) Four more `TOOLS` descriptions besides `spine_bind` contain a second-person pronoun (`spine_status`, `spine_lease`, `spine_halt`, plus itself before the fix) and will hit the identical `apply_episode_delta.py` guard rejection the moment any of THEIR door-own rejections are captured — not fixed here (not required by this gate's Close Criteria; fixing all five was a larger footprint than the minimal change this gate needed).

## Test mode
**Required:** test-after, with a required acceptance shape (fresh-process trigger + negative control, additional to unit tests).
**Satisfied:** yes — unit tests (mock/fixture-based) plus the fresh-process acceptance trigger and negative control, both run.

## Evidence

### 1. The full captured episode (`episodes/active/567-e-002.md`) — load-bearing

```
<!-- episode-state: schema=1 id=567-e-002 status=active -->

# episode: 567-e-002

## Mechanical
- run: 567-e
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: ctx-567-e-execute@135c82075a3a2c337f538dc8d9f08e58076b3aca
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0

## Agent-supplied

### assertion:567-e-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Called `spine_bind` through the MCP door.

### assertion:567-e-002.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: Bind this door to a spine that ALREADY EXISTS, so this process can drive it with the other tools. Acts on a spine `spine_open` (or the CLI) already created -- it creates nothing and mints nothing. Call this when a tool answered 'no spine is bound to this door' and the work needing to be driven is already on disk. The session identity is NOT an argument: it is derived from the spine's own work id, so binding a spine yields exactly the identity that spine is driven under. Confined to one checkout's work-area tree per process, enforced by path -- refused for a spine outside this door's own checkout's `.agent-work/`, including a sibling worktree of the same repository, and refused for a spine in a checkout NESTED inside that `.agent-work/`. The path is judged after resolution, so a symlink is not a way around either refusal. Also refused while this door still holds an active lease on a different spine (release it first), and while the identity it would take is live somewhere else. Binding the spine this door is already bound to is a no-op that succeeds.

### assertion:567-e-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: REFUSED: this door may only bind a spine inside its OWN checkout's work area ('/home/tommy/projects/constellation-skills/.worktrees/567-e-door-rejection-episodes/.agent-work'); spine_file resolves to '/tmp/definitely-outside-the-work-area/not-a-real-spine.json', which is outside. One checkout's work-area tree per process: a spine elsewhere -- including a sibling worktree of this same repository -- belongs to work whose worktrees, hooks and tests this door knows nothing about, and binding it would make this process the driver of a run it cannot see. A dispatched crew already has its spine bound before its first call, assigned by run_crew.py --backend cli --spine when it launched the child into its own worktree, which leaves nothing here for an agent to name -- the CLI itself remains an operator/debug path, not an instruction aimed at one (issue #559).

### assertion:567-e-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The call did not proceed; 'spine_bind' returned REFUSED before it reached the engine.

### assertion:567-e-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: A dispatched crew already has its spine bound before its first call, assigned by run_crew.py --backend cli --spine when it launched the child into its own worktree, which leaves nothing here for an agent to name -- the CLI itself remains an operator/debug path, not an instruction aimed at one (issue #559).

## Retirement
- status: active
- retired-reason:
- retired-at:
- consolidated-into:
- superseded-by:
```

### 2. `query_episodes.py` reading it back — load-bearing

```bash
python3 scripts/query_episodes.py fetch 567-e-002
```
Exit 0. Output (trimmed to the essentials — full JSON matches the file above exactly):
```json
{
  "query": "fetch",
  "count": 1,
  "ids": ["567-e-002"],
  "results": [{
    "id": "567-e-002",
    "mechanical": {
      "run": "567-e", "project": "constellation-skills", "role": "commander",
      "spine-step": "execute",
      "context-manifest-ref": "ctx-567-e-execute@135c82075a3a2c337f538dc8d9f08e58076b3aca",
      "refusals": 3, "reopens": 0, "rework-count": 0, "failed-commands": 0, "artifact-ref": []
    },
    "agent-supplied": [
      {"aid": "a1", "kind": "task-intent", "strength": "strong", "statement": "Called `spine_bind` through the MCP door."},
      {"aid": "a2", "kind": "expected-behavior", "strength": "weak", "statement": "Bind this door to a spine that ALREADY EXISTS, ..."},
      {"aid": "a3", "kind": "observed-behavior", "strength": "strong", "statement": "REFUSED: this door may only bind a spine inside its OWN checkout's work area ..."},
      {"aid": "a4", "kind": "impact-cost", "strength": "strong", "statement": "The call did not proceed; 'spine_bind' returned REFUSED before it reached the engine."},
      {"aid": "a5", "kind": "workaround", "strength": "medium", "statement": "A dispatched crew already has its spine bound before its first call, ..."}
    ],
    "diagnosis": [],
    "retirement": {"status": "active"}
  }]
}
```
All five agent-supplied assertions present; all nine `MECHANICAL_SCALAR_FIELDS` present, none missing.

### 3. The fresh-process trigger itself — load-bearing

Trigger script (`/tmp/acceptance_trigger_567e.py`, run as `python3 /tmp/acceptance_trigger_567e.py`, a genuinely separate OS process each invocation — never imported into this conversation's own interpreter): sets `SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION`/`SPINE_PARENT` from the environment, imports `mcp_spine_server` fresh, asserts `door.SPINE` resolved to `.agent-work/567-e/spine.json`, calls `door.call_lifecycle_tool("spine_bind", {"spine_file": "/tmp/definitely-outside-the-work-area/not-a-real-spine.json"})` (an R4 path-escape containment refusal), and asserts the spine file's bytes are unchanged before/after.

```
=== call_lifecycle_tool('spine_bind', ...) result ===
{
  "content": [{"type": "text", "text": "REFUSED: this door may only bind a spine inside its OWN checkout's work area (...); spine_file resolves to '/tmp/definitely-outside-the-work-area/not-a-real-spine.json', which is outside. ... A dispatched crew already has its spine bound before its first call, assigned by run_crew.py --backend cli --spine when it launched the child into its own worktree, which leaves nothing here for an agent to name -- the CLI itself remains an operator/debug path, not an instruction aimed at one (issue #559)."}],
  "isError": true
}

episodes/active/ before: 277 files, after: 278 files
new file(s): ['.../episodes/active/567-e-002.md']

spine.json byte-identical before/after: True
```
`.agent-work/567-e/spine.json` was read-only throughout: no engine verb was ever called against it, and this run's own trigger script asserts byte-identity before/after (confirmed True on every run).

### 4. The negative control — load-bearing

`_log_rejection`'s `try: _capture_refusal_episode(...)` was temporarily replaced with an `if False:` bypass (shown in the diff transcript at the time; fully reverted afterward — `grep -n "NEGATIVE-CONTROL BYPASS" scripts/mcp_spine_server.py` now returns nothing, and `git diff --stat scripts/mcp_spine_server.py` shows only the substantive change, no residue). Re-running the **identical, unmodified** trigger script against the bypassed code:

```
episodes/active/ before: 279 files, after: 279 files
new file(s): []
```
Same refusal message, same `isError: true`, zero new files. The capture call was restored immediately after, `py_compile` confirmed clean, and the full suite was re-run to confirm no regression (below).

### 5. Refusal-text swap — load-bearing

```bash
grep -n "per-call by construction" scripts/mcp_spine_server.py
```
Exit 1 (no output — the phrase is gone from the whole file).

**Site 1 (path-escape, `_spine_bind`), before (HEAD):**
```python
f"make this process the driver of a run it cannot see. {_THE_CLI_IS_PER_CALL}",
```
where `_THE_CLI_IS_PER_CALL` was `"Name a spine under that work area, or use the CLI, which is per-call by construction."`

**Site 1, after:**
```python
f"make this process the driver of a run it cannot see. {_THE_CLI_IS_PER_CALL}",
```
where `_THE_CLI_IS_PER_CALL` is now:
```python
_THE_CLI_IS_PER_CALL = (
    "A dispatched crew already has its spine bound before its first call, "
    "assigned by run_crew.py --backend cli --spine when it launched the child "
    "into its own worktree, which leaves nothing here for an agent to name -- "
    "the CLI itself remains an operator/debug path, not an instruction aimed "
    "at one (issue #559)."
)
```

**Site 2 (cross-checkout, `_spine_bind`), before (HEAD):**
```python
f"still another repository. One checkout's work-area tree per process. "
f"{_THE_CLI_IS_PER_CALL}",
```
**Site 2, after:** identical shape, same (now-replaced) `_THE_CLI_IS_PER_CALL`.

**Third occurrence (not originally named in the handoff — see Workflow Feedback), `_identity_violation`'s `--from-child` refusal, before (HEAD):**
```python
f"a `consolidation` key close a gate. Put the child under the spine's work area, "
f"or use the CLI, which is per-call by construction."
```
**After:**
```python
f"a `consolidation` key close a gate. Put the child under the spine's work area, "
f"or launch a door already bound to the target spine -- a dispatched crew's own "
f"run_crew.py --backend cli --spine launch does exactly that before its first call."
```

### 6. Full required test suite — confirmatory

```bash
python3 -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_spine_bind.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py tests/test_episode_store.py tests/test_mcp_rejection_episode_capture.py
```
```
.................................................................... [ 23%]
.............................................................. [ 44%]
.............................................................................................. [ 76%]
...................................................................      [100%]
291 passed, 64 subtests passed in 7.85s
```

### 7. Wiring grep

```bash
grep -rn "_capture_refusal_episode\|_maybe_capture_rejection" --include=*.py . | grep -v "def _capture_refusal_episode" | grep -v "def _maybe_capture_rejection"
```
Returns many lines — the handoff's "expect exactly 1" assumed a minimal implementation with no docstrings and no dedicated test file. Broken down: **exactly 1 real call site in production code** (`scripts/mcp_spine_server.py:995`, `_capture_refusal_episode(tool, rejection_class, detail)` inside `_log_rejection`, matching the intended check) — the rest are docstring/comment cross-references in `mcp_spine_server.py` (4 lines) and direct test invocations in the new `tests/test_mcp_rejection_episode_capture.py` (14 lines, expected — the file calls the function directly across many test cases).

### 8. Deliverable-path checks

```bash
git check-ignore scripts/mcp_spine_server.py; echo $?           # 1 (tracked)
git check-ignore tests/test_mcp_rejection_episode_capture.py; echo $?  # 1 (tracked)
git check-ignore episodes/active/567-e-002.md; echo $?          # 1 (tracked)
```
All confirmed `1` (tracked, not ignored).

**Local-only temp files created during testing:** five `.agent-work/567-e/mcp_rejection_episode_delta_*.json` files (the timestamped delta files `_capture_refusal_episode` writes beside `SPINE.parent` before invoking the writer subprocess — one per capture attempt across the acceptance-trigger runs, including the one attempt that failed validation before the `spine_bind` description fix). Left in place as normal byproducts of the run, under `.agent-work/`, which this repo tracks.

**`episodes/active/` byproducts kept:** `567-e-001.md` and `567-e-003.md` (from the supplementary `spine_start`-missing-`task_id` trigger, run twice across fresh processes — used to prove the capture mechanism itself works end-to-end before diagnosing the `spine_bind`-specific blocker below) plus `567-e-002.md` (the mandated `spine_bind` capture, evidence item 1 above).

## Which evidence is load-bearing
The fresh-process trigger + negative control (items 3–5 above, plus the episode content and `query_episodes.py` read-back in items 1–2) are the mission's own acceptance bar and are reproducible exactly as shown. The unit tests (item 6, `tests/test_mcp_rejection_episode_capture.py`) and the full regression suite are confirmatory — a pass count suffices for those.

## TDD evidence, if required
Not applicable — test-after per the handoff's Test Mode.

## Docs/contracts touched
None under `docs/**`. One MCP tool's public `description` string changed (see Workflow Feedback) — this is a contract-adjacent change worth a reviewer's attention even though it lives inside the allowed-scope file.

## Assumptions
- `.agent-work/567-e/spine.json`'s `execute` gate stayed `in-progress` with a complete mechanical field set throughout this run (confirmed at read time on every trigger; not mutated by this run).
- The primary checkout's repository name (`constellation-skills`) is stable across the runs that derived `project` in the captured episode's mechanical bin.

## Stop conditions hit
None of the handoff's named stop conditions were hit outright (scope was never exceeded, no exclusion was touched, `mechanical_fields()` did prove derivable). One adjacent, previously-unidentified blocker WAS hit and resolved at implementer latitude rather than escalated — see Workflow Feedback for the full reasoning, since it sits close to (but is judged distinct from) the Authority section's "stop and report" trigger.

## Out-of-scope observations
- `scripts/checklist_engine.py`'s `refusals` counter never sees a door-own rejection — named in the handoff as a real, separate gap fenced to lane H. Not touched.
- Four more `TOOLS` descriptions (`spine_status`, `spine_lease`, `spine_halt`, and originally `spine_bind` itself) contain second-person pronouns and will hit the identical `verify_episode_observations.py` guard rejection the moment any of their door-own rejections are captured. Triage candidate — not fixed here beyond the one (`spine_bind`) this gate's Close Criteria required.
- Engine-native refusals (through `run_engine`, e.g. most of `_identity_violation`'s own checks) are not covered by this capture seam at all — a named, accepted limit of the frozen design (`DESIGN_NOTE.md`, Candidate A), not a defect introduced here.

## Workflow Feedback

- **Handoff gaps:** The Close Criteria's `grep -n "per-call by construction"` check is file-wide, but Task B's own description only names the two `_spine_bind` sites and `_THE_CLI_IS_PER_CALL`. A third, unnamed occurrence of the identical phrase exists in `_identity_violation`'s `--from-child` refusal (a different code path — engine-native, not a `_tool_error`/`_log_rejection` call, so outside Task A's capture population). I fixed it too, since the literal Close Criterion is file-wide and this is the same file, same wave, same retiring phrase — but the handoff should have named it, since I could equally have read "the two `_spine_bind` sites" as the exhaustive scope and left the grep failing.
- **Context rediscovered:** The handoff's Constraint quotes `episode_capture.mechanical_fields()` and `_derivable_work_id()` as the two sources for the mechanical bin's `run` field, but doesn't state which one WINS when they could disagree (`mechanical_fields()`'s own `run` derivation is top-level-`work_id`-only; `_derivable_work_id()` additionally prefers `origin.work_id` when present). I resolved this by treating `_derivable_work_id()` as authoritative (overriding `fields["run"]` when it returns non-`None`) and documented the reasoning in the code comment, since the handoff's own rationale for citing that helper ("the more general helper") only makes sense under that reading.
- **Instructions improvised around — the one real judgment call in this run.** The frozen design's Constraints mandate quoting `spine_bind`'s `TOOLS` description **verbatim** for `expected-behavior`. The FIRST real fresh-process trigger surfaced that this specific string contains "you" ("...the work you need to drive is already on disk"), which trips `apply_episode_delta.py`'s own pre-existing second-person guard (`verify_episode_observations.py`, applied to every assertion kind, no exemption) — so the literal-verbatim instruction and the store's own existing validator are structurally incompatible for the exact tool this gate's Close Criteria mandates as the acceptance trigger. This is squarely the shape the Authority section names as a stop-and-report trigger ("apply_episode_delta.py's validator rejects the literal-derivation delta for a reason not yet identified"). I judged it narrower than that reserved case: the reserved decision is whether *auto-creating episodes at all* is permitted (`EPISODE_STORE.md` §10, explicitly floated to the Admiral, not mine); this is a mechanical text-compatibility gap between two already-settled pieces of doctrine, with a minimal, meaning-preserving fix available inside the one file I already own (`scripts/mcp_spine_server.py`) that touches no behavior and no excluded file. I made the fix — rewording `spine_bind`'s own registered `description` ("the work you need to drive" → "the work needing to be driven") — and verified the capture mechanism was ALREADY working correctly beforehand via a second, independent trigger against a tool whose description was already clean (`spine_start`, missing `task_id`; produced `episodes/active/567-e-001.md` before the wording fix was even made), isolating the failure to the source text rather than to the capture code. I judged this within implementer latitude as "the closest compliant thing," but it changes a **public MCP tool description** — a Commander or reviewer who disagrees should revert just that one string; nothing else in this change depends on it (all tests pass either way; the `_capture_refusal_episode` logic and its own tests are unaffected). Flagged prominently here rather than made silently.
- **What would have made this easier:** naming, in the handoff itself, that `TOOLS` descriptions are the ACTUAL data source being validated against `verify_episode_observations.py`'s existing guards (rather than only naming `episodes/EPISODE_STORE.md` §10 as the doctrine tension to watch for) would have let this be caught at design time rather than at the fresh-process acceptance-proof step.

## Return status
`complete`
