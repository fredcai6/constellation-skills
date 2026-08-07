# tests.test_prose_deletions
tests/test_prose_deletions.py, 143 lines, 12 holes

Pin the issue-#304 prose deletions in BOTH directions.

Two 86-word blocks of dead-path prose were deleted from the shipped Commander
templates: the `config_ref`-is-absent-by-design block in
`COMMANDER_SPINE.template.json` `tasks.context.imperative`, and its
byte-parallel twin in `EXECUTE_PLAN.template.json` `tasks.e0-context.imperative`.
They went because they are falsified in both directions at once: `docs/agents/`
**exists** in this repo (it holds `ORCHESTRATOR_CONTEXT.md`), so *"a skill-source
repo has no docs/agents/ overlay at all"* is false on its face; and Charter ships
a task that **writes** `docs/agents/engine-config.json`, so *"do NOT create the
overlay file"* contradicts a sibling role's shipped deliverable (#336).

**Absence alone is not the test.** The phrase `no docs/agents/ overlay at all`
occurred **twice** in `tasks.context.imperative`. The first occurrence is the
substitute-and-record rule -- the degraded-mode intake this whole issue exists to
*strengthen* -- and the second was inside the dead-path block. A naive
string-level delete removes both and silently strips degraded-mode intake while
appearing to remove only dead prose. That failure mode is pre-registered as
tripwire **T4** (`TRIPWIRES.md`, committed at `0119fa4` before any deletion
existed), and it is a tripwire aimed at the deleting edit itself.

So the deletion is pinned from both sides: the dead prose must be ABSENT, the
substitute-and-record rule must be PRESENT, and the phrase must occur EXACTLY
ONCE. An absence-only suite would pass just as happily on a template that had
deleted everything.

imports stdlib: __future__.annotations, json, pathlib.Path, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / 'skills' / 'commander' / 'templates' / 'COMMANDER_SPINE.template.json'
EXECUTE = ROOT / 'skills' / 'commander' / 'templates' / 'EXECUTE_PLAN.template.json'
SPINE_DEAD_OPENING = 'The checklist config_ref (docs/agents/engine-config.json) is absent-by-design'
EXECUTE_DEAD_OPENING = "This checklist's config_ref (docs/agents/engine-config.json) is absent-by-design"
DEAD_CLAIMS = ('a skill-source repo has no docs/agents/ overlay at all', 'do NOT create the overlay f...
SUBSTITUTE_AND_RECORD = 'Where the repo carries no docs/agents/ overlay at all (e.g. a skill-source repo), subs...
OVERLAY_PHRASE = 'no docs/agents/ overlay at all'
```

- [imperative](imperative.md) function: HOLE: no docstring
- [SpineDeadPathProseAbsent](SpineDeadPathProseAbsent.md) class: (a) The dead-path block is gone from the Commander spine's context step.
  - [SpineDeadPathProseAbsent.setUp](SpineDeadPathProseAbsent.setUp.md) method: HOLE: no docstring
  - [SpineDeadPathProseAbsent.test_opening_phrase_absent](SpineDeadPathProseAbsent.test_opening_phrase_absent.md) method: HOLE: no docstring
  - [SpineDeadPathProseAbsent.test_each_falsified_claim_absent](SpineDeadPathProseAbsent.test_each_falsified_claim_absent.md) method: HOLE: no docstring
- [ExecutePlanDeadPathProseAbsent](ExecutePlanDeadPathProseAbsent.md) class: (b) The byte-parallel block is gone from the execute plan's context step.
  - [ExecutePlanDeadPathProseAbsent.setUp](ExecutePlanDeadPathProseAbsent.setUp.md) method: HOLE: no docstring
  - [ExecutePlanDeadPathProseAbsent.test_opening_phrase_absent](ExecutePlanDeadPathProseAbsent.test_opening_phrase_absent.md) method: HOLE: no docstring
  - [ExecutePlanDeadPathProseAbsent.test_each_falsified_claim_absent](ExecutePlanDeadPathProseAbsent.test_each_falsified_claim_absent.md) method: HOLE: no docstring
- [SubstituteAndRecordRuleSurvives](SubstituteAndRecordRuleSurvives.md) class: T4, as a test: the load-bearing FIRST occurrence must survive.
  - [SubstituteAndRecordRuleSurvives.setUp](SubstituteAndRecordRuleSurvives.setUp.md) method: HOLE: no docstring
  - [SubstituteAndRecordRuleSurvives.test_substitute_and_record_rule_present](SubstituteAndRecordRuleSurvives.test_substitute_and_record_rule_present.md) method: HOLE: no docstring
  - [SubstituteAndRecordRuleSurvives.test_overlay_phrase_occurs_exactly_once](SubstituteAndRecordRuleSurvives.test_overlay_phrase_occurs_exactly_once.md) method: HOLE: no docstring
  - [SubstituteAndRecordRuleSurvives.test_surviving_occurrence_is_the_rule_not_the_dead_claim](SubstituteAndRecordRuleSurvives.test_surviving_occurrence_is_the_rule_not_the_dead_claim.md) method: HOLE: no docstring
- [DeclaredConfigRefPathStillNamed](DeclaredConfigRefPathStillNamed.md) class: The deleted block mentioned a declared `context_refs` path.
  - [DeclaredConfigRefPathStillNamed.test_engine_config_path_still_named_in_context_imperative](DeclaredConfigRefPathStillNamed.test_engine_config_path_still_named_in_context_imperative.md) method: HOLE: no docstring
