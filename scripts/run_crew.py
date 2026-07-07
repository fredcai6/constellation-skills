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
import subprocess
import sys
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
# pure helpers — paths, names, registry I/O
# --------------------------------------------------------------------------- #
def session_name(work_id: str, gate: str, role: str, attempt: int) -> str:
    """Deterministic, stable crew session name.

    `constellation/<work-id>/<gate>/<role>/attempt-<n>` — the same inputs always
    produce the same name, so a recovery can address an attempt unambiguously."""
    return f"constellation/{work_id}/{gate}/{role}/attempt-{attempt}"


def work_dir(work_id: str, root: Path) -> Path:
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
def build_crew_argv(launcher: str, *, role: str, handoff: str, model: str | None, session: str) -> list[str]:
    """PURE construction of the agent-CLI command line from role/handoff/model.

    Kept separate so tests can assert on the argv without spawning anything. The
    real launcher binary is configurable (`--command`) and defaults sensibly; the
    handoff is passed by path (the wrapper has already refused a missing one)."""
    argv: list[str] = [launcher, "--session", session, "--role", role, "--handoff", handoff]
    if model:
        argv += ["--model", model]
    return argv


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


def crew_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    """UTF-8-safe environment defaults for the child (without clobbering an
    explicit caller value)."""
    env = dict(os.environ if base_env is None else base_env)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


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


def launch_crew(
    *,
    work_id: str,
    gate: str,
    role: str,
    handoff: str,
    result: str,
    worktree: str,
    model: str | None,
    launcher: str,
    attempt: int,
    root: Path,
    entries: list[dict],
    launch: "callable | None" = None,
) -> tuple[int, dict]:
    """Record the durable entry BEFORE launching, run the crew foreground, then
    finalize the entry from the child exit code + result-artifact presence.

    Returns (exit_code, entry). Refuses if the handoff file is missing. The
    registry is persisted before the launch (so a parent loss leaves a durable
    `running` record) and again after the child exits. `launch` defaults to the
    module-level `launch_process` resolved at CALL time, so monkeypatching the
    seam (in tests) takes effect even through the CLI."""
    launch = launch if launch is not None else launch_process
    handoff_path = Path(handoff)
    if not handoff_path.is_absolute():
        handoff_path = root / handoff
    if not handoff_path.is_file():
        raise CrewLaunchError(f"refusing to launch: handoff file is missing: {handoff_path}")

    name = session_name(work_id, gate, role, attempt)
    stdout_path, stderr_path = run_log_paths(work_id, gate, role, attempt, root)
    started = _now()

    entry = {
        "crew_id": name,
        "work_id": work_id,
        "gate": gate,
        "role": role,
        "attempt": attempt,
        "status": "running",
        "session_name": name,
        "pid": os.getpid(),
        "worktree": worktree,
        "handoff": _relativize(handoff, root),
        "result": _relativize(result, root),
        "stdout": _relativize(str(stdout_path), root),
        "stderr": _relativize(str(stderr_path), root),
        "started_at": started,
        "last_heartbeat": started,
        "completed_at": None,
        "abandoned": False,
    }
    # Durable record BEFORE the crew starts.
    entries.append(entry)
    reg = registry_path(work_id, root)
    save_registry(reg, entries)

    argv = build_crew_argv(launcher, role=role, handoff=str(handoff_path), model=model, session=name)
    exit_code = launch(
        argv,
        stdin=b"",
        env=crew_env(),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )

    have_result = result_exists(result, root)
    fresh = result_fresh(result, root, started)
    entry["completed_at"] = _now()
    entry["last_heartbeat"] = entry["completed_at"]
    # A child that exits 0 but leaves only a STALE prior-attempt result at the
    # path (mtime predates this dispatch) is `failed`, not `completed`.
    if exit_code == 0 and fresh:
        entry["status"] = "completed"
        final = 0
    else:
        entry["status"] = "failed"
        final = exit_code if exit_code != 0 else 1
    entry["exit_code"] = exit_code
    entry["result_present"] = have_result
    entry["result_fresh"] = fresh
    save_registry(reg, entries)
    return final, entry


def resume_crew(
    *,
    session: str,
    root: Path,
    entries: list[dict],
    launch: "callable | None" = None,
) -> tuple[int, dict]:
    """Continue a recorded crew using its STORED session name and handoff. Refuses
    if the named crew is unknown or has been abandoned. `launch` defaults to the
    module-level `launch_process` resolved at CALL time (monkeypatch-friendly)."""
    launch = launch if launch is not None else launch_process
    entry = find_entry(entries, session)
    if entry is None:
        raise CrewLaunchError(f"cannot resume: no crew recorded with session name {session!r}")
    if is_abandoned(entry):
        raise CrewLaunchError(f"cannot resume an abandoned crew {session!r}; use --abandon --relaunch instead")

    work_id = entry["work_id"]
    handoff = entry["handoff"]
    handoff_path = Path(handoff)
    if not handoff_path.is_absolute():
        handoff_path = root / handoff
    if not handoff_path.is_file():
        raise CrewLaunchError(f"cannot resume: stored handoff is missing: {handoff_path}")

    stdout_path = Path(entry["stdout"])
    stderr_path = Path(entry["stderr"])
    if not stdout_path.is_absolute():
        stdout_path = root / entry["stdout"]
    if not stderr_path.is_absolute():
        stderr_path = root / entry["stderr"]

    # Dispatch time for THIS resume: freshness is judged against the moment we
    # relaunch the child, not the original launch, so a stale prior-attempt result
    # left at the path cannot pass this resume as `completed`.
    resumed_at = _now()
    entry["status"] = "running"
    entry["last_heartbeat"] = resumed_at
    entry["pid"] = os.getpid()
    reg = registry_path(work_id, root)
    save_registry(reg, entries)

    argv = build_crew_argv(
        entry.get("launcher", DEFAULT_LAUNCHER),
        role=entry["role"],
        handoff=str(handoff_path),
        model=entry.get("model"),
        session=entry["session_name"],
    )
    exit_code = launch(argv, stdin=b"", env=crew_env(), stdout_path=stdout_path, stderr_path=stderr_path)

    have_result = result_exists(entry["result"], root)
    fresh = result_fresh(entry["result"], root, resumed_at)
    entry["completed_at"] = _now()
    entry["last_heartbeat"] = entry["completed_at"]
    entry["status"] = "completed" if (exit_code == 0 and fresh) else "failed"
    entry["exit_code"] = exit_code
    entry["result_present"] = have_result
    entry["result_fresh"] = fresh
    save_registry(reg, entries)
    final = 0 if entry["status"] == "completed" else (exit_code if exit_code != 0 else 1)
    return final, entry


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
) -> dict:
    """Record a durable crew-runs.json entry for an EXTERNALLY-dispatched crew
    WITHOUT spawning a subprocess.

    This is the first-class form of the hand-improvisation Constellation runs do
    today: in the Agent-tool harness there is no headless `claude` CLI to spawn,
    so the implementer/reviewer is dispatched out-of-band (an Agent-tool subagent)
    and only the wrapper's DURABLE safety properties are wanted — a registry
    record, the duplicate-guard, and result-artifact verification. It reuses the
    same pure helpers as `launch_crew` (`session_name`, `run_log_paths`,
    `_relativize`, `save_registry`) so the registry logic is never forked.

    The entry is marked `dispatch="external"` and is PID-less (`pid=None`) so
    downstream tooling (recover_crews) can tell it apart from a spawned crew. It
    starts in `running` status so `active_duplicate`/`next_attempt` and the
    recovery classifier treat it exactly like a spawned in-flight attempt until
    its result is verified (see `verify_external_result`). Refuses if the handoff
    file is missing, matching the spawn path's precondition."""
    handoff_path = Path(handoff)
    if not handoff_path.is_absolute():
        handoff_path = root / handoff
    if not handoff_path.is_file():
        raise CrewLaunchError(f"refusing to record: handoff file is missing: {handoff_path}")

    name = session_name(work_id, gate, role, attempt)
    stdout_path, stderr_path = run_log_paths(work_id, gate, role, attempt, root)
    started = _now()

    entry = {
        "crew_id": name,
        "work_id": work_id,
        "gate": gate,
        "role": role,
        "attempt": attempt,
        "status": "running",
        "session_name": name,
        "dispatch": DISPATCH_EXTERNAL,
        "pid": None,
        "worktree": worktree,
        "handoff": _relativize(handoff, root),
        "result": _relativize(result, root),
        "stdout": _relativize(str(stdout_path), root),
        "stderr": _relativize(str(stderr_path), root),
        "started_at": started,
        "last_heartbeat": started,
        "completed_at": None,
        "abandoned": False,
    }
    if model:
        entry["model"] = model
    # Durable record — the crew is dispatched by the caller out-of-band, so unlike
    # the spawn path there is no child to run and no completion to finalize here.
    entries.append(entry)
    save_registry(registry_path(work_id, root), entries)
    return entry


def verify_external_result(entries: list[dict], session: str, root: Path) -> tuple[bool, dict]:
    """Verify whether the result artifact is present AND fresh for a recorded
    attempt and, when fresh, mark it resolved/`completed` in the registry.

    Returns (fresh, entry). Reuses the canonical `result_fresh` helper the spawn
    path uses — no duplicated freshness logic. Freshness is judged against the
    entry's `started_at` (its dispatch time), so a stale leftover result from a
    prior attempt at the same path does NOT clear the hold. Both `result_present`
    (existence) and `result_fresh` are recorded on the entry so the CLI can tell
    the two failure modes apart (MISSING vs STALE). Only a fresh result finalizes
    the entry to `completed` (clearing its hold on the gate/worktree); otherwise
    the entry is left `running` so the duplicate-guard keeps holding. Refuses if
    the named crew is unknown or has been abandoned."""
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
    p.add_argument("--handoff")
    p.add_argument("--result")
    p.add_argument("--root", default=".", type=Path, help="repo root (default: cwd)")
    p.add_argument("--command", default=DEFAULT_LAUNCHER, help="agent launcher binary (override for non-default CLIs)")
    p.add_argument(
        "--dispatch",
        choices=[DISPATCH_SPAWN, DISPATCH_EXTERNAL],
        default=DISPATCH_SPAWN,
        help=(
            "how to dispatch the crew. 'spawn' (default) launches the agent CLI "
            "subprocess. 'external' records the durable registry entry + duplicate-"
            "guard but spawns NOTHING (the crew is dispatched out-of-band, e.g. as "
            "an Agent-tool subagent); verify its result later with --verify-result."
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

        # fresh / abandon+relaunch launch requires the launch quartet
        missing = [n for n in ("work_id", "gate", "role", "handoff", "result")
                   if getattr(args, n) in (None, "")]
        if missing and not args.abandon:
            raise CrewLaunchError(
                "launch requires --work-id --gate --role --handoff --result "
                "(or a recovery flag --resume/--abandon)"
            )

        # The registry is keyed by work-id; for a bare `--abandon <session>`
        # (no --work-id) derive the work-id from the session name.
        if args.work_id:
            entries = load_registry(registry_path(args.work_id, root))
        elif args.abandon:
            entries = load_registry_for_resume(args.abandon, root)
        else:
            entries = []

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
            entries = load_registry(registry_path(work_id, root))
            attempt = next_attempt(entries, work_id, gate, role, worktree)
            if args.dispatch == DISPATCH_EXTERNAL:
                entry = record_external_attempt(
                    work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
                    worktree=worktree, model=args.model, attempt=attempt, root=root, entries=entries,
                )
                print(f"relaunched {entry['session_name']} -> {entry['status']} (external)")
                return 0
            exit_code, entry = launch_crew(
                work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
                worktree=worktree, model=args.model, launcher=args.command,
                attempt=attempt, root=root, entries=entries,
            )
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
        if args.dispatch == DISPATCH_EXTERNAL:
            entry = record_external_attempt(
                work_id=args.work_id, gate=args.gate, role=args.role, handoff=args.handoff,
                result=args.result, worktree=args.worktree, model=args.model,
                attempt=attempt, root=root, entries=entries,
            )
            print(f"crew {entry['session_name']} -> {entry['status']} "
                  f"(external: dispatched out-of-band; verify with "
                  f"--verify-result {entry['session_name']})")
            return 0
        exit_code, entry = launch_crew(
            work_id=args.work_id, gate=args.gate, role=args.role, handoff=args.handoff,
            result=args.result, worktree=args.worktree, model=args.model, launcher=args.command,
            attempt=attempt, root=root, entries=entries,
        )
        print(f"crew {entry['session_name']} -> {entry['status']}")
        return exit_code
    except CrewLaunchError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


def load_registry_for_resume(session: str, root: Path) -> list[dict]:
    """Resolve the registry that holds `session` by parsing the work-id from a
    `constellation/<work-id>/...` session name."""
    parts = session.split("/")
    if len(parts) < 2 or parts[0] != "constellation":
        raise CrewLaunchError(f"unrecognized session name {session!r} (expected constellation/<work-id>/...)")
    work_id = parts[1]
    return load_registry(registry_path(work_id, root))


if __name__ == "__main__":
    raise SystemExit(main())
