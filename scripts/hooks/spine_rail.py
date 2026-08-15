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
  engine's claim/release verbs and maintains a session->spine binding. It is NOT
  a second source of mid-flight truth -- Stop always reads the spine file the
  binding points at.
- Three registrations only (Stop, SessionStart, PostToolUse). No PreCompact.
- 3-strike escape hatch so a genuinely stuck agent is never trapped.

Stdlib only (json, os, re, shlex, subprocess, sys, pathlib). Windows-friendly:
UTF-8 writes, native paths, no /tmp literals. The ONE subprocess is a bounded
`git worktree list` probe used to resolve a relative --file (#440); it is never
the engine (see the `git_worktree_roots` docstring).
"""

import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# The engine's terminal statuses, re-encoded here on purpose (see docstring).
TERMINAL = {"complete", "skipped"}

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


# --- per-agent binding identity (#419) ---------------------------------------

BINDING_KEY_SEP = "#"

# Tokens that make an `agent_id` unusable as part of a key. `agent_id` is a
# harness field this repo does not own, and the gauge writer interpolates it
# into a filesystem path (`agent-{agent_id}.jsonl`), so a path separator, a
# parent-traversal token, or our own key separator must never reach it.
_AGENT_ID_REJECT = (BINDING_KEY_SEP, "/", "\\", "..")


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
        if not agent_id or not isinstance(agent_id, str):
            return None
        if any(tok in agent_id for tok in _AGENT_ID_REJECT):
            return None
        return "{sid}{sep}{aid}".format(sid=sid, sep=BINDING_KEY_SEP, aid=agent_id)
    except Exception:
        return None


def session_view(binding: dict, sid) -> dict:
    """The merged `{abs_spine_path: entry}` a harness session can see: the bare
    `sid` key plus every per-agent key `sid + BINDING_KEY_SEP + <agent_id>`.

    Readers (decide_stop, decide_session_start) must keep seeing every spine
    they saw before the per-agent split, so they read through this view rather
    than `binding[sid]`. The prefix test uses the separator on purpose -- a key
    that merely starts with the sid (`<sid>-something`) is a different session,
    not a child of this one. Never raises; returns {} on anything unusable.
    """
    merged = {}
    try:
        if not sid:
            return {}
        prefix = "{sid}{sep}".format(sid=sid, sep=BINDING_KEY_SEP)
        for key, entries in (binding or {}).items():
            if not isinstance(entries, dict):
                continue
            if key == sid or (isinstance(key, str) and key.startswith(prefix)):
                merged.update(entries)
        return merged
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


# --- worktree attribution (subagent session-sharing guard) -------------------

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


def _foreign_worktree(data: dict, b: dict) -> bool:
    """True only when the stopping session's cwd is positively a DIFFERENT
    worktree than the binding's recorded worktree.

    Returns True iff both `data["cwd"]` and `b["worktree"]` are truthy AND
    `_same_path` says they differ. Absent either -> False: no positive mismatch
    evidence, so the rail does not relax (and `_same_path`'s fail-safe True keeps
    an errored comparison from reading as foreign).
    """
    try:
        cwd = data.get("cwd")
        worktree = b.get("worktree")
        if not cwd or not worktree:
            return False
        return not _same_path(cwd, worktree)
    except Exception:
        return False


def _worktree_from_spine(abs_spine):
    """The owning worktree for one absolute `.agent-work/<id>/<name>.json`.

    This is deliberately lexical: an absolute claim path remains useful even
    after its checklist is archived, while payload cwd is a launch-time value
    that can belong to a different linked worktree. Anything outside the exact
    checklist layout is unowned rather than falling back to cwd.
    """
    try:
        if not isinstance(abs_spine, str):
            return None
        spine = Path(abs_spine)
        if not spine.is_absolute() or not spine.name.endswith(".json"):
            return None
        work_id = spine.parent
        agent_work = work_id.parent
        if spine.name == ".json" or not work_id.name or agent_work.name != ".agent-work":
            return None
        return str(agent_work.parent)
    except Exception:
        return None


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

    PostToolUse NEVER blocks -- always returns {}.
    """
    try:
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
        binding = load_binding(project_dir)
        abs_spine = None
        path_source = None
        if verb == "release":
            # Recorded binding FIRST (#440) -- see resolve_recorded_release_target.
            abs_spine = resolve_recorded_release_target(file_val, binding.get(key))
        if not abs_spine:
            abs_spine, path_source = resolve_spine_candidate(
                file_val, data, project_dir, tokens, command
            )
        if verb == "claim":
            if not abs_spine:
                # No candidate root yields a real checklist -- BIND NOTHING
                # (#440). A missing binding is recoverable; a confident wrong one
                # silently misattributes one agent's context reading to another
                # agent's work area.
                return {}
            engine_session = _extract_opt(tokens, "--session-id")
            worktree = _worktree_from_spine(abs_spine)
            if not worktree:
                return {}
            key_bindings = dict(binding.get(key) or {})
            key_bindings[abs_spine] = {
                "spine": abs_spine,
                "engine_session": engine_session,
                "worktree": worktree,
                "claimed_at": _now_iso(),
                # Provenance (#440): WHICH rung resolved the path. Additive
                # VALUE field only -- the binding KEY shape (#419) is untouched.
                "path_source": path_source,
            }
            binding[key] = key_bindings
            save_binding(project_dir, binding)
        else:  # release
            # KNOWN, NOT CHASED (#419, filed as a triage candidate): a
            # successful release is the ONLY path that removes a key. An agent
            # that dies, is cancelled, or is killed mid-run leaves its key
            # behind forever, and per-agent keying multiplies the key count by
            # every wave's fan-out. Nothing reaps them -- #419's one-time
            # sweeper was deleted after its single run, as that issue required.
            key_bindings = binding.get(key)
            if abs_spine and key_bindings and abs_spine in key_bindings:
                key_bindings = dict(key_bindings)
                del key_bindings[abs_spine]
                if key_bindings:
                    binding[key] = key_bindings
                else:
                    # Delete THIS key's now-empty entry set -- `key`, never
                    # `sid`. Under a composite key those are different keys,
                    # and deleting the bare one here would wipe a live
                    # parent's entire binding.
                    del binding[key]
                save_binding(project_dir, binding)
            # The nudge / three-strike escape-hatch ledger is documented and
            # written (decide_stop) under the BARE session_id, and it stays
            # that way: splitting strikes per-agent would fragment the count
            # and weaken the hatch. So this delete keeps `sid` while the
            # binding writes above use `key` -- that asymmetry is intended,
            # not a missed substitution (#419).
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
        "run. Keep working the gate -- do not end your turn to wait. "
        "Next imperative: {imp} "
        "If this is an honest stop (genuinely blocked or out of scope), use the "
        "engine's block verb to bubble the blocker to the parent, or waive the "
        "check with human authority -- do not just stop."
    ).format(aid=aid, imp=imperative)


def _entry_mid_flight_view(data: dict, entry: dict):
    """Per-entry mid-flight check, unchanged in substance from the pre-#202
    single-entry logic -- just factored so decide_stop can apply it to every
    bound abs_spine_path entry for a session_id, not just one.

    Returns None if this entry is NOT a genuine mid-flight blocker (foreign
    worktree, unreadable spine, released/inactive lease, or an honest engine
    block); else `(spine_path, spine_dict, aid)`.
    """
    spine_path = entry.get("spine")
    if not spine_path:
        return None
    if _foreign_worktree(data, entry):
        return None  # stopping session is not THIS entry's driver (subagent
        # sharing the parent's session_id claimed a spine in its own worktree)
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
    """Block the Stop if ANY non-foreign bound entry for this session_id is
    genuinely mid-flight (same per-entry semantics as the pre-#202 single-
    entry version, just applied across every abs_spine_path entry now bound
    under `sid`). The nudge-tracking / 3-strike escape hatch stays keyed by
    `sid` ALONE -- never fragmented per-entry, which would weaken the escape
    hatch.
    """
    try:
        sid = data.get("session_id")
        binding = load_binding(project_dir)
        # Read through the merged per-agent view (#419): a spine claimed by a
        # subagent now lives under `sid#agent_id`, and the stopping session
        # must still see it.
        sid_bindings = session_view(binding, sid)
        if not sid_bindings:
            return {}  # no binding -> allow

        mid_flight = []
        for entry in sid_bindings.values():
            view = _entry_mid_flight_view(data, entry)
            if view is not None:
                mid_flight.append(view)

        if not mid_flight:
            return {}  # every bound entry is foreign/unreadable/closed/honest-blocked -> allow

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

        _, spine, aid = mid_flight[0]
        reason = _mid_flight_reason(spine, aid)
        ctx = "ENGINE current -> " + reconstruct_current(spine)
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

def _scan_active_spine(project_dir: Path):
    """Best-effort fallback: EVERY .agent-work/*/spine.json with an active
    lease and a non-None active id, as a list of `(spine_dict, spine_path)`
    tuples in glob order (session->spine binding is preferred; this is the
    last-resort discovery path). Empty list if none found.

    Returning every match (not just the first) is deliberate: the caller
    needs a COUNT to tell an unambiguous single active spine from an
    ambiguous multi-spine scan (#261 bind-on-resume), while still wanting
    the same "first match" spine for the advisory-context injection it did
    before this match ever mattered. One glob pass serves both."""
    try:
        base = _agent_work(project_dir)
        matches = []
        for spath in base.glob("*/spine.json"):
            spine = load_spine(str(spath))
            if not isinstance(spine, dict):
                continue
            lease = spine.get("engine_session") or {}
            if lease.get("status") == "active" and active_id(spine) is not None:
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
        # entry (never a flat {spine, ...} directly). Take the FIRST entry
        # (natural dict.values() order) that has a spine and is not foreign
        # -- same "first match" tone as _scan_active_spine below.
        spine = None
        for entry in sid_bindings.values():
            if entry.get("spine") and not _foreign_worktree(data, entry):
                spine = load_spine(entry.get("spine"))
                break
        if spine is None:
            matches = _scan_active_spine(project_dir)  # best-effort fallback
            if matches:
                spine = matches[0][0]  # first match, same tone as before
            if len(matches) == 1 and sid:
                # Unambiguous (decision:no-bind-on-ambiguous-scan): exactly
                # one active-leased spine on disk and no positional-count
                # confusion about which one it is -- bind this session to it,
                # same shape g1's claim writer uses, so a resumed/compacted
                # session that never itself ran `claim` still gets a binding
                # (#261) and gauge_writer_hook.resolve_gauge_path stops
                # returning empty for it. Zero or 2+ matches: inject context
                # (below) but write NO binding -- ambiguity is not ours to
                # silently resolve.
                own_spine, own_spine_path = matches[0]
                lease_for_bind = own_spine.get("engine_session") or {}
                worktree = _worktree_from_spine(own_spine_path)
                if not worktree:
                    return {}
                # Bare `sid`, NOT binding_key(data) (#419): SessionStart never
                # carries an agent_id, so a resumed session is by definition
                # top-level. Only the READ above changed.
                sid_bindings2 = dict(binding.get(sid) or {})
                sid_bindings2[own_spine_path] = {
                    "spine": own_spine_path,
                    "engine_session": lease_for_bind.get("session_id"),
                    "worktree": worktree,
                    "claimed_at": _now_iso(),
                }
                binding[sid] = sid_bindings2
                save_binding(project_dir, binding)
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
