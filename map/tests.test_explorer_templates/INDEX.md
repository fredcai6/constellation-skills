# tests.test_explorer_templates
tests/test_explorer_templates.py, 352 lines, 39 holes

Verifier<->template cross-check for the constellation-explorer engine artifacts.

The two halves of the hard gate ship in different gates: the verifier scripts
(g1) and the templates that must feed them (g2). This suite proves them against
each other with real fixtures and no mocks — a template that emits a format the
verifier cannot parse, or a fresh draft the verifier *passes*, would silently gut
"no work is cut from an unconfirmed design." (DESIGN_SPEC Testing pathways 1b/2.)

imports stdlib: importlib.util, json, pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'skills' / 'explorer' / 'templates'
SPINE_TEMPLATE = TEMPLATES / 'EXPLORER_SPINE.template.json'
CYCLE_TEMPLATE = TEMPLATES / 'CYCLE.template.json'
SPEC_TEMPLATE = TEMPLATES / 'DESIGN_SPEC.template.md'
ENGINE = ROOT / 'scripts' / 'checklist_engine.py'
BANNER = '**UNCONFIRMED — DO NOT CUT**'
STATUS_DRAFT = '- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**'
STATUS_CONFIRMED = '- **Status: CONFIRMED**'
CONFIRMED_BY_BLANK = '- Confirmed by:'
CONFIRMED_BY_FILLED = '- Confirmed by: tester (human)'
DATE_BLANK = '- Date:'
DATE_FILLED = '- Date: 2026-07-07'
EMPTY_ROW = "| F1 | intent-fit | MAJOR | worked example: the critic's attack on a deliberate decisi...
FILLED_ROW = "| F1 | intent-fit | MAJOR | worked example: the critic's attack on a deliberate decisi...
```

- [_load](_load.md) function: HOLE: no docstring
- [_require](_require.md) function: HOLE: no docstring
- [_without_banner](_without_banner.md) function: HOLE: no docstring
- [_fill_table](_fill_table.md) function: HOLE: no docstring
- [_confirmed](_confirmed.md) function: Edit the shipped DRAFT into a CONFIRMED spec touching only the designated
- [DesignSpecTemplateCrossCheck](DesignSpecTemplateCrossCheck.md) class: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.setUp](DesignSpecTemplateCrossCheck.setUp.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_shipped_draft_refused_confirm_phase](DesignSpecTemplateCrossCheck.test_shipped_draft_refused_confirm_phase.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_shipped_draft_refused_review_phase](DesignSpecTemplateCrossCheck.test_shipped_draft_refused_review_phase.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_draft_review_fails_when_table_incomplete](DesignSpecTemplateCrossCheck.test_draft_review_fails_when_table_incomplete.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_draft_review_passes_when_table_complete](DesignSpecTemplateCrossCheck.test_draft_review_passes_when_table_complete.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_confirmed_variant_passes_both_phases](DesignSpecTemplateCrossCheck.test_confirmed_variant_passes_both_phases.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_confirmed_variant_carries_no_residual_marker](DesignSpecTemplateCrossCheck.test_confirmed_variant_carries_no_residual_marker.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_blank_status_alone_fails_confirm](DesignSpecTemplateCrossCheck.test_blank_status_alone_fails_confirm.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_blank_confirmed_by_alone_fails_confirm](DesignSpecTemplateCrossCheck.test_blank_confirmed_by_alone_fails_confirm.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_blank_date_alone_fails_confirm](DesignSpecTemplateCrossCheck.test_blank_date_alone_fails_confirm.md) method: HOLE: no docstring
  - [DesignSpecTemplateCrossCheck.test_findings_table_uses_the_fixed_columns](DesignSpecTemplateCrossCheck.test_findings_table_uses_the_fixed_columns.md) method: HOLE: no docstring
- [CycleTemplateCrossCheck](CycleTemplateCrossCheck.md) class: HOLE: no docstring
  - [CycleTemplateCrossCheck.setUp](CycleTemplateCrossCheck.setUp.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.tearDown](CycleTemplateCrossCheck.tearDown.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck._write_cycle](CycleTemplateCrossCheck._write_cycle.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck._verify](CycleTemplateCrossCheck._verify.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.test_template_is_survey_and_ships_unconsolidated](CycleTemplateCrossCheck.test_template_is_survey_and_ships_unconsolidated.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.test_zero_cycles_fails_against_fresh_area](CycleTemplateCrossCheck.test_zero_cycles_fails_against_fresh_area.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.test_unconsolidated_cycle_from_template_fails](CycleTemplateCrossCheck.test_unconsolidated_cycle_from_template_fails.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.test_consolidated_cycles_from_template_pass](CycleTemplateCrossCheck.test_consolidated_cycles_from_template_pass.md) method: HOLE: no docstring
  - [CycleTemplateCrossCheck.test_one_unconsolidated_among_consolidated_fails](CycleTemplateCrossCheck.test_one_unconsolidated_among_consolidated_fails.md) method: HOLE: no docstring
- [CycleSurveyConfiglessRuntime](CycleSurveyConfiglessRuntime.md) class: HOLE: no docstring
  - [CycleSurveyConfiglessRuntime.setUp](CycleSurveyConfiglessRuntime.setUp.md) method: HOLE: no docstring
  - [CycleSurveyConfiglessRuntime.test_template_carries_no_dangling_config_ref](CycleSurveyConfiglessRuntime.test_template_carries_no_dangling_config_ref.md) method: HOLE: no docstring
  - [CycleSurveyConfiglessRuntime.test_engine_drives_cycle_survey_without_engine_config_file](CycleSurveyConfiglessRuntime.test_engine_drives_cycle_survey_without_engine_config_file.md) method: HOLE: no docstring
- [ExplorerSpineCrossCheck](ExplorerSpineCrossCheck.md) class: HOLE: no docstring
  - [ExplorerSpineCrossCheck.setUp](ExplorerSpineCrossCheck.setUp.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_steps_in_spec_order](ExplorerSpineCrossCheck.test_steps_in_spec_order.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_inline_rework_cap_is_99](ExplorerSpineCrossCheck.test_inline_rework_cap_is_99.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_explore_closes_on_user_decision_and_verify_cycles](ExplorerSpineCrossCheck.test_explore_closes_on_user_decision_and_verify_cycles.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_review_runs_verify_spec_confirmed_review_phase](ExplorerSpineCrossCheck.test_review_runs_verify_spec_confirmed_review_phase.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_confirm_needs_user_decision_and_verify_spec_confirmed](ExplorerSpineCrossCheck.test_confirm_needs_user_decision_and_verify_spec_confirmed.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_every_bundled_script_path_uses_the_generic_token](ExplorerSpineCrossCheck.test_every_bundled_script_path_uses_the_generic_token.md) method: HOLE: no docstring
  - [ExplorerSpineCrossCheck.test_instantiates_and_engine_can_claim_and_start](ExplorerSpineCrossCheck.test_instantiates_and_engine_can_claim_and_start.md) method: HOLE: no docstring
