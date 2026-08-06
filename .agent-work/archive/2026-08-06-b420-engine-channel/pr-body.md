## Summary

Workstream B of epic #418: two engine-channel defects fixed in `scripts/checklist_engine.py`'s `current` projection.

- **RAIL echo de-duplication (`current` verb only, verb-aware).** `render_human()`'s `ACTIVE {id} [{status}] — {imperative}` line already prints the active gate's full imperative; the RAIL block appended at the CLI boundary repeated it a second time, but only on the `current` verb — the other five `RAIL_VERBS` (`claim`/`start`/`advance`/`attest`/`attach`) have no ACTIVE line and depend on the RAIL as their only "what's next" carrier, so they keep the full imperative unchanged. `_RAIL_STRINGS`'s frozen doctrine text is byte-identical to before; only the substituted `{imperative}` value changes, and only for `point == "current"`.
- **`anchors`/`constraints` rendering.** `state()`/`render_human()` never read a gate's `anchors`/`constraints` fields, even when populated — confirmed live and by a corpus grep across ~20+ real archived `execute.json` gates (issue-58, 99, 102-107, 87, 299, 304-310, epic-298 runs), where both fields carry real, structured content across three shapes (`{category: [str]}`, `{category: str}`, flat `[str]`) — not vestigial, so the renderer was built rather than deleting the fields.
- **Completeness property test** (`TaskFieldCompleteness`) enumerates a Task's fields and asserts every populated one renders in `current`'s output for a fully-populated fixture, so a future forgotten field fails loud instead of silently dropping — the same defect class as the two fixed here.
- `docs/CHECKLIST_SCHEMA.md` gains the `anchors` field (previously documented only in `commander-core.md` prose, not the schema's own Task table).

One rework cycle: the implementer's first pass on anchors-rendering broke on the `{category: str}` shape — exploded into ~90 lines, one per character — reproduced live against `skills/commander/templates/EXECUTE_PLAN.template.json`'s own shipped `g1-review` gate. Sent back with the live reproduction; fixed via a new `_anchor_category_items()` helper plus a regression test sourced verbatim from that shipped template line.

## Test plan
- [x] `python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q` — 397 passed, 24 subtests passed (388 baseline + 9 new tests, 0 regressions), independently re-run by both the Commander and the reviewer.
- [x] RED-before-GREEN independently reproduced (git-stash swap of the source file against the new test file).
- [x] `_RAIL_STRINGS` byte-identity independently confirmed via `ast.literal_eval` diff against `git show HEAD`.
- [x] Anchors dict-of-string shape (the shipped template's own `g1-review` gate) independently reproduced rendering as one clean line, not one-per-character.
- [x] `git diff scripts/checklist_engine.py | grep _check_condition` — 0 hits (shared-file fence with workstream D / #422 intact).

Driven end-to-end through `constellation-commander-delegated`'s spine (init → context → understand → plan → execute → reconcile → triage → review → feedback → archive); full trail in `.agent-work/archive/<date>-b420-engine-channel/` after this PR lands. Triage: 1 candidate filed as follow-up issue #433 (`directives` shares the same unrendered-defect class, out of this issue's authorized scope); the other (the `CHECKLIST_SCHEMA.md` doc gap) resolved in this PR itself.

Closes #420. Unblocks workstream C (#421), which relies on `anchors`/`constraints` actually rendering.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_015XQtwgzPxebsr3hjLRxJtN
