import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location("init_work_area", ROOT / "scripts" / "init_work_area.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InitWorkAreaTests(unittest.TestCase):
    def test_creates_structure(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            base = m.init_work_area(Path(d), "issue-7")
            self.assertTrue(base.is_dir())
            for sub in ["crew-handoffs", "evidence", "triage-candidates"]:
                self.assertTrue((base / sub).is_dir())

    def test_idempotent(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            m.init_work_area(Path(d), "x")
            m.init_work_area(Path(d), "x")  # second call must not raise


if __name__ == "__main__":
    unittest.main()
