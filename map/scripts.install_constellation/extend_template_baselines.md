# scripts.install_constellation:extend_template_baselines
function, scripts/install_constellation.py:1142, 59 lines

```python
def extend_template_baselines(skills: Sequence[Skill], templates_root: Path, baseline_root: Path, manifest_path: Path, *, out: Callable[[str], object]) -> set[tuple[str, str]]
```

Track upstream templates that aren't in this project's baseline yet.

Adds a pristine baseline copy + manifest entry for every passed-skill template
not already tracked, leaving every existing baseline file and manifest entry
untouched (mirrors the never-clobber working-copy seeding). This is what lets a
template shipped after a project's initial install reach its versioned-template
tracking on a later reinstall. Returns the set of (skill, template) keys newly
tracked.

calls internal: extend_template_baselines.out x3, _hash_file
calls stdlib: builtins.set x2, builtins.len, builtins.sorted, json.dumps, json.loads, shutil.copy2
reads stdlib: builtins.str x2, json (module) x2, builtins.set, builtins.tuple, shutil (module)
unresolved: 12 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
