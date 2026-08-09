"""Focused tests for the ten-item iterative-planning acceptance verifier."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify_iterative_planning_acceptance.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_iterative_planning_acceptance", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IterativePlanningAcceptanceTests(unittest.TestCase):
    def test_verifier_exists(self):
        self.assertTrue(VERIFIER.is_file())

    def test_missing_demo_refuses_all_ten_item_claim(self):
        verifier = load_verifier()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(verifier.AcceptanceError):
                verifier.verify_acceptance("missing-work", root=Path(tmp))

    def test_acceptance_names_exact_frozen_matrix(self):
        verifier = load_verifier()
        self.assertEqual(
            (
                "canonical_renamed_install",
                "zero_edge_validity",
                "forecast_non_filing",
                "eight_required_headings",
                "all_four_exits",
                "blocking_repair_holds_forecast",
                "evidence_only_creates_no_issue",
                "fixed_boundaries_preserve_or_escalate",
                "deny_harness_zero_calls",
                "relevant_and_full_tests_green",
            ),
            verifier.ACCEPTANCE_ITEMS,
        )


if __name__ == "__main__":
    unittest.main()
