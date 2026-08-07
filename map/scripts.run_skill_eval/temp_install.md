# scripts.run_skill_eval:temp_install
function, scripts/run_skill_eval.py:767, 21 lines

```python
def temp_install(worktree, temp_root) -> Path
```

Install the candidate corpus ONCE into `<temp_root>/skills` and return that

dir. Reuses install_constellation.discover_skills + install_skills (token
rewrite + bundle copy), never reinventing install. `worktree` selects the
source skill root: `<worktree>/skills` when given, else this worktree's
`skills/` (install_constellation.SOURCE_ROOT). Full-set, non-dry, non-force
into a fresh temp target; never edits install_constellation or the source
skills.

calls stdlib: pathlib.Path x2
reads internal: _install x3
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
