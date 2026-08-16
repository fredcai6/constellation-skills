# Implementation Result

## Assigned gate
g2-implement (issue #549)

## Completed slice
`decide_stop` no longer renders a subordinate's own next imperative into a parent/shared-session Stop-block reason when the surviving mid-flight entry is reachable only through that subordinate's per-agent (`sid#agent_id`) binding key. The block/allow decision, nudge/strike counting, and the `count >= 3` escape hatch are byte-for-byte unchanged; only the rendered `reason` and `additionalContext` strings change, and only for the foreign-owned case.

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`

**Specific exclusions touched:** no — `decide_session_start` untouched in code (verified via `git diff`, and pinned by a new regression test); `binding_key`, `_foreign_worktree`, `_mid_flight_reason`, `_entry_mid_flight_view` used as-is, not modified; `scripts/run_crew.py` / `tests/test_crew_launcher.py` not touched; none of the five fenced files (`scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`) touched — confirmed by empty `git diff --stat`.

## Behavior changed
Yes. `decide_stop`'s block reason/context text changes for one specific case (a mid-flight entry reachable only through a per-agent key not equal to the stopping session's own bare id) — the gating outcome (block vs allow) for every existing scenario is unchanged.

### What changed, mechanically
- **`_session_keys(binding, sid) -> list[str]`** (new, `scripts/hooks/spine_rail.py:515`): the ordered list of binding keys `session_view` merges — bare `sid` (untyped `==`) plus every composite `sid#agent_id` key (`isinstance(key, str) and key.startswith(prefix)`), in `binding`'s own iteration order. Reproduces `session_view`'s original two-branch asymmetry exactly, not tidied into a single coerced-to-str check.
- **`session_view(binding, sid)`** (`:543`): rewritten as a thin fold over `_session_keys` — identical signature, identical `{abs_spine_path: entry}` return shape, identical never-raises/`{}`-on-unusable contract.
- **`session_view_provenance(binding, sid) -> dict[str, str]`** (new, `:566`): maps each visible `abs_spine_path` to the binding key that sourced it, built from the same `_session_keys` list, last-key-wins on collision (matches `session_view`'s own `dict.update` overwrite order). `{}` on falsy `binding`/`sid`, never raises.
- **`_owning_session_reason(spine_path, owner_key) -> str`** (new, next to `_mid_flight_reason`, `:1379`): the rendered reason for a foreign-owned entry. Names `owner_key` and `spine_path`, states the stop is STILL BLOCKED, explicitly says this is not the stopping session's gate to drive, and never interpolates any imperative text.
- **`decide_stop`** (`:1427`): computes `owners = session_view_provenance(binding, sid)` alongside the existing `session_view` call; keeps `spine_path` from the mid-flight tuple (previously discarded via `_`); at the render step branches on `owners.get(spine_path)` — `== sid` or absent (defensive) keeps the original `_mid_flight_reason`/`reconstruct_current` text; anything else renders `_owning_session_reason` and a withheld-imperative `additionalContext` string (`"ENGINE current -> (withheld: gate belongs to {owner_key})"`).

## Map Impact
- **Structural anchors touched:** `scripts/hooks/spine_rail.py:515` `session_view()` (refactored onto new seam `_session_keys`, unchanged contract); new `_session_keys()` and `session_view_provenance()` added adjacent to it; new `_owning_session_reason()` added adjacent to `_mid_flight_reason()` (`:1379`); `decide_stop()` (`:1427`) — render-step wiring only, decision logic unchanged.
- **Capabilities added/changed/affected:** Stop-hook mid-flight block (capability: refuses a dishonest turn-end while a spine gate is still open) — refusal rate unchanged; rendered reason/context text now varies by ownership of the surviving mid-flight entry.
- **Constraints/assumptions touched:** `session_view` has exactly two callers (`decide_stop`, in scope; `decide_session_start`, explicitly out of scope) — honored; regression test added pinning `decide_session_start`'s behavior. `session_view`'s exact dict-shape contract (existing pinning test) — honored unmodified.
- **Decision candidates / resolved decisions:** keep-the-block-drop-the-imperative (`@grade: settled/human · leans g2-implement`) — implemented as specified: gating outcome untouched, only the two rendered strings for a foreign-owned `mid_flight[0]` change.
- **Claims/evidence produced:** full `tests/test_spine_rail.py` suite (150 passed, 1 pre-existing platform skip) backs the claim that no other test's pass/fail flipped; the updated composite test and new control test together back the claim that the wording change is scoped exactly to per-agent-key-only entries.
- **Trust limitations / drift found:** none found; map orientation for this repo was already DEGRADED-UNPARSEABLE at baseline per the handoff, unrelated to this change.
- **Triage candidates:** none raised.

## Test mode
**Required:** test-after (one existing test pinning the bug required update, not just supplementing)
**Satisfied:** yes — `test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` updated and inverted per the handoff; the refactor step (`_session_keys`/`session_view`) was verified green before and after against the existing unmodified pinning test, and the new suite runs green in a clean env.

## Evidence

### 1. (load-bearing) Updated composite-key test — decision still `block`, imperative withheld from both fields, owner key present
```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py::test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key
```
**Result:** pass. Asserts `out["decision"] == "block"`, `"COMPOSITE-MARKER" not in out["reason"]`, `"COMPOSITE-MARKER" not in out["hookSpecificOutput"]["additionalContext"]`, the owning composite key (`sid#agent_id`) present in `reason`, and nudges still keyed by bare `sid` alone (`list(sr.load_nudges(proj).keys()) == [sid]`).

### 2. (load-bearing) New control test — bare-sid-owned entry unchanged
```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py::test_stop_bare_sid_owned_mid_flight_still_renders_original_imperative_text
```
**Result:** pass. Ordinary same-session mid-flight entry still renders the original imperative-bearing `_mid_flight_reason` text in both `reason` and `additionalContext`, unchanged.

### 3. (load-bearing) `test_session_view_merges_one_bare_and_two_composite_keys` run unmodified, before and after
```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py::test_session_view_merges_one_bare_and_two_composite_keys
```
**Result:** pass, both before the `_session_keys` refactor and after. Test file diff for this test: none (byte-for-byte unmodified, confirmed by not touching those lines).

### 4. (confirmatory) `_session_keys` / `session_view_provenance` direct unit tests
```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py -k "session_view_provenance or session_keys"
```
**Result:** pass — 9 tests (bare-only, composite-only, mixed-order-preserving, empty/None sid for `_session_keys`; bare-only, composite-only, mixed via the real-claim-writer fixture shape, last-key-wins collision, empty/falsy input for `session_view_provenance`).

### 5. (load-bearing) `decide_session_start` regression
```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py -k "session_start"
```
**Result:** pass — 15 tests, including the new `test_session_start_composite_key_entry_still_renders_full_imperative_unchanged`, which proves a composite-key-only entry's imperative still renders in full into `additionalContext` (no withholding — that's `decide_stop`-only). `decide_session_start`'s own code has zero diff (`git diff` shows no lines inside its function body).

### 6. (confirmatory) Full clean-env suite
```bash
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py
```
**Result:**
```
....................................s................................... [ 47%]
........................................................................ [ 95%]
.......                                                                  [100%]
150 passed, 1 skipped in 1.57s
```
The 1 skip is pre-existing and platform-gated (`ntpath's normcase ... only applies on Windows`, `tests/test_spine_rail.py:833`), unrelated to this change. 150 passed = 139 pre-existing tests (unaffected, pass/fail set unchanged) + 11 new/changed tests (9 unit tests for `_session_keys`/`session_view_provenance`, 1 control test, 1 `decide_session_start` regression test) all green; the one named existing test (`test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key`) still counts toward the 150 with its inverted assertions.

### Fenced-file check
```bash
git diff --stat scripts/hooks/gauge_writer_hook.py scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/gauge_reader.py .mcp.json
```
**Result:** empty output — no changes to any fenced file.

## Wiring grep
```bash
grep -rn "_session_keys\|session_view_provenance\|_owning_session_reason" --include=*.py . | grep -v "def _session_keys\|def session_view_provenance\|def _owning_session_reason"
```
**Production call sites outside their own definitions: 4** —
- `_session_keys(binding, sid)` called from inside `session_view` (`scripts/hooks/spine_rail.py:556`) and inside `session_view_provenance` (`:582`)
- `session_view_provenance(binding, sid)` called from inside `decide_stop` (`:1447`)
- `_owning_session_reason(spine_path, owner_key)` called from inside `decide_stop` (`:1490`)

(Remaining grep hits are docstring prose in `spine_rail.py` and the new test call sites in `tests/test_spine_rail.py`.)

## Docs/contracts touched
- none

## Assumptions
- The exact wording of `_owning_session_reason` and the withheld-`additionalContext` string was left to inherited latitude per the handoff's Authority section; chosen wording states BLOCKED status, names the owner, and explicitly disclaims that the gate belongs to the stopping session.
- `owners.get(spine_path) is None` (provenance couldn't place the path — should not occur given `session_view` and `session_view_provenance` share the same `_session_keys` list, but handled defensively) falls back to the unchanged same-session rendering rather than the foreign-owner rendering, per the handoff's explicit "(or not present in owners, defensively)" instruction.

## Stop conditions hit
- none — `session_view`'s return shape stayed unchanged while sharing `_session_keys` with the new provenance function; `decide_session_start`'s behavior stayed untouched (code diff empty, regression test pins it); the block/allow decision for every existing test scenario is unchanged (full suite pass/fail set matches expectations, only the one named test's assertions were inverted per instruction).

## Out-of-scope observations
- none found during this gate.

## Workflow Feedback
- **Handoff gaps:** none — task, protected intent, close criteria, allowed scope, exclusions, constraints, evidence, verification commands, and stop conditions were all present and internally consistent; the exact line-number citations for `session_view`/`_mid_flight_reason`/`decide_stop` matched the pre-change file precisely, which made orienting fast.
- **Context rediscovered:** none beyond ordinary source reading — the handoff's own file:line anchors were accurate and sufficient; no map artifact was needed or missing (handoff correctly flagged DEGRADED-UNPARSEABLE map orientation upfront so no time was spent looking for a map entry point that doesn't exist).
- **Instructions improvised around:** the handoff's "Allowed Scope" for `tests/test_spine_rail.py` names one existing test as the sole permitted edit, plus "new tests," plus a "decide_session_start regression guard." For the regression guard I added a brand-new test (`test_session_start_composite_key_entry_still_renders_full_imperative_unchanged`) rather than extending `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key` as the handoff's own parenthetical suggested as one option ("reuse/extend ... or add a new small test — your call") — chose "add new" specifically to keep every other named existing test byte-for-byte unmodified, satisfying the stricter "every other existing test in this file must be unmodified" line in Allowed Scope without ambiguity.
- **What would have made this easier:** nothing material — this handoff was unusually precise (exact asymmetry called out, exact unpack site named, exact wording latitude scoped). No change suggested.

## Return status
`complete`
