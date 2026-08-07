# tests.test_build_architecture_map
tests/test_build_architecture_map.py, 190 lines, 8 holes

HOLE: no docstring

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'build_architecture_map.py'
PACKET = '# Architecture Packet: `Core`\n\n## Status\n\n**Structural node:** `struct:core`\n**Le...
```

- [load_builder](load_builder.md) function: HOLE: no docstring
- [write](write.md) function: HOLE: no docstring
- [BuildArchitectureMapTests](BuildArchitectureMapTests.md) class: HOLE: no docstring
  - [BuildArchitectureMapTests.test_builds_map_from_packets_overlays_and_source_tree](BuildArchitectureMapTests.test_builds_map_from_packets_overlays_and_source_tree.md) method: HOLE: no docstring
  - [BuildArchitectureMapTests.test_rejects_disallowed_relationship_type](BuildArchitectureMapTests.test_rejects_disallowed_relationship_type.md) method: HOLE: no docstring
  - [BuildArchitectureMapTests.test_rejects_missing_parent_reference](BuildArchitectureMapTests.test_rejects_missing_parent_reference.md) method: HOLE: no docstring
  - [BuildArchitectureMapTests.test_rejects_disallowed_overlay_node_kind](BuildArchitectureMapTests.test_rejects_disallowed_overlay_node_kind.md) method: HOLE: no docstring
  - [BuildArchitectureMapTests.test_rejects_overlay_node_without_structural_anchor](BuildArchitectureMapTests.test_rejects_overlay_node_without_structural_anchor.md) method: HOLE: no docstring
