"""Tests for the constellation-to-issues cut-work skill's scripts.

Covers the refuse-malformed RAIL (scripts/verify_issue_set.py) and the
ports-and-adapters FILER (scripts/file_issue_set.py):

  * RailTests        -- the four locked refusal rules + the well-formed pass.
  * FilerTests       -- markdown adapter files offline; the rail blocks a
                        malformed set from ever being filed.
  * IdempotencyTests -- crash-injection at before-file / after-file-before-
                        receipt / after-receipt; each re-run yields NO dupe epic.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# Spec fixtures: a CONFIRMED spec (findings table + confirmation block) and an
# UNCONFIRMED one. Shapes match what verify_spec_confirmed.py accepts/refuses.
# --------------------------------------------------------------------------- #
CONFIRMED_SPEC = """# Design Spec — toy

## Confirmation

- **Status: CONFIRMED**
- Confirmed by: fredc
- Date: 2026-07-12

## Critic findings and dispositions

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | something | EDIT | fixed it |
| F2 | testability | MAJOR | something else | REJECT | not needed |
"""

UNCONFIRMED_SPEC = """# Design Spec — toy

## Confirmation

- **Status: DRAFT**
- Confirmed by:
- Date:

## Critic findings and dispositions

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | something | EDIT | fixed it |
"""


def well_formed_manifest() -> dict:
    """A minimal well-formed issue set: two issues, one dependency edge, both
    typed, the HITL one carrying a reason."""
    return {
        "epic": {
            "title": "Decouple the toy",
            "spec_path": "DESIGN_SPEC.md",
        },
        "issues": [
            {
                "id": "A",
                "title": "Build the core",
                "body": "core body",
                "type": "AFK",
                "blocks": ["B"],
                "labels": ["afk"],
            },
            {
                "id": "B",
                "title": "Confirm the cut with the human",
                "body": "review body",
                "type": "HITL",
                "hitl_reason": "human must accept the removability ledger",
                "blocks": [],
                "labels": ["hitl"],
            },
        ],
    }


def _write(tmp: Path, spec_text: str, manifest: dict) -> tuple[Path, Path]:
    spec_path = tmp / "DESIGN_SPEC.md"
    spec_path.write_text(spec_text, encoding="utf-8")
    manifest_path = tmp / "issue_set.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return spec_path, manifest_path


class RailTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_issue_set")

    def test_unconfirmed_spec_refused(self):
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(well_formed_manifest(), UNCONFIRMED_SPEC)

    def test_missing_dependency_edge_refused(self):
        m = well_formed_manifest()
        for issue in m["issues"]:
            issue["blocks"] = []
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(m, CONFIRMED_SPEC)

    def test_untyped_issue_refused(self):
        m = well_formed_manifest()
        del m["issues"][0]["type"]
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(m, CONFIRMED_SPEC)

    def test_bad_type_value_refused(self):
        m = well_formed_manifest()
        m["issues"][0]["type"] = "MAYBE"
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(m, CONFIRMED_SPEC)

    def test_hitl_without_reason_refused(self):
        m = well_formed_manifest()
        m["issues"][1]["hitl_reason"] = "   "
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(m, CONFIRMED_SPEC)

    def test_dangling_edge_refused(self):
        m = well_formed_manifest()
        m["issues"][0]["blocks"] = ["does-not-exist"]
        with self.assertRaises(self.rail.IssueSetError):
            self.rail.verify_issue_set(m, CONFIRMED_SPEC)

    def test_well_formed_set_passes(self):
        # No raise == accepted.
        self.rail.verify_issue_set(well_formed_manifest(), CONFIRMED_SPEC)

    def test_cli_refuses_unconfirmed_nonzero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            spec_path, manifest_path = _write(Path(d), UNCONFIRMED_SPEC, well_formed_manifest())
            rc = self.rail.main([str(manifest_path), "--spec", str(spec_path)])
            self.assertNotEqual(0, rc)

    def test_cli_accepts_well_formed_zero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            spec_path, manifest_path = _write(Path(d), CONFIRMED_SPEC, well_formed_manifest())
            rc = self.rail.main([str(manifest_path), "--spec", str(spec_path)])
            self.assertEqual(0, rc)


class FilerTests(unittest.TestCase):
    def setUp(self):
        self.filer = load("file_issue_set")

    def _adapter(self, tmp: Path):
        return self.filer.MarkdownAdapter(tmp / "TRACKER.md")

    def test_markdown_files_offline(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter = self._adapter(tmp)
            receipt = self.filer.file_issue_set(
                well_formed_manifest(), CONFIRMED_SPEC, adapter, tmp / "receipt.json"
            )
            text = (tmp / "TRACKER.md").read_text(encoding="utf-8")
            # Epic + both issues landed, offline, no network.
            self.assertEqual(1, adapter.count_epics())
            self.assertIn("Build the core", text)
            self.assertIn("Confirm the cut with the human", text)
            # Receipt records the epic + every issue.
            self.assertIn("epic", receipt)
            self.assertEqual({"A", "B"}, set(receipt["issues"].keys()))
            self.assertTrue((tmp / "receipt.json").is_file())

    def test_epic_body_is_wave_ordered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter = self._adapter(tmp)
            self.filer.file_issue_set(
                well_formed_manifest(), CONFIRMED_SPEC, adapter, tmp / "receipt.json"
            )
            text = (tmp / "TRACKER.md").read_text(encoding="utf-8")
            # A blocks B, so A must be ordered ahead of B in the epic task list.
            self.assertLess(text.index("Build the core"), text.index("Confirm the cut with the human"))
            # HITL/AFK labels surface in the epic body.
            self.assertIn("HITL", text)
            self.assertIn("AFK", text)

    def test_rail_blocks_malformed_filing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter = self._adapter(tmp)
            m = well_formed_manifest()
            for issue in m["issues"]:
                issue["blocks"] = []  # no edges -> rail refuses
            with self.assertRaises(self.filer.IssueSetError):
                self.filer.file_issue_set(m, CONFIRMED_SPEC, adapter, tmp / "receipt.json")
            # NOTHING reached the tracker.
            self.assertEqual(0, adapter.count_epics())

    def test_unconfirmed_spec_blocks_filing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter = self._adapter(tmp)
            with self.assertRaises(self.filer.IssueSetError):
                self.filer.file_issue_set(
                    well_formed_manifest(), UNCONFIRMED_SPEC, adapter, tmp / "receipt.json"
                )
            self.assertEqual(0, adapter.count_epics())


class IdempotencyTests(unittest.TestCase):
    """Crash-injection at the three named points (DESIGN_SPEC TF7). Each: crash
    mid-file, then re-run to completion, and assert NO duplicate epic and no
    duplicate issues."""

    def setUp(self):
        self.filer = load("file_issue_set")

    def _run_with_crash_then_complete(self, crash_at: str):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter = self.filer.MarkdownAdapter(tmp / "TRACKER.md")
            receipt_path = tmp / "receipt.json"
            manifest = well_formed_manifest()

            # First run crashes at the injection point.
            with self.assertRaises(self.filer.CrashInjected):
                self.filer.file_issue_set(
                    manifest, CONFIRMED_SPEC, adapter, receipt_path, crash_at=crash_at
                )
            # Re-run to completion (crash cleared).
            receipt = self.filer.file_issue_set(
                manifest, CONFIRMED_SPEC, adapter, receipt_path
            )
            # Exactly one epic and no duplicate issues survived the retry.
            self.assertEqual(1, adapter.count_epics(), f"duplicate epic after crash_at={crash_at}")
            self.assertEqual(2, adapter.count_issues(), f"duplicate issue after crash_at={crash_at}")
            self.assertEqual({"A", "B"}, set(receipt["issues"].keys()))

    def test_crash_before_file(self):
        self._run_with_crash_then_complete("before-file")

    def test_crash_after_file_before_receipt(self):
        self._run_with_crash_then_complete("after-file-before-receipt")

    def test_crash_after_receipt(self):
        self._run_with_crash_then_complete("after-receipt")


if __name__ == "__main__":
    unittest.main()
