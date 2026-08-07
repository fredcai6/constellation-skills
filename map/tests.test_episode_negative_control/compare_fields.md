# tests.test_episode_negative_control:compare_fields
function, tests/test_episode_negative_control.py:172, 21 lines

```python
def compare_fields(expected: dict[str, Expect], actual: dict) -> list[str]
```

The comparison. Returns the names of the fields that do not match, in

`MECHANICAL_GROUP` order.

A list rather than a bool, deliberately: a boolean control can only say "something
is wrong", which is indistinguishable from a wrapper mapping any non-zero exit to
RED. Naming the field is what makes a red-proof discriminating.

An `Expect(REFUSED, ...)` field must be ABSENT. Present-when-refusal-was-expected is
a mismatch, which is what keeps the refusal assertions falsifiable.

reads internal: MECHANICAL_GROUP, REFUSED
reads stdlib: builtins.list, builtins.str
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 7 sites, this module only
