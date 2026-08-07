# scripts.install_constellation:rewrite_installed_skill_paths
function, scripts/install_constellation.py:430, 26 lines

```python
def rewrite_installed_skill_paths(target: Path, skill: Skill, interpreter: InterpreterResolution) -> None
```

HOLE: no docstring

calls internal: InterpreterResolution.as_sidecar
calls stdlib: json.dumps
reads internal: InterpreterResolution.interpreter, REWRITABLE_TEXT_SUFFIXES, Skill.source_name
reads stdlib: json (module)
unresolved: 10 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
