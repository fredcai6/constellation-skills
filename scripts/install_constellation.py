from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "skills"


class InstallError(Exception):
    """Raised for clear, user-correctable installer failures."""


@dataclass(frozen=True)
class Skill:
    source_name: str
    install_name: str
    source_path: Path


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise InstallError(f"{skill_md} is missing YAML frontmatter")

    try:
        frontmatter = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise InstallError(f"{skill_md} has malformed YAML frontmatter") from exc

    values: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise InstallError(f"{skill_md} has malformed frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()

    for key in ("name", "description"):
        if not values.get(key):
            raise InstallError(f"{skill_md} frontmatter must include {key}")

    return values


def discover_skills(source_root: Path = SOURCE_ROOT) -> list[Skill]:
    if not source_root.exists():
        raise InstallError(f"source skill root does not exist: {source_root}")

    skills: list[Skill] = []
    for source_path in sorted(path for path in source_root.iterdir() if path.is_dir()):
        skill_md = source_path / "SKILL.md"
        if not skill_md.exists():
            raise InstallError(f"source skill is missing SKILL.md: {source_path}")
        metadata = parse_frontmatter(skill_md)
        skills.append(
            Skill(
                source_name=source_path.name,
                install_name=metadata["name"],
                source_path=source_path,
            )
        )

    if not skills:
        raise InstallError(f"no skills found in {source_root}")
    return skills


def select_skills(requested: Sequence[str] | None, available: Iterable[Skill]) -> list[Skill]:
    skills = list(available)
    if requested is None:
        return skills

    index: dict[str, Skill] = {}
    for skill in skills:
        index[skill.source_name] = skill
        index[skill.install_name] = skill

    selected: list[Skill] = []
    seen: set[str] = set()
    unknown: list[str] = []
    for name in requested:
        skill = index.get(name)
        if skill is None:
            unknown.append(name)
            continue
        if skill.install_name not in seen:
            selected.append(skill)
            seen.add(skill.install_name)

    if unknown:
        valid = ", ".join(sorted(index))
        raise InstallError(f"unknown skill(s): {', '.join(unknown)}. Valid names: {valid}")
    return selected


def default_user_target(env: Mapping[str, str]) -> Path:
    codex_home = env.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


def resolve_target_root(args: argparse.Namespace, env: Mapping[str, str], cwd: Path) -> Path:
    if args.scope == "user":
        if args.project is not None:
            raise InstallError("--project is only valid with --scope project")
        return args.dest.expanduser() if args.dest else default_user_target(env)

    if args.dest and args.project:
        raise InstallError("use --dest or --project, not both")

    if args.dest:
        return args.dest.expanduser()

    project = args.project.expanduser() if args.project else cwd
    if not project.exists() or not project.is_dir():
        raise InstallError(f"project directory does not exist: {project}")
    return project / ".codex" / "skills"


def ensure_target_is_inside_root(target_root: Path, target: Path) -> None:
    root = target_root.resolve()
    resolved_target = target.resolve()
    if resolved_target == root or root not in resolved_target.parents:
        raise InstallError(f"refusing to overwrite path outside target root: {target}")


def install_skills(
    skills: Sequence[Skill],
    target_root: Path,
    *,
    dry_run: bool,
    force: bool,
    out: Callable[[str], object],
) -> None:
    action = "DRY RUN: would install" if dry_run else "Installing"
    out(f"{action} {len(skills)} skill(s) into {target_root}")

    for skill in skills:
        target = target_root / skill.install_name
        out(f"- {skill.install_name}: {skill.source_path} -> {target}")

        if dry_run:
            continue

        if target.exists() and not force:
            raise InstallError(f"{target} already exists; rerun with --force to replace it")

        target_root.mkdir(parents=True, exist_ok=True)
        ensure_target_is_inside_root(target_root, target)

        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.copytree(skill.source_path, target)

    if not dry_run:
        out("Installed. Restart Codex to pick up new or updated skills.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Constellation skills at user or project scope.",
    )
    parser.add_argument("--scope", choices=("user", "project"), required=True)
    parser.add_argument(
        "--project",
        type=Path,
        help="Project directory for --scope project. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        help="Explicit skills directory. Overrides the default target for the selected scope.",
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        help="Skill names to install. Accepts short names like charter or full names like constellation-charter.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the install plan only.")
    parser.add_argument("--force", action="store_true", help="Replace existing installed skill folders.")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
    out: Callable[[str], object] = print,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        runtime_env = os.environ if env is None else env
        runtime_cwd = Path.cwd() if cwd is None else cwd
        skills = select_skills(args.skills, discover_skills())
        target_root = resolve_target_root(args, runtime_env, runtime_cwd)
        install_skills(skills, target_root, dry_run=args.dry_run, force=args.force, out=out)
    except InstallError as exc:
        parser.exit(2, f"error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
