# Implementer Handoff

## Gate
`g1`

## Task
Fix `finalize_from_exit_code` in `scripts/run_crew.py` (lines 954-1022) so a dispatch given BOTH `--spine`
and `--result` no longer inverts the archive verdict: when the result artifact is missing/stale, fall back
to `spine_terminal` instead of unconditionally reading `failed`.

## Protected Intent
A dispatch whose bound spine is genuinely terminal must read `completed`, even when its `--result` artifact
was relocated out from under it (the `archive` gate always does this). A dispatch whose bound spine is NOT
terminal, and has no result either, must keep reading `failed` — this fix must never become a rubber stamp.

## Test Mode
TDD required. Red (current code fails the new scenario) before green (fixed code passes it).

## Close Criteria
- When `result` is given and `result_exists`/`result_fresh` is False, AND `spine` is given and
  `spine_terminal(spine, root)` is True: `finalize_from_exit_code` sets `status = "completed"`, `final = 0`.
- When `result` is given and missing, AND `spine` is given but NOT terminal (or `spine` is `None`):
  `status` stays `"failed"` — unchanged from current behavior.
- `blocked_gate` is still checked first, ahead of both the result-artifact and the new spine-terminal
  fallback, whenever `spine` is given — unchanged from current behavior (do not reorder the existing
  `blocked_gate is not None` branch).
- A new field `entry["verdict_source"]` is set on every call, one of exactly `"blocked_gate"` | `"result"` |
  `"spine_terminal"` | `"none"` (pin these four literal strings — do not invent others): `"blocked_gate"`
  when `blocked_gate is not None`; `"result"` when the verdict was decided by the result-artifact path
  (`result is not None` and it was fresh, OR `result is not None` and it was stale/missing and spine did NOT
  rescue it); `"spine_terminal"` when the result was missing/stale and a terminal spine rescued it into
  `completed`; `"none"` when neither `result` nor `spine` was given at all (mirrors today's `result is None
  and spine is None` case, which currently falls through to `spine_terminal(None, ...)` → always `False` →
  `failed`).
- `result_exists`, `result_fresh`, `spine_terminal`, `spine_blocked_id` are UNCHANGED — this is a
  `finalize_from_exit_code`-only fix; do not alter their signatures or logic.

## Allowed Scope
`scripts/run_crew.py` (the `finalize_from_exit_code` function and its docstring only) and `tests/test_crew_launcher.py` (adding new test methods to the existing `FinalizeFromExitCodeTests` class; you may also touch other test files under `tests/` if and only if an existing test's scenario is directly invalidated by this change — name any such test explicitly in your result, do not silently edit others).

## Specific Exclusions
- Do not touch `scripts/checklist_engine.py` — the `archive` gate's relocation behavior is correct and out
  of scope; a lane other than yours is editing this file right now.
- Do not touch `scripts/hooks/spine_rail.py`, `.mcp.json`, or anything under `.worktrees/epic-568-441/` or
  `.worktrees/tc1-worktree-identity/`.
- Do not touch `result_exists`, `result_fresh`, `spine_terminal`, or `spine_blocked_id` themselves.
- Do not propose or implement telling Admirals to pass `--result` paths that survive archival — that
  alternative is rejected by the launch order that scoped this run.

## Constraints
- `blocked_gate` decided first, ahead of both other paths, unchanged.
- A genuinely failed crew (spine not terminal, no result) must still read `failed`.
- The three required test functions (below) must call `finalize_from_exit_code(` directly — no
  `unittest.mock.patch`/`MagicMock` wrapping of that function itself.
- Also answer, or explicitly mark not-established in your `IMPLEMENTER_RESULT`: (a) does any gate OTHER
  than `archive` relocate artifacts the launcher watches — grep `scripts/checklist_engine.py` for
  relocation/move behavior across all gates, not just `archive`; (b) should a `failed` verdict ever be
  recordable while the bound spine is terminal — state your read given what you just built, you do not need
  to resolve it, a reasoned "not established, here is why" is a valid answer.

## Map Anchors (inbound)
- **Map entry point:** none — this repo's derived code map (`map/ids.jsonl`) is DEGRADED-UNPARSEABLE
  (structurally empty, confirmed by a fresh `python -m scripts.code_map build --root .` still reporting
  `ids: 0`) for the whole repo, not specific to this area. Start directly from the source anchors below.
- **Structural:** `scripts/run_crew.py:954-1022` (`finalize_from_exit_code`, what you change);
  `scripts/run_crew.py:286-361` (`result_exists`/`result_fresh`/`spine_terminal`, read-only dependencies);
  `scripts/run_crew.py:364-` (`spine_blocked_id`, backs the existing blocked-first precedent).
- **Evidence expectations:** the three named tests below (Required Evidence) are the claims this gate must
  land.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; verified via `git check-ignore scripts/run_crew.py` exiting 1
  (not ignored) before dispatch.
- **Committed** — `tests/test_crew_launcher.py`; verified via `git check-ignore tests/test_crew_launcher.py`
  exiting 1 (not ignored) before dispatch.

## Required Evidence
Add these three test methods to `FinalizeFromExitCodeTests` in `tests/test_crew_launcher.py`. The class
already has helpers you should reuse rather than reinvent: `write_result_with_mtime(path, mtime)`,
`iso(ts)`, `_write_spine(path, done=<bool>)` (module-level, ~line 1327 — a minimal one-item spine, `complete`
when `done=True` else `pending`), `_write_blocked_spine(path, blocked_id=...)` (~line 1340). `self.BASE` is
the fixed epoch anchor already used by every test in the class.

- `test_finalize_terminal_spine_rescues_missing_result` — write NO result file (or write one that's stale
  via `write_result_with_mtime(root / "r.md", self.BASE - 60)`), write a terminal spine via
  `_write_spine(root / "spine.json", done=True)`, call `RC.finalize_from_exit_code(entry, exit_code=0,
  result="r.md", root=root, since=iso(self.BASE), spine="spine.json")`. Assert `final == 0`,
  `entry["status"] == "completed"`, `entry["verdict_source"] == "spine_terminal"`.
- `test_finalize_still_fails_when_spine_not_terminal` — no result file, write a non-terminal spine via
  `_write_spine(root / "spine.json", done=False)`, call with the same both-flags shape. Assert
  `entry["status"] == "failed"`, `entry["verdict_source"] != "spine_terminal"`.
- `test_finalize_blocked_wins_regardless_of_result_or_spine` — write a FRESH result file AND write a
  terminal spine, but make the spine ALSO blocked: extend `_write_blocked_spine` usage or hand-write a
  one-item spine whose single task is `status: "blocked"` (blocked is a status a spine can carry even for a
  single-item "terminal-looking" checklist — use `_write_blocked_spine(root / "spine.json", blocked_id="w1")`
  directly, since a blocked gate is never simultaneously terminal in this engine's vocabulary — confirm that
  reading `spine_blocked_id`/`spine_terminal` yourself before asserting). Call with `result` given AND fresh.
  Assert `entry["status"] == "blocked"`, `entry["blocked_gate"] == "w1"`, `entry["verdict_source"] ==
  "blocked_gate"`, regardless of the fresh result being present.

Only `test_finalize_terminal_spine_rescues_missing_result` is a genuine RED-before-GREEN case: under the
CURRENT (unfixed) code, `result` given-but-missing always yields `done = fresh = False` regardless of the
spine, so this test fails today and must pass after your fix. The other two
(`test_finalize_still_fails_when_spine_not_terminal`, `test_finalize_blocked_wins_regardless_of_result_or_spine`)
already pass under the CURRENT code (they exercise paths the fix must NOT change) — write and run them
first, before touching `finalize_from_exit_code`, to confirm that baseline, then keep them green through the
fix as regression proof. Derive both distributions mechanically, do not summarize from a glance:
1. Write all three tests. Run `python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or test_finalize_still_fails_when_spine_not_terminal or test_finalize_blocked_wins_regardless_of_result_or_spine" 2>&1 | tail -20` against the UNCHANGED `finalize_from_exit_code` — paste the actual output; expect exactly the rescue test failing (RED) and the other two passing.
2. Apply the fix. Re-run the same command — paste the actual output; expect `3 passed`.
Also run the full existing `FinalizeFromExitCodeTests` class before and after to confirm no existing test in
that class broke: `python -m pytest -q tests/test_crew_launcher.py::FinalizeFromExitCodeTests 2>&1 | tail -20`.

## Wiring Grep
`grep -rn "verdict_source" --include=*.py . | grep -v "def finalize_from_exit_code"` — state the count and
list every call site. `verdict_source` is a new dict key this gate adds; if nothing outside
`finalize_from_exit_code` itself and your three new tests reads it, that's expected (it's an internal
observability field the registry entry carries, not yet consumed elsewhere) — state that plainly rather than
treating zero external readers as a defect for THIS gate.

## Verification Commands
```bash
git check-ignore scripts/run_crew.py tests/test_crew_launcher.py; echo "exit:$?"   # expect exit 1 (neither ignored)
python -m pytest -q tests/test_crew_launcher.py::FinalizeFromExitCodeTests
python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or test_finalize_still_fails_when_spine_not_terminal or test_finalize_blocked_wins_regardless_of_result_or_spine"
```

## Suggested Model Tier
simple bounded — one function, three new tests, no cross-file design decisions.

## Authority
The fix's shape (fall back to `spine_terminal` only when the result is missing/stale, following the
`blocked_gate`-checked-first precedent) is already decided by the frozen launch order that scoped this run —
do not redesign it. The `verdict_source` field name and its four literal values are pinned by this handoff —
do not invent your own naming.

## Stop Conditions
Stop and return if: the fix cannot be made without ever letting a genuinely failed crew (spine not terminal,
no result) read as completed; the allowed scope must be exceeded; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT per `templates/IMPLEMENTER_RESULT.template.md`: completed slice, files changed,
test mode satisfied (paste the actual red-then-green pytest output, not a summary), evidence produced,
assumptions used, the two open-question answers (or "not established" with why), stop conditions hit,
out-of-scope observations, workflow feedback. Write it to
`.agent-work/crew-verdict-and-door/crew-handoffs/g1-implementer-result.md` before ending your turn. The
`Return status` field must be one of `complete | partial | blocked | out-of-scope | failed`, lowercase.
