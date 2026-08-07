# scripts.install_constellation:settings_path_for_target_root
function, scripts/install_constellation.py:617, 9 lines

```python
def settings_path_for_target_root(target_root: Path) -> Path
```

The settings.json governing the agent config dir this install writes

into: `~/.claude/skills` -> `~/.claude/settings.json`, and at project scope
`<project>/.claude/skills` -> `<project>/.claude/settings.json`.

Derived from the RESOLVED target root rather than re-derived from scope, so
a `--dest` install -- which every test in this repo uses -- can never reach
past its own tree into the developer's real ~/.claude/settings.json.

reads internal: SETTINGS_FILENAME
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
