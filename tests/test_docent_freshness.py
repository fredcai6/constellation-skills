"""Unit tests for scripts/docent_freshness.py.

The freshness tool is the load-bearing part of docent: a stale explainer site
must be *provably* stale, not eyeballed. These tests pin the digest determinism
and the fresh(exit 0)/stale(nonzero) contract, including that perturbing a single
source-map file flips the verdict.
"""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "docent_freshness.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("docent_freshness", TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def seed_map(root: Path, *, packet_body: str = "alpha") -> Path:
    """Write a minimal but representative source-map tree under root."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "index.md").write_text("# Index\nReconciled.\n", encoding="utf-8")
    (root / "packets").mkdir(parents=True, exist_ok=True)
    (root / "packets" / "a.md").write_text(f"# Packet a\n{packet_body}\n", encoding="utf-8")
    (root / "packets" / "b.md").write_text("# Packet b\nbeta\n", encoding="utf-8")
    (root / "overlays").mkdir(parents=True, exist_ok=True)
    (root / "overlays" / "constraints.yml").write_text("constraints: []\n", encoding="utf-8")
    (root / "decisions").mkdir(parents=True, exist_ok=True)
    (root / "decisions" / "d1.md").write_text("# Decision 1\n", encoding="utf-8")
    return root


def write_site(site: Path, stamp: str) -> Path:
    site.mkdir(parents=True, exist_ok=True)
    (site / "index.html").write_text(
        "<!doctype html><html><head>"
        f'<meta name="docent-map-stamp" content="{stamp}">'
        "</head><body>demo</body></html>",
        encoding="utf-8",
    )
    return site


class ComputeStampTests(unittest.TestCase):
    def setUp(self):
        self.tool = load_tool()

    def _tmp(self):
        import tempfile

        self.addCleanup_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.addCleanup_dir.cleanup)
        return Path(self.addCleanup_dir.name)

    def test_stamp_is_64_hex_and_deterministic(self):
        root = seed_map(self._tmp())
        first = self.tool.compute_stamp(root)
        second = self.tool.compute_stamp(root)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))
        int(first, 16)  # must be hex

    def test_stamp_changes_when_a_source_file_is_perturbed(self):
        base = self._tmp()
        root_a = seed_map(base / "a", packet_body="alpha")
        root_b = seed_map(base / "b", packet_body="alpha-PERTURBED")
        self.assertNotEqual(
            self.tool.compute_stamp(root_a),
            self.tool.compute_stamp(root_b),
        )

    def test_stamp_is_independent_of_absolute_location(self):
        base = self._tmp()
        root_a = seed_map(base / "one")
        root_b = seed_map(base / "two")
        # identical trees at different absolute paths must hash identically
        self.assertEqual(
            self.tool.compute_stamp(root_a),
            self.tool.compute_stamp(root_b),
        )

    def test_generated_map_json_included_when_present(self):
        base = self._tmp()
        root_a = seed_map(base / "a")
        root_b = seed_map(base / "b")
        (root_b / "generated").mkdir(parents=True, exist_ok=True)
        (root_b / "generated" / "map.json").write_text('{"nodes": []}\n', encoding="utf-8")
        self.assertNotEqual(
            self.tool.compute_stamp(root_a),
            self.tool.compute_stamp(root_b),
        )


class CheckCliTests(unittest.TestCase):
    def setUp(self):
        self.tool = load_tool()

    def _tmp(self):
        import tempfile

        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)

    def test_stamp_subcommand_prints_digest(self):
        root = seed_map(self._tmp())
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self.tool.main(["stamp", "--map-root", str(root)])
        self.assertEqual(0, rc)
        self.assertEqual(self.tool.compute_stamp(root), buf.getvalue().strip())

    def test_check_fresh_exits_zero(self):
        base = self._tmp()
        root = seed_map(base / "map")
        site = write_site(base / "site", self.tool.compute_stamp(root))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self.tool.main(["check", str(site), "--map-root", str(root)])
        self.assertEqual(0, rc)
        self.assertIn("fresh", buf.getvalue().lower())

    def test_check_stale_exits_nonzero_after_source_perturbation(self):
        base = self._tmp()
        root = seed_map(base / "map", packet_body="alpha")
        site = write_site(base / "site", self.tool.compute_stamp(root))
        # perturb one source-map file AFTER the site captured its stamp
        (root / "packets" / "a.md").write_text("# Packet a\nMUTATED\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self.tool.main(["check", str(site), "--map-root", str(root)])
        self.assertNotEqual(0, rc)
        self.assertIn("stale", buf.getvalue().lower())

    def test_check_accepts_index_html_file_path_directly(self):
        base = self._tmp()
        root = seed_map(base / "map")
        site = write_site(base / "site", self.tool.compute_stamp(root))
        rc = self.tool.main(
            ["check", str(site / "index.html"), "--map-root", str(root)]
        )
        self.assertEqual(0, rc)

    def test_check_missing_stamp_is_error_nonzero(self):
        base = self._tmp()
        root = seed_map(base / "map")
        site = base / "site"
        site.mkdir(parents=True, exist_ok=True)
        (site / "index.html").write_text("<html><body>no stamp</body></html>", encoding="utf-8")
        rc = self.tool.main(["check", str(site), "--map-root", str(root)])
        self.assertNotEqual(0, rc)


if __name__ == "__main__":
    unittest.main()
