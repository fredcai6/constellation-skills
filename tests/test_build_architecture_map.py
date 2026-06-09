import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_architecture_map.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_architecture_map", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


PACKET = """# Architecture Packet: `Core`

## Status

**Structural node:** `struct:core`
**Level:** `component`
**Parent:** `none`
**Status:** `current`
**Confidence:** `high`
**Last reconciled:** `2026-05-24`

## Dependencies

- `struct:core` -> `struct:storage`; type `depends-on`; provenance `curated`; confidence `high`; evidence `docs/architecture/packets/core.md`
"""


class BuildArchitectureMapTests(unittest.TestCase):
    def test_builds_map_from_packets_overlays_and_source_tree(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "docs/architecture/packets/core.md", PACKET)
            write(
                repo / "docs/architecture/packets/storage.md",
                PACKET.replace("struct:core", "struct:storage").replace("Core", "Storage"),
            )
            write(
                repo / "docs/architecture/overlays/capability.yml",
                """
capabilities:
  - id: capability:prediction
    kind: capability
    parent: null
    label: Prediction
events:
  - id: event:prediction-ready
    kind: event
    parent: null
    label: Prediction ready
relationships:
  - source: struct:core
    type: supports
    target: capability:prediction
    provenance: curated
    evidence:
      - docs/architecture/overlays/capability.yml
  - source: capability:prediction
    type: emits
    target: event:prediction-ready
    provenance: curated
    evidence:
      - docs/architecture/overlays/capability.yml
""",
            )
            write(repo / "src/core/service.py", "import json\n")
            write(repo / "src/core/README.md", "# Duplicate canonical module doc\n")

            result = builder.build_architecture_map(repo, source_roots=("src",), write_output=True)

            output = repo / "docs/architecture/generated/map.json"
            self.assertTrue(output.exists())
            data = json.loads(output.read_text(encoding="utf-8"))

            node_ids = {node["id"] for node in data["nodes"]}
            self.assertIn("struct:core", node_ids)
            self.assertIn("struct:storage", node_ids)
            self.assertIn("struct:module:src.core.service", node_ids)
            self.assertIn("capability:prediction", node_ids)
            self.assertIn("event:prediction-ready", node_ids)

            relationship_types = {edge["type"] for edge in data["relationships"]}
            self.assertEqual({"depends-on", "supports", "emits"}, relationship_types)
            self.assertTrue(
                any(
                    finding["class"] == "parallel canonical docs"
                    and finding["path"] == "src/core/README.md"
                    for finding in data["findings"]
                )
            )
            self.assertEqual(data, result.map_data)

    def test_rejects_disallowed_relationship_type(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(
                repo / "docs/architecture/packets/core.md",
                PACKET.replace("depends-on", "imports"),
            )

            with self.assertRaises(builder.MapBuildError) as raised:
                builder.build_architecture_map(repo, source_roots=("src",), write_output=False)

            self.assertIn("disallowed relationship type", str(raised.exception))

    def test_rejects_missing_parent_reference(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(
                repo / "docs/architecture/packets/core.md",
                PACKET.replace("**Parent:** `none`", "**Parent:** `struct:missing`"),
            )

            with self.assertRaises(builder.MapBuildError) as raised:
                builder.build_architecture_map(repo, source_roots=("src",), write_output=False)

            self.assertIn("missing parent", str(raised.exception))

    def test_rejects_disallowed_overlay_node_kind(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "docs/architecture/packets/core.md", PACKET)
            write(
                repo / "docs/architecture/overlays/bad.yml",
                """
capabilities:
  - id: purpose:prediction
    kind: purpose
    parent: null
    label: Prediction
relationships:
  - source: struct:core
    type: supports
    target: purpose:prediction
    provenance: curated
    evidence:
      - docs/architecture/overlays/bad.yml
""",
            )

            with self.assertRaises(builder.MapBuildError) as raised:
                builder.build_architecture_map(repo, source_roots=("src",), write_output=False)

            self.assertIn("disallowed node kind", str(raised.exception))

    def test_rejects_overlay_node_without_structural_anchor(self):
        builder = load_builder()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "docs/architecture/packets/core.md", PACKET)
            write(
                repo / "docs/architecture/overlays/floating.yml",
                """
capabilities:
  - id: capability:orphan
    kind: capability
    parent: null
    label: Orphan
""",
            )

            with self.assertRaises(builder.MapBuildError) as raised:
                builder.build_architecture_map(repo, source_roots=("src",), write_output=False)

            self.assertIn("without structural anchor", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
