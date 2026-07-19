#!/usr/bin/env python
"""Workbench checklist engine: work one gated/survey plan through its gates.

The engine holds the canonical state; an agent transacts with it one step at a
time. It enforces *mechanism* (ordering, evidence shape, the rework cap, the
consolidation consistency guard) and never judges quality. See
docs/CHECKLIST_SCHEMA.md.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


def _utf8_stdio() -> None:
    """Captured stdio on Windows falls back to cp1252; checklist text with
    non-ascii then crashes every print. Field feedback (f1brainz
    engine-current-cp1252-crash): own the encoding here instead of requiring
    PYTHONIOENCODING at every call site."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()

GATED = "gated"
SURVEY = "survey"
TERMINAL = {"complete", "skipped"}
DEFAULT_REWORK_CAP = 3
DEFAULT_LEASE_STALE_SECONDS = 1800

# Verbs that mutate canonical state and therefore require the active session
# (once a lease exists). `current` is read-only; `claim`/`heartbeat`/`release`
# manage the lease itself and are handled separately.
MUTATING_VERBS = {
    "start", "advance", "record", "consolidate", "skip", "block",
    "reopen", "append", "attest", "waive", "attach", "flag-candidate",
    "amend",
}


# --------------------------------------------------------------------------- #
# gauge reader binding (#181) — loaded by file path so the engine drives whether
# it is run as a script or imported by a test via spec_from_file_location (both
# set __file__ to scripts/checklist_engine.py, so the sibling resolves). The load
# is fail-safe: if gauge_reader.py is missing or fails to import, `_gauge_reader`
# is None and the Trip policy (#182) simply does nothing — no reading, no advice,
# never forces, consistent with the whole governor's skip-on-uncertainty posture.
# --------------------------------------------------------------------------- #
def _load_gauge_reader():
    try:
        path = Path(__file__).resolve().parent / "gauge_reader.py"
        spec = importlib.util.spec_from_file_location("gauge_reader", path)
        mod = importlib.util.module_from_spec(spec)
        # Register BEFORE exec: gauge_reader's frozen @dataclass with a
        # `from __future__ import annotations` field resolves its own module via
        # sys.modules during class creation, which crashes if we exec unregistered.
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_gauge_reader = _load_gauge_reader()


class EngineError(Exception):
    """A refusal: the requested transition is not allowed. No exit-0."""


# --------------------------------------------------------------------------- #
# time source (single hook so tests can control time)
# --------------------------------------------------------------------------- #
def _now() -> str:
    """Current UTC time as an ISO-8601 string. The single module-level time
    hook: monkeypatch this in tests to control claim/heartbeat timestamps."""
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, tolerating a trailing 'Z'. Returns a
    timezone-aware datetime (assumes UTC when no offset is present)."""
    text = (value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def lease_stale_seconds(config: dict) -> int:
    return int((config or {}).get("lease_stale_seconds", DEFAULT_LEASE_STALE_SECONDS))


# --------------------------------------------------------------------------- #
# state helpers
# --------------------------------------------------------------------------- #
def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_config(cl: dict, base: Path | None) -> dict:
    """Resolve config: inline `config` wins; else follow `config_ref` to a file
    (tried relative to the working dir, then to the checklist's dir); else empty."""
    if isinstance(cl.get("config"), dict):
        return cl["config"]
    ref = cl.get("config_ref")
    if ref:
        if Path(ref).is_absolute():
            candidates = [Path(ref)]
        else:
            candidates = [Path.cwd() / ref] + ([base / ref] if base is not None else [])
        for path in candidates:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data.get("config", data)
    return {}


def rework_cap(config: dict) -> int:
    return int((config or {}).get("rework_cap", DEFAULT_REWORK_CAP))


def task(cl: dict, iid: str) -> dict:
    if iid not in cl.get("tasks", {}):
        raise EngineError(f"no such item {iid!r}")
    return cl["tasks"][iid]


def active_id(cl: dict) -> str | None:
    """First item (in order) that is not yet terminal."""
    for iid in cl.get("items", []):
        if cl["tasks"][iid]["status"] not in TERMINAL:
            return iid
    return None


# --------------------------------------------------------------------------- #
# doctrine rail (#138, channel A) — engine-carried doctrine at every decision
# point. `dispatch()` appends the position-derived rail to the success output of
# the railed verbs; `main()` appends the check-failure rail to the REFUSED path.
# The verb functions themselves stay PURE (their return values are unchanged) so
# existing exact-equality tests keep passing — the rail rides only the CLI
# boundary chokepoints. No new mechanism, verb, schema, or per-step authored text.
#
# CANONICALITY: This table is the canonical enforcement source;
# `_shared/global-everyone.md` elaborates and cites it; on conflict the table
# wins. The five strings are FROZEN and verbatim (measurement precondition for
# #145) — do not paraphrase; token placeholders {id}/{n}/{imperative} are the
# only substituted parts.
# --------------------------------------------------------------------------- #
RAIL_VERBS = {"claim", "current", "start", "advance", "attest", "attach"}

_RAIL_STRINGS = {
    "early": "Work the engine never saw did not happen. Run the step's checks, "
             "then `attest` and `advance {id}`.",
    "mid-flight": "A working solution is the MIDDLE of this run — you are {n} "
                  "steps from done. Next: {imperative}. Run it.",
    "check-failure": "This check failed; that verdict is scoped to this check, "
                     "not the approach. Do the missing work and `attest`/`attach` "
                     "the evidence, or escalate with `block`/`waive` and a reason. "
                     "Report 'this check failed', never 'this step is impossible'. "
                     "Quiet abandonment and fabricated evidence are the two "
                     "forbidden exits.",
    "near-terminal": "The finish is a sequence, not an announcement. Final "
                     "`advance` first, then `release` — the journal, not your "
                     "prose, is the proof.",
    "terminal": "Release is your last journaled action. Run `release`; do not "
                "claim it.",
}


def _rail_position(cl: dict) -> tuple[str, dict]:
    """Derive the decision-point position for a gated checklist and the tokens its
    rail string needs. ``remaining`` is the ordered list of not-yet-terminal items;
    its head (``remaining[0]``) is the active gate.

    - ``n == 0`` -> ``terminal`` (only ``release`` remains).
    - ``n == 1`` -> ``near-terminal`` (active step is the last before release).
    - active gate is the first item -> ``early``.
    - otherwise -> ``mid-flight``.
    """
    remaining = [iid for iid in cl["items"] if cl["tasks"][iid]["status"] not in TERMINAL]
    n = len(remaining)
    if n == 0:
        return "terminal", {}
    active = remaining[0]
    if n == 1:
        return "near-terminal", {}
    if active == cl["items"][0]:
        return "early", {"id": active}
    return "mid-flight", {"n": n, "imperative": cl["tasks"][active].get("imperative", "")}


def _rail(point: str, cl: dict) -> str:
    """Return the doctrine block to append at a decision point, or ``""`` when no
    rail applies. Non-gated (survey) checklists get NO rail. ``point`` is either
    ``"check-failure"`` (the REFUSED path, no token substitution) or any railed verb
    name, in which case the position is derived from ``items`` state."""
    if cl.get("type") != GATED:
        return ""
    if point == "check-failure":
        text = _RAIL_STRINGS["check-failure"]
    else:
        pos, tokens = _rail_position(cl)
        text = _RAIL_STRINGS[pos]
        for key, value in tokens.items():
            text = text.replace("{" + key + "}", str(value))
    return f"\n\nRAIL: {text}"


def _new_evidence_id(t: dict) -> str:
    return f"e-{t['id']}-{len(t.get('evidence', [])) + 1}"


def _find_evidence(cl: dict, eid: str) -> dict | None:
    """Find an evidence item by id across ALL tasks' evidence lists. Evidence ids
    are globally unique (`e-<task>-<n>`), so a checklist-wide search lets one task's
    artifact postcondition be satisfied by reference to an artifact attached to a
    sibling task (see `attest --evidence`). Returns the evidence dict or None."""
    for t in cl.get("tasks", {}).values():
        for ev in t.get("evidence", []):
            if ev.get("id") == eid:
                return ev
    return None


# --------------------------------------------------------------------------- #
# git-change-policy — mechanical artifact-output guardrails (#8)
#
# Split deliberately into a PURE evaluator (no git, no filesystem) and a thin
# git collector, so the policy semantics are fully unit-testable without a
# working tree. The evaluator decides VIOLATIONS; the collector gathers the
# changed-file facts (path/size/binary) the evaluator consumes.
# --------------------------------------------------------------------------- #
def _glob_to_regex(pattern: str) -> str:
    r"""Translate a path glob into an anchored regex. `**` matches across path
    separators (any number of segments); a single `*` matches within one
    segment (no `/`); `?` matches one non-separator char. A trailing `/**` also
    matches the directory itself (so `records/**` covers `records/x` and
    `records/a/b`). We do NOT use `PurePosixPath.match`: before Python 3.13 it
    treats `**` as a single-segment wildcard, so `records/**` would miss
    `records/a/b` — exactly the nested record-dump case this policy must catch."""
    # `records/**` should also match `records/a/b` -> normalize a trailing
    # `/**` to `(/.*)?` by handling it as part of the `**` translation below.
    out: list[str] = []
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if i + 1 < n and pattern[i + 1] == "*":
                # `**` (optionally `/**` or `**/`) crosses separators
                i += 2
                if i < n and pattern[i] == "/":
                    i += 1
                    out.append("(?:.*/)?")  # zero or more leading segments
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")  # single star: within a segment
        elif c == "?":
            out.append("[^/]")
        elif c == "/":
            # collapse a `/**` suffix so the dir prefix also matches the dir
            if pattern[i:] == "/**":
                out.append("(?:/.*)?")
                i = n
                continue
            out.append("/")
        else:
            out.append(re.escape(c))
        i += 1
    return "^" + "".join(out) + "$"


def _glob_match(path: str, pattern: str) -> bool:
    """Match a POSIX-style path against a glob pattern with recursive `**`.

    We normalize to forward slashes so Windows-style paths still match. A bare
    basename pattern like `*.parquet` matches on any segment (it is also tried
    against the final path component) so `sub/dir/x.parquet` is caught."""
    norm = (path or "").replace("\\", "/")
    regex = _glob_to_regex(pattern)
    if re.match(regex, norm):
        return True
    # basename-style pattern (no separator): also match the final component,
    # mirroring `*.parquet` matching anywhere in the tree.
    if "/" not in pattern:
        return bool(re.match(regex, norm.rsplit("/", 1)[-1]))
    return False


def evaluate_git_change_policy(files: list[dict], policy: dict) -> list[str]:
    """PURE policy evaluation. Returns a list of human-readable violations
    (empty == satisfied). `files` is a list of dicts:
    `{"path": str, "size": int, "binary": bool}`. No git, no filesystem — this
    is the fully unit-testable core.

    A file VIOLATES if:
      - it matches any `deny_globs` entry (an explicit deny ALWAYS denies — it
        beats an allow); OR
      - its size exceeds `max_file_bytes`; OR
      - it is binary and `require_human_waiver_for_binary` is true,
    UNLESS the path matches an `allow_globs` entry, which exempts it from the
    SIZE and BINARY checks only (deny still denies). Empty/missing policy lists
    mean "no constraint of that kind"; a clean (empty) file list yields zero
    violations."""
    policy = policy or {}
    deny = policy.get("deny_globs") or []
    allow = policy.get("allow_globs") or []
    max_bytes = policy.get("max_file_bytes")
    binary_needs_waiver = bool(policy.get("require_human_waiver_for_binary"))

    violations: list[str] = []
    for f in files:
        path = f.get("path", "")
        size = f.get("size")
        is_binary = bool(f.get("binary"))

        denied = next((g for g in deny if _glob_match(path, g)), None)
        if denied is not None:
            violations.append(f"{path}: matches deny glob {denied!r}")
            # explicit deny is terminal for this file; allow cannot rescue it
            continue

        allowed = any(_glob_match(path, g) for g in allow)
        if allowed:
            continue  # exempt from size/binary checks

        if isinstance(max_bytes, (int, float)) and isinstance(size, (int, float)) and size > max_bytes:
            violations.append(f"{path}: size {int(size)}B exceeds max_file_bytes {int(max_bytes)}")
        if is_binary and binary_needs_waiver:
            violations.append(f"{path}: binary/blob addition requires a human waiver")
    return violations


def _git(args: list[str], base_dir: Path | None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(base_dir) if base_dir else None,
        capture_output=True, text=True,
    )


def _collect_changed_files(policy: dict, base_dir: Path | None) -> list[dict]:
    """Thin git collector: gather `{path, size, binary}` for the changed files.

    mode `staged` -> `git diff --cached`; mode `branch` -> `git diff <base>...HEAD`.
    Binary detection uses `git diff --numstat` (a binary file shows `-\t-`).
    Size comes from the working-tree file when present, else `git cat-file` on
    the staged/HEAD blob. Kept small and isolated so the PURE evaluator carries
    the testable logic."""
    policy = policy or {}
    mode = policy.get("mode", "staged")
    if mode == "branch":
        base = policy.get("base", "origin/main")
        name_args = ["diff", "--name-only", f"{base}...HEAD"]
        numstat_args = ["diff", "--numstat", f"{base}...HEAD"]
        blob_ref = "HEAD"
    else:
        name_args = ["diff", "--cached", "--name-only"]
        numstat_args = ["diff", "--cached", "--numstat"]
        blob_ref = ":"  # the staged index entry for a path is `:<path>`

    names_proc = _git(name_args, base_dir)
    if names_proc.returncode != 0:
        raise EngineError(f"git-change-policy: collecting changed files failed: {names_proc.stderr.strip()}")
    paths = [ln for ln in names_proc.stdout.splitlines() if ln.strip()]

    binary_paths: set[str] = set()
    numstat_proc = _git(numstat_args, base_dir)
    if numstat_proc.returncode == 0:
        for line in numstat_proc.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0] == "-" and parts[1] == "-":
                binary_paths.add(parts[2])

    root = base_dir or Path.cwd()
    files: list[dict] = []
    for path in paths:
        size = None
        wt = root / path
        if wt.is_file():
            try:
                size = wt.stat().st_size
            except OSError:
                size = None
        if size is None:
            ref = f"{blob_ref}{path}" if blob_ref == ":" else f"{blob_ref}:{path}"
            cat = _git(["cat-file", "-s", ref], base_dir)
            if cat.returncode == 0:
                try:
                    size = int(cat.stdout.strip())
                except ValueError:
                    size = None
        files.append({"path": path, "size": size, "binary": path in binary_paths})
    return files


def _bash_candidates_from_git(git_path: str) -> list[str]:
    """Candidate bash.exe paths derived from a git executable path. Windows
    backstop for when `git` is on PATH but its bash directory is not.

    `shutil.which("git")` resolves git to varying depths — `…\\Git\\mingw64\\bin\\git.exe`
    (Git root = great-grandparent), `…\\Git\\cmd\\git.exe` (grandparent), or
    `…\\Git\\bin\\git.exe` (parent) — while bash always lives at `…\\Git\\bin\\bash.exe`
    and `…\\Git\\usr\\bin\\bash.exe`. Walk up 4 ancestor directories and, for each,
    emit both bash locations. Pure: no filesystem access (the caller filters by
    existence). Uses PureWindowsPath so it parses Windows paths the same on any host
    OS — this helper only runs on Windows but its unit tests run anywhere."""
    candidates: list[str] = []
    d = PureWindowsPath(git_path).parent
    for _ in range(4):
        candidates.append(str(d / "bin" / "bash.exe"))
        candidates.append(str(d / "usr" / "bin" / "bash.exe"))
        d = d.parent
    return candidates


def _find_posix_shell() -> str | None:
    """Locate a POSIX shell to run `command` checks under: bash on Windows, sh on
    POSIX. Returns the shell path, or None if none is found. On Windows
    `shutil.which("bash")` is the primary lookup (Git for Windows usually puts its
    bash dir on PATH); the git-derived candidates are a backstop for when git is on
    PATH but bash is not."""
    if os.name != "nt":
        return shutil.which("sh")
    found = shutil.which("bash")
    if found:
        return found
    git = shutil.which("git")
    if git:
        for cand in _bash_candidates_from_git(git):
            if os.path.isfile(cand):
                return cand
    return shutil.which("sh")


def _run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]:
    """Run a `command`-kind check. Route it through a POSIX shell when one is found
    (so authored grep/&&/pipe checks behave the same on Windows as on POSIX);
    when NO POSIX shell is available, FAIL VISIBLY instead of routing the POSIX-form
    check text through the platform shell (cmd.exe on Windows) — a silent cmd.exe run
    would misinterpret grep/&&/pipe checks and could false-pass or false-fail. In that
    case we do not call subprocess.run at all: we return a synthetic failed result
    (returncode 127) whose stderr names the missing shell. Returns (completed process,
    marker) where marker is "posix" or "no-posix-shell"; POSIX-form text is never run
    through cmd.exe."""
    shell = _find_posix_shell()
    if shell:
        proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
        return proc, "posix"
    proc = subprocess.CompletedProcess(
        args=command,
        returncode=127,
        stdout="",
        stderr=(
            "no POSIX shell (bash/sh) found to run a command-type check; the engine "
            "refuses to run POSIX-form check text through cmd.exe — install Git for "
            "Windows (bash) or a POSIX sh so command checks can run"
        ),
    )
    return proc, "no-posix-shell"


def _check_condition(cond: dict, t: dict, base_dir: Path | None = None) -> bool:
    """Verify one condition. command -> run it; artifact -> presence/match;
    git-change-policy -> evaluate the staged/branch diff against an artifact
    policy (#8); null -> the agent must have attested it (trust but verify).

    A WAIVED condition is honored without re-running its check: a human override
    (see `waive`) has accepted the condition, and re-running the command would
    overwrite `satisfied` and silently un-waive it at every `advance`."""
    if cond.get("waived"):
        return True
    if cond.get("attested"):
        # An artifact postcondition satisfied by cross-task reference (see `attest
        # --evidence`): honor it without re-scanning, since the artifact branch only
        # looks at this task's OWN evidence and would otherwise reset it to False.
        return True
    chk = cond.get("check")
    if chk is None:
        return bool(cond.get("satisfied"))
    kind = chk.get("kind")
    if kind == "command":
        proc, shell_marker = _run_check_command(chk["command"])
        cond["satisfied"] = proc.returncode == 0
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "command-output",
                "payload": {"cmd": chk["command"], "exit": proc.returncode, "shell": shell_marker},
                "produced_by": "engine",
                "ts": "",
            }
        )
        if cond["satisfied"]:
            cond["satisfied_by"] = eid
        return cond["satisfied"]
    if kind == "artifact":
        want = chk.get("match", {})
        for ev in t.get("evidence", []):
            if ev.get("superseded"):
                # A superseded evidence item (see `reopen` cascade) is inert: it
                # must not re-satisfy a gate from a stale approval after reopen.
                continue
            if ev.get("type") == chk["evidence_type"] and all(
                ev.get("payload", {}).get(k) == v for k, v in want.items()
            ):
                cond["satisfied"] = True
                cond["satisfied_by"] = ev["id"]
                return True
        cond["satisfied"] = False
        return False
    if kind == "git-change-policy":
        files = _collect_changed_files(chk, base_dir)
        violations = evaluate_git_change_policy(files, chk)
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "artifact-policy",
                "payload": {
                    "mode": chk.get("mode", "staged"),
                    "violations": violations,
                    "files_checked": len(files),
                },
                "produced_by": "engine",
                "ts": "",
            }
        )
        cond["satisfied"] = not violations
        if cond["satisfied"]:
            cond["satisfied_by"] = eid
        return cond["satisfied"]
    raise EngineError(f"unknown check kind {kind!r}")


# --------------------------------------------------------------------------- #
# session leasing — actor authority over the checklist STATE
# --------------------------------------------------------------------------- #
def _is_stale(session: dict | None, config: dict) -> bool:
    """A lease is stale when its `last_heartbeat` is older than the configured
    timeout. A missing/closed lease, or one with an unparseable heartbeat, is
    treated conservatively (a missing one is not 'stale'; it just isn't active).
    Tests can drive staleness by writing an old `last_heartbeat` directly, or by
    monkeypatching `_now`."""
    if not session or session.get("status") != "active":
        return False
    hb = session.get("last_heartbeat")
    if not hb:
        return True
    try:
        age = (_parse_ts(_now()) - _parse_ts(hb)).total_seconds()
    except (ValueError, TypeError):
        return True
    return age > lease_stale_seconds(config)


def _active_lease(cl: dict) -> dict | None:
    """The lease iff it is present and `status: active`; else None. A released
    lease does not gate mutation."""
    sess = cl.get("engine_session")
    if isinstance(sess, dict) and sess.get("status") == "active":
        return sess
    return None


def _refresh_owner_heartbeat(cl: dict, session_id: str | None) -> None:
    """Stamp liveness: if `session_id` owns the active lease, advance its
    `last_heartbeat` to now. No-op when there is no active lease, a different
    session owns it, or `session_id` is falsy. Called after every mutating verb
    the owner issues *and that succeeds*, so an actively-working owner never goes
    stale and a genuine idle gap self-heals on the owner's next successful verb.
    A refused verb never reaches here, so a failing-only session can still go
    stale. It never writes a takeover record — the owner resuming its own work is
    not a takeover."""
    lease = _active_lease(cl)
    if lease is not None and session_id and session_id == lease.get("session_id"):
        lease["last_heartbeat"] = _now()


def require_session(cl: dict, verb: str, session_id: str | None, config: dict) -> None:
    """The actor-authority gate. Mutating verbs are session-gated only ONCE an
    ACTIVE lease exists; with no active lease a missing `--session-id` is fine
    (legacy checklists/templates have no `engine_session`).

    Staleness gates **non-owners only** — it answers "has the owner gone quiet
    long enough that someone else may seize the lease?" The rightful owner is
    NEVER blocked by its own staleness, because an owner issuing a verb IS the
    liveness signal (the stamp `_refresh_owner_heartbeat` records it). So the
    owner always passes; a non-owner is refused — with a `claim` instruction if
    the lease is stale, or an ownership instruction if it is a different,
    still-active lease."""
    if verb not in MUTATING_VERBS:
        return
    lease = _active_lease(cl)
    if lease is None:
        return  # no lease claimed: legacy behavior, no session needed
    if session_id == lease.get("session_id"):
        return  # the owner is never blocked by its own staleness
    if _is_stale(lease, config):
        raise EngineError(
            f"checklist lease {lease.get('session_id')!r} is stale; "
            f"`claim` it (same id or --force --reason) before mutating"
        )
    raise EngineError(
        f"checklist is owned by active session {lease.get('session_id')!r}; "
        f"pass --session-id {lease.get('session_id')!r} or take over with "
        f"`claim --force --reason ...`"
    )


def claim(
    cl: dict,
    session_id: str,
    claimed_by: str,
    worktree: str,
    config: dict,
    force: bool = False,
    reason: str | None = None,
) -> str:
    """Claim ownership of the checklist for `session_id`.

    - No existing/closed/stale lease: create a fresh active lease.
    - Same `session_id` already active: idempotent resume; refresh heartbeat.
    - A DIFFERENT active, non-stale lease: refuse unless `--force --reason`.
    - `--force` takes over any lease, recording the prior session in
      `previous_session_id` and the `takeover_reason` (force needs a reason)."""
    if not (session_id or "").strip():
        raise EngineError("claim requires a non-empty --session-id")
    reason = (reason or "").strip() or None
    if force and not reason:
        raise EngineError("claim --force requires a non-empty --reason")

    existing = cl.get("engine_session")
    existing = existing if isinstance(existing, dict) else None
    now = _now()

    # idempotent same-session resume of an active lease
    if (
        existing
        and existing.get("status") == "active"
        and existing.get("session_id") == session_id
        and not force
    ):
        existing["last_heartbeat"] = now
        existing["claimed_by"] = claimed_by or existing.get("claimed_by")
        if worktree is not None:
            existing["worktree"] = worktree
        return f"resumed lease {session_id} (heartbeat refreshed)"

    blocking = (
        existing
        and existing.get("status") == "active"
        and existing.get("session_id") != session_id
        and not _is_stale(existing, config)
    )
    if blocking and not force:
        raise EngineError(
            f"checklist already owned by active session "
            f"{existing.get('session_id')!r}; use `claim --force --reason ...` to take over"
        )

    previous_id = None
    takeover_reason = None
    if existing and existing.get("session_id") and existing.get("session_id") != session_id:
        if force:
            previous_id = existing.get("session_id")
            takeover_reason = reason
        elif _is_stale(existing, config):
            previous_id = existing.get("session_id")
            takeover_reason = reason or "stale lease reclaimed"

    cl["engine_session"] = {
        "session_id": session_id,
        "status": "active",
        "claimed_at": now,
        "last_heartbeat": now,
        "claimed_by": claimed_by,
        "worktree": worktree,
        "previous_session_id": previous_id,
        "takeover_reason": takeover_reason,
    }
    if force and previous_id:
        return f"FORCED takeover of {previous_id} by {session_id} -> active (reason: {takeover_reason})"
    if previous_id:
        return f"reclaimed stale lease {previous_id}; {session_id} -> active"
    return f"claimed lease {session_id} -> active"


def heartbeat(cl: dict, session_id: str) -> str:
    """Refresh the active lease's `last_heartbeat`. Only the owning session may
    heartbeat; refuses if there is no active lease or the id mismatches."""
    lease = _active_lease(cl)
    if lease is None:
        raise EngineError("no active lease to heartbeat; `claim` first")
    if session_id != lease.get("session_id"):
        raise EngineError(
            f"heartbeat session {session_id!r} does not own the lease "
            f"({lease.get('session_id')!r})"
        )
    lease["last_heartbeat"] = _now()
    return f"heartbeat {session_id} @ {lease['last_heartbeat']}"


def release(cl: dict, session_id: str, force: bool = False, reason: str | None = None) -> str:
    """Close the lease (`status: released`). Only the owning session may release,
    unless `--force --reason` is given. After release, a new `claim` succeeds."""
    sess = cl.get("engine_session")
    if not isinstance(sess, dict) or sess.get("status") != "active":
        raise EngineError("no active lease to release")
    if session_id != sess.get("session_id") and not force:
        raise EngineError(
            f"release session {session_id!r} does not own the lease "
            f"({sess.get('session_id')!r}); use --force --reason to override"
        )
    if force and session_id != sess.get("session_id") and not (reason or "").strip():
        raise EngineError("release --force (non-owner) requires a non-empty --reason")
    sess["status"] = "released"
    sess["released_at"] = _now()
    return f"released lease {sess.get('session_id')}"


def _lease_line(cl: dict) -> str | None:
    """Human-readable active-lease summary for `current`, or None if no lease."""
    sess = cl.get("engine_session")
    if not isinstance(sess, dict):
        return None
    status = sess.get("status")
    if status == "active":
        return f"LEASE active: {sess.get('session_id')} (by {sess.get('claimed_by')}, heartbeat {sess.get('last_heartbeat')})"
    return f"LEASE {status}: {sess.get('session_id')}"


# --------------------------------------------------------------------------- #
# why-capture + refresh primitives (#179) — Modules 1 & 4.
#
# A top-level append-only `why_trail` records the running understanding at each
# non-exempt `advance`. Entries are NEVER mutated or deleted; a `reopen` freshens
# the digest by APPENDING a reopen-marker for each gate it resets, so a reopened
# gate's stale understanding stops being "latest" without editing any prior row.
# The live DIGEST is the latest non-mechanical, non-superseded `why`. All of this
# is backward compatible: a spine with no `why_trail` gets one on first write
# (setdefault), and a task with no `why_exempt` is treated as NOT exempt (opt-out
# default) — so a legacy gate REFUSES cleanly on a why-less advance, never crashes.
# --------------------------------------------------------------------------- #
def _append_why(cl: dict, gate: str, why: str | None, mechanical: bool) -> str:
    """Append one why-record to the top-level append-only `why_trail` and return
    its id. `why` is the running-understanding text (None for a mechanical step).
    `setdefault` creates `why_trail` on first write so legacy spines drive
    unchanged. Never mutates or removes a prior entry."""
    trail = cl.setdefault("why_trail", [])
    wid = f"w-{len(trail) + 1}"
    trail.append({
        "id": wid, "gate": gate, "why": why,
        "mechanical": bool(mechanical), "ts": _now(),
    })
    return wid


def _append_reopen_marker(cl: dict, gate: str, reason: str) -> None:
    """Append a reopen-marker to `why_trail`: the append-only way a `reopen`
    FRESHENS the digest. A why-record for `gate` is stale once a later reopen-marker
    names that gate, so `_latest_why_record` skips past it — no prior row edited."""
    trail = cl.setdefault("why_trail", [])
    wid = f"w-{len(trail) + 1}"
    trail.append({
        "id": wid, "gate": gate, "reopen": True,
        "reason": reason, "ts": _now(),
    })


def _latest_why_record(cl: dict) -> dict | None:
    """The live why-record: the newest `why_trail` entry that is a real (non-
    mechanical) understanding AND has not been superseded by a later reopen of its
    own gate. Returns the entry dict, or None when no live understanding exists.
    A mechanical marker is never live (it carries no understanding)."""
    trail = cl.get("why_trail", []) or []
    for i in range(len(trail) - 1, -1, -1):
        e = trail[i]
        if e.get("reopen") or e.get("mechanical") or e.get("why") is None:
            continue
        gate = e.get("gate")
        if any(trail[j].get("reopen") and trail[j].get("gate") == gate
               for j in range(i + 1, len(trail))):
            continue  # a later reopen of this gate freshened past this understanding
        return e
    return None


def _digest(cl: dict) -> str | None:
    """The live digest text: the latest non-mechanical, non-superseded `why`, or
    None when no live understanding exists."""
    rec = _latest_why_record(cl)
    return rec.get("why") if rec else None


def has_pending_refresh_request(cl: dict, gate: str) -> bool:
    """Pure predicate: True iff a pending `refresh-request` targets `gate`.

    A refresh-request is a `refresh-request`-typed evidence item (attached via the
    ordinary `attach` verb) whose payload carries POINTERS ONLY: `seam` = the gate
    it concerns, `why_ref` = the why-record id it was raised against — never copies
    of state. It is pending while present and not superseded (the reopen cascade
    supersedes evidence; the flow that consumes/fulfils it is #183). No shared
    mutable state, no side effects."""
    for t in cl.get("tasks", {}).values():
        if not isinstance(t, dict):
            continue
        for ev in t.get("evidence", []) or []:
            if not isinstance(ev, dict) or ev.get("type") != "refresh-request":
                continue
            if ev.get("superseded"):
                continue
            if (ev.get("payload") or {}).get("seam") == gate:
                return True
    return False


def _why_suffix(cl: dict, aid: str | None) -> str:
    """The why-capture lines appended to `current` (gated checklists only): a
    `DIGEST:` line carrying the live understanding, and a `REFRESH REQUESTED:` line
    when a pending refresh-request targets the active gate. Empty for surveys or
    when neither applies. No new verb — these ride the read-only `current`."""
    if cl.get("type") != GATED:
        return ""
    out = ""
    digest = _digest(cl)
    if digest is not None:
        out += f"\nDIGEST: {digest}"
    if aid is not None and has_pending_refresh_request(cl, aid):
        rec = _latest_why_record(cl)
        ref = f" (why_ref {rec['id']})" if rec else ""
        out += f"\nREFRESH REQUESTED: {aid}{ref}"
    return out


# --------------------------------------------------------------------------- #
# Trip — two-band gate policy (#182), Module 3 of the Context Governor (epic-178).
#
# At each GATE BOUNDARY the engine reads the context-fullness gauge (#181's reader)
# and applies model-keyed thresholds (#181's `thresholds_for`). Two bands, both
# fail-safe on a missing/stale reading (`read()` collapses stale -> None inside):
#
#   SOFT (fill >= soft): an ADVISORY stop-by-default question rides the read-only
#     `current` output — "you've used most of your context; unless you're basically
#     done, hand off here at this seam." SOFT NEVER forces; the agent may decline
#     (any reason accepted in v1 — we do not police reason quality; declining is
#     simply choosing to `advance`, which SOFT never blocks).
#   HARD (fill >= hard): the engine REFUSES to `advance` until a `refresh-request`
#     exists for the gate (#179's `has_pending_refresh_request`), pointing at the
#     exact `attach` command. HARD ALWAYS forces.
#
# CHECKS AT GATE BOUNDARIES ONLY — the mid-gate runaway is a deliberately accepted
# limit; there is no mid-gate check. Like the doctrine rail, this policy rides the
# CLI-boundary chokepoints in `dispatch` so the verb functions stay PURE (their
# return values are unchanged, so existing exact-equality tests keep passing): SOFT
# is a suffix on `current`'s dispatch output; HARD is a pre-`advance` guard.
#
# The agent NEVER introspects fill: the engine supplies the fill fact, the agent
# supplies the stop-point judgment.
#
# ROLLOUT CAVEAT: do NOT enable/exercise the HARD band in production until #183's
# tier-skill wiring lands — an agent hitting HARD writes a refresh-request with no
# invoker watching and can strand. Both bands are built and tested here; this is a
# rollout-ordering constraint, not a build dependency.
# --------------------------------------------------------------------------- #
def _gauge_path(base_dir: Path | None) -> Path | None:
    """The gauge file for this checklist: `.agent-work/<work_id>/gauge.json`, a
    SIBLING of the spine — #180's writer drops it at `Path(spine).parent /
    "gauge.json"`, and `base_dir` IS that spine directory. Returns None when the
    location is unresolvable (no `base_dir`, e.g. a checklist processed without a
    file path): an unresolvable work_id yields no reading and no advice."""
    if base_dir is None:
        return None
    return Path(base_dir) / "gauge.json"


def _read_gauge(base_dir: Path | None):
    """Read a fresh `Reading` for this checklist, or None. Fail-safe: an absent
    reader binding or unresolvable path collapses to None, and the reader itself
    never raises (every failure mode — absent/corrupt/malformed/stale/clock-skew —
    is already collapsed to None inside `read()`). A None reading must produce
    neither a SOFT question nor a HARD refusal."""
    if _gauge_reader is None:
        return None
    path = _gauge_path(base_dir)
    if path is None:
        return None
    return _gauge_reader.read(path)


def _refresh_attach_hint(gate: str) -> str:
    """The exact `attach` command that raises a refresh-request for `gate` — the
    remedy both bands point the agent at (payload is pointers only: seam + why_ref,
    per #179). `<why-id>` is a placeholder the agent fills from the live DIGEST."""
    return (f"attach {gate} --type refresh-request "
            f"--field seam={gate} --field why_ref=<why-id>")


def _trip_advisory(cl: dict, base_dir: Path | None) -> str:
    """The Trip advisory suffix for the read-only `current` at a gate boundary
    (gated checklists only). Empty for surveys, a missing/stale reading, or when
    below `soft`. SOFT band: a stop-by-default question (advisory — never forces).
    HARD band: the same escalated to the exact remedy; the refusal itself is
    enforced on `advance` by `_trip_hard_gate`."""
    if cl.get("type") != GATED:
        return ""
    gate = active_id(cl)
    if gate is None:
        return ""
    reading = _read_gauge(base_dir)
    if reading is None:
        return ""
    soft, hard = _gauge_reader.thresholds_for(reading.model)
    fill = reading.fill_fraction
    if fill >= hard:
        if has_pending_refresh_request(cl, gate):
            return (f"\nCONTEXT {fill:.0%} (>= hard): refresh already requested for "
                    f"{gate} — hand off now; do not keep working.")
        return (f"\nCONTEXT {fill:.0%} (>= hard): `advance` is BLOCKED until you "
                f"request a refresh. Run: {_refresh_attach_hint(gate)}  — then hand off.")
    if fill >= soft:
        return (f"\nCONTEXT {fill:.0%} (>= soft): you've used most of your context. "
                f"Unless you're basically done, hand off here at {gate} rather than "
                f"pushing through (advisory — decline with a reason if you're nearly done).")
    return ""


def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None) -> None:
    """Trip HARD backstop at the `advance` gate boundary: REFUSE to advance when
    the gauge reads `fill >= hard` and no `refresh-request` is pending for the
    gate. No-op for surveys, a missing/stale reading (None), or below `hard` — HARD
    never forces on an absent reading. Called BEFORE `advance` mutates state, so a
    refusal leaves the gate exactly `in-progress`."""
    if cl.get("type") != GATED or not iid:
        return
    reading = _read_gauge(base_dir)
    if reading is None:
        return
    _, hard = _gauge_reader.thresholds_for(reading.model)
    if reading.fill_fraction < hard:
        return
    if has_pending_refresh_request(cl, iid):
        return  # the agent already requested a refresh; the backstop is satisfied
    raise EngineError(
        f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit — "
        f"advancing is blocked until you request a refresh, so work is handed off at "
        f"a seam rather than lost to a runaway. Run: {_refresh_attach_hint(iid)}"
    )


# --------------------------------------------------------------------------- #
# verbs (each returns a human/agent-readable message; refusals raise)
# --------------------------------------------------------------------------- #
def current(cl: dict) -> str:
    lease = _lease_line(cl)
    prefix = f"{lease}\n" if lease else ""
    aid = active_id(cl)
    if aid is None:
        if cl["type"] == SURVEY and cl.get("consolidation") is None:
            body = "ALL ITEMS VISITED. Next: consolidate"
        else:
            waived = []
            for iid in cl.get("items", []):
                t = cl["tasks"][iid]
                for c in t.get("postconditions", []):
                    if c.get("waived"):
                        waived.append(f"{iid}.{c['id']}")
            body = (f"DONE: no open items. WAIVED: {waived}" if waived
                    else "DONE: no open items.")
    else:
        t = task(cl, aid)
        body = f"ACTIVE {aid} [{t['status']}] — {t['imperative']}"
    return prefix + body + _why_suffix(cl, aid)


def start(cl: dict, iid: str, base_dir: Path | None = None) -> str:
    t = task(cl, iid)
    if t["status"] != "pending":
        raise EngineError(f"{iid} is {t['status']!r}, cannot start")
    if cl["type"] == GATED and active_id(cl) != iid:
        raise EngineError(f"{iid} is not the active gate; start {active_id(cl)!r} first")
    unmet = [c["id"] for c in t.get("preconditions", []) if not _check_condition(c, t, base_dir)]
    if unmet:
        raise EngineError(f"{iid}: preconditions unmet {unmet} (verify upstream work, then attest)")
    t["status"] = "in-progress"
    return f"{iid} -> in-progress"


def advance(cl: dict, iid: str, from_child: str | None = None, base_dir: Path | None = None,
            why: str | None = None, mechanical: bool = False) -> str:
    if cl["type"] != GATED:
        raise EngineError("advance is for gated checklists; use record")
    t = task(cl, iid)
    if t["status"] != "in-progress":
        raise EngineError(f"{iid} is {t['status']!r}, must be in-progress to advance")
    if from_child:
        child_path = Path(from_child)
        if not child_path.is_absolute() and base_dir is not None:
            child_path = base_dir / from_child
        if not child_path.exists():
            raise EngineError(f"child checklist {from_child} not found")
        cons = json.loads(child_path.read_text(encoding="utf-8")).get("consolidation")
        if not cons:
            raise EngineError(f"child {from_child} has no consolidation yet")
        attach(cl, iid, "review-result", cons)
    posts = t.get("postconditions", [])
    if not posts:
        raise EngineError(f"{iid}: a gated gate needs >=1 postcondition")
    unmet = [c["id"] for c in posts if not _check_condition(c, t, base_dir)]
    if unmet:
        raise EngineError(f"{iid}: postconditions unmet {unmet}")
    # Why-capture (#179): postconditions are proven ABOVE, before we ever solicit
    # the why (no buying past unfinished work — a failed postcondition yields the
    # postcondition refusal, not the why prompt). A non-exempt gate must then carry
    # either a running --why or an explicit --mechanical marker; SILENCE FAILS CLOSED.
    # A missing `why_exempt` is treated as NOT exempt (opt-out default). The record
    # lands on the append-only why_trail; a mechanical marker never becomes the digest.
    if not bool(t.get("why_exempt")):
        if mechanical:
            _append_why(cl, iid, why=None, mechanical=True)
        elif (why or "").strip():
            _append_why(cl, iid, why=why.strip(), mechanical=False)
        else:
            raise EngineError(
                f"{iid}: advancing a non-exempt gate requires a running understanding — "
                f"pass --why \"<understanding>\" (reference the task state, don't duplicate "
                f"it) or --mechanical for a step that carries no new understanding"
            )
    t["status"] = "complete"
    waived = [c["id"] for c in posts if c.get("waived")]
    if waived:
        return f"{iid} -> complete (WAIVED postconditions {waived})"
    return f"{iid} -> complete"


def record(cl: dict, iid: str, result: str, finding: str | None) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("record is for survey checklists; use advance")
    if result not in ("pass", "fail"):
        raise EngineError("result must be pass or fail")
    t = task(cl, iid)
    t["result"] = result
    t["finding"] = finding
    t["status"] = "complete"
    return f"{iid} recorded {result}" + (f": {finding}" if finding else "")


def consolidate(cl: dict, verdict: str | None, summary: str | None, override_reason: str | None) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("consolidate is for survey checklists")
    open_items = [i for i in cl["items"] if cl["tasks"][i]["status"] not in TERMINAL]
    if open_items:
        raise EngineError(f"cannot consolidate; unvisited items {open_items}")
    fails = [i for i in cl["items"] if cl["tasks"][i].get("result") == "fail"]
    if verdict == "APPROVE" and fails and not override_reason:
        raise EngineError(f"cannot APPROVE with failing items {fails}; supply --override-reason")
    cons: dict = {
        "verdict": verdict,
        "findings": [
            f"{i}: {cl['tasks'][i].get('finding')}" for i in fails if cl["tasks"][i].get("finding")
        ],
    }
    if summary:
        cons["summary"] = summary
    if override_reason:
        cons["override_reason"] = override_reason
    cl["consolidation"] = cons
    return f"consolidated: verdict={verdict} findings={len(cons['findings'])}"


def skip(cl: dict, iid: str, reason: str) -> str:
    t = task(cl, iid)
    t["status"] = "skipped"
    t.setdefault("status_detail", {})["reason"] = reason
    return f"{iid} -> skipped because {reason}"


def block(cl: dict, iid: str, blocker: str, authority: str, next_action: str) -> str:
    t = task(cl, iid)
    detail = {"blocker": blocker, "authority_needed": authority, "next_action": next_action}
    t["status"] = "blocked"
    t["status_detail"] = detail
    cl.setdefault("blockers", []).append({"item": iid, **detail})
    return f"{iid} -> blocked (bubbled to parent)"


def _reset_conditions(conds: list[dict]) -> None:
    """Reset each condition to unsatisfied and drop the markers that would let a
    stale approval carry across a rework: `satisfied_by`, `waived` (a prior human
    waiver does not survive rework) and `attested` (nor an artifact-by-reference
    attestation). Shared by the target-gate reset and the downstream cascade."""
    for c in conds:
        c["satisfied"] = False
        c.pop("satisfied_by", None)
        c.pop("waived", None)
        c.pop("attested", None)


def _supersede_evidence(t: dict, iid: str, reason: str) -> None:
    """Mark every evidence item on task `t` superseded by a reopen of `iid`.
    Evidence is RETAINED (audit trail preserved) but rendered inert for
    satisfaction (see `_check_condition` artifact branch and `attest --evidence`):
    a reopened gate must not re-pass from the stale approval it just invalidated."""
    for ev in t.get("evidence", []):
        ev["superseded"] = {"by": f"reopen:{iid}", "reason": reason, "ts": _now()}


def reopen(cl: dict, iid: str, reason: str, cap: int | None = None) -> str:
    """Reopen a complete gate for rework. Increments `rework_count`, escalates
    (blocks + bubbles, no reopen) when the cap is exceeded, and on the success
    path resets the gate's postconditions and CASCADES downstream: every later
    gate that is `complete`/`in-progress` is reset to `pending` (both pre- and
    postconditions cleared, evidence superseded, `status_detail.superseded_by_reopen`
    stamped). `skipped`/`blocked` downstream gates are deliberate OBE/bubble states
    and are left untouched. Evidence on the target and each cascaded gate is
    superseded (retained, not deleted) so a reopened gate cannot re-pass from a
    stale approval — the bug this cascade fixes."""
    t = task(cl, iid)
    if cl["type"] != GATED:
        raise EngineError("reopen applies to gated checklists")
    if t["status"] != "complete":
        raise EngineError(f"can only reopen a complete gate; {iid} is {t['status']!r}")
    if cap is None:
        cap = rework_cap(cl.get("config", {}))
    if t.get("rework_count", 0) + 1 > cap:
        detail = {
            "blocker": f"rework cap {cap} exceeded: {reason}",
            "authority_needed": "parent agent / human",
            "next_action": "escalate; do not re-dispatch",
        }
        t["status"] = "blocked"
        t["status_detail"] = detail
        cl.setdefault("blockers", []).append({"item": iid, **detail})
        return f"ESCALATED {iid}: rework cap {cap} reached; blocked and bubbled to parent (not reopened)"
    t["rework_count"] = t.get("rework_count", 0) + 1
    t["status"] = "in-progress"
    t.setdefault("status_detail", {})["reopen_reason"] = reason
    _reset_conditions(t.get("postconditions", []))
    _supersede_evidence(t, iid, reason)
    # Cascade to downstream gates: reopening an upstream gate invalidates the work
    # that depended on it. Only complete/in-progress gates are reset; skipped and
    # blocked gates are deliberate states we do not churn.
    items = cl.get("items", [])
    cascaded: list[str] = []
    if iid in items:
        for did in items[items.index(iid) + 1:]:
            dt = cl["tasks"][did]
            if dt["status"] not in ("complete", "in-progress"):
                continue
            dt["status"] = "pending"
            _reset_conditions(dt.get("preconditions", []))
            _reset_conditions(dt.get("postconditions", []))
            _supersede_evidence(dt, iid, reason)
            dt.setdefault("status_detail", {})["superseded_by_reopen"] = iid
            cascaded.append(did)
    # Freshen the digest (#179): append a reopen-marker for the target and every
    # cascaded gate, so their now-stale understanding stops being the latest `why`
    # (append-only — prior why-records are never mutated). See `_latest_why_record`.
    _append_reopen_marker(cl, iid, reason)
    for did in cascaded:
        _append_reopen_marker(cl, did, reason)
    msg = f"{iid} reopened (rework {t['rework_count']}/{cap})"
    if cascaded:
        msg += f"; cascade-reset downstream {cascaded} (evidence superseded, retained)"
    return msg


_AMEND_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _build_amend_task(op: dict) -> dict:
    """Build a full pending task from an `add` op, mirroring `append()`'s shape.
    `preconditions`/`constraints` default to empty; `directives`/`child_checklist`
    default to None. Deep-copied so the caller's op dict is never aliased into
    canonical state."""
    return {
        "id": op["id"],
        "title": op["title"],
        "imperative": op["imperative"],
        "preconditions": copy.deepcopy(op.get("preconditions") or []),
        "postconditions": copy.deepcopy(op["postconditions"]),
        "constraints": copy.deepcopy(op.get("constraints") or []),
        "directives": copy.deepcopy(op.get("directives")),
        "child_checklist": op.get("child_checklist"),
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }


def amend(cl: dict, delta: dict, reason: str, authority: str, base_dir: Path | None = None) -> str:
    """Intentional mid-stream re-planning of a GATED checklist. Apply a delta of
    `add`/`drop`/`rescope` ops that touch PENDING gates only — completed and
    in-progress gates are never edited. The whole delta is ALL-OR-NOTHING: it is
    validated and built on COPIES, and only committed to `cl` once every op passes,
    so a refusal leaves `cl` unmutated (important: `main()` persists `cl` even on
    the error path). Records an audit entry to `cl["amendments"]`.

    - `add`: insert a new pending gate (`id` kebab-ish and unique; non-empty
      `title`/`imperative`; >=1 postcondition). `after` names an existing gate to
      insert behind (omit to append). The insert may not land before a frozen
      (non-pending) gate.
    - `drop`: remove a pending gate.
    - `rescope`: overwrite provided fields (title/imperative/pre/postconditions/
      constraints/directives) on a pending gate; postconditions if given stay >=1.
    Requires non-empty `--reason` and `--authority` (human ratification), same as
    `waive`."""
    if cl.get("type") != GATED:
        raise EngineError("amend applies to gated checklists")
    if not (authority or "").strip():
        raise EngineError("amend requires a non-empty --authority")
    if not (reason or "").strip():
        raise EngineError("amend requires a non-empty --reason")
    ops = (delta or {}).get("ops")
    if not isinstance(ops, list) or not ops:
        raise EngineError("amend delta needs a non-empty 'ops' list")

    # Build the new state on copies; commit to cl only after every op validates.
    new_items = list(cl["items"])
    new_tasks = dict(cl["tasks"])
    summaries: list[str] = []

    def _floor() -> int:
        """1 + index of the last non-pending (frozen) gate; 0 if none. A new gate
        may not be inserted at an index below this."""
        floor = 0
        for idx, tid in enumerate(new_items):
            if new_tasks[tid]["status"] != "pending":
                floor = idx + 1
        return floor

    for op in ops:
        kind = op.get("op")
        if kind == "add":
            nid = op.get("id")
            if not isinstance(nid, str) or not _AMEND_ID_RE.match(nid):
                raise EngineError(f"add: id {nid!r} must match ^[a-z0-9][a-z0-9-]*$")
            if nid in new_tasks:
                raise EngineError(f"add {nid}: id already exists")
            if not (op.get("title") or "").strip():
                raise EngineError(f"add {nid}: a non-empty title is required")
            if not (op.get("imperative") or "").strip():
                raise EngineError(f"add {nid}: a non-empty imperative is required")
            posts = op.get("postconditions")
            if not isinstance(posts, list) or len(posts) < 1:
                raise EngineError(f"add {nid}: a gated gate needs >=1 postcondition")
            after = op.get("after")
            if after is not None:
                if after not in new_tasks:
                    raise EngineError(f"add {nid}: after {after!r} does not exist")
                insert_at = new_items.index(after) + 1
            else:
                insert_at = len(new_items)
            floor = _floor()
            if insert_at < floor:
                frozen = new_items[floor - 1]
                raise EngineError(
                    f"add {nid}: cannot insert before frozen (non-pending) gate {frozen}"
                )
            new_tasks[nid] = _build_amend_task(op)
            new_items.insert(insert_at, nid)
            summaries.append(f"added {nid}")
        elif kind == "drop":
            tid = op.get("id")
            if tid not in new_tasks:
                raise EngineError(f"drop {tid}: no such gate")
            status = new_tasks[tid]["status"]
            if status != "pending":
                raise EngineError(f"drop {tid}: only a pending gate can be dropped (is {status!r})")
            new_items.remove(tid)
            del new_tasks[tid]
            summaries.append(f"dropped {tid}")
        elif kind == "rescope":
            tid = op.get("id")
            if tid not in new_tasks:
                raise EngineError(f"rescope {tid}: no such gate")
            status = new_tasks[tid]["status"]
            if status != "pending":
                raise EngineError(f"rescope {tid}: only a pending gate can be rescoped (is {status!r})")
            overwritable = ("title", "imperative", "postconditions",
                            "preconditions", "constraints", "directives")
            fields = {k: op[k] for k in overwritable if k in op}
            if not fields:
                raise EngineError(f"rescope {tid}: at least one overwritable field is required")
            if "postconditions" in fields:
                posts = fields["postconditions"]
                if not isinstance(posts, list) or len(posts) < 1:
                    raise EngineError(f"rescope {tid}: postconditions must be a non-empty list")
            # Deep-copy the task before overwriting so the original object in
            # cl["tasks"] stays untouched until the final commit (all-or-nothing).
            updated = copy.deepcopy(new_tasks[tid])
            for key, value in fields.items():
                updated[key] = copy.deepcopy(value)
            new_tasks[tid] = updated
            summaries.append(f"rescoped {tid}")
        else:
            raise EngineError(f"amend: unknown op kind {kind!r}")

    # Commit: every op validated. Only now do we touch canonical state.
    cl["items"] = new_items
    cl["tasks"] = new_tasks
    cl.setdefault("amendments", []).append(
        {"ts": _now(), "reason": reason, "authority": authority, "ops": summaries}
    )
    return f"amended: {', '.join(summaries)} (authority {authority})"


def append(cl: dict, iid: str, title: str, imperative: str) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("append only on survey checklists")
    if iid in cl.get("tasks", {}):
        raise EngineError(f"item {iid!r} already exists")
    cl["tasks"][iid] = {
        "id": iid,
        "title": title,
        "imperative": imperative,
        "preconditions": [],
        "postconditions": [],
        "constraints": [],
        "directives": None,
        "child_checklist": None,
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }
    cl["items"].append(iid)
    return f"appended {iid}"


def attest(cl: dict, iid: str, cond_id: str, which: str, note: str | None, evidence_id: str | None = None) -> str:
    """Satisfy a condition by attestation.

    Two paths:
    - `check: null` (qualitative): the agent's manual verification stands in for a
      mechanical check — set `satisfied` from the note. Unchanged legacy behavior.
    - `check.kind == "artifact"`: satisfy the postcondition **by reference** to an
      already-attached artifact (`--evidence <id>`), instead of re-attaching the
      same artifact to a sibling task. The engine still enforces mechanism: the
      referenced evidence must EXIST, be of the required `evidence_type`, and match
      the required `match` fields. It never lets an agent assert an artifact out of
      thin air (that is what a `check: null` attest does, not this).

    `command` / `git-change-policy` checks stay engine-checked and refuse attest.

    The requested `which` list is searched FIRST (an explicit `--which` still wins),
    then the OTHER condition list as a fallback — precondition ids (`p*`) and
    postcondition ids (`c*`) are disjoint, so a bare `attest <id> --cond c1` (default
    `--which preconditions`) still resolves a postcondition without forcing the caller
    to pass `--which postconditions`. If the cond is in neither list, the error names
    both."""
    t = task(cl, iid)
    other = "postconditions" if which == "preconditions" else "preconditions"
    for list_name in (which, other):
        for c in t.get(list_name, []):
            if c["id"] != cond_id:
                continue
            chk = c.get("check")
            if chk is None:
                c["satisfied"] = True
                c["satisfied_by"] = note or "attested"
                return f"attested {iid}.{cond_id}"
            if chk.get("kind") == "artifact":
                if not evidence_id:
                    raise EngineError(
                        f"{cond_id} is an artifact check; attest it by referencing an "
                        f"already-attached artifact via --evidence <id>"
                    )
                ev = _find_evidence(cl, evidence_id)
                if ev is None:
                    raise EngineError(f"evidence {evidence_id!r} not found in this checklist")
                if ev.get("superseded"):
                    raise EngineError(
                        f"evidence {evidence_id!r} is superseded and cannot satisfy a condition"
                    )
                want_type = chk.get("evidence_type")
                if ev.get("type") != want_type:
                    raise EngineError(
                        f"evidence {evidence_id!r} is type {ev.get('type')!r}, "
                        f"not the required {want_type!r}"
                    )
                want_match = chk.get("match", {})
                if not all(ev.get("payload", {}).get(k) == v for k, v in want_match.items()):
                    raise EngineError(f"evidence {evidence_id!r} does not match required {want_match}")
                c["satisfied"] = True
                c["satisfied_by"] = evidence_id
                c["attested"] = {"evidence": evidence_id, "note": note}
                return f"attested {iid}.{cond_id} via {evidence_id}"
            raise EngineError(f"{cond_id} is engine-checked; cannot attest")
    raise EngineError(f"condition {cond_id!r} not found in preconditions or postconditions on {iid}")


def waive(
    cl: dict,
    iid: str,
    cond_id: str,
    which: str,
    authority: str,
    reason: str | None,
    forced: bool = False,
) -> str:
    """Human override: explicitly satisfy a condition by waiver, auditable.

    Refused unless the condition's `override_policy.allowed` is true — unless an
    explicit high-friction `--force` is given (force still demands authority +
    reason and is recorded as a forced override). The engine does not judge
    whether a waiver is wise; it records authority and refuses accidental use."""
    t = task(cl, iid)
    for c in t.get(which, []):
        if c["id"] != cond_id:
            continue
        policy = c.get("override_policy") or {}
        allowed = bool(policy.get("allowed"))
        if not allowed and not forced:
            raise EngineError(
                f"{iid}.{cond_id} is not waivable (no override policy); pass --force to override deliberately"
            )
        if not (authority or "").strip():
            raise EngineError("waive requires a non-empty --authority")
        reason = (reason or "").strip() or None
        if (policy.get("reason_required") or forced) and not reason:
            raise EngineError("waive requires a non-empty --reason")
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "waiver",
                "payload": {"cond": cond_id, "authority": authority, "reason": reason, "forced": forced},
                "produced_by": "human",
                "ts": "",
            }
        )
        c["satisfied"] = True
        c["satisfied_by"] = eid
        c["waived"] = {"authority": authority, "reason": reason, "evidence": eid, "forced": forced}
        tag = " (FORCED)" if forced else ""
        return f"waived {iid}.{cond_id}{tag} by {authority} -> {eid}"
    raise EngineError(f"{which} {cond_id!r} not found on {iid}")


def attach(cl: dict, iid: str, etype: str, payload: dict) -> str:
    t = task(cl, iid)
    eid = _new_evidence_id(t)
    t.setdefault("evidence", []).append(
        {"id": eid, "type": etype, "payload": payload, "produced_by": "engine", "ts": ""}
    )
    return f"attached {eid} ({etype}) to {iid}"


def flag_candidate(cl: dict, frm: str, statement: str) -> str:
    cands = cl.setdefault("triage_candidates", [])
    cid = f"tc{len(cands) + 1}"
    cands.append({"id": cid, "from": frm, "statement": statement})
    return f"flagged {cid}"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, help="checklist JSON file")
    p.add_argument("--dry-run", action="store_true", help="do not write changes back")
    sub = p.add_subparsers(dest="verb", required=True)

    def add_session(parser: argparse.ArgumentParser) -> None:
        # optional on every mutating verb; only enforced once a lease exists
        parser.add_argument("--session-id", dest="session_id", default=None,
                            help="owning engine session (required only once a lease has been claimed)")

    sub.add_parser("current")

    s = sub.add_parser("claim")
    s.add_argument("--session-id", dest="session_id", required=True)
    s.add_argument("--claimed-by", dest="claimed_by", default="agent", help="role claiming the lease")
    s.add_argument("--worktree", default=".")
    s.add_argument("--force", action="store_true", help="take over an active/ambiguous lease (records prior session)")
    s.add_argument("--reason", help="required with --force: why the takeover is justified")
    s = sub.add_parser("heartbeat")
    s.add_argument("--session-id", dest="session_id", required=True)
    s = sub.add_parser("release")
    s.add_argument("--session-id", dest="session_id", required=True)
    s.add_argument("--force", action="store_true", help="release a lease you do not own (requires --reason)")
    s.add_argument("--reason", help="required when force-releasing a lease you do not own")

    s = sub.add_parser("start")
    s.add_argument("id")
    add_session(s)
    s = sub.add_parser("advance")
    s.add_argument("id")
    s.add_argument("--from-child", dest="from_child", help="child checklist file; attach its consolidation as review-result first")
    s.add_argument("--why", help="the running understanding justifying this advance; required on a non-exempt gate unless --mechanical (reference the task state, do not duplicate it)")
    s.add_argument("--mechanical", action="store_true", help="discharge the why prompt: this advance carries no new understanding (a distinct flag, not a magic string)")
    add_session(s)
    s = sub.add_parser("record")
    s.add_argument("id")
    s.add_argument("--result", required=True, choices=["pass", "fail"])
    s.add_argument("--finding")
    add_session(s)
    s = sub.add_parser("consolidate")
    s.add_argument("--verdict")
    s.add_argument("--summary")
    s.add_argument("--override-reason")
    add_session(s)
    s = sub.add_parser("skip")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    add_session(s)
    s = sub.add_parser("block")
    s.add_argument("id")
    s.add_argument("--blocker", required=True)
    s.add_argument("--authority", default="parent agent")
    s.add_argument("--next", dest="next_action", default="")
    add_session(s)
    s = sub.add_parser("reopen")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    add_session(s)
    s = sub.add_parser("append")
    s.add_argument("id")
    s.add_argument("--title", required=True)
    s.add_argument("--imperative", required=True)
    add_session(s)
    s = sub.add_parser("amend")
    s.add_argument("--delta", required=True, help="path to a JSON delta file: {\"ops\": [...]}")
    s.add_argument("--reason", required=True, help="why this re-planning is justified")
    s.add_argument("--authority", required=True, help="who ratified the amendment (e.g. human)")
    add_session(s)
    s = sub.add_parser("attest")
    s.add_argument("id")
    s.add_argument("--cond", required=True)
    s.add_argument("--which", choices=["preconditions", "postconditions"], default="preconditions")
    s.add_argument("--note")
    s.add_argument("--evidence", help="evidence id that satisfies an artifact postcondition by reference (avoids re-attaching the same artifact to a sibling task)")
    add_session(s)
    s = sub.add_parser("waive")
    s.add_argument("id")
    s.add_argument("--cond", required=True)
    s.add_argument("--which", choices=["preconditions", "postconditions"], default="postconditions")
    s.add_argument("--authority", required=True, help="who is accepting the risk (e.g. human)")
    s.add_argument("--reason", help="why the check is being waived")
    s.add_argument("--force", action="store_true", help="waive even without an override policy (high-friction; recorded as forced)")
    add_session(s)
    s = sub.add_parser("attach")
    s.add_argument("id")
    s.add_argument("--type", required=True)
    s.add_argument("--payload", help="JSON object (or use the quote-safe --field / --payload-file)")
    s.add_argument("--payload-file", dest="payload_file", help="path to a JSON file holding the payload")
    s.add_argument("--field", action="append", default=[], metavar="K=V", help="repeatable key=value; avoids passing JSON through the shell")
    add_session(s)
    s = sub.add_parser("flag-candidate")
    s.add_argument("--from", dest="frm", required=True)
    s.add_argument("--statement", required=True)
    add_session(s)
    return p.parse_args(argv)


def build_payload(args: argparse.Namespace) -> dict:
    """Assemble an attach payload without forcing JSON through the shell.
    Priority: --payload-file, then --payload (JSON), then --field K=V pairs."""
    if getattr(args, "payload_file", None):
        return json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    payload = json.loads(args.payload) if getattr(args, "payload", None) else {}
    for pair in getattr(args, "field", None) or []:
        key, _, value = pair.partition("=")
        payload[key] = value
    if not payload:
        raise EngineError("attach needs one of --payload-file, --payload, or --field K=V")
    return payload


def dispatch(cl: dict, args: argparse.Namespace, base_dir: Path | None = None) -> str:
    v = args.verb
    config = load_config(cl, base_dir)
    # heartbeat/release manage the lease only and are NOT railed — keep their pure
    # early returns. current/claim ARE railed, so they fall through to the append.
    if v == "heartbeat":
        return heartbeat(cl, args.session_id)
    if v == "release":
        return release(
            cl, args.session_id,
            force=getattr(args, "force", False), reason=getattr(args, "reason", None),
        )
    if v == "current":
        # Trip SOFT/HARD advisory (#182) rides the read-only `current` at the gate
        # boundary — like the doctrine rail, it hangs off this CLI chokepoint so
        # `current` itself stays pure. Empty for surveys / missing reading / below soft.
        message = current(cl) + _trip_advisory(cl, base_dir)
    elif v == "claim":
        message = claim(
            cl, args.session_id, args.claimed_by, args.worktree, config,
            force=getattr(args, "force", False), reason=getattr(args, "reason", None),
        )
    else:
        # Actor-authority gate: once an active lease exists, a mutating verb must
        # carry the owning --session-id. No lease -> legacy behavior (no session).
        session_id = getattr(args, "session_id", None)
        require_session(cl, v, session_id, config)
        # Trip HARD backstop (#182): at the `advance` gate boundary, refuse when the
        # gauge reads >= hard and no refresh-request exists yet. Checked BEFORE the
        # verb runs so a refusal never mutates state. No-op on a missing reading.
        if v == "advance":
            _trip_hard_gate(cl, getattr(args, "id", None), base_dir)
        # Run the verb FIRST: a refused verb raises here (before the liveness stamp),
        # so it never refreshes the lease even though main() persists on the error
        # path. Only a verb that returns successfully reaches the stamp below.
        message = _run_verb(cl, args, base_dir)
        # Owner activity = liveness: a SUCCESSFUL mutating verb by the owner refreshes
        # the lease, so an actively-working session never goes stale and an idle gap
        # self-heals. A refused verb never gets here.
        if v in MUTATING_VERBS:
            _refresh_owner_heartbeat(cl, session_id)
    # Doctrine rail (#138 channel A): append the position-derived doctrine block to
    # the railed verbs' success output. The verb functions above stay pure; the rail
    # rides only this CLI-boundary chokepoint. `_rail` returns "" for non-gated cls.
    if v in RAIL_VERBS:
        message += _rail(v, cl)
    return message


def _run_verb(cl: dict, args: argparse.Namespace, base_dir: Path | None) -> str:
    """Execute a mutating verb and return its message, or raise EngineError if the
    verb refuses. Read-only/lease verbs are handled by `dispatch` before this."""
    v = args.verb
    if v == "start":
        return start(cl, args.id, base_dir=base_dir)
    if v == "advance":
        return advance(cl, args.id, from_child=getattr(args, "from_child", None),
                       base_dir=base_dir, why=getattr(args, "why", None),
                       mechanical=getattr(args, "mechanical", False))
    if v == "record":
        return record(cl, args.id, args.result, args.finding)
    if v == "consolidate":
        return consolidate(cl, args.verdict, args.summary, args.override_reason)
    if v == "skip":
        return skip(cl, args.id, args.reason)
    if v == "block":
        return block(cl, args.id, args.blocker, args.authority, args.next_action)
    if v == "reopen":
        return reopen(cl, args.id, args.reason, cap=rework_cap(load_config(cl, base_dir)))
    if v == "append":
        return append(cl, args.id, args.title, args.imperative)
    if v == "amend":
        try:
            delta = json.loads(Path(args.delta).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise EngineError(f"amend: cannot read delta {args.delta!r}: {exc}")
        return amend(cl, delta, args.reason, args.authority, base_dir=base_dir)
    if v == "attest":
        return attest(cl, args.id, args.cond, args.which, args.note, evidence_id=getattr(args, "evidence", None))
    if v == "waive":
        return waive(cl, args.id, args.cond, args.which, args.authority, args.reason, forced=args.force)
    if v == "attach":
        return attach(cl, args.id, args.type, build_payload(args))
    if v == "flag-candidate":
        return flag_candidate(cl, args.frm, args.statement)
    raise EngineError(f"unknown verb {v!r}")


# --------------------------------------------------------------------------- #
# append-only journal sidecar (#131) — one line per SUCCESSFUL mutating verb
#
# The spine is a single mutable JSON file: a careful agent could study genuine
# engine output and forge the whole terminal shape. The journal raises that cost.
# It is written ONLY by main() (the CLI boundary), append-only, one JSON line per
# successful mutating verb, each line hash-chained to the previous. The engine
# NEVER reads it back for its own operation, so it is fully backward compatible:
# a journal-absent spine keeps working everywhere. Only the eval provenance check
# cross-verifies it (journal-absent spines are grandfathered there).
# --------------------------------------------------------------------------- #
def journal_path(spine_path: Path) -> Path:
    """The journal sidecar for a spine file: ``<spine>.journal`` (so
    ``spine.json`` -> ``spine.json.journal``, and a child ``review.json`` gets its
    own ``review.json.journal``)."""
    return Path(str(spine_path) + ".journal")


def _all_evidence_ids(cl: dict) -> set[str]:
    ids: set[str] = set()
    for t in cl.get("tasks", {}).values():
        if isinstance(t, dict):
            for ev in t.get("evidence", []) or []:
                if isinstance(ev, dict) and ev.get("id"):
                    ids.add(ev["id"])
    return ids


def _journal_hash(entry: dict) -> str:
    """SHA-256 over the entry's canonical (sorted, hash-excluded) JSON. The
    ``prev_hash`` field is part of that payload, so each line commits to the whole
    chain before it — tampering with any earlier line invalidates every hash after."""
    payload = {k: entry[k] for k in
               ("seq", "ts", "session_id", "verb", "task", "evidence_ids", "prev_hash")}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _read_journal_tail(jp: Path) -> tuple[int, str]:
    """(next seq, last hash) for an existing journal, or (1, "") when absent/empty.
    Never raises — a corrupt/unreadable journal degrades to a fresh chain rather
    than blocking the engine (the sidecar must never break a mutation)."""
    try:
        lines = [ln for ln in jp.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return 1, ""
    if not lines:
        return 1, ""
    try:
        last = json.loads(lines[-1])
        return len(lines) + 1, last.get("hash", "")
    except ValueError:
        return len(lines) + 1, ""


def append_journal_entry(spine_path: Path, verb: str, task_id: str | None,
                         session_id: str | None, evidence_ids: list[str]) -> None:
    """Append one hash-chained line to the spine's journal for a successful
    mutating verb. Best-effort and non-fatal: a journal write failure must never
    fail the mutation it records (the spine is already the source of truth), so any
    OSError is swallowed."""
    jp = journal_path(spine_path)
    seq, prev = _read_journal_tail(jp)
    entry = {
        "seq": seq,
        "ts": _now(),
        "session_id": session_id,
        "verb": verb,
        "task": task_id,
        "evidence_ids": sorted(evidence_ids),
        "prev_hash": prev,
    }
    entry["hash"] = _journal_hash(entry)
    try:
        with jp.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.file)
    cl = load(path)
    ev_before = _all_evidence_ids(cl)
    try:
        message = dispatch(cl, args, base_dir=path.parent)
    except EngineError as exc:
        # state may carry legitimate mutations (command results, escalation); persist unless read-only/dry-run
        if not args.dry_run and args.verb != "current":
            save(path, cl)
        # Doctrine rail (#138 channel A): a refusal is a check-failure decision point.
        # Append the check-failure rail (gated checklists only; "" for surveys).
        print(f"REFUSED: {exc}{_rail('check-failure', cl)}", file=sys.stderr)
        return 1
    if not args.dry_run and args.verb != "current":
        save(path, cl)
        # Journal AFTER the spine is persisted, only on the SUCCESS path, only for
        # verbs that actually mutate canonical state. New evidence produced by this
        # verb is captured by diffing the evidence-id set across the dispatch.
        if args.verb in MUTATING_VERBS:
            new_ev = sorted(_all_evidence_ids(cl) - ev_before)
            append_journal_entry(
                path, args.verb, getattr(args, "id", None),
                getattr(args, "session_id", None), new_ev,
            )
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
