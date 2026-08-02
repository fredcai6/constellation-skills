# Staged constellation feedback (fenced delegated run — harvest into shared .agent-work/CONSTELLATION_FEEDBACK.md)

## reviewer-perturb-to-test-on-uncommitted-tree
- Lesson: reviewer-perturb-to-test-on-uncommitted-tree
- Scope: constellation (reviewer skill / commander gate hygiene)
- Origin: 638-f12-stability-rework, g2-review, 2026-07-18
- Finding: the constellation-reviewer's "prove the discriminating test can genuinely FAIL" step
  perturbs a source file then restores it. On this run the reviewed change was UNCOMMITTED (the
  commander commits at archive), so the reviewer's `git checkout -- <file>` reverted to HEAD and
  WIPED the implementer's uncommitted work; it recovered via `git apply` of a captured diff and
  md5-verified the restore.
- Recommendation: the reviewer skill's perturb-to-test guidance should state — on an uncommitted
  working tree, back up the target by FILE COPY and restore by copy; NEVER `git checkout`/`git
  restore` an uncommitted change (it reverts to HEAD, discarding peer work in the same tree).
  Alternatively the commander can commit the gate's change before dispatching the reviewer so
  `git checkout` is safe; but the copy-restore rule is the robust default.
- Corroboration: the commander independently ground-truthed the tree was intact afterward
  (numstat + fix markers + 23 tests) — recovery held, but the hazard is real and recurring-prone.

## handoff-simplification-limits-paths-flag
- Lesson: handoff-simplification-limits-paths-flag
- Scope: constellation (commander handoff authoring)
- Origin: 638-f12-stability-rework, g2-implement, 2026-07-18
- Finding: the commander authored the verification command `py -m src.utils.simplification_limits
  <paths>` (positional); the CLI requires `--paths <paths>`. The implementer caught and corrected
  it. Minor, but a recurring handoff-authoring slip worth a one-line note in the crew-dispatch /
  handoff reference (the canonical form is `--paths`, per this repo's CREW_CONTEXT).
