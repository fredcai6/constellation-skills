#!/usr/bin/env python
"""Safe crew launcher with a durable session-recovery registry.

Commander must never hand-launch crew sessions. This wrapper launches crew work
FOREGROUND/BLOCKING by default, assigns a deterministic session name, records
durable launch metadata BEFORE the crew starts, captures stdout/stderr to
deterministic files, and verifies the expected result artifact exists before it
reports success. It refuses to launch a DUPLICATE crew for the same active
work-id/gate/role/worktree unless the prior attempt is explicitly abandoned, and
it supports explicit recovery (`--resume`/`--abandon --relaunch`) after a parent
session is lost.

Deliberate seams keep the wrapper fully testable without spawning a real agent:
  * `build_crew_argv(...)`  — PURE construction of the launcher command line.
  * `launch_process(...)`   — the ONLY place a real subprocess is spawned; tests
                              monkeypatch it to fake exit codes and to write (or
                              withhold) the result artifact.
  * registry read/write, session-name generation, duplicate detection, and
    result-artifact verification are PURE, directly-tested functions.

This wrapper does NOT advance gates, merge PRs, repair git, or integrate results;
that stays with Commander and the engine (#6 owns checklist leasing).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Registry statuses that mean "this attempt still holds the gate/worktree" and
# therefore block a duplicate launch until explicitly abandoned.
ACTIVE_STATUSES = {"running", "resumable"}
DEFAULT_LAUNCHER = "claude"

# Dispatch modes. "spawn" (default) launches a real `claude` CLI subprocess via
# `launch_process`. "external" records the durable registry entry but spawns
# NOTHING — the crew is dispatched out-of-band (e.g. as an Agent-tool subagent in
# the Constellation harness, where no headless `claude` CLI exists). The external
# marker below lets recovery/recover_crews tell a hand-dispatched crew apart from
# a spawned one.
DISPATCH_SPAWN = "spawn"
DISPATCH_EXTERNAL = "external"

# Backend names. A durable registry entry records which crew-launch backend
# produced it (Decision 1: exactly two — `cli` spawns a headless `claude`
# subprocess; `external` records-only, the crew is dispatched out-of-band). New
# entries carry `backend`; a legacy entry without one is inferred by
# `entry_backend` (dispatch == "external" -> external, else cli).
BACKEND_CLI = "cli"
BACKEND_EXTERNAL = "external"

# The `--backend auto` token opts into auto-detection (Decision 4): choose `cli`
# when a headless `claude` CLI is found on PATH, else `external`. `None` (flag
# omitted, backend derived from legacy `--dispatch`) is treated the same as
# `auto` by `select_backend`, but the CLI never passes `auto`/`None` unless the
# operator explicitly asked for `--backend auto` (Decision 5, backward compat).
BACKEND_AUTO = "auto"


class CrewLaunchError(Exception):
    """A refusal: the requested launch/recovery is not allowed. No exit-0."""


# --------------------------------------------------------------------------- #
# time source (single hook so tests can control timestamps)
# --------------------------------------------------------------------------- #
def _now() -> str:
    """Current UTC time as an ISO-8601 string. Monkeypatch in tests to control
    started_at/heartbeat/completed_at timestamps."""
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# work-id grammar — a work-id is a PATH, and it may nest
#
# The epic/commander convention nests one segment: `epic-418-followon/commander-424`
# names the work area `.agent-work/epic-418-followon/commander-424/`. So `/` is a
# legal SEPARATOR in a work-id, not an illegal character, and every helper below
# composes paths from all of its segments. What a work-id may never be is a way OUT
# of `.agent-work/`, so each segment is checked and anything unsafe is refused
# loudly — never trimmed, never normalized into something that happens to resolve.
#
# `gate` and `role`, by contrast, are single session-name components and must stay
# flat: a `/` in either makes `constellation/<work-id>/<gate>/<role>/attempt-<n>`
# ambiguous to parse back, which is precisely the hole `work_id_from_session` used
# to fall into. They are refused at the boundary that builds the name.
# --------------------------------------------------------------------------- #
WORK_ID_SEGMENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
ATTEMPT_RE = re.compile(r"attempt-[0-9]+")
#: The session-name components AFTER the work-id: `<gate>/<role>/attempt-<n>`.
SESSION_TAIL_LEN = 3


def validate_work_id(work_id: str) -> str:
    """The one place a work-id is judged. Returns it unchanged, or REFUSES loudly.

    A work-id is one or more `/`-separated segments, each starting alphanumeric and
    otherwise `[A-Za-z0-9._-]`. That admits the nesting convention and excludes every
    escape from the work area: `..`, an empty segment (leading/trailing/doubled `/`),
    an absolute path, a Windows separator, a drive letter. The refusal NAMES the
    offending segment — a caller that gets "unsafe" with no subject cannot tell a
    typo from a convention it is holding wrong."""
    if not isinstance(work_id, str) or not work_id:
        raise CrewLaunchError(f"work-id must be a non-empty string, got {work_id!r}")
    if "\\" in work_id:
        raise CrewLaunchError(
            f"work-id {work_id!r} contains a backslash; segments are separated by '/' "
            "on every platform"
        )
    segments = work_id.split("/")
    for segment in segments:
        if not WORK_ID_SEGMENT_RE.fullmatch(segment):
            raise CrewLaunchError(
                f"work-id {work_id!r} has an unsafe segment {segment!r}: every segment "
                f"must match {WORK_ID_SEGMENT_RE.pattern} (so a nested id like "
                "'epic-418-followon/commander-424' is fine, but '..', an empty segment "
                "and an absolute path are not)"
            )
    return work_id


def _validate_session_component(value: str, label: str) -> str:
    """A session-name component that must stay FLAT (gate, role).

    Refused rather than accepted-and-escaped: a `/` here would silently extend the
    work-id when the name is parsed back, which is the defect this module just fixed.
    """
    if not isinstance(value, str) or not value:
        raise CrewLaunchError(f"{label} must be a non-empty string, got {value!r}")
    if "/" in value or "\\" in value:
        raise CrewLaunchError(
            f"{label} {value!r} must not contain a path separator: it is ONE component "
            f"of the session name constellation/<work-id>/<gate>/<role>/attempt-<n>, "
            "and a separator here makes that name ambiguous to parse back"
        )
    return value


# --------------------------------------------------------------------------- #
# pure helpers — paths, names, registry I/O
# --------------------------------------------------------------------------- #
def session_name(work_id: str, gate: str, role: str, attempt: int) -> str:
    """Deterministic, stable crew session name.

    `constellation/<work-id>/<gate>/<role>/attempt-<n>` — the same inputs always
    produce the same name, so a recovery can address an attempt unambiguously.

    The work-id may nest (`epic-418-followon/commander-424`); `gate` and `role` may
    not, because the name is parsed back by counting the fixed tail. Both rules are
    enforced HERE, at the boundary that mints the name, so an unparseable name is
    never written into a durable registry entry in the first place."""
    validate_work_id(work_id)
    _validate_session_component(gate, "gate")
    _validate_session_component(role, "role")
    return f"constellation/{work_id}/{gate}/{role}/attempt-{attempt}"


def assignment_session_name(work_id: str, gate: str, role: str) -> str:
    """The lease identity for an ASSIGNMENT, not a process instance:
    `constellation/<work-id>/<gate>/<role>` — `session_name`'s own output with the
    `attempt-<n>` tail stripped off, never a second name builder. A spine belongs
    to a task, not to an agent or a session; keying the lease on the attempt makes
    every legitimate respawn read as a different claimant and forces an
    unwarranted takeover (`checklist_engine.py::claim` matches identity by plain
    string equality — this is the string a respawn must reproduce to resume)."""
    return session_name(work_id, gate, role, 1).rsplit("/", 1)[0]


def work_id_from_session(session: str) -> str:
    """The work-id a `constellation/...` session name belongs to.

    Parsed from the RIGHT, not the left. The name is
    `constellation/<work-id>/<gate>/<role>/attempt-<n>` and only the WORK-ID may
    contain `/` (`session_name` refuses a separator in gate/role), so the work-id is
    everything between the `constellation` prefix and the fixed three-component tail.

    Reading `split("/")[1]` instead truncated a nested work-id to its first segment
    and silently addressed a DIFFERENT run's registry — for
    `epic-418-followon/commander-424` that is the Admiral's own `crew-runs.json`.
    The commander's completed crew then never got finalized and sat `running` in a
    live registry with its result artifact present on disk."""
    parts = session.split("/")
    if (
        len(parts) < 2 + SESSION_TAIL_LEN
        or parts[0] != "constellation"
        or not ATTEMPT_RE.fullmatch(parts[-1])
    ):
        raise CrewLaunchError(
            f"unrecognized session name {session!r} (expected "
            "constellation/<work-id>/<gate>/<role>/attempt-<n>)"
        )
    return validate_work_id("/".join(parts[1:-SESSION_TAIL_LEN]))


def work_dir(work_id: str, root: Path) -> Path:
    validate_work_id(work_id)
    return root / ".agent-work" / work_id


def registry_path(work_id: str, root: Path) -> Path:
    return work_dir(work_id, root) / "crew-runs.json"


def run_log_paths(work_id: str, gate: str, role: str, attempt: int, root: Path) -> tuple[Path, Path]:
    """Deterministic stdout/stderr capture paths for one attempt."""
    runs = work_dir(work_id, root) / "crew-runs"
    stem = f"{gate}-{role}-attempt-{attempt}"
    return runs / f"{stem}.stdout.txt", runs / f"{stem}.stderr.txt"


def load_registry(path: Path) -> list[dict]:
    """Read the registry list; a missing file is an empty registry."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise CrewLaunchError(f"crew registry is not a JSON list: {path}")
    return data


def save_registry(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def find_entry(entries: list[dict], name: str) -> dict | None:
    """The entry whose session_name (== crew_id) matches `name`, or None."""
    for entry in entries:
        if entry.get("session_name") == name or entry.get("crew_id") == name:
            return entry
    return None


def is_abandoned(entry: dict) -> bool:
    return bool(entry.get("abandoned")) or entry.get("status") == "abandoned"


def active_duplicate(entries: list[dict], work_id: str, gate: str, role: str, worktree: str) -> dict | None:
    """The blocking duplicate, if any: an existing entry for the same
    work-id/gate/role/worktree whose status is still active (`running`/
    `resumable`) and which has NOT been abandoned. PURE — used both to refuse a
    fresh launch and (by recover_crews) to report an active lock."""
    for entry in entries:
        if is_abandoned(entry):
            continue
        if entry.get("status") not in ACTIVE_STATUSES:
            continue
        if (
            entry.get("work_id") == work_id
            and entry.get("gate") == gate
            and entry.get("role") == role
            and entry.get("worktree") == worktree
        ):
            return entry
    return None


def next_attempt(entries: list[dict], work_id: str, gate: str, role: str, worktree: str) -> int:
    """One past the highest attempt recorded for this gate/role/worktree (>=1)."""
    attempts = [
        int(entry.get("attempt", 0))
        for entry in entries
        if entry.get("work_id") == work_id
        and entry.get("gate") == gate
        and entry.get("role") == role
        and entry.get("worktree") == worktree
    ]
    return (max(attempts) + 1) if attempts else 1


def result_exists(result: str | os.PathLike[str], root: Path) -> bool:
    """Whether the expected result artifact exists. A relative path is resolved
    against `root`; an absolute path is honored as-is."""
    path = Path(result)
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def result_fresh(result: str | os.PathLike[str], root: Path, since: str) -> bool:
    """Whether the expected result artifact exists AND is FRESH relative to the
    crew's dispatch time `since` (an ISO-8601 string — the registry entry's
    `started_at`). This is the ONE canonical freshness definition; every result
    check reuses it, so a stale leftover result from a prior attempt at the same
    path can never pass as success and the definition can never fork.

    Fresh means the artifact's mtime is at/after `since` floored to whole seconds.
    A missing file is never fresh (existence is a precondition of freshness). The
    floor keeps coarse filesystem mtime resolution from falsely flagging a result
    written in the same second as dispatch. Single machine, no clock skew: both
    the mtime and `since` are POSIX-based, so the comparison is
    timezone-independent."""
    path = Path(result)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        return False
    floor = datetime.fromisoformat(since).replace(microsecond=0)
    return path.stat().st_mtime >= floor.timestamp()


# --------------------------------------------------------------------------- #
# injectable seams — argv construction (pure) and the real launch
# --------------------------------------------------------------------------- #
# Headless agents (`claude -p`) have no interactive approver, so without an
# explicit permission mode every tool action needing approval is DENIED and a
# spawned crew can write nothing (same wall run_skill_eval.py's EXEC_ALLOWED_TOOLS
# / DEFAULT_PERMISSION_MODE document for the narrower eval case — issue #115
# tc2). Every dispatch in this epic worked around it by hand-writing a
# gitignored `.claude/settings.local.json` into the worktree first; the
# launcher grants it instead, so no operator has to remember to. acceptEdits is
# the least-powerful documented mode that clears the file-write wall.
DEFAULT_CREW_PERMISSION_MODE = "acceptEdits"

# A crew's work is a full bounded engineering task (unlike the eval harness's
# python/pytest-only need), so the grant is broad: unrestricted Bash plus the
# core file/search tools, and the MCP spine door tools a crew drives its own
# checklist through (`mcp_spine_server.py`).
#
# The `mcp__spine__*` entries are hand-typed here on purpose, not imported from
# `mcp_spine_server.TOOL_NAMES` at module scope: that module reads `SPINE_FILE`
# and `SPINE_ENGINE` straight out of the environment at import time (raises
# `KeyError` if either is unset) so importing it here would make importing
# `run_crew` itself require a bound spine even for callers -- the CLI, the test
# suite -- that have no spine to bind. `tests/test_crew_launcher.py` instead
# imports `mcp_spine_server` (with a scratch env) and asserts this tuple's
# `mcp__spine__*` entries equal its `TOOL_NAMES`, so the two lists cannot drift
# apart silently the way they did when the door grew from 7 to 9 tools.
CREW_ALLOWED_TOOLS = (
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "TodoWrite", "ToolSearch",
    "mcp__spine__spine_status", "mcp__spine__spine_lease", "mcp__spine__spine_start",
    "mcp__spine__spine_advance", "mcp__spine__spine_evidence", "mcp__spine__spine_halt",
    "mcp__spine__spine_survey_result", "mcp__spine__spine_capture", "mcp__spine__spine_amend",
)

# Ruling (human, verbatim): "agent cannot waive itself. I'll allow commander to
# waive crew, admiral to waive commander, human for admiral. always ask up."
# `spine_evidence` bundles `attest`/`attach`/`waive` behind one tool name, so
# `--allowedTools` (which grants/denies a whole tool, not one of its actions)
# cannot admit attest/attach while refusing waive on its own. A `PreToolUse`
# hook can: it sees the actual call, including `tool_input.action`, before the
# tool runs, and can `deny` just that one action. `WAIVE_DENY_REASON` is what
# the crew sees on the denied call -- it names the blocked path (`spine_halt`
# block) so a crew that hits a check it cannot satisfy is told how to ask up
# instead of reading the denial as a dead end.
# No apostrophes/single-quotes in this string: it is interpolated into a
# single-quoted shell command below (`crew_settings_json`), where a literal
# single-quote character would terminate the quoting early.
WAIVE_DENY_REASON = (
    "A crew must not waive its own bound spine check -- always ask up. Call "
    "spine_halt with action=block, name what you cannot satisfy, and return; "
    "only a human or commander waives it from there."
)
assert "'" not in WAIVE_DENY_REASON, (
    "WAIVE_DENY_REASON is interpolated into a single-quoted shell command; a "
    "literal single-quote would terminate that quoting early"
)

# The PreToolUse hook command itself: reads the tool call's stdin JSON, denies
# only when `tool_input.action == "waive"`, and is silent (`{}`, no opinion --
# `--allowedTools` still decides) for every other action, including attest and
# attach. Written to be invoked directly by tests too (`subprocess.run(["python3",
# "-c", _WAIVE_HOOK_PY], input=<json>, ...)`), so the behavior this grants is
# checked without spawning a real agent CLI.
_WAIVE_HOOK_PY = (
    "import json,sys\n"
    "d=json.load(sys.stdin)\n"
    'a=(d.get("tool_input") or {}).get("action")\n'
    'if a=="waive":\n'
    '    print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse",'
    '"permissionDecision":"deny","permissionDecisionReason":' + json.dumps(WAIVE_DENY_REASON) + '}}))\n'
    "else:\n"
    '    print("{}")\n'
)


def crew_settings_json() -> str:
    """The `--settings` JSON blob every spawned crew gets: a `PreToolUse` hook on
    `mcp__spine__spine_evidence` that denies only `action=waive` (see
    `WAIVE_DENY_REASON` above). Passed as an inline JSON string (`--settings`
    accepts a file path OR a JSON string), so this needs no new file and never
    touches the repo's own `.claude/settings.json` -- it merges with it and with
    the worktree's project settings, which cover different hook events (Stop /
    SessionStart / PostToolUse), so nothing collides."""
    return json.dumps({
        "hooks": {
            "PreToolUse": [{
                "matcher": "mcp__spine__spine_evidence",
                "hooks": [{"type": "command", "command": f"python3 -c '{_WAIVE_HOOK_PY}'"}],
            }],
        },
    })


def build_crew_argv(
    launcher: str, *, role: str, handoff: str | None, model: str | None, session: str,
    spine: str | None = None,
) -> list[str]:
    """PURE construction of the agent-CLI command line from role/handoff/model.

    Kept separate so tests can assert on the argv without spawning anything. The
    real launcher binary is configurable (`--command`) and defaults sensibly; a
    given handoff is passed by path (the wrapper has already refused a missing
    one).

    `handoff` is nullable: a crew with a bound `spine` and no `handoff` is told
    to drive the spine instead of reading a document (issue #559) -- the
    existing handoff branch is kept byte-identical whenever `handoff` IS given
    (even alongside a `spine`), so every current dispatch and test is
    untouched. Refuses (rather than emitting a document-less, spine-less
    prompt) when neither is given; callers refuse this combination earlier too
    (`CrewSpec.__post_init__`), so this is a second, cheaper backstop on the
    pure function itself.

    The claude CLI has no `--session`/`--role`/`--handoff` flags (issue #91: the
    old flag form fails with `unknown option '--session'` on current CLIs), so
    role, session name, and handoff path travel inside the headless `-p` prompt;
    the registry — not the CLI — owns crew identity.

    Always appends `--permission-mode` + `--allowedTools` + `--settings` (M2 job
    1, issue #559 job 4): a dispatch into a worktree with no hand-written
    settings file must complete crew work end to end, so the launcher grants
    what a crew needs (and denies what it must ask up for) instead of an
    operator remembering to."""
    if handoff is not None:
        prompt = (
            f"You are the constellation {role} crew for session {session}. "
            f"Read the handoff at {handoff} and execute it exactly. "
            "The run is only complete when the result artifact the handoff names exists."
        )
    elif spine is not None:
        prompt = (
            f"You are the constellation {role} crew for session {session}. "
            "Call mcp__spine__spine_status first: your spine is already bound. "
            "Drive it gate by gate through the door -- do not author a plan of "
            "your own -- until it reports done."
        )
    else:
        raise CrewLaunchError(
            "build_crew_argv requires a handoff, a spine, or both -- refusing to "
            "build a prompt that names neither"
        )
    argv: list[str] = [launcher, "-p", prompt]
    if model:
        argv += ["--model", model]
    argv += ["--permission-mode", DEFAULT_CREW_PERMISSION_MODE]
    argv += ["--settings", crew_settings_json()]
    argv += ["--allowedTools", *CREW_ALLOWED_TOOLS]
    return argv


_CLI_DRIFT_MARKERS = ("unknown option", "unrecognized arguments", "unknown command")

# ISSUE #454. Same defect class as run_skill_eval's marker sniff: every marker
# above is a MULTI-WORD phrase matched by substring against a colour-capable CLI's
# CAPTURED stderr. The Claude Code harness exports FORCE_COLOR=3, which makes a
# child colourize even when its stdout is a pipe rather than a terminal, and an
# escape landing between the words ("\x1b[31munknown\x1b[0m option") silently stops
# the phrase matching. The hint would then never print, and a plain flag-drift
# failure would read as an unexplained crew failure. The reported `line` would also
# carry raw escapes into the message a human reads.
#
# DECLINED, deliberately (scope): `crew_env` does NOT unset FORCE_COLOR. That would
# fix it at the source but is a production-behavior change to what a live crew
# launch inherits — the Admiral's call. Stripping here closes the defect without
# changing what the child does. Floated up with #454.
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    """Captured output as plain text. PURE. See the #454 note above."""
    return _ANSI_RE.sub("", text or "")


def cli_drift_hint(stderr_text: str) -> str | None:
    """Actionable message when a failed launch looks like agent-CLI flag drift
    (the launcher rejected our argv) rather than a crew failure. Returns None
    when the stderr carries no drift marker."""
    for line in strip_ansi(stderr_text).splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in _CLI_DRIFT_MARKERS):
            return (
                f"agent CLI rejected the launch arguments ({line.strip()!r}) — the installed "
                "CLI's flags have likely drifted from what run_crew.py emits. Re-dispatch "
                "out-of-band with `--backend external` (record-only) and launch the crew "
                "yourself, or override the launcher with `--command`."
            )
    return None


def _print_drift_hint_if_any(stderr_path: Path) -> None:
    """Best-effort drift sniff on a failed launch's captured stderr."""
    try:
        text = stderr_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    hint = cli_drift_hint(text)
    if hint:
        print(hint, file=sys.stderr)


def launch_process(argv: list[str], *, stdin: bytes, env: dict[str, str], stdout_path: Path, stderr_path: Path) -> int:
    """The ONE place a real crew subprocess is spawned. Tests monkeypatch this to
    simulate exit codes and to write (or withhold) the result artifact, so no
    test ever launches a real agent CLI.

    Foreground/blocking: we feed the supplied (empty) stdin, capture stdout/stderr
    to the deterministic files, and return the child's exit code."""
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        proc = subprocess.run(argv, input=stdin, stdout=out, stderr=err, env=env)
    return proc.returncode


def crew_env(
    base_env: dict[str, str] | None = None,
    *,
    spine_file: str | None = None,
    spine_session: str | None = None,
) -> dict[str, str]:
    """UTF-8-safe environment defaults for the child, PLUS the MCP door binding.

    `spine_file` is the spine THIS crew will drive and `spine_session` is its
    assignment-keyed lease identity (`assignment_session_name`, no `attempt-<n>`
    tail). Both are optional so a caller with no spine to bind (e.g. a legacy
    registry entry recorded before this field existed) still gets a valid
    environment — when omitted (`None`), the inherited-environment route is left
    exactly as it is (this is what lets the Admiral's own bootstrap, which passes
    `base_env` but no `--spine`, keep working).

    When a binding IS given, it is ASSIGNED, not `setdefault`-ed: an explicit
    `spine_file`/`spine_session` is more specific than whatever the DISPATCHING
    process's own environment happens to carry (`base_env` defaults to this
    process's `os.environ`). `setdefault` here previously let a door-bound
    dispatcher's own `SPINE_FILE`/`SPINE_SESSION` silently win over the value
    being derived for a child it is launching with an explicit spine, so the
    child claimed the DISPATCHER's lease instead of its own — a caller-supplied
    `--spine` was silently ignored. Assigning closes that hijack; a caller with
    nothing to bind still leaves the inherited value untouched, exactly as
    before."""
    env = dict(os.environ if base_env is None else base_env)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    if spine_file is not None:
        env["SPINE_FILE"] = spine_file
    if spine_session is not None:
        env["SPINE_SESSION"] = spine_session
    return env


def _crew_door_env(*, work_id: str, gate: str, role: str, spine: str | None, root: Path) -> dict[str, str]:
    """The env every dispatched/resumed crew gets: its OWN spine (if any),
    resolved absolute against `root`, and its assignment-keyed lease identity —
    built in one place so `dispatch` and `resume` cannot drift apart.

    `spine_file` and `spine_session` are bound as a PAIR, and ONLY when `spine`
    was given. Deriving `spine_session` unconditionally (even with `spine=None`)
    used to hand a no-`--spine` child a mismatched pair: whatever SPINE_FILE the
    DISPATCHING process happened to have ambient (left untouched, correctly) next
    to a freshly-derived SPINE_SESSION belonging to a different spine entirely —
    a file/identity pair that never matched each other. No `spine` means the
    inherited-environment route is genuinely untouched, both variables together,
    exactly as `crew_env()`'s own contract already promises."""
    if spine is None:
        return crew_env()
    return crew_env(
        spine_file=_resolve_optional_path(spine, root),
        spine_session=assignment_session_name(work_id, gate, role),
    )


def process_alive(pid: int | None) -> bool:
    """Whether `pid` names a live process. The injectable PID-liveness seam used
    by recovery classification (recover_crews imports it). Default uses
    `os.kill(pid, 0)`: ESRCH/no-such-process -> dead; EPERM (the process exists
    but is not ours) -> alive. Tests monkeypatch this so recovery never inspects
    real PIDs."""
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (OSError, ValueError):
        return False
    return True


# --------------------------------------------------------------------------- #
# launch / recovery orchestration
# --------------------------------------------------------------------------- #
def _relativize(path: str, root: Path) -> str:
    """Store paths in the registry relative to root when possible (matches the
    issue's example shape), else verbatim."""
    p = Path(path)
    if p.is_absolute():
        try:
            return p.relative_to(root.resolve()).as_posix()
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def _require_handoff(handoff: str, root: Path, *, action: str) -> Path:
    """Resolve the handoff path against root and REFUSE if it is missing. `action`
    ("launch" | "record") shapes the refusal message so the spawn and external
    paths keep their distinct wording."""
    handoff_path = Path(handoff)
    if not handoff_path.is_absolute():
        handoff_path = root / handoff
    if not handoff_path.is_file():
        raise CrewLaunchError(f"refusing to {action}: handoff file is missing: {handoff_path}")
    return handoff_path


def _resolve_optional_path(path: str | None, root: Path) -> str | None:
    """`path` made absolute against `root`, or `None` unchanged. Used for `spine`,
    which — unlike `handoff` — is not required to exist yet at dispatch time (a
    crew may instantiate its own plan on first turn), so there is no
    `_require_spine` existence check to pair with this."""
    if path is None:
        return None
    p = Path(path)
    return str(p if p.is_absolute() else root / p)


def build_entry(
    *,
    work_id: str,
    gate: str,
    role: str,
    attempt: int,
    worktree: str,
    handoff: str | None,
    result: str,
    root: Path,
    started: str,
    backend: str,
    pid: int | None,
    dispatch: str | None = None,
    model: str | None = None,
    spine: str | None = None,
) -> dict:
    """Construct the base `crew-runs.json` entry shared by BOTH backends (the
    consolidation the wave-1 triage named). One place builds the durable record so
    the two dispatch paths can never drift in shape.

    Every new entry carries a `backend` field (`"cli"` | `"external"`, Decision 1)
    and starts `running` so the duplicate-guard/recovery classifier treat it as an
    in-flight attempt. Backend-specific shape is passed in, not forked here:
      * `pid`      — the spawning process (cli) or `None` (external, PID-less).
      * `dispatch` — external keeps its legacy `dispatch: "external"` marker
                     (Decision 5) so today's tooling and records still parse;
                     the cli backend passes `None` (no marker, as before).
      * `model`    — recorded only when the caller stored it (external), matching
                     the prior per-path shape; the cli path does not store it.
      * `handoff`  — nullable (issue #559): recorded as `None` for a spine-only
                     crew, the same "recorded null, not omitted" shape `spine`
                     already uses below.
      * `spine`    — the spine this crew drives, so a resume can rebind the same
                     door (optional: `None` for a caller with nothing to bind,
                     recorded as `None` rather than omitted — a legacy entry
                     predating this field is the only case with no key at all)."""
    name = session_name(work_id, gate, role, attempt)
    stdout_path, stderr_path = run_log_paths(work_id, gate, role, attempt, root)
    entry = {
        "crew_id": name,
        "work_id": work_id,
        "gate": gate,
        "role": role,
        "attempt": attempt,
        "status": "running",
        "session_name": name,
        "backend": backend,
        "pid": pid,
        "worktree": worktree,
        "handoff": _relativize(handoff, root) if handoff is not None else None,
        "result": _relativize(result, root),
        "spine": _relativize(spine, root) if spine is not None else None,
        "stdout": _relativize(str(stdout_path), root),
        "stderr": _relativize(str(stderr_path), root),
        "started_at": started,
        "last_heartbeat": started,
        "completed_at": None,
        "abandoned": False,
    }
    if dispatch is not None:
        entry["dispatch"] = dispatch
    if model:
        entry["model"] = model
    return entry


def finalize_from_exit_code(
    entry: dict,
    *,
    exit_code: int,
    result: str,
    root: Path,
    since: str,
) -> int:
    """Finalize a spawned attempt's entry from the child exit code and result
    freshness since dispatch. The ONE tail both `CliBackend.dispatch` and
    `CliBackend.resume` call — no copy-paste of the completed/failed rule.

    Sets `completed_at`/`last_heartbeat` (now), `status`, `exit_code`,
    `result_present`, and `result_fresh`, and returns the process-level exit code
    to report. Reuses the single canonical `result_fresh` (`since` is the entry's
    dispatch time): a child that exits 0 but leaves only a STALE prior-attempt
    result at the path (mtime predates dispatch) is `failed`, not `completed`."""
    have_result = result_exists(result, root)
    fresh = result_fresh(result, root, since)
    now = _now()
    entry["completed_at"] = now
    entry["last_heartbeat"] = now
    if exit_code == 0 and fresh:
        entry["status"] = "completed"
        final = 0
    else:
        entry["status"] = "failed"
        final = exit_code if exit_code != 0 else 1
    entry["exit_code"] = exit_code
    entry["result_present"] = have_result
    entry["result_fresh"] = fresh
    return final


def entry_backend(entry: dict) -> str:
    """The backend that owns a recorded entry. New entries carry `backend`
    explicitly; a legacy entry without one is inferred — `dispatch == "external"`
    -> external, else cli (Decision 5, backward compatible)."""
    backend = entry.get("backend")
    if backend in (BACKEND_CLI, BACKEND_EXTERNAL):
        return backend
    return BACKEND_EXTERNAL if entry.get("dispatch") == DISPATCH_EXTERNAL else BACKEND_CLI


@dataclass
class CrewSpec:
    """The parameters of one crew launch, passed to a backend's `dispatch`.

    Shared by both backends; `model`/`launcher` are only meaningful to the cli
    backend (the external backend spawns nothing).

    Identity is checked HERE, at construction, rather than deeper in `session_name`:
    every dispatch path builds a spec before it touches the filesystem, so an
    unparseable identity is refused before a handoff is read or a registry is
    written, and the refusal names the id rather than a missing file.

    `handoff` is nullable (issue #559): a crew given `spine` and no `handoff`
    drives its bound spine instead of reading a document. A spec with NEITHER
    is refused here, at construction -- the one choke point every backend
    passes through -- rather than leaving a crew with no job at all. The
    external backend layers its OWN, stricter refusal on top (it always needs
    a handoff, spine or not, since it cannot bind one)."""
    work_id: str
    gate: str
    role: str
    handoff: str | None
    result: str
    worktree: str
    attempt: int
    spine: str | None = None
    model: str | None = None
    launcher: str = DEFAULT_LAUNCHER

    def __post_init__(self) -> None:
        validate_work_id(self.work_id)
        _validate_session_component(self.gate, "gate")
        _validate_session_component(self.role, "role")
        if self.handoff is None and self.spine is None:
            raise CrewLaunchError(
                "a crew needs a job: refusing a dispatch with neither --handoff "
                "nor --spine given"
            )


# --------------------------------------------------------------------------- #
# crew-launch backends — one result contract, exactly two implementations
# --------------------------------------------------------------------------- #
class CrewBackend:
    """A pluggable crew-launch backend (Decision 1). Exactly two concrete
    implementations exist — `CliBackend` and `ExternalBackend` — behind ONE
    result contract (Decision 2): every backend records a durable entry
    *before/at* dispatch, honors the duplicate-guard, and verifies results
    exists-AND-fresh against the entry's `started_at` (the single `result_fresh`,
    never forked). A backend may *dispatch* differently but may never weaken this
    contract."""

    name: str = ""

    def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[int | None, dict]:
        """Record the durable entry (running) BEFORE work. cli: spawn the
        subprocess then finalize -> (exit_code, entry). external: record-only, no
        subprocess -> (None, entry); the caller verifies later."""
        raise NotImplementedError

    def resume(self, session: str, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]:
        """cli: relaunch the subprocess with the stored session/handoff and
        finalize. external: unrecoverable-by-wrapper (raise CrewLaunchError)."""
        raise NotImplementedError

    def verify(self, entries: list[dict], session: str, *, root: Path) -> tuple[bool, dict]:
        """Uniform across backends: exists-AND-fresh against the entry's
        `started_at`; finalize to `completed` on fresh, else leave `running`.

        Returns (fresh, entry). Reuses the canonical `result_fresh` — no
        duplicated freshness logic. Freshness is judged against the entry's
        `started_at` (its dispatch time), so a stale leftover result from a prior
        attempt at the same path does NOT clear the hold. Both `result_present`
        (existence) and `result_fresh` are recorded so the CLI can tell the two
        failure modes apart (MISSING vs STALE). Only a fresh result finalizes to
        `completed`; otherwise the entry is left `running` so the duplicate-guard
        keeps holding. Refuses if the named crew is unknown or abandoned."""
        entry = find_entry(entries, session)
        if entry is None:
            raise CrewLaunchError(f"cannot verify: no crew recorded with session name {session!r}")
        if is_abandoned(entry):
            raise CrewLaunchError(f"cannot verify an abandoned crew {session!r}")

        present = result_exists(entry["result"], root)
        fresh = result_fresh(entry["result"], root, entry["started_at"])
        entry["result_present"] = present
        entry["result_fresh"] = fresh
        if fresh:
            now = _now()
            entry["status"] = "completed"
            entry["completed_at"] = now
            entry["last_heartbeat"] = now
        save_registry(registry_path(entry["work_id"], root), entries)
        return fresh, entry


class CliBackend(CrewBackend):
    """Spawn a headless `claude` CLI subprocess via the single `launch_process`
    seam. Records the durable entry (running) BEFORE the child starts, runs it
    foreground, then finalizes from the child exit code + result freshness."""

    name = BACKEND_CLI

    def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]:
        # Resolve the seam at CALL time so a monkeypatched module-level
        # `launch_process` (tests, or the CLI) takes effect.
        launch = launch if launch is not None else launch_process
        # `_require_handoff` only runs when a handoff was actually given: a
        # spine-only spec (`spec.handoff is None`) has already cleared
        # `CrewSpec.__post_init__`'s "needs a job" check, so there is nothing to
        # require here.
        handoff_path = _require_handoff(spec.handoff, root, action="launch") if spec.handoff is not None else None

        started = _now()
        entry = build_entry(
            work_id=spec.work_id, gate=spec.gate, role=spec.role, attempt=spec.attempt,
            worktree=spec.worktree, handoff=spec.handoff, result=spec.result, root=root,
            started=started, backend=self.name, pid=os.getpid(), spine=spec.spine,
        )
        # Durable record BEFORE the crew starts (so a parent loss leaves a durable
        # `running` record).
        entries.append(entry)
        reg = registry_path(spec.work_id, root)
        save_registry(reg, entries)

        stdout_path, stderr_path = run_log_paths(spec.work_id, spec.gate, spec.role, spec.attempt, root)
        argv = build_crew_argv(
            spec.launcher, role=spec.role,
            handoff=(str(handoff_path) if handoff_path is not None else None),
            model=spec.model, session=entry["session_name"], spine=spec.spine,
        )
        env = _crew_door_env(work_id=spec.work_id, gate=spec.gate, role=spec.role, spine=spec.spine, root=root)
        exit_code = launch(argv, stdin=b"", env=env, stdout_path=stdout_path, stderr_path=stderr_path)

        final = finalize_from_exit_code(entry, exit_code=exit_code, result=spec.result, root=root, since=started)
        save_registry(reg, entries)
        if final != 0:
            _print_drift_hint_if_any(stderr_path)
        return final, entry

    def resume(self, session: str, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]:
        launch = launch if launch is not None else launch_process
        entry = find_entry(entries, session)
        if entry is None:
            raise CrewLaunchError(f"cannot resume: no crew recorded with session name {session!r}")
        if is_abandoned(entry):
            raise CrewLaunchError(f"cannot resume an abandoned crew {session!r}; use --abandon --relaunch instead")

        work_id = entry["work_id"]
        stored_handoff = entry.get("handoff")
        handoff_path: Path | None = None
        if stored_handoff is not None:
            handoff_path = Path(stored_handoff)
            if not handoff_path.is_absolute():
                handoff_path = root / stored_handoff
            if not handoff_path.is_file():
                raise CrewLaunchError(f"cannot resume: stored handoff is missing: {handoff_path}")

        stdout_path = Path(entry["stdout"])
        stderr_path = Path(entry["stderr"])
        if not stdout_path.is_absolute():
            stdout_path = root / entry["stdout"]
        if not stderr_path.is_absolute():
            stderr_path = root / entry["stderr"]

        # Dispatch time for THIS resume: freshness is judged against the moment we
        # relaunch the child, not the original launch, so a stale prior-attempt
        # result left at the path cannot pass this resume as `completed`.
        resumed_at = _now()
        entry["status"] = "running"
        entry["last_heartbeat"] = resumed_at
        entry["pid"] = os.getpid()
        reg = registry_path(work_id, root)
        save_registry(reg, entries)

        argv = build_crew_argv(
            entry.get("launcher", DEFAULT_LAUNCHER),
            role=entry["role"],
            handoff=(str(handoff_path) if handoff_path is not None else None),
            model=entry.get("model"),
            session=entry["session_name"],
            spine=entry.get("spine"),
        )
        env = _crew_door_env(
            work_id=entry["work_id"], gate=entry["gate"], role=entry["role"],
            spine=entry.get("spine"), root=root,
        )
        exit_code = launch(argv, stdin=b"", env=env, stdout_path=stdout_path, stderr_path=stderr_path)

        final = finalize_from_exit_code(entry, exit_code=exit_code, result=entry["result"], root=root, since=resumed_at)
        save_registry(reg, entries)
        if final != 0:
            _print_drift_hint_if_any(stderr_path)
        return final, entry


class ExternalBackend(CrewBackend):
    """Record-only backend: the crew is dispatched out-of-band (an Agent-tool
    subagent in the Constellation harness, where no headless `claude` CLI exists).
    `dispatch` spawns NOTHING — it records the durable entry (running, PID-less,
    keeping the `dispatch: "external"` marker) and returns `(None, entry)`; the
    caller verifies the result later. `resume` is unrecoverable-by-wrapper.

    `--spine` is REFUSED here: binding is impossible by construction when
    nothing is spawned and no environment is built, so accepting the option
    would record it in the registry and silently bind nothing. There is no
    out-of-band way to bind a child this backend never launches."""

    name = BACKEND_EXTERNAL

    def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[None, dict]:
        if spec.spine is not None:
            raise CrewLaunchError(
                f"refusing --spine {spec.spine!r} on the external backend: "
                f"ExternalBackend spawns no process and builds no environment, so "
                f"nothing binds the value into a child's SPINE_FILE/SPINE_SESSION. "
                f"--spine is only meaningful on the cli backend (--backend cli). A "
                f"spine-only dispatch here would leave the crew with no job at "
                f"all -- pass --handoff instead."
            )
        # `spec.spine is None` (checked above) plus `CrewSpec.__post_init__`'s
        # "needs a job" refusal together guarantee `spec.handoff` is not None by
        # this point -- the external backend never relaxes the handoff
        # requirement the cli backend does, since it cannot bind a spine.
        # Refuses if the handoff is missing, matching the spawn path's
        # precondition (with the external path's "record" wording).
        _require_handoff(spec.handoff, root, action="record")

        started = _now()
        entry = build_entry(
            work_id=spec.work_id, gate=spec.gate, role=spec.role, attempt=spec.attempt,
            worktree=spec.worktree, handoff=spec.handoff, result=spec.result, root=root,
            started=started, backend=self.name, pid=None,
            dispatch=DISPATCH_EXTERNAL, model=spec.model, spine=spec.spine,
        )
        # Durable record — the crew is dispatched by the caller out-of-band, so
        # unlike the spawn path there is no child to run and no completion to
        # finalize here (the caller verifies later with `verify`).
        entries.append(entry)
        save_registry(registry_path(spec.work_id, root), entries)
        return None, entry

    def resume(self, session: str, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]:
        # An externally-dispatched crew cannot be resumed by the wrapper: in-process
        # Agent-tool teammates cannot spawn background subagents, so external
        # dispatch is synchronous and recovery is out-of-band (Decision 6).
        raise CrewLaunchError(
            f"cannot resume external crew {session!r}: an externally-dispatched crew is "
            f"unrecoverable by the wrapper. SendMessage to the crew's recorded agentId to "
            f"resume it in place (skills/_shared/windows.md §2), else abandon and "
            f"relaunch it (--abandon {session} --relaunch)."
        )


# --------------------------------------------------------------------------- #
# backend selection — explicit override wins, else auto-detect (Decision 4)
# --------------------------------------------------------------------------- #
def select_backend(
    explicit: str | None,
    *,
    launcher: str = DEFAULT_LAUNCHER,
    which=shutil.which,
) -> CrewBackend:
    """Choose the crew-launch backend (Decision 4). PURE (given an injectable
    `which`): explicit override always wins; otherwise auto-detect from whether the
    headless `claude` CLI is on PATH.

      * `explicit in {"cli","external"}` -> that backend (explicit override wins);
      * `explicit in {None, "auto"}`     -> auto-detect: `which(launcher)` truthy
        (the CLI is on PATH) -> `CliBackend`; else `ExternalBackend`.

    `which` is injectable so tests control PATH presence without touching the real
    PATH. Fails visibly on an unknown token (no hidden fallback)."""
    if explicit == BACKEND_CLI:
        return CliBackend()
    if explicit == BACKEND_EXTERNAL:
        return ExternalBackend()
    if explicit not in (None, BACKEND_AUTO):
        raise CrewLaunchError(
            f"unknown backend {explicit!r} (expected one of "
            f"{BACKEND_AUTO!r}, {BACKEND_CLI!r}, {BACKEND_EXTERNAL!r})"
        )
    return CliBackend() if which(launcher) else ExternalBackend()


# --------------------------------------------------------------------------- #
# public module functions — thin backward-compatible wrappers over the backends
# --------------------------------------------------------------------------- #
def launch_crew(
    *,
    work_id: str,
    gate: str,
    role: str,
    handoff: str | None,
    result: str,
    worktree: str,
    model: str | None,
    launcher: str,
    attempt: int,
    root: Path,
    entries: list[dict],
    spine: str | None = None,
    launch: "callable | None" = None,
) -> tuple[int, dict]:
    """Record the durable entry BEFORE launching, run the crew foreground, then
    finalize the entry from the child exit code + result-artifact freshness.

    Thin wrapper over `CliBackend.dispatch` (signature + observable behavior
    preserved). Returns (exit_code, entry). Refuses if the handoff file is missing.
    `launch` defaults to the module-level `launch_process` resolved at CALL time,
    so monkeypatching the seam (in tests) takes effect even through the CLI."""
    spec = CrewSpec(
        work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
        worktree=worktree, attempt=attempt, model=model, launcher=launcher, spine=spine,
    )
    return CliBackend().dispatch(spec, root=root, entries=entries, launch=launch)


def resume_crew(
    *,
    session: str,
    root: Path,
    entries: list[dict],
    launch: "callable | None" = None,
) -> tuple[int, dict]:
    """Continue a recorded crew using its STORED session name and handoff, routing
    to the RECORDED entry's backend (Decision 6). `entry_backend(entry)` picks the
    backend: a `cli` entry relaunches the subprocess and finalizes (today's
    behavior); an `external` entry is unrecoverable-by-wrapper — `ExternalBackend`
    raises `CrewLaunchError` with the SendMessage-to-agentId / --abandon --relaunch
    guidance, so recovery NEVER silently spawns for an externally-dispatched crew.

    An unknown session has no entry to route from, so it falls to `CliBackend`,
    which raises the standard `cannot resume: no crew recorded` refusal (unchanged).
    `launch` defaults to the module-level `launch_process` resolved at CALL time."""
    entry = find_entry(entries, session)
    backend: CrewBackend = (
        ExternalBackend()
        if entry is not None and entry_backend(entry) == BACKEND_EXTERNAL
        else CliBackend()
    )
    return backend.resume(session, root=root, entries=entries, launch=launch)


def record_external_attempt(
    *,
    work_id: str,
    gate: str,
    role: str,
    handoff: str,
    result: str,
    worktree: str,
    model: str | None,
    attempt: int,
    root: Path,
    entries: list[dict],
    spine: str | None = None,
) -> dict:
    """Record a durable crew-runs.json entry for an EXTERNALLY-dispatched crew
    WITHOUT spawning a subprocess. Thin wrapper over `ExternalBackend.dispatch`
    (signature + observable behavior preserved: returns the entry dict).

    In the Agent-tool harness there is no headless `claude` CLI to spawn, so the
    implementer/reviewer is dispatched out-of-band and only the wrapper's DURABLE
    safety properties are wanted — a registry record, the duplicate-guard, and
    result-artifact verification. The entry is marked `dispatch="external"` and is
    PID-less (`pid=None`) so downstream tooling (recover_crews) can tell it apart
    from a spawned crew; it starts `running` so the duplicate-guard/recovery
    classifier treat it like an in-flight attempt until its result is verified
    (see `verify_external_result`). Refuses if the handoff file is missing."""
    spec = CrewSpec(
        work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
        worktree=worktree, attempt=attempt, model=model, spine=spine,
    )
    _, entry = ExternalBackend().dispatch(spec, root=root, entries=entries)
    return entry


def verify_external_result(entries: list[dict], session: str, root: Path) -> tuple[bool, dict]:
    """Verify whether the result artifact is present AND fresh for a recorded
    attempt and, when fresh, mark it resolved/`completed`. Thin wrapper over the
    backend-uniform `CrewBackend.verify` (signature + observable behavior
    preserved). Returns (fresh, entry). Reuses the canonical `result_fresh`."""
    return ExternalBackend().verify(entries, session, root=root)


def abandon_crew(entries: list[dict], session: str, root: Path) -> dict:
    """Mark a prior attempt abandoned (releases its hold on the gate/worktree)."""
    entry = find_entry(entries, session)
    if entry is None:
        raise CrewLaunchError(f"cannot abandon: no crew recorded with session name {session!r}")
    entry["abandoned"] = True
    entry["status"] = "abandoned"
    entry["completed_at"] = entry.get("completed_at") or _now()
    save_registry(registry_path(entry["work_id"], root), entries)
    return entry


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Safe foreground crew launcher with a durable recovery registry.")
    p.add_argument("--work-id", dest="work_id")
    p.add_argument("--gate")
    p.add_argument("--role")
    p.add_argument("--model")
    p.add_argument("--worktree", default=".")
    p.add_argument(
        "--handoff",
        help=(
            "path to the handoff document. Optional when --spine is given: a "
            "spine-only dispatch drives its bound spine instead of reading a "
            "document. Refused if neither --handoff nor --spine is given, and "
            "always required on the external backend (it cannot bind a spine)."
        ),
    )
    p.add_argument("--result")
    p.add_argument(
        "--spine",
        help=(
            "path to the spine/checklist file this crew will drive through its MCP "
            "door. On the cli backend, bound into the spawned child's SPINE_FILE "
            "(and its assignment-keyed SPINE_SESSION, derived from "
            "--work-id/--gate/--role) so the door resolves to this crew's own spine "
            "instead of .mcp.json's demo default. REFUSED on the external backend, "
            "which spawns no process and so binds nothing."
        ),
    )
    p.add_argument("--root", default=".", type=Path, help="repo root (default: cwd)")
    p.add_argument("--command", default=DEFAULT_LAUNCHER, help="agent launcher binary (override for non-default CLIs)")
    p.add_argument(
        "--dispatch",
        choices=[DISPATCH_SPAWN, DISPATCH_EXTERNAL],
        default=DISPATCH_SPAWN,
        help=(
            "LEGACY selector, kept backward compatible. 'spawn' (default) launches "
            "the agent CLI subprocess; 'external' records the durable registry entry "
            "+ duplicate-guard but spawns NOTHING (the crew is dispatched out-of-band, "
            "e.g. as an Agent-tool subagent); verify its result later with "
            "--verify-result. 'spawn' maps to the 'cli' backend, 'external' to the "
            "'external' backend. Superseded by --backend (which wins when given)."
        ),
    )
    p.add_argument(
        "--backend",
        choices=[BACKEND_AUTO, BACKEND_CLI, BACKEND_EXTERNAL],
        default=None,
        help=(
            "canonical crew-launch backend selector (Decisions 4-5). When given it "
            "wins over --dispatch: 'cli' spawns the agent CLI subprocess, 'external' "
            "records-only (out-of-band dispatch), 'auto' auto-detects (cli when a "
            "headless 'claude' CLI is on PATH, else external). When omitted the "
            "backend is derived from --dispatch (spawn->cli, external->external) with "
            "NO auto-detection, so existing invocations keep their exact behavior."
        ),
    )
    # recovery flags
    p.add_argument("--resume", help="continue a recorded crew by its session name")
    p.add_argument("--abandon", help="mark a prior crew abandoned (releases its gate/worktree hold)")
    p.add_argument("--relaunch", action="store_true", help="with --abandon: relaunch a fresh attempt (attempt++)")
    p.add_argument(
        "--verify-result",
        dest="verify_result",
        help="verify the result artifact for an externally-dispatched crew (by session name) "
             "and, if present, mark it completed in the registry",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)

    try:
        # --- verify an externally-dispatched crew's result ------------------ #
        if args.verify_result:
            entries = load_registry_for_resume(args.verify_result, root)
            fresh, entry = verify_external_result(entries, args.verify_result, root)
            if fresh:
                print(f"verify {entry['session_name']} -> fresh ({entry['status']})")
                return 0
            # Fail visibly, distinguishing the two modes. The entry is left
            # `running` (verify_external_result only completes on a fresh result).
            if entry.get("result_present"):
                print(
                    f"REFUSED: result artifact stale: {entry['result']} predates "
                    f"dispatch {entry['started_at']} "
                    f"({entry['session_name']} left {entry['status']})",
                    file=sys.stderr,
                )
            else:
                print(
                    f"REFUSED: result artifact absent: {entry['result']} "
                    f"({entry['session_name']} left {entry['status']})",
                    file=sys.stderr,
                )
            return 1

        # --- resume an existing crew ---------------------------------------- #
        if args.resume:
            entries = load_registry_for_resume(args.resume, root)
            exit_code, entry = resume_crew(session=args.resume, root=root, entries=entries)
            print(f"resumed {entry['session_name']} -> {entry['status']}")
            return exit_code

        # fresh / abandon+relaunch launch requires work-id/gate/role/result, plus
        # at least one of handoff/spine (checked separately below -- `handoff` is
        # NOT in this hard list, issue #559: a spine-only dispatch is legal).
        missing = [n for n in ("work_id", "gate", "role", "result")
                   if getattr(args, n) in (None, "")]
        if missing and not args.abandon:
            raise CrewLaunchError(
                "launch requires --work-id --gate --role --result, plus at least "
                "one of --handoff/--spine (or a recovery flag --resume/--abandon)"
            )
        if not args.abandon and not args.handoff and not args.spine:
            raise CrewLaunchError(
                "launch requires --handoff, --spine, or both (a crew needs a job)"
            )

        # The registry is keyed by work-id; for a bare `--abandon <session>`
        # (no --work-id) derive the work-id from the session name.
        if args.work_id:
            entries = load_registry(registry_path(args.work_id, root))
        elif args.abandon:
            entries = load_registry_for_resume(args.abandon, root)
        else:
            entries = []

        # Resolve the effective backend (Decisions 4-5). --backend wins when given;
        # otherwise derive it from the legacy --dispatch (spawn->cli,
        # external->external) with NO auto-detection, so an invocation with no new
        # flag resolves to the exact same backend it does today. Only an explicit
        # `--backend auto` opts into PATH auto-detection.
        backend_token = args.backend if args.backend is not None else (
            BACKEND_EXTERNAL if args.dispatch == DISPATCH_EXTERNAL else BACKEND_CLI
        )
        backend = select_backend(backend_token, launcher=args.command)

        # --- abandon (optionally relaunch) ---------------------------------- #
        if args.abandon:
            abandoned = abandon_crew(entries, args.abandon, root)
            print(f"abandoned {abandoned['session_name']}")
            if not args.relaunch:
                return 0
            # relaunch a fresh attempt for the SAME gate/role/worktree
            work_id = abandoned["work_id"]
            gate, role, worktree = abandoned["gate"], abandoned["role"], abandoned["worktree"]
            handoff = args.handoff or abandoned["handoff"]
            result = args.result or abandoned["result"]
            spine = args.spine or abandoned.get("spine")
            entries = load_registry(registry_path(work_id, root))
            attempt = next_attempt(entries, work_id, gate, role, worktree)
            spec = CrewSpec(
                work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
                worktree=worktree, attempt=attempt, model=args.model, launcher=args.command,
                spine=spine,
            )
            exit_code, entry = backend.dispatch(spec, root=root, entries=entries)
            if backend.name == BACKEND_EXTERNAL:
                print(f"relaunched {entry['session_name']} -> {entry['status']} (external)")
                return 0
            print(f"relaunched {entry['session_name']} -> {entry['status']}")
            return exit_code

        # --- fresh launch --------------------------------------------------- #
        dup = active_duplicate(entries, args.work_id, args.gate, args.role, args.worktree)
        if dup is not None:
            raise CrewLaunchError(
                f"refusing duplicate crew: an active attempt already holds "
                f"{args.gate}/{args.role}@{args.worktree}: {dup['session_name']} "
                f"(status {dup['status']!r}). Resolve it (recover_crews / --resume / "
                f"--abandon --relaunch) before launching."
            )
        attempt = next_attempt(entries, args.work_id, args.gate, args.role, args.worktree)
        spec = CrewSpec(
            work_id=args.work_id, gate=args.gate, role=args.role, handoff=args.handoff,
            result=args.result, worktree=args.worktree, attempt=attempt,
            model=args.model, launcher=args.command, spine=args.spine,
        )
        exit_code, entry = backend.dispatch(spec, root=root, entries=entries)
        if backend.name == BACKEND_EXTERNAL:
            print(f"crew {entry['session_name']} -> {entry['status']} "
                  f"(external: dispatched out-of-band; verify with "
                  f"--verify-result {entry['session_name']})")
            return 0
        print(f"crew {entry['session_name']} -> {entry['status']}")
        return exit_code
    except CrewLaunchError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


def load_registry_for_resume(session: str, root: Path) -> list[dict]:
    """Resolve the registry that holds `session` by parsing the work-id out of a
    `constellation/<work-id>/<gate>/<role>/attempt-<n>` session name.

    See `work_id_from_session` for why the parse is right-anchored."""
    return load_registry(registry_path(work_id_from_session(session), root))


if __name__ == "__main__":
    raise SystemExit(main())
