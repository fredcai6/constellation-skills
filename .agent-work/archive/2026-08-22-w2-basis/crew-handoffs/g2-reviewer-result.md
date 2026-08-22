# Review Result

## Assigned Gate
g2 (g2-review)

## Result
APPROVE

## Handoff compliance
Full compliance. The handoff asked for `basis` authored on exactly `plan.c2`/`plan.c4`/`plan.c5`, matching the shapes ratified in `PLAN_ALTERNATIVES.md`, with a red-proof integration test pinned to the shipped revision. `git diff` on the shipped template shows exactly 3 lines changed, each gaining only a `basis` object; independently confirmed (a script scanning every task/condition in the file) that no other condition anywhere in the template carries a `basis` key. `<work-id>` remains an unresolved literal placeholder. HEAD is still `9d5aac6daa58a72fc6a665cb39879ee5705f7f71`, matching the new test's pin.

## Scope drift
None. `git status --porcelain` shows 6 modified files, but 2 of them (`docs/CHECKLIST_SCHEMA.md`, `scripts/checklist_engine.py`) are g1's own already-uncommitted work — nothing in this epic branch is committed per-gate, so g1's uncommitted diff is still visible alongside g2's. Confirmed byte-for-byte unchanged by g2: both files' diff-stat (37 and 108 insertion lines respectively) exactly match the counts g1's own IMPLEMENTER_RESULT reported before g2 started, and `git diff` shows zero deletions anywhere in the whole working tree. `tests/test_checklist_engine.py`'s diff is 100% additions, confined to one new class (`CommanderSpineBasisFields`) appended at the end of the file — the pre-existing g1 classes (`BasisAttestGuard`, `BasisRendering`) elsewhere in the same uncommitted diff are untouched. The 3 template files each show a clean +3/-3 surgical edit with unchanged total line count (142 before/after) — no `json.load`/`json.dump` round-trip.

## Evidence verdict
Independently reproduced every claim rather than trusting the transcript:
- `json.load` parses the shipped template cleanly.
- Overlay (`.agent-work/templates/COMMANDER_SPINE.template.json`) and baseline (`.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json`) are byte-identical to the shipped template (`diff` empty both ways).
- Swapped the shipped template back to its pre-g2 (git-HEAD) content and reran `py -m pytest -k CommanderSpineBasisFields -v`: 5 real failures (3 subtests on `test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape` plus `test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key` and `test_live_checklist_from_the_template_renders_basis_lines_at_plan`), matching the implementer's quoted RED transcript.
- Restored the edited template (diff against a pre-restore backup: identical) and reran the same `-k` filter: 3 passed clean (GREEN).
- Full suite: `514 passed, 148 subtests passed` — exactly +3 tests / +3 subtests over g1's reported baseline of 511/145.
- `GoldenOutputBriefing`/`TemplateOnlyFieldAllowlist` both green (10/10) against the real shipped template carrying a real `basis` field for the first time.

TDD evidence in the implementer result is consistent with this independent reproduction (red observed pre-edit, green post-edit).

## Code/doc quality
Minimal, surgical change. Cross-checked the authored `basis` shape against `docs/CHECKLIST_SCHEMA.md`'s Basis subsection (line 296+) directly: `locator_kind: file` + `locator.path` + optional `because` matches the documented example and field table exactly; `plan.c4`'s glob/`min_matches` fields match the documented file-locator shape. New test class follows the file's existing conventions (gate-tagged docstring, `_skip_if_head_moved` pin pattern) consistent with the sibling `BasisRendering`/`BasisAttestGuard` classes from g1.

**Fowler pass** (`r6-fowler`, recorded to `.agent-work/w2-basis/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0): 11 of 12 baseline smells absent; 1 overridden — `data-clumps` (the `{locator_kind, locator, because}` shape repeats identically across `plan.c2/c4/c5`), logged standard: `docs/CHECKLIST_SCHEMA.md`'s Basis subsection defines this as the single documented shape for every basis-bearing condition; reason: this is schema-conforming JSON config data, not a repeated in-code parameter group, and the epic's exactly-3 cap makes extracting a builder for 3 literals premature abstraction.

## Map impact verdict
- **Evidence supports claimed change:** yes — the diff, JSON validity, byte-identical overlay/baseline, and reproduced red→green all back the implementer's claimed behavior exactly.
- **Constraints not violated:** yes — `ruling-engine-first-backfill-where-it-earns-it` (exactly 3, not more), `ruling-basis-lives-in-hand-written-templates` (surgical text edit, confirmed no round-trip), `ruling-red-proof-pinned-to-shipped-revision` (pinned to HEAD, real skip path if HEAD moves) are all honored.
- **Notes match the diff:** yes — the implementer's Map Impact notes name exactly the anchors touched (`plan.c2/c4/c5`) and claim no new capability (correct: this applies g1's already-shipped mechanism to real content, not a capability change).
- **Decision candidates surfaced:** n/a — the 3 conditions and shapes were already ratified in `PLAN_ALTERNATIVES.md`, not re-derived here, correctly.
- **Durable context routed:** yes — nothing new to route; this gate's scope was fully bounded by the prior plan.

## Reconciliation check
None. This gate applies an already-shipped, already-documented mechanism (g1) to real template content in exactly the 3 conditions ratified by `PLAN_ALTERNATIVES.md`. No architecture baseline concerns.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback

- **Handoff gaps:** none — the handoff was thorough (exact ratified shapes, exact close criteria, exact stop conditions) and the "expect exactly 4 files touched" wording needed one clarifying inference: it means the 4 files g2 itself may add diffs to, not that `git status` overall shows only 4 files — this epic branch never commits per-gate, so g1's own uncommitted `scripts/checklist_engine.py`/`docs/CHECKLIST_SCHEMA.md` diff is still visible alongside g2's. Worth a one-line clarification in future handoffs of this shape ("g1's uncommitted diff will still show — verify it is byte-identical to g1's own reported diff-stat, not that it's absent").
- **Context rediscovered:** this crew's own `crew-runs.json` entry carries `spine: null` and `SPINE_SESSION`/`SPINE_FILE` in the environment resolve to the parent Commander's own spine, not a spine bound for this crew — confirmed before touching any engine state, consistent with the same pattern g1's implementer and reviewer already hit on this same work-id. Per the reviewer skill's own branch for this case, authored and drove an independent `REVIEW_SURVEY` at the handoff's named location instead of touching the Commander's `execute.json`.
- **Instructions improvised around:** none beyond the above — the reviewer skill already names the `spine: null` branch explicitly ("Do not author a survey of your own when a spine is already bound... only for the case where nothing is bound"), so this was compliance with documented skill guidance, not an improvisation.
- **What would have made this easier:** nothing concrete for this gate specifically. One self-correction worth naming: while authoring `.agent-work/w2-basis/FOWLER_PASS.json` I initially dropped a closing brace in the hand-typed `data-clumps` override entry (3 open braces, 2 close) — caught immediately by `verify_fowler_pass.py`'s refusal (`Expecting property name enclosed in double quotes`) rather than a silent bad record, exactly the rail's job. Fixed and reverified before recording.

## Return status
complete
