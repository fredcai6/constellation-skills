# scripts.install_constellation:Skill
class, scripts/install_constellation.py:26, 6 lines

```python
@dataclass(frozen=True)
class Skill
```

HOLE: no docstring

```python
source_name: str
install_name: str
source_path: Path
required_scripts: tuple[str, ...]
required_references: tuple[str, ...]
```

reads stdlib: builtins.str x4, builtins.tuple x2, pathlib.Path
writes internal: Skill.install_name, Skill.required_references, Skill.required_scripts, Skill.source_name, Skill.source_path

referenced by: 14 sites, this module only
