## Summary

Two documentation corrections, epic #418 wave 5, crew 5.

- **#496**: `docs/agents/CREW_CONTEXT.md`'s "pass `newline='\n'` explicitly on every write" rule
  didn't name `scripts/checklist_engine.py`'s `save()` as its known exception — `save()` write_bytes()s,
  deliberately preserving whichever line ending the target file already has instead of forcing
  one. Added one sentence naming that exception.
- **#411**: `.agent-work/archive/2026-08-02-issue-304/TREND_SNAPSHOT.md` §2 listed `_shared` as a
  20th peer row in its "per-role surface" table, contradicting `install_constellation.py`'s own
  exclusion rule (`_shared holds bundled refs, not a skill`) and the README's doctrine that
  `_shared` is not a skill. Dropped the row; noted the snapshot's true role count (19, at commit
  `fc1685a`) and `_shared`'s actual nature as bundled shared surface.

Both verified against source before editing (see `.agent-work/impl-w5-docs-496-411/notes.md`);
both held.

Not touched: `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — crew 4's exclusive
territory this wave.

## Test plan

- [x] Verified #496 against `docs/agents/CREW_CONTEXT.md` and `scripts/checklist_engine.py`'s
      `save()` — held.
- [x] Verified #411 against `TREND_SNAPSHOT.md` and `install_constellation.py`'s exclusion rule —
      held.
- [x] `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — 1867 passed, 2 skipped, exit 0
      (sanity check; no code changed).
- [x] `git diff --name-only` on the branch touches exactly the two intended files.

Closes #496, #411.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TTKPTbD6nnMt7jFWw9GtjX
