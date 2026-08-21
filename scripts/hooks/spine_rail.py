#!/usr/bin/env python3
"""spine_rail.py -- Claude Code hook suite for the Constellation spine rail.

One script, dispatched by event name (argv[1]): Stop, SessionStart, PostToolUse.
It is a deterrent that refuses dishonest turn-ends mid-spine and re-injects
resume doctrine after compaction, judging the ENGINE'S OWN TRUTH -- the spine
state file plus its journal sidecar -- and NEVER the agent's prose.

Design contract (frozen DESIGN_SPEC #138 channel B, D3):

- Fail-open. Any error anywhere prints nothing and exits 0. A hook must never
  crash or hang a turn. Every handler is wrapped and returns {} on trouble.
- State-file facts ONLY. Decisions read the spine JSON (json.load) and count the
  journal lines. The agent's words (last_assistant_message, etc.) are never
  parsed for a decision.
- Read the spine STATE FILE directly; do NOT subprocess the engine. This is a
  deliberate, spec-accepted LOCALITY COST: this module re-encodes the engine's
  TERMINAL statuses (a second place that knows "what is terminal") in exchange
  for robustness in headless/subagent contexts and clean unit-testability.
- Discovery is the PostToolUse hook's ONLY job: it watches Bash commands for the
  engine's claim/release verbs, AND the MCP spine door's own `spine_lease`
  claim/release tool (#door-binding), and maintains a session->spine binding
  from either source. It is NOT a second source of mid-flight truth -- Stop
  always reads the spine file the binding points at.
- Three registrations only (Stop, SessionStart, PostToolUse). No PreCompact.
- 3-strike escape hatch so a genuinely stuck agent is never trapped.

Stdlib only (json, os, re, shlex, subprocess, sys, pathlib). Windows-friendly:
UTF-8 writes, native paths, no /tmp literals. The ONE subprocess is a bounded
`git worktree list` probe used to resolve a relative --file (#440); it is never
the engine (see the `git_worktree_roots` docstring).
"""

import errno
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import msvcrt as _msvcrt
except ImportError:
    _msvcrt = None

_IS_WINDOWS = os.name == "nt"

# The engine's terminal statuses, re-encoded here on purpose (see docstring).
TERMINAL = {"complete", "skipped"}

# The one MCP door tool capable of a claim/release (#door-binding). Narrow on
# purpose: this repo's .mcp.json registers exactly one MCP server, "spine" --
# widening to the whole mcp__spine__* namespace or to mcp__spine-epic__ (a
# distinct, unregistered-in-this-repo tool name) is explicitly out of scope.
DOOR_LEASE_TOOL_NAME = "mcp__spine__spine_lease"

# --- stable marker substrings (asserted by tests; hook contract) -------------

STUCK_MSG = (
    "SPINE-RAIL: released turn-end after 3 no-progress nudges. The rail is "
    "standing down for this turn so a genuinely stuck run is not trapped. If a "
    "gate is still open, block the gate through the engine so the blocker "
    "bubbles to the parent, then investigate -- do not silently abandon it."
)


# --- project dir + scratch file locations ------------------------------------

def resolve_project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def _agent_work(project_dir: Path) -> Path:
    return project_dir / ".agent-work"


def binding_path(project_dir: Path) -> Path:
    return _agent_work(project_dir) / ".spine-rail-binding.json"


def nudge_path(project_dir: Path) -> Path:
    return _agent_work(project_dir) / ".spine-rail-nudges.json"


def _load_json_map(path: Path) -> dict:
    """Load a JSON object map; return {} on absent/corrupt/non-object."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_json_map(path: Path, data: dict) -> None:
    """Atomically write a JSON object map. Never raises.

    KNOWN, NOT CHASED (#419, deliberately outside that issue's scope; filed as
    a triage candidate): the write is atomic but the surrounding
    load-modify-save is NOT, and nothing takes a lock, so two agents claiming
    at the same moment can lose one of the two claims. Per-agent keying widens
    that window rather than creating it -- a dispatched wave now writes N
    entries where it wrote one, so exposure grows with fan-out. The symptom of
    a lost write is SILENCE, indistinguishable from an idle governor, and it
    reintroduces exactly the blindness #419 removes. Raised independently by
    two reviewers and a cold critic.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass


def _is_old_shape_binding_entry(entry: dict) -> bool:
    """True if `entry` looks like the OLD flat per-session binding value
    (`{spine, engine_session, worktree}`) rather than the NEW nested
    `{abs_spine_path: {spine, engine_session, worktree, claimed_at}}` map.

    A `"spine"` key present DIRECTLY on `entry` is the old shape's signature --
    the new shape's values are themselves dicts keyed by abs_spine_path, never
    a literal `"spine"` key at this level.
    """
    return "spine" in entry


def load_binding(project_dir: Path) -> dict:
    """Load `session_id -> {abs_spine_path: {spine, engine_session, worktree,
    claimed_at}}`.

    An old-shape (flat, pre-#202) entry under a session_id is treated as
    ABSENT for that session_id -- fail-open, never a crash and never a silent
    misinterpretation as a new-shape entry (decision:binding-schema-may-change).
    No in-place migration: the file self-heals as sessions re-claim under the
    new writer.
    """
    raw = _load_json_map(binding_path(project_dir))
    try:
        return {
            sid: entry
            for sid, entry in raw.items()
            if isinstance(entry, dict) and not _is_old_shape_binding_entry(entry)
        }
    except Exception:
        return {}


def save_binding(project_dir: Path, data: dict) -> None:
    _save_json_map(binding_path(project_dir), data)


# --- the binding-store transaction (#441) -------------------------------------
#
# `_save_json_map`'s docstring above names the KNOWN, NOT CHASED defect this
# section fixes: load-modify-save is atomic on the WRITE but not across the
# whole read-modify-write interval, so concurrent writers can lose one
# another's update, or -- measured live under 16 spawned production writers,
# see tests/test_spine_rail.py::test_spawn_binding_transaction_red_green --
# tear the file into two concatenated JSON documents outright. Every binding
# WRITE now goes through `_binding_transaction`: one stable sibling advisory
# lock covers load -> safe reap -> one mutation callback -> unique-temp
# atomic replace. Readers (`load_binding`) stay outside the lock and keep
# their existing fail-open behavior -- only writers serialize.

# Named, bounded, and directly tested (#441) -- never widen these without a
# human float (best-seam-plan risk: "Lock timeout must be short enough for
# hooks yet long enough for the tested critical section").
LOCK_RETRY_ATTEMPTS = 200
LOCK_RETRY_INTERVAL_SECONDS = 0.01
LOCK_ACQUIRE_TIMEOUT_SECONDS = 2.0  # mirrors GIT_PROBE_TIMEOUT_SECONDS's bound

# A genuinely missing/unreadable claim target is retained until its recorded
# `claimed_at` is a parseable AWARE timestamp at least this old (#441 m2).
# Untrustworthy age (absent/naive/unparseable) is NEVER evidence of
# staleness -- the entry is retained, not reaped, in that case.
REAP_MISSING_TARGET_GRACE_SECONDS = 24 * 60 * 60


def _lock_path(project_dir: Path) -> Path:
    b = binding_path(project_dir)
    return b.with_name(b.name + ".lock")


def _posix_try_lock(fileobj) -> bool:
    """One nonblocking POSIX advisory-lock attempt via `fcntl.flock`. True on
    success, False on contention (the only outcome that means 'try again'),
    and any other OSError propagates -- the caller treats that as a lock-API
    failure and fails the transaction open without retrying."""
    import fcntl
    try:
        fcntl.flock(fileobj.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            return False
        raise


def _posix_unlock(fileobj) -> None:
    import fcntl
    try:
        fcntl.flock(fileobj.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass


def _windows_try_lock(fileobj, msvcrt_mod) -> bool:
    """One nonblocking Windows byte-range lock attempt: seek to the start of
    the stable lock file and lock exactly its first byte via
    `msvcrt.locking(..., LK_NBLCK, 1)`. `msvcrt_mod` is an INJECTED parameter,
    never the bare module import, so this adapter's contract is directly
    unit-testable on every platform (#441's `test_windows_lock_adapter_
    contract`), not only on a real Windows host. True on success, False on
    contention, any other OSError propagates (same contract as the POSIX
    adapter)."""
    try:
        fileobj.seek(0)
        msvcrt_mod.locking(fileobj.fileno(), msvcrt_mod.LK_NBLCK, 1)
        return True
    except OSError as exc:
        if getattr(exc, "errno", None) in (errno.EACCES, errno.EDEADLOCK):
            return False
        raise


def _windows_unlock(fileobj, msvcrt_mod) -> None:
    try:
        fileobj.seek(0)
        msvcrt_mod.locking(fileobj.fileno(), msvcrt_mod.LK_UNLCK, 1)
    except Exception:
        pass


def _try_lock(fileobj) -> bool:
    if _IS_WINDOWS and _msvcrt is not None:
        return _windows_try_lock(fileobj, _msvcrt)
    return _posix_try_lock(fileobj)


def _unlock(fileobj) -> None:
    if _IS_WINDOWS and _msvcrt is not None:
        _windows_unlock(fileobj, _msvcrt)
    else:
        _posix_unlock(fileobj)


def _open_lock_file(project_dir: Path):
    """Open (creating if absent) the stable sibling lock file -- NEVER the
    registry itself, and NEVER replaced -- initializing one byte so the
    Windows byte-range adapter always has a byte to lock. Returns None (never
    raises) on any open/mkdir failure; the caller treats that as a fail-open
    transaction abort."""
    try:
        path = _lock_path(project_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        f = open(path, "a+b")
        f.seek(0, os.SEEK_END)
        if f.tell() == 0:
            f.write(b"\0")
            f.flush()
        return f
    except Exception:
        return None


def _acquire_lock(fileobj, *, sleep=time.sleep, clock=time.monotonic) -> bool:
    """Try `_try_lock` until it succeeds, until LOCK_RETRY_ATTEMPTS is
    exhausted, or until LOCK_ACQUIRE_TIMEOUT_SECONDS has elapsed -- whichever
    comes first. Both bounds are read from the module globals on EVERY call
    (not captured as function-default values), so a test can monkeypatch
    either constant and see it take effect. Any lock-API error (not mere
    contention) is caught here too and treated as an immediate fail-open --
    it is a documented failure path, not something the transaction
    propagates. NEVER raises."""
    start = clock()
    for _ in range(LOCK_RETRY_ATTEMPTS):
        try:
            if _try_lock(fileobj):
                return True
        except Exception:
            return False
        if clock() - start >= LOCK_ACQUIRE_TIMEOUT_SECONDS:
            return False
        sleep(LOCK_RETRY_INTERVAL_SECONDS)
    return False


def _parse_aware_iso(text):
    """A timezone-AWARE datetime parsed from `text`, or None for anything
    absent, non-string, naive, or unparseable. Untrustworthy age must never
    be treated as evidence of staleness (#441 m2)."""
    try:
        if not isinstance(text, str):
            return None
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return None
        return dt
    except Exception:
        return None


def _reap_binding_entries(binding: dict, now: str) -> dict:
    """The transaction-internal safe reaper (#441 m2), called only from
    inside `_binding_transaction` under the held lock.

    Deletes:
    - a malformed outer-key value (not a dict) or a malformed per-agent
      entry (not a dict, or its `spine` field is not a string);
    - an entry whose target IS readable and whose `engine_session.status`
      is exactly `"released"`;
    - an entry whose target is missing/unreadable AND whose `claimed_at`
      parses as an aware timestamp at least REAP_MISSING_TARGET_GRACE_SECONDS
      old.

    Retains everything else, in particular: every readable target whose
    lease is NOT released (active or otherwise) regardless of age, and a
    missing/unreadable target whose age is untrustworthy (absent, naive, or
    unparseable `claimed_at`). An old-shape (pre-#202) per-key value is
    passed through UNTOUCHED -- this reaper prunes the established nested-map
    shape, it does not migrate schema (mirrors `load_binding`'s read-time
    treatment of the same old shape).

    Does not scan globally, infer liveness, consult the journal, or touch
    anything outside the one binding-store file. NEVER raises -- returns the
    input unchanged on any unexpected error so a defect here fails toward
    keeping data, not discarding it."""
    try:
        now_dt = _parse_aware_iso(now)
        reaped = {}
        for key, entries in (binding or {}).items():
            if not isinstance(entries, dict):
                continue
            if _is_old_shape_binding_entry(entries):
                reaped[key] = entries
                continue
            kept = {}
            for abs_spine, entry in entries.items():
                if not isinstance(entry, dict) or not isinstance(entry.get("spine"), str):
                    continue
                spine = load_spine(entry.get("spine"))
                if spine is not None:
                    lease = spine.get("engine_session") or {}
                    if lease.get("status") == "released":
                        continue
                    kept[abs_spine] = entry
                    continue
                claimed_dt = _parse_aware_iso(entry.get("claimed_at"))
                if claimed_dt is not None and now_dt is not None:
                    age = (now_dt - claimed_dt).total_seconds()
                    if age >= REAP_MISSING_TARGET_GRACE_SECONDS:
                        continue
                kept[abs_spine] = entry
            if kept:
                reaped[key] = kept
        return reaped
    except Exception:
        return dict(binding or {})


def _replace_binding_atomically(project_dir: Path, data: dict) -> bool:
    """Write `data` to the registry through a UNIQUE same-directory temp name
    (never the fixed `.tmp` name `_save_json_map` uses) and `os.replace`.
    Best-effort cleanup of the temp file on any failure. Returns False (never
    raises) on any open/write/replace error -- the caller treats that as a
    fail-open transaction abort with the registry left exactly as it was."""
    path = binding_path(project_dir)
    tmp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        return True
    except Exception:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
        return False


def _binding_transaction(project_dir: Path, mutate, *, now=None):
    """Run one binding-store writer transaction: acquire the stable sibling
    lock, load the raw registry, safe-reap it, hand the reaped nested map to
    `mutate`, and -- only if the result differs from what was loaded --
    persist it through a unique-temp atomic replace before releasing the
    lock.

    `mutate(reaped: dict) -> dict | None` receives the LOCKED, REAPED map and
    returns the new map to persist (even if it decides there is nothing to
    change -- equality with the loaded map is what skips the write), or None
    to abandon the transaction outright (used when the write is invalid even
    under the fresh locked snapshot, e.g. a claim target that no longer
    validates).

    Fails open -- returns None, registry left byte-unchanged -- on lock-file
    open failure, lock contention, lock timeout, any lock-API error, or a
    replace failure. NEVER raises."""
    lock_file = _open_lock_file(project_dir)
    if lock_file is None:
        return None
    try:
        if not _acquire_lock(lock_file):
            return None
        try:
            raw = _load_json_map(binding_path(project_dir))
            now_str = now() if callable(now) else (now or _now_iso())
            reaped = _reap_binding_entries(raw, now_str)
            new_map = mutate(reaped)
            if new_map is None:
                return None
            if new_map != raw:
                if not _replace_binding_atomically(project_dir, new_map):
                    return None
            return new_map
        finally:
            _unlock(lock_file)
    except Exception:
        return None
    finally:
        try:
            lock_file.close()
        except Exception:
            pass


# --- per-agent binding identity (#419) ---------------------------------------

BINDING_KEY_SEP = "#"

# The SOLE acting-agent-id predicate (#441): an ALLOWLIST, not a denylist.
# `agent_id` is a harness field this repo does not own, and the gauge writer
# interpolates it into a filesystem path (`agent-{agent_id}.jsonl`), so the
# admitted alphabet must be exactly what both consumers can safely use --
# never a hand-maintained reject list that can admit a character (`:`, `*`,
# `?`, space, `.`) neither consumer actually wants. binding_key() below and
# gauge_writer_hook._is_usable_agent_id both drive off this ONE definition so
# the two hooks cannot drift out of step with each other again.
_AGENT_ID_ALLOWED = re.compile(r"\A[A-Za-z0-9_-]{1,64}\Z")


def is_usable_agent_id(agent_id) -> bool:
    """True only for a 1-64 character ASCII alnum/`_`/`-` string. NEVER
    raises. This is the authoritative predicate (#441) -- callers must not
    reimplement or widen it."""
    try:
        return isinstance(agent_id, str) and _AGENT_ID_ALLOWED.match(agent_id) is not None
    except Exception:
        return False


def binding_key(payload: dict):
    """The outer key this payload's binding is filed under -- the SINGLE place
    the composite per-agent key is composed anywhere in the codebase (the gauge
    writer calls this same function through its `_spine_rail` module handle, so
    the two hooks cannot drift).

    Agent-tool subagents SHARE their parent's `session_id`, so keying on
    `session_id` alone piles every crew claim under one key and the gauge writer
    -- seeing more than one candidate -- calls it ambiguous and writes nothing.
    The harness hands the acting agent's identity over directly as `agent_id`
    (measured live on 2.1.222; see tests/fixtures/probe_payloads.jsonl), so the
    key is a payload lookup, never a search.

    Three-way, deliberately not two-way:

    | payload                                     | returns                  |
    |---------------------------------------------|--------------------------|
    | `session_id`, no `agent_id` (top-level)     | bare `session_id`        |
    | `session_id` + well-formed `agent_id`       | `"<session_id>#<agent>"` |
    | `agent_id` present but UNUSABLE             | `None`                   |
    | `session_id` falsy                          | `None`                   |

    `None` means BIND NOTHING -- the caller writes no entry at all. An unusable
    `agent_id` must NOT fall back to the bare `session_id`: that would file the
    SUBAGENT's entry under the PARENT's key, push the parent to two candidates
    and silence the PARENT's gauge, manufacturing exactly the blindness this
    keying exists to remove. Failing closed costs that one subagent its binding
    and affects nobody else.

    A present-but-null `agent_id` reads as unusable, not as absent: it is not a
    string, and the probed harness omits the key entirely for a top-level agent
    rather than sending null.
    """
    try:
        data = payload or {}
        sid = data.get("session_id")
        if not sid:
            return None
        if "agent_id" not in data:
            return sid  # top-level agent -- behavior unchanged
        agent_id = data.get("agent_id")
        if not is_usable_agent_id(agent_id):
            return None
        return "{sid}{sep}{aid}".format(sid=sid, sep=BINDING_KEY_SEP, aid=agent_id)
    except Exception:
        return None


def _session_keys(binding: dict, sid) -> list[str]:
    """The ordered list of `binding` keys that "this session's view" merges:
    the bare `sid` key (if present) plus every per-agent key
    `sid + BINDING_KEY_SEP + <agent_id>`, in `binding`'s own iteration order.

    Reproduces session_view's exact two-branch asymmetry on purpose, not
    tidied into one coerced-to-str check: the bare-key branch is an untyped
    `key == sid` equality (whatever type `sid` is), while the composite
    branch requires `isinstance(key, str) and key.startswith(prefix)` --
    a non-str key can never match the prefix branch, but CAN match the bare
    branch if `sid` itself is that same non-str value. `session_view` and
    `session_view_provenance` both fold over this SAME list so they can never
    disagree about what's visible to `sid`. Never raises; [] on unusable
    input (falsy `sid`, non-dict `binding`).
    """
    try:
        if not sid:
            return []
        prefix = "{sid}{sep}".format(sid=sid, sep=BINDING_KEY_SEP)
        keys = []
        for key in (binding or {}).keys():
            if key == sid or (isinstance(key, str) and key.startswith(prefix)):
                keys.append(key)
        return keys
    except Exception:
        return []


def session_view(binding: dict, sid) -> dict:
    """The merged `{abs_spine_path: entry}` a harness session can see: the bare
    `sid` key plus every per-agent key `sid + BINDING_KEY_SEP + <agent_id>`.

    Readers (decide_stop, decide_session_start) must keep seeing every spine
    they saw before the per-agent split, so they read through this view rather
    than `binding[sid]`. Never raises; returns {} on anything unusable.
    """
    merged = {}
    try:
        if not sid:
            return {}
        binding = binding or {}
        for key in _session_keys(binding, sid):
            entries = binding.get(key)
            if not isinstance(entries, dict):
                continue
            merged.update(entries)
        return merged
    except Exception:
        return {}


def session_view_provenance(binding: dict, sid) -> dict[str, str]:
    """Maps each `abs_spine_path` in `session_view(binding, sid)`'s result to
    the binding key that sourced it -- the bare `sid`, or a composite
    `sid#agent_id` key.

    Built from the SAME `_session_keys(binding, sid)` list `session_view`
    folds over, so the two can never disagree about what's visible to `sid`.
    Last-key-wins on a path collision, matching `session_view`'s own
    `dict.update` overwrite semantics exactly (later keys in `_session_keys`
    order win, same as a later `merged.update(entries)` call overwriting an
    earlier one). Never raises; {} on falsy `binding`/`sid`.
    """
    try:
        if not binding or not sid:
            return {}
        owners = {}
        for key in _session_keys(binding, sid):
            entries = binding.get(key)
            if not isinstance(entries, dict):
                continue
            for spine_path in entries.keys():
                owners[spine_path] = key
        return owners
    except Exception:
        return {}


def load_nudges(project_dir: Path) -> dict:
    return _load_json_map(nudge_path(project_dir))


def save_nudges(project_dir: Path, data: dict) -> None:
    _save_json_map(nudge_path(project_dir), data)


# --- pure state-file readers -------------------------------------------------

def load_spine(spine_path) -> dict | None:
    """json.load the spine state file. Return None on any failure."""
    try:
        with open(spine_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def active_id(spine: dict):
    """First item id whose task status is NOT terminal; None if all terminal."""
    try:
        items = spine.get("items") or []
        tasks = spine.get("tasks") or {}
        for iid in items:
            task = tasks.get(iid) or {}
            if task.get("status") not in TERMINAL:
                return iid
        return None
    except Exception:
        return None


def journal_seq(spine_path) -> int:
    """Progress signal: count of non-blank lines in <spine_path>.journal.

    0 if the journal is absent or unreadable. NEVER raises.
    """
    try:
        jpath = str(spine_path) + ".journal"
        count = 0
        with open(jpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    except Exception:
        return 0


def reconstruct_current(spine: dict) -> str:
    """Rebuild the engine's `current` output from the state file (no subprocess).

    Optional `LEASE active: ...` line, then `ACTIVE <aid> [<status>] -- <imp>`
    or `DONE: no open items.` when every item is terminal.
    """
    lines = []
    lease = spine.get("engine_session") or {}
    if lease.get("status") == "active":
        lines.append(
            "LEASE active: {sid} (by {by}, heartbeat {hb})".format(
                sid=lease.get("session_id"),
                by=lease.get("claimed_by"),
                hb=lease.get("last_heartbeat"),
            )
        )
    aid = active_id(spine)
    if aid is None:
        lines.append("DONE: no open items.")
    else:
        task = (spine.get("tasks") or {}).get(aid) or {}
        lines.append(
            "ACTIVE {aid} [{status}] -- {imp}".format(
                aid=aid,
                status=task.get("status"),
                imp=task.get("imperative"),
            )
        )
    return "\n".join(lines)


# --- path comparison and spine location --------------------------------------
#
# What this section is NOT, since it was for a long time: an ownership test.
# `_foreign_worktree` used to answer "is this bound spine mine to drive?" by
# comparing the stopping payload's cwd against the binding's recorded worktree.
# That is broken by construction (#609 lane F g3). Spines are 1:1 with work
# AREAS, not worktrees: a Commander gets a worktree, an in-tree crew works in
# its Commander's tree in its own area, so ONE worktree holds several spines and
# `same worktree, therefore mine` is wrong the moment a crew shares its
# Commander's tree. The tree answers WHERE; only the binding key answers WHOSE
# (decision:worktree-is-location-spine-path-is-identity).
#
# Ownership is decided by binding-key provenance at both former call sites, by
# the same comparison: `_own_entries`, which decide_stop and decide_session_start
# both call. Stated as one rule -- SELECTION is a property of the binding key at
# both sites, and BLOCKING, at the one site that blocks, is a property of the
# spine. The sites differ in what they do when the acting agent owns nothing
# visible, and that difference follows from the second half of the rule: a Stop
# blocks either way, so it still names the leading gate and withholds its
# imperative, while a SessionStart, blocking nothing, hands out nothing -- and
# writes nothing.
#
# That last clause has to name the WRITE and not just the render, and getting
# there took two corrections. `decide_session_start`'s fallback scan reads no
# binding key, but the branch it sits in WRITES one, under the bare `sid` --
# the same key this rule reads as OWN -- so a site that withheld at the
# selection and then fell through manufactured, one branch later, the very
# ownership it had just withheld, and the next Stop was answered with another
# agent's gate as its own (#609 lane F g3 rework 2). A withholding that feeds a
# writer is not a withholding.
#
# Withholding at the reader is still not enough, because that one write is
# reached by THREE states of the read rather than two (rework 3, B5):
#
#   - no binding at all: nothing has been claimed under this session, so there
#     is no attribution to contradict. #261's resumed session, and the scan is
#     its only route back to its own run. It binds, and must keep binding.
#   - a non-empty view the agent owns NONE of: withheld at the selection, scan
#     included, because a spine this session claimed would be in the view and
#     owned.
#   - a non-empty view the agent DOES own, whose spine no longer loads --
#     archived at closeout, deleted, moved, or an entry with no usable `spine`
#     field. Nothing is withheld there, correctly, and the scan may then hand
#     that agent whatever active-leased spine the tree holds, a sibling agent's
#     included: on one match by writing a binding as well, on two or more by
#     rendering alone.
#
# So the last word belongs to neither reader path but to
# `_attributed_to_another_key`, which refuses to file -- and, since rework 4,
# refuses to RENDER -- a path that THIS SESSION'S VIEW of the binding store
# already attributes to a DIFFERENT binding key. That view is what
# `session_view_provenance` returns: the bare `sid` plus this session's own
# `sid#agent_id` keys, never the store entire, so a claim filed under a
# different harness session_id is invisible to the rule and neither the write
# nor the render is withheld for one (rework 4, B7). Both of those are narrower
# than the question of whether the scan should bind a session to a spine NOBODY
# has claimed, which is genuinely open and is not answered anywhere in this
# file.
#
# What remains here compares paths and locates spines, and decides nothing
# about identity.

def _same_path(a, b) -> bool:
    """True if a and b name the same path after normcase+normpath.

    Fail-SAFE: on ANY exception return True. A comparison failure must never
    spuriously relax the rail into treating a driving session as foreign.
    """
    try:
        if not isinstance(a, str) or not isinstance(b, str):
            return True  # un-comparable input -> fail safe, do not relax
        na = os.path.normcase(os.path.normpath(a))
        nb = os.path.normcase(os.path.normpath(b))
        return na == nb
    except Exception:
        return True


def _worktree_from_spine(abs_spine):
    """The owning worktree for an absolute spine path, or None if none owns it.

    The rule: walk up to the NEAREST `.agent-work` ancestor and return its
    parent. Arbitrary depth. No `.agent-work` ancestor at all means unowned.

    This is deliberately lexical: an absolute claim path remains useful even
    after its checklist is archived, while payload cwd is a launch-time value
    that can belong to a different linked worktree. It answers LOCATION only --
    where the spine lives -- never "is this mine"; ownership is the lease, and
    among spines sharing one tree the discriminator is binding-key provenance.

    NEAREST, never outermost: paths of the shape
    `.agent-work/archive/<epic>/workspace/.agent-work/<id>/spine.json` exist in
    tree, and that inner segment belongs to a nested SANDBOX project rooted at
    `workspace/`. Taking the outermost would derive the real repo as the root of
    a spine that belongs to the sandbox.

    It used to require the exact one-level `.agent-work/<id>/<name>.json` shape
    and return None for anything deeper -- which made a crew's own plan under
    `.agent-work/<id>/crew-handoffs/<gate>/PLAN.json`, and every archived spine,
    read as unowned. Those SHAPE preconditions (`.json` suffix, non-empty work-id
    segment, exact depth) did not move away: they are now held by
    `_is_claim_layout`, at the one caller whose strictness is a security
    property. Only the ABSOLUTE-path precondition stays here, because a relative
    path's answer would depend on the ambient cwd -- the exact forgeable reading
    this derivation exists to remove.

    `os.path` rather than `Path`, and `normcase` + `normpath` rather than
    `realpath`: symlink resolution stays OUTSIDE, so `_is_valid_claim_target`'s
    second, resolved check can still fail (see its own docstring).

    This is the ONE implementation of the rule in the repo. Its specification is
    the shared case table in `tests/test_worktree_derivation.py`, which drives
    this function directly -- read the table, not this docstring, for what the
    rule admits. The engine-side twin was deleted in #609 g2 under
    `ADMIRAL_RULING-2` N2, once its consumers had gone; it re-lands in #610's
    wave together with #315, the consumer that threads the derived worktree into
    the engine's check runner, and re-derives against that same table. It will
    re-land as a COPY, not an import: this module is stdlib-only by design and
    may gain none.

    NEVER raises.
    """
    try:
        if not isinstance(abs_spine, str) or not os.path.isabs(abs_spine):
            return None
        target = os.path.normcase(".agent-work")
        current = os.path.dirname(os.path.normcase(os.path.normpath(abs_spine)))
        while True:
            head, tail = os.path.split(current)
            if tail == target:
                return head or None
            if not head or head == current:
                return None
            current = head
    except Exception:
        return None


def _is_claim_layout(abs_spine) -> bool:
    """Whether `abs_spine` has the narrow `<worktree>/.agent-work/<work-id>/
    <name>.json` shape a bindable claim target must have.

    This is the shape half of what `_worktree_from_spine` used to conflate with
    the location half. Splitting them is the point of the change: location is a
    property of any path, while THIS is the ownership gate's admission test, and
    widening the first must not widen the second.

    Deliberately case-SENSITIVE on the `.agent-work` segment, matching what this
    predicate accepted before the split. `_worktree_from_spine` now folds case
    (on Windows), so on that platform this is the stricter of the two -- which is
    correct: the gate is required to accept exactly what it accepted before, and
    it never accepted `.AGENT-WORK`.

    NEVER raises.
    """
    try:
        if not isinstance(abs_spine, str):
            return False
        spine = Path(abs_spine)
        if not spine.is_absolute() or not spine.name.endswith(".json"):
            return False
        work_id = spine.parent
        if spine.name == ".json" or not work_id.name:
            return False
        return work_id.parent.name == ".agent-work"
    except Exception:
        return False


# --- PostToolUse: command-token parsing --------------------------------------

def _tokenize(command: str) -> list:
    try:
        return shlex.split(command)
    except Exception:
        return command.split()


def _extract_verb(tokens: list):
    """Positional verb after the engine script token, skipping the global
    --file <path> option. Returns None if not found."""
    idx = None
    for i, tok in enumerate(tokens):
        if "checklist_engine.py" in tok:
            idx = i
            break
    if idx is None:
        return None
    i = idx + 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--file":
            i += 2
            continue
        if tok.startswith("--file="):
            i += 1
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok
    return None


def _extract_opt(tokens: list, name: str):
    """Value of `--name value` or `--name=value`; None if absent."""
    prefix = name + "="
    for i, tok in enumerate(tokens):
        if tok == name:
            return tokens[i + 1] if i + 1 < len(tokens) else None
        if tok.startswith(prefix):
            return tok[len(prefix):]
    return None


# --- #440: validated candidate-root resolution of a relative --file ----------
#
# The payload carries NO per-agent root. `CLAUDE_PROJECT_DIR` is fixed at
# session launch (#269, not ours to change -- decision:not-fixing-269) and the
# payload's `cwd` is the SESSION LAUNCH directory, measured identical across a
# parent and its subagents (tests/fixtures/probe_payloads.jsonl, six real
# payloads). So "join the relative --file onto cwd and trust it" recorded a
# main-checkout path for every worktree-dispatched agent: 60 of 64 live entries
# on 2026-08-05. The resolution must therefore VERIFY against the filesystem
# rather than compute an answer it cannot check
# (decision:fix-the-resolution-not-the-caller).

PATH_SOURCE_ABSOLUTE = "absolute"
PATH_SOURCE_WORKTREE_OPT = "worktree_opt"
PATH_SOURCE_CD_TARGET = "cd_target"
PATH_SOURCE_PAYLOAD_CWD = "payload_cwd"
PATH_SOURCE_GIT_WORKTREE = "git_worktree"
PATH_SOURCE_PROJECT_DIR = "project_dir"
PATH_SOURCE_DOOR_ENV = "door_env"

# TOLD TRUTH vs GUESS (#440 g1b). The first three sources are the CALLER's own
# statement of where it is -- an absolute --file, an absolute --worktree, a `cd`
# in its own command. The rest are inferences this hook makes on the caller's
# behalf. Only the inferences can be wrong about which tree the agent meant, so
# only the inferences are subject to the ambiguity guard in
# `resolve_spine_candidate`; a told-truth rung short-circuits ahead of it.
TOLD_TRUTH_PATH_SOURCES = frozenset((
    PATH_SOURCE_ABSOLUTE,
    PATH_SOURCE_WORKTREE_OPT,
    PATH_SOURCE_CD_TARGET,
))


def looks_like_checklist(path) -> bool:
    """True only if `path` is a readable JSON OBJECT carrying a top-level
    `items` LIST -- the weakest test that positively identifies a checklist.

    Existence alone is NOT enough, and that is the whole point: the defect this
    resolution fixes has been CREATING phantom `.agent-work/<work_id>/` trees
    inside the main checkout (the gauge writer's atomic write makes parent
    directories), so `exists()` can be decoyed by leftovers from the very bug
    being fixed. A stray `gauge.json` has no `items`; a checklist always does --
    `active_id` reads exactly `items` + `tasks`, and the engine cannot drive a
    file without them.

    `tasks` is deliberately NOT also required: `items` alone already separates a
    checklist from every leftover this hook can meet, and a stricter test only
    buys new ways to reject a legitimate file. NEVER raises.
    """
    try:
        if not path:
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return isinstance(data, dict) and isinstance(data.get("items"), list)
    except Exception:
        return False


def normalize_shell_path(text):
    """A path as a SHELL wrote it -> a path this process can open. None if
    unusable.

    Two shells reach this hook. The Bash tool on Windows is git-bash, so a `cd`
    target is routinely MSYS-style (`/c/Programs/foo`), which is not a valid
    Windows path and fails every existence test; PowerShell writes native form.
    Strips one layer of surrounding quotes (the `cd` target is parsed out of raw
    command TEXT, not out of shlex tokens, so its quotes survive).

    KNOWN, NOT CHASED (#440): a bare drive root written MSYS-style (`/c`) is not
    converted -- no engine command cd's to a drive root, and a two-character
    token is not worth the false-positive risk of rewriting any `/x` path.
    """
    try:
        if not isinstance(text, str):
            return None
        s = text.strip()
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
            s = s[1:-1].strip()
        if not s:
            return None
        # /c/Programs/foo -> C:/Programs/foo
        if len(s) > 3 and s[0] == "/" and s[1].isalpha() and s[2] == "/":
            s = s[1].upper() + ":/" + s[3:]
        return s
    except Exception:
        return None


# A PostToolUse hook runs on the turn's critical path, so the ONLY subprocess
# this module ever spawns is bounded by this. 2 seconds is generous for a local
# `git worktree list` (milliseconds warm) and short enough that a locked index,
# a dead network drive or a missing `git` costs the turn nothing it will notice.
GIT_PROBE_TIMEOUT_SECONDS = 2.0


def git_worktree_roots(project_dir) -> list:
    """Worktree roots registered against `project_dir`, EXCLUDING the main tree.

    The main tree is filtered out on purpose: rung 5 already yields the project
    dir, so leaving it in would only relabel that same answer as `git_worktree`
    and cost the `path_source` field its meaning. A `git_worktree` source now
    says exactly one thing -- the spine was found in a DIFFERENT tree.

    This is the module's one subprocess, and it does not contradict the "do NOT
    subprocess the engine" contract in the docstring: the engine is a stateful
    thing whose answers must come from its state file, whereas `git` is being
    asked a question about the FILESYSTEM that no file in this repo records.

    Never raises, never hangs: any non-zero exit, timeout, missing binary or
    unparsable output returns []. The caller's generator is lazy, so this is not
    even reached unless rungs 0-3 all failed.
    """
    try:
        proc = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=GIT_PROBE_TIMEOUT_SECONDS,
        )
        if proc.returncode != 0:
            return []
        roots = []
        for line in (proc.stdout or "").splitlines():
            if not line.startswith("worktree "):
                continue
            root = line[len("worktree "):].strip()
            if root and not _same_path(root, str(project_dir)):
                roots.append(root)
        return roots
    except Exception:
        return []


# A `cd` / `pushd` / `Set-Location` and its target, anywhere in the observed
# command text. The leading class is a command-position guard so `--cd x` and
# `abcd x` do not match. `;` is in the separator class because PowerShell 5.1
# has no `&&` and chains with `;`. Quoted alternatives come first so a target
# containing spaces is captured whole.
_CD_RE = re.compile(
    r"""(?:^|[;&|(]|\s)(?:cd|pushd|Set-Location)\s+("[^"]*"|'[^']*'|[^\s;&|]+)""",
    re.IGNORECASE,
)


def last_cd_target(command):
    """The LAST `cd`/`pushd`/`Set-Location` target in `command`, or None.

    KNOWN, NOT CHASED (#440): only the last one is tried. An earlier `cd` in the
    same command is not a fallback -- if the last target does not validate the
    ladder moves on to the next RUNG rather than to an earlier `cd`. Every
    engine invocation this hook has been measured against has at most one.
    """
    try:
        matches = _CD_RE.findall(command or "")
        return matches[-1] if matches else None
    except Exception:
        return None


def _candidate_roots(data: dict, project_dir: Path, tokens: list, command: str):
    """Candidate roots for a relative `--file`, in ladder order, as a GENERATOR.

    Lazy on purpose: rung 4 shells out to `git`, and a PostToolUse hook must not
    pay for -- or hang on -- a subprocess it does not need. A consumer that stops
    at a TOLD-TRUTH rung (0-2) never advances the generator far enough to run it,
    which is the case a worktree-dispatched agent always takes.

    Since g1b (#440) a consumer that reaches the GUESSED rungs does drain the
    generator, because it cannot know its guess is unambiguous without asking
    every other guessed rung -- so `git` is spawned there. That is still not the
    turn's hot path: `handle_post_tool_use` returns before any of this unless the
    observed command is an engine `claim` or `release`, which happens twice per
    run, not once per tool call.
    """
    cwd = data.get("cwd")

    # Rung 1: an ABSOLUTE --worktree in the observed command. Relative forms are
    # skipped rather than joined: the engine's own convention is `--worktree .`,
    # which resolves against the same untrustworthy cwd this whole ladder exists
    # to stop trusting, so it would be a wrong answer wearing a right label.
    wt = normalize_shell_path(_extract_opt(tokens, "--worktree"))
    if wt and Path(wt).is_absolute():
        yield wt, PATH_SOURCE_WORKTREE_OPT

    # Rung 2: the last cd/Set-Location/pushd target in the command text. A
    # relative target resolves against the payload cwd; if that does not
    # validate the ladder falls through -- it never guesses a second base.
    cd = normalize_shell_path(last_cd_target(command))
    if cd:
        cd_path = Path(cd)
        if cd_path.is_absolute():
            yield str(cd_path), PATH_SOURCE_CD_TARGET
        elif cwd:
            yield str(Path(cwd) / cd_path), PATH_SOURCE_CD_TARGET

    # Rung 3: the payload cwd -- today's behaviour, now merely a candidate.
    if cwd:
        yield str(cwd), PATH_SOURCE_PAYLOAD_CWD

    # Rung 4: every OTHER git worktree registered against the project dir. This
    # is the only rung that answers when the command carries no positional clue
    # at all -- an agent whose Bash tool already runs inside its worktree writes
    # no `cd`, so nothing in the payload names its root.
    for root in git_worktree_roots(project_dir):
        yield root, PATH_SOURCE_GIT_WORKTREE

    # Rung 5: the project dir.
    yield str(project_dir), PATH_SOURCE_PROJECT_DIR


def resolve_spine_candidate(file_val, data: dict, project_dir: Path,
                            tokens: list, command: str):
    """`(abs_spine, path_source)` for this command's `--file`, or `(None, None)`.

    Rung 0 first: an absolute `--file` is ground truth and is taken AS-IS,
    deliberately WITHOUT a validity test. Validating it would break the case the
    store most needs to survive -- a `release` whose spine has already been
    archived, moved or deleted must still be able to name its own entry.

    Otherwise the first TOLD-TRUTH root (rungs 1-2) that yields a VALIDATING
    checklist wins outright, exactly as before -- the caller stated where it is,
    so there is nothing to be uncertain about and nothing to weigh it against.

    The GUESSED rungs (3 onward) are held to a stricter rule (#440 g1b): the
    EARLIEST validating guess is kept, but if a later guess validates a
    DIFFERENT file the answer is thrown away and NOTHING is bound. `.agent-work/`
    is tracked, so a committed checklist sits at the same relative path in the
    main checkout and in every worktree; without this the payload cwd (rung 3)
    simply beat the worktree (rung 4) and the store recorded the main checkout's
    copy -- a confident wrong path, the failure class this whole issue exists to
    end. Skip on uncertainty is the store's own posture and it is not symmetric:
    a missing binding is recoverable, a wrong one silently misattributes one
    agent's context reading to another agent's work area.

    Two guesses resolving to the SAME file are AGREEMENT, not ambiguity (rung 5
    re-yields the payload cwd whenever a top-level agent runs in the project
    dir) -- bind it, and keep the earliest rung's `path_source`.

    `(None, None)` means BIND NOTHING: a binding naming a spine that is not
    there is precisely the defect being fixed, so silence beats a confident
    wrong record (the same fail-closed posture as `binding_key` returning None,
    and the same refusal `resolve_recorded_release_target` makes on two matches).
    NEVER raises.

    KNOWN, NOT CHASED (#440 g1b): the guard is all-or-nothing across the guessed
    rungs -- it does not try to BREAK a tie (by mtime, by lease freshness, or by
    reading which spine is actually active). Any such tie-break is a new guess
    layered on the guesses that just disagreed, which is what this is refusing.
    """
    try:
        if not file_val:
            return None, None
        rel = Path(file_val)
        if rel.is_absolute():
            return str(rel), PATH_SOURCE_ABSOLUTE
        guess = None  # (abs_path, source) of the EARLIEST validating guess
        for base, source in _candidate_roots(data, project_dir, tokens, command):
            try:
                candidate = str((Path(base) / rel).resolve())
            except Exception:
                continue
            if not looks_like_checklist(candidate):
                continue
            if source in TOLD_TRUTH_PATH_SOURCES:
                return candidate, source
            if guess is None:
                guess = (candidate, source)
            elif not _same_path(candidate, guess[0]):
                return None, None  # two guesses, two files -> refuse to guess
        return guess if guess is not None else (None, None)
    except Exception:
        return None, None


def resolve_recorded_release_target(file_val, key_bindings):
    """The one recorded `abs_spine` under this key that a relative `--file`
    names, or None when the answer is ambiguous or absent.

    `release` is not `claim`, and the filesystem ladder is the wrong tool for
    it: by release time the spine may already be archived, moved or deleted, so
    NO candidate would validate, the entry would never be removed, and nothing
    reaps abandoned keys (#419). A release must be able to remove what its own
    claim put there, and the store itself is the record of what that was.

    Exactly one match wins. Two matches is genuine ambiguity -- one session_id
    can legitimately hold two spines whose relative paths are identical in two
    different trees (#202) -- and guessing between them would delete a live
    agent's binding. The caller falls through to the ladder instead.
    """
    try:
        if not file_val or not key_bindings:
            return None
        rel = str(file_val).replace("\\", "/").strip().lower()
        while rel.startswith("./"):
            rel = rel[2:]
        if not rel:
            return None
        # Leading separator: `run1/spine.json` must not match a recorded
        # `.../run11/spine.json`.
        suffix = "/" + rel
        matches = [
            path for path in key_bindings
            if isinstance(path, str) and path.replace("\\", "/").lower().endswith(suffix)
        ]
        return matches[0] if len(matches) == 1 else None
    except Exception:
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_valid_claim_target(abs_spine) -> bool:
    """The rail-owned claim-target validator (#441): a resolved absolute
    target must be lexically/resolve-CONTAINED as
    `<worktree>/.agent-work/<work-id>/<name>.json` AND a currently readable
    JSON object carrying an `items` list. `_is_claim_layout` enforces exactly
    that containment shape (it returns False for anything outside it), so this
    composes it with `looks_like_checklist` rather than re-deriving the shape
    test. Applied to BOTH absolute and relative claim
    resolution -- rung 0 (an absolute `--file`) is ground truth about WHERE
    the caller means, never about whether that target is a real, current
    checklist. Re-checked inside the locked mutator so a target that vanishes
    between resolution and lock acquisition cannot bind.

    The shape test is `_is_claim_layout`, NOT `_worktree_from_spine`. The two
    were the same function until the derivation was widened to nearest-ancestor
    at arbitrary depth; keeping this gate on the derivation would have widened
    what the rail accepts as a claimable spine along with it, silently turning a
    change about LOCATION into a change to the OWNERSHIP gate. This admission
    test accepts exactly what it accepted before that split, and
    `tests/test_spine_rail.py` pins that both ways.

    Symlink-escape guard: the LEXICAL path can satisfy the containment shape
    while a symlink -- the leaf file itself, or an ancestor directory -- walks
    the REAL file somewhere else entirely. `Path.resolve()` follows every
    symlink in the chain, so re-running the identical containment check
    against the resolved path catches an escape the lexical check alone would
    miss; a target with no symlinks resolves to itself and this is a no-op.
    This is also why the derivation stays lexical: were it to resolve symlinks
    itself, both checks would return the same value and the second could never
    fail. NEVER raises."""
    try:
        if not _is_claim_layout(abs_spine):
            return False
        if not looks_like_checklist(abs_spine):
            return False
        resolved = str(Path(abs_spine).resolve())
        return _is_claim_layout(resolved)
    except Exception:
        return False


def _handle_door_lease(data: dict, project_dir: Path) -> dict:
    """Maintain the session->spine binding from a DOOR-issued spine_lease
    claim/release (`DOOR_LEASE_TOOL_NAME`) -- the second, additive binding-
    writing source alongside the Bash `checklist_engine.py` path below.

    The door call carries NO `--file`: `SPINE_FILE`/`SPINE_SESSION` are THIS
    hook process's OWN environment, per `scripts/mcp_spine_server.py`'s
    existing contract (`_spine_from_env`, which reads
    `os.environ.get("SPINE_FILE", "").strip()` and answers `None` -- never
    raising, never binding a cwd -- when unset, empty or whitespace, with
    readability asked per call by `_unbound_refusal` rather than once at
    import; issues #603 and #604), so the claimed spine's absolute path is
    resolved from this process's own environment -- never guessed from a
    candidate-root ladder the way the Bash `--file` path is
    (decision:door-binding-source-of-truth). Reuses
    `_is_valid_claim_target` UNCHANGED (#441's containment/readability
    validator) -- no second validator.

    Fail-open, always: a missing/non-dict `tool_input`, an unrecognized
    `action`, an unresolved acting identity, or an unresolvable/out-of-tree
    `SPINE_FILE` records no binding and raises nothing -- returns {}
    unconditionally, same contract as `handle_post_tool_use`.
    """
    try:
        tool_input = data.get("tool_input")
        if not isinstance(tool_input, dict):
            return {}
        action = tool_input.get("action")
        if action not in ("claim", "release"):
            return {}
        sid = data.get("session_id")
        key = binding_key(data)
        if key is None:
            return {}  # unresolved identity -> bind nothing (fail closed)
        file_val = os.environ.get("SPINE_FILE")
        if not file_val:
            return {}
        try:
            abs_spine = str(Path(file_val).resolve())
        except Exception:
            return {}

        if action == "claim":
            if not _is_valid_claim_target(abs_spine):
                return {}
            engine_session = os.environ.get("SPINE_SESSION")
            worktree = _worktree_from_spine(abs_spine)
            if not worktree:
                return {}

            def _door_claim_mutate(reaped, _abs_spine=abs_spine, _key=key,
                                    _engine_session=engine_session, _worktree=worktree):
                # Re-check under the lock (#441): the target may have moved
                # or vanished between resolution above and lock acquisition.
                if not _is_valid_claim_target(_abs_spine):
                    return None
                new_map = dict(reaped)
                key_bindings = dict(new_map.get(_key) or {})
                key_bindings[_abs_spine] = {
                    "spine": _abs_spine,
                    "engine_session": _engine_session,
                    "worktree": _worktree,
                    "claimed_at": _now_iso(),
                    "path_source": PATH_SOURCE_DOOR_ENV,
                }
                new_map[_key] = key_bindings
                return new_map

            _binding_transaction(project_dir, _door_claim_mutate)
        else:  # release -- SPINE_FILE is authoritative, no ladder needed
            def _door_release_mutate(reaped, _key=key, _abs_spine=abs_spine):
                new_map = dict(reaped)
                key_bindings = dict(new_map.get(_key) or {})
                if key_bindings and _abs_spine in key_bindings:
                    key_bindings = dict(key_bindings)
                    del key_bindings[_abs_spine]
                    if key_bindings:
                        new_map[_key] = key_bindings
                    else:
                        new_map.pop(_key, None)
                return new_map

            _binding_transaction(project_dir, _door_release_mutate)
            # Same nudge-reset symmetry as the Bash release path: only for a
            # TOP-LEVEL release (key == sid), never fragmented per-entry.
            if key == sid:
                nudges = load_nudges(project_dir)
                if sid in nudges:
                    del nudges[sid]
                    save_nudges(project_dir, nudges)
        return {}
    except Exception:
        return {}


def handle_post_tool_use(data: dict, project_dir: Path) -> dict:
    """Maintain the session->spine binding from engine claim/release commands.

    One session_id can hold a binding into more than one distinct spine at
    once (#202) -- the binding is keyed by the RESOLVED ABSOLUTE SPINE PATH
    itself (`abs_spine`), not by worktree or cwd
    (decision:key-binding-by-spine-path-not-worktree-or-cwd). A claim writes
    only `binding[key][abs_spine]`, leaving any other abs_spine_path entries
    for that key untouched; a release removes only that one entry.

    The OUTER key is `binding_key(data)` (#419), not the bare `session_id`:
    subagents share their parent's session_id, so keying on it alone piled
    every crew claim under one key and left the gauge writer with no way to
    tell whose reading it held. `binding_key` returning None means the acting
    identity is unresolved -- bind NOTHING, write no entry at all.

    Both mutations now go through `_binding_transaction` (#441): one stable
    sibling lock covers load -> safe reap -> this mutation -> unique-temp
    atomic replace, closing the lost-update/torn-write window that an
    unlocked load-modify-save left open under concurrent writers.

    A second, additive source now feeds the same store: a door-issued
    `DOOR_LEASE_TOOL_NAME` claim/release (dispatched to `_handle_door_lease`
    below, before any Bash command parsing) -- the Bash path below this
    dispatch is otherwise untouched and unreached for a door payload.

    PostToolUse NEVER blocks -- always returns {}.
    """
    try:
        if data.get("tool_name") == DOOR_LEASE_TOOL_NAME:
            return _handle_door_lease(data, project_dir)
        command = ((data.get("tool_input") or {}).get("command")) or ""
        if not command:
            return {}
        tokens = _tokenize(command)
        if not any("checklist_engine.py" in tok for tok in tokens):
            return {}
        verb = _extract_verb(tokens)
        if verb not in ("claim", "release"):
            return {}
        sid = data.get("session_id")
        key = binding_key(data)
        if key is None:
            return {}  # unresolved identity -> bind nothing (fail closed)
        file_val = _extract_opt(tokens, "--file")
        if verb == "claim":
            abs_spine, path_source = resolve_spine_candidate(
                file_val, data, project_dir, tokens, command
            )
            if not abs_spine or not _is_valid_claim_target(abs_spine):
                # No candidate root yields a real, contained checklist
                # (#440/#441) -- BIND NOTHING. A missing binding is
                # recoverable; a confident wrong one silently misattributes
                # one agent's context reading to another agent's work area.
                return {}
            engine_session = _extract_opt(tokens, "--session-id")
            worktree = _worktree_from_spine(abs_spine)
            if not worktree:
                return {}

            def _claim_mutate(reaped, _abs_spine=abs_spine, _key=key,
                               _engine_session=engine_session, _worktree=worktree,
                               _path_source=path_source):
                # Re-check under the lock (#441): the target may have moved
                # or vanished between resolution above and lock acquisition.
                if not _is_valid_claim_target(_abs_spine):
                    return None
                new_map = dict(reaped)
                key_bindings = dict(new_map.get(_key) or {})
                key_bindings[_abs_spine] = {
                    "spine": _abs_spine,
                    "engine_session": _engine_session,
                    "worktree": _worktree,
                    "claimed_at": _now_iso(),
                    # Provenance (#440): WHICH rung resolved the path.
                    # Additive VALUE field only -- the binding KEY shape
                    # (#419) is untouched.
                    "path_source": _path_source,
                }
                new_map[_key] = key_bindings
                return new_map

            _binding_transaction(project_dir, _claim_mutate)
        else:  # release
            # KNOWN, NOT CHASED (#419, filed as a triage candidate): a
            # successful release is the ONLY path that removes a key. An agent
            # that dies, is cancelled, or is killed mid-run leaves its key
            # behind forever, and per-agent keying multiplies the key count by
            # every wave's fan-out. The transaction's own safe reap (#441 m2)
            # is the bounded, conservative mitigation -- there is still no
            # unbounded global sweep.

            def _release_mutate(reaped, _key=key, _file_val=file_val):
                new_map = dict(reaped)
                key_bindings = dict(new_map.get(_key) or {})
                # Recorded binding FIRST (#440), against the LOCKED, REAPED
                # snapshot -- see resolve_recorded_release_target. Only when
                # that finds nothing does the filesystem ladder run.
                target = resolve_recorded_release_target(_file_val, key_bindings)
                if not target:
                    target, _ = resolve_spine_candidate(
                        _file_val, data, project_dir, tokens, command
                    )
                if target and key_bindings and target in key_bindings:
                    key_bindings = dict(key_bindings)
                    del key_bindings[target]
                    if key_bindings:
                        new_map[_key] = key_bindings
                    else:
                        # Delete THIS key's now-empty entry set -- `key`,
                        # never `sid`. Under a composite key those are
                        # different keys, and deleting the bare one here
                        # would wipe a live parent's entire binding.
                        new_map.pop(_key, None)
                return new_map

            _binding_transaction(project_dir, _release_mutate)
            # The nudge / three-strike escape-hatch ledger is documented and
            # written (decide_stop) under the BARE session_id, and it stays
            # that way: splitting strikes per-agent would fragment the count
            # and weaken the hatch. It lives outside the binding-store
            # transaction -- it is not a binding-store writer.
            # It also fires only for a TOP-LEVEL release (`key == sid`). The
            # strikes belong to the session whose turn-ends get nudged, so a
            # subagent releasing its own spine must not reset its parent's
            # count.
            if key == sid:
                nudges = load_nudges(project_dir)
                if sid in nudges:
                    del nudges[sid]
                    save_nudges(project_dir, nudges)
        return {}
    except Exception:
        return {}


# --- Stop: refuse dishonest mid-spine turn-ends ------------------------------

def _mid_flight_reason(spine: dict, aid) -> str:
    if aid is None:
        return (
            "SPINE MID-FLIGHT: every item is terminal but the engine lease is "
            "still ACTIVE -- the run is not closed until the lease is released. "
            "Run the engine's release verb to close the lease before ending "
            "your turn; do not end your turn to wait with an open lease."
        )
    imperative = ((spine.get("tasks") or {}).get(aid) or {}).get("imperative") or ""
    return (
        "SPINE MID-FLIGHT: gate {aid} is still open -- you are in the MIDDLE of "
        "the spine, not at its end, so ending your turn now abandons an active "
        "run. This Stop hook is authoritative over any SOFT-band context-trip "
        "advisory you saw on spine_status/current -- that advisory is "
        "non-binding guidance, never license to end this turn. "
        "Next imperative: {imp} "
        "If you genuinely cannot continue (context exhausted, truly blocked), "
        "the sanctioned exit is the engine's block verb -- spine_halt block -- "
        "with a reason, or waive the check with human authority; do not end "
        "your turn to \"hand off.\""
    ).format(aid=aid, imp=imperative)


def _owning_session_reason(spine_path: str, owner_key: str) -> str:
    """Stop-block reason for a mid-flight entry reachable ONLY through a
    per-agent key (`owner_key`) that is not this stopping session's own bare
    id -- e.g. a subordinate subagent's gate, visible to the parent purely
    because they share a harness `session_id`.

    Deliberately withholds the owning gate's next imperative (#549): a
    subordinate's own next-step text rendered into the PARENT's Stop-block
    reason reads as an instruction for the parent to go execute, which is not
    this session's gate to drive. Still names the stop as BLOCKED and points
    at who actually owns it, so the parent does not read silence as "done."
    """
    return (
        "SPINE MID-FLIGHT (foreign-owned): a gate on {spine} is still open "
        "under {owner} -- STILL BLOCKED, but this is not your gate to drive. "
        "It belongs to a different session/agent (bound under a per-agent "
        "key you merely share a harness session with), so do not act on its "
        "next step yourself. Let that session/agent finish or bubble its own "
        "blocker; if you believe it has gone silent, investigate that "
        "session rather than ending your own turn to wait on it here."
    ).format(spine=spine_path, owner=owner_key)


def _is_own_entry(owner_key, own_key) -> bool:
    """Whether a visible binding entry belongs to the AGENT that is acting.

    `owner_key` is the binding key that sourced the entry
    (`session_view_provenance`); `own_key` is `binding_key(payload)`, the acting
    agent's own key. Ownership is that comparison and nothing else -- never the
    tree the entry sits in (#609 lane F g3, decision:worktree-is-location-spine-
    path-is-identity).

    Two deliberate readings of a missing key, in opposite directions:

    - `owner_key is None` -- provenance could not place this path at all. Read
      it as OWN, which preserves the pre-#549 rendering rather than inventing a
      foreign owner for an entry nobody can attribute.
    - `own_key is None` -- `binding_key` refused to compose a key for this
      payload (a malformed `agent_id`, #441's allowlist), so the hook cannot say
      who is acting. Nothing placed then matches, so every attributable entry
      reads as foreign. Each caller's no-match path is its own withholding
      direction: decide_stop still BLOCKS and withholds the imperative,
      decide_session_start hands out no gate -- and, where anything at all is
      visible, does not fall through to the scan that would bind one. That
      second clause is not decoration: the scan's bind writes the key this
      comparison reads, so without it an unidentifiable agent was handed an
      ownership record on its next call.

    NEVER raises.
    """
    try:
        if owner_key is None:
            return True
        return owner_key == own_key
    except Exception:
        return False


def _own_entries(candidates, owners, own_key) -> list:
    """The subset of `candidates` the ACTING agent owns, in the order given.

    `candidates` is any sequence whose element `[0]` is the abs spine path that
    `owners` (`session_view_provenance`) is keyed by -- decide_stop passes its
    mid-flight `(spine_path, spine, aid)` tuples, decide_session_start passes
    the merged view's `(spine_path, entry)` items. Both sites ask the SAME
    question with the SAME comparison, which is the point of naming it once:
    selection is a binding-key property at both call sites (#609 lane F g3).

    What each site does when this returns EMPTY differs on purpose, and the
    two are still not folded together. decide_stop has to answer a stop that
    blocks regardless, so it renders the leading entry with the imperative
    withheld. decide_session_start is deciding whether to hand out a gate at
    all, so it hands out nothing.

    An empty result at decide_session_start must not fall through into the
    fallback's bind-on-resume: that write files under the bare `sid`, which is
    the key this comparison reads as OWN, so falling through would undo this
    function's own answer one branch later (#609 lane F g3 rework 2).

    That is a rule about THIS result, and it has once been mistaken for the
    whole guard on that writer, which it is not: the same write is also reached
    with a NON-empty result here, by an agent that owns an entry whose spine no
    longer loads. Nothing this function returns can speak for that case. The
    write is guarded at the write, by `_attributed_to_another_key` (rework 3).

    NEVER raises; [] on unusable input, which is the withholding direction at
    both sites.
    """
    try:
        return [c for c in candidates if _is_own_entry(owners.get(c[0]), own_key)]
    except Exception:
        return []


def _attributed_to_another_key(owners, spine_path, bind_key) -> bool:
    """Whether `owners` ALREADY attributes `spine_path` to a binding key other
    than `bind_key` -- the key about to take that path, by filing it or by
    rendering its gate as this session's own.

    WHAT `owners` IS, AND IS NOT. Both call sites pass
    `session_view_provenance(binding, sid)`, which is THIS SESSION's view of the
    binding store -- the bare `sid` plus this session's own `sid#agent_id` keys
    -- and never the store entire. A path claimed under a DIFFERENT harness
    session_id is not in that mapping, so this answers False for it and the
    caller proceeds. That gap is measured rather than assumed, and it is not
    exotic: every crew on this project is launched as its own session. Whether a
    resume may bind or render across a session boundary is an open authority
    question and is not settled here (#609 lane F g3 rework 4, B7).

    This is the ownership comparison asked from the CLAIMING side.
    `_is_own_entry` asks a reader "is this entry mine?"; this asks "would taking
    this path contradict an attribution already visible here?" The two are
    separate questions, and this one has to be asked at the bind-on-resume,
    because that branch is reached by more than one reader path and a
    reader-side answer only covers the path it was written for (rework 3, B5).
    Rework 4 asks it of that same branch's RENDER selection too: handing out a
    gate the view attributes elsewhere contradicts that attribution exactly as
    much as filing it does (B6).

    What it deliberately does NOT decide: whether the scan should bind or render
    at all. A path attributed to NOBODY is not a contradiction, so #261's
    resumed session and #202's sibling merge are both untouched -- the authority
    question about binding a session to a spine no one claimed is recorded
    separately and is not settled here.

    Paths are compared with `_same_path`, so a differently-spelled route to the
    same file still counts as the same attribution. Unusable input answers
    True: this guards a write and a render, and withholding either is the
    fail-safe direction, exactly as `_same_path`'s own True-on-exception is at
    the comparison one layer down. NEVER raises.
    """
    try:
        for path, owner_key in owners.items():
            if owner_key == bind_key:
                continue
            if _same_path(path, spine_path):
                return True
        return False
    except Exception:
        return True


def _entry_mid_flight_view(entry: dict):
    """Per-entry mid-flight check, unchanged in substance from the pre-#202
    single-entry logic -- just factored so decide_stop can apply it to every
    bound abs_spine_path entry for a session_id, not just one.

    Returns None if this entry is NOT a genuine mid-flight blocker (unreadable
    spine, released/inactive lease, or an honest engine block); else
    `(spine_path, spine_dict, aid)`.

    Mid-flight is a property of the SPINE -- an open gate under an active lease
    -- so nothing here reads the payload. It used to skip an entry whose
    recorded worktree differed from the stopping payload's cwd, on the theory
    that a different tree meant a different driver; that skip let a session walk
    away from its own mid-flight run whenever it stopped from somewhere else,
    and did nothing at all about the case it was aimed at, an in-tree crew.
    WHOSE gate this is is decided by binding-key provenance in decide_stop,
    which is also the only thing that decision may change: what gets rendered,
    never whether an open gate blocks.
    """
    spine_path = entry.get("spine")
    if not spine_path:
        return None
    spine = load_spine(spine_path)
    if spine is None:
        return None  # unreadable -> allow
    lease = spine.get("engine_session") or {}
    if lease.get("status") != "active":
        return None  # run closed -> allow
    aid = active_id(spine)
    tasks = spine.get("tasks") or {}
    if aid is not None and (tasks.get(aid) or {}).get("status") == "blocked":
        return None  # honest engine block -> allow
    return spine_path, spine, aid


def decide_stop(data: dict, project_dir: Path) -> dict:
    """Block the Stop if ANY bound entry for this session_id is genuinely
    mid-flight (same per-entry semantics as the pre-#202 single-entry version,
    just applied across every abs_spine_path entry now bound under `sid`). The
    nudge-tracking / 3-strike escape hatch stays keyed by `sid` ALONE -- never
    fragmented per-entry, which would weaken the escape hatch.

    Ownership decides WHAT IS RENDERED, never whether an open gate blocks
    (#609 lane F g3): every visible mid-flight entry blocks, and binding-key
    provenance picks which one the stopping agent is answered with -- its own
    gate where it has one, and otherwise the foreign-owner wording with the
    imperative withheld.
    """
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        # Read through the merged per-agent view (#419): a spine claimed by a
        # subagent now lives under `sid#agent_id`, and the stopping session
        # must still see it.
        sid_bindings = session_view(binding, sid)
        # Which binding key sourced each visible path (#549), against the
        # ACTING agent's own key (#609 lane F g3) -- an entry this agent
        # claimed renders the ordinary imperative-bearing reason, while one
        # claimed by another agent it merely shares a harness session with
        # gets the foreign-owner wording instead, so neither a parent nor a
        # crew ever sees the other's next step rendered as its own instruction
        # to act on. `binding_key` is the one function that composes a key
        # anywhere in this codebase, so the two sides of this comparison
        # cannot drift: a payload with no `agent_id` yields the bare `sid`,
        # which is exactly the pre-#609 comparison.
        owners = session_view_provenance(binding, sid)
        own_key = binding_key(data)
        if not sid_bindings:
            return {}  # no binding -> allow

        mid_flight = []
        for entry in sid_bindings.values():
            view = _entry_mid_flight_view(entry)
            if view is not None:
                mid_flight.append(view)

        if not mid_flight:
            return {}  # every bound entry is unreadable/closed/honest-blocked -> allow

        # Mid-flight: aggregate a single progress signal across every
        # mid-flight entry (never fragment nudges[sid] per-entry).
        seq = sum(journal_seq(spine_path) for spine_path, _, _ in mid_flight)
        active_ids = sorted(
            "{}::{}".format(spine_path, aid) for spine_path, _, aid in mid_flight
        )
        nudges = load_nudges(project_dir)
        prior = nudges.get(sid) or {"count": 0, "journal_seq": -1, "active_id": None}
        progress = (seq != prior.get("journal_seq")) or (active_ids != prior.get("active_id"))
        count = (0 if progress else prior.get("count", 0)) + 1
        nudges[sid] = {"count": count, "journal_seq": seq, "active_id": active_ids}
        save_nudges(project_dir, nudges)

        if count >= 3:
            # Escape hatch: allow the stop, but leave a loud marker.
            return {"continue": True, "systemMessage": STUCK_MSG}

        # Answer this agent with ITS OWN gate wherever it has one, and fall
        # back to the leading entry only when it has none. Order alone would
        # hand a Commander whichever entry happened to be claimed first --
        # routinely its in-tree crew's, whose gate is precisely the one it must
        # not be told to drive.
        own = _own_entries(mid_flight, owners, own_key)
        spine_path, spine, aid = (own or mid_flight)[0]
        if _is_own_entry(owners.get(spine_path), own_key):
            # This agent's own entry (or provenance couldn't place it -- fail
            # toward the pre-existing behavior): unchanged wording.
            reason = _mid_flight_reason(spine, aid)
            ctx = "ENGINE current -> " + reconstruct_current(spine)
        else:
            owner_key = owners.get(spine_path)
            # Foreign-owned: reachable only through a per-agent key that is
            # not this session's own bare id. Withhold the owning gate's next
            # imperative from BOTH rendered fields -- reason (#549's primary
            # leak) and additionalContext (reconstruct_current would leak the
            # same imperative through `ACTIVE {aid} [...] -- {imperative}`).
            reason = _owning_session_reason(spine_path, owner_key)
            ctx = "ENGINE current -> (withheld: gate belongs to {})".format(owner_key)
        return {
            "decision": "block",
            "reason": reason,
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": ctx,
            },
        }
    except Exception:
        return {}


# --- SessionStart: re-inject resume doctrine after compaction ----------------

# A5 (deficiency cleanup batch A+B): the fallback scan's own staleness
# threshold, mirroring `checklist_engine.DEFAULT_LEASE_STALE_SECONDS`
# (1800s). Duplicated deliberately, not imported: this hook is stdlib-only
# by contract and cannot import the engine (the same reason `reconstruct_
# current` above duplicates the lease-line render instead of calling it).
_LEASE_STALE_SECONDS = 1800


def _lease_is_stale(lease: dict, now_text: str | None = None) -> bool:
    """Mirrors `checklist_engine._is_stale`'s verdict -- same threshold, same
    fail-toward-stale rule for a missing/unparseable heartbeat -- without
    importing the engine. Used ONLY to gate an ADVISORY injection, never to
    refuse a claim or reap a binding, so failing toward "stale" here costs
    nothing worse than an unshown suggestion, never a lost record (contrast
    `_reap_binding_entries`, which fails the OTHER way because a delete is
    not reversible; the two rules are not in tension, they answer different
    questions)."""
    hb_dt = _parse_aware_iso(lease.get("last_heartbeat"))
    if hb_dt is None:
        return True
    now_dt = _parse_aware_iso(now_text) if now_text else datetime.now(timezone.utc)
    if now_dt is None:
        return True
    return (now_dt - hb_dt).total_seconds() > _LEASE_STALE_SECONDS


def _scan_active_spine(project_dir: Path):
    """Best-effort fallback: EVERY .agent-work/*/spine.json with an active,
    NON-STALE lease and a non-None active id, as a list of `(spine_dict,
    spine_path)` tuples in glob order (session->spine binding is preferred;
    this is the last-resort discovery path). Empty list if none found.

    A5 (deficiency cleanup batch A+B): staleness is checked HERE, not just at
    the injection site downstream, because this is the ONE fallback path with
    no proof of ownership behind it at all -- unlike the `owned` bindings
    branch above (this session's OWN claim, which stays ungated: an owner is
    never blocked by its own staleness, same rule `require_session` uses),
    this glob answers "some active-leased spine is on disk", session
    unknown, and could be anyone's, dead or alive. Before this, EVERY active
    lease in this checkout (58 of them, all stale) was an eligible match.

    Returning every match (not just the first) is deliberate: the caller
    needs a COUNT to tell an unambiguous single active spine from an
    ambiguous multi-spine scan (#261 bind-on-resume), and it needs the LIST
    itself, because the spine it injects as advisory context is the first
    match this session's view does not attribute to another binding key --
    not simply the first (#609 lane F g3 rework 4). One glob pass serves
    both."""
    try:
        base = _agent_work(project_dir)
        matches = []
        for spath in base.glob("*/spine.json"):
            spine = load_spine(str(spath))
            if not isinstance(spine, dict):
                continue
            lease = spine.get("engine_session") or {}
            if lease.get("status") != "active" or active_id(spine) is None:
                continue
            if _lease_is_stale(lease):
                continue
            matches.append((spine, str(spath)))
        return matches
    except Exception:
        return []


def decide_session_start(data: dict, project_dir: Path) -> dict:
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        # Merged per-agent view (#419), same reason as decide_stop: a resumed
        # session must still find a spine claimed under a per-agent key.
        sid_bindings = session_view(binding, sid)
        # Per-entry iteration mirroring decide_stop's already-generalized
        # pattern (#202/#261): `sid_bindings` is a dict of abs_spine_path ->
        # entry (never a flat {spine, ...} directly).
        #
        # SELECTION is a binding-key property here exactly as it is at
        # decide_stop (#609 lane F g3); only the BLOCKING decision is asymmetric
        # between the two sites, because this site has none. Membership in the
        # merged view is NOT the binding-key answer: session_view folds in every
        # `sid#<agent_id>` key, and Agent-tool subagents SHARE their parent's
        # session_id -- that sharing is the whole premise of #419 and of the
        # per-agent key -- so ANOTHER AGENT's entry is in this view by
        # construction. Taking the first entry in dict order would hand a
        # restarting Commander whichever spine happened to be claimed first,
        # routinely its crew's, together with "pick the run back up at this gate
        # and drive it through the engine". That is the #549/#419 failure class
        # itself, here, in the hook whose job is to end it.
        #
        # Nothing measured says a SessionStart payload carries an `agent_id`:
        # the pinned probe capture is PostToolUse only, and a SessionStart is a
        # per-harness-session event. With no `agent_id`, `binding_key` yields the
        # bare `sid`, which selects this session's own top-level claim and
        # ignores its crews'. Asking `binding_key` rather than assuming that
        # absence is what keeps the site honest if one ever does arrive: it
        # would then answer the agent the payload names, not a different one.
        owners = session_view_provenance(binding, sid)
        own_key = binding_key(data)
        owned = _own_entries(list(sid_bindings.items()), owners, own_key)
        spine = None
        for _spine_path, entry in owned:
            if entry.get("spine"):
                spine = load_spine(entry.get("spine"))
                break
        # Owning none of the VISIBLE entries is a DIFFERENT situation from
        # holding no binding at all, and the fallback below must not conflate
        # them. `_scan_active_spine` itself reads no binding key, but the branch
        # it sits in WRITES one, under the bare `sid` -- exactly the key this
        # site and decide_stop read as OWN. So falling through to it is not a
        # passive withholding: on one active-leased in-tree spine it manufactures
        # the very ownership that was just withheld, and the next Stop is then
        # answered with another agent's gate AS ITS OWN. That is the #549 leak
        # produced by the rule meant to end it, so the two cases are told apart
        # by the two facts already in hand here:
        #
        # - `sid_bindings` non-empty and NOTHING in it this agent's -- every
        #   visible entry was claimed by another agent under a per-agent key,
        #   and a spine this session had claimed would already be in this view.
        #   Withhold entirely: no binding, and no resume context either, because
        #   that context reconstructs the owning gate through
        #   `reconstruct_current` and ends "Pick the run back up at this gate and
        #   drive it through the engine" -- the same imperative decide_stop's
        #   foreign-owner branch refuses to render, in the same direction.
        # - `sid_bindings` EMPTY -- nothing has been claimed under this session
        #   at all, so there is no ownership to contradict. That is #261's
        #   resumed/compacted session that never itself ran `claim`, and the
        #   scan is its only route back to its own run. Untouched.
        #
        # An OWN entry whose spine no longer loads also lands here with `spine`
        # None, and this rule leaves it alone, correctly: the agent owns what it
        # can see, so there is nothing here to withhold from it.
        #
        # What that does NOT mean -- it was written here once and it was wrong,
        # which is how B5 got scoped out of rework 2 -- is that such an agent
        # contradicts no one. The scan below can hand it whatever active-leased
        # spine the tree holds, and on this lane that is routinely one a sibling
        # agent has visibly claimed. That case is answered below instead, by
        # `_attributed_to_another_key`, asked once of what the scan RENDERS and
        # once of what it WRITES -- those two acts are what every route into
        # this branch has in common, and a reader-side rule covers only the
        # route it was written for.
        if spine is None and sid_bindings and not owned:
            return {}
        if spine is None:
            matches = _scan_active_spine(project_dir)  # best-effort fallback
            # The scan is a THIRD selection site, and until this rework it was
            # the only one not held to the rule the other two obey: it took
            # `matches[0]`, which is glob order -- filesystem order, which knows
            # nothing about who claimed what (#609 lane F g3 rework 4, B6).
            #
            # So the same question the write asks below is asked here, of each
            # candidate in turn: rendering a gate this session's view attributes
            # to another binding key contradicts that attribution exactly as
            # much as filing it does, because the context this branch ends with
            # is "Pick the run back up at this gate and drive it through the
            # engine". Asking it per candidate rather than only of `matches[0]`
            # is what decouples the rule from `len(matches) == 1`: the write
            # below is gated on that count because AMBIGUITY is not ours to
            # resolve silently, and ambiguity is a different question from
            # ownership. On 2+ matches the count is the only reason nothing was
            # filed, which read like the ownership rule holding when it was not
            # being asked at all -- and the render went out regardless.
            #
            # Asked with `own_key`, the READER's key, the same one `_own_entries`
            # is asked with above -- this is a render, and a render is a read.
            # The write below passes the bare `sid` instead because that is the
            # key it would file under. On every SessionStart payload measured so
            # far the two are the same string (no `agent_id` arrives, so
            # `binding_key` yields the bare `sid`), and they are still named
            # separately here rather than shared, because if one ever does
            # arrive the acting agent is who this selection is for.
            #
            # A path attributed to NOBODY is unchanged by this: it contradicts
            # no one, so it renders exactly as it did before, and the open
            # authority question about binding a session to a spine no one
            # claimed is not touched here either.
            for _cand_spine, _cand_path in matches:
                if _attributed_to_another_key(owners, _cand_path, own_key):
                    continue
                spine = _cand_spine
                break
            if len(matches) == 1 and sid:
                # Unambiguous (decision:no-bind-on-ambiguous-scan): exactly
                # one active-leased spine on disk and no positional-count
                # confusion about which one it is -- bind this session to it,
                # same shape g1's claim writer uses, so a resumed/compacted
                # session that never itself ran `claim` still gets a binding
                # (#261) and gauge_writer_hook.resolve_gauge_path stops
                # returning empty for it. Zero or 2+ matches: write NO binding
                # -- ambiguity is not ours to silently resolve -- while the
                # context injection below still hands out whatever the selection
                # above kept, which on 2+ matches is the only thing that answers
                # such a session at all.
                own_spine, own_spine_path = matches[0]
                # The WRITE's own guard, asked again here rather than read off
                # the selection above, because this write is reached by more than
                # one reader path. `spine` is left None both when the agent owns
                # nothing visible AND when it owns an entry whose spine no longer
                # loads -- archived, deleted, moved, or carrying no usable
                # `spine` field -- and on that second route there is nothing
                # above to withhold, so a reader-side rule never sees it (#609
                # lane F g3 rework 3, B5). Guarding each reader path in turn had
                # missed a door twice.
                #
                # It is asked of `sid` here and of `own_key` above because the
                # two acts take the path in different ways: this one FILES it,
                # under the bare `sid`, so that is the key an existing
                # attribution would have to contradict. On every SessionStart
                # payload measured the two keys are the same string.
                #
                # The rule is narrow on purpose: the scan may still bind a path
                # nobody has claimed, but it may not CONTRADICT an attribution
                # already VISIBLE TO THIS SESSION. Filing another agent's spine
                # under this session's bare `sid` does exactly that, and it does
                # it in both directions at once -- provenance is last-key-wins,
                # so the write hands this session the other agent's gate as its
                # own AND takes that gate away from the agent that claimed it.
                #
                # "Visible to this session" is the literal reach, not a hedge:
                # `owners` is `session_view_provenance(binding, sid)`, so the
                # attributions compared are those filed under the bare `sid` and
                # under this session's own `sid#agent_id` keys. A spine claimed
                # by a DIFFERENT harness session_id is not in that mapping, and
                # this write proceeds against such a claim (rework 4, B7).
                # Widening the comparison across the session boundary is an open
                # authority question and is deliberately not answered here.
                if _attributed_to_another_key(owners, own_spine_path, sid):
                    return {}
                lease_for_bind = own_spine.get("engine_session") or {}
                worktree = _worktree_from_spine(own_spine_path)
                if not worktree:
                    return {}

                # Bare `sid`, NOT binding_key(data) (#419): SessionStart never
                # carries an agent_id, so a resumed session is by definition
                # top-level. Only the READ above changed. Routed through the
                # transaction (#441) so a concurrent claim/release for this
                # same sid cannot be silently overwritten by this merge.
                def _resume_mutate(reaped, _sid=sid, _own_spine_path=own_spine_path,
                                    _engine_session=lease_for_bind.get("session_id"),
                                    _worktree=worktree):
                    new_map = dict(reaped)
                    sid_bindings2 = dict(new_map.get(_sid) or {})
                    sid_bindings2[_own_spine_path] = {
                        "spine": _own_spine_path,
                        "engine_session": _engine_session,
                        "worktree": _worktree,
                        "claimed_at": _now_iso(),
                    }
                    new_map[_sid] = sid_bindings2
                    return new_map

                _binding_transaction(project_dir, _resume_mutate)
        if spine is None:
            return {}
        lease = spine.get("engine_session") or {}
        if lease.get("status") != "active":
            return {}
        if active_id(spine) is None:
            return {}
        resume_ctx = (
            "RESUMING an active Constellation spine run after a restart or "
            "compaction. ENGINE current -> " + reconstruct_current(spine) + " "
            "Pick the run back up at this gate and drive it through the engine. "
            "Remember release-is-last: the run is not done until you release the "
            "engine lease."
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": resume_ctx,
            },
        }
    except Exception:
        return {}


# --- dispatch ----------------------------------------------------------------

def main(argv, stdin_text) -> int:
    """Dispatch by event name (argv[1]); print result JSON only if non-empty;
    always exit 0. Wrapped: any exception -> print nothing, exit 0 (fail-open)."""
    try:
        event = argv[1] if len(argv) > 1 else ""
        try:
            data = json.loads(stdin_text) if stdin_text and stdin_text.strip() else {}
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        project_dir = resolve_project_dir()
        if event == "Stop":
            result = decide_stop(data, project_dir)
        elif event == "SessionStart":
            result = decide_session_start(data, project_dir)
        elif event == "PostToolUse":
            result = handle_post_tool_use(data, project_dir)
        else:
            result = {}
        if result:
            print(json.dumps(result))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        _stdin = sys.stdin.read()
    except Exception:
        _stdin = ""
    sys.exit(main(sys.argv, _stdin))
