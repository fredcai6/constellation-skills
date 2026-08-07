# tests.test_context_determinism:RealCheckoutSkew
class, tests/test_context_determinism.py:393, 230 lines

```python
class RealCheckoutSkew(TestCase)
```

The untracked-vs-absent case, stated rather than masked.

A path that is untracked-but-present here and absent in a clean checkout is a
real difference in what was *delivered*, and the manifest is a delivery record,
so the two manifests SHOULD disagree on that row's `rev`. What must never
differ is the record's shape: same step, same rows, same order.

**The skew is materialised, not hoped for.** An earlier version of this class
projected the shipped Commander declaration, whose every path is legitimately
absent from a skill-source tree — so all six rows were `rev: None` on both
sides, the "revs differ" branch never executed, and the class could not fail.
The declaration below therefore names real **tracked** files (identical in both
trees, so their revs must AGREE — the determinism half) alongside one file this
test creates untracked in the working tree only (so its rev must DIFFER — the
skew half). Both halves are asserted to have actually occurred.

```python
PROBE = 'untracked-skew-probe.md'
TRACKED = ({'root': 'repo', 'path': 'scripts/agent_work_root.py', 'required': True}, {'root': 'sk...
```

- [declaration](RealCheckoutSkew.declaration.md) method: HOLE: no docstring
- [test_a_clean_checkout_differs_only_in_rev_never_in_shape](RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.md) method: HOLE: no docstring
- [test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content](RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.md) method: Regression, review BLOCKER-1 (#300 g5 rework 1).

writes internal: RealCheckoutSkew.PROBE, RealCheckoutSkew.TRACKED

referenced by: none found
