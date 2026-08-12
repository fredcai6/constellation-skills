## Summary

Closes the falsification debt named in #436: `scripts/verify_worktree_precondition_coverage.py`'s
`WORKTREE_ENTERING_GATES` enumeration has only ever carried one entry (Commander's `init` gate),
so the loop had never been observed refusing on a genuinely new, second entry — only on the one
it already knew. This PR proves it does, both live and durably.

- **Live deliberate-breakage demo** (executed and reverted in this session, not shipped): added a
  throwaway `scoutbot` fixture template/gate as a second `WORKTREE_ENTERING_GATES` entry, ran the
  real CLI, observed a real refusal (`exit 1`) naming the exact new template path, gate id, and
  missing precondition marker — without falsely flagging the known-good Commander entry. Reverted;
  re-run confirmed `exit 0` again. Verbatim capture in `.agent-work/epic-418-redux/notes-436.md`.
- **Permanent regression test** (`EnumerationGeneralizesPastOneEntry` in
  `tests/test_worktree_precondition_wiring.py`): the same scenario, in-process, so this stays
  proven going forward — refuses and names a genuinely new second entry, stays silent on the
  known-good one, passes once the new entry is fixed.
- **One real gap found and closed**: the failure path never stated the enumerated count the way
  the success path already did (pre-ruling decision:count-is-part-of-the-output). Added
  `EnumerationStatesCountOnFailure` (TDD red → green) and the one-line fix in
  `verify_coverage()` — failure output now leads with `N of M worktree-entering template(s)
  checked failed:`.

**Verdict: the enumeration loop already discriminates correctly.** No defect found in the core
logic — this PR makes that a proven, durable fact instead of an unproven assumption, and closes
the one output gap the probe did find.

## Evidence

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` → `1724 passed, 4 skipped, 643 subtests
  passed in 648.07s`, exit 0 (LO-436 baseline at main `ca0e36a`: `1721 passed, 4 skipped, 643
  subtests` — delta is exactly the 3 new tests, zero regressions).
- Live refusal (verbatim in notes-436.md): `1 of 2 worktree-entering template(s) checked failed:
  skills/scoutbot/templates/SCOUTBOT_SPINE.template.json: gate 'init' does not wire ...
  'verify_worktree_isolation.py'`, exit 1 — then reverted, re-confirmed exit 0.
- Isolation proof: `python scripts/verify_worktree_isolation.py --here
  C:/Programs/constellation-skills-wt/r418-436` → `worktree OK`, exit 0.

## Scope

Touched only `scripts/verify_worktree_precondition_coverage.py` and its test file, per LO-436
fences. Did not touch `checklist_engine.py`, `episodes/`, `apply_episode_delta.py`, or
`collect_feedback.py` (concurrent sibling ownership: #433, #460, #464).

## Test plan

- [x] `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_worktree_precondition_wiring.py -v`
      — 5 passed
- [x] `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — 1724 passed, 4 skipped, 643 subtests,
      exit 0
- [x] Live CLI demo executed and reverted; `git diff` shows only the intentional count-message
      change

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TTKPTbD6nnMt7jFWw9GtjX
