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
SHARED_REFERENCE_ROOT = SOURCE_ROOT / "_shared"


class InstallError(Exception):
    """Raised for clear, user-correctable installer failures."""


@dataclass(frozen=True)
class Skill:
    source_name: str
    install_name: str
    source_path: Path
    required_scripts: tuple[str, ...]
    required_references: tuple[str, ...]


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
    "admiral": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "apply_lessons_delta.py", "verify_lessons_applied.py", "verify_worktree_isolation.py", "agent_work_root.py"),
    "lessons-auditor": ("checklist_engine.py",),
    "charter": ("checklist_engine.py",),
    "commander": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "run_crew.py", "recover_crews.py", "apply_lessons_delta.py", "verify_lessons_applied.py", "verify_worktree_isolation.py", "agent_work_root.py"),
    "workbench": ("checklist_engine.py",),
    "interrogator": ("checklist_engine.py",),
    "cartographer": ("checklist_engine.py", "build_architecture_map.py"),
    "docent": ("docent_freshness.py",),
    "implementer": ("checklist_engine.py",),
    "reviewer": ("checklist_engine.py",),
    "explorer": ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py"),
}
# Global doctrine buckets (single source: skills/_shared/), bundled into each skill's
# references/ at install exactly as the scripts above are bundled into scripts/. The
# audience Venn is enforced by which buckets a skill carries: everyone-global is shared
# by all; the tier buckets reach only their tier. A role reads its own bucket(s) at the
# checklist context-read step; the project supplies thin local deltas under docs/agents/.
_GLOBAL_EVERYONE = ("global-everyone.md", "windows.md")
_GLOBAL_ORCHESTRATOR = ("global-everyone.md", "global-orchestrator.md", "windows.md")
_GLOBAL_CREW = ("global-everyone.md", "global-crew.md", "windows.md")
_GLOBAL_ALL_TIERS = ("global-everyone.md", "global-orchestrator.md", "global-crew.md", "windows.md")
SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {
    "admiral": _GLOBAL_ORCHESTRATOR,
    "lessons-auditor": _GLOBAL_EVERYONE,
    "charter": _GLOBAL_ALL_TIERS,  # the baseline Charter elicits project deltas from
    "commander": _GLOBAL_ORCHESTRATOR,
    "workbench": _GLOBAL_ALL_TIERS,  # generic driver for either tier
    "interrogator": _GLOBAL_EVERYONE,
    "cartographer": _GLOBAL_ORCHESTRATOR,
    "docent": _GLOBAL_ORCHESTRATOR,
    "scout": _GLOBAL_ORCHESTRATOR,
    "implementer": _GLOBAL_CREW,
    "reviewer": _GLOBAL_CREW,
    "triage": _GLOBAL_ORCHESTRATOR,
    "explorer": _GLOBAL_ORCHESTRATOR,
    "prototyper": _GLOBAL_CREW,
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
    for source_path in sorted(
        path
        for path in source_root.iterdir()
        if path.is_dir() and not path.name.startswith("_")  # _shared holds bundled refs, not a skill
    ):
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
                required_references=SKILL_REFERENCE_BUNDLES.get(source_path.name, ()),
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


def validate_required_references(
    skills: Iterable[Skill], shared_root: Path = SHARED_REFERENCE_ROOT
) -> None:
    missing: list[str] = []
    for skill in skills:
        for reference in skill.required_references:
            if not (shared_root / reference).is_file():
                missing.append(f"{skill.install_name}: {shared_root / reference}")
    if missing:
        raise InstallError(f"required reference(s) missing: {'; '.join(missing)}")


def _platform_interpreter() -> str:
    """Interpreter for installed command strings: the `py` launcher on Windows,
    `python3` elsewhere. Installed spine imperatives ship the literal `python <…>`
    prefix; rewriting it here spares Windows users the recurring `python`->`py`
    hand-patch (the source templates keep `python <…>` to preserve the authoring
    contract)."""
    return "py" if os.name == "nt" else "python3"


def rewrite_installed_skill_paths(target: Path, skill: Skill) -> None:
    # Rewrite the interpreter prefix FIRST, before the skill-dir tokens consume the
    # trailing `<`: the replacement preserves the `<` so `<…-skill-dir>` still resolves.
    replacements = {
        "python <": f"{_platform_interpreter()} <",
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
    full_set: bool,
    restart_message: str,
    out: Callable[[str], object],
) -> None:
    action = "DRY RUN: would install" if dry_run else "Installing"
    out(f"{action} {len(skills)} skill(s) into {target_root}")

    # Set-level wipe only when replacing the FULL set (clears orphaned
    # constellation-* dirs whose upstream skill no longer exists). A --skills
    # subset with --force replaces only the selected skills, via the
    # per-target removal below.
    if force and full_set and not dry_run:
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
        for reference in skill.required_references:
            reference_target = target / "references" / reference
            reference_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SHARED_REFERENCE_ROOT / reference, reference_target)

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
) -> set[tuple[str, str]]:
    """Seed pristine blank-template baselines + manifest for a project install.

    The baseline is what three-way template reconciliation diffs against; the
    installer therefore never overwrites an existing baseline — upgrades are
    reconciled by check_skill_freshness.py, which owns baseline promotion.

    Returns the set of (skill_install_name, template_name) keys that ENTERED
    tracking this run — every template on a fresh seed, only the genuinely-new
    ones on an extend. The caller seeds working copies for exactly this set, so a
    reinstall never backfills working copies for templates the project chose not
    to track (which would otherwise read as false `project-customized` drift and
    mask later upstream changes).
    """
    templates_root = project_root / ".agent-work" / "templates"
    baseline_root = templates_root / ".baseline"
    manifest_path = templates_root / "TEMPLATES_MANIFEST.json"

    if baseline_root.exists() or manifest_path.exists():
        # The baseline is the reconcile anchor; never overwrite an existing one.
        # But DO track templates that shipped *after* this project's baseline — a
        # new upstream template otherwise never reaches an established project's
        # versioned-template tracking (check_skill_freshness only sees the
        # manifest). Existing baselines and manifest entries are left untouched.
        return extend_template_baselines(
            skills, templates_root, baseline_root, manifest_path, out=out
        )

    entries: list[dict[str, str]] = []
    seeded: set[tuple[str, str]] = set()
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
            seeded.add((skill.install_name, template.name))

    if not entries:
        return set()

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
    return seeded


def extend_template_baselines(
    skills: Sequence[Skill],
    templates_root: Path,
    baseline_root: Path,
    manifest_path: Path,
    *,
    out: Callable[[str], object],
) -> set[tuple[str, str]]:
    """Track upstream templates that aren't in this project's baseline yet.

    Adds a pristine baseline copy + manifest entry for every passed-skill template
    not already tracked, leaving every existing baseline file and manifest entry
    untouched (mirrors the never-clobber working-copy seeding). This is what lets a
    template shipped after a project's initial install reach its versioned-template
    tracking on a later reinstall. Returns the set of (skill, template) keys newly
    tracked.
    """
    if not manifest_path.is_file():
        # A baseline dir without a manifest is a hand-made/odd state; don't guess.
        out("Template baseline present without a manifest; leaving it untouched.")
        return set()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("templates", [])
    tracked = {(e["skill"], e["template"]) for e in manifest["templates"]}

    added: set[tuple[str, str]] = set()
    for skill in skills:
        source_templates = skill.source_path / "templates"
        if not source_templates.is_dir():
            continue
        for template in sorted(source_templates.iterdir()):
            if not template.is_file():
                continue
            if (skill.install_name, template.name) in tracked:
                continue  # already tracked — never re-anchor an existing baseline
            target = baseline_root / skill.install_name / template.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():  # never clobber an existing anchor file
                shutil.copy2(template, target)
            manifest["templates"].append(
                {
                    "skill": skill.install_name,
                    "template": template.name,
                    "sha256": _hash_file(template),
                }
            )
            added.add((skill.install_name, template.name))

    if added:
        manifest["templates"].sort(key=lambda e: (e["skill"], e["template"]))
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        out(
            f"Template baseline extended: +{len(added)} new template(s) now tracked -> "
            f"{baseline_root}. Run check_skill_freshness.py to reconcile."
        )
    else:
        out("Template baseline already tracks every installed template; left untouched.")
    return added


def write_template_working_copies(
    skills: Sequence[Skill],
    project_root: Path,
    *,
    only: set[tuple[str, str]],
    out: Callable[[str], object],
) -> int:
    """Seed editable project-local template working copies (flat, never clobbered).

    The pristine `.baseline/` is only the reconcile anchor; these flat copies at
    `.agent-work/templates/<name>` are what a project actually edits and commits —
    the half of the versioned-template model the baseline alone does not provide.
    Skills resolve a template project-local-first (`.agent-work/templates/<name>`,
    falling back to the bundled copy), so without a working copy a template edit
    has nowhere to live but the installed skill (which a reinstall overwrites).

    Seeds copies ONLY for `only` — the (skill, template) keys that entered baseline
    tracking this run (every template on a fresh seed, only the genuinely-new ones
    on a reinstall). This deliberately does NOT backfill a working copy for every
    template a project lacks one for: a frozen copy of a template the project never
    customizes reads as false `project-customized` drift and masks later upstream
    changes the project should adopt. Copies are taken from the bundled source in
    token form (identical to the baseline, so they read `up-to-date`); existing
    copies — Charter seeds or prior edits — are never overwritten. Returns the
    number newly seeded.
    """
    templates_root = project_root / ".agent-work" / "templates"
    seeded = 0
    for skill in skills:
        source_templates = skill.source_path / "templates"
        if not source_templates.is_dir():
            continue
        for template in sorted(source_templates.iterdir()):
            if not template.is_file():
                continue
            if (skill.install_name, template.name) not in only:
                continue  # only seed templates entering tracking this run
            target = templates_root / template.name
            if target.exists():
                continue  # never clobber a project edit or a Charter seed
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, target)
            seeded += 1
    if seeded:
        out(
            f"Template working copies seeded: {seeded} editable copy(ies) -> "
            f"{templates_root} (edit + commit these; reconcile with check_skill_freshness.py)"
        )
    return seeded


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
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help=(
            "Seed the project template baseline + manifest without installing skills. "
            "For projects that consume user-scope skills but need template versioning. "
            "Requires --scope project."
        ),
    )
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
        validate_required_references(skills)

        if args.baseline_only:
            if args.scope != "project":
                raise InstallError("--baseline-only requires --scope project")
            if args.dest:
                raise InstallError("--baseline-only does not take --dest")
            project_root = args.project.expanduser() if args.project else runtime_cwd
            if not project_root.is_dir():
                raise InstallError(f"project directory does not exist: {project_root}")
            seeded = write_template_baselines(skills, project_root, out=out)
            write_template_working_copies(skills, project_root, only=seeded, out=out)
            return 0

        target_roots = resolve_target_roots(args, runtime_env, runtime_cwd)
        for agent, target_root in target_roots:
            out(f"{agent.name}:")
            install_skills(
                skills,
                target_root,
                dry_run=args.dry_run,
                force=args.force,
                full_set=args.skills is None,
                restart_message=agent.restart_message,
                out=out,
            )
        if args.scope == "project" and not args.dry_run and not args.dest:
            project_root = args.project.expanduser() if args.project else runtime_cwd
            seeded = write_template_baselines(skills, project_root, out=out)
            write_template_working_copies(skills, project_root, only=seeded, out=out)
    except InstallError as exc:
        parser.exit(2, f"error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
