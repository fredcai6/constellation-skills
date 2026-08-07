# scripts.checklist_engine:_find_posix_shell
function, scripts/checklist_engine.py:717, 17 lines

```python
def _find_posix_shell() -> str | None
```

Locate a POSIX shell to run `command` checks under: bash on Windows, sh on

POSIX. Returns the shell path, or None if none is found. On Windows
`shutil.which("bash")` is the primary lookup (Git for Windows usually puts its
bash dir on PATH); the git-derived candidates are a backstop for when git is on
PATH but bash is not.

calls internal: _bash_candidates_from_git
calls stdlib: shutil.which x4, os.path.isfile
reads stdlib: shutil (module) x4, os (module) x2, os.name, os.path

referenced by: 1 sites, this module only
