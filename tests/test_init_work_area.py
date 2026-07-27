import importlib.util
import json
import tempfile
import unittest
import unittest.mock
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


# Fixture carrying the generic <skill-dir> token instead of <commander-skill-dir>,
# to exercise resolve_spine's generalization independently of the commander token.
GENERIC_SPINE_FIXTURE = json.dumps(
    {
        "work_id": "<work-id>",
        "tasks": {
            "init": {
                "postconditions": [
                    {
                        "check": {
                            "kind": "command",
                            "command": "python <skill-dir>/scripts/init_work_area.py <work-id>",
                        }
                    }
                ]
            }
        },
    },
    indent=2,
)


def write_generic_fixture(d: Path) -> Path:
    tpl = d / "GENERIC_SPINE.template.json"
    tpl.write_text(GENERIC_SPINE_FIXTURE, encoding="utf-8")
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

    def test_refuses_a_root_that_is_already_the_agent_work_dir(self):
        # The flag name reads as "the agent-work root", so passing .agent-work
        # itself is an easy slip; unguarded it silently scaffolds
        # .agent-work/.agent-work/<work-id>/ (f1Brainz 624-phase0).
        m = load()
        with tempfile.TemporaryDirectory() as d:
            already = Path(d) / ".agent-work"
            already.mkdir()
            with self.assertRaises(SystemExit) as ctx:
                m.init_work_area(already, "issue-7")
            self.assertIn(".agent-work", str(ctx.exception))
            self.assertFalse((already / ".agent-work").exists())

    def test_refusal_names_the_parent_as_the_intended_root(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            already = Path(d) / ".agent-work"
            already.mkdir()
            with self.assertRaises(SystemExit) as ctx:
                m.init_work_area(already, "issue-7")
            self.assertIn(str(Path(d)), str(ctx.exception))

    def test_a_root_merely_containing_agent_work_is_fine(self):
        # Only the final segment is the footgun; a project legitimately named
        # e.g. <tmp>/.agent-work-notes must still scaffold.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / ".agent-work-notes"
            root.mkdir()
            base = m.init_work_area(root, "issue-7")
            self.assertTrue(base.is_dir())


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
            (root / "skills" / "commander" / "scripts").mkdir(parents=True)
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
            (root / "skills" / "commander" / "scripts").mkdir(parents=True)
            tpl = write_fixture(root)
            base = root / ".agent-work" / "issue-7"
            base.mkdir(parents=True)
            sentinel = base / "spine.json"
            sentinel.write_text("SENTINEL-DO-NOT-OVERWRITE", encoding="utf-8")
            out = m.instantiate_spine(root, "issue-7", tpl, skill_dir="skills/commander", force=True)
            self.assertEqual(out, sentinel)
            data = json.loads(sentinel.read_text(encoding="utf-8"))
            self.assertEqual(data["work_id"], "issue-7")

    def test_generic_skill_dir_token_resolves_with_explicit_skill_dir(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "skills" / "explorer" / "scripts").mkdir(parents=True)
            tpl = write_generic_fixture(root)
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "issue-7", "skills/explorer", root)
            data = json.loads(resolved)
            self.assertNotIn("<skill-dir>", resolved)
            self.assertIn(
                "skills/explorer/scripts/init_work_area.py issue-7",
                data["tasks"]["init"]["postconditions"][0]["check"]["command"],
            )

    def test_generic_skill_dir_token_autodetects_without_skill_dir(self):
        # Same auto-detect rule as the commander token: bundled scripts at
        # <root>/scripts collapses "<skill-dir>/scripts" -> "scripts".
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            tpl = write_generic_fixture(root)
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "issue-7", None, root)
            data = json.loads(resolved)
            self.assertNotIn("<skill-dir>", resolved)
            self.assertIn(
                "python scripts/init_work_area.py issue-7",
                data["tasks"]["init"]["postconditions"][0]["check"]["command"],
            )

    def test_generic_skill_dir_token_bare_falls_back_to_root_without_scripts_dir(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # no <root>/scripts present
            tpl = write_generic_fixture(root)
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "issue-7", None, root)
            data = json.loads(resolved)
            self.assertIn(
                "python ./scripts/init_work_area.py issue-7",
                data["tasks"]["init"]["postconditions"][0]["check"]["command"],
            )

    def test_explicit_skill_dir_without_scripts_fails_visibly(self):
        # The issue-99 T2 regression: an explicit --skill-dir whose scripts/
        # does not exist (source repo, repo-relative skills/<name>) must refuse
        # loudly instead of writing a spine with broken command-check paths.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()  # source-repo layout
            tpl = write_fixture(root)
            with self.assertRaises(SystemExit) as ctx:
                m.instantiate_spine(root, "issue-7", tpl, skill_dir="skills/commander")
            self.assertIn("scripts/", str(ctx.exception))
            self.assertFalse((root / ".agent-work" / "issue-7" / "spine.json").exists())

    def test_commander_token_byte_identical_alongside_generic_token(self):
        # Both tokens can coexist in one template without cross-resolution.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            mixed = json.dumps(
                {
                    "commander_cmd": "python <commander-skill-dir>/scripts/x.py <work-id>",
                    "generic_cmd": "python <skill-dir>/scripts/x.py <work-id>",
                }
            )
            resolved = m.resolve_spine(mixed, "issue-7", None, root)
            data = json.loads(resolved)
            self.assertEqual(data["commander_cmd"], "python scripts/x.py issue-7")
            self.assertEqual(data["generic_cmd"], "python scripts/x.py issue-7")


class ShippedSpineTemplatesTests(unittest.TestCase):
    """Every shipped spine template must materialize with no residual work-id
    placeholder the resolver is responsible for. Regression guard for the
    ADMIRAL_SPINE `<epic-id>` bug: the resolver substitutes `<work-id>` only, so
    an admiral spine authored with `<epic-id>` left literal placeholders in the
    execute.p2 / closeout.c2 command checks and refused `start`."""

    def _materialize(self, m, rel_template):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()  # source-repo layout: bundled scripts at root
            tpl = ROOT / rel_template
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "epic-42", None, root)
            data = json.loads(resolved)  # must stay valid JSON
            return resolved, data

    def test_admiral_spine_resolves_work_id_cleanly(self):
        m = load()
        resolved, data = self._materialize(m, "skills/admiral/templates/ADMIRAL_SPINE.template.json")
        self.assertNotIn("<epic-id>", resolved)
        self.assertNotIn("<work-id>", resolved)
        self.assertEqual(data["work_id"], "epic-42")
        # The two command-check preconditions that previously carried the literal
        # placeholder now reference the real work id.
        blob = json.dumps(data)
        self.assertIn("epic-42", blob)

    def test_admiral_spine_resolves_admiral_skill_dir_and_session_id_cleanly(self):
        # The epic-101/epic-138 recurrence (#114/#154): ADMIRAL_SPINE's own
        # <admiral-skill-dir>/<admiral-session-id> tokens (distinct from the
        # commander's <commander-skill-dir>/<commander-session-id>) were never
        # in the resolver's hardcoded vocabulary, so they survived resolution
        # literally inside the execute.p2 / feedback.c2 / feedback.c6 command
        # checks -- exactly the "9 unresolved placeholders" epic-138 hit.
        m = load()
        resolved, _data = self._materialize(m, "skills/admiral/templates/ADMIRAL_SPINE.template.json")
        self.assertNotIn("<admiral-skill-dir>", resolved)
        self.assertNotIn("<admiral-session-id>", resolved)
        # The post-init assertion must not fire on the real, correctly-resolved template.
        m._assert_no_resolver_placeholders(resolved)

    def test_commander_and_explorer_spines_resolve_work_id_cleanly(self):
        m = load()
        for rel in (
            "skills/commander/templates/COMMANDER_SPINE.template.json",
            "skills/explorer/templates/EXPLORER_SPINE.template.json",
        ):
            resolved, data = self._materialize(m, rel)
            self.assertNotIn("<work-id>", resolved, rel)
            self.assertEqual(data["work_id"], "epic-42", rel)
            # Neither shipped template trips the post-init assertion: their
            # remaining literals (<engine>, <date>, <N>, <path>, <file>,
            # <spine-template>) are prose placeholders, not resolver-owned tokens.
            m._assert_no_resolver_placeholders(resolved)


class GenericRoleTokenTests(unittest.TestCase):
    """resolve_spine discovers <role-skill-dir>/<role-session-id> tokens by
    pattern rather than a hardcoded per-role list, so a role invented after
    this fix (or one whose skill directory name itself carries a hyphen, e.g.
    a hypothetical lessons-auditor) does not recur the #114/#154 defect."""

    def test_admiral_role_tokens_resolve_with_explicit_skill_dir(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "skills" / "admiral" / "scripts").mkdir(parents=True)
            tpl = root / "SPINE.template.json"
            tpl.write_text(
                json.dumps(
                    {
                        "work_id": "<work-id>",
                        "session_id": "<admiral-session-id>",
                        "cmd": "python <admiral-skill-dir>/scripts/x.py <work-id>",
                    }
                ),
                encoding="utf-8",
            )
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "issue-7", "skills/admiral", root)
            data = json.loads(resolved)
            self.assertNotIn("<admiral-skill-dir>", resolved)
            self.assertNotIn("<admiral-session-id>", resolved)
            self.assertEqual(data["session_id"], "admiral-issue-7")
            self.assertIn("skills/admiral/scripts/x.py issue-7", data["cmd"])

    def test_hyphenated_role_name_skill_dir_token_resolves(self):
        # A role name that itself contains a hyphen (e.g. a future
        # lessons-auditor spine) must still be discovered as one token, not
        # mis-parsed at the first internal hyphen.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()  # source-repo layout: auto-detect collapse
            tpl = root / "SPINE.template.json"
            tpl.write_text(
                '{"cmd": "python <lessons-auditor-skill-dir>/scripts/x.py <work-id>", '
                '"session_id": "<lessons-auditor-session-id>"}',
                encoding="utf-8",
            )
            resolved = m.resolve_spine(tpl.read_text(encoding="utf-8"), "issue-7", None, root)
            data = json.loads(resolved)
            self.assertIn("python scripts/x.py issue-7", data["cmd"])
            self.assertEqual(data["session_id"], "lessons-auditor-issue-7")
            m._assert_no_resolver_placeholders(resolved)


class ResolverPlaceholderAssertionTests(unittest.TestCase):
    """Direct unit coverage of the post-init hard check, independent of
    resolve_spine, since under the generalized resolver every real role token
    it discovers is (by construction) fully substituted -- this is the
    defense-in-depth guard for a future resolver regression or an
    out-of-pattern token (e.g. a role name with characters outside
    [a-zA-Z0-9-])."""

    def test_raises_on_leftover_work_id(self):
        m = load()
        with self.assertRaises(SystemExit) as ctx:
            m._assert_no_resolver_placeholders('{"work_id": "<work-id>"}')
        self.assertIn("<work-id>", str(ctx.exception))

    def test_raises_on_leftover_role_skill_dir(self):
        m = load()
        with self.assertRaises(SystemExit) as ctx:
            m._assert_no_resolver_placeholders('{"cmd": "python <admiral-skill-dir>/x.py"}')
        self.assertIn("<admiral-skill-dir>", str(ctx.exception))

    def test_raises_on_leftover_role_session_id(self):
        m = load()
        with self.assertRaises(SystemExit) as ctx:
            m._assert_no_resolver_placeholders('{"session_id": "<admiral-session-id>"}')
        self.assertIn("<admiral-session-id>", str(ctx.exception))

    def test_does_not_raise_on_benign_prose_placeholders(self):
        # <engine>, <date>, <N>, <path>, <file>, <spine-template> are documentation
        # placeholders this script never resolves -- they must not false-positive.
        m = load()
        m._assert_no_resolver_placeholders(
            "<engine> claim ...; archive/<date>-<work>; cycle-<N>.json; "
            "check <path>; see <file>; --spine <spine-template>"
        )

    def test_instantiate_spine_leaves_non_resolver_placeholders_alone(self):
        # A template placeholder outside the <role-skill-dir>/<role-session-id>/
        # <work-id> families (an operator-filled field, matching <engine>/<date>/<N>
        # convention) is not the resolver's job and must not trip the guard or
        # block the write -- confirms the guard is scoped to resolver-owned
        # families only, not a blanket "no <...> anywhere" rule.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            tpl = root / "SPINE.template.json"
            tpl.write_text('{"work_id": "<work-id>", "note": "<operator-fills-this-in>"}', encoding="utf-8")
            out = m.instantiate_spine(root, "issue-7", tpl)
            self.assertTrue(out.exists())
            self.assertIn("<operator-fills-this-in>", out.read_text(encoding="utf-8"))

    def test_instantiate_spine_raises_when_a_resolver_owned_token_cannot_resolve(self):
        # Wires the guard into instantiate_spine itself: given a resolve_spine that
        # regresses (returns text with a resolver-owned placeholder still literal --
        # the exact epic-101/epic-138 failure mode, simulated here since the real
        # resolve_spine cannot itself leave one behind by construction), instantiate_spine
        # must refuse to write the broken spine to disk rather than stranding the engine
        # on it later.
        m = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tpl = root / "SPINE.template.json"
            tpl.write_text('{"work_id": "<work-id>"}', encoding="utf-8")
            dest = root / ".agent-work" / "issue-7" / "spine.json"
            with unittest.mock.patch.object(
                m, "resolve_spine", return_value='{"cmd": "python <admiral-skill-dir>/x.py issue-7"}'
            ):
                with self.assertRaises(SystemExit):
                    m.instantiate_spine(root, "issue-7", tpl)
            self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
