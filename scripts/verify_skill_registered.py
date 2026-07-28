#!/usr/bin/env python
"""Refuse a mechanically-broken or unregistered skill — the constellation-write-a-skill RAIL.

This is the single mechanically-enforced rail for the `constellation-write-a-skill`
skill (DESIGN_SPEC Section C). A minted skill must clear it before it is accepted.
The rail COMPOSES the corpus tooling rather than re-implementing it:

  1. MECHANICALLY BROKEN — re-uses `curate_corpus.py`'s mechanical checks and
     refuses on the *gating* subset (unparseable SKILL.md; no when-to-use marker;
     a confusable-pair skill with no exclusion clause; a missing/invalid invoker
     tag). Soft budgets curate also measures (size, description length, reference
     TOCs, duplication) stay ADVISORY here — they never refuse a mint. Semantic
     goodness (completion-criteria sharpness, the no-op test, negative space, ...)
     is DELIBERATELY not gated: that is the independent reviewer's judgment. The
     rail proves the skill installs and is registered, never that it is *good*.

  2. UNREGISTERED DEAD SEAM — the one property `curate_corpus.py` cannot see. A
     skill directory is auto-discovered, but the scripts and shared doctrine it
     needs are wired ONLY by its entries in `install_constellation.py`'s
     SKILL_REFERENCE_BUNDLES / SKILL_SCRIPT_BUNDLES. A skill missing from the
     reference bundle installs with NO doctrine — a dead seam that looks fine on
     disk. This missing-bundle-registration case is the exact failure mode the
     rail guards (DESIGN_SPEC Section C / x6-anatomy).

The `main` CLI additionally runs `install --dry-run` over the real corpus as the
installability half of the check. Standard library only.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Resolve the sibling corpus tools whether run as a script (its dir is already
# sys.path[0]) or imported by a test loader (which does not add scripts/ to the
# path). Both are bundled side-by-side into the installed skill's scripts/ dir.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curate_corpus  # noqa: E402
import install_constellation  # noqa: E402

# The curate checks whose FLAGGED status is a MINT-BLOCKING defect (a skill that
# is mechanically broken), as opposed to a soft budget that only shortlists for a
# curator's eye. These mirror curate_corpus' own check names.
GATING_CHECKS = frozenset({
    "parse",                    # SKILL.md does not parse
    "description",              # no description field
    "description-when-to-use",  # no "Use when ..." trigger marker
    "description-exclusion",    # confusable-pair skill with no exclusion clause
    "invoker",                  # missing or invalid invoker tag
})


class SkillRegistrationError(Exception):
    """Raised when a minted skill is mechanically broken or unregistered — the rail's refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SkillRegistrationError(message)


def _gating_findings(skill: str, root: Path) -> list[str]:
    """Run curate's mechanical checks over `root` and return the details of every
    FLAGGED finding for `skill` that falls in the mint-blocking GATING subset."""
    details: list[str] = []
    for finding in curate_corpus.curate(root):
        if finding.skill != skill:
            continue
        if finding.status == curate_corpus.STATUS_FLAGGED and finding.check in GATING_CHECKS:
            details.append(f"{finding.check}: {finding.detail}")
    return details


def verify_skill_registered(
    skill: str,
    root: Path | str = "skills",
    *,
    reference_bundles: dict | None = None,
    script_bundles: dict | None = None,
) -> None:
    """Raise SkillRegistrationError if `skill` (a source directory name under
    `root`) is mechanically broken or unregistered; return None if it is clean.

    `reference_bundles` / `script_bundles` default to the live registration maps
    in install_constellation; tests inject their own to exercise the gate.
    """
    root = Path(root)
    reference_bundles = (
        install_constellation.SKILL_REFERENCE_BUNDLES
        if reference_bundles is None else reference_bundles
    )
    script_bundles = (
        install_constellation.SKILL_SCRIPT_BUNDLES
        if script_bundles is None else script_bundles
    )

    # 1. The skill exists on disk with a parseable SKILL.md.
    skill_md = root / skill / "SKILL.md"
    _require(skill_md.is_file(), f"no SKILL.md for skill {skill!r} under {root}")

    # 2. Registration — the dead-seam gate. Every skill needs a doctrine
    #    reference bundle; without it the install wires no global doctrine at all.
    _require(
        skill in reference_bundles,
        f"skill {skill!r} is not registered in install_constellation.SKILL_REFERENCE_BUNDLES "
        f"— it would install as a dead seam (no doctrine). Register it before minting.",
    )

    # 2b. If the skill ships bundled scripts, every one must exist on disk (an
    #     entry naming a missing script is a broken registration). Resolution
    #     goes through the installer's OWN resolver, never a second hand-rolled
    #     `scripts/<name>` join: not every bundled script is flat in scripts/
    #     (SCRIPT_SOURCE_SUBDIRS), and a private copy of that lookup drifts into
    #     a FALSE refusal the moment one is not -- which is exactly what
    #     happened to `workbench` when the hook pair started shipping (#262).
    scripts_root = Path(install_constellation.REPO_ROOT) / "scripts"
    for script in script_bundles.get(skill, ()):
        source = install_constellation.script_source_path(script, scripts_root)
        _require(
            source.is_file(),
            f"skill {skill!r} registers script {script!r} that does not exist "
            f"(resolved to {source})",
        )

    # 3. Mechanically broken — the gating subset of curate_corpus.
    broken = _gating_findings(skill, root)
    _require(
        not broken,
        f"skill {skill!r} is mechanically broken (curate gating flags): " + "; ".join(broken),
    )


def _dry_run_installs(skill: str) -> None:
    """Installability half (CLI only): the real skill passes install --dry-run."""
    skills = install_constellation.discover_skills()
    selected = install_constellation.select_skills([skill], skills)
    # A junk target is fine — a dry run writes nothing.
    install_constellation.install_skills(
        selected, install_constellation.REPO_ROOT / ".dry-run-target",
        dry_run=True, force=False, full_set=False, restart_message="", out=lambda _: None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, help="the source directory name of the minted skill (e.g. write-a-skill)")
    parser.add_argument("--root", default="skills", help="the skills/ directory (default: skills)")
    args = parser.parse_args(argv)

    try:
        verify_skill_registered(args.skill, args.root)
        _dry_run_installs(args.skill)
    except (SkillRegistrationError, install_constellation.InstallError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    print(f"skill ok: {args.skill} is registered, mechanically clean, and installs (--dry-run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
