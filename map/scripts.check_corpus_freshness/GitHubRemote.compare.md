# scripts.check_corpus_freshness:GitHubRemote.compare
method, scripts/check_corpus_freshness.py:95, 5 lines

```python
def compare(self, base: str, head: str) -> dict
```

GitHub compare of base...head. `ahead_by` is how many commits `head`

(upstream main) has that `base` (the install) lacks, and `commits` are
exactly those commits oldest-first.

calls internal: GitHubRemote._get
reads internal: GitHubRemote.repo

referenced by: 1 sites, this module only
