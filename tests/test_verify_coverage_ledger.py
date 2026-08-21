import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "verify_coverage_ledger", ROOT / "scripts" / "verify_coverage_ledger.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest(*names):
    return {"sources": {"src": {"skills": list(names)}}}


def _well_formed_ledger():
    return {
        "ledger": [
            {"external": "systematic-debugging", "source": "sp", "status": "new", "home_skill": "diagnose", "reason": None},
            {"external": "tdd", "source": "mp", "status": "covered", "home_skill": "implementer", "reason": None},
            {"external": "using-superpowers", "source": "sp", "status": "declined", "home_skill": None, "reason": "router; when-to-use descriptions suffice solo"},
        ]
    }


class CoverageLedgerRailTest(unittest.TestCase):
    def setUp(self):
        self.mod = load()
        # A fake corpus whose only real skill dirs are the ones the well-formed ledger names.
        self._tmp = tempfile.TemporaryDirectory()
        self.skills_root = Path(self._tmp.name)
        for name in ("diagnose", "implementer"):
            (self.skills_root / name).mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _verify(self, ledger, manifest):
        return self.mod.verify_coverage_ledger(ledger, manifest, self.skills_root)

    # (d) well-formed ledger -> passes
    def test_well_formed_passes(self):
        manifest = _manifest("systematic-debugging", "tdd", "using-superpowers")
        # Should not raise.
        self._verify(_well_formed_ledger(), manifest)

    # (a) a new row naming a nonexistent home -> refused
    def test_new_row_with_nonexistent_home_refused(self):
        ledger = _well_formed_ledger()
        ledger["ledger"][0]["home_skill"] = "does-not-exist"
        manifest = _manifest("systematic-debugging", "tdd", "using-superpowers")
        with self.assertRaises(self.mod.CoverageLedgerError) as cm:
            self._verify(ledger, manifest)
        self.assertIn("does-not-exist", str(cm.exception))

    # (b) an installed external missing from the ledger -> refused
    def test_installed_external_missing_from_ledger_refused(self):
        manifest = _manifest("systematic-debugging", "tdd", "using-superpowers", "brand-new-external")
        with self.assertRaises(self.mod.CoverageLedgerError) as cm:
            self._verify(_well_formed_ledger(), manifest)
        self.assertIn("brand-new-external", str(cm.exception))

    # (c) a declined row with no reason -> refused
    def test_declined_row_without_reason_refused(self):
        ledger = _well_formed_ledger()
        ledger["ledger"][2]["reason"] = ""
        manifest = _manifest("systematic-debugging", "tdd", "using-superpowers")
        with self.assertRaises(self.mod.CoverageLedgerError) as cm:
            self._verify(ledger, manifest)
        self.assertIn("no reason", str(cm.exception))

    # The real, shipped ledger + manifest pass the rail end-to-end via main().
    def test_real_repo_ledger_passes(self):
        self.assertEqual(self.mod.main([]), 0)


if __name__ == "__main__":
    unittest.main()
