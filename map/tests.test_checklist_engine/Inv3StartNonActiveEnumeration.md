# tests.test_checklist_engine:Inv3StartNonActiveEnumeration
class, tests/test_checklist_engine.py:2759, 76 lines

```python
class Inv3StartNonActiveEnumeration(TestCase)
```

Finding 1 (g3-review rework 3 -> 4, the FOURTH instance of the same

anti-pattern). `start()`'s own "not the active gate" guard
(`checklist_engine.py` ~:1420) named an UNCONDITIONAL `start {active}`
exit -- self-recovering only in the one case every prior fixture could
express (`_make_non_active`'s guard hardcoded `status="pending"`), and
silently wrong whenever the active gate was actually `in-progress` or
`blocked` (both ordinary, reopen-cascade-reachable states). Fixed by
wiring `task_id`/`verb`/`status="pending"` onto that raise (the refusing
task IS always pending here -- the status!="pending" branch above it
already returns otherwise), routing it into the SAME
pending/GATED/non-active branch rework 3 already proved safe (never
guesses a command for the active gate; points at `current`) -- no new
branch, per the rework request's explicit instruction to reuse rather
than parallel-write.

Generated over `E.STATUS_VALUES` restricted to the statuses `active_id`
can actually return (non-terminal: `pending`/`in-progress`/`blocked`),
not hand-picked, so a future new status is not silently skipped.

```python
ACTIVE_GATE_STATUSES = tuple((s for s in E.STATUS_VALUES if s not in E.TERMINAL))
```

- [test_active_statuses_are_exactly_the_non_terminal_ones](Inv3StartNonActiveEnumeration.test_active_statuses_are_exactly_the_non_terminal_ones.md) method: HOLE: no docstring
- [test_generated_grid_never_names_a_refusing_command_for_the_active_gate](Inv3StartNonActiveEnumeration.test_generated_grid_never_names_a_refusing_command_for_the_active_gate.md) method: HOLE: no docstring
- [test_generated_grid_the_named_advice_current_never_refuses](Inv3StartNonActiveEnumeration.test_generated_grid_the_named_advice_current_never_refuses.md) method: HOLE: no docstring
- [test_reopen_cascade_reproduces_the_ordinary_reachability_path](Inv3StartNonActiveEnumeration.test_reopen_cascade_reproduces_the_ordinary_reachability_path.md) method: HOLE: no docstring

calls stdlib: builtins.tuple
reads internal: E x2
writes internal: Inv3StartNonActiveEnumeration.ACTIVE_GATE_STATUSES
unresolved: 2 reads (dispatch-unknown-base), 2 reads (unbound-name), 1 writes (unbound-name)

referenced by: none found
