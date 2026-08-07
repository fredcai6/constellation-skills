# tests.test_prototyper_templates
tests/test_prototyper_templates.py, 181 lines, 11 holes

Verifier<->template cross-check for the PROTOTYPE_RESULT.template.md gate.

g1-vocab (verdict enum, 4th disposition value) and g2-seam (workbench close via
the engine's generic artifact/match postcondition mechanism) shipped in
different gates. This suite proves them against each other with a REAL
fixture and the REAL vendored engine — never a hand-typed duplicate of the
enum strings, never a mocked engine — the exact failure mode
`lesson:verify-harness-field-and-drive-real-writer` names: a decision that
depends on a harness-supplied payload field must be verified against the
harness contract by driving the real writer path.

`prototype-result` is used here as a plain string tag to the engine's
existing generic `artifact`/`match` mechanism (like `user-decision` or
`review-result` elsewhere in this repo) — no new first-class `evidence_type`
is added to checklist_engine.py, and this suite never edits that file.

imports stdlib: json, pathlib.Path, re, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'skills' / 'prototyper' / 'templates' / 'PROTOTYPE_RESULT.template.md'
ENGINE = ROOT / 'scripts' / 'checklist_engine.py'
TEMPLATE_TEXT = TEMPLATE.read_text(encoding='utf-8')
VERDICT_VALUES = _extract_enum(TEMPLATE_TEXT, 'Verdict')
DISPOSITION_VALUES = _extract_enum(TEMPLATE_TEXT, 'Disposition')
```

- [_extract_enum](_extract_enum.md) function: Pull the backtick-quoted, pipe-separated enum on the line directly
- [PrototypeResultEnumExtraction](PrototypeResultEnumExtraction.md) class: Proves the extraction actually reads the shipped template's current
  - [PrototypeResultEnumExtraction.test_verdict_enum_extracted_from_real_template](PrototypeResultEnumExtraction.test_verdict_enum_extracted_from_real_template.md) method: HOLE: no docstring
  - [PrototypeResultEnumExtraction.test_disposition_enum_extracted_from_real_template](PrototypeResultEnumExtraction.test_disposition_enum_extracted_from_real_template.md) method: HOLE: no docstring
  - [PrototypeResultEnumExtraction.test_disposition_enum_carries_the_new_4th_value](PrototypeResultEnumExtraction.test_disposition_enum_carries_the_new_4th_value.md) method: HOLE: no docstring
- [_fixture_checklist](_fixture_checklist.md) function: HOLE: no docstring
- [PrototypeResultEngineRoundTrip](PrototypeResultEngineRoundTrip.md) class: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip.setUp](PrototypeResultEngineRoundTrip.setUp.md) method: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip.tearDown](PrototypeResultEngineRoundTrip.tearDown.md) method: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip._write_checklist](PrototypeResultEngineRoundTrip._write_checklist.md) method: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip._run](PrototypeResultEngineRoundTrip._run.md) method: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip.test_real_verdict_and_disposition_values_accepted_by_advance](PrototypeResultEngineRoundTrip.test_real_verdict_and_disposition_values_accepted_by_advance.md) method: HOLE: no docstring
  - [PrototypeResultEngineRoundTrip.test_off_vocabulary_verdict_is_refused_by_advance](PrototypeResultEngineRoundTrip.test_off_vocabulary_verdict_is_refused_by_advance.md) method: HOLE: no docstring
