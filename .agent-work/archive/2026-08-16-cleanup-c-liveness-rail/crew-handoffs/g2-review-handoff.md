# Reviewer Handoff

## Gate
g2 (issue #549)

## Survey State Location
`.agent-work/cleanup-c-liveness-rail/g2-review/review.json`

## What Was Implemented
`scripts/hooks/spine_rail.py`'s `decide_stop` used to render whichever mid-flight entry sorted first into the block reason — imperative text included — even when that entry was reachable only through a subordinate's per-agent (`sid#agent_id`) binding key, because `session_view` merged bare and composite keys into one dict with no record of which key sourced which path. Added `_session_keys` (the shared seam `session_view` now folds over, reproducing its exact bare/composite asymmetry), `session_view_provenance` (same seam, tracks the owning key per path), and `_owning_session_reason` (new wording for the foreign-owned case, no imperative). `decide_stop` now branches at the render step: bare-`sid`-owned entries render unchanged; per-agent-key-only entries render the new foreign-owner text in both `reason` and `additionalContext`. Committed as `915daefa` on branch `cleanup/c-liveness-rail`.

## How to Inspect the Diff
`git show 915daefa` — this is a linked worktree at `/home/tommy/projects/constellation-skills/.worktrees/cleanup-c-liveness-rail`, and the change is already committed. Prior commit `cbd18faf` (issue #599, `scripts/run_crew.py` only) is a separate, already-reviewed gate — do not re-review it.

## Task Statement
Keep `decide_stop` blocking exactly the same stops it blocks today; change ONLY the rendered `reason`/`additionalContext` text for a mid-flight entry reachable only through a per-agent key, so it names the owning session instead of relaying that gate's next imperative. Full original task in `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-implement-handoff.md`.

## Close Criteria
- `_session_keys(binding, sid)` reproduces `session_view`'s EXACT pre-existing two-branch asymmetry (untyped `key == sid` vs. `isinstance(key, str) and key.startswith(prefix)`) — read both the old and new code (`git show 915daefa~1:scripts/hooks/spine_rail.py` vs. the new version) and confirm the branch logic is identical, not tidied.
- `session_view`'s return shape and behavior are UNCHANGED — run `tests/test_spine_rail.py::test_session_view_merges_one_bare_and_two_composite_keys` yourself and confirm it passes with ZERO modification (diff the test file's own content for that test — it should be byte-identical).
- `decide_session_start` (`:1438`-ish) is untouched in code — confirm via `git show 915daefa -- scripts/hooks/spine_rail.py | grep -B3 -A3 "^[+-].*decide_session_start"` shows only comment-text mentions, never a change inside the function body. A new regression test should assert its behavior is unchanged — confirm it exists and passes.
- `session_view_provenance` is built from the SAME `_session_keys` list as `session_view` (read the code — they must call the same helper, not two independently-written loops that could drift).
- `decide_stop`'s block/allow decision, nudge/strike counting (`journal_seq`, `active_ids`, `count`), and the `count >= 3` escape hatch are BYTE-IDENTICAL in behavior to before this commit. Verify by running the FULL `tests/test_spine_rail.py` suite and confirming every pre-existing test still passes (not just the ones this gate touched) — a change to gating behavior would show up as a different pass/fail set, not just new assertions.
- BOTH `reason` AND `additionalContext` are checked for the foreign-owned case — read `_owning_session_reason` and the `decide_stop` wiring and confirm `additionalContext` no longer contains the subordinate's imperative (via `reconstruct_current`) when the owner is foreign. A fix that only touches `reason` and leaves `additionalContext` leaking is incomplete — BLOCK if you find this.
- The updated test `tests/test_spine_rail.py::test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` asserts BOTH halves: `decision == "block"` (still refused) AND `"COMPOSITE-MARKER" not in reason` AND the owning key/agent id appears instead — a test that only checks one half proves nothing per the mission's own framing.
- A control test exists proving a bare-`sid`-owned mid-flight entry (the session's own gate, no subordinate involved) still renders the ORIGINAL imperative-bearing `_mid_flight_reason` text unchanged — this proves the fix is scoped to foreign-owned entries only, not a blanket rewording. Find this test and confirm it actually exercises that path (not accidentally testing the same foreign-owned case twice).
- No fenced file touched: `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`. Confirm via `git show 915daefa --stat` showing only `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`.
- `scripts/run_crew.py` / `tests/test_crew_launcher.py` untouched by this commit (that was gate g1, already merged into this branch as `cbd18faf`) — confirm `git show 915daefa --stat` does not list them.

## Allowed Scope
`scripts/hooks/spine_rail.py` (`_session_keys`, `session_view` refactor, `session_view_provenance`, `_owning_session_reason`, `decide_stop` wiring), `tests/test_spine_rail.py` (the one named test update, new tests, one regression guard for `decide_session_start`).

## Specific Exclusions
`decide_session_start`, `binding_key`, `_foreign_worktree`, `_mid_flight_reason`, `_entry_mid_flight_view` (used as-is, not modified), the nudge/strike escape-hatch logic, every fenced file, and `scripts/run_crew.py`/`tests/test_crew_launcher.py` (separate, already-complete gate).

## Constraints the Implementation Must Respect
- `_session_keys`, `session_view_provenance`, `_owning_session_reason` should be genuinely testable in isolation (pure functions, no file I/O).
- `session_view` must never raise, `{}` on any unusable input — same as before.

## Map Anchors (inbound)
Map orientation is DEGRADED-UNPARSEABLE at baseline (zero authored map anchors corpus-wide) — no map artifact to check against; use file:line citations instead.
- **Structural:** `scripts/hooks/spine_rail.py` — `session_view()`, `_foreign_worktree()`, `_entry_mid_flight_view()`, `_mid_flight_reason()`, `decide_stop()`, `binding_key()`, `decide_session_start()` (read-only reference, must be untouched).
- **Capability:** Stop-hook mid-flight block — must keep refusing exactly as often.
- **Constraints/assumptions:** `session_view` has exactly two callers; `decide_session_start` is out of scope and must show zero behavior change.
- **Decision anchors:**
  - keep-the-block-drop-the-imperative — reason/additionalContext text only, never the gating outcome. `@grade: settled/human · leans g2-implement`
  - no-abandonment-by-inference — no side-effect writes. `@grade: settled/human · leans g2-implement`
- **Evidence expectations:** `test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` (updated, both halves) and `test_session_view_merges_one_bare_and_two_composite_keys` (unchanged, still green).
- **Map confidence flags:** none (DEGRADED, discharged).

## Evidence Produced
Full IMPLEMENTER_RESULT at `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-implement-result.md`. Independently reproduced by the Commander before this dispatch: `find . -name __pycache__ -type d -exec rm -rf {} + ; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py` → `150 passed, 1 skipped` (the skip is a pre-existing Windows-only test, unrelated to this change — confirm this yourself and name the skipped test). This evidence targets `g2-integrate.c1` (the test-suite postcondition) and `g2-review.c1` (this review's own `review-result` artifact).

## Suggested Model Tier
Stronger — this is a security-adjacent hook with a subtle shared-seam correctness requirement (session_view and session_view_provenance must never disagree) and a cross-caller non-regression requirement (decide_session_start). Read the actual render-step branching carefully, not just the new functions in isolation.

## Stop Conditions
Stop and return BLOCK if: `session_view`'s behavior changed for ANY input, `decide_session_start` shows any code or behavior change, the block/allow decision differs for any existing test scenario, `additionalContext` still leaks the imperative for the foreign-owned case, the updated test checks only one of the two required halves, or any fenced file / `run_crew.py` / `test_crew_launcher.py` shows a diff.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.

Write the full REVIEW_RESULT to `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-review-result.md` before ending your turn.
