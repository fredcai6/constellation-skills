from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date
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
    required_scripts: tuple[str, ...]


@dataclass(frozen=True)
class AgentTarget:
    name: str
    user_env_var: str | None
    user_config_dir: str
    project_config_dir: str
    restart_message: str


AGENT_TARGETS: dict[str, AgentTarget] = {
    "claude": AgentTarget(
        name="Claude Code",
        user_env_var=None,
        user_config_dir=".claude",
        project_config_dir=".claude",
        restart_message=(
            "Installed. Claude Code picks up changes in existing skill directories during the current session; "
            "restart it if this created a top-level skills directory."
        ),
    ),
    "codex": AgentTarget(
        name="Codex",
        user_env_var="CODEX_HOME",
        user_config_dir=".codex",
        project_config_dir=".codex",
        restart_message="Installed. Restart Codex to pick up new or updated skills.",
    ),
    "cursor": AgentTarget(
        name="Cursor",
        user_env_var=None,
        user_config_dir=".cursor",
        project_config_dir=".cursor",
        restart_message="Installed. Restart Cursor if the new or updated skills are not listed.",
    ),
    "gemini": AgentTarget(
        name="Gemini CLI",
        user_env_var=None,
        user_config_dir=".gemini",
        project_config_dir=".gemini",
        restart_message="Installed. Restart Gemini CLI if the new or updated skills are not listed.",
    ),
}
AGENT_CHOICES = sorted((*AGENT_TARGETS, "all"))
SKILL_SCRIPT_BUNDLES: dict[str, tuple[str, ...]] = {
    "admiral": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "apply_lessons_delta.py"),
    "lessons-auditor": ("checklist_engine.py",),
    "charter": ("checklist_engine.py",),
    "commander": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "run_crew.py", "recover_crews.py", "apply_lessons_delta.py"),
    "workbench": ("checklist_engine.py",),
    "interrogator": ("checklist_engine.py",),
    "cartographer": ("checklist_engine.py", "build_architecture_map.py"),
    "implementer": ("checklist_engine.py",),
    "reviewer": ("checklist_engine.py",),
}
REWRITABLE_TEXT_SUFFIXES = {".json", ".md", ".txt"}


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise InstallError(f"{skill_md} is missing YAML frontmatter")

    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise InstallError(f"{skill_md} has malformed YAML frontmatter") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
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
                required_scripts=SKILL_SCRIPT_BUNDLES.get(source_path.name, ()),
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


def validate_required_scripts(skills: Iterable[Skill], scripts_root: Path = REPO_ROOT / "scripts") -> None:
    missing: list[str] = []
    for skill in skills:
        for script in skill.required_scripts:
            if not (scripts_root / script).is_file():
                missing.append(f"{skill.install_name}: {scripts_root / script}")
    if missing:
        raise InstallError(f"required script(s) missing: {'; '.join(missing)}")


def rewrite_installed_skill_paths(target: Path, skill: Skill) -> None:
    replacements = {
        "<skill-dir>": target.as_posix(),
        f"<{skill.source_name}-skill-dir>": target.as_posix(),
    }
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in REWRITABLE_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        rewritten = text
        for token, replacement in replacements.items():
            rewritten = rewritten.replace(token, replacement)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")


def home_from_env(env: Mapping[str, str]) -> Path:
    for key in ("HOME", "USERPROFILE"):
        value = env.get(key)
        if value:
            return Path(value).expanduser()
    return Path.home()


def default_user_target(agent: AgentTarget, env: Mapping[str, str]) -> Path:
    if agent.user_env_var:
        configured_home = env.get(agent.user_env_var)
        if configured_home:
            return Path(configured_home).expanduser() / "skills"
    return home_from_env(env) / agent.user_config_dir / "skills"


def resolve_target_root(
    args: argparse.Namespace,
    agent: AgentTarget,
    env: Mapping[str, str],
    cwd: Path,
) -> Path:
    if args.scope == "user":
        if args.project is not None:
            raise InstallError("--project is only valid with --scope project")
        return args.dest.expanduser() if args.dest else default_user_target(agent, env)

    if args.dest and args.project:
        raise InstallError("use --dest or --project, not both")

    if args.dest:
        return args.dest.expanduser()

    project = args.project.expanduser() if args.project else cwd
    if not project.exists() or not project.is_dir():
        raise InstallError(f"project directory does not exist: {project}")
    return project / agent.project_config_dir / "skills"


def resolve_target_roots(
    args: argparse.Namespace,
    env: Mapping[str, str],
    cwd: Path,
) -> list[tuple[AgentTarget, Path]]:
    if args.agent == "all":
        if args.dest:
            raise InstallError("--dest is only valid when installing for one --agent")
        return [
            (agent, resolve_target_root(args, agent, env, cwd))
            for agent in AGENT_TARGETS.values()
        ]

    agent = AGENT_TARGETS[args.agent]
    return [(agent, resolve_target_root(args, agent, env, cwd))]


def ensure_target_is_inside_root(target_root: Path, target: Path) -> None:
    root = target_root.resolve()
    resolved_target = target.resolve()
    if resolved_target == root or root not in resolved_target.parents:
        raise InstallError(f"refusing to overwrite path outside target root: {target}")


def remove_existing_constellation_set(target_root: Path) -> None:
    if not target_root.exists():
        return
    if not target_root.is_dir():
        raise InstallError(f"target root is not a directory: {target_root}")

    for target in target_root.iterdir():
        if not target.name.startswith("constellation-"):
            continue
        ensure_target_is_inside_root(target_root, target)
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()


def install_skills(
    skills: Sequence[Skill],
    target_root: Path,
    *,
    dry_run: bool,
    force: bool,
    restart_message: str,
    out: Callable[[str], object],
) -> None:
    action = "DRY RUN: would install" if dry_run else "Installing"
    out(f"{action} {len(skills)} skill(s) into {target_root}")

    if force and not dry_run:
        remove_existing_constellation_set(target_root)

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
        rewrite_installed_skill_paths(target, skill)
        for script in skill.required_scripts:
            script_target = target / "scripts" / script
            script_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / "scripts" / script, script_target)

    if not dry_run:
        out(restart_message)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def write_template_baselines(
    skills: Sequence[Skill],
    project_root: Path,
    *,
    out: Callable[[str], object],
) -> None:
    """Seed pristine blank-template baselines + manifest for a project install.

    The baseline is what three-way template reconciliation diffs against; the
    installer therefore never overwrites an existing baseline — upgrades are
    reconciled by check_skill_freshness.py, which owns baseline promotion.
    """
    templates_root = project_root / ".agent-work" / "templates"
    baseline_root = templates_root / ".baseline"
    manifest_path = templates_root / "TEMPLATES_MANIFEST.json"

    if baseline_root.exists() or manifest_path.exists():
        out(
            "Template baseline already exists; leaving it untouched. "
            "Run scripts/check_skill_freshness.py to reconcile against this install."
        )
        return

    entries: list[dict[str, str]] = []
    for skill in skills:
        source_templates = skill.source_path / "templates"
        if not source_templates.is_dir():
            continue
        for template in sorted(source_templates.iterdir()):
            if not template.is_file():
                continue
            target = baseline_root / skill.install_name / template.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, target)
            entries.append(
                {
                    "skill": skill.install_name,
                    "template": template.name,
                    "sha256": _hash_file(template),
                }
            )

    if not entries:
        return

    manifest = {
        "generated": date.today().isoformat(),
        "source_commit": _source_commit(),
        "baseline_origin": "baseline-from-install",
        "templates": entries,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    out(
        f"Template baseline seeded: {len(entries)} template(s) -> {baseline_root} "
        f"(manifest: {manifest_path})"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Constellation skills for supported agents at user or project scope.",
    )
    parser.add_argument("--agent", choices=AGENT_CHOICES, required=True)
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
        validate_required_scripts(skills)
        target_roots = resolve_target_roots(args, runtime_env, runtime_cwd)
        for agent, target_root in target_roots:
            out(f"{agent.name}:")
            install_skills(
                skills,
                target_root,
                dry_run=args.dry_run,
                force=args.force,
                restart_message=agent.restart_message,
                out=out,
            )
        if args.scope == "project" and not args.dry_run and not args.dest:
            project_root = args.project.expanduser() if args.project else runtime_cwd
            write_template_baselines(skills, project_root, out=out)
    except InstallError as exc:
        parser.exit(2, f"error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
