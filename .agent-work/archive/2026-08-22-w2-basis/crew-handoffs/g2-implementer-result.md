# Implementation Result

## Assigned gate
g2 (g2-implement)

## Completed slice
Hand-authored a `basis` field onto exactly `plan.c2`, `plan.c4`, `plan.c5` in the shipped `skills/commander/templates/COMMANDER_SPINE.template.json`, synced both overlay mirrors, and added a red-proof integration test class pinned to the shipped git HEAD.

## Scope
**Files changed:**
- `skills/commander/templates/COMMANDER_SPINE.template.json` (3 conditions edited: plan.c2/c4/c5)
- `.agent-work/templates/COMMANDER_SPINE.template.json` (sync copy)
- `.agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json` (sync copy)
- `tests/test_checklist_engine.py` (new `CommanderSpineBasisFields` test class only)

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, `scripts/generate_spine.py`, `specs/`, and every other condition in `COMMANDER_SPINE.template.json` are untouched (confirmed via `git diff` showing exactly the 3 target lines changed and `git status` showing no other files modified by this dispatch).

## Behavior changed
Yes — `plan.c2`/`c4`/`c5` now render a `basis:` sub-line under `current`/`render_human` output when open, and `attest`ing any of them now resolves the locator and attaches a report-only `basis-check` evidence item (g1's existing, unmodified mechanism). No blocking behavior changed: `attest` still unconditionally accepts these `check: null` conditions regardless of resolution outcome.

## Map Impact
- **Structural anchors touched:** `skills/commander/templates/COMMANDER_SPINE.template.json:plan.c2/c4/c5` — each gained a `basis` sibling object; `.agent-work/templates/` overlay mirror kept byte-identical.
- **Capabilities added/changed/affected:** none new — this is the first live *application* of g1's already-shipped basis mechanism to real template content, not a capability change.
- **Constraints/assumptions touched:** `ruling-engine-first-backfill-where-it-earns-it` honored (exactly these 3 conditions, not a rollout); `ruling-basis-lives-in-hand-written-templates` honored (surgical text edit, no `json.load`/`json.dump` round-trip); `ruling-red-proof-pinned-to-shipped-revision` honored (test pinned to `git rev-parse HEAD` at implementation time, skips if HEAD moves).
- **Decision candidates / resolved decisions:** none — the 3 conditions and their locator shapes were already ratified in `PLAN_ALTERNATIVES.md`, not re-derived here.
- **Claims/evidence produced:** `grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json` → 3; full `tests/test_checklist_engine.py` suite green at 514 passed/148 subtests (baseline before this gate: 511 passed/145 subtests — exactly +3 tests, +3 subtests, no regressions).
- **Trust limitations / drift found:** none — overlay/baseline copies were byte-identical to the shipped file before this gate started (checked per the handoff's stop condition), and remain byte-identical after.
- **Triage candidates:** none raised by this gate.

## Test mode
**Required:** test-first (TDD required for the new integration test)
**Satisfied:** yes — the new test class was written and run against the pre-edit template first, observed to fail, then the template was edited to make it pass.

## Evidence

```bash
cd /home/tommy/projects/569-w2-basis && python3 -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json')); print('parses ok')"
# -> parses ok
cd /home/tommy/projects/569-w2-basis && diff skills/commander/templates/COMMANDER_SPINE.template.json .agent-work/templates/COMMANDER_SPINE.template.json && echo "overlay matches"
# -> overlay matches
cd /home/tommy/projects/569-w2-basis && diff skills/commander/templates/COMMANDER_SPINE.template.json .agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json && echo "baseline matches"
# -> baseline matches
cd /home/tommy/projects/569-w2-basis && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_checklist_engine.py
# -> 514 passed, 148 subtests passed in 4.61s
cd /home/tommy/projects/569-w2-basis && grep -c '"basis"' skills/commander/templates/COMMANDER_SPINE.template.json
# -> 3
cd /home/tommy/projects/569-w2-basis && git rev-parse HEAD
# -> 9d5aac6daa58a72fc6a665cb39879ee5705f7f71
```

**Result:** pass — all verification commands from the handoff ran clean.

## TDD evidence, if required

- Failing test observed: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_checklist_engine.py -k CommanderSpineBasisFields -v` against the **pre-edit** template → 5 failures: `test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape` failed all 3 subtests (`AssertionError: None is not an instance of <class 'dict'> : plan.c{2,4,5} carries no basis object`); `test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key` failed (found `[]`, expected `['plan.c2','plan.c4','plan.c5']`); `test_live_checklist_from_the_template_renders_basis_lines_at_plan` failed (no `basis:` lines in `current()` output).
- Passing test observed: same command against the **post-edit** template → all 3 test methods pass (full-suite run above folds this in: 514 passed including the 3 new tests and 148 subtests including the 3 new `cond=c2/c4/c5` subtests).
- Refactor while green: no refactor needed — the edit was the minimal surgical insertion the handoff specified.

## Diff of the exact JSON inserted at each condition

**plan.c2** — inserted before the closing `}` of the condition object (after `"satisfied": false`):
```json
, "basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/execute.json"}, "because": "execute.json's own existence is checkable; whether its gates are genuinely cut from the frame and cover the full ownership scope stays a human/reviewer judgment call"}
```

**plan.c4** — inserted before the closing `}`:
```json
, "basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/plan-candidate-*.md", "glob": true, "min_matches": 2}, "because": "at least 2 candidate files must exist for a real design-it-twice panel to have run; PLAN_ALTERNATIVES.md's own convergence and the ordering claim stay a judgment call no file check can make"}
```

**plan.c5** — inserted before the closing `}`:
```json
, "basis": {"locator_kind": "file", "locator": {"path": ".agent-work/<work-id>/PLAN_CRITIC.md"}, "because": "the critic's findings file must exist; whether it was genuinely cold-read and triaged stays a judgment call"}
```

No other bytes in the file changed (`git diff` shows exactly these 3 lines touched; every other condition, including `plan.c1`, `plan.c3`, `plan.c6`, `reconcile.c1`, `archive.c2`, `init.c1`, and everything in every other gate, is byte-identical).

## Docs/contracts touched
- none — `docs/CHECKLIST_SCHEMA.md` was g1's scope and is untouched by this gate.

## Assumptions
- The exact `basis` field shape (`locator_kind`/`locator`/`because`, `file` kind's `path`/`glob`/`min_matches`) was taken from `docs/CHECKLIST_SCHEMA.md`'s "Basis" subsection and cross-checked against `scripts/checklist_engine.py`'s `_resolve_basis_locator` source directly, per the handoff's instruction not to trust the handoff's illustrative JSON alone. Both sources agreed exactly with the handoff's illustrative shapes, so no shape decisions were improvised.

## Stop conditions hit
- none. The live template's `plan.c2`/`c4`/`c5` text matched the handoff's quoted text exactly (byte for byte); g1's shipped `basis` shape matched the handoff's assumed shape exactly; overlay/baseline files were byte-identical to the shipped file before this gate started.

## Out-of-scope observations
- none.

## Workflow Feedback

- **Handoff gaps:** none — the handoff was unusually thorough (exact quoted condition text, exact basis shapes, explicit cross-check instruction, stop conditions, required evidence list). No field was missing or ambiguous.
- **Context rediscovered:** the dispatch environment's `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` pointed at the parent Commander's spine (`constellation/w2-basis/commander/commander`), not a spine bound for this crew — confirmed via this run's own `crew-runs.json` entry (`"spine": null`) before touching any engine state. This is a now-repeated pattern (documented in this agent's own memory from three prior occurrences on this same work-id and a sibling one) but the `constellation-implementer` skill's own text still opens with "a spine is bound for you before you start" unconditionally, with no branch for the `run_crew.py` `spine: null` case. Authored and drove my own plan under this crew's `scratch_dir` via the CLI instead, exactly as those prior occurrences did.
- **Instructions improvised around:** the skill's "a dispatched crew's spine is bound for you" opening assumes SPINE_FILE always names a spine that's actually mine. When `crew-runs.json` shows `spine: null`, that assumption is false and following it literally would mean driving the parent Commander's `execute` gate on its behalf — refused instead.
- **What would have made this easier:** the `constellation-implementer` skill branching on `crew-runs.json`'s own `spine` field for the current crew_id before assuming `SPINE_FILE` is bound to this run, the same fix already named in this agent's memory for the crew-dispatch skills generally.

## Return status
complete
