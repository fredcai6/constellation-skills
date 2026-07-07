import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tiny inline spine fixture carrying every placeholder the resolver must handle.
# Intentionally NOT the real COMMANDER_SPINE template, so these tests do not
# break when g2 edits that template's prose (handoff: use your own fixture).
SPINE_FIXTURE = json.dumps(
    {
        "work_id": "<work-id>",
        "session_id": "<commander-session-id>",
        "tasks": {
            "init": {
                "postconditions": [
                    {
                        "check": {
                            "kind": "command",
                            "command": "python <commander-skill-dir>/scripts/init_work_area.py <work-id>",
                        }
                    }
                ]
            }
        },
    },
    indent=2,
)


def load():
    spec = importlib.util.spec_from_file_location("init_work_area", ROOT / "scripts" / "init_work_area.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture(d: Path) -> Path:
    tpl = d / "SPINE.template.json"
    tpl.write_text(SPINE_FIXTURE, encoding="utf-8")
    return tpl


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


class SpineInstantiationTests(unittest.TestCase):
    def test_bare_init_writes_no_spine(self):
        # Backward compatibility: scaffolding alone must not create spine.json.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            base = m.init_work_area(Path(d), "issue-7")
            self.assertFalse((base / "spine.json").exists())

    def test_instantiate_resolves_all_placeholders_with_explicit_skill_dir(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tpl = write_fixture(root)
            out = m.instantiate_spine(root, "issue-7", tpl, skill_dir="skills/commander")
            self.assertEqual(out, root / ".agent-work" / "issue-7" / "spine.json")
            self.assertTrue(out.exists())
            text = out.read_text(encoding="utf-8")
            # Valid JSON.
            data = json.loads(text)
            # No residual placeholders of any kind.
            for token in ("<work-id>", "<commander-skill-dir>", "<commander-session-id>"):
                self.assertNotIn(token, text)
            self.assertEqual(data["work_id"], "issue-7")
            self.assertEqual(data["session_id"], "commander-issue-7")
            self.assertIn(
                "skills/commander/scripts/init_work_area.py issue-7",
                data["tasks"]["init"]["postconditions"][0]["check"]["command"],
            )

    def test_autodetect_collapses_skill_dir_scripts_to_top_level(self):
        # Source-repo layout: bundled scripts at <root>/scripts. Omitting
        # --skill-dir must collapse "<commander-skill-dir>/scripts" -> "scripts"
        # so the init command references the real top-level script path.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            tpl = write_fixture(root)
            out = m.instantiate_spine(root, "issue-7", tpl)  # no skill_dir
            data = json.loads(out.read_text(encoding="utf-8"))
            cmd = data["tasks"]["init"]["postconditions"][0]["check"]["command"]
            self.assertIn("python scripts/init_work_area.py issue-7", cmd)
            self.assertNotIn("<commander-skill-dir>", out.read_text(encoding="utf-8"))

    def test_no_clobber_without_force(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tpl = write_fixture(root)
            base = root / ".agent-work" / "issue-7"
            base.mkdir(parents=True)
            sentinel = base / "spine.json"
            sentinel.write_text("SENTINEL-DO-NOT-OVERWRITE", encoding="utf-8")
            result = m.instantiate_spine(root, "issue-7", tpl, skill_dir="skills/commander")
            # Refused: existing file left intact, no write.
            self.assertIsNone(result)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "SENTINEL-DO-NOT-OVERWRITE")

    def test_force_overwrites(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tpl = write_fixture(root)
            base = root / ".agent-work" / "issue-7"
            base.mkdir(parents=True)
            sentinel = base / "spine.json"
            sentinel.write_text("SENTINEL-DO-NOT-OVERWRITE", encoding="utf-8")
            out = m.instantiate_spine(root, "issue-7", tpl, skill_dir="skills/commander", force=True)
            self.assertEqual(out, sentinel)
            data = json.loads(sentinel.read_text(encoding="utf-8"))
            self.assertEqual(data["work_id"], "issue-7")


if __name__ == "__main__":
    unittest.main()
