# scripts.checklist_engine:_bash_candidates_from_git
function, scripts/checklist_engine.py:697, 18 lines

```python
def _bash_candidates_from_git(git_path: str) -> list[str]
```

Candidate bash.exe paths derived from a git executable path. Windows

backstop for when `git` is on PATH but its bash directory is not.

`shutil.which("git")` resolves git to varying depths — `…\Git\mingw64\bin\git.exe`
(Git root = great-grandparent), `…\Git\cmd\git.exe` (grandparent), or
`…\Git\bin\git.exe` (parent) — while bash always lives at `…\Git\bin\bash.exe`
and `…\Git\usr\bin\bash.exe`. Walk up 4 ancestor directories and, for each,
emit both bash locations. Pure: no filesystem access (the caller filters by
existence). Uses PureWindowsPath so it parses Windows paths the same on any host
OS — this helper only runs on Windows but its unit tests run anywhere.

calls stdlib: builtins.str x2, builtins.range, pathlib.PureWindowsPath
reads stdlib: builtins.list, builtins.str
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
