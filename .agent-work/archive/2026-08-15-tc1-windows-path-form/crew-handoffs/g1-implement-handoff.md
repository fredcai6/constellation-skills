# Implementer Handoff

## Gate
g1 (tc1-windows-path-form)

## Task
Fix one test assertion in `tests/test_spine_origin_isolation.py` so
`RefusesAGuardedVerbFromAForeignTree::test_the_refusal_names_both_trees_on_stderr` passes on
Windows CI, without weakening what it proves.

Root cause (already verified against the code by the Commander, not a guess): the refusal
message's cwd-side now comes from `git rev-parse --show-toplevel`
(`scripts/checklist_engine.py` main(), ~line 3439), which git renders posix-form even on
Windows. The test's cwd-side assertion at line 517 still expects native-form
(`str(self.foreign)`), which only agrees with posix-form on POSIX — not on Windows. The
predicate's comparison (`os.path.normcase` both sides, `scripts/checklist_engine.py:170-174`)
already folds separators/case and is unaffected; this is a display/assertion mismatch only.

## Protected Intent
The property under test — the refusal names both trees on stderr — must survive intact.
Losing or weakening that assertion is not an acceptable way to make this test green.

## Test Mode
Test-after is what this gate IS — editing an existing test's assertion, not adding
production code. No TDD cycle applies; the "test" being fixed is itself the deliverable.

## Close Criteria
- `tests/test_spine_origin_isolation.py:517`'s cwd-side assertion changed from
  `self.assertIn(str(self.foreign), message)` to `self.assertIn(self.foreign.as_posix(), message)`
  — mirroring the stored-side pattern already used one line above it
  (`self.assertIn(self.worktree.as_posix(), message)`, line 516).
- No other line in this test changes. Exactly one line touched.
- `RefusesAGuardedVerbFromAForeignTree::test_the_refusal_names_both_trees_on_stderr` still
  passes on this (Linux) machine after the change (it already passes today since
  `self.foreign.as_posix() == str(self.foreign)` on POSIX — no separator difference there —
  so this is a no-behavior-change-on-POSIX edit).
- `OriginRefusalPredicate::test_it_is_pure` (same file) stays green and byte-unmodified.
- Full `tests/` suite stays green (see Verification Commands).

## Allowed Scope
`tests/test_spine_origin_isolation.py` — exactly the one assertion line named above.

## Specific Exclusions
- Do NOT touch `scripts/checklist_engine.py::origin_worktree_refusal` or its call site in
  `main()` — the comparison logic and its purity are out of scope (LAUNCH_ORDER Pre-Ruling
  1, "predicate-untouched"; `test_it_is_pure` pins this).
- Do NOT touch `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`, or `.mcp.json` — owned
  by other open PRs.
- Do NOT add normalization to the comparison, and do NOT "fix" the predicate — it is already
  separator-agnostic via `os.path.normcase`, confirmed by the Commander before this dispatch.
- Do NOT touch any other assertion, test, or line in this file.

## Constraints
- One assertion only. If satisfying the close criteria requires touching more than this one
  line, STOP and return `blocked` — do not improvise a larger fix.
- This is a Windows-only CI failure; you are running on Linux and cannot reproduce the
  Windows failure directly. Do not fabricate a Windows reproduction. Reason about correctness
  from the code (git's posix-form output on Windows, `os.path.normcase`'s Windows folding
  behavior) rather than claiming an observed run.

## Map Anchors (inbound)
- **Map entry point:** `map/tests.test_spine_origin_isolation/INDEX.md` (map is
  DEGRADED-UNPARSEABLE per the context step's orientation receipt; this packet file is one
  of the hash-pinned substitutes read instead).
- **Structural:** `tests/test_spine_origin_isolation.py`, class
  `RefusesAGuardedVerbFromAForeignTree`, method
  `test_the_refusal_names_both_trees_on_stderr` (~line 507-517).
- **Capability:** worktree-identity refusal message construction — only the test-side
  assertion changes; the message-construction code itself is untouched.
- **Constraints/assumptions:** file ownership fence — only this test file is writable this
  run; `test_it_is_pure` must remain green and unmodified.
- **Decision anchors:** Option (a) chosen over (b) per LAUNCH_ORDER "The judgment call" —
  update the test's cwd-side assertion to posix form rather than adding native-separator
  rendering to the refusal message.
  `@grade: settled/human · leans g1-implement · settle: n/a — ratified by LAUNCH_ORDER`
- **Evidence expectations:** the fixed assertion holds on both Windows and POSIX by
  construction — `engine_cwd` is always `git rev-parse --show-toplevel`'s stdout (posix-form
  on every platform including Windows), so `self.foreign.as_posix()` matches there, and
  `self.foreign.as_posix() == str(self.foreign)` already holds on POSIX.

## Deliverable Path Check
- **Committed** — `tests/test_spine_origin_isolation.py`; verified via
  `git check-ignore tests/test_spine_origin_isolation.py` exiting 1 (not ignored) before
  dispatch.

## Required Evidence
- The exact diff (before/after) of the one changed line.
- Output of running the single targeted test:
  `python -m pytest tests/test_spine_origin_isolation.py -q -k test_the_refusal_names_both_trees_on_stderr`
- Output of running the full file:
  `python -m pytest tests/test_spine_origin_isolation.py -q`
- Confirmation `test_it_is_pure` is unmodified: `git diff tests/test_spine_origin_isolation.py`
  shows only the one line, and the diff does not touch the `OriginRefusalPredicate` class.
- A short written argument (2-4 sentences) for why the new assertion holds on Windows
  (git's posix-form toplevel output) AND POSIX (as_posix() == str() there) — this is the
  "two-platform argument" the LAUNCH_ORDER asks the Commander to have; the Commander re-states
  it in the final report, but wants your independent confirmation as the one who touched the
  line.

## Wiring Grep
none — this slice edits an existing test assertion; it adds no new callable symbol.

## Verification Commands

```bash
git diff tests/test_spine_origin_isolation.py
python -m pytest tests/test_spine_origin_isolation.py -q
```

## Suggested Model Tier
simple bounded — one assertion, root cause and fix already fully specified.

## Authority
The fix (option (a): posix-form cwd assertion) is already decided by admiral-post-568's
LAUNCH_ORDER for tc1-windows-path-form and ratified by the Commander at the plan step. You
are not deciding (a) vs (b) — you are implementing the already-chosen (a).

## Stop Conditions
Stop and return `blocked` if: the fix requires touching more than the one named line: any
other test in this file starts failing after the change; `test_it_is_pure` fails or would
need modification; the allowed scope must be exceeded to satisfy the close criteria.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/tc1-windows-path-form/crew-handoffs/g1-implement-result.md` before ending your
turn: completed slice, files changed, test mode satisfied, evidence produced, assumptions
used, stop conditions hit, out-of-scope observations, workflow feedback. Return status field
lowercase (`complete`, `partial`, `blocked`, `out-of-scope`, or `failed`).
