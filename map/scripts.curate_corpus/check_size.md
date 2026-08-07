# scripts.curate_corpus:check_size
function, scripts/curate_corpus.py:189, 18 lines

```python
def check_size(skill: str, body: str) -> list[Finding]
```

Body line/word counts vs the soft size budgets.

calls internal: Finding x3
calls stdlib: builtins.len x2
reads internal: SKILL_LINE_HARD_FLAG x2, SKILL_WORD_TARGET x2, STATUS_FLAGGED x2, Finding, STATUS_OK
reads stdlib: builtins.list
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
