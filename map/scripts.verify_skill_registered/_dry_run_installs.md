# scripts.verify_skill_registered:_dry_run_installs
function, scripts/verify_skill_registered.py:135, 9 lines

```python
def _dry_run_installs(skill: str) -> None
```

Installability half (CLI only): the real skill passes install --dry-run.

calls third-party: install_constellation.discover_skills, install_constellation.install_skills, install_constellation.select_skills
reads third-party: install_constellation (module) x4, install_constellation.REPO_ROOT

referenced by: 1 sites, this module only
