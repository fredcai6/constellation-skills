"""The overlay-freshness guard `scripts/check_template_overlay_freshness.py`
was written to catch exactly what `tests/test_cli_retirement_guard.py`'s own
docstring got wrong: it asserted "Each overlay file is byte-identical to its
`skills/` source and mirrored again under `.baseline/`, so a sweep must edit
all three copies" as settled fact, and nothing in the repo checked it. Measured
against this tree the claim is false for 8 files -- the overlay was seeded
2026-08-10 at `source_commit: 3697e12c`, and `skills/` has moved 591 commits
past that without the overlay following.

THIS SUITE HAS TWO JOBS, AND BOTH MATTER. The unit tests below prove the
predicate itself is right in BOTH directions -- a file that silently went
stale IS flagged, and a file someone deliberately customized is NOT -- using
constructed fixtures where the answer is chosen by this test, not measured. A
guard that can only ever fail is not evidence its logic is correct; a guard
that never fails is not evidence either, which is why the second half of this
suite runs `check()` against the REAL repo tree and expects it to be red.

`test_real_repo_overlay_has_no_stale_templates` is that second half, and it is
EXPECTED TO FAIL on this tree, on purpose. Read it as a red-proof, not a bug:
a passing version of this test would mean nothing, because "written on a
tree, immediately green" is indistinguishable from a check that does not
work. The failure names the exact 8 files a maintainer needs to refresh
(`scripts/check_skill_freshness.py --update-baseline`-shaped work, done
elsewhere, never by this file)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_template_overlay_freshness.py"
_spec = importlib.util.spec_from_file_location("check_template_overlay_freshness", SCRIPT)
CTOF = importlib.util.module_from_spec(_spec)
sys.modules["check_template_overlay_freshness"] = CTOF
_spec.loader.exec_module(CTOF)

REPO_ROOT = Path(__file__).resolve().parents[1]

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_repo(tmp_path: Path) -> Path:
    """A minimal repo shape: one skills/ source, one baseline mirror, one
    overlay file, all starting identical -- the up-to-date case a real,
    untouched overlay should be in most of the time."""
    repo = tmp_path / "repo"
    _write(repo / "skills" / "widget" / "templates" / "WIDGET.template.md", "v1 upstream\n")
    _write(
        repo / ".agent-work" / "templates" / ".baseline" / "constellation-widget" / "WIDGET.template.md",
        "v1 upstream\n",
    )
    _write(repo / ".agent-work" / "templates" / "WIDGET.template.md", "v1 upstream\n")
    return repo


class TestThePredicateItself:
    """The whole design of this guard is one three-way distinction. Each test
    below is a fixture built so ONLY that distinction decides the outcome --
    proof the predicate discriminates correctly, not just that it runs."""

    def test_all_three_copies_agreeing_is_ok_a_positive_control(self):
        """POSITIVE CONTROL: nothing has drifted and nothing was edited. This
        is the state a freshly seeded, untouched overlay is in, and it proves
        the guard does not cry wolf on the common case."""
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        rows = CTOF.check(repo)
        assert rows == [{
            "template": ".agent-work/templates/WIDGET.template.md",
            "status": "ok",
            "detail": "matches skills/widget/templates/WIDGET.template.md",
        }]

    def test_overlay_unchanged_while_skills_moved_on_is_stale(self):
        """The exact shape of the real defect: upstream (`skills/`) changed,
        nobody touched the overlay, so the overlay still equals the pristine
        `.baseline/` mirror. This MUST be flagged -- it is silent drift, and
        catching it on day one is this guard's entire reason to exist."""
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        _write(repo / "skills" / "widget" / "templates" / "WIDGET.template.md", "v2 upstream\n")
        # overlay and .baseline both still read "v1 upstream" -- untouched.

        rows = CTOF.check(repo)
        assert rows == [{
            "template": ".agent-work/templates/WIDGET.template.md",
            "status": "stale",
            "detail": (
                "differs from skills/widget/templates/WIDGET.template.md but still "
                "equals .agent-work/templates/.baseline/constellation-widget/"
                "WIDGET.template.md -- nobody edited the overlay, skills/ moved on "
                "underneath it"
            ),
        }]
        code = CTOF.main(["--repo-root", str(repo)])
        assert code == 1

    def test_project_edit_that_also_differs_from_skills_is_not_flagged(self):
        """POSITIVE CONTROL, the direction that makes this guard hard: a human
        deliberately customized the overlay copy. It now differs from
        `skills/` too -- by coincidence of timing, not because it is stale --
        and MUST NOT be flagged. A guard that cannot tell these apart would
        forbid the overlay from doing the one thing it exists to do."""
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        _write(repo / "skills" / "widget" / "templates" / "WIDGET.template.md", "v2 upstream\n")
        _write(
            repo / ".agent-work" / "templates" / "WIDGET.template.md",
            "v1 upstream, plus our team's local house rule\n",
        )
        # .baseline/ still reads "v1 upstream" -- the project edit is real,
        # deliberate, and differs from BOTH the new upstream and the old baseline.

        rows = CTOF.check(repo)
        assert rows == [{
            "template": ".agent-work/templates/WIDGET.template.md",
            "status": "project-edited",
            "detail": (
                "differs from both skills/widget/templates/WIDGET.template.md and "
                ".agent-work/templates/.baseline/constellation-widget/"
                "WIDGET.template.md -- a deliberate project edit, not drift"
            ),
        }]
        code = CTOF.main(["--repo-root", str(repo)])
        assert code == 0, "a project-edited file must never fail the guard"

    def test_no_skills_source_is_reported_not_crashed_on(self):
        """`DEFAULT.template.json` and `WORKFLOW_CLOSEOUT.template.md` in the
        real corpus have no live `skills/` counterpart at all (their last
        consumer, the pre-#639 `workbench` skill, was retired). This must
        surface as its own status, not raise and not silently vanish."""
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        _write(
            repo / ".agent-work" / "templates" / ".baseline" / "constellation-widget" / "ORPHAN.template.json",
            "{}\n",
        )
        _write(repo / ".agent-work" / "templates" / "ORPHAN.template.json", "{}\n")
        # No skills/**/templates/ORPHAN.template.json anywhere.

        rows = CTOF.check(repo)
        orphan_rows = [r for r in rows if r["template"].endswith("ORPHAN.template.json")]
        assert len(orphan_rows) == 1
        assert orphan_rows[0]["status"] == "no-skills-source"
        code = CTOF.main(["--repo-root", str(repo)])
        assert code == 0, "a file with no skills/ source must never fail the guard"

    def test_manifest_file_itself_is_excluded_from_the_walk(self):
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        _write(repo / ".agent-work" / "templates" / "TEMPLATES_MANIFEST.json", "{}\n")

        rows = CTOF.check(repo)
        assert all(r["template"] != ".agent-work/templates/TEMPLATES_MANIFEST.json" for r in rows), (
            "TEMPLATES_MANIFEST.json is the manifest, not a template -- it has no "
            "skills/ source and no baseline counterpart of its own, so walking it "
            "would either crash or misreport"
        )

    def test_basename_collision_under_skills_refuses_rather_than_guesses(self):
        """`_index_by_basename` is the seam this whole design leans on: two
        `skills/` templates sharing a name would make "find the file with this
        name" ambiguous, and picking one silently would make every row from
        that point on a coin flip. It must refuse instead."""
        import tempfile
        repo = _seed_repo(Path(tempfile.mkdtemp()))
        _write(repo / "skills" / "other" / "templates" / "WIDGET.template.md", "collision\n")

        with pytest.raises(CTOF.FreshnessError, match="collision"):
            CTOF.check(repo)

    def test_no_overlay_directory_is_clean(self):
        import tempfile
        repo = Path(tempfile.mkdtemp()) / "repo"
        repo.mkdir()
        assert CTOF.check(repo) == []
        assert CTOF.main(["--repo-root", str(repo)]) == 0


class TestTheRealRepoOverlay:
    """Non-synthetic: the guard run against this worktree's actual
    `.agent-work/templates/`, `skills/`, and `.baseline/`."""

    def test_the_real_walk_is_not_vacuous(self):
        """Floor test in the shape `check_role_spine_bookends.py`'s own suite
        uses: before trusting an absence assertion, prove the walk actually
        looked at something. A moved directory or an emptied glob would make
        every status below pass by finding nothing."""
        rows = CTOF.check(REPO_ROOT)
        assert len(rows) >= 50, (
            f"the real-repo walk found only {len(rows)} overlay templates -- it found "
            f"53 (51 manifest entries plus the .baseline dir itself is excluded, minus "
            f"TEMPLATES_MANIFEST.json) when this guard was written, so a count this low "
            f"means the walk narrowed and the stale-file assertion below is vacuous"
        )

    def test_real_repo_overlay_has_no_stale_templates(self):
        """The standing guard, and it was RED when it was written -- by the
        real corpus, not by a fixture this test chose. It named the 8 stale
        files the module docstring records; the overlay refresh landed in the
        same change and turned it green with no edit to this test.

        It is now the tripwire: the next time `skills/` moves and the overlay
        does not follow, this is what says so, on the day it starts rather
        than 591 commits later.

        A companion test pinning that historical set exactly was deleted with
        the refresh. Once the drift was fixed it could never assert anything
        again -- it skipped unconditionally, and a check that can only skip is
        not evidence. The measurement it carried is preserved where a reader
        will actually meet it: this module's docstring,
        `scripts/check_template_overlay_freshness.py`, and the corrected
        docstring in `tests/test_cli_retirement_guard.py`."""
        rows = CTOF.check(REPO_ROOT)
        stale = {Path(r["template"]).name for r in rows if r["status"] == "stale"}
        assert not stale, (
            f"{len(stale)} overlay template(s) are stale (differ from their skills/ "
            f"source but still equal .baseline/, meaning nobody edited them -- skills/ "
            f"just moved on): {sorted(stale)}. Refresh with "
            f"`scripts/check_skill_freshness.py --update-baseline`-shaped work; do not "
            f"hand-edit .agent-work/templates/."
        )

    def test_default_and_workflow_closeout_are_the_known_no_skills_source_files(self):
        """What is left of the six files #639 displaced when it retired
        `workbench` as an installable skill. Pinned so a future reader does not
        mistake a `no-skills-source` row for a bug in this script.

        Four of the six landed in `skills/_shared/`: `checklist-engine.md` and
        `status-model.md` as references, `STATE_NOTE` and
        `CONSTELLATION_FEEDBACK` as templates. `WORKFLOW_CLOSEOUT.template.md`
        joined them there in the same change as this pin -- it was homeless but
        LIVE, cited by `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` as the artifact
        that confirms the lesson apply-or-defer gate passed.

        `DEFAULT.template.json` is the last one, and it stays here deliberately
        rather than being given a home. #639 retired it ON PURPOSE as unused --
        `tests/test_validate_spine.py` records that decision by pinning the
        shipped-template count at 11, lowered from 12 for exactly this file,
        with the reason "one doc citation, no driver". Giving it a
        `skills/_shared/templates/` home would resurrect a template nothing
        drives and silently reverse that ruling. The coherent finish is to
        complete the retirement -- drop it from the overlay, the baseline and
        `TEMPLATES_MANIFEST.json` -- which is a deletion nobody has authorized,
        so this row stands as the visible reminder that #639 stopped halfway."""
        rows = CTOF.check(REPO_ROOT)
        no_source = {Path(r["template"]).name for r in rows if r["status"] == "no-skills-source"}
        assert no_source == {"DEFAULT.template.json"}, (
            f"the no-skills-source set changed to {sorted(no_source)} -- either a template "
            f"gained/lost a skills/ home, or the resolution logic broke"
        )
