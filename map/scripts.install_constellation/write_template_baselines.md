# scripts.install_constellation:write_template_baselines
function, scripts/install_constellation.py:1070, 70 lines

```python
def write_template_baselines(skills: Sequence[Skill], project_root: Path, *, out: Callable[[str], object]) -> set[tuple[str, str]]
```

Seed pristine blank-template baselines + manifest for a project install.

The baseline is what three-way template reconciliation diffs against; the
installer therefore never overwrites an existing baseline — upgrades are
reconciled by check_skill_freshness.py, which owns baseline promotion.

Returns the set of (skill_install_name, template_name) keys that ENTERED
tracking this run — every template on a fresh seed, only the genuinely-new
ones on an extend. The caller seeds working copies for exactly this set, so a
reinstall never backfills working copies for templates the project chose not
to track (which would otherwise read as false `project-customized` drift and
mask later upstream changes).

calls internal: _hash_file, _source_commit, extend_template_baselines, write_template_baselines.out
calls stdlib: builtins.set x2, builtins.len, builtins.sorted, datetime.date.today, json.dumps, shutil.copy2
reads stdlib: builtins.str x4, builtins.dict, builtins.list, builtins.set, builtins.tuple, datetime.date, json (module), shutil (module)
unresolved: 11 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
