## Summary

Two one-line guard hardenings against the same defect family (a check that
cannot fail in the healthy-only world), in non-overlapping files. Closes #488,
closes #489.

- **#488**: `resolve_gauge_path` (`scripts/hooks/gauge_writer_hook.py`)
  appended one gauge-path candidate per binding with no dedup, so the caller's
  "2+ candidates is ambiguous, skip" check counted *bindings*, not *distinct
  paths*. Measured live: an Admiral bound to its own spine plus the
  `latitude` survey its own spine step requires (both under one work dir,
  both resolving to the same `gauge.json`) tripped the ambiguous-binding skip
  and ran a whole wave with its own context governor dark. Fix: dedup
  candidates by distinct `Path` before returning them. Same-path bindings now
  produce a real reading; genuinely different gauge paths still skip (#261's
  protection unweakened).
- **#489**: `tests/test_verify_spec_confirmed.py`'s live-spec fixture took
  `matches[0]` from a glob with no signal a second match existed — a quiet
  wrong answer inside a verification test. Extracted
  `_resolve_revised_spec_matches`, which now raises naming every match found
  on 2+; zero-match behaviour (skip) is unchanged.

## Test plan

- [x] Built the defective world for each issue and observed the current code
      getting it wrong before fixing (pasted in the result artifact and
      `.agent-work/epic-418-redux/notes-488-489.md`).
- [x] `tests/test_gauge_writer.py` — 70 passed (67 pre-existing + 3 new).
- [x] `tests/test_verify_spec_confirmed.py` — 26 passed (22 pre-existing + 4
      new), including both live-regression tests against the real,
      still-single `REVISED_SPEC.md`.
- [x] Full suite: see result artifact for the real exit code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TTKPTbD6nnMt7jFWw9GtjX
