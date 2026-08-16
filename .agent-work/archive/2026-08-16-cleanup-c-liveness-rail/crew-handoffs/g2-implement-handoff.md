# Implementer Handoff

## Gate
g2-implement (issue #549)

## Task
In `scripts/hooks/spine_rail.py`, stop `decide_stop` from rendering a subordinate's own next imperative into an orchestrator's Stop-block reason when the orchestrator's cwd happens to equal that subordinate's recorded worktree. Keep blocking exactly as often as today — only change the rendered text for an entry reachable ONLY through a per-agent (`sid#agent_id`) key.

## Protected Intent
`decide_stop` must refuse EXACTLY the same set of stops it refuses today. This gate changes what a block SAYS for one specific case, never whether it blocks. A change that lets a currently-blocked stop through is out of scope and must be floated, not implemented.

## Test Mode
Test-after allowed. One EXISTING test currently pins the bug being fixed and MUST be updated (not just supplemented) — see Close Criteria.

## Close Criteria
- Extract `_session_keys(binding: dict, sid) -> list[str]` — the ordered list of binding keys that "this session's view" merges: the bare `sid` key (if present) plus every per-agent key `sid + BINDING_KEY_SEP + <agent_id>`, in `binding`'s own iteration order. This must reproduce `session_view`'s EXACT current two-branch asymmetry from its existing code (read it first, at `scripts/hooks/spine_rail.py:515`): `key == sid` is an untyped equality check, while the prefix branch requires `isinstance(key, str) and key.startswith(prefix)`. Do NOT tidy this into a single coerced-to-str check — reproduce the asymmetry exactly, because an existing test's fixture (decoy keys of mixed shape) depends on it.
- Rewrite `session_view(binding, sid)` as a thin fold over `_session_keys`: same signature, same return shape (`{abs_spine_path: entry}`), same empty-`sid`/try-except-wrapped-never-raises behavior. The existing test `tests/test_spine_rail.py::test_session_view_merges_one_bare_and_two_composite_keys` (~line 493) must pass byte-for-byte unmodified — run it before and after your change and diff nothing but pass/fail.
- `decide_session_start` (`scripts/hooks/spine_rail.py:1438`) — the ONLY other caller of `session_view` — must be untouched in code and behavior. Do not edit it. Add a regression test asserting its output is unchanged by this gate (e.g. reuse/extend `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key`, or add a new small test — your call).
- Add `session_view_provenance(binding: dict, sid) -> dict[str, str]` — maps each `abs_spine_path` in `session_view(binding, sid)`'s result to the binding key that sourced it (the bare `sid`, or a composite `sid#agent_id` key). Built from the SAME `_session_keys(binding, sid)` list `session_view` uses (so the two can never disagree about what's visible to `sid`), with last-key-wins on a path collision — matching `session_view`'s own `dict.update` overwrite semantics exactly. Never raises; `{}` on anything unusable (`binding` falsy, `sid` falsy).
- Add `_owning_session_reason(spine_path: str, owner_key: str) -> str` next to `_mid_flight_reason` (`:1303`) — the rendered Stop-block reason for an entry reachable ONLY through a per-agent key. Must name the owning session/agent and must NOT include that spine's next imperative text. Exact wording is your call (inherited latitude: "the refusal wording") — but it must make clear the stop is still blocked, AND that this gate is not the stopping session's own to drive.
- In `decide_stop` (`:1351`): compute `owners = session_view_provenance(binding, sid)` once, alongside the existing `session_view(binding, sid)` call. When building `mid_flight`, also carry each entry's `spine_path` through (today it's the first tuple element, currently discarded via `_` at the render step's unpack — keep it). At the render step (today: `_, spine, aid = mid_flight[0]; reason = _mid_flight_reason(spine, aid); ctx = "ENGINE current -> " + reconstruct_current(spine)`), branch on `owners.get(spine_path)`:
  - `== sid` (or not present in `owners`, defensively) → UNCHANGED: `reason = _mid_flight_reason(spine, aid)`, `ctx = "ENGINE current -> " + reconstruct_current(spine)`.
  - `!= sid` (a per-agent-key-only entry) → `reason = _owning_session_reason(spine_path, owner_key)`, AND `ctx` must ALSO be changed to NOT embed the imperative — `reconstruct_current(spine)` renders `ACTIVE {aid} [...] -- {imperative}`, which is the SAME leak the fix removes from `reason`, through a second field. Use something like `ctx = "ENGINE current -> (withheld: gate belongs to {})".format(owner_key)` — exact wording your call, but it must not contain the subordinate's imperative text.
- The block/allow decision (`decision: "block"` vs `{}`), the nudge/strike counting (`journal_seq`, `active_ids`, `count`), and the `count >= 3` escape hatch are UNCHANGED by this gate — only the two rendered strings for a foreign-owned `mid_flight[0]` change. Verify by diffing the full `tests/test_spine_rail.py` suite's pass/fail set before/after, not just by adding new assertions.
- Update the EXISTING test `tests/test_spine_rail.py::test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` (~line 545) — it currently asserts `"COMPOSITE-MARKER" in out["reason"]`, which pins the pre-fix bug (its own docstring says so: "Before the read routing this Stop was allowed... which is exactly the silence being fixed" — that was about #419's silent-allow bug, not this one; this test's current assertion on the REASON TEXT is the #549 bug, not the fix). Invert: assert `"COMPOSITE-MARKER" not in out["reason"]` AND `"COMPOSITE-MARKER" not in out["hookSpecificOutput"]["additionalContext"]`, and assert the owning composite key (or the sub's agent id) appears in `reason` instead. Keep the existing `decision == "block"` and nudge-under-bare-`sid` assertions unchanged — both halves must still hold.
- Add a NEW control test: a mid-flight entry reachable through the BARE `sid` key (the ordinary same-session case — no subordinate involved) still renders the original imperative-bearing `_mid_flight_reason` text, unchanged. This proves the fix is scoped to per-agent-key-only entries, never a blanket rewording.
- No fenced file touched: `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`.

## Allowed Scope
- `scripts/hooks/spine_rail.py` — `_session_keys` (new), `session_view` (refactored, unchanged contract), `session_view_provenance` (new), `_owning_session_reason` (new), `decide_stop` (wiring change only, at the render step).
- `tests/test_spine_rail.py` — the ONE named test update (`test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key`), new tests for `_session_keys`/`session_view_provenance`/the control case, plus a `decide_session_start` regression guard. Every other existing test in this file must be unmodified and pass.

## Specific Exclusions
- Do not modify `decide_session_start` (`:1438`) or its own call to `session_view` — read-only reference.
- Do not modify `binding_key` (`:467`), `_foreign_worktree` (`:640`), `_mid_flight_reason` (`:1303`), or `_entry_mid_flight_view` (`:1323`) — they are used as-is; `_entry_mid_flight_view`'s existing per-entry foreign/unreadable/closed/honest-block filtering is unchanged, only what happens to a SURVIVING mid-flight entry's rendered text at the very end of `decide_stop` changes.
- Do not change the nudge/strike escape-hatch logic (`count >= 3`) or its keying (still by bare `sid` alone, never fragmented per-entry).
- Do not touch `scripts/run_crew.py` or `tests/test_crew_launcher.py` — that was a separate gate (g1, already complete).

## Constraints
- `_session_keys`, `session_view_provenance`, and `_owning_session_reason` should be genuinely testable in isolation (pure functions over `binding`/`sid`/`spine_path`/`owner_key` — no file I/O, no real session state).
- `session_view`'s return value must never raise and must return `{}` on any unusable input, exactly as it does today (empty/falsy `sid`, non-dict `binding` values, etc. — read the existing try/except wrapping before changing anything).

## Map Anchors (inbound)
Map orientation for this repo is DEGRADED-UNPARSEABLE at baseline `a69bbac4` (zero authored map anchors corpus-wide). No map artifact touches this gate; work from the file:line citations below.
- **Map entry point:** none — DEGRADED, see `.agent-work/cleanup-c-liveness-rail/MISSION_FRAME.md`.
- **Structural:** `scripts/hooks/spine_rail.py:515` `session_view()`; `:640` `_foreign_worktree()`; `:1323` `_entry_mid_flight_view()`; `:1303` `_mid_flight_reason()`; `:1351` `decide_stop()`; `:467` `binding_key()`; `:1438` `decide_session_start()` (read-only reference, do not change).
- **Capability:** Stop-hook mid-flight block — refuses a dishonest turn-end while a spine gate is still open; must keep refusing exactly as often.
- **Constraints/assumptions:** `session_view` has exactly two callers: `decide_stop` (in scope) and `decide_session_start` (explicitly out of scope — a regression test must pin its behavior unchanged). An existing test pins `session_view`'s exact dict shape and must keep passing unmodified.
- **Decision anchors:**
  - keep-the-block-drop-the-imperative — #549 changes the rendered reason (and additionalContext) only, never the gating outcome.
    `@grade: settled/human · leans g2-implement`
  - no-abandonment-by-inference — not directly load-bearing here, but the same non-negotiable applies: no side-effect writes.
    `@grade: settled/human · leans g2-implement`
- **Evidence expectations:** `tests/test_spine_rail.py::test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` (existing, currently pins the bug — must be updated, not just supplemented); `tests/test_spine_rail.py::test_session_view_merges_one_bare_and_two_composite_keys` (existing, must keep passing unchanged).
- **Map confidence flags:** none (DEGRADED, discharged).

## Deliverable Path Check
- **Committed** — `scripts/hooks/spine_rail.py`; verified via `git check-ignore scripts/hooks/spine_rail.py` exiting 1 (not ignored).
- **Committed** — `tests/test_spine_rail.py`; verified via `git check-ignore tests/test_spine_rail.py` exiting 1 (not ignored).

## Required Evidence
Both halves, per the mission's own framing ("or the test proves nothing"):
1. (load-bearing) The updated `test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` passing: `decision == "block"` (still refused) AND `"COMPOSITE-MARKER" not in reason` AND `"COMPOSITE-MARKER" not in additionalContext` AND the owning key/agent id appears in `reason` instead. Nudge-under-bare-`sid` assertion unchanged.
2. (load-bearing) The new control test: a bare-`sid`-owned mid-flight entry still renders the original imperative-bearing `_mid_flight_reason` text unchanged.
3. (load-bearing) `test_session_view_merges_one_bare_and_two_composite_keys` — run unmodified, green.
4. (confirmatory) `_session_keys`/`session_view_provenance` direct unit tests (bare-only, composite-only, mixed store reusing the existing fixture shape, empty/`None` sid).
5. (load-bearing) `decide_session_start` regression: unchanged behavior, asserted directly.
6. (confirmatory) Full clean-env suite: `find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py` — paste full output.

## Wiring Grep
```bash
grep -rn "_session_keys\|session_view_provenance\|_owning_session_reason" --include=*.py . | grep -v "def _session_keys\|def session_view_provenance\|def _owning_session_reason"
```
State the count of call sites found outside each definition.

## Verification Commands
```bash
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py
git diff --stat scripts/hooks/gauge_writer_hook.py scripts/checklist_engine.py scripts/mcp_spine_server.py
```

## Suggested Model Tier
Stronger — this gate touches a security-adjacent hook (the Stop-block rail) with a subtle cross-caller constraint (`decide_session_start` must not move) and an asymmetric existing-code detail (`_session_keys` must reproduce, not tidy, `session_view`'s two-branch check). Precision matters more than speed here.

## Authority
The provenance mechanism (shared `_session_keys` seam), the reason-wording approach, and which existing test to update are all already decided by the plan — implement as specified. The exact prose of `_owning_session_reason`'s message is yours to write (inherited latitude).

## Stop Conditions
Stop and return if: `session_view`'s return shape cannot stay unchanged while sharing `_session_keys` with the new provenance function, `decide_session_start`'s behavior cannot be kept untouched, or the block/allow decision for any existing test scenario would change.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (6 items above, load-bearing vs confirmatory noted), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full IMPLEMENTER_RESULT to `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-implement-result.md` before ending your turn — that write is the delivery.
