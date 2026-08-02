from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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


SKILL_SCRIPT_BUNDLES: dict[str, tuple[str, ...]] = {
    "admiral": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "apply_lessons_delta.py", "verify_lessons_applied.py", "verify_worktree_isolation.py", "agent_work_root.py"),
    "lessons-auditor": ("checklist_engine.py",),
    "charter": ("checklist_engine.py",),
    # map_orient.py is invoked by COMMANDER_SPINE.template.json as a command
    # postcondition at BOTH the context step (verify-orientation) and the plan
    # step (verify-frame), so it must travel with the skill that serves that
    # template -- an uninstalled script would surface as a confusing gate failure
    # mid-run. It loads no sibling module at runtime (stdlib only), so it has no
    # SCRIPT_RUNTIME_COMPANIONS entry; that is a checked fact, not an omission --
    # tests/test_install_constellation.py pins companions against actual dynamic
    # loads.
    "commander": ("checklist_engine.py", "init_work_area.py", "verify_agent_feedback.py", "verify_state_note.py", "run_crew.py", "recover_crews.py", "apply_lessons_delta.py", "verify_lessons_applied.py", "verify_worktree_isolation.py", "agent_work_root.py", "map_orient.py"),
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
    "explorer": ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py"),
    "curator": ("curate_corpus.py",),
    "to-issues": ("verify_spec_confirmed.py", "verify_issue_set.py", "file_issue_set.py"),
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
    "curator": _GLOBAL_EVERYONE + ("skill-goodness.md",),
    "to-issues": _GLOBAL_ORCHESTRATOR,
    "diagnose": _GLOBAL_ORCHESTRATOR,
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


def rewrite_installed_skill_paths(
    target: Path, skill: Skill, interpreter: InterpreterResolution
) -> None:
    # Rewrite the interpreter prefix FIRST, before the skill-dir tokens consume the
    # trailing `<`: the replacement preserves the `<` so `<…-skill-dir>` still resolves.
    replacements = {
        "python <": f"{interpreter.interpreter} <",
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
GAUGE_WRITER_HOOK_SCRIPT = "gauge_writer_hook.py"
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

# Hooks are a Claude Code mechanism. No other supported agent reads a
# `hooks.PostToolUse` array, so detecting -- let alone writing -- one under
# ~/.codex/ would be reporting on a file nothing ever reads.
HOOK_CAPABLE_AGENT_NAMES = frozenset({AGENT_TARGETS["claude"].name})

WIRING_WIRED = "wired"
WIRING_STALE = "stale"
WIRING_UNWIRED = "unwired"
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

_ESCAPED_HOOK_SCRIPT = re.escape(GAUGE_WRITER_HOOK_SCRIPT)
# Quoted form first: an installed path on Windows can contain spaces, so the
# quotes -- not whitespace -- are what delimit it.
_HOOK_SCRIPT_PATH_RE = re.compile(
    rf'"([^"]*{_ESCAPED_HOOK_SCRIPT})"|(\S*{_ESCAPED_HOOK_SCRIPT})'
)
_ENV_TOKEN_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|%([A-Za-z_][A-Za-z0-9_]*)%")


@dataclass(frozen=True)
class HookWiring:
    """One read-only verdict about one settings.json."""

    state: str
    settings_path: Path
    settings_exists: bool
    resolved: tuple[str, ...] = ()    # governor commands whose script IS on disk
    unresolved: tuple[str, ...] = ()  # governor commands that resolve to nothing
    # governor commands carrying an env token we decline to evaluate -- neither
    # confirmed nor condemned, because from here they are genuinely unknowable
    undeterminable: tuple[str, ...] = ()
    error: str | None = None


def settings_path_for_target_root(target_root: Path) -> Path:
    """The settings.json governing the agent config dir this install writes
    into: `~/.claude/skills` -> `~/.claude/settings.json`, and at project scope
    `<project>/.claude/skills` -> `<project>/.claude/settings.json`.

    Derived from the RESOLVED target root rather than re-derived from scope, so
    a `--dest` install -- which every test in this repo uses -- can never reach
    past its own tree into the developer's real ~/.claude/settings.json."""
    return target_root.parent / SETTINGS_FILENAME


def installed_gauge_writer_path(target_root: Path) -> Path:
    return target_root / HOOK_OWNER_INSTALL_NAME / "scripts" / GAUGE_WRITER_HOOK_SCRIPT


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


def extract_hook_script_path(command: str) -> str | None:
    """The gauge-writer script path a hook `command` string invokes, or None
    when the command is not a Context Governor entry at all."""
    match = _HOOK_SCRIPT_PATH_RE.search(command)
    if match is None:
        return None
    return match.group(1) or match.group(2)


def governor_hook_commands(settings: object) -> list[str]:
    """Every PostToolUse `command` string that invokes a gauge writer hook,
    flattened across matcher blocks. Deliberately tolerant of shapes it does
    not expect: an odd settings.json is something to REPORT, never something to
    raise on in the middle of an otherwise-fine install."""
    commands: list[str] = []
    if not isinstance(settings, dict):
        return commands
    hooks = settings.get("hooks")
    entries = hooks.get(HOOK_EVENT) if isinstance(hooks, dict) else None
    if not isinstance(entries, list):
        return commands
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for hook in entry.get("hooks") or []:
            if not isinstance(hook, dict):
                continue
            command = hook.get("command")
            if isinstance(command, str) and extract_hook_script_path(command):
                commands.append(command)
    return commands


def detect_hook_wiring(settings_path: Path, *, env: Mapping[str, str]) -> HookWiring:
    """Three-state and READ-ONLY -- opens nothing for writing and creates
    nothing.

    Classification is by RESOLVING each entry's script path against the
    filesystem, never by string-matching the command. Under a string match a
    moved, renamed, or uninstalled tree still reads as `wired`, which is exactly
    the reassuring-failure shape this detector exists to prevent."""
    if not settings_path.is_file():
        return HookWiring(WIRING_UNWIRED, settings_path, False)
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return HookWiring(WIRING_UNREADABLE, settings_path, True, error=str(exc))

    resolved: list[str] = []
    unresolved: list[str] = []
    undeterminable: list[str] = []
    for command in governor_hook_commands(settings):
        raw = extract_hook_script_path(command) or ""
        expanded = _expand_env_tokens(raw, env)
        if _ENV_TOKEN_RE.search(expanded):
            # An env token we will not evaluate survives. Resolving it against
            # the installer's own environment would answer a question about the
            # WRONG process, so we decline rather than guess in either direction.
            undeterminable.append(command)
            continue
        (resolved if Path(expanded).is_file() else unresolved).append(command)

    if resolved:
        state = WIRING_WIRED
    elif undeterminable:
        # Ahead of STALE deliberately: "I cannot tell" must not be reported as
        # "definitely broken" any more than as "definitely fine".
        state = WIRING_UNDETERMINABLE
    elif unresolved:
        state = WIRING_STALE
    else:
        state = WIRING_UNWIRED
    return HookWiring(
        state, settings_path, True, tuple(resolved), tuple(unresolved), tuple(undeterminable)
    )


def describe_hook_wiring(wiring: HookWiring) -> str:
    """One reportable line. ASCII only -- this goes to a Windows console."""
    if wiring.state == WIRING_WIRED:
        paths = ", ".join(sorted(
            {extract_hook_script_path(command) or command for command in wiring.resolved}
        ))
        return f"- Context Governor hooks: WIRED -- {paths}"
    if wiring.state == WIRING_STALE:
        return (
            f"- Context Governor hooks: STALE -- {len(wiring.unresolved)} {HOOK_EVENT} "
            f"entry(ies) in {wiring.settings_path} name a {GAUGE_WRITER_HOOK_SCRIPT} that "
            f"is not on disk, so the hook never runs and nothing else can tell you that: "
            f"{'; '.join(wiring.unresolved)}. Re-run with --wire-hooks to add a correct "
            f"entry; the stale one is left in place for you to remove."
        )
    if wiring.state == WIRING_UNDETERMINABLE:
        return (
            f"- Context Governor hooks: CANNOT EVALUATE -- {len(wiring.undeterminable)} "
            f"{HOOK_EVENT} entry(ies) in {wiring.settings_path} name the script through an "
            f"environment variable this installer will not expand, because it would be "
            f"expanded in the WRONG process (this one, not the future hook's): "
            f"{'; '.join(wiring.undeterminable)}. Whether the hook fires cannot be "
            f"determined from here -- it is neither confirmed nor condemned."
        )
    if wiring.state == WIRING_UNREADABLE:
        return (
            f"- Context Governor hooks: UNREADABLE -- could not parse "
            f"{wiring.settings_path} ({wiring.error}), so the wiring state is unknown. "
            f"Nothing was read past this point and nothing was changed."
        )
    where = wiring.settings_path if wiring.settings_exists else f"{wiring.settings_path} (absent)"
    return (
        f"- Context Governor hooks: UNWIRED -- no {HOOK_EVENT} entry for "
        f"{GAUGE_WRITER_HOOK_SCRIPT} in {where}, so the Context Governor never fires. "
        f"Re-run with --wire-hooks to add one; nothing is written without that flag."
    )


def report_hook_wiring(
    target_root: Path, *, env: Mapping[str, str], out: Callable[[str], object]
) -> HookWiring:
    wiring = detect_hook_wiring(settings_path_for_target_root(target_root), env=env)
    out(describe_hook_wiring(wiring))
    return wiring


def build_hook_command(script_path: Path, interpreter: str) -> str:
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
    never re-probed here, never hardcoded."""
    return f'{interpreter} "{script_path.as_posix()}"'


def build_hook_entry(command: str) -> dict:
    return {
        "matcher": HOOK_MATCHER,
        "hooks": [{"type": "command", "command": command, "timeout": HOOK_TIMEOUT}],
    }


def add_hook_entry(settings: dict, entry: dict) -> bool:
    """Append `entry` as a SIBLING in `hooks.PostToolUse`, in place. Never nests
    inside an existing matcher block, never reorders what is already there, and
    never removes anything -- including a stale governor entry, which is
    reported rather than silently rewritten (no self-healing, by design).

    Returns False when an identical command is already present."""
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(f"--wire-hooks: 'hooks' in settings is not an object: {type(hooks).__name__}")
    entries = hooks.setdefault(HOOK_EVENT, [])
    if not isinstance(entries, list):
        raise InstallError(
            f"--wire-hooks: 'hooks.{HOOK_EVENT}' in settings is not an array: {type(entries).__name__}"
        )
    if entry["hooks"][0]["command"] in governor_hook_commands(settings):
        return False
    entries.append(entry)
    return True


def wire_hooks(
    target_root: Path,
    *,
    interpreter: str,
    dry_run: bool,
    scope: str,
    out: Callable[[str], object],
) -> None:
    """The ONE path on which this installer writes a settings.json. Reached only
    from the explicit `--wire-hooks` opt-in (`decision:opt-in-wiring-only`, a
    human ruling), and still a no-op under `--dry-run`."""
    script = installed_gauge_writer_path(target_root)
    if not dry_run and not script.is_file():
        raise InstallError(
            f"--wire-hooks: no {GAUGE_WRITER_HOOK_SCRIPT} at {script}. Refusing to wire a "
            f"path with no file behind it, and refusing to point at another skill's copy."
        )

    command = build_hook_command(script, interpreter)
    settings_path = settings_path_for_target_root(target_root)

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

    added = add_hook_entry(settings, build_hook_entry(command))

    if dry_run:
        # `dry_run` is pre-existing plumbing and this is a NEW write path, so the
        # bail-out is placed after everything that can refuse and before anything
        # that can write -- the mutation above happened only in memory.
        verb = "add" if added else "leave unchanged (already present)"
        out(f"- DRY RUN: would {verb} the {HOOK_EVENT} entry in {settings_path}")
        out(f"- DRY RUN: would write command: {command}")
        out("- DRY RUN: settings.json NOT written")
        return

    if added:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        out(f"- wired the Context Governor {HOOK_EVENT} hook into {settings_path}")
        out(f"  command: {command}")
    else:
        out(f"- Context Governor {HOOK_EVENT} hook already present in {settings_path}; unchanged")

    if scope == "project":
        # The absolute path is the accepted cost of rejecting a project-relative
        # form, and it embeds the user's home directory AND user name. A
        # project-scope settings.json is committable, so say so out loud rather
        # than letting committing it be the path of least resistance.
        out(
            f"- NOTE: this entry embeds an absolute path containing your user name, and it "
            f"is machine-specific. A project-scope {SETTINGS_FILENAME} is committable -- "
            f"prefer --scope user, or keep {settings_path} out of version control."
        )


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
            if HOOK_OWNER_SKILL not in {skill.source_name for skill in skills}:
                raise InstallError(
                    f"--wire-hooks needs the '{HOOK_OWNER_SKILL}' skill -- the canonical owner "
                    f"of {GAUGE_WRITER_HOOK_SCRIPT} -- and this install does not include it. "
                    f"Refusing to wire a hook it cannot locate rather than silently pointing "
                    f"at some other skill's copy."
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
                        interpreter=interpreter.interpreter,
                        dry_run=args.dry_run,
                        scope=args.scope,
                        out=out,
                    )
                # Always-on and read-only, with or without the flag. Runs AFTER
                # the install so a fresh install that just placed the hook flips
                # a previously-stale entry to wired.
                report_hook_wiring(target_root, env=runtime_env, out=out)
        if args.scope == "project" and not args.dry_run and not args.dest:
            project_root = args.project.expanduser() if args.project else runtime_cwd
            seeded = write_template_baselines(skills, project_root, out=out)
            write_template_working_copies(skills, project_root, only=seeded, out=out)
    except InstallError as exc:
        parser.exit(2, f"error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
