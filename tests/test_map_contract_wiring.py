"""The map-first contract as it is actually SERVED to a Commander run.

Two different things are pinned here and they must not be confused:

1. **The anchor** (`ContextImperativeAnchor`). PRE-B captured five runs with
   *verified* Commander loads, so both pathless map-first imperatives definitely
   fired -- and orientation still moved not at all (`map_before_src` false on 4
   of 4 runs that read source; bootstrap orientation 0 of 5). The measured
   diagnosis is that **a map-first imperative anchored to a late artifact is not
   a map-first imperative**: the served plan imperative said *"BEFORE authoring
   execute.json, produce a mission frame from the current map"*, and authoring
   `execute.json` happens at the END of a long run, so a run can crawl source for
   fifty calls, read the map, then author the frame and have **complied exactly**
   (run #698: source at call 25, map at call 57). The instruction was never
   ignored; it was satisfied by a sequence it does not constrain. These tests pin
   the CONTEXT imperative to an **act** anchor -- before you open any source file
   -- because `context` precedes `understand` and `plan` in the spine, so an
   instruction anchored there is anchored before exploration.

2. **The wiring** (`ContractWiring`). The two engine-checked command
   postconditions, and specifically their **asymmetry**: `verify-orientation` at
   CONTEXT, `verify-frame` at PLAN, and `verify-frame` deliberately NOT at
   context. See that class's docstring for why the cheap symmetric resolution
   silently destroys the property.

Honest limit, stated here so no reader has to infer it: none of this makes the
frame check *sound*. Measured against the epic's baseline five, the citation
check has sensitivity 0/4 and specificity 0/1. It ships as a regression floor so
map-*ignoring* cannot silently return; the measured defect is map-*lateness*,
and the anchor above -- not this wiring -- is the untested variable aimed at it.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"


def spine() -> dict:
    return json.loads(SPINE.read_text(encoding="utf-8"))


def task(step: str) -> dict:
    return spine()["tasks"][step]


def imperative(step: str) -> str:
    return task(step)["imperative"]


def command_checks(step: str) -> list[tuple[str, str]]:
    """(condition id, command) for every `command` postcondition on `step`."""
    out = []
    for cond in task(step).get("postconditions", []):
        check = cond.get("check") or {}
        if check.get("kind") == "command":
            out.append((cond["id"], check["command"]))
    return out


# =============================================================================
# 1. THE ANCHOR -- an act, not an artifact
# =============================================================================


class ContextImperativeAnchor(unittest.TestCase):
    def test_the_map_read_is_anchored_before_any_source_file_is_opened(self):
        """The whole point. The anchor is an ACT the run cannot postpone."""
        self.assertIn("Before you open any source file", imperative("context"))

    def test_the_context_map_read_is_not_anchored_to_a_late_artifact(self):
        """`execute.json` is authored at the END of a run.

        Anchoring the map read to it is what PRE-B measured as compliance with
        zero orientation. The context step must not reintroduce that anchor --
        not with `execute.json`, and not with any other 'before authoring X'
        phrasing, which is the same defect wearing a different noun.
        """
        prose = imperative("context")
        self.assertNotIn("execute.json", prose)
        self.assertNotIn("before authoring", prose.lower())

    def test_the_context_imperative_names_the_orient_command_it_expects(self):
        """A pathless 'read the map' fired in all five PRE-B runs and moved
        nothing. The imperative names the exact command so the read has a
        receipt, not a recollection."""
        prose = imperative("context")
        self.assertIn("map_orient.py orient", prose)
        self.assertIn("--root <repo-root>", prose)
        self.assertIn("--work-id <work-id>", prose)

    def test_later_source_reads_are_framed_as_confirming_not_building(self):
        """The sequence claim, stated in the prose the agent actually reads."""
        prose = imperative("context")
        self.assertIn("confirming", prose.lower())
        self.assertIn("RESOLVED", prose)

    def test_degraded_is_a_declared_reading_not_a_licence_to_start_from_code(self):
        prose = imperative("context")
        self.assertIn("DEGRADED", prose)
        self.assertIn("before any source read", prose.lower())
        for flag in ("--substitute", "--unmapped", "--escalation"):
            with self.subTest(flag=flag):
                self.assertIn(flag, prose)

    def test_every_declared_context_ref_still_appears_verbatim_in_the_prose(self):
        """`tests/test_context_declaration_lint.py` owns this rule; it is
        restated here because the anchor edit rewrites this exact string, and a
        dropped path would otherwise surface as a confusing failure in a suite
        that is not about this change."""
        prose = imperative("context")
        for entry in task("context")["context_refs"]:
            with self.subTest(path=entry["path"]):
                self.assertIn(entry["path"], prose)

    def test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite(self):
        # "sanctioned degradation" was a phrase of the
        # config_ref-is-absent-by-design block, deleted at #304 as falsified in
        # both directions (docs/agents/ EXISTS here, and Charter ships a task
        # that WRITES docs/agents/engine-config.json). The sentinel is
        # re-pointed at a surviving degraded-mode rule; the property under test
        # -- prose rules a path list cannot express survive the rewrite -- is
        # unchanged.
        prose = imperative("context")
        self.assertIn("record the substitution", prose)
        self.assertIn("degraded is a declared reading, never a licence to start from code", prose)


# =============================================================================
# 2. THE WIRING -- asymmetric on purpose
# =============================================================================


class ContractWiring(unittest.TestCase):
    """`verify-orientation` at CONTEXT, `verify-frame` at PLAN, and NEVER
    `verify-frame` at context.

    The first draft of this plan was ambiguous here and a cold critic BLOCKed
    it, because the cheap resolution -- run the same pair at both steps and let
    an absent frame pass at context -- silently destroys the property the frame
    check exists for. No frame exists at context: the step runs before
    `understand` and `plan`. Making 'absent frame' a pass anywhere teaches the
    checker that an absent frame is acceptable, and the ABSENT-frame refusal is
    the single most important negative case in the whole contract (an absent
    frame must never vacuously pass). The road not to take, recorded so a future
    implementer hitting the contradiction does not take it: do NOT resolve the
    asymmetry by weakening the refusal. If `verify-frame` ever has to be
    context-safe, add a step-scoped subcommand -- never a vacuous pass.
    """

    def test_context_c2_is_a_command_check_naming_verify_orientation(self):
        checks = dict(command_checks("context"))
        self.assertIn("c2", checks)
        self.assertIn("map_orient.py verify-orientation", checks["c2"])

    def test_the_plan_step_carries_a_verify_frame_command_check(self):
        commands = [cmd for _, cmd in command_checks("plan")]
        self.assertTrue(
            any("map_orient.py verify-frame" in cmd for cmd in commands),
            f"no verify-frame check on the plan step: {commands}",
        )

    def test_verify_frame_never_runs_at_the_context_step(self):
        """The load-bearing negative. No frame exists at context."""
        for cond_id, cmd in command_checks("context"):
            with self.subTest(cond=cond_id):
                self.assertNotIn("verify-frame", cmd)

    def test_verify_orientation_is_not_duplicated_onto_the_plan_step(self):
        """Symmetry is the failure mode here, not the goal: the orientation
        receipt is written and gated once, at the step whose anchor makes it
        early."""
        for cond_id, cmd in command_checks("plan"):
            with self.subTest(cond=cond_id):
                self.assertNotIn("verify-orientation", cmd)

    def test_neither_new_check_uses_a_relative_root(self):
        """Command checks inherit the launcher's cwd. `<repo-root>` (added in
        g1) is the robustness token; the pre-existing relative checks are
        fragile-not-broken and are tracked as #341, deliberately not fixed
        here."""
        for step in ("context", "plan"):
            for cond_id, cmd in command_checks(step):
                if "map_orient.py" not in cmd:
                    continue
                with self.subTest(step=step, cond=cond_id):
                    self.assertIn("--root <repo-root>", cmd)
                    self.assertNotIn("--root .", cmd)
                    self.assertNotIn("--root ..", cmd)

    def test_the_plan_check_is_waivable_by_a_human_with_a_recorded_reason(self):
        """The trivial-change escape ('shrink or skip the frame') must survive
        as a RECORDED waiver, not as a silent skip."""
        for cond in task("plan")["postconditions"]:
            check = cond.get("check") or {}
            if "verify-frame" not in check.get("command", ""):
                continue
            policy = cond.get("override_policy")
            self.assertIsNotNone(policy, f"{cond['id']} carries no override_policy")
            self.assertTrue(policy["allowed"])
            self.assertEqual(policy["authority"], "human")
            self.assertTrue(policy["reason_required"])

    def test_the_context_check_policy_is_tighter_than_the_plan_check(self):
        """No `override_policy` on the context check: waiving it needs the
        high-friction `--force` path, which always demands authority + reason."""
        for cond in task("context")["postconditions"]:
            check = cond.get("check") or {}
            if "verify-orientation" not in check.get("command", ""):
                continue
            self.assertIsNone(cond.get("override_policy"))

    def test_the_plan_imperative_names_where_the_frame_must_be_written(self):
        """A check nobody can satisfy is worse than no check: the step that is
        gated has to be told the exact path the gate reads."""
        self.assertIn(".agent-work/<work-id>/MISSION_FRAME.md", imperative("plan"))

    def test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take(self):
        """Required in PROSE, not only in code: a future implementer hitting
        the contradiction ('why not just run both at both steps?') needs the
        answer where they are already reading."""
        prose = imperative("plan")
        self.assertIn("verify-frame", prose)
        self.assertIn("no frame exists", prose.lower())

    def test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix(self):
        """Do not overclaim: the plan-step check inherits the late-anchor defect
        it was measured against."""
        self.assertIn("floor", imperative("plan").lower())


# =============================================================================
# 3. The script is shipped with the skill that runs it
# =============================================================================


class ScriptIsBundled(unittest.TestCase):
    def _installer(self):
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(
            "install_constellation_under_test", ROOT / "scripts" / "install_constellation.py"
        )
        module = importlib.util.module_from_spec(spec)
        # A frozen dataclass resolves its own module through sys.modules at class
        # creation; without this line the import raises on 3.14.
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_map_orient_ships_with_every_skill_whose_template_invokes_it(self):
        """The drift this guards: `gauge_reader.py` was never added to any of
        the ten bundles carrying `checklist_engine.py`, so the feature was inert
        in every install since it shipped and nothing reported it. A command
        postcondition naming a script that was never installed fails at the
        gate, in a run, with a confusing error."""
        m = self._installer()
        for skill in ("commander",):
            with self.subTest(skill=skill):
                self.assertIn(
                    "map_orient.py",
                    m.expand_script_bundle(m.SKILL_SCRIPT_BUNDLES[skill]),
                )

    def test_the_bundled_script_source_actually_exists(self):
        m = self._installer()
        self.assertTrue(
            m.script_source_path("map_orient.py", ROOT / "scripts").is_file()
        )


if __name__ == "__main__":
    unittest.main()
