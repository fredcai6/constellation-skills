"""Every shipped command check must actually run after instantiation
(epic-559/b-instructions-to-checks, rework r3).

The cold reviewer found `REVIEW_SURVEY.template.json`'s `r6-fowler.c1` shipping
a check command that still held `<fowler-pass-record-path>` -- a token nothing
ever substitutes, so the check is non-functional out of the box even though a
prior census called the row "already converted, no action": the census checked
that a command existed, never that it would actually run.

This sweeps all six templates named in `skills/workbench/references/checklist-engine.md`'s
own "Template set" table (the canonical list of shipped role checklists) for
command-kind pre/postconditions whose text still carries a bracket token after
the SAME substitution `scripts/init_work_area.py`'s `resolve_spine` performs for
real (`<work-id>`, `<repo-root>`, `<*-skill-dir>`, `<*-session-id>`).

Two site classes survive that substitution and both are asserted here:

  * A curated, closed allowlist of intentional author-fill-in slots
    (`<exact test command>` in EXECUTE_PLAN.template.json / IMPLEMENTER_PLAN.template.json)
    -- prose an authoring Commander/implementer necessarily writes fresh for
    each concrete plan; there is no fixed value to derive, so the resolver
    cannot and should not touch it.
  * Everything else must be EMPTY. `r6-fowler.c1` and `zc-consolidate.c1`
    (INTERROGATION.template.json, same phantom-placeholder shape) were the two
    real sites; both are now expressed purely in terms of `<work-id>` --
    `.agent-work/<work-id>/FOWLER_PASS.json` and
    `.agent-work/<work-id>/INTERROGATION_RECORD.json` -- so they resolve with
    the very same substitution every other `<work-id>` reference in these
    templates already gets, with nothing left for an agent to invent.

A future author who ships a new phantom placeholder, or drops one of these two
off the allowlist without fixing it, turns this test red.

The allowlist is scoped by SITE -- `(template file, task id, condition id)` --
not by the token's spelling alone. A round-2 cold review built a synthetic
case: `<exact test command>` embedded in a different, genuinely broken gate
passed silently under a spelling-only allowlist, because nothing checked
*where* the token was permitted. `AllowlistBoundaryTests` below pins that
boundary the way `tests/test_mcp_adoption.py::_cli_only_verb_violations` pins
its own: a synthetic offender that must be caught, an innocent case that must
not be flagged, and the accepted sites named explicitly so the allowlist
cannot grow without a deliberate edit here.

`test_no_unresolved_token_survives_instantiation` also asserts how many
command checks it examined (`EXPECTED_COMMAND_CHECK_COUNT`). A loop that only
asserts `offenders == []` reads as a clean pass even if an extraction break --
a key rename, a shape change -- makes it examine zero checks and find zero
offenders.
"""

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT_WORK_AREA = ROOT / "scripts" / "init_work_area.py"

# The exact six-row "Template set" table in
# skills/workbench/references/checklist-engine.md -- the canonical list of
# shipped role templates, not an arbitrarily chosen subset.
TEMPLATES = [
    ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json",
    ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json",
    ROOT / "skills" / "interrogator" / "templates" / "INTERROGATION.template.json",
    ROOT / "skills" / "reviewer" / "templates" / "REVIEW_SURVEY.template.json",
    ROOT / "skills" / "implementer" / "templates" / "IMPLEMENTER_PLAN.template.json",
    ROOT / "skills" / "charter" / "templates" / "ENGINE_CONFIG.template.json",
]

TOKEN_RE = re.compile(r"<[^<>\n]{1,80}>")

# Intentional authoring-time fill-in slots: the authoring agent writes real,
# per-plan content here (there is no fixed value resolve_spine could derive),
# and each gate's own imperative instructs exactly that.
#
# Scoped by SITE -- (template file name, task id, condition id) -- not by the
# token's spelling. Matching on spelling alone lets `<exact test command>`
# planted in an unrelated, genuinely broken gate pass silently; scoping to the
# exact two sites that are supposed to carry it closes that gap and pins the
# allowlist against silent growth (`AllowlistBoundaryTests` below asserts this
# dict's exact contents).
ALLOWED_SURVIVOR_SITES = {
    ("EXECUTE_PLAN.template.json", "g1-integrate", "c1"): "<exact test command>",
    ("IMPLEMENTER_PLAN.template.json", "m1", "c2"): "<exact test command>",
}

# How many command-kind pre/postconditions the six shipped templates carry
# today. A silent extraction break -- a key rename, a shape change in
# command_checks() -- would make the sweep below examine zero and find zero
# offenders, which reads as a clean pass. Asserting the count catches that.
# 13 -> 12 (#315/#568): the Commander spine's `init` precondition `c0` ran
# `verify_worktree_isolation.py --here` and was deleted when worktree isolation
# became engine-native (`checklist_engine.origin_worktree_refusal`). One fewer
# command check to examine; the tripwire is unchanged in strength.
EXPECTED_COMMAND_CHECK_COUNT = 12


def unresolved_offenders(template_name, resolved_commands):
    """Return one message per (site, token) where an unresolved bracket token
    survives instantiation and the site is not the token's allowlisted home."""
    offenders = []
    for tid, kind, cid, command in resolved_commands:
        for token in TOKEN_RE.findall(command):
            if ALLOWED_SURVIVOR_SITES.get((template_name, tid, cid)) == token:
                continue
            offenders.append(f"{template_name}::{tid}.{cid} ({kind}): {token!r} in {command!r}")
    return offenders


def load_resolve_spine():
    spec = importlib.util.spec_from_file_location("init_work_area", INIT_WORK_AREA)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve_spine


def command_checks(data):
    """Yield (task_id, cond_kind, cond_id, command) for every command-kind
    pre/postcondition across every task in a checklist template."""
    for tid, task in data.get("tasks", {}).items():
        for kind in ("preconditions", "postconditions"):
            for cond in task.get(kind, []) or []:
                check = cond.get("check")
                if isinstance(check, dict) and check.get("kind") == "command":
                    yield tid, kind, cond["id"], check.get("command", "")


class ShippedCheckCommandsResolveTests(unittest.TestCase):
    def setUp(self):
        self.resolve_spine = load_resolve_spine()

    def _resolved_commands(self, template_path):
        raw = template_path.read_text(encoding="utf-8")
        resolved_text = self.resolve_spine(raw, work_id="w-scratch", skill_dir=None, root=ROOT)
        data = json.loads(resolved_text)
        return list(command_checks(data))

    def test_templates_exist(self):
        for path in TEMPLATES:
            self.assertTrue(path.is_file(), f"missing shipped template: {path}")

    def test_no_unresolved_token_survives_instantiation(self):
        offenders = []
        examined = 0
        for path in TEMPLATES:
            resolved = self._resolved_commands(path)
            examined += len(resolved)
            offenders.extend(unresolved_offenders(path.name, resolved))
        self.assertEqual(
            examined, EXPECTED_COMMAND_CHECK_COUNT,
            f"expected to examine {EXPECTED_COMMAND_CHECK_COUNT} command-kind checks across "
            f"the six shipped templates, examined {examined} -- either a template gained/lost "
            f"a command check (update EXPECTED_COMMAND_CHECK_COUNT) or the extraction broke "
            f"(command_checks() silently found fewer/more than it should)",
        )
        self.assertEqual(
            offenders, [],
            "shipped command check(s) still carry an unresolved, non-allowlisted "
            "placeholder after instantiation:\n" + "\n".join(offenders),
        )

    def test_fowler_pass_record_path_resolves_from_work_id_alone(self):
        data = json.loads(
            (ROOT / "skills" / "reviewer" / "templates" / "REVIEW_SURVEY.template.json")
            .read_text(encoding="utf-8")
        )
        c1 = next(c for c in data["tasks"]["r6-fowler"]["postconditions"] if c["id"] == "c1")
        command = c1["check"]["command"]
        self.assertIn("<work-id>", command)
        self.assertNotIn("fowler-pass-record-path", command)

    def test_interrogation_record_path_resolves_from_work_id_alone(self):
        data = json.loads(
            (ROOT / "skills" / "interrogator" / "templates" / "INTERROGATION.template.json")
            .read_text(encoding="utf-8")
        )
        c1 = next(c for c in data["tasks"]["zc-consolidate"]["postconditions"] if c["id"] == "c1")
        command = c1["check"]["command"]
        self.assertIn("<work-id>", command)
        self.assertNotIn("interrogation-record-path", command)


class AllowlistBoundaryTests(unittest.TestCase):
    """Pins the false-positive / false-negative boundary of
    `unresolved_offenders`, the same three-way shape
    `tests/test_mcp_adoption.py::_cli_only_verb_violations` pins its own with:
    a synthetic offender that must be caught, an innocent case that must not
    be flagged, and the accepted exceptions named explicitly."""

    # A synthetic offender: `<exact test command>` (or any other unresolved
    # token) at a site NOT in ALLOWED_SURVIVOR_SITES. Proves the detector
    # fires on a real offender instead of accepting the token everywhere it
    # appears -- the gap the round-2 cold review found.
    VIOLATING = {
        "the allowlisted token planted in a different, unrelated gate":
            ("EXECUTE_PLAN.template.json", "g9-bogus", "c1", "<exact test command>"),
        "an ordinary unresolved token at an allowlisted site's neighbor":
            ("IMPLEMENTER_PLAN.template.json", "m1", "c1", "<work-id>"),
    }

    # The two real, accepted sites -- exactly what ships today.
    INNOCENT = {
        "the real EXECUTE_PLAN g1-integrate site":
            ("EXECUTE_PLAN.template.json", "g1-integrate", "c1", "<exact test command>"),
        "the real IMPLEMENTER_PLAN m1 site":
            ("IMPLEMENTER_PLAN.template.json", "m1", "c2", "<exact test command>"),
    }

    def test_a_violating_site_is_caught(self):
        for label, (template_name, tid, cid, command) in self.VIOLATING.items():
            found = unresolved_offenders(template_name, [(tid, "postconditions", cid, command)])
            self.assertTrue(
                found,
                f"{label!r} was not caught -- the allowlist accepted an unresolved token "
                f"outside its pinned site, which is the whole defect this boundary exists "
                f"to catch",
            )

    def test_an_innocent_site_is_left_alone(self):
        for label, (template_name, tid, cid, command) in self.INNOCENT.items():
            found = unresolved_offenders(template_name, [(tid, "postconditions", cid, command)])
            self.assertEqual(
                found, [],
                f"{label!r} was flagged, but it is the correct, accepted authoring-time slot "
                f"named in this file's own allowlist:\n" + "\n".join(found),
            )

    def test_the_allowlist_is_pinned_and_does_not_silently_grow(self):
        """Nothing else guards ALLOWED_SURVIVOR_SITES from growing -- a future
        edit that adds a third site changes this dict, and this equality is
        the thing that forces a deliberate look at that change."""
        self.assertEqual(
            ALLOWED_SURVIVOR_SITES,
            {
                ("EXECUTE_PLAN.template.json", "g1-integrate", "c1"): "<exact test command>",
                ("IMPLEMENTER_PLAN.template.json", "m1", "c2"): "<exact test command>",
            },
        )


if __name__ == "__main__":
    unittest.main()
