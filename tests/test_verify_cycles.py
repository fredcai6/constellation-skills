import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "verify_cycles", ROOT / "scripts" / "verify_cycles.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONSOLIDATED_CYCLE = json.dumps({"type": "survey", "consolidation": {"verdict": "converge"}})
UNCONSOLIDATED_CYCLE = json.dumps({"type": "survey", "consolidation": None})


class VerifyCyclesTests(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.work_area = self.root / ".agent-work" / "explore-widget"
        self.work_area.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_cycle(self, name, text):
        (self.work_area / name).write_text(text, encoding="utf-8")

    def verify(self):
        self.m.verify_cycles(self.root, "explore-widget")

    def test_pass_with_consolidated_cycles(self):
        self.write_cycle("cycle-1.json", CONSOLIDATED_CYCLE)
        self.write_cycle("cycle-2.json", CONSOLIDATED_CYCLE)
        self.verify()  # must not raise

    def test_fail_zero_cycles(self):
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self.verify()
        self.assertIn("zero cycles", str(ctx.exception))

    def test_fail_unconsolidated_cycle(self):
        self.write_cycle("cycle-1.json", CONSOLIDATED_CYCLE)
        self.write_cycle("cycle-2.json", UNCONSOLIDATED_CYCLE)
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self.verify()
        self.assertIn("unconsolidated", str(ctx.exception))

    def test_fail_unparseable_json(self):
        self.write_cycle("cycle-1.json", "{not json")
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self.verify()
        self.assertIn("unparseable", str(ctx.exception))

    def test_fail_not_a_survey(self):
        self.write_cycle("cycle-1.json", json.dumps({"type": "gated", "consolidation": None}))
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self.verify()
        self.assertIn("not a survey", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
