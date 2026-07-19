#!/usr/bin/env python
"""Scaffold a Constellation work area: .agent-work/<work-id>/ and its subdirs.

Optionally instantiate spine.json from a named spine template, resolving the
commander placeholders so the result is immediately runnable by the engine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUBDIRS = ["crew-handoffs", "evidence", "triage-candidates"]

# Placeholder families the resolver owns: <work-id> plus role-specific
# "<role>-skill-dir" / "<role>-session-id" tokens (<commander-skill-dir>,
# <admiral-skill-dir>, ...; role names may themselves carry hyphens, e.g. a
# hypothetical <lessons-auditor-skill-dir>). A token in one of these families
# left unresolved in a materialized spine is always a resolver bug, never an
# intentional literal — unlike prose placeholders such as <engine>, <date>,
# <N>, <path>, which this script never resolves and are fine to survive.
_ROLE_SKILL_DIR_RE = re.compile(r"<([a-zA-Z0-9-]+)-skill-dir>")
_ROLE_SESSION_ID_RE = re.compile(r"<([a-zA-Z0-9-]+)-session-id>")
_RESOLVER_OWNED_TOKEN_RE = re.compile(
    r"<(work-id|[a-zA-Z0-9-]+-skill-dir|[a-zA-Z0-9-]+-session-id)>"
)


def _assert_no_resolver_placeholders(text: str) -> None:
    """Fail loudly if a resolver-owned placeholder survives resolution.

    This is the epic-101/epic-138 class of defect (#114, #154): a role's spine
    template introduces its own placeholder (e.g. ``<admiral-skill-dir>``,
    ``<admiral-session-id>``) that the resolver did not know how to substitute,
    and it is left literal inside an engine check-command string — the engine
    then refuses to ``advance`` many steps into a run, with a confusing
    "file not found" pointing at the literal placeholder, instead of failing
    here at instantiation where the cause is obvious.
    """
    leftover = sorted(set(_RESOLVER_OWNED_TOKEN_RE.findall(text)))
    if leftover:
        raise SystemExit(
            "spine.json still carries unresolved placeholder(s) after resolution: "
            + ", ".join(f"<{token}>" for token in leftover)
            + " -- add the token to resolve_spine rather than shipping a spine "
            "with a literal placeholder in a check command."
        )


def init_work_area(root: Path, work_id: str) -> Path:
    base = root / ".agent-work" / work_id
    for sub in [""] + SUBDIRS:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def _resolve_skill_dir_token(text: str, token: str, skill_dir: str | None, root: Path) -> str:
    """Resolve one ``<token>`` skill-dir placeholder in ``text``.

    - ``<token>`` -> ``skill_dir`` when given — but fail visibly when the
      template references ``<token>/scripts`` and ``skill_dir`` carries no
      ``scripts/`` directory (e.g. an explicit repo-relative ``skills/<name>``
      in the source repo, where bundled scripts live at ``<root>/scripts``):
      substituting it verbatim would write a spine whose command checks point
      at nonexistent script paths. When omitted, auto-detect the source-repo
      layout (bundled scripts at ``<root>/scripts``) and collapse the token
      form ``<token>/scripts`` -> ``scripts`` so the init command references
      the real top-level script path; any remaining bare token resolves to
      the repo root (``.``).
    """
    placeholder = f"<{token}>"
    if skill_dir is not None:
        scripts_ref = f"{placeholder}/scripts"
        if scripts_ref in text:
            candidate = Path(skill_dir)
            scripts_dir = (candidate if candidate.is_absolute() else root / candidate) / "scripts"
            if not scripts_dir.is_dir():
                raise SystemExit(
                    f"--skill-dir {skill_dir!r} carries no scripts/ directory ({scripts_dir}) "
                    f"but the template references {scripts_ref}. Omit --skill-dir in a source "
                    "repo with top-level bundled scripts (auto-detect), or pass the installed "
                    "skill directory, which carries scripts/."
                )
        return text.replace(placeholder, skill_dir)
    if (root / "scripts").is_dir():
        # Bundled scripts live at the repo top level; skill-dir == repo root.
        text = text.replace(f"{placeholder}/scripts", "scripts")
    # Any remaining bare token resolves to the repo root.
    return text.replace(placeholder, ".")


def resolve_spine(template_text: str, work_id: str, skill_dir: str | None, root: Path) -> str:
    """Resolve spine placeholders in a spine template's text.

    - Every role-specific ``<role-skill-dir>`` token present (``<commander-skill-dir>``,
      ``<admiral-skill-dir>``, and any future role's) resolves via
      ``_resolve_skill_dir_token`` from the same ``skill_dir``/``root`` inputs (see that
      helper), discovered by pattern rather than hardcoded per role so a new role's spine
      template does not recur this defect under a fresh token name (#114/#154). The
      generic ``<skill-dir>`` token resolves the same way; ``<commander-skill-dir>``
      behavior is unchanged (byte-identical) by this generalization.
    - Every role-specific ``<role-session-id>`` token (``<commander-session-id>``,
      ``<admiral-session-id>``, ...) -> ``<role>-<work-id>`` (the conventional default),
      likewise discovered by pattern.
    - ``<work-id>`` -> the work_id argument (all occurrences).
    """
    text = template_text
    for token in sorted({f"{role}-skill-dir" for role in _ROLE_SKILL_DIR_RE.findall(text)}):
        text = _resolve_skill_dir_token(text, token, skill_dir, root)
    text = _resolve_skill_dir_token(text, "skill-dir", skill_dir, root)
    for role in sorted(set(_ROLE_SESSION_ID_RE.findall(text))):
        text = text.replace(f"<{role}-session-id>", f"{role}-{work_id}")
    text = text.replace("<work-id>", work_id)
    return text


def instantiate_spine(
    root: Path,
    work_id: str,
    template: Path,
    skill_dir: str | None = None,
    force: bool = False,
) -> Path | None:
    """Write .agent-work/<work-id>/spine.json from ``template`` with placeholders resolved.

    Returns the written path, or ``None`` when an existing spine.json is left
    intact because ``force`` was not passed.
    """
    base = init_work_area(root, work_id)
    dest = base / "spine.json"
    if dest.exists() and not force:
        print(f"spine.json already exists (in-progress run state); pass --force to overwrite: {dest}")
        return None
    resolved = resolve_spine(template.read_text(encoding="utf-8"), work_id, skill_dir, root)
    # Fail visibly if resolution produced invalid JSON rather than writing a broken spine.
    json.loads(resolved)
    # Fail visibly if any resolver-owned placeholder survived resolution (#114/#154),
    # rather than writing a spine that will strand the engine on a literal placeholder
    # many steps into a run.
    _assert_no_resolver_placeholders(resolved)
    dest.write_text(resolved, encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".")
    parser.add_argument("--spine", help="path to a spine template to instantiate into spine.json")
    parser.add_argument("--skill-dir", dest="skill_dir", help="value for <commander-skill-dir> and <skill-dir> (auto-detected if omitted)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing spine.json")
    args = parser.parse_args(argv)
    root = Path(args.root)
    base = init_work_area(root, args.work_id)
    print(f"work area ready: {base}")
    if args.spine:
        dest = instantiate_spine(root, args.work_id, Path(args.spine), args.skill_dir, args.force)
        if dest is not None:
            print(f"spine ready: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
