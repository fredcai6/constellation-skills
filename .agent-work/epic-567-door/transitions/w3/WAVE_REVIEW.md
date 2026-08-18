## Wave review — boundary w3 (wave 2 complete, wave 3 authorized)

**Wave 2 delivered.** Five lanes, five merged PRs — #631 (D1), #629 (D2), #630 (E), #627 (F), #628 (H). `origin/main` runs **3374 passed, 6 skipped, 1219 subtests, 0 failed** in a clean detached worktree, up from 3191 at epic start. `git grep "CLI fallback"` over `skills/`, `specs/` and the tracked `.agent-work/templates/` overlay returns **zero**, and `tests/test_cli_retirement_guard.py` (718 lines) is on main to keep it that way.

**The wave's most valuable finding was why the text kept coming back.** `tests/test_mcp_adoption.py` *mandated* it across nine assertions, failing with "the CLI door must stay, never be removed or discouraged." Every earlier sweep was reverted by a red suite telling the deleter it had broken a rule. That mandate is now inverted, and the guard generalizes an in-tree precedent that already asserted absence for two files.

**Two lanes returned evidenced honest nulls**, and both were accepted on their evidence rather than their conclusion. #535's mechanism was already shipped — lane F cited its own launch as the proof. #442's premise did not reproduce across 11 cold subjects in four framings.

**Decision: advance to a third wave.** At this boundary the human overturned the Admiral's reading of the epic's own result. Three sites — a Commander's `execute.json`, an Interrogator's `interrogation.json`, an in-session crew's plan — reach the engine outside the door, and had been recorded as a documented limit. His ruling: an exception to the single access point is a failure. So #634 was filed and becomes lane K, alongside lane J carrying #619 and #633, which are one shape — a launcher taking a machine-local default instead of a declared one.

`execute` was reopened rather than left complete, cascading closeout back to pending, because a spine claiming the epic had ended would have been false.
