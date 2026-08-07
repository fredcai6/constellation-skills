"""Focused tests for the frozen, offline Epic #418 demonstration contract."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify_epic_418_demo.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_epic_418_demo", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Epic418DemoVerifierTests(unittest.TestCase):
    def test_verifier_exists(self):
        self.assertTrue(VERIFIER.is_file())

    def test_missing_demo_refuses(self):
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(verifier.DemoError):
                verifier.verify_demo("missing-work", root=Path(tmp))

    def test_derived_counts_include_every_original_item_and_edge(self):
        verifier = load_verifier()
        original = {
            "issues": [
                {"id": "A", "title": "Alpha", "body": "two words", "blocks": ["B"]},
                {"id": "B", "title": "Beta", "body": "three clear words", "blocks": []},
            ]
        }
        manifest = {
            "current_wave": {"issues": [{"id": "A1", "title": "Now", "blocks": []}]},
            "wave_forecast": [{"outcome": "Later", "why_likely": "Evidence first", "entry_conditions": []}],
        }
        metrics = verifier.derive_metrics(original, manifest)
        self.assertEqual(2, metrics["before_issue_count"])
        self.assertEqual(1, metrics["after_issue_count"])
        self.assertEqual(1, metrics["before_edge_count"])
        self.assertEqual(0, metrics["after_edge_count"])
        self.assertGreater(metrics["before_word_count"], 0)
        self.assertGreater(metrics["after_word_count"], 0)

    def test_deny_receipt_rejects_any_call(self):
        verifier = load_verifier()
        valid = {
            "schema_version": 1,
            "tracker_calls": 0,
            "network_calls": 0,
            "subprocess_calls": 0,
            "gh_shim_first": True,
            "tracker_adapter": "raise-on-write",
        }
        verifier.verify_deny_receipt(valid)
        for field in ("tracker_calls", "network_calls", "subprocess_calls"):
            broken = dict(valid)
            broken[field] = 1
            with self.subTest(field=field), self.assertRaises(verifier.DemoError):
                verifier.verify_deny_receipt(broken)


if __name__ == "__main__":
    unittest.main()
