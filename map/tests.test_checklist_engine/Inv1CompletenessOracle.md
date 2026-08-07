# tests.test_checklist_engine:Inv1CompletenessOracle
class, tests/test_checklist_engine.py:4073, 78 lines

```python
class Inv1CompletenessOracle(TestCase)
```

#227 g2 constraint 3 (INV-1, completeness): current()'s output must be a

superset of every argument the caller's ACTUAL next legal verb needs. The
map below is HAND-AUTHORED against the verbs' RUNTIME bodies:

  - advance --why: optional at parse_args() (~line 1668) but REQUIRED at
    runtime unless --mechanical or the gate is why_exempt — see advance()
    ~1077-1087 (`raise EngineError(...)` on a why-less non-exempt advance).
  - attest --evidence: optional at parse_args() (~line 1715) but REQUIRED
    at runtime whenever the condition's check.kind == "artifact" — see
    attest() ~1539-1544 (`raise EngineError(...)` with no --evidence).

A map built by walking `parser._actions` for `required=True` would omit
BOTH of these — exactly the two args agents most often re-open source to
discover. This test does not call any engine map or read state()'s
next_verbs list; it inspects the rendered current() STRING directly, so it
cannot be a self-confirming fixture.

Rework 1 (g2 review BLOCK) split this into TWO scenarios instead of one:
while an open artifact-kind postcondition is unresolved, `advance` is not
yet the caller's legal next verb at all (only `attest --evidence` is), so
a single gate can't exercise both `--evidence` and `--why` truthfully at
once — the original combined test's premise ("advance is always next") was
exactly the bug this rework fixes.

```python
VERB_REQUIRED_ARGS = {'start': [('id', 'always')], 'advance': [('id', 'always'), ('why', lambda t, c=None: n...
```

- [test_current_output_covers_attest_evidence_when_that_is_the_legal_move](Inv1CompletenessOracle.test_current_output_covers_attest_evidence_when_that_is_the_legal_move.md) method: HOLE: no docstring
- [test_current_output_covers_advance_why_once_it_is_the_legal_move](Inv1CompletenessOracle.test_current_output_covers_advance_why_once_it_is_the_legal_move.md) method: HOLE: no docstring

calls stdlib: builtins.bool
writes internal: Inv1CompletenessOracle.VERB_REQUIRED_ARGS
unresolved: 3 calls (dispatch-unknown-base), 2 reads (unbound-name)

referenced by: none found
