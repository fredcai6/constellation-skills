# tests.test_interrogation
tests/test_interrogation.py, 270 lines, 36 holes

Tests for the constellation-interrogator sharpening rail

(scripts/verify_interrogation.py).

The interrogator drives a survey to a joint understanding. This rail mechanically
enforces the two locked behaviors of DESIGN_SPEC Section D1 on the interrogation
RECORD (the survey's consolidated output):

  * FinishGateTests   -- no-quit-early: a record marked `consolidated` is REFUSED
                         unless it carries a joint-understanding sign-off (a real
                         `by` + `statement`) AND no question is still open. Loop
                         termination is not enough; the human sign-off is the gate.
  * DecisionBlockTests -- a `decision`-typed question marked resolved is REFUSED
                         without a non-empty `human_answer`: a decision is never
                         self-answered by the agent.
  * FactAllowedTests  -- a `fact`-typed question the agent resolved by exploring
                         code (non-empty `code_evidence`) is ALLOWED without a
                         human answer; a resolved fact with no evidence is refused.
  * RailExceptionTests -- a defended finish-gate exception passes ONLY with an
                         independent reviewer's co-sign + a log entry; self-
                         assertion never passes.
  * StructureTests    -- the record shape refusals + CLI exit codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
```

- [load](load.md) function: HOLE: no docstring
- [_fact](_fact.md) function: HOLE: no docstring
- [_decision](_decision.md) function: HOLE: no docstring
- [_signoff](_signoff.md) function: HOLE: no docstring
- [_record](_record.md) function: HOLE: no docstring
- [FinishGateTests](FinishGateTests.md) class: No-quit-early: consolidation refused without the joint-understanding sign-off.
  - [FinishGateTests.setUp](FinishGateTests.setUp.md) method: HOLE: no docstring
  - [FinishGateTests.test_consolidated_with_signoff_and_no_open_passes](FinishGateTests.test_consolidated_with_signoff_and_no_open_passes.md) method: HOLE: no docstring
  - [FinishGateTests.test_consolidated_without_signoff_refused](FinishGateTests.test_consolidated_without_signoff_refused.md) method: HOLE: no docstring
  - [FinishGateTests.test_consolidated_with_empty_signoff_statement_refused](FinishGateTests.test_consolidated_with_empty_signoff_statement_refused.md) method: HOLE: no docstring
  - [FinishGateTests.test_consolidated_with_empty_signoff_by_refused](FinishGateTests.test_consolidated_with_empty_signoff_by_refused.md) method: HOLE: no docstring
  - [FinishGateTests.test_consolidated_with_open_question_refused](FinishGateTests.test_consolidated_with_open_question_refused.md) method: HOLE: no docstring
  - [FinishGateTests.test_not_consolidated_needs_no_signoff](FinishGateTests.test_not_consolidated_needs_no_signoff.md) method: HOLE: no docstring
- [DecisionBlockTests](DecisionBlockTests.md) class: A decision is never self-answered: resolved decision needs a human answer.
  - [DecisionBlockTests.setUp](DecisionBlockTests.setUp.md) method: HOLE: no docstring
  - [DecisionBlockTests.test_decision_with_human_answer_passes](DecisionBlockTests.test_decision_with_human_answer_passes.md) method: HOLE: no docstring
  - [DecisionBlockTests.test_decision_resolved_without_human_answer_refused](DecisionBlockTests.test_decision_resolved_without_human_answer_refused.md) method: HOLE: no docstring
  - [DecisionBlockTests.test_decision_resolved_missing_human_answer_key_refused](DecisionBlockTests.test_decision_resolved_missing_human_answer_key_refused.md) method: HOLE: no docstring
  - [DecisionBlockTests.test_open_decision_needs_no_human_answer](DecisionBlockTests.test_open_decision_needs_no_human_answer.md) method: HOLE: no docstring
- [FactAllowedTests](FactAllowedTests.md) class: A fact resolved by exploring code is allowed without a human answer.
  - [FactAllowedTests.setUp](FactAllowedTests.setUp.md) method: HOLE: no docstring
  - [FactAllowedTests.test_fact_resolved_by_code_evidence_passes](FactAllowedTests.test_fact_resolved_by_code_evidence_passes.md) method: HOLE: no docstring
  - [FactAllowedTests.test_fact_resolved_without_evidence_refused](FactAllowedTests.test_fact_resolved_without_evidence_refused.md) method: HOLE: no docstring
  - [FactAllowedTests.test_fact_needs_no_human_answer](FactAllowedTests.test_fact_needs_no_human_answer.md) method: HOLE: no docstring
- [RailExceptionTests](RailExceptionTests.md) class: A defended finish-gate exception needs an independent reviewer co-sign.
  - [RailExceptionTests.setUp](RailExceptionTests.setUp.md) method: HOLE: no docstring
  - [RailExceptionTests.test_reviewer_cosigned_exception_passes](RailExceptionTests.test_reviewer_cosigned_exception_passes.md) method: HOLE: no docstring
  - [RailExceptionTests.test_self_asserted_exception_refused](RailExceptionTests.test_self_asserted_exception_refused.md) method: HOLE: no docstring
  - [RailExceptionTests.test_exception_does_not_excuse_self_answered_decision](RailExceptionTests.test_exception_does_not_excuse_self_answered_decision.md) method: HOLE: no docstring
- [StructureTests](StructureTests.md) class: HOLE: no docstring
  - [StructureTests.setUp](StructureTests.setUp.md) method: HOLE: no docstring
  - [StructureTests.test_empty_goal_refused](StructureTests.test_empty_goal_refused.md) method: HOLE: no docstring
  - [StructureTests.test_bad_mode_refused](StructureTests.test_bad_mode_refused.md) method: HOLE: no docstring
  - [StructureTests.test_no_questions_refused](StructureTests.test_no_questions_refused.md) method: HOLE: no docstring
  - [StructureTests.test_bad_question_kind_refused](StructureTests.test_bad_question_kind_refused.md) method: HOLE: no docstring
  - [StructureTests.test_bad_question_status_refused](StructureTests.test_bad_question_status_refused.md) method: HOLE: no docstring
  - [StructureTests.test_duplicate_question_id_refused](StructureTests.test_duplicate_question_id_refused.md) method: HOLE: no docstring
  - [StructureTests.test_skipped_question_needs_neither_answer_nor_evidence](StructureTests.test_skipped_question_needs_neither_answer_nor_evidence.md) method: HOLE: no docstring
  - [StructureTests.test_cli_refuses_unsigned_consolidation_nonzero](StructureTests.test_cli_refuses_unsigned_consolidation_nonzero.md) method: HOLE: no docstring
  - [StructureTests.test_cli_accepts_signed_consolidation_zero](StructureTests.test_cli_accepts_signed_consolidation_zero.md) method: HOLE: no docstring
