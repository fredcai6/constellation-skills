# tests.test_crew_launcher:BackendInvariantContractTests
class, tests/test_crew_launcher.py:1039, 41 lines

```python
class BackendInvariantContractTests(TestCase)
```

Decision 2: the result contract is backend-invariant — both backends verify

exists-AND-fresh identically against the entry's started_at via the single
`result_fresh`, never forked.

```python
BASE = 1000000000.0
```

- [_entry_for](BackendInvariantContractTests._entry_for.md) method: HOLE: no docstring
- [test_both_backends_verify_exists_and_fresh_identically](BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically.md) method: HOLE: no docstring

writes internal: BackendInvariantContractTests.BASE

referenced by: none found
