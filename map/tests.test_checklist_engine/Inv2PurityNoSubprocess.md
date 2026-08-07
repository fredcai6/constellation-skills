# tests.test_checklist_engine:Inv2PurityNoSubprocess
class, tests/test_checklist_engine.py:4153, 29 lines

```python
class Inv2PurityNoSubprocess(TestCase)
```

#227 g2 constraint 2 (INV-2, purity): state()/current() must NEVER

invoke subprocess for a command/git-change-policy check — reading state is
not a probe. Patches subprocess.run to explode if called, drives current()
over a spine full of command- and git-change-policy-kind conditions
recorded as unsatisfied, and asserts it renders (without raising from
current() itself) while subprocess.run is never reached.

- [test_current_never_invokes_subprocess](Inv2PurityNoSubprocess.test_current_never_invokes_subprocess.md) method: HOLE: no docstring

referenced by: none found
