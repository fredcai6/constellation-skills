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


def map_check_note(step: str) -> str:
    """The step's `map_check_note` -- why its check is worded and placed as it is.

    The reasoning used to sit inline in the imperative, where every run paid to
    read text only an editor of the check can act on. It moved one field over,
    onto the same step: `render_human` emits `imperative`, the conditions,
    `constraints`, `anchors` and `directives` and nothing else, so a sibling
    field costs a run nothing while sitting where whoever edits the step is
    already looking. Same role as `execute`'s `context_headroom_note`. These
    tests moved with it, so the guard still fails if the reasoning is deleted
    rather than relocated."""
    return task(step)["map_check_note"]


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

    def test_the_plan_note_records_the_asymmetry_and_the_road_not_to_take(self):
        """Required in PROSE, not only in code: a future implementer hitting
        the contradiction ('why not just run both at both steps?') needs the
        answer where they are already reading -- which is the step, not a
        doctrine file one hop away."""
        prose = map_check_note("plan")
        self.assertIn("verify-frame", prose)
        self.assertIn("no frame exists", prose.lower())

    def test_the_plan_note_states_that_the_check_is_a_floor_not_the_fix(self):
        """Do not overclaim: the plan-step check inherits the late-anchor defect
        it was measured against, and the measurement (sensitivity 0/4,
        specificity 0/1) is recorded with it."""
        prose = map_check_note("plan").lower()
        self.assertIn("floor", prose)
        self.assertIn("0/4", prose)

    def test_the_plan_note_interprets_the_measurement_it_cites(self):
        """The bare numbers mislead in a specific, reproducible way: a reader
        who sees `0/4` and `still blocking` reaches for `--report-only`. What
        makes them readable is the ratified finding -- the four defective runs
        would have PASSED the gate, so this is zero discriminating power against
        that population, not a floor that happened to face a clean baseline."""
        prose = map_check_note("plan").lower()
        self.assertIn("zero discriminating power", prose)
        self.assertIn("not a loophole someone might find", prose)

    def test_the_plan_note_records_what_the_one_firing_was(self):
        """Specificity 0/1 reads as a defect until you know the firing was
        #716, whose correct answer was non-engagement -- i.e. the waivable
        trivial-change escape behaving exactly as designed."""
        prose = map_check_note("plan").lower()
        self.assertIn("#716", prose)
        self.assertIn("non-engagement", prose)

    def test_both_notes_point_at_the_ruling_that_settled_this(self):
        """A measurement with no route back to its adjudication gets
        re-litigated. Both notes name the archived log."""
        for step in ("context", "plan"):
            with self.subTest(step=step):
                self.assertIn(
                    ".agent-work/archive/2026-08-03-epic-298/ADMIRAL_LOG.md",
                    map_check_note(step),
                )

    def test_the_ruling_the_notes_cite_is_actually_in_the_tree(self):
        """A pointer to a file nobody kept is worse than no pointer. The log is
        tracked, so this asserts the citation still resolves."""
        log = ROOT / ".agent-work" / "archive" / "2026-08-03-epic-298" / "ADMIRAL_LOG.md"
        self.assertTrue(log.is_file(), f"{log} is missing; the notes cite it")
        text = log.read_text(encoding="utf-8")
        self.assertIn("sensitivity 0/4 and specificity 0/1", text)
        self.assertIn("zero discriminating power", text)

    def test_the_plan_note_records_the_rescue_that_failed(self):
        """Pre-crawl expectations in the receipt were tested and do not work.
        Without that on the record it is the first thing a reader proposes."""
        prose = map_check_note("plan").lower()
        self.assertIn("only ordering evidence is the transcript", prose)

    def test_the_context_note_records_why_the_anchor_is_an_act(self):
        """The late-artifact diagnosis is what justifies `context`'s wording;
        it belongs on `context`, not folded into the plan step's note."""
        prose = map_check_note("context").lower()
        self.assertIn("before you open any source file", prose)
        self.assertIn("call 57", prose)

    def test_each_note_sits_immediately_after_the_imperative_it_qualifies(self):
        """Relocating the reasoning is only safe while an editor still finds it.

        This was a prose pointer inside the imperative ("...is in this step's
        map_check_note"). A cold read killed it: the line spends a run's context
        telling that run NOT to read something, which is the definition of text
        that does not earn its place. Adjacency does the same job for free --
        an editor opening the step sees `map_check_note` as the very next key --
        and it is a stronger guarantee than prose, because a pointer can go
        stale while key order cannot."""
        for step in ("context", "plan"):
            with self.subTest(step=step):
                keys = list(task(step).keys())
                self.assertEqual(
                    keys[keys.index("imperative") + 1], "map_check_note",
                    f"{step}: map_check_note must directly follow imperative",
                )
                self.assertNotIn(
                    "map_check_note", imperative(step),
                    f"{step}: the note is adjacent; a prose pointer is dead weight",
                )

    def test_the_notes_are_not_rendered_to_a_run(self):
        """The whole reason this text is a sibling field and not imperative
        prose: `render_human` emits a fixed set of fields, and a note is not
        one of them. If that ever changes, the runtime cost comes back and
        these notes have to shrink to what a run can act on."""
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(
            "checklist_engine_under_test", ROOT / "scripts" / "checklist_engine.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cl = spine()
        for earlier in ("init", "context", "understand"):
            cl["tasks"][earlier]["status"] = "complete"
        cl["tasks"]["plan"]["status"] = "in-progress"
        rendered = module.current(cl)
        self.assertIn(imperative("plan")[:60], rendered)
        self.assertNotIn("sensitivity 0/4", rendered)


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
