from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
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

# RUNTIME COMPANIONS: a bundled script that loads a sibling module at runtime must
# ship that sibling too, or the feature silently no-ops wherever the skill is
# actually installed. Expressed as a dependency rather than hand-added to every
# bundle below, because the hand-added form is what drifted: `gauge_reader.py` was
# never added to any of the ten bundles carrying `checklist_engine.py`, so the
# Context Governor (epic-178) was inert in every install since it shipped --
# `_load_gauge_reader()` fails open to None, so Trip never fired and nothing
# reported that it wasn't firing. `tests/test_install_constellation.py` pins this
# against the engine's actual dynamic loads, so a new companion cannot be
# forgotten the same way.
SCRIPT_RUNTIME_COMPANIONS: dict[str, tuple[str, ...]] = {
    # checklist_engine._load_gauge_reader() -> Path(__file__).parent/"gauge_reader.py"
    #
    # The rest are the #305 context-manifest capture seam, reached NOT by a path
    # load but by `sys.path.insert(0, <own parent>)` + a plain import -- which is
    # why the original companion guard could not see them (#362). The engine
    # wraps that import in `try/except ImportError` with a no-op fallback, so an
    # install missing them completes every gate and emits ZERO manifests with
    # nothing on stderr. The whole transitive closure ships, not just the first
    # hop: episode_capture needs agent_work_root at module scope and
    # context_manifest deferred inside emit_step_manifest (deferred to break the
    # context_manifest -> checklist_engine cycle).
    "checklist_engine.py": (
        "gauge_reader.py", "episode_capture.py",
        "agent_work_root.py", "context_manifest.py",
    ),
    # gauge_writer_hook._load_spine_rail() -> Path(__file__).parent/"spine_rail.py",
    # inside a bare `try/except Exception: return None`. A split lands the pair
    # where neither can find the other and NOTHING raises -- the hook just stops
    # resolving gauge paths. Co-location is the whole contract here.
    "gauge_writer_hook.py": ("spine_rail.py",),
}

# SOURCE SUBDIRECTORIES: scripts whose source lives under a subdirectory of
# scripts/ rather than scripts/ itself. The install DESTINATION stays flat
# (`<installed skill>/scripts/<name>`) for every script, which is what puts a
# script and its runtime companions in one directory for free. Only the source
# lookup varies. The hook pair's source layout is frozen -- this repo's own
# settings file and the hooks' own tests hardcode `scripts/hooks/...` -- so the
# installer reaches into the subdirectory instead of relocating the sources.
SCRIPT_SOURCE_SUBDIRS: dict[str, str] = {
    "gauge_writer_hook.py": "hooks",
    "spine_rail.py": "hooks",
}

# NON-INSTALLABLE PACKAGES: directories under scripts/ that are real Python
# packages -- they carry an __init__.py and their modules import each other with
# intra-package relative imports (`from .discovery import ...`). Because the
# install destination is FLAT (above), copying such a package's modules out
# strips the package that those relative imports resolve against, and every one
# of them raises at import. So these are not bundled at all: they are run from a
# checkout as `python -m scripts.<package>`, and no skill declares them.
#
# scripts/hooks/ is NOT one of these. It is a plain source subdirectory of
# standalone modules that import nothing from each other, so flattening it is
# safe and SCRIPT_SOURCE_SUBDIRS handles it.
#
# tests/test_install_constellation.py holds every directory under scripts/ to
# one of these two declarations, so a new package cannot arrive undeclared.
NON_INSTALLABLE_PACKAGES: frozenset[str] = frozenset({"code_map"})


def script_source_path(script: str, scripts_root: Path) -> Path:
    """Where a bundled script is READ from. Single resolver so validation and the
    copy loop can never disagree about a script's source -- a disagreement would
    surface as a hard install failure or, worse, a missing companion."""
    subdir = SCRIPT_SOURCE_SUBDIRS.get(script)
    return scripts_root / subdir / script if subdir else scripts_root / script


def expand_script_bundle(scripts: tuple[str, ...]) -> tuple[str, ...]:
    """Add each script's runtime companions, preserving order and de-duplicating.
    Applied at discovery so every install path inherits it automatically."""
    expanded: list[str] = []
    for script in scripts:
        for name in (script, *SCRIPT_RUNTIME_COMPANIONS.get(script, ())):
            if name not in expanded:
                expanded.append(name)
    return tuple(expanded)


# EPISODE STORE, WRITE SIDE ONLY (#447). The admiral and commander bundles carry the
# store's WRITER (apply_episode_delta.py) and its capture GATE
# (verify_episode_captured.py) because their spines invoke both by name. They do NOT
# carry query_episodes.py -- the read path does not travel with the roles that write.
#
# That omission is a DEFAULT, NOT A BOUNDARY, and the difference matters: an installed
# role that wanted to read the store still can, by at least four measured routes, and a
# reader who believed otherwise would be wrong about the only thing this bundle line
# could be read as promising. The four:
#   1. repo-relative execution -- `python scripts/query_episodes.py` from the project
#      root runs the repo's own copy; nothing about the install is in the way;
#   2. plain Read/Grep -- episodes/ is a TRACKED repo path, so any agent can open the
#      files directly without any script at all;
#   3. the unfiltered copytree in install_skills() below -- a skill's own
#      directory is copied wholesale, so anything committed inside one ships with it;
#   4. SCRIPT_RUNTIME_COMPANIONS -- a future bundled script that imports
#      query_episodes would drag it along automatically.
# The real guarantee lives in doctrine and in the capture gate's own valve
# (scripts/verify_episode_captured.py: ids and counts out, statements never), not here.
SKILL_SCRIPT_BUNDLES: dict[str, tuple[str, ...]] = {
    "admiral": ("checklist_engine.py", "init_work_area.py", "verify_state_note.py", "apply_episode_delta.py", "verify_episode_captured.py", "verify_worktree_isolation.py", "agent_work_root.py", "verify_iterative_role_artifacts.py"),
    "charter": ("checklist_engine.py",),
    # map_orient.py is invoked by COMMANDER_SPINE.template.json as a command
    # postcondition at BOTH the context step (verify-orientation) and the plan
    # step (verify-frame), so it must travel with the skill that serves that
    # template -- an uninstalled script would surface as a confusing gate failure
    # mid-run. It loads no sibling module at runtime (stdlib only), so it has no
    # SCRIPT_RUNTIME_COMPANIONS entry; that is a checked fact, not an omission --
    # tests/test_install_constellation.py pins companions against actual dynamic
    # loads.
    "commander": ("checklist_engine.py", "init_work_area.py", "verify_state_note.py", "run_crew.py", "recover_crews.py", "apply_episode_delta.py", "verify_episode_captured.py", "verify_worktree_isolation.py", "agent_work_root.py", "map_orient.py", "verify_iterative_role_artifacts.py"),
    # workbench is the checklist engine's home skill, so it is the canonical (and
    # only) owner of the gauge WRITER hook -- the gauge exists solely to feed
    # checklist_engine.py's `current` advisory. Deliberately NOT a companion of
    # checklist_engine.py: that would copy the hook into every engine-carrying
    # skill and leave "which copy is canonical?" ambiguous for whatever later
    # wires it into a settings.json.
    "workbench": ("checklist_engine.py", "gauge_writer_hook.py"),
    "interrogator": ("checklist_engine.py", "verify_interrogation.py"),
    "cartographer": ("checklist_engine.py", "build_architecture_map.py"),
    "docent": ("docent_freshness.py",),
    "implementer": ("checklist_engine.py",),
    "reviewer": ("checklist_engine.py", "verify_fowler_pass.py"),
    "explorer": ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py", "verify_iterative_role_artifacts.py"),
    "curator": ("curate_corpus.py",),
    "to-initial-issues": ("verify_issue_set.py", "file_issue_set.py"),
    "replan": ("verify_issue_set.py",),
    "diagnose": ("verify_diagnosis.py",),
    "write-a-skill": ("verify_skill_registered.py", "curate_corpus.py", "install_constellation.py"),
}
# Global doctrine buckets (single source: skills/_shared/), bundled into each skill's
# references/ at install exactly as the scripts above are bundled into scripts/. The
# audience Venn is enforced by which buckets a skill carries: everyone-global is shared
# by all; the tier buckets reach only their tier. A role reads its own bucket(s) at the
# checklist context-read step; the project supplies thin local deltas under docs/agents/.
_GLOBAL_EVERYONE = ("global-everyone.md", "windows.md")
_GLOBAL_ORCHESTRATOR = ("global-everyone.md", "global-orchestrator.md", "design-it-twice-brief.md", "windows.md")
_GLOBAL_CREW = ("global-everyone.md", "global-crew.md", "windows.md")
_GLOBAL_ALL_TIERS = ("global-everyone.md", "global-orchestrator.md", "global-crew.md", "windows.md")
SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {
    "admiral": _GLOBAL_ORCHESTRATOR,
    "commander-delegated": _GLOBAL_ORCHESTRATOR,
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
    "curator": _GLOBAL_EVERYONE + ("skill-goodness.md",),
    "to-initial-issues": _GLOBAL_ORCHESTRATOR,
    "replan": _GLOBAL_ORCHESTRATOR,
    "diagnose": _GLOBAL_ORCHESTRATOR,
    # how-to-talk is prose discipline any agent applies to its own human-facing
    # output, so it is not tier-specific: it carries only the everyone-global
    # doctrine (mirrors interrogator). It ships no script.
    "how-to-talk": _GLOBAL_EVERYONE,
    # write-a-skill authors against the shared skill-goodness criteria, so the
    # reference travels with the installed skill alongside the everyone-global
    # doctrine (mirrors curator's tier; skill-goodness.md is its own bucket).
    "write-a-skill": _GLOBAL_EVERYONE + ("skill-goodness.md",),
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
                required_scripts=expand_script_bundle(
                    SKILL_SCRIPT_BUNDLES.get(source_path.name, ())),
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
            source = script_source_path(script, scripts_root)
            if not source.is_file():
                missing.append(f"{skill.install_name}: {source}")
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
    contract). This is the os.name-based FALLBACK used only when
    `probe_host_interpreter` cannot find any working candidate on the host --
    see `resolve_interpreter`."""
    return "py" if os.name == "nt" else "python3"


INTERPRETER_CANDIDATES: tuple[str, ...] = ("py", "python3", "python")
DEFAULT_INTERPRETER_PROBE_TIMEOUT = 5.0  # seconds; bounds a hung/misregistered `py` launcher


@dataclass(frozen=True)
class InterpreterResolution:
    """The interpreter resolved for ONE install run, plus how it was resolved --
    carried into both the text-rewrite and the per-skill sidecar so a consumer can
    tell a genuinely-probed host from the os.name guess."""

    interpreter: str
    candidates: tuple[str, ...]
    resolved_via: str  # "probe" | "os-default-fallback"

    def as_sidecar(self) -> dict:
        return {
            "interpreter": self.interpreter,
            "candidates": list(self.candidates),
            "resolved_via": self.resolved_via,
        }


def _probe_interpreter_candidate(candidate: str, *, timeout: float) -> bool:
    """Whether `<candidate> --version` exits 0 within `timeout`. A missing
    candidate, a non-zero exit, and a timeout are ALL treated as this candidate
    failing -- never a raise, never a hang past `timeout`."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"  # cp1252 pipes can silently corrupt captured output
    try:
        result = subprocess.run(
            [candidate, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def probe_host_interpreter(
    *,
    candidates: Sequence[str] = INTERPRETER_CANDIDATES,
    timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT,
) -> str | None:
    """Try each candidate in order via a REAL `<candidate> --version` subprocess
    call, accepting the first that exits 0 within `timeout`. Returns `None` if
    every candidate fails. A hung/misregistered `py` launcher is a real, observed
    Windows failure mode -- the per-candidate timeout is what keeps that from
    hanging the whole install run where before a bad guess was harmless."""
    for candidate in candidates:
        # NOTE(windows-store-alias): a bare `python` can resolve to the Microsoft
        # Store's app-execution-alias stub when no real interpreter is installed --
        # it behaves inconsistently rather than like a real interpreter; the
        # timeout above still bounds it, and a failure here is just treated as
        # this candidate failing, same as any other.
        if _probe_interpreter_candidate(candidate, timeout=timeout):
            return candidate
    return None


def resolve_interpreter(
    *,
    candidates: Sequence[str] = INTERPRETER_CANDIDATES,
    timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT,
) -> InterpreterResolution:
    """Resolve the interpreter to stamp into installed skill bodies for ONE
    install run: probe the host once, falling back to `_platform_interpreter`'s
    os.name guess only if every candidate fails (never raises). Call this ONCE
    per run and thread the result through -- never re-probe per skill. Caching
    prevents INTRA-run drift only; cross-run determinism (#197's
    `stable_corpus_id`, which compares two separate install invocations) rests on
    the probe being naturally stable given a static host PATH, the same basis
    today's pure os.name read relies on."""
    probed = probe_host_interpreter(candidates=candidates, timeout=timeout)
    if probed is not None:
        return InterpreterResolution(probed, tuple(candidates), "probe")
    return InterpreterResolution(_platform_interpreter(), tuple(candidates), "os-default-fallback")


def installed_path_replacements(
    target: Path, skill: Skill, interpreter: InterpreterResolution
) -> dict[str, str]:
    """The token -> replacement map applied to an installed bundle's text, as ONE
    definition shared by the writer below and by any reader that must reproduce the
    transform to compare an installed copy against its source.

    Extracted rather than inlined because a verifier that re-derived this map could
    drift from the installer and then report drift that is really its own. That is
    not hypothetical: comparing raw source bytes against installed bytes reports
    every placeholder-bearing bundle as stale, which is exactly what a
    substitution-blind check did during epic #418's closeout.

    Insertion order is load-bearing -- see the note in `rewrite_installed_skill_paths`.
    """
    # Rewrite the interpreter prefix FIRST, before the skill-dir tokens consume the
    # trailing `<`: the replacement preserves the `<` so `<…-skill-dir>` still resolves.
    # Forward slashes keep an absolute Windows interpreter executable while also
    # remaining valid when the command is embedded in a JSON checklist string.
    installed_interpreter = interpreter.interpreter.replace("\\", "/")
    return {
        "python <": f"{installed_interpreter} <",
        "<skill-dir>": target.as_posix(),
        f"<{skill.source_name}-skill-dir>": target.as_posix(),
    }


def apply_installed_path_replacements(text: str, replacements: dict[str, str]) -> str:
    """Apply `replacements` to `text` in insertion order. The single application
    path, so the writer and any verifier cannot disagree about ordering."""
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    return text


def rewrite_installed_skill_paths(
    target: Path, skill: Skill, interpreter: InterpreterResolution
) -> None:
    replacements = installed_path_replacements(target, skill, interpreter)
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in REWRITABLE_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        rewritten = apply_installed_path_replacements(text, replacements)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")
    # Per-skill sidecar: any engine-invoking command string living inside this
    # skill's own installed tree finds its interpreter resolution as a sibling,
    # matching the installer's existing per-skill copy convention (required_scripts,
    # required_references) rather than a single shared install-root file.
    (target / "interpreter.json").write_text(
        json.dumps(interpreter.as_sidecar(), indent=2) + "\n", encoding="utf-8"
    )


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


INITIAL_CUT_INSTALL_NAME = "constellation-to-initial-issues"
LEGACY_INITIAL_CUT_INSTALL_NAME = "constellation-to-issues"


def migrate_legacy_initial_cut_destination(
    skills: Sequence[Skill],
    target_root: Path,
    *,
    force: bool,
    dry_run: bool,
    out: Callable[[str], object],
) -> None:
    """Apply the one sanctioned hard-rename migration, and no broader cleanup.

    Selecting the canonical skill detects only the exact legacy install folder.
    Explicit ``--force`` is the authority to remove it.  Dry-run reports the
    same exact target without mutation.
    """
    if not any(skill.install_name == INITIAL_CUT_INSTALL_NAME for skill in skills):
        return
    legacy = target_root / LEGACY_INITIAL_CUT_INSTALL_NAME
    if not legacy.exists():
        return
    ensure_target_is_inside_root(target_root, legacy)
    migration = "--skills to-initial-issues --force"
    if not force:
        raise InstallError(
            f"legacy initial-cut destination exists at {legacy}; migrate with {migration}"
        )
    if dry_run:
        out(f"- DRY RUN: would remove legacy initial-cut destination {legacy}")
        return
    if legacy.is_dir():
        shutil.rmtree(legacy)
    else:
        legacy.unlink()


# ---------------------------------------------------------------------------
# Context Governor hook wiring (#262)
# ---------------------------------------------------------------------------
# The hook scripts bundled above do nothing at all until a settings.json
# actually invokes them, and NOTHING ELSE IN THE SYSTEM CAN REPORT THAT GAP:
# per #265 a hook that never runs cannot write a sidecar explaining that it
# never ran. So detection here is always on.
#
# It is also strictly READ-ONLY. `decision:opt-in-wiring-only` is a human
# ruling: without --wire-hooks the installer reads settings.json, reports, and
# writes nothing -- it does not even create the file when it is absent.

SETTINGS_FILENAME = "settings.json"
# The per-machine sibling Claude Code also reads. Its hooks MERGE with (never
# replace) the ones in settings.json -- so this file is where a command
# carrying an absolute path and a host-probed interpreter name belongs, and
# settings.json stays the same bytes for every contributor. See `--hooks-from
# source` in `wire_hooks`.
LOCAL_SETTINGS_FILENAME = "settings.local.json"
GAUGE_WRITER_HOOK_SCRIPT = "gauge_writer_hook.py"
SPINE_RAIL_HOOK_SCRIPT = "spine_rail.py"
# The canonical owner (see SKILL_SCRIPT_BUNDLES["workbench"]): exactly one
# installed copy exists, so the wiring has an unambiguous path to point at.
HOOK_OWNER_SKILL = "workbench"
HOOK_OWNER_INSTALL_NAME = "constellation-workbench"
HOOK_EVENT = "PostToolUse"
# Matcher and timeout are carried VERBATIM from the snippet in
# docs/GAUGE_WRITER_HOOK.md. Neither is tuned, derived, or invented here: the
# matcher is "*" (unlike spine_rail.py's "Bash", the gauge must see every tool
# call to track fill continuously) and the timeout is the documented 10.
HOOK_MATCHER = "*"
HOOK_TIMEOUT = 10


@dataclass(frozen=True)
class HookSpec:
    """ONE hook this installer knows how to wire and to detect.

    Four exist (#539), not one: the Context Governor's PostToolUse gauge writer
    plus the three `spine_rail.py` events. Before this table the installer
    hard-coded the gauge writer's event/matcher/timeout as module constants and
    had no representation at all for the other three -- so `--wire-hooks` could
    only ever produce a quarter of the wiring, and detection could only ever
    see a quarter of it.

    `(event, script)` is the identity: two specs never share both, so one
    settings.json entry belongs to at most one spec, and `spine_rail.py`
    appearing under three different events stays unambiguous."""

    name: str                  # stable id used in reports; never user-facing config
    script: str                # the hook script's FILE NAME, not a path
    event: str                 # the Claude Code hook event this entry lives under
    matcher: str | None        # None for events (Stop) that take no matcher
    args: tuple[str, ...]      # positional arguments appended after the script path
    timeout: int


# Every field below is carried VERBATIM from this repo's own
# .claude/settings.json (the four entries it ships) -- nothing here is tuned,
# derived, or invented. `tests/test_interpreter_portability.py` holds this
# table to that file so the two cannot drift apart.
GAUGE_WRITER_SPEC = HookSpec(
    name="gauge_writer",
    script=GAUGE_WRITER_HOOK_SCRIPT,
    event=HOOK_EVENT,
    matcher=HOOK_MATCHER,
    args=(),
    timeout=HOOK_TIMEOUT,
)
SPINE_RAIL_SPECS: tuple[HookSpec, ...] = (
    HookSpec("spine_rail_stop", SPINE_RAIL_HOOK_SCRIPT, "Stop", None, ("Stop",), 20),
    HookSpec(
        "spine_rail_session_start", SPINE_RAIL_HOOK_SCRIPT, "SessionStart",
        "compact|resume|startup", ("SessionStart",), 20,
    ),
    HookSpec(
        "spine_rail_post_tool_use", SPINE_RAIL_HOOK_SCRIPT, "PostToolUse",
        "Bash", ("PostToolUse",), 10,
    ),
)
HOOK_SPECS: tuple[HookSpec, ...] = (GAUGE_WRITER_SPEC, *SPINE_RAIL_SPECS)

# Named hook SETS the CLI exposes. `governor` is the default and is exactly
# what `--wire-hooks` did before #539 -- the flag's existing contract is
# unchanged, and the rail (which can BLOCK a Stop) is never added to somebody's
# settings.json as a side effect of an install they already knew how to run.
HOOK_SETS: dict[str, tuple[HookSpec, ...]] = {
    "governor": (GAUGE_WRITER_SPEC,),
    "rail": SPINE_RAIL_SPECS,
    "all": HOOK_SPECS,
}
DEFAULT_HOOK_SET = "governor"

# Where the wiring points its script paths.
HOOKS_FROM_INSTALLED = "installed"  # <target_root>/constellation-workbench/scripts/
HOOKS_FROM_SOURCE = "source"        # this checkout's own scripts/hooks/
HOOKS_FROM_CHOICES = (HOOKS_FROM_INSTALLED, HOOKS_FROM_SOURCE)

# Hooks are a Claude Code mechanism. No other supported agent reads a
# `hooks.PostToolUse` array, so detecting -- let alone writing -- one under
# ~/.codex/ would be reporting on a file nothing ever reads.
HOOK_CAPABLE_AGENT_NAMES = frozenset({AGENT_TARGETS["claude"].name})

WIRING_WIRED = "wired"
WIRING_STALE = "stale"
WIRING_UNWIRED = "unwired"
# Only reachable when more than one spec is being asked about: SOME hooks
# resolve and others have no entry at all. Before #539 this shape could not be
# expressed -- a single resolvable entry made the whole verdict `wired`, so
# three missing hooks out of four would have read as fully wired. That is the
# reassuring-failure shape, one level up from the one `stale` was added for.
WIRING_PARTIAL = "partial"
# NOT a fourth classification of entries -- it says the entries could not be
# classified at all. Reporting that beats lying in the reassuring direction
# ("wired") or the alarming one ("stale"), and beats taking the install down.
WIRING_UNREADABLE = "unreadable"
# Also not a classification of entries: it says THESE entries cannot be
# classified from here. See `_EXPANDABLE_ENV_TOKENS`.
WIRING_UNDETERMINABLE = "undeterminable"

# The ONLY env token this detector will expand. Everything else stays literal
# and makes its entry undeterminable, on purpose.
#
# Expansion happens in the INSTALLER's environment, but the entry will run in a
# future HOOK's environment -- different process, different variables. Expanding
# freely lets an unrelated variable that happens to be set right now resolve a
# path and report WIRED, which manufactures exactly the reassuring failure this
# detector exists to prevent (reproduced with a `%MYTOOLS%` entry during g2
# review). `CLAUDE_PROJECT_DIR` is the one token we can reason about: it is the
# form our own docs recommend for a source checkout, so refusing to detect it
# would be incoherent. Note we are still stricter about what we EMIT than what
# we ACCEPT -- `build_hook_command` never produces a token at all.
_EXPANDABLE_ENV_TOKENS = frozenset({"CLAUDE_PROJECT_DIR"})

def _script_path_re(script: str) -> re.Pattern:
    """Matches the path of `script` inside a hook command string. Quoted form
    first: an installed path on Windows can contain spaces, so the quotes --
    not whitespace -- are what delimit it."""
    escaped = re.escape(script)
    return re.compile(rf'"([^"]*{escaped})"|(\S*{escaped})')


_HOOK_SCRIPT_PATH_RES: dict[str, re.Pattern] = {
    script: _script_path_re(script)
    for script in (GAUGE_WRITER_HOOK_SCRIPT, SPINE_RAIL_HOOK_SCRIPT)
}
_HOOK_SCRIPT_PATH_RE = _HOOK_SCRIPT_PATH_RES[GAUGE_WRITER_HOOK_SCRIPT]
_ENV_TOKEN_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|%([A-Za-z_][A-Za-z0-9_]*)%")


@dataclass(frozen=True)
class HookWiring:
    """One read-only verdict about one settings.json, covering the `specs` it
    was asked about (the Context Governor's one hook by default)."""

    state: str
    settings_path: Path
    settings_exists: bool
    resolved: tuple[str, ...] = ()    # commands whose script IS on disk
    unresolved: tuple[str, ...] = ()  # commands that resolve to nothing
    # commands carrying an env token we decline to evaluate -- neither
    # confirmed nor condemned, because from here they are genuinely unknowable
    undeterminable: tuple[str, ...] = ()
    error: str | None = None
    # Spec NAMES with no entry in this settings.json at all. Distinct from
    # `unresolved` on purpose: "you never wired this" and "you wired it at a
    # path that no longer exists" are different problems with different fixes,
    # and only the second one is a defect.
    missing: tuple[str, ...] = ()
    specs: tuple[HookSpec, ...] = (GAUGE_WRITER_SPEC,)


def settings_path_for_target_root(target_root: Path) -> Path:
    """The settings.json governing the agent config dir this install writes
    into: `~/.claude/skills` -> `~/.claude/settings.json`, and at project scope
    `<project>/.claude/skills` -> `<project>/.claude/settings.json`.

    Derived from the RESOLVED target root rather than re-derived from scope, so
    a `--dest` install -- which every test in this repo uses -- can never reach
    past its own tree into the developer's real ~/.claude/settings.json."""
    return target_root.parent / SETTINGS_FILENAME


def local_settings_path_for_target_root(target_root: Path) -> Path:
    """The per-machine settings file beside the shared one."""
    return target_root.parent / LOCAL_SETTINGS_FILENAME


def installed_hook_path(target_root: Path, script: str) -> Path:
    """Where `script` lands in an INSTALL. The destination is flat under the
    canonical owner's bundle, so both hook scripts sit in one directory."""
    return target_root / HOOK_OWNER_INSTALL_NAME / "scripts" / script


def installed_gauge_writer_path(target_root: Path) -> Path:
    return installed_hook_path(target_root, GAUGE_WRITER_HOOK_SCRIPT)


def source_hook_path(script: str, repo_root: Path = REPO_ROOT) -> Path:
    """Where `script` lives in THIS checkout -- `scripts/hooks/<script>`,
    resolved through the same `script_source_path` the copy loop uses so the
    two can never disagree about a hook's source.

    This is the half of #539 the installer could not do at all: `hook_command`
    could only ever point at an INSTALLED skill copy, so the repo that owns
    the hooks was the one repo whose hooks it could not wire."""
    return script_source_path(script, repo_root / "scripts")


def hook_script_path(target_root: Path, script: str, *, hooks_from: str) -> Path:
    if hooks_from == HOOKS_FROM_SOURCE:
        return source_hook_path(script)
    return installed_hook_path(target_root, script)


def _expand_env_tokens(text: str, env: Mapping[str, str]) -> str:
    """Expand ONLY `_EXPANDABLE_ENV_TOKENS`, and only when actually set,
    leaving every other token LITERAL rather than dropping it -- a dropped
    token would collapse the path to a shorter one that might coincidentally
    exist. A surviving token is the signal `detect_hook_wiring` uses to declare
    an entry undeterminable rather than guessing at it."""

    def replace(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        if name not in _EXPANDABLE_ENV_TOKENS:
            return match.group(0)
        return env.get(name, match.group(0))

    return _ENV_TOKEN_RE.sub(replace, text)


def extract_hook_script_path(command: str, script: str = GAUGE_WRITER_HOOK_SCRIPT) -> str | None:
    """The `script` path a hook `command` string invokes, or None when the
    command does not invoke that script at all. Defaults to the gauge writer,
    so every pre-#539 caller keeps asking exactly the question it asked."""
    pattern = _HOOK_SCRIPT_PATH_RES.get(script) or _script_path_re(script)
    match = pattern.search(command)
    if match is None:
        return None
    return match.group(1) or match.group(2)


def hook_command_text(hook: object) -> str | None:
    """One hook object's full invocation as a single string.

    Exec-form entries (`{"command": "python3", "args": ["/path/x.py"]}`) put
    the script path in `args`, not in `command`. We never EMIT that form, but
    a hand-written one is real and must not read as "no hook here at all" --
    that would be a silent false negative in the one detector that exists to
    catch silence. Joining is enough for path extraction; it is never executed."""
    if not isinstance(hook, dict):
        return None
    command = hook.get("command")
    if not isinstance(command, str):
        return None
    args = hook.get("args")
    if isinstance(args, list):
        return " ".join([command, *(a for a in args if isinstance(a, str))])
    return command


def _event_hook_commands(settings: object, event: str) -> list[str]:
    """Every hook command string under one event, flattened across matcher
    blocks. Deliberately tolerant of shapes it does not expect: an odd
    settings.json is something to REPORT, never something to raise on in the
    middle of an otherwise-fine install."""
    commands: list[str] = []
    if not isinstance(settings, dict):
        return commands
    hooks = settings.get("hooks")
    entries = hooks.get(event) if isinstance(hooks, dict) else None
    if not isinstance(entries, list):
        return commands
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for hook in entry.get("hooks") or []:
            text = hook_command_text(hook)
            if text is not None:
                commands.append(text)
    return commands


def hook_commands_for_spec(settings: object, spec: HookSpec) -> list[str]:
    """Every command under `spec.event` that invokes `spec.script`."""
    return [
        command
        for command in _event_hook_commands(settings, spec.event)
        if extract_hook_script_path(command, spec.script)
    ]


def governor_hook_commands(settings: object) -> list[str]:
    """Every PostToolUse command string that invokes a gauge writer hook."""
    return hook_commands_for_spec(settings, GAUGE_WRITER_SPEC)


def detect_hook_wiring(
    settings_path: Path,
    *,
    env: Mapping[str, str],
    specs: Sequence[HookSpec] = (GAUGE_WRITER_SPEC,),
) -> HookWiring:
    """READ-ONLY -- opens nothing for writing and creates nothing.

    Classification is by RESOLVING each entry's script path against the
    filesystem, never by string-matching the command. Under a string match a
    moved, renamed, or uninstalled tree still reads as `wired`, which is exactly
    the reassuring-failure shape this detector exists to prevent.

    Each spec in `specs` is classified on its own, then rolled up. `specs`
    defaults to the Context Governor's single hook, so every pre-#539 caller
    gets byte-identical verdicts; pass `HOOK_SPECS` to ask about all four."""
    specs = tuple(specs)
    if not settings_path.is_file():
        return HookWiring(
            WIRING_UNWIRED, settings_path, False,
            missing=tuple(spec.name for spec in specs), specs=specs,
        )
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return HookWiring(WIRING_UNREADABLE, settings_path, True, error=str(exc), specs=specs)

    resolved: list[str] = []
    unresolved: list[str] = []
    undeterminable: list[str] = []
    missing: list[str] = []
    covered: list[str] = []       # spec has at least one entry that RESOLVES
    unknown_specs: list[str] = []  # spec has entries, none resolve, some unknowable
    broken_specs: list[str] = []   # spec has entries and every one names nothing

    for spec in specs:
        commands = hook_commands_for_spec(settings, spec)
        if not commands:
            missing.append(spec.name)
            continue
        spec_resolved: list[str] = []
        spec_unknown: list[str] = []
        spec_unresolved: list[str] = []
        for command in commands:
            raw = extract_hook_script_path(command, spec.script) or ""
            expanded = _expand_env_tokens(raw, env)
            if _ENV_TOKEN_RE.search(expanded):
                # An env token we will not evaluate survives. Resolving it
                # against the installer's own environment would answer a
                # question about the WRONG process, so we decline rather than
                # guess in either direction.
                spec_unknown.append(command)
            elif Path(expanded).is_file():
                spec_resolved.append(command)
            else:
                spec_unresolved.append(command)
        resolved.extend(spec_resolved)
        undeterminable.extend(spec_unknown)
        unresolved.extend(spec_unresolved)
        if spec_resolved:
            covered.append(spec.name)
        elif spec_unknown:
            unknown_specs.append(spec.name)
        else:
            broken_specs.append(spec.name)

    if not covered and not unknown_specs and not broken_specs:
        # Nothing was wired at all. Not a defect -- an uninstalled project.
        state = WIRING_UNWIRED
    elif broken_specs:
        # Something is definitely wired WRONG: a named path with no file.
        state = WIRING_STALE
    elif missing:
        state = WIRING_PARTIAL
    elif unknown_specs:
        # Ahead of WIRED deliberately: a spec we cannot evaluate is not a spec
        # we have confirmed. "I cannot tell" must not be reported as
        # "definitely broken" any more than as "definitely fine".
        state = WIRING_UNDETERMINABLE
    else:
        state = WIRING_WIRED
    return HookWiring(
        state, settings_path, True, tuple(resolved), tuple(unresolved),
        tuple(undeterminable), missing=tuple(missing), specs=specs,
    )


def _wiring_label(wiring: HookWiring) -> str:
    """What to CALL the hooks in a report line. Kept as the pre-#539 wording
    whenever the question asked was the pre-#539 question, so existing reports
    and the docs that quote them stay word-for-word correct."""
    if tuple(wiring.specs) == (GAUGE_WRITER_SPEC,):
        return "Context Governor hooks"
    return "Constellation hooks"


def _wiring_events(wiring: HookWiring) -> str:
    return "/".join(dict.fromkeys(spec.event for spec in wiring.specs))


def _wiring_scripts(wiring: HookWiring) -> str:
    return "/".join(dict.fromkeys(spec.script for spec in wiring.specs))


def describe_hook_wiring(wiring: HookWiring) -> str:
    """One reportable line. ASCII only -- this goes to a Windows console."""
    label = _wiring_label(wiring)
    events = _wiring_events(wiring)
    scripts = _wiring_scripts(wiring)
    if wiring.state == WIRING_WIRED:
        paths = ", ".join(sorted({
            extract_hook_script_path(command, spec.script) or command
            for spec in wiring.specs
            for command in wiring.resolved
            if extract_hook_script_path(command, spec.script)
        }))
        return f"- {label}: WIRED -- {paths}"
    if wiring.state == WIRING_PARTIAL:
        return (
            f"- {label}: PARTIALLY WIRED -- {len(wiring.resolved)} of {len(wiring.specs)} "
            f"hook(s) resolve in {wiring.settings_path}, but these have no entry at all: "
            f"{', '.join(wiring.missing)}. Those events never fire and nothing else can "
            f"tell you that. Re-run with --wire-hooks --hooks all to add the missing ones."
        )
    if wiring.state == WIRING_STALE:
        return (
            f"- {label}: STALE -- {len(wiring.unresolved)} {events} "
            f"entry(ies) in {wiring.settings_path} name a {scripts} that "
            f"is not on disk, so the hook never runs and nothing else can tell you that: "
            f"{'; '.join(wiring.unresolved)}. Re-run with --wire-hooks to add a correct "
            f"entry; the stale one is left in place for you to remove."
        )
    if wiring.state == WIRING_UNDETERMINABLE:
        return (
            f"- {label}: CANNOT EVALUATE -- {len(wiring.undeterminable)} "
            f"{events} entry(ies) in {wiring.settings_path} name the script through an "
            f"environment variable this installer will not expand, because it would be "
            f"expanded in the WRONG process (this one, not the future hook's): "
            f"{'; '.join(wiring.undeterminable)}. Whether the hook fires cannot be "
            f"determined from here -- it is neither confirmed nor condemned."
        )
    if wiring.state == WIRING_UNREADABLE:
        return (
            f"- {label}: UNREADABLE -- could not parse "
            f"{wiring.settings_path} ({wiring.error}), so the wiring state is unknown. "
            f"Nothing was read past this point and nothing was changed."
        )
    where = wiring.settings_path if wiring.settings_exists else f"{wiring.settings_path} (absent)"
    return (
        f"- {label}: UNWIRED -- no {events} entry for "
        f"{scripts} in {where}, so nothing there ever fires. "
        f"Re-run with --wire-hooks to add one; nothing is written without that flag. "
        f"NOT WIRED YET is not the same as WIRED WRONG: this reads as an uninstalled "
        f"project, not a defective one."
    )


def local_settings_note(target_root: Path) -> str:
    """A sentence naming the per-machine sibling when one exists, else "".

    Every verdict this installer prints is about the SHARED settings.json.
    Claude Code merges hooks across both files, so a reader who is told
    "UNWIRED" while a populated settings.local.json sits next to it would draw
    a false conclusion about whether the hooks run. Say it exists; do not
    claim it satisfies anything."""
    local_path = local_settings_path_for_target_root(target_root)
    if not local_path.is_file():
        return ""
    return (
        f" NOTE: {local_path.name} also exists beside it and Claude Code merges its "
        f"hooks with these; it is per-machine and does not ship, so it cannot satisfy "
        f"this verdict."
    )


def report_hook_wiring(
    target_root: Path,
    *,
    env: Mapping[str, str],
    out: Callable[[str], object],
    specs: Sequence[HookSpec] = (GAUGE_WRITER_SPEC,),
) -> HookWiring:
    wiring = detect_hook_wiring(
        settings_path_for_target_root(target_root), env=env, specs=specs)
    out(describe_hook_wiring(wiring) + local_settings_note(target_root))
    return wiring


def assert_shell_safe_command(command: str) -> None:
    """A hook `command` must begin with a COMMAND WORD -- never with a quote.

    This is the #539 trap made unrepresentable. Claude Code spawns a shell-form
    hook with `sh -c` on POSIX, Git Bash on Windows, or PowerShell when Git
    Bash is not installed. PowerShell parses a statement that STARTS with a
    double quote as a string-literal expression rather than a command: it
    echoes the path and exits 0 without running anything. A hook that silently
    does nothing is indistinguishable from a hook with nothing to say, which is
    worse than one that errors.

    Naming the interpreter first is what removes that hazard, and it removes it
    under EVERY shell -- `sh`, Git Bash, PowerShell and `cmd` all parse a
    leading bare word as a command to run. So this invariant does not depend on
    the PowerShell parse claim being true; it is simply the form that is
    correct whether or not it is."""
    # Leading WHITESPACE is the same defect wearing a hat: a shell strips it,
    # so ` "path"` is the leading-quote command again. Requiring a bare word
    # character first is the invariant, not "does not literally begin with a
    # double quote".
    if not command or command[0] in "\"' \t":
        raise InstallError(
            f"refusing to emit a hook command that does not start with a command word: "
            f"{command!r}. "
            f"Under PowerShell (Claude Code's shell-form fallback on a Windows host "
            f"without Git Bash) a leading quote parses as a string literal, so the hook "
            f"echoes its own path and exits 0 without running -- a silent no-op. Name "
            f"the interpreter first."
        )


def build_hook_command(script_path: Path, interpreter: str, args: Sequence[str] = ()) -> str:
    """The literal `command` string an entry carries.

    ABSOLUTE, and never `${CLAUDE_PROJECT_DIR}`. That variable delivers its
    anti-tamper property only as an accident of undocumented harness behaviour
    (#269 established it is fixed at session launch, so it HAPPENS to point at
    the main checkout for an agent working in a worktree) -- unowned by us and
    one release from changing. An absolute installed path is pinned BY
    CONSTRUCTION and asks the harness to guarantee nothing, which is what
    actually protects the ruling that an agent's own branch cannot edit the code
    that judges it.

    `interpreter` comes from the run's single `resolve_interpreter()` probe --
    never re-probed here, never hardcoded. Naming it at all is only safe
    BECAUSE this string is written per machine: no single interpreter name
    works on every platform, which is why the git-tracked settings.json names
    none (#539)."""
    command = f'{interpreter} "{script_path.as_posix()}"'
    if args:
        command = " ".join([command, *args])
    assert_shell_safe_command(command)
    return command


def build_hook_entry(command: str, spec: HookSpec = GAUGE_WRITER_SPEC) -> dict:
    hooks = [{"type": "command", "command": command, "timeout": spec.timeout}]
    if spec.matcher is None:
        # Stop takes no matcher. Emitting `"matcher": null` or a bogus "*"
        # would be inventing config this repo's own settings.json does not use.
        return {"hooks": hooks}
    return {"matcher": spec.matcher, "hooks": hooks}


def add_hook_entry(settings: dict, entry: dict, event: str = HOOK_EVENT) -> bool:
    """Append `entry` as a SIBLING in `hooks.<event>`, in place. Never nests
    inside an existing matcher block, never reorders what is already there, and
    never removes anything -- including a stale governor entry, which is
    reported rather than silently rewritten (no self-healing, by design).

    Returns False when an identical command is already present under `event`."""
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(f"--wire-hooks: 'hooks' in settings is not an object: {type(hooks).__name__}")
    entries = hooks.setdefault(event, [])
    if not isinstance(entries, list):
        raise InstallError(
            f"--wire-hooks: 'hooks.{event}' in settings is not an array: {type(entries).__name__}"
        )
    if entry["hooks"][0]["command"] in _event_hook_commands(settings, event):
        return False
    entries.append(entry)
    return True


def settings_path_for_wiring(target_root: Path, hooks_from: str) -> Path:
    """Which settings file `--wire-hooks` writes.

    `installed` keeps writing the same file it always wrote. `source` writes
    the per-machine sibling instead, and that is not a preference: a
    source-tree command carries this checkout's absolute path AND an
    interpreter name probed on THIS host, so it is wrong for every other
    machine by construction. Claude Code merges hooks across both files rather
    than letting one replace the other, so the shared file keeps whatever it
    already had."""
    if hooks_from == HOOKS_FROM_SOURCE:
        return local_settings_path_for_target_root(target_root)
    return settings_path_for_target_root(target_root)


def wire_hooks(
    target_root: Path,
    *,
    interpreter: InterpreterResolution,
    dry_run: bool,
    scope: str,
    out: Callable[[str], object],
    specs: Sequence[HookSpec] = (GAUGE_WRITER_SPEC,),
    hooks_from: str = HOOKS_FROM_INSTALLED,
) -> None:
    """The ONE path on which this installer writes a settings file. Reached only
    from the explicit `--wire-hooks` opt-in (`decision:opt-in-wiring-only`, a
    human ruling), and still a no-op under `--dry-run`."""
    specs = tuple(specs)

    # FAIL LOUDLY ON A PLATFORM WE CANNOT SERVE (#539). `resolve_interpreter`
    # never raises: when every candidate fails to run it falls back to an
    # os.name GUESS so the rest of the install can proceed. Stamping that guess
    # into a hook command would write wiring we already know cannot run, and a
    # hook that cannot start is exactly as silent as one that was never wired.
    # Refuse instead, and name what was tried.
    if interpreter.resolved_via != "probe":
        raise InstallError(
            f"--wire-hooks: no Python interpreter answered on this host. Tried "
            f"{', '.join(interpreter.candidates)} -- none of them exited 0 for "
            f"`--version`. Refusing to write a hook command built from the os.name "
            f"fallback guess ({interpreter.interpreter!r}), because that wiring could "
            f"not run and a hook that never starts reports nothing at all. Put a working "
            f"Python on PATH under one of those names and re-run."
        )

    settings_path = settings_path_for_wiring(target_root, hooks_from)

    if hooks_from == HOOKS_FROM_SOURCE and is_git_tracked(settings_path):
        raise InstallError(
            f"--wire-hooks --hooks-from source: refusing to write {settings_path} -- it is "
            f"git-tracked. Source-tree wiring carries this checkout's absolute path and an "
            f"interpreter probed on this host, so committing it hands every teammate a "
            f"path that does not exist on their machine. Untrack it (it belongs in "
            f".gitignore) and re-run."
        )

    commands: list[tuple[HookSpec, str]] = []
    for spec in specs:
        script = hook_script_path(target_root, spec.script, hooks_from=hooks_from)
        if not dry_run and not script.is_file():
            raise InstallError(
                f"--wire-hooks: no {spec.script} at {script}. Refusing to wire a "
                f"path with no file behind it, and refusing to point at another skill's copy."
            )
        commands.append((spec, build_hook_command(script, interpreter.interpreter, spec.args)))

    settings: dict = {}
    if settings_path.is_file():
        try:
            loaded = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise InstallError(
                f"--wire-hooks: refusing to touch {settings_path} -- it is not valid JSON "
                f"({exc}). Fix or move it; the installer will not clobber a file it cannot read."
            )
        if not isinstance(loaded, dict):
            raise InstallError(
                f"--wire-hooks: refusing to touch {settings_path} -- its top level is "
                f"{type(loaded).__name__}, not an object."
            )
        settings = loaded

    added: list[tuple[HookSpec, str]] = []
    unchanged: list[tuple[HookSpec, str]] = []
    for spec, command in commands:
        target = added if add_hook_entry(
            settings, build_hook_entry(command, spec), spec.event) else unchanged
        target.append((spec, command))

    if dry_run:
        # `dry_run` is pre-existing plumbing and this is a NEW write path, so the
        # bail-out is placed after everything that can refuse and before anything
        # that can write -- the mutation above happened only in memory.
        for spec, command in commands:
            verb = "add" if (spec, command) in added else "leave unchanged (already present)"
            out(f"- DRY RUN: would {verb} the {spec.event} entry in {settings_path}")
            out(f"- DRY RUN: would write command: {command}")
        out(f"- DRY RUN: {settings_path.name} NOT written")
        return

    if added:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        for spec, command in added:
            out(f"- wired the {spec.name} {spec.event} hook into {settings_path}")
            out(f"  command: {command}")
    for spec, _command in unchanged:
        out(f"- {spec.name} {spec.event} hook already present in {settings_path}; unchanged")

    if hooks_from == HOOKS_FROM_SOURCE:
        out(
            f"- NOTE: this wiring points at this checkout's own scripts/hooks/ and names "
            f"the interpreter probed here ({interpreter.interpreter}). It is correct on "
            f"THIS machine only. It was written to {settings_path.name}, which is "
            f"per-machine and must never be committed; Claude Code merges its hooks with "
            f"whatever {SETTINGS_FILENAME} already carries rather than replacing them."
        )
    elif scope == "project":
        # The absolute path is the accepted cost of rejecting a project-relative
        # form, and it embeds the user's home directory AND user name. A
        # project-scope settings.json is committable, so say so out loud rather
        # than letting committing it be the path of least resistance.
        out(
            f"- NOTE: this entry embeds an absolute path containing your user name, and it "
            f"is machine-specific. A project-scope {SETTINGS_FILENAME} is committable -- "
            f"prefer --scope user, or keep {settings_path} out of version control."
        )


# --------------------------------------------------------------------------- #
# readiness check (#458) -- report-only: never repairs, never writes settings.json
# --------------------------------------------------------------------------- #
# "Is this project set up to run Constellation" answered as four separately
# testable checks, never a single opaque verdict. Each returns a ReadinessCheck
# so a failing item always carries a NAMED reason -- a check that can only ever
# report ready is the exact defect this exists to catch.


READINESS_READY = "READY"
READINESS_NOT_READY = "NOT READY"
# A THIRD outcome, not a flavour of the second (#539). `check_hooks_shippable`
# can reach a state where it honestly cannot tell -- an entry names its script
# through an environment variable that only exists in the future hook's
# process. Expanding it here would answer a question about the wrong process.
# Two states force that honest "I cannot tell" to be laundered into a pass or
# a fail; a correctly wired repo was being reported as defective on exactly
# that account. Undeterminable is not ready -- but it is not a defect either.
READINESS_UNDETERMINABLE = "CANNOT DETERMINE"


@dataclass(frozen=True)
class ReadinessCheck:
    """One readiness item's verdict. `reason` is always populated -- on a pass
    it names what was actually verified, not just 'ok', so a reader can tell a
    real determination from a check that never ran.

    `determinable=False` means the check ran and reached no verdict. It implies
    `ready=False` (an unconfirmed item is never reported as confirmed) but it
    must not be rolled up as a failure."""

    ready: bool
    reason: str
    determinable: bool = True

    @property
    def verdict(self) -> str:
        if self.ready:
            return READINESS_READY
        return READINESS_NOT_READY if self.determinable else READINESS_UNDETERMINABLE


def check_engine_runnable(*, python: str = sys.executable, timeout: float = 10.0) -> ReadinessCheck:
    """Readiness item 1: engine present and runnable (environment-scoped).

    Actually imports and runs pytest under `python` (default `sys.executable`
    specifically -- never a bare `python`/`py` shell-out, which is a DIFFERENT
    interpreter than the one this process is running under and can silently
    diverge from it). Distinguishes three outcomes: the interpreter itself
    cannot be launched; the interpreter launches but pytest is not importable
    (`py` on a real box exits nonzero with 'No module named pytest' and reads
    exactly like a red suite if only a launch is checked); both present and
    working."""
    try:
        result = subprocess.run(
            [python, "-m", "pytest", "--version"],
            capture_output=True, text=True, timeout=timeout,
        )
    except FileNotFoundError:
        return ReadinessCheck(False, f"interpreter not found: {python}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ReadinessCheck(False, f"interpreter at {python} did not run: {exc}")

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        if "no module named pytest" in detail.lower():
            return ReadinessCheck(False, f"pytest not installed for {python}: {detail}")
        return ReadinessCheck(False, f"pytest failed to run under {python}: {detail[:200] or 'no output'}")

    return ReadinessCheck(True, f"pytest runnable under {python} ({(result.stdout or '').strip()})")


def check_work_area_present(project_root: Path) -> ReadinessCheck:
    """Readiness item 4: work area present (tree-scoped).

    README.md's own Baseline Assumptions: 'a Git repo, Markdown docs, and
    file-based workflow state'. A `.git` entry -- directory (a normal repo) or
    file (a worktree's pointer, e.g. this very worktree) -- is the check;
    `.agent-work/` is deliberately NOT required, since a project ready to
    *start* using Constellation has not necessarily run it yet."""
    git_entry = project_root / ".git"
    if not git_entry.exists():
        return ReadinessCheck(False, f"no .git at {project_root} -- not a Git repo")
    return ReadinessCheck(True, f".git present at {project_root}")


def check_skills_installed(
    target_root: Path, *, expected_skills: Iterable[str] | None = None
) -> ReadinessCheck:
    """Readiness item 2: skills installed and registered (tree/target-scoped).

    Ready iff `target_root` carries a `CORPUS.json` marker (the installer's own
    provenance stamp) and at least one `constellation-*` skill folder; when
    `expected_skills` is given (the install_name set a real --agent/--scope/
    --skills combination would target), every named skill must be present too.

    `target_root` is the SAME path `resolve_target_roots` computes for a real
    install -- the readiness CLI mode therefore takes --agent/--scope itself
    rather than standing scope-agnostic, since "installed" only means
    something relative to a specific target."""
    if not target_root.is_dir():
        return ReadinessCheck(False, f"no skills directory at {target_root}")
    marker = target_root / CORPUS_MARKER
    if not marker.is_file():
        return ReadinessCheck(
            False, f"no {CORPUS_MARKER} at {target_root} -- skills not installed")
    installed = {
        path.name for path in target_root.iterdir()
        if path.is_dir() and path.name.startswith("constellation-")
    }
    if not installed:
        return ReadinessCheck(
            False, f"{CORPUS_MARKER} present but no constellation-* skill folders under {target_root}")
    if expected_skills is not None:
        missing = sorted(set(expected_skills) - installed)
        if missing:
            return ReadinessCheck(
                False, f"missing skill(s) at {target_root}: {', '.join(missing)}")
    return ReadinessCheck(True, f"{len(installed)} skill(s) installed at {target_root}")


def is_git_tracked(path: Path) -> bool:
    """Whether `path` is tracked in the git repo that contains it, by real
    `git ls-files` membership -- presence on disk is never enough. `cwd` is
    the file's own parent so this resolves correctly even when the file sits
    in a subdirectory of the repo root (the real install layout: .git at the
    project root, settings.json one level down under .claude/). Any git
    failure (not a repo, git missing) reads as untracked, never raises."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            cwd=str(path.parent), capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def check_hooks_shippable(
    target_root: Path,
    *,
    scope: str,
    env: Mapping[str, str],
    specs: Sequence[HookSpec] = (GAUGE_WRITER_SPEC,),
) -> ReadinessCheck:
    """Readiness item 3: hooks wired in a file that ships (environment-scoped).

    Reuses `detect_hook_wiring`/`describe_hook_wiring` rather than re-deriving
    wiring detection. Ready iff the hooks are WIRED AND, for
    `scope == 'project'` only, the settings.json backing that verdict is
    git-tracked (`git ls-files` membership) -- a gitignored
    `settings.local.json` can be WIRED while the tracked `settings.json` is
    not, which must read as NOT ready. `scope == 'user'` has no tracked/
    untracked axis at all (`~/.claude/settings.json` is never part of a repo),
    so WIRED alone is sufficient there -- `settings_path_for_target_root`
    already derives the real runtime path by construction.

    Three outcomes, not two (#539). CANNOT EVALUATE is returned as
    `determinable=False`: the detector's refusal to expand an env token from
    the wrong process is correct and must survive the roll-up intact, instead
    of being reported as a defect on a healthy config."""
    settings_path = settings_path_for_target_root(target_root)
    wiring = detect_hook_wiring(settings_path, env=env, specs=specs)
    # `describe_hook_wiring` renders a standalone bullet; this is embedded
    # after a bullet of its own, so drop the marker rather than print "- - ".
    # A local file cannot make this item READY (#180: at project scope the
    # wiring must be in a file that SHIPS), but staying silent about it invites
    # the reader to conclude the hooks do not run at all, which may be false.
    reason = describe_hook_wiring(wiring).removeprefix("- ") + local_settings_note(target_root)
    if wiring.state == WIRING_UNDETERMINABLE:
        return ReadinessCheck(False, reason, determinable=False)
    if wiring.state != WIRING_WIRED:
        return ReadinessCheck(False, reason)
    if scope == "project" and not is_git_tracked(settings_path):
        return ReadinessCheck(
            False,
            f"{settings_path} is WIRED but not git-tracked (git ls-files) -- an "
            f"untracked settings file (e.g. settings.local.json) never ships with the project",
        )
    return ReadinessCheck(True, f"{_wiring_label(wiring)} WIRED via {settings_path}")


READINESS_ITEMS: tuple[str, ...] = ("engine", "skills", "hooks", "work_area")


# Exit code for the roll-up "some item could not be determined, and nothing
# was found wrong". Distinct from 1 on purpose: a caller that treats any
# nonzero as broken keeps working, and one that wants the distinction can have
# it without us pretending to a verdict we do not hold.
READINESS_EXIT_UNDETERMINABLE = 3


@dataclass(frozen=True)
class ReadinessReport:
    """One agent target's full readiness verdict: the four ReadinessChecks,
    keyed by `READINESS_ITEMS` name. `ready` is true only when all four are."""

    checks: Mapping[str, ReadinessCheck]

    @property
    def ready(self) -> bool:
        return all(check.ready for check in self.checks.values())

    @property
    def verdict(self) -> str:
        """READY, NOT READY, or CANNOT DETERMINE. The last is reached only when
        nothing was found wrong AND at least one item reached no verdict --
        never as a softer way of saying NOT READY."""
        if self.ready:
            return READINESS_READY
        if any(not c.ready and c.determinable for c in self.checks.values()):
            return READINESS_NOT_READY
        return READINESS_UNDETERMINABLE

    @property
    def exit_code(self) -> int:
        return {
            READINESS_READY: 0,
            READINESS_NOT_READY: 1,
            READINESS_UNDETERMINABLE: READINESS_EXIT_UNDETERMINABLE,
        }[self.verdict]


def build_readiness_report(
    *,
    agent: AgentTarget,
    target_root: Path,
    scope: str,
    project_root: Path,
    env: Mapping[str, str],
    expected_skills: Iterable[str] | None = None,
    python: str = sys.executable,
    specs: Sequence[HookSpec] = (GAUGE_WRITER_SPEC,),
) -> ReadinessReport:
    """Combine all four readiness checks for one agent target.

    Hooks are a Claude Code mechanism (`HOOK_CAPABLE_AGENT_NAMES`); for any
    other agent, item 3 is reported READY with an explicit 'not applicable'
    reason rather than silently skipped -- a check the reader cannot tell was
    never run is the exact defect this readiness mode exists to catch."""
    if agent.name in HOOK_CAPABLE_AGENT_NAMES:
        hooks = check_hooks_shippable(target_root, scope=scope, env=env, specs=specs)
    else:
        hooks = ReadinessCheck(
            True, f"not applicable: {agent.name} has no hook mechanism to check")
    return ReadinessReport({
        "engine": check_engine_runnable(python=python),
        "skills": check_skills_installed(target_root, expected_skills=expected_skills),
        "hooks": hooks,
        "work_area": check_work_area_present(project_root),
    })


def describe_readiness_report(agent_name: str, report: ReadinessReport) -> str:
    """One reportable block: a per-item verdict line plus an overall verdict
    line, each carrying the check's own named reason."""
    lines = [f"{agent_name}:"]
    for name in READINESS_ITEMS:
        check = report.checks[name]
        lines.append(f"  - {name}: {check.verdict} -- {check.reason}")
    lines.append(f"  {report.verdict}")
    return "\n".join(lines)


def run_readiness_check(
    args: argparse.Namespace,
    *,
    env: Mapping[str, str],
    cwd: Path,
    out: Callable[[str], object],
) -> int:
    """The `--check-readiness` entry point: answers "is this project set up to
    run Constellation" and refuses (nonzero exit) with a named per-item reason
    when it is not. Report-only -- never repairs, never writes settings.json
    at any scope, under any condition."""
    skills = select_skills(args.skills, discover_skills())
    expected_skills = [skill.install_name for skill in skills]
    project_root = args.project.expanduser() if args.project else cwd

    # --project here names the directory readiness item 4 (work area) checks,
    # independent of where skills install -- decoupled from `resolve_target_roots`,
    # which (correctly, for INSTALL) refuses --project at --scope user because it
    # has no meaning as an install location there. Readiness's own use of
    # --project is a different question, so strip it before resolving targets.
    target_args = args
    if args.scope == "user" and args.project is not None:
        target_args = argparse.Namespace(**{**vars(args), "project": None})
    target_roots = resolve_target_roots(target_args, env, cwd)

    specs = HOOK_SETS[getattr(args, "hooks", DEFAULT_HOOK_SET)]
    verdicts: list[str] = []
    for agent, target_root in target_roots:
        report = build_readiness_report(
            agent=agent, target_root=target_root, scope=args.scope,
            project_root=project_root, env=env, expected_skills=expected_skills,
            specs=specs,
        )
        out(describe_readiness_report(agent.name, report))
        verdicts.append(report.verdict)

    # A definite failure on ANY agent outranks an undeterminable on another:
    # the run is refused, and saying so does not launder the unknown item --
    # its own line still reads CANNOT DETERMINE.
    if READINESS_NOT_READY in verdicts:
        return 1
    if READINESS_UNDETERMINABLE in verdicts:
        return READINESS_EXIT_UNDETERMINABLE
    return 0


def install_skills(
    skills: Sequence[Skill],
    target_root: Path,
    *,
    dry_run: bool,
    force: bool,
    full_set: bool,
    restart_message: str,
    out: Callable[[str], object],
    interpreter: InterpreterResolution | None = None,
) -> None:
    action = "DRY RUN: would install" if dry_run else "Installing"
    out(f"{action} {len(skills)} skill(s) into {target_root}")

    migrate_legacy_initial_cut_destination(
        skills, target_root, force=force, dry_run=dry_run, out=out
    )

    # Set-level wipe only when replacing the FULL set (clears orphaned
    # constellation-* dirs whose upstream skill no longer exists). A --skills
    # subset with --force replaces only the selected skills, via the
    # per-target removal below.
    if force and full_set and not dry_run:
        remove_existing_constellation_set(target_root)

    # Resolved lazily, at most once, and reused for every skill in THIS call --
    # never a module-level global (a hidden global risks one pytest-process test
    # reading a stale value left by an earlier test). A caller installing across
    # multiple target roots in one run (e.g. `--agent all`) should resolve once
    # itself and pass `interpreter` explicitly so the whole run shares one probe.
    resolved_interpreter = interpreter

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
        if resolved_interpreter is None:
            resolved_interpreter = resolve_interpreter()
        rewrite_installed_skill_paths(target, skill, resolved_interpreter)
        for script in skill.required_scripts:
            # Destination is flat for every script regardless of where its source
            # lives -- that flatness is what keeps a script and its runtime
            # companions in one directory.
            script_target = target / "scripts" / script
            script_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(script_source_path(script, REPO_ROOT / "scripts"), script_target)
        for reference in skill.required_references:
            reference_target = target / "references" / reference
            reference_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SHARED_REFERENCE_ROOT / reference, reference_target)

    if not dry_run:
        # Stamp the installed root with a CORPUS.json provenance marker, scoped to
        # the skills this run wrote so foreign siblings in a shared root never enter
        # the id. This makes every install (user + project scope) a verifiable build
        # artifact that check_corpus_freshness.py can later date against upstream.
        corpus_id = write_corpus_marker(
            target_root,
            _source_commit(),
            names=[skill.install_name for skill in skills],
        )
        out(f"- {CORPUS_MARKER}: {corpus_id}")
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


# --------------------------------------------------------------------------- #
# corpus provenance — sha256 id + source_commit + date (the install lockfile)
# --------------------------------------------------------------------------- #
# One CORPUS.json per installed skills root stamps *which* corpus a project (or
# user) is carrying: a content hash for integrity, the constellation commit it was
# built from for staleness checks (check_corpus_freshness.py), and the build date.
# The eval harness imports these same primitives, but its own stable_corpus_id()
# (run_skill_eval.py) path-normalizes the id (#153) so a byte-identical corpus
# hashes the same across install paths -- an eval run's id and a real install's
# compute_corpus_id() are therefore DELIBERATELY not identical when install paths
# differ; only the FORMAT and file-selection rules are shared. Provenance travels
# with the copy; a project install is a verifiable build artifact, not an
# unattributable fork.
CORPUS_MARKER = "CORPUS.json"


def compute_corpus_id(skills_dir, names: Iterable[str] | None = None) -> str:
    """Content id of an installed skill tree: ``"sha256:" + sha256`` over the
    sorted ``(rel_posix_path, _hash_file(p))`` pairs of every file. PURE.

    ``names`` restricts the hash to those top-level subdirectories (the skills a
    given install actually wrote), so foreign siblings already present in a shared
    skills root — a user's own skills under ``~/.claude/skills`` — never perturb
    the constellation corpus id. ``None`` hashes the whole tree, which is what the
    eval harness wants for its clean temp_install. The marker file itself is always
    excluded so writing it cannot change the id it records.
    """
    skills_dir = Path(skills_dir)
    roots = (
        [skills_dir / n for n in names]
        if names is not None
        else [skills_dir]
    )
    pairs: list[tuple[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.name == CORPUS_MARKER:
                continue
            # Generated bytecode appears the first time a bundled script runs
            # (e.g. the checklist engine inside an eval workspace); it is not
            # corpus content and must not perturb the id.
            if path.suffix == ".pyc" or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(skills_dir).as_posix()
            pairs.append((rel, _hash_file(path)))
    digest = hashlib.sha256()
    for rel, file_hash in sorted(pairs):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def write_corpus_marker(
    skills_dir,
    source_commit: str,
    *,
    names: Iterable[str] | None = None,
    build_date: str | None = None,
) -> str:
    """Compute the corpus id and write ``<skills_dir>/CORPUS.json``. Returns the id.

    The marker carries ``corpus_id`` (content hash), ``source_commit`` (the
    constellation commit this corpus was built from) and ``date`` (UTC build date).
    ``build_date`` is injectable for deterministic tests; it defaults to today.
    ``names`` is forwarded to :func:`compute_corpus_id`.
    """
    skills_dir = Path(skills_dir)
    corpus_id = compute_corpus_id(skills_dir, names)
    marker = {
        "corpus_id": corpus_id,
        "source_commit": source_commit,
        "date": build_date if build_date is not None else date.today().isoformat(),
    }
    (skills_dir / CORPUS_MARKER).write_text(
        json.dumps(marker, indent=2) + "\n", encoding="utf-8"
    )
    return corpus_id


def assert_corpus(run_skills_dir, expected_id: str) -> bool:
    """Whether a copied skill tree hashes to ``expected_id`` (whole-tree). A
    mismatch fences an eval run (corpus_mismatch), never silently counts."""
    return compute_corpus_id(run_skills_dir) == expected_id


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
        "--wire-hooks",
        action="store_true",
        help=(
            "Add the Context Governor PostToolUse hook entry to the target scope's "
            "settings.json, additively. WITHOUT this flag the installer only reads and "
            "reports the wiring state and never writes or creates that file."
        ),
    )
    parser.add_argument(
        "--hooks",
        choices=sorted(HOOK_SETS),
        default=DEFAULT_HOOK_SET,
        help=(
            "Which hooks --wire-hooks writes and which hooks are reported on: "
            "'governor' (default) is the Context Governor's PostToolUse gauge writer "
            "alone -- exactly what --wire-hooks has always written; 'rail' is the three "
            "spine_rail.py events (Stop, SessionStart, PostToolUse); 'all' is all four. "
            "Also applies to --check-readiness."
        ),
    )
    parser.add_argument(
        "--hooks-from",
        choices=HOOKS_FROM_CHOICES,
        default=HOOKS_FROM_INSTALLED,
        help=(
            "Where the wired commands point. 'installed' (default) points at the "
            "installed skill copy. 'source' points at THIS checkout's own "
            "scripts/hooks/, for developing the hooks themselves -- it writes "
            f"{LOCAL_SETTINGS_FILENAME} rather than {SETTINGS_FILENAME}, because a "
            "source-tree command is correct on the machine that wrote it and no other."
        ),
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help=(
            "Seed the project template baseline + manifest without installing skills. "
            "For projects that consume user-scope skills but need template versioning. "
            "Requires --scope project."
        ),
    )
    parser.add_argument(
        "--check-readiness",
        action="store_true",
        help=(
            "Report whether this project/environment is ready to run Constellation and exit "
            "nonzero with a named reason for each failing item. Report-only: never repairs "
            "anything and never writes settings.json at any scope."
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

        if args.check_readiness:
            # Refuse EARLY, before any check runs: this mode never writes
            # settings.json under any condition, so pairing it with a flag whose
            # whole point is writing one is a contradiction to reject, not honor.
            if args.wire_hooks:
                raise InstallError(
                    "--check-readiness cannot be combined with --wire-hooks -- "
                    "readiness reports only and never writes settings.json"
                )
            if args.baseline_only:
                raise InstallError(
                    "--check-readiness cannot be combined with --baseline-only"
                )
            if args.hooks_from != HOOKS_FROM_INSTALLED:
                # --hooks-from only affects what gets WRITTEN, and this mode
                # writes nothing. Accepting it silently would imply it changed
                # what was checked. (--hooks DOES apply here: it selects which
                # hooks are reported on.)
                raise InstallError(
                    "--check-readiness cannot be combined with --hooks-from -- readiness "
                    "reports only and never writes a settings file, so there is nothing "
                    "for it to change. Use --hooks to choose which hooks are reported on."
                )
            return run_readiness_check(args, env=runtime_env, cwd=runtime_cwd, out=out)

        skills = select_skills(args.skills, discover_skills())
        validate_required_scripts(skills)
        validate_required_references(skills)

        if args.wire_hooks:
            # Refuse EARLY, before anything is written. An installer that
            # declines to wire a hook it cannot locate is correct -- and this is
            # not a fail-open violation: `decision:fail-open-is-inviolable`
            # governs hook EXECUTION paths, not installer preconditions.
            if args.baseline_only:
                raise InstallError(
                    "--wire-hooks cannot be combined with --baseline-only (which installs "
                    "no skills, so there would be no hook to point at)"
                )
            if (
                args.hooks_from == HOOKS_FROM_INSTALLED
                and HOOK_OWNER_SKILL not in {skill.source_name for skill in skills}
            ):
                raise InstallError(
                    f"--wire-hooks needs the '{HOOK_OWNER_SKILL}' skill -- the canonical owner "
                    f"of {GAUGE_WRITER_HOOK_SCRIPT} -- and this install does not include it. "
                    f"Refusing to wire a hook it cannot locate rather than silently pointing "
                    f"at some other skill's copy."
                )
            if args.hooks_from == HOOKS_FROM_SOURCE:
                # Source wiring points at THIS checkout, so the check is about
                # the checkout, not about what is being installed.
                missing_sources = [
                    str(source_hook_path(spec.script))
                    for spec in HOOK_SETS[args.hooks]
                    if not source_hook_path(spec.script).is_file()
                ]
                if missing_sources:
                    raise InstallError(
                        f"--wire-hooks --hooks-from source: this checkout has no hook "
                        f"script(s) at {', '.join(missing_sources)}. Source wiring only "
                        f"means anything in a checkout that owns scripts/hooks/."
                    )

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
        if args.wire_hooks and not any(
            agent.name in HOOK_CAPABLE_AGENT_NAMES for agent, _ in target_roots
        ):
            raise InstallError(
                f"--wire-hooks wires Claude Code hooks; --agent {args.agent} has no "
                f"{SETTINGS_FILENAME} hook mechanism to wire into."
            )
        # Resolve ONCE for the whole process here (not per target root / agent) so
        # a `--agent all` run still probes the host exactly once, not once per
        # agent target. A --wire-hooks dry run still probes, so it can PRINT the
        # exact command string it would have written.
        interpreter = None if (args.dry_run and not args.wire_hooks) else resolve_interpreter()
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
                interpreter=interpreter,
            )
            if agent.name in HOOK_CAPABLE_AGENT_NAMES:
                if args.wire_hooks:
                    wire_hooks(
                        target_root,
                        interpreter=interpreter,
                        dry_run=args.dry_run,
                        scope=args.scope,
                        out=out,
                        specs=HOOK_SETS[args.hooks],
                        hooks_from=args.hooks_from,
                    )
                # Always-on and read-only, with or without the flag. Runs AFTER
                # the install so a fresh install that just placed the hook flips
                # a previously-stale entry to wired.
                report_hook_wiring(
                    target_root, env=runtime_env, out=out, specs=HOOK_SETS[args.hooks])
        if args.scope == "project" and not args.dry_run and not args.dest:
            project_root = args.project.expanduser() if args.project else runtime_cwd
            seeded = write_template_baselines(skills, project_root, out=out)
            write_template_working_copies(skills, project_root, only=seeded, out=out)
    except InstallError as exc:
        parser.exit(2, f"error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
