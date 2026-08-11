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
ALLOWED_SURVIVORS = {"<exact test command>"}


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
        for path in TEMPLATES:
            for tid, kind, cid, command in self._resolved_commands(path):
                for token in TOKEN_RE.findall(command):
                    if token not in ALLOWED_SURVIVORS:
                        offenders.append(f"{path.relative_to(ROOT)}::{tid}.{cid} ({kind}): {token!r} in {command!r}")
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


if __name__ == "__main__":
    unittest.main()
