# tests.test_run_skill_eval:_tokened_worktree
function, tests/test_run_skill_eval.py:585, 14 lines

```python
def _tokened_worktree(tmp_path: Path) -> Path
```

Like `throwaway_worktree` but the skill body carries a `<skill-dir>` token, so

the installer's `rewrite_installed_skill_paths` bakes the ABSOLUTE install path
(`target.as_posix()`) into the installed SKILL.md. That reproduces the #153
pollution the stable corpus id must normalize out; without a rewritable token the
two installs are byte-identical and the RAW-differs canary below is a false green.

reads internal: FOO_SKILL_MD
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
