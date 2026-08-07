# scripts.check_corpus_freshness:GitHubRemote._get
method, scripts/check_corpus_freshness.py:65, 25 lines

```python
def _get(self, path: str) -> dict
```

HOLE: no docstring

calls internal: FreshnessError
calls stdlib: json.loads x2, subprocess.run, urllib.request.Request, urllib.request.urlopen
reads stdlib: json (module) x3, urllib (module) x3, builtins.OSError x2, subprocess (module) x2, urllib.request x2, builtins.TimeoutError, json.JSONDecodeError, subprocess.TimeoutExpired, urllib.error, urllib.error.URLError
unresolved: 3 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
