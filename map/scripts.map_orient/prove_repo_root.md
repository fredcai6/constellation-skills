# scripts.map_orient:prove_repo_root
function, scripts/map_orient.py:324, 20 lines

```python
def prove_repo_root(root_abs: str, dot_git_present: bool, git_toplevel: str | None) -> RootProof
```

PURE. POSITIVE repo-root proof -- never an absence test (#265).

"I could not look" and "I looked and found nothing" are different verdicts.
Only affirmative evidence -- a `.git` entry at the root, or git naming this
exact path as the toplevel -- proves we were entitled to look.

calls internal: RootProof x4, _same_path

referenced by: 5 sites, this module only
