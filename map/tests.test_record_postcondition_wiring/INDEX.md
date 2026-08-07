# tests.test_record_postcondition_wiring
tests/test_record_postcondition_wiring.py, 275 lines, 26 holes

Tests for #422 (epic-418 workstream D, gate g2): `record()`'s new command-kind

postcondition check (`scripts/checklist_engine.py`).

Before this change, `record()` (the survey verb) stored whatever result the agent
typed and never evaluated `postconditions` at all. This wires it to mirror
`advance()`'s existing pattern (reuse `_check_condition`, same `EngineError`
refusal shape) for `command`-kind postconditions ONLY, and ONLY when
`result == "pass"`:

  * RecordCommandPostconditionTests -- the generic mechanism: a passing command
    postcondition lets `record(pass)` through; a failing one refuses it;
    `record(fail)` is never blocked by the same failing check; an item with no
    command postcondition is unaffected (the regression floor).
  * InterrogationDeliberateBreakageTests / FowlerDeliberateBreakageTests -- the
    acceptance criteria: the REAL, unmodified `scripts/verify_interrogation.py`
    and `scripts/verify_fowler_pass.py` rails, invoked as a subprocess via a real
    command postcondition against a genuinely bad scratch record written to
    `tmp_path`, actually refuse `record(pass)`. Minimal invalid fixtures follow
    the shapes in `tests/test_interrogation.py` (`_decision(human_answer="")` --
    a resolved decision self-answered by the agent) and `tests/test_fowler_pass.py`
    (`_all_absent()` with one baseline smell dropped -- a skipped smell).

Loaded the same way as `tests/test_checklist_engine.py`: importlib from
ROOT/scripts, so these tests run against the real vendored engine module, not an
installed copy.

imports stdlib: __future__.annotations, copy, importlib.util, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'checklist_engine.py'
E = load_engine()
PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'
REQUIRED_SMELLS = ('long-method', 'large-class', 'duplicated-code', 'feature-envy', 'data-clumps', 'primi...
```

- [load_engine](load_engine.md) function: HOLE: no docstring
- [survey_item](survey_item.md) function: HOLE: no docstring
- [survey](survey.md) function: HOLE: no docstring
- [command_post](command_post.md) function: HOLE: no docstring
- [RecordCommandPostconditionTests](RecordCommandPostconditionTests.md) class: The generic mechanism, mirroring advance()'s own pattern.
  - [RecordCommandPostconditionTests.test_pass_with_passing_command_postcondition_succeeds](RecordCommandPostconditionTests.test_pass_with_passing_command_postcondition_succeeds.md) method: HOLE: no docstring
  - [RecordCommandPostconditionTests.test_pass_with_failing_command_postcondition_refused](RecordCommandPostconditionTests.test_pass_with_failing_command_postcondition_refused.md) method: HOLE: no docstring
  - [RecordCommandPostconditionTests.test_fail_never_blocked_by_failing_command_postcondition](RecordCommandPostconditionTests.test_fail_never_blocked_by_failing_command_postcondition.md) method: HOLE: no docstring
  - [RecordCommandPostconditionTests.test_item_with_no_command_postcondition_unaffected](RecordCommandPostconditionTests.test_item_with_no_command_postcondition_unaffected.md) method: HOLE: no docstring
  - [RecordCommandPostconditionTests.test_null_kind_postcondition_stays_unevaluated](RecordCommandPostconditionTests.test_null_kind_postcondition_stays_unevaluated.md) method: HOLE: no docstring
  - [RecordCommandPostconditionTests.test_record_refused_on_gated_unchanged](RecordCommandPostconditionTests.test_record_refused_on_gated_unchanged.md) method: HOLE: no docstring
- [_fact](_fact.md) function: HOLE: no docstring
- [_decision](_decision.md) function: HOLE: no docstring
- [_interrogation_record](_interrogation_record.md) function: HOLE: no docstring
- [InterrogationDeliberateBreakageTests](InterrogationDeliberateBreakageTests.md) class: Real, unmodified scripts/verify_interrogation.py run as a subprocess
  - [InterrogationDeliberateBreakageTests.setUp](InterrogationDeliberateBreakageTests.setUp.md) method: HOLE: no docstring
  - [InterrogationDeliberateBreakageTests.tearDown](InterrogationDeliberateBreakageTests.tearDown.md) method: HOLE: no docstring
  - [InterrogationDeliberateBreakageTests._item_for](InterrogationDeliberateBreakageTests._item_for.md) method: HOLE: no docstring
  - [InterrogationDeliberateBreakageTests.test_valid_record_lets_record_pass_through](InterrogationDeliberateBreakageTests.test_valid_record_lets_record_pass_through.md) method: HOLE: no docstring
  - [InterrogationDeliberateBreakageTests.test_self_answered_decision_refuses_record_pass](InterrogationDeliberateBreakageTests.test_self_answered_decision_refuses_record_pass.md) method: HOLE: no docstring
- [_smell](_smell.md) function: HOLE: no docstring
- [_all_absent](_all_absent.md) function: HOLE: no docstring
- [_fowler_record](_fowler_record.md) function: HOLE: no docstring
- [FowlerDeliberateBreakageTests](FowlerDeliberateBreakageTests.md) class: Real, unmodified scripts/verify_fowler_pass.py run as a subprocess against
  - [FowlerDeliberateBreakageTests.setUp](FowlerDeliberateBreakageTests.setUp.md) method: HOLE: no docstring
  - [FowlerDeliberateBreakageTests.tearDown](FowlerDeliberateBreakageTests.tearDown.md) method: HOLE: no docstring
  - [FowlerDeliberateBreakageTests._item_for](FowlerDeliberateBreakageTests._item_for.md) method: HOLE: no docstring
  - [FowlerDeliberateBreakageTests.test_complete_pass_lets_record_pass_through](FowlerDeliberateBreakageTests.test_complete_pass_lets_record_pass_through.md) method: HOLE: no docstring
  - [FowlerDeliberateBreakageTests.test_skipped_smell_refuses_record_pass](FowlerDeliberateBreakageTests.test_skipped_smell_refuses_record_pass.md) method: HOLE: no docstring
