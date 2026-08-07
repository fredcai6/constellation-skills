# tests.test_map_contract_wiring:ScriptIsBundled.test_map_orient_ships_with_every_skill_whose_template_invokes_it
method, tests/test_map_contract_wiring.py:256, 13 lines

```python
def test_map_orient_ships_with_every_skill_whose_template_invokes_it(self)
```

The drift this guards: `gauge_reader.py` was never added to any of

the ten bundles carrying `checklist_engine.py`, so the feature was inert
in every install since it shipped and nothing reported it. A command
postcondition naming a script that was never installed fails at the
gate, in a run, with a confusing error.

calls internal: ScriptIsBundled._installer, ScriptIsBundled.assertIn, ScriptIsBundled.subTest
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
