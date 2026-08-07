# tests.test_episode_negative_control:compare_manifest_rows
function, tests/test_episode_negative_control.py:338, 17 lines

```python
def compare_manifest_rows(expected: list[dict], manifest: dict) -> list[str]
```

Mismatched declared PATHS, in declaration order — a list of names, never a bool,

for exactly the reason `compare_fields` is.

A row that is missing, out of declaration order, or carrying the wrong `rev` — which
includes `null` where a file really was delivered — is named. That is what stops an
all-null manifest reading as success.

calls stdlib: builtins.len x2, builtins.enumerate, builtins.isinstance
reads stdlib: builtins.list
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
