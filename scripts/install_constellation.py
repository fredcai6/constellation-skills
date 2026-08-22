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
SHARED_TEMPLATE_ROOT = SHARED_REFERENCE_ROOT / "templates"


class InstallError(Exception):
    """Raised for clear, user-correctable installer failures."""


@dataclass(frozen=True)
class Skill:
    source_name: str
    install_name: str
    source_path: Path
    required_scripts: tuple[str, ...]
    required_references: tuple[str, ...]
    required_templates: tuple[str, ...] = ()


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
    #
    # gauge_reader.py joins it for #600: the hook now loads the reader to reach
    # `owner_key`, the ONE definition of the name a gauge file carries, because
    # the writer and the engine compute that name in separate processes and must
    # not drift. Same silent-failure shape as the pair above, but WORSE than a
    # no-op if it splits: the load fails open to no owner, so the hook would
    # write the unowned `gauge.json` while an engine holding a lease reads
    # `gauge-<owner>.json` -- a governor that is dark rather than merely
    # inert. (`checklist_engine.py` above already carries the same companion for
    # its own load; both entries are needed, since a bundle may carry either
    # script without the other.)
    "gauge_writer_hook.py": ("spine_rail.py", "gauge_reader.py"),
    # run_crew.py: `sys.path.insert(0, <own parent>)` + a plain top-level
    # `import install_constellation` (#539, for `assert_shell_safe_command`).
    # Exactly the #305 mechanism this dict exists to catch -- and it did not,
    # because the guard that pins this dict against reality was keyed to the
    # literal `"checklist_engine.py"` and watched no other script (#559 pass
    # 3). No bundle carrying `run_crew.py` shipped this companion, so
    # Commander and Explorer, installed, raised `ModuleNotFoundError` at
    # import -- before argparse ever ran -- and could launch no crew at all.
    "run_crew.py": ("install_constellation.py",),
    # apply_episode_delta.py._guard() -> Path(__file__).parent /
    # "verify_episode_observations.py" (episode-guard-at-write): the writer imports the
    # closeout suite's own instruction-shaped-statement guard so a write-time rejection
    # can never drift from the read-time one. The guard module in turn resolves
    # query_episodes.py the same lazy way for its OWN scan_store()/query() -- unused by
    # the writer (it calls only triggers_for()/EXCEPTIONS, never scan_store()), but the
    # companion guard below walks reachability statically, not by what is actually
    # called, so it has to ship too or this entry alone would still fail the guard.
    # This is one of the four routes the write-side bundle comment (SKILL_SCRIPT_BUNDLES,
    # below) already named for query_episodes.py travelling with the writer: "a future
    # bundled script that imports query_episodes would drag it along automatically."
    "apply_episode_delta.py": ("verify_episode_observations.py", "query_episodes.py"),
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
    # code_map_precommit.py bundles no skill (no `required_scripts` names it):
    # it is only ever invoked in place, resolved dynamically at git-hook run
    # time (see its own docstring and `install_git_precommit_hook` above).
    # Declared here anyway so `scripts/hooks/` stays fully accounted for --
    # `ScriptsPackageBundlingTests` requires every script under a subdirectory
    # be either a declared non-installable package or fully present in this
    # dict, and a plain module that is neither would fail that gate silently
    # for the wrong reason (looking unbundled by omission, not by design).
    "code_map_precommit.py": "hooks",
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

# THE ONE SHIPPING UNIT THAT IS NOT A SKILL (#639).
#
# `discover_skills` refuses a directory under `skills/` that has no `SKILL.md`,
# so before this constant the only way to ship a bundle of scripts was to dress
# it as a skill an agent could load. `constellation-workbench` was that dress:
# vestigial as a skill, load-bearing as a bundle, and named for the wrapper
# rather than the cargo -- so anyone reading `skills/workbench/` to decide
# whether it still earned its place measured inert files and concluded it was
# dead. It was not: deleting it unwired the Stop hook, the SessionStart hook,
# the gauge writer and the engine path on every installed machine.
#
# This unit has no `SKILL.md`, never appears in an agent's skill list, and is
# installed on every run regardless of `--skills`, because the hook wiring on a
# consuming machine points into it and a subset install must not leave that
# wiring dangling.
#
# ITS SOURCES DO NOT MOVE, deliberately. The install DESTINATION is what #639 is
# about; `SCRIPT_SOURCE_SUBDIRS` above already proves source location and
# install location are independent, and `AGENT_GUIDE.md`'s layout table names
# `scripts/` as where shared machinery lives. Relocating the hook pair would
# additionally break this repo's own `.claude/settings.json`, 28 test
# references, and the frozen-source-layout decision recorded above -- all to
# move files the installer can already reach where they sit.
ENGINE_BUNDLE_INSTALL_NAME = "constellation-engine"

# Exactly what `constellation-workbench` shipped before #639: the engine, the
# gauge writer hook, and the transitive runtime closure of both. Expanded from
# the same two roots through the same companion table, so the cargo cannot drift
# from what the hooks and the door actually need.
ENGINE_BUNDLE_ROOTS: tuple[str, ...] = ("checklist_engine.py", "gauge_writer_hook.py")
ENGINE_BUNDLE_SCRIPTS: tuple[str, ...] = expand_script_bundle(ENGINE_BUNDLE_ROOTS)
# Global doctrine buckets (single source: skills/_shared/), bundled into each skill's
# references/ at install exactly as the scripts above are bundled into scripts/. The
# audience Venn is enforced by which buckets a skill carries: everyone-global is shared
# by all; the tier buckets reach only their tier. A role reads its own bucket(s) at the
# checklist context-read step; the project supplies thin local deltas under docs/agents/.
# Shared TEMPLATES, bundled into each skill's templates/ exactly as the shared
# references are bundled into its references/ (#639). Before this table only
# references had a shared-bundling mechanism: a skill's templates arrived solely
# through the wholesale copytree of its own directory, so a template two skills
# both needed had to live in a third skill they could point at -- which is one of
# the things that kept `workbench` alive as a wrapper after its teaching was cut.
# The alternative was a copy per consumer, and two copies of a file that must not
# drift is the failure `_shared/` exists to prevent.
SKILL_TEMPLATE_BUNDLES: dict[str, tuple[str, ...]] = {
    # The crash-resume state note: both spine templates name it as the fallback
    # when a project carries no .agent-work/templates/ overlay, and
    # verify_state_note.py is the gate that reads what it produces.
    "admiral": ("STATE_NOTE.template.md", "CONSTELLATION_FEEDBACK.template.md"),
    "commander": ("STATE_NOTE.template.md", "CONSTELLATION_FEEDBACK.template.md"),
    # commander-delegated cites the feedback template but never stands up a work
    # area (the Admiral does it), so it needs no state note.
    "commander-delegated": ("CONSTELLATION_FEEDBACK.template.md",),
}

# `checklist-engine.md` is in every tuple because `global-everyone.md` -- which
# every skill carries -- cites it by name. Before #639 it lived under the
# `workbench` skill and every citation was a CROSS-PACKAGE pointer that only
# resolved if that skill happened to be installed; bundled here it is a local
# `references/checklist-engine.md` in each skill that names it.
_GLOBAL_EVERYONE = ("global-everyone.md", "windows.md", "checklist-engine.md")
_GLOBAL_ORCHESTRATOR = ("global-everyone.md", "global-orchestrator.md", "design-it-twice-brief.md", "windows.md", "checklist-engine.md")
_GLOBAL_CREW = ("global-everyone.md", "global-crew.md", "windows.md", "checklist-engine.md")
_GLOBAL_ALL_TIERS = ("global-everyone.md", "global-orchestrator.md", "global-crew.md", "windows.md", "checklist-engine.md")
SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {
    # admiral and commander stand up a worktree/work area themselves (issue #610);
    # commander-delegated never does (the Admiral does it for them), so it stays on
    # plain _GLOBAL_ORCHESTRATOR like every other consumer of that shared tuple.
    "admiral": _GLOBAL_ORCHESTRATOR + ("stand-up-work-area.md",),
    "commander-delegated": _GLOBAL_ORCHESTRATOR,
    "charter": _GLOBAL_ALL_TIERS,  # the baseline Charter elicits project deltas from
    "commander": _GLOBAL_ORCHESTRATOR + ("stand-up-work-area.md", "status-model.md"),
    "interrogator": _GLOBAL_EVERYONE,
    "cartographer": _GLOBAL_ORCHESTRATOR,
    "docent": _GLOBAL_ORCHESTRATOR,
    "scout": _GLOBAL_ORCHESTRATOR,
    "implementer": _GLOBAL_CREW + ("status-model.md",),
    "reviewer": _GLOBAL_CREW + ("status-model.md",),
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
                required_templates=SKILL_TEMPLATE_BUNDLES.get(source_path.name, ()),
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


def validate_required_templates(
    skills: Iterable[Skill], shared_root: Path = SHARED_TEMPLATE_ROOT
) -> None:
    missing: list[str] = []
    for skill in skills:
        for template in skill.required_templates:
            if not (shared_root / template).is_file():
                missing.append(f"{skill.install_name}: {shared_root / template}")
    if missing:
        raise InstallError(f"required template(s) missing: {'; '.join(missing)}")


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


# THERE IS NO os.name FALLBACK, by owner ruling. There used to be a
# `_platform_interpreter()` returning `py` on Windows and `python3` elsewhere,
# reached only when every candidate below had been probed and rejected. Read
# those two facts together and the fallback cannot be right by construction:
# its answer is always drawn from the set that was just disproved. On Windows
# it returned `py`, already probed, already failed; on POSIX `python3`, the
# same. It was never a safety net -- it was a guaranteed-wrong value that only
# ran in worlds where its own answer had been falsified, and it stamped that
# value into every installed skill body so the failure surfaced later,
# somewhere else, with no trace back to the cause.
#
# Measured on the owner's Windows host: `py` resolves to an extensionless
# `#!/bin/sh` wrapper PowerShell cannot execute, and neither `python3` nor
# `python` is on PATH. All three candidates fail, and the old fallback stamped
# `py` -- the exact thing just proven unlaunchable.
#
# `resolve_interpreter` therefore RAISES when nothing answers. See #539.
INTERPRETER_CANDIDATES: tuple[str, ...] = ("py", "python3", "python")
DEFAULT_INTERPRETER_PROBE_TIMEOUT = 5.0  # seconds; bounds a hung/misregistered `py` launcher


@dataclass(frozen=True)
class InterpreterResolution:
    """The interpreter resolved for ONE install run, plus how it was resolved --
    carried into both the text-rewrite and the per-skill sidecar so a consumer can
    tell a genuinely-probed host from the os.name guess."""

    interpreter: str
    candidates: tuple[str, ...]
    # Always "probe" for anything `resolve_interpreter` produces -- the
    # os.name fallback that used to write "os-default-fallback" is gone (see
    # INTERPRETER_CANDIDATES above). The field STAYS because
    # scripts/verify_installed_bundles.py reconstructs this dataclass from an
    # installed `interpreter.json` sidecar, and a bundle installed by an older
    # version legitimately still carries "os-default-fallback" on disk. Reading
    # that back is exactly how a consumer learns a bundle was built from the
    # disproved guess and should be reinstalled.
    resolved_via: str  # "probe" | (historical, from an old sidecar) "os-default-fallback"

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


def no_interpreter_message(candidates: Sequence[str]) -> str:
    """The refusal text, as one definition, so the CLI error and the readiness
    report cannot describe the same host condition differently."""
    return (
        f"no working Python interpreter found on this host. Tried "
        f"{', '.join(candidates)} -- each was launched as a real "
        f"`<name> --version` subprocess and none exited 0 (a missing command, a "
        f"non-zero exit and a timeout all count as failing). Constellation stamps "
        f"one of these names into installed skill bodies and hook commands, so "
        f"there is no correct value to write. Put a working Python on PATH under "
        f"one of those names -- on Windows the python.org installer provides `py` "
        f"and `python`; on POSIX `python3` is the PEP 394 guarantee -- then re-run."
    )


def resolve_interpreter(
    *,
    candidates: Sequence[str] = INTERPRETER_CANDIDATES,
    timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT,
) -> InterpreterResolution:
    """Resolve the interpreter to stamp into installed skill bodies for ONE
    install run: probe the host once. Call this ONCE per run and thread the
    result through -- never re-probe per skill. Caching prevents INTRA-run
    drift only; cross-run determinism (#197's `stable_corpus_id`, which
    compares two separate install invocations) rests on the probe being
    naturally stable given a static host PATH.

    RAISES `InstallError` when no candidate answers. This function used to
    promise "never raises" and fall back to an os.name guess; that contract is
    gone by owner ruling (#539), because the guess is drawn from the set the
    probe just disproved and so cannot be right on any platform. Refusing here
    keeps the failure at its cause instead of stamping an unlaunchable name
    into every installed bundle and surfacing it later, somewhere else.

    Callers that must REPORT this condition rather than abort on it -- the
    `--check-readiness` mode -- call `probe_host_interpreter` directly and get
    `None`, which is the same measurement without the control flow."""
    probed = probe_host_interpreter(candidates=candidates, timeout=timeout)
    if probed is None:
        raise InstallError(no_interpreter_message(candidates))
    return InterpreterResolution(probed, tuple(candidates), "probe")


# --------------------------------------------------------------------------- #
# .mcp.json interpreter wiring (M2 g3-rework, widened g4-repair) -- CLI-entry-point-only
# --------------------------------------------------------------------------- #
# `.mcp.json` is git-tracked (like settings.json, #539). #539 also records the
# rule that governs it: a tracked config that code also reads directly cannot
# hold an unresolvable value, because anything that consumes the file before
# wiring runs -- a test, a fresh clone, a harness reading `.mcp.json` at
# session start -- sees it verbatim. So the committed file carries a real,
# launchable bare interpreter name (`python3` here; the PEP 394 guarantee on
# POSIX) rather than staying on `MCP_INTERPRETER_PLACEHOLDER` forever, and
# wiring's job is to rewrite that bare name -- or the placeholder, for a
# config that has not been through this repo's own commit -- to the
# interpreter THIS run actually probed.
#
# SUPERSEDED FOR THIS REPO by #553/#575, and the reasoning above is exactly
# why. "Launchable as committed" and "correct on every machine" cannot both
# hold for one literal -- `python3` is the PEP 394 guarantee on POSIX and is
# the name that hits the Microsoft Store alias stub on Windows -- so the
# rewrite bought the first by writing the tracked file per machine, which
# breaks the second for everyone the file ships to. The `${VAR:-default}`
# form measured below satisfies both at once, so this repo's own `.mcp.json`
# uses it and wiring is a no-op here twice over: the var form is not
# rewritable, and a tracked target is refused outright. The machinery below
# stays for an UNTRACKED `.mcp.json` in a downstream project, which is a real
# and still-supported case. `is_rewritable_mcp_command` is the one
# predicate for "which commands wiring may touch": the placeholder plus bare
# `python`/`python3`/`py` (and their `.exe` forms); anything with a path
# separator, or naming any other program, is left alone on purpose -- a caller
# who pinned a path meant it, and a wrapper script is not ours to guess at.
# This is the ONE write path -- shared with scripts/wire_mcp_interpreter.py,
# which reuses `rewrite_mcp_config_interpreter` (and this predicate) by
# reference rather than carrying a second copy.
#
# `wire_repo_mcp_config`/`mcp_config_path` are keyword-only `main()` parameters,
# not CLI flags: they default to `False`/`None` so a direct call to `main()`
# (every test in this suite, and any other library caller) never touches this
# checkout's own tracked `.mcp.json`. Only `if __name__ == "__main__":` passes
# `wire_repo_mcp_config=True`, so a real install run wires it automatically --
# nothing to remember -- while `main()` itself stays exactly as pure as it
# always was.
MCP_CONFIG_FILENAME = ".mcp.json"
MCP_INTERPRETER_PLACEHOLDER = "<python-interpreter>"

# --------------------------------------------------------------------------- #
# The `${VAR:-default}` command form (#553 option 2, #575) -- MEASURED, not assumed
# --------------------------------------------------------------------------- #
# #553 listed this option but recorded expansion-in-`command` as UNVERIFIED, and
# the epic-418-followon ADMIRAL_LOG made measuring it the first instruction of
# the door work. It was never run; main took the rewrite path below instead, and
# PR #555 (which proposed exactly `${CONSTELLATION_PYTHON:-python3}`) was closed
# as superseded on that unmeasured assumption.
#
# Measured 2026-08-22, Claude Code 2.1.234 on Linux, via `claude mcp get`'s real
# health-check against local-scope servers whose stored `command` was confirmed
# verbatim on disk (so the CLI was not expanding at add-time):
#
#   command                        env                     result
#   `python3`                      --                      connected  (control)
#   `${CP:-python3}`               CP unset                connected
#   `${CP:-python3}`               CP=/nonexistent/nope    FAILED     (var IS read)
#   `${CP:-python3}`               CP=<other real python>  connected  (var IS honored)
#   `python3`                      CP=/nonexistent/nope    connected  (control holds)
#
# So expansion DOES apply to `command`, not only to `env`. That is what lets the
# committed file stay machine-neutral AND launchable, which no single literal
# could be (#539's thesis) and which the rewrite path below tried to buy by
# writing a tracked file per machine.
#
# CAUTION, also measured (3/3 reproducible, both `VAR=` and `export VAR=""`):
# the `:-` spelling does NOT carry POSIX `:-` semantics. `${CP:-python3}` with
# CP set-but-EMPTY expands to the EMPTY STRING and the server fails to launch;
# only an UNSET variable yields the default. That is POSIX `${VAR-default}`
# behaviour wearing `:-`'s spelling. A dispatcher that exports
# CONSTELLATION_PYTHON="" (a script that computed nothing, say) therefore breaks
# the door silently rather than falling back -- so `expand_mcp_var` below
# reproduces the MEASURED rule, never the shell's.
MCP_INTERPRETER_ENV_VAR = "CONSTELLATION_PYTHON"

#: `${NAME}` or `${NAME:-default}`. The default may be empty (`${SPINE_FILE:-}`),
#: and may not itself contain `}`.
_MCP_VAR_RE = re.compile(r"^\$\{(?P<name>\w+)(?::-(?P<default>[^}]*))?\}$")


def expand_mcp_var(raw: object, env: Mapping[str, str]) -> object:
    """Expand a whole-string `${NAME}` / `${NAME:-default}` the way Claude Code
    was MEASURED to expand it (see the block above), so a test or a readiness
    check resolves a committed `.mcp.json` value to what the harness will really
    launch instead of guessing.

    Deliberately NOT POSIX and NOT `os.path.expandvars`: a name that is present
    in `env` wins even when its value is empty, and the default applies only when
    the name is ABSENT. `os.path.expandvars` also leaves an unset `${NAME}` as
    the literal text, which would read as a launchable command here.

    Anything that is not a full-string reference is returned unchanged -- this is
    a resolver for the one shape `.mcp.json` uses, not a general interpolator."""
    if not isinstance(raw, str):
        return raw
    match = _MCP_VAR_RE.match(raw)
    if match is None:
        return raw
    name = match.group("name")
    if name in env:
        return env[name]            # set-but-empty wins over the default (measured)
    return match.group("default") or ""


def is_mcp_var_command(command: object) -> bool:
    """Whether `command` is the portable `${VAR:-default}` form. Such a command
    is machine-neutral by construction, so wiring must leave it alone -- it is
    already the answer wiring exists to produce."""
    return isinstance(command, str) and _MCP_VAR_RE.match(command) is not None

# Bare names wiring may resolve, beyond the placeholder -- exactly the
# interpreter launcher names `resolve_interpreter` itself probes, plus their
# Windows `.exe` forms. Nothing else: a bare `uv`, `node`, or wrapper script
# name is a different program and not ours to guess at.
MCP_REWRITABLE_BARE_NAMES: frozenset[str] = frozenset({
    "python", "python3", "py",
    "python.exe", "python3.exe", "py.exe",
})


def is_rewritable_mcp_command(command: object) -> bool:
    """Whether `command` is something `rewrite_mcp_config_interpreter` may
    replace with the resolved interpreter: the placeholder, or a bare name in
    `MCP_REWRITABLE_BARE_NAMES`. A path -- anything containing `/` or `\\` --
    is never rewritable regardless of its final component: a caller who
    pinned `/usr/bin/python3.12` meant it, and stomping that is a worse bug
    than the silent no-op this predicate exists to fix. Any other program
    name is likewise left alone."""
    if not isinstance(command, str):
        return False
    if command == MCP_INTERPRETER_PLACEHOLDER:
        return True
    # The portable `${VAR:-default}` form is already machine-neutral AND
    # launchable -- it is the answer wiring exists to produce, so resolving it
    # to this host's name would DOWNGRADE it. Stated explicitly rather than
    # left to fall through the bare-name check below, so a test can pin the
    # intent instead of an accident of set membership.
    if is_mcp_var_command(command):
        return False
    if "/" in command or "\\" in command:
        return False
    return command in MCP_REWRITABLE_BARE_NAMES


def default_mcp_config_path(repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / MCP_CONFIG_FILENAME


def rewrite_mcp_config_interpreter(mcp_config_path: Path, interpreter: InterpreterResolution) -> bool:
    """Rewrite every `mcpServers[*].command` that `is_rewritable_mcp_command`
    accepts -- the placeholder, or a bare `python`/`python3`/`py` name -- to
    `interpreter.interpreter`. Returns whether the file changed; a command
    that is already the resolved interpreter counts as unchanged, so a
    correctly-wired config stays a true no-op rather than a same-value
    rewrite.

    `interpreter` is threaded in, never re-probed here -- mirrors
    `resolve_interpreter`'s "call once per run, thread the result through"
    contract, so this stays a pure rewrite over an already-resolved value and
    never second-guesses the probe.

    RAISES `InstallError` when `mcp_config_path` is git-tracked. A probed
    interpreter is a fact about ONE machine -- on a POSIX host it is routinely
    `py`, which here resolves to the operator's own `~/.local/bin/py` shim --
    and a tracked `.mcp.json` SHIPS, so writing it hands every other checkout a
    name that need not exist there. This is #539's rule (no tracked string names
    an interpreter) applied to the file that never received #539's fix. The
    refusal existed once, on PR #555, with a test named
    `test_wiring_refuses_a_git_tracked_mcp_json_...`; it was lost when that
    branch was closed as superseded rather than repealed, and this restores it.
    The portable answer is now measured and available -- see
    MCP_INTERPRETER_ENV_VAR -- so a refused caller is not stranded."""
    if is_git_tracked(mcp_config_path):
        raise InstallError(
            f"refusing to wire {mcp_config_path}: it is git-tracked. The resolved "
            f"interpreter ({interpreter.interpreter!r}) is a fact about THIS machine, "
            f"and a tracked .mcp.json ships to every other checkout. Use the portable "
            f"form instead -- set the command to "
            f'"${{{MCP_INTERPRETER_ENV_VAR}:-python3}}", which Claude Code expands from '
            f"the launching environment (measured; see MCP_INTERPRETER_ENV_VAR), so each "
            f"machine overrides it via {MCP_INTERPRETER_ENV_VAR} without touching the file. "
            f"Untrack it instead if it is genuinely machine-local."
        )
    config = json.loads(mcp_config_path.read_text(encoding="utf-8"))
    changed = False
    for server in config.get("mcpServers", {}).values():
        command = server.get("command")
        if is_rewritable_mcp_command(command) and command != interpreter.interpreter:
            server["command"] = interpreter.interpreter
            changed = True
    if changed:
        mcp_config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return changed


def apply_repo_mcp_config_wiring(
    mcp_config_path: Path,
    interpreter: InterpreterResolution,
    *,
    dry_run: bool,
    out: Callable[[str], object],
) -> None:
    """Report-and-wire step for THIS checkout's own `.mcp.json`, run once per
    CLI invocation after skills install successfully.

    A missing file is a silent, named no-op rather than a refusal: an
    installed copy of this script (write-a-skill bundles it) runs from inside
    some other skill's tree with no `.mcp.json` beside it, and that is not a
    defect to abort an otherwise-successful install over."""
    if not mcp_config_path.is_file():
        out(f"- {MCP_CONFIG_FILENAME}: none at {mcp_config_path}; nothing to wire")
        return
    if dry_run and is_git_tracked(mcp_config_path):
        # Same refusal the real run makes, surfaced at the same point -- a dry
        # run that promised "would wire" a file the real run then refuses would
        # be a lie in the one mode whose entire job is to predict the real run.
        out(
            f"- DRY RUN: {mcp_config_path} is git-tracked; would NOT wire it "
            f'(use "${{{MCP_INTERPRETER_ENV_VAR}:-python3}}" instead)'
        )
        return
    if dry_run:
        config = json.loads(mcp_config_path.read_text(encoding="utf-8"))
        rewritable_count = sum(
            1 for server in config.get("mcpServers", {}).values()
            if is_rewritable_mcp_command(server.get("command"))
            and server.get("command") != interpreter.interpreter
        )
        if rewritable_count:
            out(
                f"- DRY RUN: would wire {rewritable_count} {mcp_config_path} "
                f"server command(s) -> {interpreter.interpreter!r} (probed)"
            )
        else:
            out(
                f"- DRY RUN: {mcp_config_path} carries no rewritable interpreter "
                f"command; nothing to wire"
            )
        return
    # A tracked target is REFUSED by `rewrite_mcp_config_interpreter`, and that
    # refusal is reported here rather than raised onward: this step runs at the
    # tail of an otherwise-successful install, and aborting with exit 2 after the
    # skills are already on disk would report a completed install as a failure.
    # The standalone `scripts/wire_mcp_interpreter.py` lets the same InstallError
    # out to its own top-level handler, so a caller who asked for wiring ONLY
    # still gets a hard, visible error. One refusal, two proportionate reactions.
    try:
        changed = rewrite_mcp_config_interpreter(mcp_config_path, interpreter)
    except InstallError as exc:
        out(f"- {mcp_config_path}: NOT wired -- {exc}")
        return
    if changed:
        out(f"- {mcp_config_path}: wired command -> {interpreter.interpreter!r} (probed)")
    else:
        out(
            f"- {mcp_config_path}: no rewritable interpreter command found; "
            f"nothing to wire"
        )


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


def install_engine_bundle(
    target_root: Path,
    *,
    dry_run: bool,
    out: Callable[[str], object],
) -> None:
    """Install the non-skill engine bundle (#639).

    Unconditional: every install writes it, whatever `--skills` selected, because
    a consuming machine's settings.json wires five hook entries into this
    directory and a subset install that skipped it would leave every one of them
    naming a path with no file behind it.

    Replace-in-place rather than merge, matching how a skill target is written:
    a script dropped from `ENGINE_BUNDLE_SCRIPTS` must not survive as a stale
    copy that an old settings.json can still resolve.
    """
    target = target_root / ENGINE_BUNDLE_INSTALL_NAME
    out(f"- {ENGINE_BUNDLE_INSTALL_NAME}: {len(ENGINE_BUNDLE_SCRIPTS)} script(s) -> {target}")
    if dry_run:
        return
    ensure_target_is_inside_root(target_root, target)
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    scripts_dir = target / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for script in ENGINE_BUNDLE_SCRIPTS:
        shutil.copy2(script_source_path(script, REPO_ROOT / "scripts"), scripts_dir / script)


# The engine's home before #639. A machine that has ever installed this corpus
# carries hook wiring into it, so vacating the path is a migration, not a rename.
LEGACY_ENGINE_HOME_INSTALL_NAME = "constellation-workbench"


def migrate_legacy_engine_home(
    target_root: Path,
    *,
    force: bool,
    dry_run: bool,
    out: Callable[[str], object],
) -> None:
    """Remove the engine scripts from their pre-#639 home, loudly.

    THE FAILURE THIS EXISTS TO PREVENT IS SILENT, AND IT IS THE SUBSET INSTALL.
    A full `--force` install wipes every `constellation-*` directory
    (`remove_existing_constellation_set`), so the old copies vanish and any
    settings.json entry still naming them resolves to nothing -- which
    `detect_hook_wiring` reports as STALE, because it classifies by resolving
    paths against the filesystem rather than by matching strings. That case is
    already loud.

    A `--skills <subset>` install does NOT wipe. Without this migration the old
    `constellation-workbench/scripts/` survives intact, every wired path still
    resolves, and five hooks plus the engine go on running the PREVIOUS
    revision's code forever, with nothing anywhere reporting a problem. That is
    strictly worse than a broken path: a stale hook that runs is indistinguishable
    from a current one that runs.

    So it runs on every install, subset or not, and requires `--force` -- the
    same authority `migrate_legacy_initial_cut_destination` requires, for the
    same reason: removing something a previous install wrote is not a side
    effect of an install someone already knew how to run.
    """
    legacy_scripts = target_root / LEGACY_ENGINE_HOME_INSTALL_NAME / "scripts"
    if not legacy_scripts.exists():
        return
    ensure_target_is_inside_root(target_root, legacy_scripts)
    if dry_run:
        # Dry run reports and never raises, including when --force is absent: a
        # plan is exactly where someone should LEARN a migration is pending, and
        # this one fires on every machine that has ever installed this corpus, so
        # raising here would make --dry-run unusable for all of them.
        needs = "" if force else " (needs --force)"
        out(f"- DRY RUN: would remove the engine's pre-#639 home {legacy_scripts}{needs}")
        return
    if not force:
        raise InstallError(
            f"the engine's pre-#639 home still exists at {legacy_scripts}; it holds the "
            f"copies five wired hook entries resolve to, so leaving it in place would keep "
            f"those hooks running the old code with nothing reporting it. Migrate with "
            f"--force."
        )
    shutil.rmtree(legacy_scripts)
    out(f"- removed the engine's pre-#639 home {legacy_scripts}")


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
# The canonical owner (see ENGINE_BUNDLE_INSTALL_NAME): exactly one installed
# copy exists, so the wiring has an unambiguous path to point at. Since #639
# that owner is the non-skill engine bundle rather than a skill -- which is what
# lets the wiring name the cargo instead of a wrapper, and what lets
# `--wire-hooks` stop depending on a particular skill being in the install set.
HOOK_OWNER_INSTALL_NAME = ENGINE_BUNDLE_INSTALL_NAME
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

    Five exist (#539, #door-binding), not one: the Context Governor's PostToolUse
    gauge writer plus four `spine_rail.py` registrations. Before this table the
    installer hard-coded the gauge writer's event/matcher/timeout as module
    constants and had no representation at all for the rest -- so `--wire-hooks`
    could only ever produce a fraction of the wiring, and detection could only
    ever see that same fraction.

    `(event, script, matcher)` is the identity: two specs never share all
    three, so one settings.json entry belongs to at most one spec.
    `spine_rail.py` appears under three distinct events, and twice under
    `PostToolUse` alone (once per matcher) -- both stay unambiguous because
    `matcher` is part of the identity, not just `name`."""

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
    # #door-binding: the MCP spine door's own claim/release tool. A second
    # PostToolUse entry for the SAME script -- the `(event, script)` identity
    # claim above is no longer true on its own; `matcher` now also
    # distinguishes entries for one (event, script) pair, same as `name` does.
    HookSpec(
        "spine_rail_post_tool_use_door", SPINE_RAIL_HOOK_SCRIPT, "PostToolUse",
        "mcp__spine__spine_lease", ("PostToolUse",), 10,
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
HOOKS_FROM_INSTALLED = "installed"  # <target_root>/constellation-engine/scripts/
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


def detect_stale_permission_rules(settings_path: Path) -> list[str]:
    """READ-ONLY. `permissions.allow` entries naming a path under a
    `constellation-*` directory that is not on disk.

    WHY THIS IS A REPORT AND NEVER A REWRITE (#639). The installer does not own
    that block: it has never written a permission rule, and
    `test_wire_hooks_is_additive_and_preserves_unrelated_settings` pins
    `permissions` as surviving `wire_hooks` byte-identical. The rules on a given
    machine are hand-approved, per-machine, and incomplete by construction --
    they name the engine copies under three skills and not the one a crew
    actually drives.

    It is also a materially different failure from a stale HOOK. A hook entry
    naming a moved script fails SILENTLY: nothing fires and nothing says so,
    which is why that case earns a migration. A permission rule naming a moved
    script fails LOUDLY, by prompting -- the human sees it, approves once, and
    their own approval writes the corrected rule. Reporting converts a surprise
    prompt into an expected one; rewriting would make an installer that edits
    security config on a human's behalf.

    Classification is by RESOLVING the path, the same discipline
    `detect_hook_wiring` uses, so a rule pointing at a directory that still
    exists is never reported.
    """
    if not settings_path.is_file():
        return []
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # Unreadable settings are already reported by the hook detector, which
        # runs beside this one. Saying it twice would not add information.
        return []
    allow = ((settings or {}).get("permissions") or {}).get("allow") or []
    stale: list[str] = []
    for rule in allow:
        if not isinstance(rule, str):
            continue
        for token in re.findall(r"[^\s'\"()]*constellation-[^\s'\"()]*", rule):
            candidate = token.rstrip(":*")
            if candidate and not Path(candidate).exists():
                stale.append(rule)
                break
    return stale


def report_stale_permission_rules(
    target_root: Path,
    *,
    out: Callable[[str], object],
) -> list[str]:
    """Print the read-only permission-rule notice, if there is one to print."""
    settings_path = settings_path_for_target_root(target_root)
    stale = detect_stale_permission_rules(settings_path)
    if stale:
        out(
            f"- permissions: {len(stale)} `permissions.allow` rule(s) in {settings_path} "
            f"name a constellation path that is not on disk, so they match nothing and you "
            f"will be prompted where they used to allow: {'; '.join(stale)}. This installer "
            f"does not edit permissions -- approve the new path once when prompted, or "
            f"update the rule yourself."
        )
    return stale


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
    report_stale_permission_rules(target_root, out=out)
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

    Naming the interpreter first is what removes THAT hazard, and it removes
    it under EVERY shell -- `sh`, Git Bash, PowerShell and `cmd` all parse a
    leading bare word as a command to run. So the leading-word invariant does
    not depend on the PowerShell parse claim being true; it is simply the
    form that is correct whether or not it is.

    CONTRACT, NARROWED (#539/#560): passing this check is NECESSARY but no
    longer SUFFICIENT for the command to actually run everywhere. Every
    command `build_hook_command` builds now leads with
    `${MCP_INTERPRETER_ENV_VAR:-<interpreter>}`, a POSIX parameter expansion
    -- and that expansion is only real under a shell that performs it. Before
    the interpreter became a `${VAR:-default}` reference, a bare interpreter
    name needed no expansion at all, so shell-independence held BY ACCIDENT;
    #651 shipped the `${VAR:-default}` form without pinning a shell, which is
    exactly how a command that passes THIS guard still no-ops on Windows
    (PowerShell does not do `${VAR:-default}` expansion; #651's own tests
    caught it). So: a command this function accepts is only valid alongside
    an entry that also pins `"shell": "bash"` (see `build_hook_entry`, which
    pins it on every entry it writes) -- this function checks the command's
    own shape and cannot see or enforce that sibling key, so callers that
    build a hook entry by hand remain responsible for both halves of the
    contract, not just this one."""
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


def build_hook_command(
    script_path: Path,
    interpreter: str,
    args: Sequence[str] = (),
    *,
    project_root: Path | None = None,
) -> str:
    """The literal `command` string an entry carries.

    HUMAN RULING (owner, 2026-08-22, #539/#560), superseding the #269 paragraph
    this docstring used to carry verbatim: "I'm not worried about rogue agents
    or bad actors. just trying to make execution easier. is there a
    simplification we can make? I don't buy that anti-tamper for the python
    executable is necessary at all." That withdraws the constraint this
    function used to enforce -- PATH always absolute, never
    `${CLAUDE_PROJECT_DIR}` -- which #269 leaned on to argue that an absolute,
    installed path was pinned BY CONSTRUCTION and so protected the rule that an
    agent's own branch cannot edit the code that judges it. The old reasoning
    was real and is kept here rather than deleted: `${CLAUDE_PROJECT_DIR}` is
    fixed at session launch (#269), so it happens to point at the main
    checkout for an agent working in a worktree, and an absolute path does not
    depend on that harness behaviour holding. What changes is the WEIGHT given
    to that property: the owner has ruled it is not worth the cost of the
    absolute form (a machine-specific, username-bearing path that a project-
    scope settings.json could never honestly commit). This function no longer
    tries to defend against a tampering agent; it only needs to be correct and
    portable.

    So the PATH is now `${CLAUDE_PROJECT_DIR}`-relative whenever `project_root`
    is given (project scope: `${CLAUDE_PROJECT_DIR}/scripts/hooks/<script>` for
    `HOOKS_FROM_SOURCE`, `${CLAUDE_PROJECT_DIR}/.claude/skills/constellation-engine/
    scripts/<script>` for an installed copy -- both project-relative now, and
    the source/installed distinction is preserved because it names two
    genuinely different files). `project_root=None` keeps the path ABSOLUTE,
    which callers must still use at `--scope user`: a user-scope
    `~/.claude/settings.json` is read for EVERY project a session opens, not
    just one, so it has no single project root `${CLAUDE_PROJECT_DIR}` could
    correctly stand for -- `${CLAUDE_PROJECT_DIR}` would resolve to whatever
    project happens to be open, which is not necessarily where the installed
    skill actually lives (`~/.claude/skills/...`). The PATH form is therefore
    SCOPE-appropriate, decided by the caller (`wire_hooks`), not a property of
    this function alone.

    The INTERPRETER is written as `${MCP_INTERPRETER_ENV_VAR}:-<interpreter>}`
    (e.g. `${CONSTELLATION_PYTHON:-py}`), not the bare `interpreter` name --
    #539's residual on this file, closed by measurement rather than assumption.
    Every hook entry Claude Code runs shell-form, and (reproduced independently,
    2026-08-22, via `claude -p` + a temp `--settings` file per
    `skills/_shared/windows.md` #6: control/single-quoted/double-quoted marker
    arms, plus a set-but-empty arm) the REAL SHELL performs true POSIX
    `${VAR:-default}` expansion on a hook `command` -- set-but-empty correctly
    falls back to the default here, unlike `.mcp.json`'s `command`, which
    Claude Code's own expander handles with non-POSIX `:-` semantics (#575).
    So the same env var the MCP door already uses (`MCP_INTERPRETER_ENV_VAR` --
    one knob, not two) also overrides a hook's interpreter, with no new
    mechanism and no new failure mode to document. This is the ONE knob for
    BOTH halves now: the interpreter is unified everywhere (this function never
    had a second knob for it), and the ruling above is what lets the PATH join
    it as something callers can also choose to unify, instead of staying
    absolute by a rule that no longer applies.

    `interpreter` -- the DEFAULT inside that expansion -- still comes from the
    run's single `resolve_interpreter()` probe, never re-probed here, never
    hardcoded, so behaviour is UNCHANGED when the env var is unset: this only
    ADDS an override path.

    A side effect worth naming: `${MCP_INTERPRETER_ENV_VAR}...}` always starts
    with `$`, never a quote, so the leading-quote hazard `assert_shell_safe_command`
    guards is now structurally unreachable from this call site (even an empty
    `interpreter` no longer produces one) -- the call stays, as defense in depth
    on a public function, not because this site can still trip it."""
    portable_interpreter = f"${{{MCP_INTERPRETER_ENV_VAR}:-{interpreter}}}"
    if project_root is None:
        path_text = script_path.as_posix()
    else:
        try:
            relative = script_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            raise InstallError(
                f"build_hook_command: {script_path} is not inside project_root "
                f"{project_root} -- no ${{CLAUDE_PROJECT_DIR}}-relative form exists for it. "
                f"This is an installer bug (a caller passed a project_root that does not "
                f"actually contain the script it is wiring), not a per-host condition."
            )
        path_text = f"${{CLAUDE_PROJECT_DIR}}/{relative.as_posix()}"
    command = f'{portable_interpreter} "{path_text}"'
    if args:
        command = " ".join([command, *args])
    assert_shell_safe_command(command)
    return command


def build_hook_entry(command: str, spec: HookSpec = GAUGE_WRITER_SPEC) -> dict:
    # "shell": "bash" is not decorative: `command` now leads with
    # `${MCP_INTERPRETER_ENV_VAR:-<interpreter>}`, which needs a REAL POSIX
    # shell to expand (measured: bash does true `${VAR:-default}` expansion on
    # a hook `command`; PowerShell/cmd.exe do not). Without this pin Claude
    # Code can fall back to PowerShell on a Windows host with no Git Bash, the
    # `${...}` token is passed through unexpanded, and the hook never runs --
    # silently, the exact #539 failure shape. Matches every entry this repo's
    # own tracked .claude/settings.json ships.
    hooks = [{"type": "command", "command": command, "shell": "bash", "timeout": spec.timeout}]
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

    Returns False when an identical command is already present under the SAME
    matcher within `event`. Scoped to (matcher, command), not command alone
    (#door-binding): two specs now legitimately share one (event, script) --
    `spine_rail.py`'s two PostToolUse registrations, one per matcher -- and
    they build the IDENTICAL command string (same script, same event
    argument). A command-only dedup would read the second registration as a
    repeat of the first and silently drop it, leaving a spec in `HOOK_SPECS`
    that `--wire-hooks` can never actually wire."""
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(f"--wire-hooks: 'hooks' in settings is not an object: {type(hooks).__name__}")
    entries = hooks.setdefault(event, [])
    if not isinstance(entries, list):
        raise InstallError(
            f"--wire-hooks: 'hooks.{event}' in settings is not an array: {type(entries).__name__}"
        )
    new_matcher = entry.get("matcher")
    new_command = entry["hooks"][0]["command"]
    for existing in entries:
        if not isinstance(existing, dict) or existing.get("matcher") != new_matcher:
            continue
        for hook in existing.get("hooks") or []:
            if hook_command_text(hook) == new_command:
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

    # FAIL LOUDLY ON A PLATFORM WE CANNOT SERVE (#539). Since the owner ruling,
    # `resolve_interpreter` RAISES rather than returning an os.name guess, so a
    # CLI run can no longer reach here with an unprobed resolution -- the
    # refusal now happens one level up, at its cause. This guard stays as
    # defense in depth on a PUBLIC function, and it is not dead code: the other
    # producer of an `InterpreterResolution` is
    # scripts/verify_installed_bundles.py, which reconstructs one from an
    # installed `interpreter.json` sidecar, and a bundle installed by an older
    # version still carries "os-default-fallback" on disk. What is refused is
    # wiring from a resolution never measured on THIS host, whatever made it.
    if interpreter.resolved_via != "probe":
        raise InstallError(
            f"--wire-hooks: refusing to wire from an interpreter resolution that was not "
            f"probed on this host (resolved_via={interpreter.resolved_via!r}, "
            f"interpreter={interpreter.interpreter!r}). A hook command built from an "
            f"unmeasured name may not start at all, and a hook that never starts reports "
            f"nothing. Re-run the installer so this host is probed afresh."
        )

    settings_path = settings_path_for_wiring(target_root, hooks_from)

    # The base `${CLAUDE_PROJECT_DIR}` stands for, or None for an absolute
    # path (#539/#560 ruling -- see `build_hook_command`'s docstring for the
    # human ruling this reverses #269's constraint on). `--scope user` has no
    # single governing project (one settings.json is read for every project a
    # session opens), so it stays absolute regardless of `hooks_from`.
    # `--scope project` IS one project, so both forms are expressible
    # relative to it: source hooks are always REPO_ROOT-relative (their
    # location is a fixed fact about the checkout, not about `target_root`),
    # and installed hooks are relative to the project two levels above
    # `target_root` -- the `<project>/<agent.project_config_dir>/skills`
    # layout `resolve_target_root` actually produces (`.claude` is one path
    # segment for every HOOK_CAPABLE agent, i.e. just `claude`).
    if scope != "project":
        relative_base: Path | None = None
    elif hooks_from == HOOKS_FROM_SOURCE:
        relative_base = REPO_ROOT
    else:
        relative_base = target_root.parent.parent

    # RAISES on a git-tracked target ONLY when the command this function is
    # about to build would still be absolute (`relative_base is None`, i.e.
    # `--scope user`). Reverts #651's broadening (`if is_git_tracked(...)`,
    # unconditional on `hooks_from`) back toward something narrower, but not
    # to its pre-#651 shape either (`hooks_from == HOOKS_FROM_SOURCE`) --
    # that shape refused only source wiring and left the installed path free
    # to write into an already-committed settings.json, which was #651's own
    # bug fix. The guard's REASON was always "the emitted command cannot be
    # committed"; #651 was right that this covered every `hooks_from` value
    # at the time, because every path was absolute regardless. The #539/#560
    # ruling changes that fact at `--scope project`: BOTH halves of the
    # command -- interpreter (`${MCP_INTERPRETER_ENV_VAR:-...}`) and now path
    # (`${CLAUDE_PROJECT_DIR}/...`) -- are portable there, so the command IS
    # safe to commit and this guard would only be blocking the very
    # convergence item 3 of #539/#560 asks for (`.claude/settings.json`
    # matching what `--wire-hooks` itself would emit). At `--scope user` the
    # path stays absolute (see `relative_base` above), so the original
    # reason still holds there and the guard still fires -- unconditionally
    # on `hooks_from`, same as #651, since `hooks_from` no longer changes
    # whether the PATH is portable, only which file gets absolute path.
    if relative_base is None and is_git_tracked(settings_path):
        portable_interpreter = f"${{{MCP_INTERPRETER_ENV_VAR}:-{interpreter.interpreter}}}"
        raise InstallError(
            f"--wire-hooks --scope user: refusing to write {settings_path} -- it is "
            f"git-tracked. A user-scope settings.json has no single project to be relative "
            f"to (it is read for every project a session opens), so its command keeps an "
            f"ABSOLUTE, per-machine path even though {SETTINGS_FILENAME}'s project-scope "
            f"form is now portable (#539/#560 ruling). The interpreter half is portable "
            f"({portable_interpreter!r}, the same {MCP_INTERPRETER_ENV_VAR} knob `.mcp.json` "
            f"uses) but that alone does not make an absolute path safe to commit. Wire at "
            f"--scope project instead (writes a ${{CLAUDE_PROJECT_DIR}}-relative, "
            f"committable command), or keep {settings_path} out of version control."
        )

    commands: list[tuple[HookSpec, str]] = []
    for spec in specs:
        script = hook_script_path(target_root, spec.script, hooks_from=hooks_from)
        if not dry_run and not script.is_file():
            raise InstallError(
                f"--wire-hooks: no {spec.script} at {script}. Refusing to wire a "
                f"path with no file behind it, and refusing to point at another skill's copy."
            )
        commands.append((
            spec,
            build_hook_command(
                script, interpreter.interpreter, spec.args, project_root=relative_base),
        ))

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
        # Still routed to the per-machine sibling regardless of portability
        # (`settings_path_for_wiring` above) -- that routing is about keeping
        # a developer's own source-tree override out of the file every
        # contributor shares, not about whether the command COULD be
        # committed. At `--scope user` it also carries an absolute path
        # (relative_base is None there), so say so; at `--scope project` the
        # path is portable but the file is still per-machine, so say that
        # instead of repeating a claim ("correct on THIS machine only") that
        # is no longer true of the path half.
        if relative_base is None:
            out(
                f"- NOTE: this wiring points at this checkout's own scripts/hooks/ by an "
                f"ABSOLUTE path and names the interpreter probed here "
                f"({interpreter.interpreter}) as its default. It is correct on THIS "
                f"machine only. It was written to {settings_path.name}, which is "
                f"per-machine and must never be committed; Claude Code merges its hooks "
                f"with whatever {SETTINGS_FILENAME} already carries rather than "
                f"replacing them."
            )
        else:
            out(
                f"- NOTE: this wiring points at this checkout's own scripts/hooks/ by a "
                f"${{CLAUDE_PROJECT_DIR}}-relative path (portable -- #539/#560 ruling) and "
                f"names the interpreter probed here ({interpreter.interpreter}) as its "
                f"DEFAULT, overridable via {MCP_INTERPRETER_ENV_VAR}. It was still written "
                f"to {settings_path.name}, which is per-machine by convention -- that "
                f"routing is deliberate (a source-tree override should not land in the "
                f"file every contributor shares), not a portability limit of the command "
                f"itself; Claude Code merges its hooks with whatever {SETTINGS_FILENAME} "
                f"already carries rather than replacing them."
            )
    elif scope == "project":
        # Pre-ruling this warned that the entry embedded an absolute,
        # username-bearing path. It no longer does (both the path and the
        # interpreter default are portable), so there is nothing left to
        # warn about -- a project-scope settings.json this wiring wrote is
        # exactly what item 3 of #539/#560 wants it to be: committable as
        # written, the same form the tracked .claude/settings.json now ships.
        pass


# --------------------------------------------------------------------------- #
# readiness check (#458) -- report-only: never repairs, never writes settings.json
# --------------------------------------------------------------------------- #
# "Is this project set up to run Constellation" answered as five separately
# testable checks, never a single opaque verdict. Each returns a ReadinessCheck
# so a failing item always carries a NAMED reason -- a check that can only ever
# report ready is the exact defect this exists to catch.
#
# The fifth item, `interpreter`, arrived with #539's ruling that the installer
# hard-stops when no interpreter answers. An abort is right for an install and
# wrong for a diagnostic: readiness exists to NAME what is wrong with a host,
# so it reports this condition as a plain NOT READY instead of refusing to run.


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


def check_interpreter_resolvable(
    *,
    candidates: Sequence[str] = INTERPRETER_CANDIDATES,
    timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT,
) -> ReadinessCheck:
    """Readiness item 5: an interpreter this installer can NAME (environment-scoped).

    A distinct question from item 1, not a duplicate of it. `check_engine_runnable`
    asks whether pytest runs under `sys.executable` -- an interpreter that
    always exists, because it is the one running this process. This asks
    whether any of `INTERPRETER_CANDIDATES` resolves as a NAME on PATH, which
    is what installed skill bodies and hook commands are written in terms of.
    A host can pass item 1 and fail this one: a venv Python running the
    installer says nothing about whether `py`/`python3`/`python` are launchable
    for a hook subprocess later.

    Reported, never raised. `resolve_interpreter` refusing is right for an
    install; refusing to run the DIAGNOSTIC when this condition is the
    diagnosis would be its own defect, so this calls `probe_host_interpreter`
    directly -- the same measurement without the control flow."""
    probed = probe_host_interpreter(candidates=candidates, timeout=timeout)
    if probed is None:
        return ReadinessCheck(False, no_interpreter_message(candidates))
    return ReadinessCheck(
        True,
        f"`{probed}` answered `{probed} --version` on this host "
        f"(tried {', '.join(candidates)} in order)",
    )


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
    failure (not a repo, git missing) reads as untracked, never raises.

    `path` is made absolute FIRST, and both the subprocess `cwd` and the
    pathspec are derived from that absolute path -- a relative `path` (e.g.
    `.claude/settings.local.json` from `--project .`) would otherwise resolve
    its RELATIVE parent (`.claude`) against the process's real cwd for `cwd`,
    while git evaluates the still-relative pathspec against THAT same cwd too,
    doubling the parent segment (`.claude/.claude/...`) and reporting a tracked
    file as untracked. Absolutizing first makes the answer independent of
    whether the caller passed a relative or an absolute path.

    It is `os.path.abspath`, deliberately, and NOT `Path.resolve()`.
    `resolve()` follows symlinks, so a git-tracked symlink whose target lives
    outside the repo resolves to a path git knows nothing about and reads as
    untracked -- reintroducing the exact false negative this function was
    fixed for, and letting the installer write machine-specific wiring
    straight through the link into a file some other repo tracks, with no
    local `git status` signal. `resolve()` also touches the filesystem and
    raises `RuntimeError` on a symlink loop, which is outside the caught set
    and breaks the never-raises contract above. `abspath` normalizes `..`
    without following links and without any filesystem I/O."""
    try:
        absolute = Path(os.path.abspath(os.fspath(path)))
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(absolute)],
            cwd=str(absolute.parent), capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def resolve_git_hooks_dir(repo_root: Path) -> Path | None:
    """Resolve the git hooks directory that a real `git commit` in `repo_root`
    would actually consult, via `git rev-parse --path-format=absolute
    --git-path hooks` run with `cwd=repo_root`.

    Report-only, matching `is_git_tracked`'s style: any git failure (not a
    repo, git missing, timeout) returns `None` rather than raising. Correctly
    resolves the SHARED hooks directory when `repo_root` is a linked worktree
    (`--git-path` resolves through the worktree's `.git` file to the common
    dir the main checkout and every sibling worktree share), and honors
    `core.hooksPath` when the repo sets one, since both are exactly what
    `--git-path hooks` itself accounts for -- this function adds no path
    logic of its own beyond invoking git and reading its answer."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-path", "hooks"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


GIT_PRECOMMIT_HOOK_MARKER = "# constellation-code-map-precommit-hook"


def _git_precommit_hook_wrapper_text() -> str:
    """The shell wrapper body written to `<hooks-dir>/pre-commit`.

    `<toplevel>` is resolved at RUN TIME, inside the wrapper, via `git
    rev-parse --show-toplevel` -- never a path baked in at install time. This
    is what lets one shared hooks directory serve every sibling worktree
    correctly: each invocation resolves and execs ITS OWN worktree's copy of
    `scripts/hooks/code_map_precommit.py`, which in turn (see that file's own
    docstring) resolves `repo_root` dynamically the same way for the same
    reason. This wrapper's job is only the first hop -- finding its own
    toplevel to locate the shim -- the shim does the rest."""
    return (
        "#!/bin/sh\n"
        f"{GIT_PRECOMMIT_HOOK_MARKER} -- installed by install_constellation.py; "
        "safe to re-run, refuses to clobber a foreign pre-commit hook.\n"
        'toplevel="$(git rev-parse --show-toplevel)" || exit 0\n'
        'exec python3 "$toplevel/scripts/hooks/code_map_precommit.py"\n'
    )


def install_git_precommit_hook(
    repo_root: Path, *, dry_run: bool, out: Callable[[str], object]
) -> None:
    """Write the `pre-commit` wrapper into `repo_root`'s real (possibly
    shared) git hooks directory, so `git commit` actually reaches
    `scripts/hooks/code_map_precommit.py` -- the shim's only real caller.

    Report-only on every failure path, matching this file's other
    report-only detection/wiring functions: a hooks dir that cannot be
    resolved, or a pre-existing foreign `pre-commit` without this function's
    own idempotency marker, is reported and skipped, never raised past this
    function or clobbered."""
    hooks_dir = resolve_git_hooks_dir(repo_root)
    if hooks_dir is None:
        out(f"- git pre-commit hook: could not resolve a hooks directory for {repo_root}; nothing to wire")
        return
    hook_path = hooks_dir / "pre-commit"
    wrapper_text = _git_precommit_hook_wrapper_text()
    if hook_path.is_file():
        existing = hook_path.read_text(encoding="utf-8", errors="replace")
        if GIT_PRECOMMIT_HOOK_MARKER not in existing:
            out(
                f"- git pre-commit hook: {hook_path} already exists and is not ours "
                f"(no {GIT_PRECOMMIT_HOOK_MARKER!r} marker); refusing to clobber it"
            )
            return
        if existing == wrapper_text:
            out(f"- git pre-commit hook: {hook_path} already up to date; nothing to do")
            return
    if dry_run:
        out(f"- DRY RUN: would write git pre-commit hook -> {hook_path}")
        return
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(wrapper_text, encoding="utf-8")
    hook_path.chmod(hook_path.stat().st_mode | 0o111)
    out(f"- git pre-commit hook: wired -> {hook_path}")


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


READINESS_ITEMS: tuple[str, ...] = (
    "engine", "interpreter", "skills", "hooks", "work_area")


# Exit code for the roll-up "some item could not be determined, and nothing
# was found wrong". Distinct from 1 on purpose: a caller that treats any
# nonzero as broken keeps working, and one that wants the distinction can have
# it without us pretending to a verdict we do not hold.
READINESS_EXIT_UNDETERMINABLE = 3


@dataclass(frozen=True)
class ReadinessReport:
    """One agent target's full readiness verdict: the four ReadinessChecks,
    keyed by `READINESS_ITEMS` name. `ready` is true only when all of them are."""

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
    """Combine all five readiness checks for one agent target.

    Hooks are a Claude Code mechanism (`HOOK_CAPABLE_AGENT_NAMES`); for any
    other agent, item 3 is reported READY with an explicit 'not applicable'
    reason rather than silently skipped -- a check the reader cannot tell was
    never run is the exact defect this readiness mode exists to catch."""
    if agent.name in HOOK_CAPABLE_AGENT_NAMES:
        hook_env = env
        if scope == "project":
            # #539/#560 item 4: at project scope, a tracked entry now reads
            # `${CLAUDE_PROJECT_DIR}/...` as committed (item 3's convergence),
            # and `detect_hook_wiring` already special-cases that ONE token as
            # expandable (`_EXPANDABLE_ENV_TOKENS`) -- but it used to be handed
            # whatever `env` (the CALLING process's os.environ) happened to
            # carry, which is often nothing: a readiness check run from a
            # plain terminal has no CLAUDE_PROJECT_DIR at all, so a correctly
            # wired repo reported CANNOT DETERMINE for a fact this CLI
            # invocation already knows. `project_root` is that fact -- the
            # same directory `check_work_area_present` below checks, and #269
            # is what guarantees a real future hook process sees
            # CLAUDE_PROJECT_DIR set to exactly this directory. Overriding it
            # here is not a guess about the wrong process; it is telling the
            # detector the one thing this readiness run was already told,
            # authoritatively, by its own `--project`/cwd. `--scope user` is
            # untouched: a user-scope settings.json has no single project for
            # `${CLAUDE_PROJECT_DIR}` to stand for (see `build_hook_command`'s
            # docstring), so its commands stay absolute and need no expansion.
            hook_env = {**env, "CLAUDE_PROJECT_DIR": str(project_root)}
        hooks = check_hooks_shippable(target_root, scope=scope, env=hook_env, specs=specs)
    else:
        hooks = ReadinessCheck(
            True, f"not applicable: {agent.name} has no hook mechanism to check")
    return ReadinessReport({
        "engine": check_engine_runnable(python=python),
        "interpreter": check_interpreter_resolvable(),
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

    # After the set-level wipe (which already vacated the old home on a full
    # --force run) and before the skills, so the bundle the hook wiring points at
    # exists no matter which subset of skills this call writes.
    migrate_legacy_engine_home(target_root, force=force, dry_run=dry_run, out=out)
    install_engine_bundle(target_root, dry_run=dry_run, out=out)

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
        for template in skill.required_templates:
            template_target = target / "templates" / template
            template_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SHARED_TEMPLATE_ROOT / template, template_target)

    if not dry_run:
        # Stamp the installed root with a CORPUS.json provenance marker, scoped to
        # the skills this run wrote so foreign siblings in a shared root never enter
        # the id. This makes every install (user + project scope) a verifiable build
        # artifact that check_corpus_freshness.py can later date against upstream.
        corpus_id = write_corpus_marker(
            target_root,
            _source_commit(),
            names=[skill.install_name for skill in skills] + [ENGINE_BUNDLE_INSTALL_NAME],
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


def skill_template_sources(skill: Skill) -> list[Path]:
    """Every template file an install of `skill` writes into its templates/ dir.

    Two sources since #639, not one: the skill's own `templates/` directory, and
    the shared templates bundled into it from `_shared/templates/`. The three
    baseline/working-copy walks below all read THIS, because a walk that saw only
    the first source would anchor no baseline for a shared template -- and
    check_skill_freshness, which reads the manifest, would then never report an
    upstream change to one. Sorted by name so the manifest is stable run to run
    regardless of which source a template came from.
    """
    found: dict[str, Path] = {}
    own = skill.source_path / "templates"
    if own.is_dir():
        found.update({p.name: p for p in own.iterdir() if p.is_file()})
    for name in skill.required_templates:
        found[name] = SHARED_TEMPLATE_ROOT / name
    return [found[name] for name in sorted(found)]


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
        for template in skill_template_sources(skill):
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
        for template in skill_template_sources(skill):
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
        for template in skill_template_sources(skill):
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
            "spine_rail.py events (Stop, SessionStart, PostToolUse -- the latter registered "
            "twice, once per matcher); 'all' is all five. Also applies to --check-readiness."
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


def is_self_install(args: argparse.Namespace) -> bool:
    """Whether this run installs into the checkout's own default targets --
    no explicit `--dest` and no explicit `--project` pointing elsewhere. Pure:
    reads only the parsed args, no filesystem or environment access."""
    return args.dest is None and args.project is None


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
    out: Callable[[str], object] = print,
    wire_repo_mcp_config: bool = False,
    mcp_config_path: Path | None = None,
    install_git_pre_commit_hook: bool = False,
    git_repo_root: Path | None = None,
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
        validate_required_templates(skills)

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
            # No skill-membership check here since #639. The hook owner used to be
            # the `workbench` SKILL, which `--skills` could leave out, so wiring had
            # to refuse a path it could not locate. The owner is now the engine
            # BUNDLE, installed on every non-dry run regardless of `--skills`
            # (`install_engine_bundle`), so the condition this guard tested can no
            # longer be false -- and a guard whose answer is the same in the healthy
            # and the broken world discriminates nothing. `--baseline-only` is the
            # one case where no install happens at all, and it is refused above.
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
            # NO interpreter probe on this path, deliberately. --baseline-only
            # seeds template baselines and working copies, both of which are
            # `shutil.copy2` of a source template verbatim -- it never calls
            # `rewrite_installed_skill_paths`, so no `python <` token is ever
            # rewritten and there is no interpreter name to write. Refusing here
            # would block a legitimate operation on a ground that does not apply
            # to it, which is the mirror of the defect this ruling fixes.
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
        # agent target.
        #
        # UNCONDITIONAL, including under --dry-run. A dry run used to skip the
        # probe entirely, which meant that on a host with no working interpreter
        # it printed a clean plan and exited 0 for an install that could not
        # succeed -- a dry run that says "fine" about a run that would refuse is
        # worse than no dry run. It now refuses at exactly the point the real run
        # would, and for the same stated reason.
        interpreter = resolve_interpreter()
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
        # Wiring targets THIS checkout's own .mcp.json (`default_mcp_config_path()`,
        # unconditional) -- firing it on a run that installs somewhere else
        # (`--dest`, or `--project` pointing outside this checkout) would rewrite
        # a file the run never touched otherwise. Skip the whole call rather than
        # redirect its path: an explicit `mcp_config_path` override (every test
        # in RepoMcpConfigWiringTests) is a caller who named its own target and
        # is exempt from this guard. `--scope user` with no `--dest` still
        # satisfies `is_self_install` and still wires the checkout's own
        # `.mcp.json`, even though the install target is the user's home
        # directory rather than this checkout's project scope -- that matches
        # today's behavior and is accepted, not a second bug this wave.
        if wire_repo_mcp_config and (mcp_config_path is not None or is_self_install(args)):
            # Same `interpreter` this run already resolved above -- never a
            # second probe. Runs once per process regardless of --agent all,
            # since this checkout's own .mcp.json is not per-agent-target.
            apply_repo_mcp_config_wiring(
                mcp_config_path if mcp_config_path is not None else default_mcp_config_path(),
                interpreter,
                dry_run=args.dry_run,
                out=out,
            )
        # Same self-install-only shape as the `.mcp.json` wiring immediately above:
        # `git_repo_root` lets a caller (every test in `GitPreCommitHookWiringTests`)
        # decouple from `is_self_install(args)` and exercise the write mechanics
        # directly, while the real CLI entry point below never passes it, so
        # `is_self_install(args)` alone gates a real run -- this checkout's own
        # `.git/hooks` is never touched by installing somewhere else.
        if install_git_pre_commit_hook and (git_repo_root is not None or is_self_install(args)):
            install_git_precommit_hook(
                git_repo_root if git_repo_root is not None else REPO_ROOT,
                dry_run=args.dry_run,
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
    # wire_repo_mcp_config=True / install_git_pre_commit_hook=True ONLY here: a
    # real process invocation wires this checkout's own .mcp.json AND its own
    # git pre-commit hook automatically, with nothing to remember, while a
    # direct library/test call to main() (every other caller) never touches
    # either.
    raise SystemExit(main(wire_repo_mcp_config=True, install_git_pre_commit_hook=True))
