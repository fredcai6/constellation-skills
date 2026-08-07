# scripts.install_constellation:discover_skills
function, scripts/install_constellation.py:257, 28 lines

```python
def discover_skills(source_root: Path = SOURCE_ROOT) -> list[Skill]
```

HOLE: no docstring

calls internal: InstallError x3, Skill, expand_script_bundle, parse_frontmatter
calls stdlib: builtins.sorted
reads internal: SKILL_REFERENCE_BUNDLES, SKILL_SCRIPT_BUNDLES, Skill
reads stdlib: builtins.list
unresolved: 8 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
