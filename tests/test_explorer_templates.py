"""Verifier<->template cross-check for the constellation-explorer engine artifacts.

The two halves of the hard gate ship in different gates: the verifier scripts
(g1) and the templates that must feed them (g2). This suite proves them against
each other with real fixtures and no mocks — a template that emits a format the
verifier cannot parse, or a fresh draft the verifier *passes*, would silently gut
"no work is cut from an unconfirmed design." (DESIGN_SPEC Testing pathways 1b/2.)
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "skills" / "explorer" / "templates"
SPINE_TEMPLATE = TEMPLATES / "EXPLORER_SPINE.template.json"
CYCLE_TEMPLATE = TEMPLATES / "CYCLE.template.json"
SPEC_TEMPLATE = TEMPLATES / "DESIGN_SPEC.template.md"
ENGINE = ROOT / "scripts" / "checklist_engine.py"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# DESIGN_SPEC.template.md -> verify_spec_confirmed.py
#
# The shipped template is a DRAFT that MUST be refused. A CONFIRMED variant is
# built by editing ONLY the fields the template designates. Each edit is a
# stable substring so a drift in the template surfaces as a KeyError-style
# assertion here rather than a silently-wrong fixture.
# --------------------------------------------------------------------------- #
BANNER = "**UNCONFIRMED — DO NOT CUT**"
STATUS_DRAFT = "- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**"
STATUS_CONFIRMED = "- **Status: CONFIRMED**"
CONFIRMED_BY_BLANK = "- Confirmed by:"
CONFIRMED_BY_FILLED = "- Confirmed by: tester (human)"
DATE_BLANK = "- Date:"
DATE_FILLED = "- Date: 2026-07-07"
EMPTY_ROW = "| F1 | intent-fit | MAJOR | worked example: the critic's attack on a deliberate decision |  |  |"
FILLED_ROW = "| F1 | intent-fit | MAJOR | worked example: the critic's attack on a deliberate decision | EDIT | addressed in chosen design |"


def _require(text, needle):
    assert needle in text, f"template no longer contains designated field: {needle!r}"
    return text


def _without_banner(text):
    _require(text, BANNER)
    return text.replace(BANNER + "\n", "", 1)


def _fill_table(text):
    _require(text, EMPTY_ROW)
    return text.replace(EMPTY_ROW, FILLED_ROW)


def _confirmed(text):
    """Edit the shipped DRAFT into a CONFIRMED spec touching only the designated
    fields: drop the marker banner, flip Status, fill confirmer + date, fill the
    Disposition/Reason cells."""
    text = _without_banner(text)
    text = _require(text, STATUS_DRAFT).replace(STATUS_DRAFT, STATUS_CONFIRMED)
    text = _require(text, CONFIRMED_BY_BLANK).replace(CONFIRMED_BY_BLANK, CONFIRMED_BY_FILLED)
    text = _require(text, DATE_BLANK).replace(DATE_BLANK, DATE_FILLED)
    return _fill_table(text)


class DesignSpecTemplateCrossCheck(unittest.TestCase):
    def setUp(self):
        self.m = _load("verify_spec_confirmed")
        self.tpl = SPEC_TEMPLATE.read_text(encoding="utf-8")

    def test_shipped_draft_refused_confirm_phase(self):
        # The point of the whole gate: a fresh draft must NOT pass.
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(self.tpl, "confirm")
        self.assertIn("UNCONFIRMED", str(ctx.exception))

    def test_shipped_draft_refused_review_phase(self):
        # Still refused -- but on the EMPTY DISPOSITION CELL, which is review's
        # actual job, not on the marker. Before #428 this asserted "UNCONFIRMED",
        # which is what made `--phase review` unpassable: the shipped template
        # carries the marker deliberately and it only comes off at confirm, so
        # every conformant draft hit the marker refusal first and no amount of
        # critic triage could ever turn review green.
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(self.tpl, "review")
        self.assertIn("Disposition", str(ctx.exception))

    def test_shipped_draft_passes_review_once_table_filled_marker_still_on(self):
        # #428, the payoff: this is the REAL explorer sequence -- critic findings
        # triaged, marker deliberately still standing (it comes off at confirm).
        # Review must go green here or the explorer's review gate can never close.
        text = _fill_table(self.tpl)
        self.assertIsNotNone(self.m._unconfirmed_marker_hit(text), "fixture lost the marker")
        self.m.verify_spec_confirmed(text, "review")  # no raise

    def test_shipped_draft_with_table_filled_still_refused_at_confirm(self):
        # The other direction: relaxing review must not leak into confirm. The
        # marker still refuses the cut.
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(_fill_table(self.tpl), "confirm")
        self.assertIn("UNCONFIRMED", str(ctx.exception))

    def test_draft_review_fails_when_table_incomplete(self):
        # Marker removed but the shipped table still has an empty Disposition
        # cell -> review must refuse on the incomplete table, not the marker.
        text = _without_banner(self.tpl)
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "review")
        self.assertIn("Disposition", str(ctx.exception))

    def test_draft_review_passes_when_table_complete(self):
        # Status still DRAFT, marker gone, every Disposition filled -> review
        # passes (review does not gate on confirmation status).
        text = _fill_table(_without_banner(self.tpl))
        self.m.verify_spec_confirmed(text, "review")  # no raise

    def test_confirmed_variant_passes_both_phases(self):
        confirmed = _confirmed(self.tpl)
        self.m.verify_spec_confirmed(confirmed, "review")  # no raise
        self.m.verify_spec_confirmed(confirmed, "confirm")  # no raise

    def test_confirmed_variant_carries_no_residual_marker(self):
        # Guard against a second standalone marker line lurking in the body: the
        # confirmed variant must be clean, or the gate would refuse a good spec.
        confirmed = _confirmed(self.tpl)
        self.assertIsNone(self.m._unconfirmed_marker_hit(confirmed))

    # Each Confirmation field tested blank INDEPENDENTLY with the others filled
    # (g1 lesson: a combined-blank fixture masked a real newline-bleed bug).
    def test_blank_status_alone_fails_confirm(self):
        text = _confirmed(self.tpl).replace(STATUS_CONFIRMED, "- **Status: DRAFT**")
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("CONFIRMED", str(ctx.exception))

    def test_blank_confirmed_by_alone_fails_confirm(self):
        text = _confirmed(self.tpl).replace(CONFIRMED_BY_FILLED, CONFIRMED_BY_BLANK)
        self.assertEqual(self.m.parse_confirmation(text)["confirmed_by"], "")
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("Confirmed by", str(ctx.exception))

    def test_blank_date_alone_fails_confirm(self):
        text = _confirmed(self.tpl).replace(DATE_FILLED, DATE_BLANK)
        self.assertEqual(self.m.parse_confirmation(text)["date"], "")
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("Date", str(ctx.exception))

    def test_findings_table_uses_the_fixed_columns(self):
        # The header row is contractual; assert the exact canonical columns are
        # what the verifier actually parses out of the shipped template.
        self.assertIn(
            "| ID | Lens | Severity | Finding | Disposition | Reason |", self.tpl
        )


# --------------------------------------------------------------------------- #
# CYCLE.template.json -> verify_cycles.py
# --------------------------------------------------------------------------- #
class CycleTemplateCrossCheck(unittest.TestCase):
    def setUp(self):
        self.m = _load("verify_cycles")
        self.tpl = json.loads(CYCLE_TEMPLATE.read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.work_area = self.root / ".agent-work" / "explore-topic"
        self.work_area.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_cycle(self, name, data):
        (self.work_area / name).write_text(json.dumps(data), encoding="utf-8")

    def _verify(self):
        self.m.verify_cycles(self.root, "explore-topic")

    def test_template_is_survey_and_ships_unconsolidated(self):
        # This is exactly what verify_cycles keys on: a shipped cycle is a survey
        # with consolidation:null, and only a consolidated cycle lets explore close.
        self.assertEqual(self.tpl["type"], "survey")
        self.assertIsNone(self.tpl["consolidation"])
        # The flavor field ships as a placeholder naming the three flavors.
        for flavor in ("shotgun", "compare", "refine"):
            self.assertIn(flavor, self.tpl["flavor"])

    def test_zero_cycles_fails_against_fresh_area(self):
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self._verify()
        self.assertIn("zero cycles", str(ctx.exception))

    def test_unconsolidated_cycle_from_template_fails(self):
        # The template shipped as-is is an UNCONSOLIDATED cycle.
        self._write_cycle("cycle-1.json", self.tpl)
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self._verify()
        self.assertIn("unconsolidated", str(ctx.exception))

    def test_consolidated_cycles_from_template_pass(self):
        consolidated = dict(self.tpl)
        consolidated["consolidation"] = {"verdict": "converge to spec", "summary": "clustered and culled"}
        self._write_cycle("cycle-1.json", consolidated)
        self._write_cycle("cycle-2.json", consolidated)
        self._verify()  # no raise

    def test_one_unconsolidated_among_consolidated_fails(self):
        consolidated = dict(self.tpl)
        consolidated["consolidation"] = {"verdict": "another cycle"}
        self._write_cycle("cycle-1.json", consolidated)
        self._write_cycle("cycle-2.json", self.tpl)  # still null
        with self.assertRaises(self.m.CyclesVerificationError) as ctx:
            self._verify()
        self.assertIn("unconsolidated", str(ctx.exception))


# --------------------------------------------------------------------------- #
# CYCLE.template.json -> checklist_engine.py, driven config-less
#
# The cycle survey is instantiated into a work area and driven by the engine in
# a directory with NO engine-config file. A dangling `config_ref` to an absent
# engine-config.json (the shape a fresh install has) must never make the engine
# refuse to load or drive the survey. (Carry-forward tc2 / DESIGN_SPEC "fail
# visibly; no silent fallback" — a survey needs no config and must say so.)
# --------------------------------------------------------------------------- #
class CycleSurveyConfiglessRuntime(unittest.TestCase):
    def setUp(self):
        self.tpl = json.loads(CYCLE_TEMPLATE.read_text(encoding="utf-8"))

    def test_template_carries_no_dangling_config_ref(self):
        # A survey never consults rework_cap (reopen raises for non-gated), so it
        # needs no config. The key is dropped rather than pointed at a file a
        # fresh install won't have.
        self.assertNotIn("config_ref", self.tpl)

    def test_engine_drives_cycle_survey_without_engine_config_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # No docs/agents/engine-config.json anywhere on the config search
            # path (neither cwd=root nor the checklist's own dir).
            self.assertFalse((root / "docs" / "agents" / "engine-config.json").exists())
            work_area = root / ".agent-work" / "explore-topic"
            work_area.mkdir(parents=True)
            cycle = dict(self.tpl)
            cycle["work_id"] = "explore-topic"
            cycle["cycle"] = "1"
            cycle["flavor"] = "shotgun"
            cycle_path = work_area / "cycle-1.json"
            cycle_path.write_text(json.dumps(cycle), encoding="utf-8")

            def run(*verb):
                return subprocess.run(
                    [sys.executable, str(ENGINE), "--file", str(cycle_path), *verb],
                    capture_output=True, text=True, cwd=str(root),
                )

            claim = run("claim", "--session-id", "explore-topic",
                        "--claimed-by", "explorer", "--worktree", ".")
            self.assertEqual(claim.returncode, 0, claim.stderr)
            start = run("start", "c0-frame", "--session-id", "explore-topic")
            self.assertEqual(start.returncode, 0, start.stderr)
            record = run("record", "c0-frame", "--result", "pass",
                         "--session-id", "explore-topic")
            self.assertEqual(record.returncode, 0, record.stderr)
            for item in ("q1", "x1"):
                skip = run("skip", item, "--reason", "config-less drive test",
                           "--session-id", "explore-topic")
                self.assertEqual(skip.returncode, 0, skip.stderr)
            consolidate = run("consolidate", "--verdict", "another cycle",
                              "--summary", "framed", "--session-id", "explore-topic")
            self.assertEqual(consolidate.returncode, 0, consolidate.stderr)


# --------------------------------------------------------------------------- #
# EXPLORER_SPINE.template.json -> init_work_area.py --spine + checklist_engine.py
# --------------------------------------------------------------------------- #
class ExplorerSpineCrossCheck(unittest.TestCase):
    def setUp(self):
        self.iwa = _load("init_work_area")
        self.spine = json.loads(SPINE_TEMPLATE.read_text(encoding="utf-8"))

    def test_steps_in_spec_order(self):
        self.assertEqual(
            self.spine["items"],
            ["init", "context", "explore", "spec", "review", "confirm", "route"],
        )

    def test_inline_rework_cap_is_99(self):
        # The Critical-review para: the default cap of 3 would hard-block the
        # critic->re-explore loop in any repo without an engine-config file.
        self.assertEqual(self.spine.get("config", {}).get("rework_cap"), 99)

    def test_explore_closes_on_user_decision_and_verify_cycles(self):
        posts = self.spine["tasks"]["explore"]["postconditions"]
        kinds = [(p["check"] or {}).get("kind") for p in posts]
        self.assertIn("artifact", kinds)
        artifact = next(p for p in posts if (p["check"] or {}).get("kind") == "artifact")
        self.assertEqual(artifact["check"]["evidence_type"], "user-decision")
        command = next(p for p in posts if (p["check"] or {}).get("kind") == "command")
        self.assertIn("verify_cycles.py", command["check"]["command"])

    def test_review_runs_verify_spec_confirmed_review_phase(self):
        posts = self.spine["tasks"]["review"]["postconditions"]
        command = next(p for p in posts if (p["check"] or {}).get("kind") == "command")
        self.assertIn("verify_spec_confirmed.py", command["check"]["command"])
        self.assertIn("--phase review", command["check"]["command"])

    def test_confirm_needs_user_decision_and_verify_spec_confirmed(self):
        posts = self.spine["tasks"]["confirm"]["postconditions"]
        artifact = next(p for p in posts if (p["check"] or {}).get("kind") == "artifact")
        self.assertEqual(artifact["check"]["evidence_type"], "user-decision")
        command = next(p for p in posts if (p["check"] or {}).get("kind") == "command")
        self.assertIn("verify_spec_confirmed.py", command["check"]["command"])
        # confirm phase is the default: no explicit --phase review here.
        self.assertNotIn("--phase review", command["check"]["command"])

    def test_every_bundled_script_path_uses_the_generic_token(self):
        # No <commander-skill-dir> should leak into the explorer spine; every
        # bundled-script path must use the generic <skill-dir> token.
        raw = SPINE_TEMPLATE.read_text(encoding="utf-8")
        self.assertNotIn("<commander-skill-dir>", raw)
        self.assertIn("<skill-dir>/scripts/", raw)

    def test_instantiates_and_engine_can_claim_and_start(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Resolve script paths against the REAL repo so the command
            # postconditions reference scripts that actually exist. Use POSIX
            # form so the substituted path stays valid JSON on Windows.
            out = self.iwa.instantiate_spine(
                root, "explore-topic", SPINE_TEMPLATE, skill_dir=ROOT.as_posix()
            )
            self.assertIsNotNone(out)
            text = out.read_text(encoding="utf-8")

            # No unresolved skill-dir token survived instantiation.
            self.assertNotIn("<skill-dir>", text)
            # Resolved command postconditions reference real script paths.
            self.assertIn("scripts/verify_cycles.py", text)
            self.assertIn("scripts/verify_spec_confirmed.py", text)
            self.assertTrue((ROOT / "scripts" / "verify_cycles.py").is_file())
            self.assertTrue((ROOT / "scripts" / "verify_spec_confirmed.py").is_file())

            # The engine can claim the lease and start the first gate.
            # Run from `root`: the engine enforces worktree isolation natively
            # against the `origin.worktree` stamped at instantiation (#315/#568),
            # and a real explorer drives this spine from the tree it was
            # instantiated into. Without `cwd`, the engine would read the test
            # runner's cwd and correctly refuse. This test is about the template
            # being instantiable and drivable, so give it the honest cwd rather
            # than exempting it from the guard.
            claim = subprocess.run(
                [sys.executable, str(ENGINE), "--file", str(out), "claim",
                 "--session-id", "explore-topic", "--claimed-by", "explorer", "--worktree", "."],
                capture_output=True, text=True, cwd=str(root),
            )
            self.assertEqual(claim.returncode, 0, claim.stderr)
            start = subprocess.run(
                [sys.executable, str(ENGINE), "--file", str(out), "start", "init",
                 "--session-id", "explore-topic"],
                capture_output=True, text=True, cwd=str(root),
            )
            self.assertEqual(start.returncode, 0, start.stderr)
            self.assertIn("init -> in-progress", start.stdout)


if __name__ == "__main__":
    unittest.main()
