# scripts.run_skill_eval:verdict
function, scripts/run_skill_eval.py:407, 33 lines

```python
def verdict(run_results: list, *, n: int, m: int, corpus_id: str | None = None, source_commit: str | None = None) -> Verdict
```

The corpus verdict from the per-run classifications. PURE.

Tally is over COMPLETED runs only (completed-pass/-fail); fenced runs
(inconclusive/errored) are excluded. `completed < n => INCONCLUSIVE (exit 2)`;
`passed >= n => PASS (exit 0)`; else `FAIL (exit 1)`. Environment flake can
only ever yield INCONCLUSIVE, never FAIL a good corpus.

2-of-3 is a regression-vs-variance smoke, NOT a statistical guarantee: it
separates a corpus that reliably fails from one that reliably works and stops
a single lucky/unlucky run from being the verdict.

calls internal: Verdict
calls stdlib: builtins.len x5, builtins.list
unresolved: 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
