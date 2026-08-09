#!/usr/bin/env python
"""Verify installed iterative-planning role artifacts without tracker/network I/O."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
# Mirrors install_constellation.CORPUS_MARKER: the file the installer writes into
# a skills root. Duplicated rather than imported because this script runs from an
# installed bundle, where the installer is not on the path.
CORPUS_MARKER = "CORPUS.json"
TRANSITION_LINE = re.compile(
    r"^\s*-\s+TRANSITION \| boundary=(?P<boundary>[^ |]+) "
    r"\| decision=(?P<decision>[^ |]+) \| verified\s*$"
)


class RoleArtifactError(Exception):
    """Raised when a role artifact cannot satisfy its installed public contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RoleArtifactError(message)


def _string(value: object, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{path} must be a nonempty string")
    assert isinstance(value, str)
    return value


def _read_json(path: Path, label: str) -> dict:
    _require(path.is_file(), f"{label} is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoleArtifactError(f"{label} is not readable JSON: {exc}") from exc
    _require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def _write_markdown(path: Path, text: str) -> None:
    _require(bool(text.strip()), f"rendered Markdown for {path.name} must be nonempty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.strip() + "\n")


def _is_skills_root(path: Path, exclude: Path | None = None) -> bool:
    """Whether ``path`` is a directory that installed constellation bundles live in.

    Decided by structure, never by name: either the installer's corpus marker
    (``install_constellation.py``'s ``CORPUS_MARKER``) sits in it, or it already
    holds at least one installed bundle -- a ``constellation-*`` child carrying
    its own ``SKILL.md``.

    ``exclude`` drops one child from the sibling scan. Without it, a candidate
    named ``constellation-*`` carrying its own ``SKILL.md`` is itself the child
    that makes its parent look like a skills root, so the two-clause test in
    ``_is_installed_bundle`` collapses back to the name test that caused #501.
    The probe passes no ``exclude``, so scope detection is unchanged.
    """
    if not path.is_dir():
        return False
    if (path / CORPUS_MARKER).is_file():
        return True
    skip = exclude.resolve() if exclude is not None else None
    return any(
        (child / "SKILL.md").is_file() and (skip is None or child.resolve() != skip)
        for child in path.glob("constellation-*")
    )


def _is_installed_bundle(path: Path) -> bool:
    """Whether ``path`` is an installed skill bundle rather than a source checkout.

    A bundle carries its own ``SKILL.md`` and sits inside a skills root. The
    source repo is itself named ``constellation-skills``, so a name test wrongly
    accepts it; it carries no top-level ``SKILL.md``, so this does not. A
    Commander worktree is not named ``constellation-*`` at all, so a name test
    wrongly refuses it; this reaches the same not-installed verdict without
    consulting the name.

    The parent must look like a skills root on the strength of some OTHER bundle
    (or the corpus marker), never on the strength of the candidate itself --
    otherwise a ``constellation-*`` name plus a ``SKILL.md`` is self-certifying.
    """
    return (path / "SKILL.md").is_file() and _is_skills_root(path.parent, exclude=path)


def _candidate_skills_roots() -> list[Path]:
    """The known install scopes, most specific first -- project scope before user
    scope, matching install_constellation.py's two --scope targets."""
    return [Path.cwd() / ".claude" / "skills", Path.home() / ".claude" / "skills"]


def _installed_skills_root(skills_root: str | Path | None = None) -> Path:
    """Where the installed constellation bundles live.

    Resolution order: an explicit ``--skills-root`` wins; else this script's own
    bundle, when it really is one; else the known install scopes, announced on
    stderr so a fallback is never silent; else refuse, naming every root tried.
    """
    if skills_root is not None:
        chosen = Path(skills_root).expanduser()
        _require(chosen.is_dir(), f"--skills-root is not a directory: {chosen}")
        return chosen

    bundle = Path(__file__).resolve().parents[1]
    if _is_installed_bundle(bundle):
        return bundle.parent

    tried = [bundle.parent]
    for candidate in _candidate_skills_roots():
        if _is_skills_root(candidate):
            print(
                f"note: this script is not inside an installed bundle ({bundle}); "
                f"resolved installed skills root {candidate}",
                file=sys.stderr,
            )
            return candidate
        tried.append(candidate)

    raise RoleArtifactError(
        "cannot locate an installed constellation skills root: this script is not inside an "
        f"installed skill bundle ({bundle}) and no known skills root was found -- pass "
        f"--skills-root <path> to name one explicitly. Roots tried ({len(tried)}): "
        + "; ".join(str(path) for path in tried)
    )


def _load_module(name: str, path: Path):
    _require(path.is_file(), f"installed public verifier is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None, f"cannot load installed verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _initial_verifier(skills_root: Path):
    return _load_module(
        "installed_verify_issue_set",
        skills_root / "constellation-to-initial-issues" / "scripts" / "verify_issue_set.py",
    )


def _replan_verifier(skills_root: Path):
    return _load_module(
        "installed_verify_replan",
        skills_root / "constellation-replan" / "scripts" / "verify_replan.py",
    )


def _work_area(work_id: str) -> Path:
    _string(work_id, "work-id")
    _require(bool(SAFE_ID.fullmatch(work_id)), "work-id contains unsafe path characters")
    return Path.cwd() / ".agent-work" / work_id


def verify_explorer(work_id: str, skills_root: str | Path | None = None) -> None:
    artifact = _read_json(_work_area(work_id) / "SHAPED_BRIEF.json", "Explorer SHAPED_BRIEF")
    verifier = _initial_verifier(_installed_skills_root(skills_root))
    try:
        verifier.verify_shaped_brief(artifact)
    except verifier.IssueSetError as exc:
        raise RoleArtifactError(f"Explorer SHAPED_BRIEF violates G1: {exc}") from exc


def verify_commander(work_id: str, skills_root: str | Path | None = None) -> None:
    artifact = _read_json(_work_area(work_id) / "REPLAN_INPUT.json", "Commander REPLAN_INPUT")
    verifier = _replan_verifier(_installed_skills_root(skills_root))
    try:
        verifier.verify_replan_input(artifact)
    except verifier.ReplanError as exc:
        raise RoleArtifactError(f"Commander REPLAN_INPUT violates G2: {exc}") from exc


def _next_wave(work_area: Path) -> dict:
    value = _read_json(work_area / "NEXT_WAVE.json", "Admiral NEXT_WAVE")
    required = {"boundary_id", "launch_id", "trigger"}
    _require(set(value) == required, "Admiral NEXT_WAVE must contain exactly boundary_id, launch_id, trigger")
    for field in ("boundary_id", "launch_id"):
        entry = _string(value[field], f"Admiral NEXT_WAVE.{field}")
        _require(bool(SAFE_ID.fullmatch(entry)), f"Admiral NEXT_WAVE.{field} contains unsafe path characters")
    _require(value["trigger"] in {"wave_boundary", "material_exception"}, "Admiral NEXT_WAVE.trigger is invalid")
    return value


def _verify_transition_audit(log_path: Path, boundary_id: str, decision: str) -> None:
    _require(log_path.is_file(), f"Admiral audit log is missing: {log_path}")
    matches = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        match = TRANSITION_LINE.fullmatch(line)
        if match and match.group("boundary") == boundary_id:
            matches.append(match.group("decision"))
    _require(len(matches) == 1, f"boundary {boundary_id!r} must have exactly one verified TRANSITION audit entry")
    _require(matches[0] == decision, "verified TRANSITION audit decision must match REPLAN_RESULT.decision")


def verify_admiral_prelaunch(work_id: str, skills_root: str | Path | None = None) -> None:
    work_area = _work_area(work_id)
    next_wave = _next_wave(work_area)
    boundary_id = next_wave["boundary_id"]
    transition = work_area / "transitions" / boundary_id
    source = _read_json(transition / "REPLAN_INPUT.json", "Admiral boundary REPLAN_INPUT")
    result = _read_json(transition / "REPLAN_RESULT.json", "Admiral boundary REPLAN_RESULT")
    verifier = _replan_verifier(_installed_skills_root(skills_root))
    try:
        verifier.verify_replan_result(source, result)
    except verifier.ReplanError as exc:
        raise RoleArtifactError(f"Admiral transition violates G2: {exc}") from exc
    _require(result["applicable"] is True, "inapplicable transition cannot authorize NEXT_WAVE")
    _require(
        result["decision"] in {"advance", "replan"},
        "only advance or replan may authorize NEXT_WAVE",
    )
    try:
        rendered = verifier.render_replan_markdown(source, result)
    except verifier.ReplanError as exc:
        raise RoleArtifactError(f"Admiral transition cannot render: {exc}") from exc
    _require(bool(rendered.strip()), "Admiral transition renderer returned empty Markdown")
    _verify_transition_audit(work_area / "ADMIRAL_LOG.md", boundary_id, result["decision"])
    _write_markdown(transition / "CURRENT_TRUTH.md", result["revised_epic_body"])
    _write_markdown(transition / "WAVE_REVIEW.md", result["wave_review_comment"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("explorer", "commander", "admiral-prelaunch"))
    parser.add_argument("--work-id", required=True)
    parser.add_argument(
        "--skills-root",
        default=None,
        help="directory the installed constellation bundles live in; wins over autodetection",
    )
    args = parser.parse_args(argv)
    try:
        if args.mode == "explorer":
            verify_explorer(args.work_id, args.skills_root)
        elif args.mode == "commander":
            verify_commander(args.work_id, args.skills_root)
        else:
            verify_admiral_prelaunch(args.work_id, args.skills_root)
    except (OSError, RoleArtifactError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"iterative role artifact ok: {args.mode} ({args.work_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
