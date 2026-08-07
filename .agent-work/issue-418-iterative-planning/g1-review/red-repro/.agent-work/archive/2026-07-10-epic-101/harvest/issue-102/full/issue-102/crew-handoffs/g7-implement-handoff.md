# Implementer Handoff

## Gate
g7-implement (issue #102, Move 11 — mechanical regression net)

## Task
Add the regression net to `tests/test_install_constellation.py`, modeled on
`test_deep_module_vocabulary_ships_into_installed_skill` (line ~679). Two test classes plus wiring.
Do NOT create a new `global-*.md` filename. Add tests only (no production edits).

### (1) Content-pin test(s) — a signature of each relocated doctrine ships to its INSTALLED destination
Install a skill (as the model test does: `installer.main([... "--skills", <skill>], ...)`), read the
bundled destination file, assert the signature is present. Destinations differ by bucket:

EVERYONE moves — assert on ANY installed skill's bundled `references/global-everyone.md` (bundles to all):
- Move 1 boilerplate: signature `reporting misfit is compliance` (in "## Engine-drive compliance").
- Move 2 engine-mechanism pointer: signature `checklist-engine.md` (the mechanism pointer in the same section).
- Move 4 scoped-nulls: signature `never the idea class` (in "## Scoped nulls").
- Move 5 world-verification: signature from the heading `Verify claimed side-effects against the world`.
- Move 8 delegate-not-replacement: signature from the heading `A delegate is not a replacement`.

ORCHESTRATOR moves — assert on an ORCHESTRATOR skill's bundled `references/global-orchestrator.md`
(bundles ONLY to orchestrator tier — use `commander`, NOT a crew skill):
- Move 6 unchanged-tree: signature `Unchanged-tree shortcut`.
- Move 7 crew-idle: signature `Idle subagent adjudication` (or `idle_notification`).

SINGLE-HOME move:
- Move 9 sibling-ids: assert on `constellation-lessons-auditor`'s installed `SKILL.md` — signature
  `forks its identity` (the home keeps the full rule).

MOVE-10 canonical (its restatements were cut to pointers by #99; guard the canonical still ships):
- assert the design-it-twice canonical ships in the orchestrator bundle — signature `Design-it-twice`
  in commander's bundled `references/global-orchestrator.md` (or in the bundled `design-it-twice-brief.md`).

You may implement these as one parametrized/subtest test or several small tests — your call; each moved
doctrine must have its own asserted signature so a dropped/mangled relocation fails a test.

### (2) No-residual-duplicate test — retired inline signature must NOT reappear in the CARRIER it was cut from
CRITICAL SCOPING (get this exactly right or the test false-fails):
- The residual grep globs `skills/**/SKILL.md` **ONLY**. EXCLUDE every `references/` file — both the
  bundled `_shared` copies (which legitimately carry the rule now) AND deliberately-retained role
  references (`workbench/references/checklist-engine.md`, `prototyper/references/{measurement,ui}.md`,
  `admiral/references/fleet-doctrine.md`). Read the SOURCE tree `skills/`, not an install.
- Most moves' home is a `_shared` bucket (a reference, excluded), so "signature absent from ALL
  SKILL.md bodies" is correct for them. Residual signatures (each must be absent from all SKILL.md):
  - boilerplate: `reporting misfit is compliance`
  - banner: `FOLLOW THIS SKILL STRICTLY` (count 0)
  - world-verification: `not on what the result claims` AND `never on what the report asserted`
    (NOT `claimed side-effect` — the carrier pointers legitimately echo that section name)
  - delegate-not-replacement: `delegate is not a replacement`
  - unchanged-tree: `Unchanged-tree shortcut`
  - crew-idle: `idle_notification`
- EXCEPTION — Move 9's home is `lessons-auditor/SKILL.md` (a SKILL.md, NOT a bucket), which
  legitimately KEEPS the full rule. So the sibling-ids residual must be scoped to the CARRIER admiral
  only: assert the delegated rationale `breaks recurrence counting` is absent from
  `skills/admiral/SKILL.md` (present in lessons-auditor is fine). Do NOT assert it absent from all SKILL.md.

Falsification (state in the test docstring): restore an inline copy into a carrier SKILL.md → residual
test goes red; drop the bucket line → the matching content-pin goes red.

## Test Mode
test-after (this gate IS the test net). Full suite must be green including the new tests.

## Close Criteria
- Content-pin present for each moved doctrine (moves 1,2,4,5,6,7,8,9 + move-10 canonical), asserting on
  the CORRECT installed destination (everyone→any skill; orchestrator→commander; move 9→lessons-auditor).
- No-residual test present with the SKILL.md-only scoping and the move-9 admiral-scoped exception.
- No new `global-*.md` filename; existing structural tests unchanged and still green.
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
`tests/test_install_constellation.py` (additions) and, only if you prefer, a new `tests/test_*.py` file
you create. NOTHING else — no production/skill edits.

## Specific Exclusions
Do NOT edit any skills/ file (the moves are done and merged). Do NOT weaken existing structural tests.
Do NOT add a `global-*.md`. manifest/ROADMAP/repo-root stray (#105).

## Constraints
- Model on `test_deep_module_vocabulary_ships_into_installed_skill`.
- Residual globs `skills/**/SKILL.md` only; move-9 residual scoped to admiral/SKILL.md.
- Use the installer's own `main([...])` entry (see existing tests) to produce installs in a tmpdir.

## Map Anchors (inbound)
- Structural: tests/test_install_constellation.py:679 (model); install_constellation.py bundle map (everyone→all, orchestrator→orchestrator tier).
- Constraint: no new global-* filename; existing glob test untouched.
- Decision: mechanical net added by cluster A itself.

## Deliverable Path Check
- Committed — tests/test_install_constellation.py (tracked, not ignored).
- Local-only — .agent-work/issue-102/crew-handoffs/g7-implement-result.md.

## Required Evidence
Full `py -m pytest tests/ -q` output tail (green, new tests counted); list the new test names; show one
content-pin and the residual test body; a NOTE that you sanity-checked the residual scoping by
confirming the moved signatures are absent from SKILL.md bodies but present in the bundled buckets.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
py -m pytest tests/ -q
py -m pytest tests/test_install_constellation.py -q -k "pin or residual or relocat" -v   # your new tests
```

## Suggested Model Tier
stronger — the residual scoping (SKILL.md-only, move-9 exception) and correct per-bucket content-pin
destinations are the crux; getting them wrong yields false-pass/false-fail tests.

## Authority
Test placement/naming/shape are yours. The scoping rules above are contractual (from the plan-critic
triage). Report if a signature you were given does not actually appear where expected.

## Stop Conditions
Stop if: a content-pin cannot find its signature in the expected installed destination (means a prior
move regressed — report it), or the residual scoping cannot be expressed without false-failing on a
retained reference.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g7-implement-result.md AND as
your final message): new test names, content-pin + residual bodies (or key excerpts), full suite tail,
scoping sanity-check note, assumptions, stop conditions, out-of-scope observations, workflow feedback.
Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT.
