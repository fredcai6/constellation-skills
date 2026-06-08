#!/usr/bin/env python
"""Workbench checklist engine: work one gated/survey plan through its gates.

The engine holds the canonical state; an agent transacts with it one step at a
time. It enforces *mechanism* (ordering, evidence shape, the rework cap, the
consolidation consistency guard) and never judges quality. See
docs/CHECKLIST_SCHEMA.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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
}


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


def _new_evidence_id(t: dict) -> str:
    return f"e-{t['id']}-{len(t.get('evidence', [])) + 1}"


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


def _check_condition(cond: dict, t: dict, base_dir: Path | None = None) -> bool:
    """Verify one condition. command -> run it; artifact -> presence/match;
    git-change-policy -> evaluate the staged/branch diff against an artifact
    policy (#8); null -> the agent must have attested it (trust but verify).

    A WAIVED condition is honored without re-running its check: a human override
    (see `waive`) has accepted the condition, and re-running the command would
    overwrite `satisfied` and silently un-waive it at every `advance`."""
    if cond.get("waived"):
        return True
    chk = cond.get("check")
    if chk is None:
        return bool(cond.get("satisfied"))
    kind = chk.get("kind")
    if kind == "command":
        proc = subprocess.run(chk["command"], shell=True, capture_output=True, text=True)
        cond["satisfied"] = proc.returncode == 0
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "command-output",
                "payload": {"cmd": chk["command"], "exit": proc.returncode},
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


def require_session(cl: dict, verb: str, session_id: str | None, config: dict) -> None:
    """The backward-compat gate. Mutating verbs are only session-gated ONCE an
    ACTIVE lease exists. With no active lease, a missing `--session-id` is fine
    (every existing checklist/template has no `engine_session`). With an active,
    non-stale lease, the caller's `--session-id` must match its `session_id`. A
    STALE active lease does not silently block — but it must be reclaimed via
    `claim` first, so a mutating verb against a stale-only lease is refused with
    an instruction to claim."""
    if verb not in MUTATING_VERBS:
        return
    lease = _active_lease(cl)
    if lease is None:
        return  # no lease claimed: legacy behavior, no session needed
    if _is_stale(lease, config):
        raise EngineError(
            f"checklist lease {lease.get('session_id')!r} is stale; "
            f"`claim` it (same id or --force --reason) before mutating"
        )
    if session_id != lease.get("session_id"):
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
# verbs (each returns a human/agent-readable message; refusals raise)
# --------------------------------------------------------------------------- #
def current(cl: dict) -> str:
    lease = _lease_line(cl)
    prefix = f"{lease}\n" if lease else ""
    aid = active_id(cl)
    if aid is None:
        if cl["type"] == SURVEY and cl.get("consolidation") is None:
            return prefix + "ALL ITEMS VISITED. Next: consolidate"
        waived = []
        for iid in cl.get("items", []):
            t = cl["tasks"][iid]
            for c in t.get("postconditions", []):
                if c.get("waived"):
                    waived.append(f"{iid}.{c['id']}")
        if waived:
            return prefix + f"DONE: no open items. WAIVED: {waived}"
        return prefix + "DONE: no open items."
    t = task(cl, aid)
    return prefix + f"ACTIVE {aid} [{t['status']}] — {t['imperative']}"


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


def advance(cl: dict, iid: str, from_child: str | None = None, base_dir: Path | None = None) -> str:
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


def reopen(cl: dict, iid: str, reason: str, cap: int | None = None) -> str:
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
    for c in t.get("postconditions", []):
        c["satisfied"] = False
        c.pop("satisfied_by", None)
        c.pop("waived", None)  # rework re-evaluates: a prior waiver does not carry over
    return f"{iid} reopened (rework {t['rework_count']}/{cap})"


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


def attest(cl: dict, iid: str, cond_id: str, which: str, note: str | None) -> str:
    t = task(cl, iid)
    for c in t.get(which, []):
        if c["id"] == cond_id:
            if c.get("check") is not None:
                raise EngineError(f"{cond_id} is engine-checked; cannot attest")
            c["satisfied"] = True
            c["satisfied_by"] = note or "attested"
            return f"attested {iid}.{cond_id}"
    raise EngineError(f"{which} {cond_id!r} not found on {iid}")


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
    s = sub.add_parser("attest")
    s.add_argument("id")
    s.add_argument("--cond", required=True)
    s.add_argument("--which", choices=["preconditions", "postconditions"], default="preconditions")
    s.add_argument("--note")
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
    if v == "current":
        return current(cl)
    if v == "claim":
        return claim(
            cl, args.session_id, args.claimed_by, args.worktree, config,
            force=getattr(args, "force", False), reason=getattr(args, "reason", None),
        )
    if v == "heartbeat":
        return heartbeat(cl, args.session_id)
    if v == "release":
        return release(
            cl, args.session_id,
            force=getattr(args, "force", False), reason=getattr(args, "reason", None),
        )
    # Actor-authority gate: once an active lease exists, a mutating verb must
    # carry the owning --session-id. No lease -> legacy behavior (no session).
    require_session(cl, v, getattr(args, "session_id", None), config)
    if v == "start":
        return start(cl, args.id, base_dir=base_dir)
    if v == "advance":
        return advance(cl, args.id, from_child=getattr(args, "from_child", None), base_dir=base_dir)
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
    if v == "attest":
        return attest(cl, args.id, args.cond, args.which, args.note)
    if v == "waive":
        return waive(cl, args.id, args.cond, args.which, args.authority, args.reason, forced=args.force)
    if v == "attach":
        return attach(cl, args.id, args.type, build_payload(args))
    if v == "flag-candidate":
        return flag_candidate(cl, args.frm, args.statement)
    raise EngineError(f"unknown verb {v!r}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.file)
    cl = load(path)
    try:
        message = dispatch(cl, args, base_dir=path.parent)
    except EngineError as exc:
        # state may carry legitimate mutations (command results, escalation); persist unless read-only/dry-run
        if not args.dry_run and args.verb != "current":
            save(path, cl)
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    if not args.dry_run and args.verb != "current":
        save(path, cl)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
