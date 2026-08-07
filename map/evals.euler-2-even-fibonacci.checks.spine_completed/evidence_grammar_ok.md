# evals.euler-2-even-fibonacci.checks.spine_completed:evidence_grammar_ok
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:151, 44 lines

```python
def evidence_grammar_ok(data: dict) -> tuple[bool, str]
```

Whether the spine's evidence matches engine grammar and cross-verifies the

engine-checked conditions. Catches hand-written evidence that flips statuses
without the engine-produced records the engine would have left.

calls stdlib: builtins.isinstance x5, builtins.len x2
reads internal: ENGINE_CHECK_KINDS, EVIDENCE_ID_RE
reads stdlib: builtins.dict x5, builtins.list, builtins.str
unresolved: 27 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
