# Run summary — #530

- Isolation: verified in the repo-local linked worktree.
- Change: commit `97eb5d34` adds a strict lexical worktree derivation from
  absolute `.agent-work/<work-id>/<name>.json` paths at claim and unambiguous
  SessionStart binding writers; malformed paths bind nothing.
- Red/green: a real git main-plus-linked-worktree regression failed with the
  base writer recording stale main cwd, then passed after the correction. It
  exercises shared session, distinct agent ids, production claim/Stop/release/
  SessionStart paths.
- Verification: `python -m pytest -q tests/test_spine_rail.py` reports
  `111 passed, 1 skipped`; independent review APPROVE reproduces the named
  regressions and confirms no release/schema/lifecycle/#441 expansion.
- Reconcile: no packet map exists; a reasoned no-op is recorded and missing
  citable rail coverage remains escalated to the Admiral.
- Triage: no new candidate or filing; the unavailable `pytest` executable was
  journal-amended to the equivalent available `python -m pytest` invocation and
  recorded as evidence-only.
- Remaining risk: Windows has not been exercised, per the explicit wave
  allowance. No push, PR, or merge was attempted.
