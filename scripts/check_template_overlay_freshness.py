#!/usr/bin/env python
"""Guard: a project's `.agent-work/templates/` overlay must never be STALE.

Written against a false claim caught in `tests/test_cli_retirement_guard.py`'s
own docstring: "Each overlay file is byte-identical to its `skills/` source and
mirrored again under `.baseline/`, so a sweep must edit all three copies."
Measured on this tree the day that claim was checked: 8 of the overlay's files
disagree with their `skills/` source --
`ADMIRAL_SPINE.template.json`, `CHARTER.template.json`,
`COMMANDER_SPINE.template.json`, `EXPLORER_SPINE.template.json`,
`AGENT_GUIDE.template.md`, `AGENTS.pointer.template.md`,
`CLAUDE.pointer.template.md`, `ORCHESTRATOR_CONTEXT.template.md` -- and nothing
in the repo computed that. The overlay was seeded 2026-08-10 at
`source_commit: 3697e12c`; the tree it was measured against was 591 commits
past that. This script is the check that would have caught the drift on the
day it started, instead of 591 commits later.

WHY "OVERLAY != skills/" IS NOT THE CHECK. The overlay at `.agent-work/templates/`
exists precisely so a project's own edits to a template survive reinstall --
`README.md`'s rule is "agents prefer `.agent-work/templates/<name>` and fall
back to bundled `templates/<name>`", and the installer deliberately never
clobbers it (`scripts/install_constellation.py`, project-scope install path).
A guard asserting "overlay must equal `skills/`" would forbid the very
customization the overlay is for, and the first legitimate project edit would
either break the guard or force it to be silenced -- the same decay this
repo's own `check_role_spine_bookends.py` and `test_cli_retirement_guard.py`
docstrings warn against for a hand-maintained exception list.

THE THIRD COPY IS WHAT MAKES THE DISTINCTION COMPUTABLE.
`docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (~L301-304, ~L393) is explicit that the
pristine mirror at `.agent-work/templates/.baseline/` exists so "two diffs are
always computable": what the PROJECT changed (overlay vs. baseline), and what
UPSTREAM changed (skills/ vs. baseline). This script computes both and reduces
them to the one distinction that matters for a drift guard:

  overlay == skills/        -> up to date, nothing to say.
  overlay != skills/
    and overlay == baseline -> STALE. Nobody edited the overlay; the file just
                                sat still while `skills/` moved on underneath
                                it. This is drift, and it is what this script
                                flags.
    and overlay != baseline -> PROJECT-EDITED. Someone deliberately changed
                                the overlay copy since it was seeded, and it
                                no longer matches either the pristine mirror
                                OR upstream by coincidence. Flagging this would
                                punish the overlay for doing its job, so this
                                script never does.

This is `check_skill_freshness.py`'s three-way status collapsed to the one
axis that matters here (its `upstream-changed` == this script's `stale` when
the project side hasn't touched the file; its `project-customized` and
`both-changed` are both `project-edited` here, because a script whose only
job is "flag the overlay" has no business also grading the QUALITY of a human
edit). It is not reused directly: `check_skill_freshness.py` needs an
installed `constellation-*` skills root and drives off a project's own
`TEMPLATES_MANIFEST.json` entries paired against that install. This repo IS
the skill source -- there is no external install to point it at, and its
`skills/<role>/templates/<name>` layout has no `constellation-` prefix -- so
the same reasoning `check_role_spine_bookends.py`'s docstring gives for not
reusing `check_skill_freshness.py` applies again here: the shape does not fit,
so this is a small standalone rather than a forced reuse.

RESOLUTION IS BY BASENAME, NOT BY THE MANIFEST'S SKILL FIELD, AND THAT IS
DELIBERATE. The overlay is FLAT (`.agent-work/templates/<name>`); the baseline
is PER-SKILL (`.agent-work/templates/.baseline/constellation-<role>/<name>`);
and `skills/` is also per-skill but WITHOUT the `constellation-` prefix, plus
one shared bucket, `skills/_shared/templates/`, that several roles bundle from
(issue #639 moved `CONSTELLATION_FEEDBACK.template.md` and
`STATE_NOTE.template.md` there; `TEMPLATES_MANIFEST.json` still files both
under `constellation-workbench`, the pre-#639 name, because the manifest
records where a template was BUNDLED, not where its source now lives).
Reproducing the installer's full bundle-resolution tables here to turn a
manifest "skill" field into today's true source directory would be a second,
drifting copy of `scripts/install_constellation.py`'s own
`SKILL_TEMPLATE_BUNDLES`/`ENGINE_BUNDLE_ROOTS` machinery. Basename lookup does
not need that table: every template name is unique across the whole
`skills/*/templates/` + `skills/_shared/templates/` tree (`_assert_unique`
below refuses rather than guess if that ever stops being true), and unique
across the whole `.baseline/*/**` tree the same way. So "find the file with
this name" is the correct answer independent of which bucket produced it, and
does not go stale itself if a future issue moves a template between buckets
again.

TWO OVERLAY FILES HAVE NO `skills/` SOURCE TO COMPARE AGAINST AT ALL:
`DEFAULT.template.json` and `WORKFLOW_CLOSEOUT.template.md`. Both were part of
`constellation-workbench` when the overlay was seeded, and #639 retired
`workbench` as an installable skill (see `install_constellation.py`'s
`LEGACY_ENGINE_HOME_INSTALL_NAME`/`ENGINE_BUNDLE_INSTALL_NAME` doctrine)
without giving either template a new home under `skills/`. `.baseline/` still
carries both (it was mirrored before the retirement), so the overlay-vs-baseline
half of the comparison is answerable, but the skills/-vs-baseline half is not:
there is no live upstream to have drifted from. Reported as `no-skills-source`,
not silently skipped and not crashed on -- an author retiring the last
consumer of a shared template should see that this script noticed, not get a
stack trace. `TEMPLATES_MANIFEST.json` itself is excluded from the walk
entirely (not even as `no-skills-source`): it is the manifest, not a template.

Exit codes:
  0  every overlay file is up to date, project-edited, or has no skills/ source
  1  at least one overlay file is STALE (report printed)
  2  REFUSED -- a file could not be read, or basenames collided where the
     comparison assumes they cannot
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


class FreshnessError(Exception):
    pass


def _index_by_basename(paths: list[Path], what: str) -> dict[str, Path]:
    """basename -> path, refusing rather than silently picking one on a
    collision. The whole basename-lookup design in the module docstring rests
    on this being injective; a collision means that premise broke and every
    row this script prints from that point on would be a guess."""
    index: dict[str, Path] = {}
    collided: dict[str, list[Path]] = {}
    for path in paths:
        if path.name in index:
            collided.setdefault(path.name, [index[path.name]]).append(path)
        else:
            index[path.name] = path
    if collided:
        detail = "; ".join(
            f"{name}: {[str(p) for p in ps]}" for name, ps in sorted(collided.items())
        )
        raise FreshnessError(
            f"{what} has {len(collided)} basename collision(s), so basename lookup "
            f"can no longer address a unique file -- {detail}"
        )
    return index


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FreshnessError(f"{path}: cannot read -- {exc}") from exc


def check(repo_root: Path) -> list[dict[str, str]]:
    """One row per file directly under `.agent-work/templates/` (excluding the
    `.baseline/` directory and `TEMPLATES_MANIFEST.json`). `status` is one of
    'ok', 'stale', 'project-edited', 'no-skills-source'."""
    overlay_dir = repo_root / ".agent-work" / "templates"
    baseline_dir = overlay_dir / ".baseline"
    skills_dir = repo_root / "skills"

    if not overlay_dir.is_dir():
        return []

    skills_sources = _index_by_basename(
        [p for p in skills_dir.glob("*/templates/*") if p.is_file()],
        "skills/*/templates/ (including skills/_shared/templates/)",
    )
    baseline_files = _index_by_basename(
        [p for p in baseline_dir.glob("*/*") if p.is_file()] if baseline_dir.is_dir() else [],
        ".agent-work/templates/.baseline/*/",
    )

    rows: list[dict[str, str]] = []
    for overlay_file in sorted(overlay_dir.iterdir()):
        if overlay_file.is_dir():
            continue
        if overlay_file.name == "TEMPLATES_MANIFEST.json":
            continue

        rel = overlay_file.relative_to(repo_root).as_posix()
        overlay_text = _read(overlay_file)

        skills_source = skills_sources.get(overlay_file.name)
        if skills_source is None:
            rows.append({
                "template": rel,
                "status": "no-skills-source",
                "detail": "no file named this under skills/*/templates/ or "
                          "skills/_shared/templates/ -- nothing to compare against",
            })
            continue

        baseline_file = baseline_files.get(overlay_file.name)
        if baseline_file is None:
            rows.append({
                "template": rel,
                "status": "no-baseline",
                "detail": f"no file named this under {baseline_dir.relative_to(repo_root)}/*/ "
                          f"-- cannot tell stale from project-edited without it",
            })
            continue

        skills_text = _read(skills_source)
        baseline_text = _read(baseline_file)

        if overlay_text == skills_text:
            status, detail = "ok", f"matches {skills_source.relative_to(repo_root)}"
        elif overlay_text == baseline_text:
            status, detail = "stale", (
                f"differs from {skills_source.relative_to(repo_root)} but still equals "
                f"{baseline_file.relative_to(repo_root)} -- nobody edited the overlay, "
                f"skills/ moved on underneath it"
            )
        else:
            status, detail = "project-edited", (
                f"differs from both {skills_source.relative_to(repo_root)} and "
                f"{baseline_file.relative_to(repo_root)} -- a deliberate project edit, "
                f"not drift"
            )
        rows.append({"template": rel, "status": status, "detail": detail})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    try:
        rows = check(args.repo_root.resolve())
    except FreshnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print("no .agent-work/templates/ overlay found -- nothing to check")
        return 0

    stale = [row for row in rows if row["status"] == "stale"]
    for row in rows:
        marker = "!" if row["status"] == "stale" else " "
        print(f"{marker} {row['status']:<18} {row['template']} -- {row['detail']}")

    if stale:
        print(
            f"\n{len(stale)} overlay template(s) are stale: they no longer match their "
            f"skills/ source but were never edited (they still equal .baseline/). "
            f"Refresh them from skills/ and promote a new baseline; do not hand-edit."
        )
        return 1
    print(f"\nall {len(rows)} overlay template(s) checked -- none stale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
