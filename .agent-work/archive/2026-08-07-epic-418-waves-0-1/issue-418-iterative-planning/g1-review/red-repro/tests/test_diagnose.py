"""Tests for the constellation-diagnose skill's rail (scripts/verify_diagnosis.py).

The rail is reproduce-before-you-claim. These tests exercise the three cases the
DESIGN_SPEC (Section B, "Testing pathways") names, plus the exception path and
the structural refusals:

  * SeededRuntimeBugTests -- one loop over a seeded runtime bug: the oracle (a
                             test) reproduces it, the finding records the observed
                             mechanism, and the rail confirms it.
  * SeededDisconnectTests -- the SAME loop over a seeded intent/execution
                             disconnect, reached via the map-as-oracle probe.
  * RailBlocksTests       -- a 'confirmed' claim with no falsifier / no observed
                             result is BLOCKED; the reviewer-cosigned exception
                             passes; a self-asserted exception does NOT.
  * StructureTests        -- the shape + route-out-don't-fix refusals + CLI codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# A seeded RUNTIME bug and its oracle (a test). The loop's reproduce step is
# actually run here, so observed_result is an observation, not a hand-written
# string.
# --------------------------------------------------------------------------- #
def seeded_add(a, b):
    """Seeded bug: multiplies instead of adds."""
    return a * b


def reproduce_runtime_bug() -> str:
    """The oracle: a test that fails on the seeded bug. Returns the observed
    reproduce result (empty string means it did NOT reproduce)."""
    expected = 5
    got = seeded_add(2, 3)
    if got != expected:
        return f"seeded_add(2, 3) expected {expected}, got {got}"
    return ""


# --------------------------------------------------------------------------- #
# A seeded DISCONNECT and its oracle (the map/intent used as a runtime probe).
# The "map" claims seeded_touch is pure; execution mutates a module global.
# --------------------------------------------------------------------------- #
_STATE = {"writes": 0}
MAP_CLAIM_PURE = True  # what the (stale) map/intent says about seeded_touch


def seeded_touch(x):
    """Execution drifted from the map: the map says pure, this mutates _STATE."""
    _STATE["writes"] += 1
    return x


def probe_disconnect() -> str:
    """The oracle: probe the map's purity claim against actual behavior. Returns
    the observed disagreement (empty string means map and execution agree)."""
    before = _STATE["writes"]
    seeded_touch(1)
    after = _STATE["writes"]
    mutated = after != before
    if MAP_CLAIM_PURE and mutated:
        return f"map says seeded_touch is pure; execution mutated _STATE ({before} -> {after})"
    return ""


class SeededRuntimeBugTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_diagnosis")

    def test_loop_reproduces_and_rail_confirms(self):
        # Reproduce step actually runs the oracle.
        observed = reproduce_runtime_bug()
        self.assertTrue(observed, "seeded runtime bug did not reproduce")
        finding = {
            "symptom": "seeded_add(2, 3) returns a wrong sum",
            "altitude": "runtime",
            "oracle": "unit test asserting seeded_add(2, 3) == 5",
            "status": "confirmed",
            "cause": "seeded_add uses * instead of +",
            "falsifier": "seeded_add(2, 3) returns 5 (then the * hypothesis is wrong)",
            "observed_result": observed,
            "route": "triage",
        }
        # No raise == the rail confirms a reproduced runtime cause.
        self.rail.verify_diagnosis(finding)


class SeededDisconnectTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_diagnosis")

    def test_same_loop_reaches_disconnect_via_map_oracle(self):
        observed = probe_disconnect()
        self.assertTrue(observed, "seeded disconnect did not reproduce via the map oracle")
        finding = {
            "symptom": "seeded_touch behaves as if impure, disagreeing with the map",
            "altitude": "disconnect",
            "oracle": "the map's 'seeded_touch is pure' claim probed against actual behavior",
            "status": "confirmed",
            "cause": "seeded_touch mutates _STATE; the map's purity claim is stale",
            "falsifier": "seeded_touch leaves _STATE unchanged (then the map is right)",
            "observed_result": observed,
            "map_staleness_caveat": "map purity claim is the oracle; reviewer weighs whether the map, not the code, is what is wrong",
            "route": "reviewer",
        }
        self.rail.verify_diagnosis(finding)

    def test_disconnect_without_caveat_refused(self):
        finding = {
            "symptom": "execution disagrees with the map",
            "altitude": "disconnect",
            "oracle": "map claim probed against behavior",
            "status": "confirmed",
            "falsifier": "behavior matches the map",
            "observed_result": "map says X, behavior did Y",
            "route": "reviewer",
            # map_staleness_caveat deliberately absent
        }
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(finding)


class RailBlocksTests(unittest.TestCase):
    """The reproduce-before-you-claim rail and its cosigned exception."""

    def setUp(self):
        self.rail = load("verify_diagnosis")

    def _confirmed(self, **overrides) -> dict:
        finding = {
            "symptom": "something returns the wrong value",
            "altitude": "runtime",
            "oracle": "a failing test",
            "status": "confirmed",
            "cause": "some mechanism",
            "falsifier": "the mechanism would show X",
            "observed_result": "expected 5, got 6",
            "route": "triage",
        }
        finding.update(overrides)
        return finding

    def test_confirmed_without_falsifier_blocked(self):
        # THE falsifier for the skill itself: a confirmed claim with no reproduce
        # evidence must NOT pass.
        f = self._confirmed()
        del f["falsifier"]
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(f)

    def test_confirmed_without_observed_result_blocked(self):
        f = self._confirmed()
        del f["observed_result"]
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(f)

    def test_confirmed_with_empty_evidence_blocked(self):
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(self._confirmed(falsifier="   ", observed_result=""))

    def test_reviewer_cosigned_exception_passes(self):
        # A trivial one-line cause with no reproduce evidence passes ONLY with an
        # independent reviewer's co-sign + a log entry.
        f = self._confirmed()
        del f["falsifier"]
        del f["observed_result"]
        f["rail_exception"] = {
            "reviewer_cosign": "reviewer-agent-7",
            "log": "one-line typo, reviewer agreed the full loop is not worth it",
        }
        self.rail.verify_diagnosis(f)

    def test_self_asserted_exception_blocked(self):
        # Self-assertion (no reviewer_cosign) never passes, even with a log.
        f = self._confirmed()
        del f["falsifier"]
        del f["observed_result"]
        f["rail_exception"] = {"reviewer_cosign": "", "log": "I judged it trivial"}
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(f)

    def test_suspected_needs_no_reproduce_evidence(self):
        # Mid-loop: a suspected cause is not yet a claim, so the rail does not
        # demand reproduce evidence.
        f = {
            "symptom": "wrong value",
            "altitude": "runtime",
            "oracle": "a test being written",
            "status": "suspected",
        }
        self.rail.verify_diagnosis(f)


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_diagnosis")

    def test_empty_symptom_refused(self):
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis({"symptom": "  ", "altitude": "runtime",
                                        "oracle": "a test", "status": "suspected"})

    def test_bad_altitude_refused(self):
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis({"symptom": "x", "altitude": "cosmic",
                                        "oracle": "a test", "status": "suspected"})

    def test_empty_oracle_refused(self):
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis({"symptom": "x", "altitude": "runtime",
                                        "oracle": "", "status": "suspected"})

    def test_bad_status_refused(self):
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis({"symptom": "x", "altitude": "runtime",
                                        "oracle": "a test", "status": "solved"})

    def test_confirmed_fault_must_route_out_not_note(self):
        # Route-out-don't-fix: a confirmed fault cannot be handed back as a note.
        f = {
            "symptom": "x", "altitude": "runtime", "oracle": "a test",
            "status": "confirmed", "falsifier": "y", "observed_result": "z",
            "route": "note",
        }
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(f)

    def test_explained_by_design_is_a_note(self):
        f = {
            "symptom": "looked like a bug", "altitude": "runtime",
            "oracle": "a test that then passed", "status": "explained-by-design",
            "route": "note",
        }
        self.rail.verify_diagnosis(f)

    def test_explained_by_design_cannot_route_to_triage(self):
        f = {
            "symptom": "looked like a bug", "altitude": "runtime",
            "oracle": "a test", "status": "explained-by-design", "route": "triage",
        }
        with self.assertRaises(self.rail.DiagnosisError):
            self.rail.verify_diagnosis(f)

    def test_cli_refuses_unreproduced_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "finding.json"
            p.write_text(json.dumps({
                "symptom": "x", "altitude": "runtime", "oracle": "a test",
                "status": "confirmed", "route": "triage",
            }), encoding="utf-8")
            self.assertNotEqual(0, self.rail.main([str(p)]))

    def test_cli_accepts_reproduced_zero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "finding.json"
            p.write_text(json.dumps({
                "symptom": "x", "altitude": "runtime", "oracle": "a test",
                "status": "confirmed", "falsifier": "y", "observed_result": "z",
                "route": "triage",
            }), encoding="utf-8")
            self.assertEqual(0, self.rail.main([str(p)]))


if __name__ == "__main__":
    unittest.main()
