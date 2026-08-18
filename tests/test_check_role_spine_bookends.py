"""#567 lane L: the role-spine-template bookend lint.

Mitigation for form B's silent-permissive failure -- a role spine template
that declares no bookends at all, or whose repo declaration has drifted from
what is actually installed (the shape `init_work_area.py` mints spines from).
Scoped to role spine templates (`*_SPINE.template.json`) only; does not touch
`checklist_engine.py::_is_bookend()` or its permissive default."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_role_spine_bookends.py"
_spec = importlib.util.spec_from_file_location("check_role_spine_bookends", SCRIPT)
CRSB = importlib.util.module_from_spec(_spec)
sys.modules["check_role_spine_bookends"] = CRSB
_spec.loader.exec_module(CRSB)


def _spine(items: list[str], bookend_ids: set[str]) -> dict:
    return {
        "items": items,
        "tasks": {
            tid: {"id": tid, "bookend": True} if tid in bookend_ids else {"id": tid}
            for tid in items
        },
    }


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class RoleSpineBookendLintTests(unittest.TestCase):
    def _roots(self, tmp: str) -> tuple[Path, Path]:
        repo_root = Path(tmp) / "repo"
        skills_root = Path(tmp) / "installed"
        repo_root.mkdir()
        skills_root.mkdir()
        return repo_root, skills_root

    def test_undeclared_template_is_a_red_proof(self):
        """A role spine template with zero declared bookends fails -- the
        exact shape lane K left behind before this lint existed."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            template = repo_root / "skills" / "widget" / "templates" / "WIDGET_SPINE.template.json"
            _write(template, _spine(["init", "middle", "archive"], set()))
            # Installed copy also undeclared -- undeclared is checked before drift.
            _write(
                skills_root / "constellation-widget" / "templates" / "WIDGET_SPINE.template.json",
                _spine(["init", "middle", "archive"], set()),
            )

            rows = CRSB.check(repo_root, skills_root)
            self.assertEqual(1, len(rows))
            self.assertEqual("undeclared", rows[0]["status"])

            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(1, code)

    def test_declared_and_matching_installed_copy_is_a_green_proof(self):
        """A role spine template that declares bookends, with the installed
        corpus copy carrying the identical set, passes clean."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            payload = _spine(["init", "middle", "archive"], {"init", "archive"})
            template = repo_root / "skills" / "widget" / "templates" / "WIDGET_SPINE.template.json"
            _write(template, payload)
            _write(
                skills_root / "constellation-widget" / "templates" / "WIDGET_SPINE.template.json",
                payload,
            )

            rows = CRSB.check(repo_root, skills_root)
            self.assertEqual(1, len(rows))
            self.assertEqual("ok", rows[0]["status"])

            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(0, code)

    def test_drift_between_repo_and_installed_declarations_fails(self):
        """Exactly the corpus state the Admiral hit minutes after merging K:
        repo declares bookends, the installed copy does not (or declares a
        different set) because the corpus has not been reinstalled yet."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            template = repo_root / "skills" / "widget" / "templates" / "WIDGET_SPINE.template.json"
            _write(template, _spine(["init", "middle", "archive"], {"init", "archive"}))
            _write(
                skills_root / "constellation-widget" / "templates" / "WIDGET_SPINE.template.json",
                _spine(["init", "middle", "archive"], set()),
            )

            rows = CRSB.check(repo_root, skills_root)
            self.assertEqual(1, len(rows))
            self.assertEqual("drift", rows[0]["status"])

            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(1, code)

    def test_installed_copy_entirely_absent_is_the_worst_case_of_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            template = repo_root / "skills" / "widget" / "templates" / "WIDGET_SPINE.template.json"
            _write(template, _spine(["init", "middle", "archive"], {"init", "archive"}))
            # No installed copy written at all.

            rows = CRSB.check(repo_root, skills_root)
            self.assertEqual(1, len(rows))
            self.assertEqual("installed-missing", rows[0]["status"])

            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(1, code)

    def test_no_role_spine_templates_found_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            (repo_root / "skills").mkdir()
            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(0, code)

    def test_unreadable_template_refuses_rather_than_silently_passing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, skills_root = self._roots(tmp)
            template = repo_root / "skills" / "widget" / "templates" / "WIDGET_SPINE.template.json"
            template.parent.mkdir(parents=True)
            template.write_text("{not valid json", encoding="utf-8")

            code = CRSB.main(["--repo-root", str(repo_root), "--skills-root", str(skills_root)])
            self.assertEqual(2, code)

    def test_real_repo_role_spine_templates_all_declare_at_least_one_bookend(self):
        """Non-synthetic sanity check against this repo's own three role
        spine templates (commander, admiral, explorer as of #567) -- each
        must declare >=1 bookend regardless of installed-corpus drift, which
        this assertion deliberately does not check (that depends on whether
        the corpus has been reinstalled, which this test suite does not
        control)."""
        repo_root = Path(__file__).resolve().parents[1]
        templates = sorted(repo_root.glob("skills/*/templates/*_SPINE.template.json"))
        self.assertGreaterEqual(len(templates), 1)
        for template in templates:
            bookends = CRSB._bookend_ids(CRSB._load_tasks(template))
            self.assertTrue(bookends, f"{template} declares zero bookend tasks")


if __name__ == "__main__":
    unittest.main()
