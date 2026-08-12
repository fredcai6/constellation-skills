## Summary
- #464: `CONSTELLATION_FEEDBACK`'s `Lesson:` field carries an episode id since #447 retired the lessons playbook, but kept the old name. Renamed to `Episode:` in the template + doctrine header, together with its collector (`scripts/collect_feedback.py`) in one change.
- `fingerprint()`/`fingerprints()` read `entry['episode']` first, falling back to `entry['lesson']` — required for un-upgraded external exports and the legacy prose shapes (network_elo/story_time), which are deliberately not renamed since they're other projects' literal content. The internal hash prefix stays the literal `'lesson:'` string so existing fingerprints keep matching (no re-filing, no orphaned identities).
- Fixed a self-inflicted `verify_retirement.py` regression found while verifying: two docstring mentions of "episode store" tripped the `unapproved-store-mention` leg; reworded them, and updated the one `tests/data/store_mentions.approved.txt` census entry keyed to the exact template line whose field label moved.

## Evidence
- Enumeration before: `grep -rn -e '\*\*Lesson\[:*\]' -e '"lesson"' -e \'lesson\' -e 'Lesson field' scripts/ .agent-work/CONSTELLATION_FEEDBACK.md skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md tests/test_feedback_tooling.py` → 12 hits (3 changed in `collect_feedback.py`, 1 changed in `CONSTELLATION_FEEDBACK.md` header, 3 historical narrative lines left untouched, 2 changed in `template.md`, 2 renamed tests, 3 untouched external-shape tests).
- Same command after: 4 hits, all deliberately-kept fallback/external-format code — zero readers of the old field name remain in the must-fix set.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_feedback_tooling.py -k 'episode_id_groups_across_slug_drift or episode_id_takes_precedence_over_slug or legacy_lesson_field_format_still_fingerprints or episode_field_takes_precedence_over_legacy_lesson_field'` → 4 passed, real exit 0.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` → **1723 passed, 4 skipped, 643 subtests passed, real exit 0** (baseline was 1721 passed).

## Test plan
- [x] TDD red observed before implementation (3 of 4 named tests failed against the pre-rename collector; the 4th already passed by design)
- [x] TDD green after implementation (4 named tests + full `test_feedback_tooling.py`, 33 tests)
- [x] Full suite green, count strictly greater than baseline, real exit code captured
- [x] `verify_worktree_isolation.py --here` exits 0
- [x] `verify_retirement.py` scan clean (0 violations)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TTKPTbD6nnMt7jFWw9GtjX
