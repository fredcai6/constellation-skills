# scripts.check_corpus_freshness:evaluate
function, scripts/check_corpus_freshness.py:125, 27 lines

```python
def evaluate(marker: dict, remote: GitHubRemote) -> tuple[int, str]
```

Return (exit_code, human report). Raises FreshnessError only for the

cannot-determine causes the caller maps to exit 2.

calls internal: FreshnessError, GitHubRemote.compare, GitHubRemote.head_commit, _subject
reads internal: GitHubRemote.branch x2
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
