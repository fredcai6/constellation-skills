# scripts.build_architecture_map
scripts/build_architecture_map.py, 423 lines, 15 holes

HOLE: no docstring

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, re, typing.Any, typing.Iterable, typing.Sequence
imported by: none found

```python
ALLOWED_LEVELS = {'system-context', 'container', 'component', 'code-path', 'module', 'function-or-method'}
ALLOWED_NODE_STATUS = {'current', 'partial', 'stale', 'disputed'}
ALLOWED_CONFIDENCE = {'high', 'medium', 'low', 'unknown'}
ALLOWED_RELATIONSHIPS = {'supports', 'depends-on', 'emits', 'constrained-by', 'explained-by', 'verified-by'}
ALLOWED_OVERLAY_KINDS = {'capability', 'event', 'constraint', 'assumption', 'decision', 'claim'}
OVERLAY_NODE_SECTIONS = {'capabilities': 'capability', 'events': 'event', 'constraints': 'constraint', 'assumpt...
SOURCE_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.cs'}
```

- [MapBuildError](MapBuildError.md) class: Raised when architecture map inputs fail validation.
- [BuildResult](BuildResult.md) class: HOLE: no docstring
  - [BuildResult.__init__](BuildResult.__init__.md) method: HOLE: no docstring
- [normalize_value](normalize_value.md) function: HOLE: no docstring
- [repo_path](repo_path.md) function: HOLE: no docstring
- [required_field](required_field.md) function: HOLE: no docstring
- [parse_packet](parse_packet.md) function: HOLE: no docstring
- [parse_overlay_value](parse_overlay_value.md) function: HOLE: no docstring
- [parse_overlay](parse_overlay.md) function: HOLE: no docstring
  - [parse_overlay.flush](parse_overlay.flush.md) method: HOLE: no docstring
- [module_node_id](module_node_id.md) function: HOLE: no docstring
- [scan_source_tree](scan_source_tree.md) function: HOLE: no docstring
- [validate_map](validate_map.md) function: HOLE: no docstring
- [build_architecture_map](build_architecture_map.md) function: HOLE: no docstring
- [build_parser](build_parser.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
