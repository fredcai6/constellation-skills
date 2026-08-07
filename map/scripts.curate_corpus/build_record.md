# scripts.curate_corpus:build_record
function, scripts/curate_corpus.py:406, 17 lines

```python
def build_record(root: Path, findings: list[Finding]) -> dict
```

The --json machine record: the run's root, the heuristic constants that

produced it, and the findings as structured rows.

calls stdlib: builtins.sorted, builtins.str
reads internal: CONFUSABLE_SKILLS, DESCRIPTION_MAX_CHARS, DESCRIPTION_MAX_WORDS, MIN_CLUSTER_SKILLS, REFERENCE_TOC_LINE_THRESHOLD, SHINGLE_SIZE, SKILL_LINE_HARD_FLAG, SKILL_WORD_TARGET
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
