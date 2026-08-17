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
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PureWindowsPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    # The context-manifest assembly seam (#305). Imported here so `start`/`reopen`
    # can emit. The sidecar and its closure now DO ship with every engine-carrying
    # skill, declared in install_constellation.SCRIPT_RUNTIME_COMPANIONS — an
    # earlier version of this comment said the opposite and treated the fallback
    # as the normal installed case, which is precisely how the seam stayed inert
    # everywhere it was installed (#362). The fallback is kept for a genuinely
    # partial tree only, following the same "absence is normal, never raise" rule
    # the manifest producer itself follows. It is NOT the expected path, and
    # tests/test_install_constellation.py asserts an installed engine binds the
    # real function rather than this one.
    from episode_capture import emit_step_manifest  # noqa: E402
except ImportError:  # pragma: no cover — only reachable from a partial install
    def emit_step_manifest(*_args, **_kwargs):  # type: ignore[misc]
        return None


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
# The full task-status vocabulary (#227 gate g3): the single source of truth
# an (status, verb) recovery grid is GENERATED from, rather than hand-typed
# per test. TERMINAL below is the subset that ends a task's lifecycle.
STATUS_VALUES = ("pending", "in-progress", "blocked", "complete", "skipped")
TERMINAL = {"complete", "skipped"}
DEFAULT_REWORK_CAP = 3
DEFAULT_LEASE_STALE_SECONDS = 1800

# Verbs that mutate canonical state and therefore require the active session
# (once a lease exists). `current` is read-only; `claim`/`heartbeat`/`release`
# manage the lease itself and are handled separately.
MUTATING_VERBS = {
    "start", "advance", "record", "consolidate", "skip", "block",
    "resume", "reopen", "append", "attest", "waive", "attach", "flag-candidate",
    "amend",
}


# Verbs that BEGIN work at a gate, and are therefore the ones the Trip HARD band
# refuses over the line (#467). `start` opens a pending gate; `reopen` drives a
# complete gate back to in-progress and cascades downstream — both commit an agent
# to work it may not be able to finish. `advance` is deliberately ABSENT: closing
# the gate you are already inside IS the handoff and is never governor-refused. So
# is `resume`, which only restores a blocked gate to the status it already held.
TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}


# Stamp-and-compare is RETIRED (#609 g2). `origin.worktree` used to be compared,
# on every mutating verb, against a worktree toplevel the engine resolved from
# its own ambient cwd; `origin_worktree_refusal` and the two verb sets that fed
# it are gone, along with the per-verb `git rev-parse` that supplied the other
# side. THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived. There is no
# second value that can disagree with the first, and no ambient reading a check
# command could forge by `cd`-ing first, because the engine no longer asks the
# question anywhere.
#
# The lexical rule that derives a worktree from a spine's path is NOT retired --
# only the engine's copy of it is. The rule lives in the stdlib-only hook, as
# `spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
# case table is its specification. The engine-side copy was deleted in #609 g2
# under `ADMIRAL_RULING-2` N2: it had TWO consumers -- the shape question inside
# `origin_worktree_refusal`, deleted by that same gate, and #315's `cwd` thread,
# re-homed to #610 by `ADMIRAL_RULING-1` R3 -- and a third that
# `ADMIRAL_RULING-1` R2 withdrew before it ever existed. Three sound decisions
# in a row, and a definition nothing calls is not shipped. It re-lands in
# #610's wave together with #315 -- the consumer that threads `cwd` into the
# engine's check runner -- and re-derives against that same table.
#
# Nothing was left unguarded by that removal WHEREVER A LEASE EXISTS -- and the
# leaseless path was WIDENED. The comparison answered "where am I", never "is
# this mine": ownership is the LEASE, but only where one is actually held.
# `require_session` gates mutating verbs only once an active lease exists and
# returns early otherwise, and `_active_lease` reads a RELEASED lease as absent.
# So on a spine with NO ACTIVE LEASE -- never claimed, or claimed and since
# released -- this comparison was the sole refusal, and the engine now asserts
# nothing about location. Measured from a foreign worktree: `start` and `attach`
# on a never-claimed spine, and `start` after a release, went from refused to
# accepted, WRITING STATE INTO A TREE THE AGENT IS NOT STANDING IN. Under an
# active lease held by another session, nothing changed.
#
# That widening is ACCEPTED and deliberate, not a no-op. A `cd <worktree> &&`
# prefix defeated the comparison, so it was never a boundary -- but a forgeable
# guard is not the same as no guard. This supersedes the 2026-08-15
# worktree-identity ruling, which settled how the two sides of the comparison
# should be resolved -- a question that no longer exists.
#
# `origin.worktree` is still WRITTEN, by `spine_lifecycle.build_origin` and
# `init_work_area.instantiate_spine`. It is provenance -- what a human or a
# reconciler reads to see where a spine came from -- and nothing reads it to
# decide anything. `tests/test_spine_origin_isolation.py` pins both halves of
# that pairing and goes red if either one breaks.


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
    """A refusal: the requested transition is not allowed. No exit-0.

    Optional structured attributes (#227 gate g3) let the CLI boundary
    (`main()`, via `recovery_for()`) compose a recovery line WITHOUT
    re-parsing the message string -- the verb functions that raise stay pure
    (their message text is unchanged); they just also hand the boundary the
    facts it needs:
      - `task_id` / `verb`: which task, and which attempted verb, refused.
      - `status`: the task's ACTUAL status at refusal time (a status-caused
        refusal -- start/advance/resume/reopen each require one).
      - `unmet`: the REAL unmet condition ids from a live check inside the
        verb (`start`'s preconditions, `advance`'s postconditions), each as
        {"id", "which", "kind"}. A command/git-change-policy kind's pass/fail
        is only known HERE, at the moment the check ran -- `state()` must
        never re-derive it (INV-2 purity), so this is genuinely a fact only
        the exception carries.
      - `valid_ids`: every real p*/c* id on the task, for an unknown-cond-id
        refusal on `attest` (a malformed-argument refusal, a 4th axis
        outside the (status, verb) grid -- see `recovery_for`).
    None of these are read anywhere except `recovery_for` at the CLI
    boundary; a caller that never inspects them (most of the existing test
    suite, which raises/asserts EngineError by message text) is unaffected."""

    def __init__(self, message, *, task_id=None, verb=None, status=None,
                 unmet=None, valid_ids=None):
        super().__init__(message)
        self.task_id = task_id
        self.verb = verb
        self.status = status
        self.unmet = unmet
        self.valid_ids = valid_ids


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


def _dominant_newline(path: Path) -> bytes:
    """The line ending `path` already uses: CRLF only when its endings are
    unambiguously CRLF, LF in every other case (missing file, empty file, LF file,
    MIXED file). Mixed is deliberately not guessed at — see `save`."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        return b"\n"
    crlf = raw.count(b"\r\n")
    bare_lf = raw.count(b"\n") - crlf
    return b"\r\n" if crlf and not bare_lf else b"\n"


def _restore_mode(fd: int, tmp_name: str, mode: int) -> None:
    """Give the temp file the target's existing permissions, on every platform.

    `mkstemp` creates 0600, so a bare rename would silently NARROW a spine's
    permissions — a behaviour change nobody asked for, on the file the whole fleet
    reads.

    **`os.fchmod` is Unix-only, and this repo's CI is `windows-latest`.** Calling it
    unguarded raised `AttributeError` on Windows for every save of an existing file —
    and since every mutating engine verb ends in `save()`, that is not a failing test,
    it is a dead engine on that platform. Caught during closeout rather than in CI
    (issue #567 lane A).

    So: prefer `fchmod` on the FD where it exists, because the temp is already open
    and an FD cannot be swapped underneath us; fall back to `chmod` on the path, which
    Windows does implement (honouring only the read-only bit, which is the correct
    best effort there — Windows has no POSIX mode bits to restore). A failure to
    restore permissions is deliberately NOT fatal: the document is what matters, and
    refusing to save because a mode could not be copied would trade a real write for
    a cosmetic one."""
    try:
        os.fchmod(fd, mode)  # POSIX
        return
    except (AttributeError, OSError, NotImplementedError):
        pass
    try:
        os.chmod(tmp_name, mode)  # Windows, and any POSIX oddity above
    except (OSError, NotImplementedError):
        pass


def save(path: Path, data: dict) -> None:
    """Write the checklist as JSON ATOMICALLY, PRESERVING the line ending the file
    already uses, and write BYTES so nothing translates them again.

    Text mode (`newline=None`, what this used to do) rewrites every ending to the
    platform's — CRLF on Windows, LF on POSIX. One engine verb would then rewrite a
    whole file's endings and destroy its blame, on a file the engine only meant to
    add one field to.

    **A file that does not exist yet, or one with MIXED endings, gets LF.** Mixed is
    not a preference the engine can read, so it normalises rather than guesses.

    **The new document is installed by rename, never written over the live file
    (#613).** This used to end in `Path(path).write_bytes(payload)`, which opens the
    target with O_TRUNC and only then writes: a reader running concurrently could
    observe a truncated spine and raise `JSONDecodeError` on state that is perfectly
    valid on disk (`tests/test_crew_launcher.py` had to tolerate exactly that in its
    parent-heartbeat poll), and a crash mid-write left the spine permanently corrupt
    — on the only record that the work happened. So: write a UNIQUE temp sibling
    (unique, because two concurrent writers sharing one fixed temp name can install a
    durably unparseable document — worse than the tear this fixes), `fsync` it so the
    rename cannot become durable before the data is, then `os.replace` it into place.
    A reader now sees the complete old document or the complete new one.

    **Atomicity here is not mutual exclusion.** The WRITE is atomic; the
    read-modify-write is not. Two callers that each `load()` → mutate → `save()` still
    clobber each other, and the loser's update goes missing from a file that is
    perfectly well-formed — so nothing raises and nothing notices. Guarding that is a
    separate job (locking or compare-and-swap) and is deliberately not done here; see
    `scripts/hooks/spine_rail.py`'s binding-store transaction for the same
    distinction drawn in the same words.
    """
    path = Path(path)
    payload = (json.dumps(data, indent=2) + "\n").encode("utf-8")
    # Read the EXISTING file's endings and mode BEFORE anything replaces it.
    eol = _dominant_newline(path)
    if eol != b"\n":
        # json.dumps escapes any literal CR as \r, so no b"\r" survives in the
        # serialised bytes and this replace cannot produce b"\r\r\n".
        payload = payload.replace(b"\n", eol)
    try:
        mode = path.stat().st_mode & 0o7777
    except OSError:
        mode = None  # new file: keep whatever mkstemp's 0600 gives it
    # Same directory as the target -- `os.replace` is only atomic within one
    # filesystem.
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp",
                                    dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            if mode is not None:
                _restore_mode(f.fileno(), tmp_name, mode)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:  # a failure anywhere above leaves no .tmp behind
            try:
                os.unlink(tmp_name)
            except OSError:
                pass


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


_RAIL_CURRENT_MIDFLIGHT_POINTER = "the ACTIVE line above"


def _rail(point: str, cl: dict) -> str:
    """Return the doctrine block to append at a decision point, or ``""`` when no
    rail applies. Non-gated (survey) checklists get NO rail. ``point`` is either
    ``"check-failure"`` (the REFUSED path, no token substitution) or any railed verb
    name, in which case the position is derived from ``items`` state.

    Issue #420: on the `current` verb specifically, `render_human()`'s own
    ``ACTIVE {id} [{status}] — {imperative}`` line already prints the active
    gate's full imperative, so substituting it AGAIN into the mid-flight rail's
    ``{imperative}`` token duplicated it. For every OTHER railed verb
    (claim/start/advance/attest/attach) there is no ACTIVE line in that verb's
    own output — the rail's imperative mention is the ONLY place the caller
    sees "what's next" there, so it must keep the full text unchanged. The fix
    is verb-aware and touches only what fills the token, never the frozen
    `_RAIL_STRINGS` values themselves: substitute a short pointer for
    `{imperative}` only when `point == "current"` and the position is
    `mid-flight` (the only position that uses the `{imperative}` token)."""
    if cl.get("type") != GATED:
        return ""
    if point == "check-failure":
        text = _RAIL_STRINGS["check-failure"]
    else:
        pos, tokens = _rail_position(cl)
        if pos == "mid-flight" and point == "current":
            tokens = dict(tokens, imperative=_RAIL_CURRENT_MIDFLIGHT_POINTER)
        text = _RAIL_STRINGS[pos]
        for key, value in tokens.items():
            text = text.replace("{" + key + "}", str(value))
    return f"\n\nRAIL: {text}"


def _rail_prefix(point: str, cl: dict) -> str:
    """The doctrine rail as a FRONT-loaded prefix (#227 gate g3, items 2/4):
    ``"RAIL: <text>\\n\\n"`` when a rail applies, else ``""``. `_rail()`'s own
    unit contract is UNCHANGED (still a ``"\\n\\n" + "RAIL: " + text`` suffix
    shape -- pinned by `test_rail_marker_and_leading_newlines`); this only
    repositions the SAME text at the two CLI-boundary call sites
    (`dispatch()`'s success path, `main()`'s REFUSED path) so the banner
    lands FIRST and the operative result/refusal line lands LAST on the
    stream -- the field defect this fixes: `tail -1` used to show only the
    banner, silently hiding a real REFUSED line."""
    rail = _rail(point, cl)
    return f"{rail.lstrip(chr(10))}\n\n" if rail else ""


# --------------------------------------------------------------------------- #
# recovery (#227 gate g3, item a) — every STATE-CAUSED `REFUSED` names its
# exact exit verb. Composed ONLY at the CLI boundary (`main()`), never inside
# a verb function: the same design law as the rail above (~:160-171) — verb
# functions stay pure, so `recovery_for` reads ONLY the structured facts an
# `EngineError` carries (see the class docstring) plus the task's condition
# definitions in `cl` (kind/statement/id — never the message text itself).
#
# Reuses `_next_verbs()` (the SAME tested "legal move from here" mapping
# `current` already shows, incl. its `NextVerbsAreLegalFromHere` proof that
# every hint it prints actually runs) for the two non-terminal statuses
# (`pending`/`in-progress`) rather than re-deriving that logic — one source of
# truth for "what command is actually legal right now."  `blocked`/`complete`/
# `skipped` are handled directly: `blocked` must NOT blindly suggest `resume`
# when the gate has no restorable prior status (constraint 6 — that would
# print the exact command that just refused), and `skipped` genuinely has no
# recovery verb (an honest "no verb reverses a skip" beats a fabricated one).
# --------------------------------------------------------------------------- #
_RECOVERY_TAIL = "Do not edit the JSON — use the engine."


def recovery_for(exc: "EngineError", cl: dict) -> str:
    """A recovery line naming a runnable exit command for a state-caused
    `EngineError`, or ``""`` when the refusal carries no `task_id` (not every
    refusal is state-caused — a missing/malformed argument, an unowned lease,
    etc. are left as their existing bare message)."""
    tid = exc.task_id
    if tid is None or tid not in cl.get("tasks", {}):
        return ""
    t = cl["tasks"][tid]

    # Axis 4 (outside the (status, verb) grid): unknown --cond id on attest.
    if exc.valid_ids is not None:
        ids = ", ".join(exc.valid_ids) if exc.valid_ids else "(this task defines no conditions)"
        return (f"Recovery: {tid} defines these condition ids: {ids} -- re-run attest "
                f"with a real --cond from that list. {_RECOVERY_TAIL}")

    # amend's drop/rescope/retext-check sub-ops guard on task status exactly
    # like start/advance/resume/reopen (Reviewer BLOCK, g3-review rework 1:
    # these previously raised bare messages with no recovery at all). They get
    # DEDICATED branches, not the generic complete/skipped/blocked/pending
    # branches below: those are tuned for "how do I finish this gate," but
    # drop/rescope need the gate back at 'pending' specifically (no verb ever
    # resets a gate to 'pending' except `resume` restoring a blocked gate whose
    # recorded prior_status was 'pending' -- verified live, not assumed), and
    # retext-check needs 'pending' OR 'in-progress' (so `reopen` on a complete
    # gate -- which lands 'in-progress' -- genuinely unblocks it too).
    if exc.verb in ("amend-drop", "amend-rescope", "amend-retext-check"):
        status = exc.status if exc.status is not None else t.get("status")
        op_label = {"amend-drop": "drop", "amend-rescope": "rescope",
                    "amend-retext-check": "retext-check"}[exc.verb]
        wants_in_progress_too = exc.verb == "amend-retext-check"
        if wants_in_progress_too and status == "complete":
            return (f'Recovery: reopen {tid} --reason "<why>", then retry the same amend '
                    f"delta (retext-check accepts a pending or in-progress gate). {_RECOVERY_TAIL}")
        if status == "blocked":
            detail = t.get("status_detail") or {}
            prior = detail.get("prior_status")
            wants = ("pending", "in-progress") if wants_in_progress_too else ("pending",)
            if prior in wants:
                return (f'Recovery: resume {tid} --reason "<why the blocker cleared>", then '
                        f"retry the same amend delta ({op_label} only applies to "
                        f"{'a pending or in-progress' if wants_in_progress_too else 'a pending'} "
                        f"gate). {_RECOVERY_TAIL}")
        needed = "a pending or in-progress" if wants_in_progress_too else "a pending"
        return (f"Recovery: amend's {op_label} only applies to {needed} gate; {tid} is "
                f"{status!r} and no verb reaches {needed} status from here -- escalate to a "
                f"human if the plan genuinely needs to change. {_RECOVERY_TAIL}")

    # Real unmet conditions found by a LIVE check inside start()/advance():
    # command/git-change-policy kinds are only knowable HERE (INV-2 forbids
    # `state()` from re-deriving them).
    if exc.unmet:
        lines = []
        for cond in exc.unmet:
            cid, which, kind = cond["id"], cond["which"], cond["kind"]
            if kind in ("null", "artifact"):
                hint = f'attest {tid} --cond {cid} --which {which} --note "<verification>"'
                if kind == "artifact":
                    hint += " --evidence <evidence-id>"
            else:
                singular = which[:-1]  # preconditions -> precondition
                hint = (f"fix the underlying issue so {singular} {cid} passes, "
                        f"then retry {exc.verb} {tid}")
            lines.append(hint)
        return "Recovery: " + " | ".join(lines) + f". {_RECOVERY_TAIL}"

    # Status-caused: `exc.verb` required a different status than the task is
    # actually in.
    status = exc.status if exc.status is not None else t.get("status")
    if status == "complete":
        return f'Recovery: reopen {tid} --reason "<why>". {_RECOVERY_TAIL}'
    if status == "skipped":
        return (f"Recovery: {tid} is 'skipped' (terminal) -- no verb reverses a skip; "
                f"this needs a human decision (`amend` a new gate, or accept it stays "
                f"skipped). {_RECOVERY_TAIL}")
    if status == "blocked":
        detail = t.get("status_detail") or {}
        prior = detail.get("prior_status")
        if prior in ("pending", "in-progress"):
            return (f'Recovery: resume {tid} --reason "<why the blocker cleared>" '
                    f'(there is no separate "unblock" verb -- resume is it). {_RECOVERY_TAIL}')
        # Reviewer BLOCK (g3-review, rework 1): the previous text also offered
        # `reopen` as an alternative here -- reopen() requires status=="complete"
        # and this branch is ONLY reached when status=="blocked", so it always
        # refused when run (reproduced live). Only `skip` genuinely works from
        # a non-restorable blocked gate; do not name an exit without running it.
        return (f"Recovery: {tid} is blocked with no restorable prior status (rework-cap "
                f'escalated, or blocked before `resume` existed) -- `resume`/`reopen` would '
                f"also refuse here (reopen needs a complete gate, not blocked); use "
                f'`skip {tid} --reason "<why>"`, or escalate to a human. {_RECOVERY_TAIL}')
    if status == "pending" and cl.get("type", GATED) == GATED:
        # Position-awareness (Reviewer BLOCK, g3-review rework 2): before this
        # gate, `_next_verbs` had exactly one caller (`state()`), always
        # invoked on the checklist's own active gate. `recovery_for` is the
        # first caller to invoke it on an ARBITRARY refusing task, which need
        # not be active. `start()` -- and ONLY `start()` -- additionally
        # refuses a non-active gate on a GATED checklist, so `_next_verbs`'s
        # bare "start {tid}" suggestion can itself refuse when `tid` isn't
        # active (reproduced live: a 2-gate fixture, g2 pending/non-active,
        # `advance g2` refused with a `start g2` recovery that ALSO refused).
        # `advance`/`resume`/`reopen` carry NO active-gate check, so the
        # `in-progress` sub-case below has no equivalent hole.
        active = active_id(cl)
        if active is not None and active != tid:
            # Do NOT try to guess the active gate's own correct command here:
            # that would re-run `_next_verbs`'s status dispatch a second,
            # riskier time -- the active gate could itself be pending,
            # in-progress, or blocked, and blindly suggesting "start
            # {active}" would refuse whenever it is not literally pending
            # (the exact same anti-pattern this fix exists to close, one
            # level removed). `current` is read-only, NEVER refuses, and is
            # the single already-correct source for "what do I do right
            # now" -- point at it instead of re-deriving.
            return (f"Recovery: {tid} is not the active gate; the checklist works "
                    f"gates in order and {active!r} must be worked first -- run "
                    f"`current` to see {active}'s legal next move (do not act on "
                    f"{tid} yet). {_RECOVERY_TAIL}")
    if status in ("pending", "in-progress"):
        hints = _next_verbs(tid, t, cl.get("type", GATED))
        if hints:
            return "Recovery: " + " | ".join(hints) + f". {_RECOVERY_TAIL}"
    return ""


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


def repo_revision(base_dir: Path | None = None) -> dict:
    """The repo's HEAD commit and whether its working tree is dirty relative to it
    -- Tommy's doctrine-version traceability stamp (#300 g5): "practically, it's
    just the repo rev number ... it could just be the current repo version in
    totality for ease."

    A bare commit SHA lies about a dirty tree -- that is precisely why
    `context_manifest.rev()` never uses one for a per-file row. An earlier
    version of this docstring argued `dirty` keeps that coarser, repo-wide SHA
    honest by shipping *inside the same content field* as `commit` -- a review
    disproved that (#300 g5 rework 1): two checkouts at the same commit,
    delivering byte-identical declared canon, disagreed on content solely
    because `git status --porcelain` is repo-wide and picked up dirt on a file
    no declaration named. What to do about that was `context_manifest`'s call,
    not this function's: `commit` is canon-determined (identical for any
    checkout of that commit) so it is safe as manifest *content*, and `dirty`
    first moved to the manifest's excluded `run` subtree and was then dropped
    altogether (#327, #305 g4) -- it is repo-wide, so it reports dirt on files no
    declaration names, and once a real caller made that observable the field
    turned out to be neither dependably constant nor informatively varying.
    Neither move reopens the honesty gap a bare SHA has -- the per-file blob OID
    already answers "which bytes did this agent actually get" for a dirty,
    untracked or out-of-repo file, which is the question `dirty` was protecting;
    `commit` only ever had to be the coarse, human-facing traceability stamp.
    This function is unaffected and still returns both fields together: it is a
    general repo-facts primitive, not pre-shaped to one caller's appetite, and
    its one manifest consumer simply now uses `commit` only.

    Uses `_git()`, the same subprocess helper `_collect_changed_files` already
    relies on for git-change-policy -- so this stays the one place in the module
    that shells out for repo-level git facts, not a second ad-hoc caller.
    `context_manifest.py` imports this function by name rather than reimplementing
    it, which keeps that module's own "shells out to nothing" invariant
    (`ProducerGuards.test_producer_shells_out_to_nothing`) literally true: no
    `subprocess` identifier ever appears in its source.

    Absence -- no git on PATH, `base_dir` not inside a repository, or any other
    git failure -- yields `{"commit": None, "dirty": None}` rather than raising.
    A revision stamp is best-effort provenance, not a precondition the caller
    must satisfy first; this mirrors `read_bytes()`/`rev()`'s "absence is normal,
    never raise" rule for a manifest row.
    """
    commit_proc = _git(["rev-parse", "HEAD"], base_dir)
    if commit_proc.returncode != 0:
        return {"commit": None, "dirty": None}
    commit = commit_proc.stdout.strip()
    status_proc = _git(["status", "--porcelain"], base_dir)
    dirty = bool(status_proc.stdout.strip()) if status_proc.returncode == 0 else None
    return {"commit": commit, "dirty": dirty}


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
        # ISSUE #454, corner case NOT chased (deliberate): the engine's own verdict
        # here is returncode-only, and an exit code carries no ANSI, so this site is
        # immune to the forced-colour defect that broke the mutation floor. What is
        # NOT immune is an author who writes a check that pipes a colour-capable
        # tool into a text matcher (`pytest ... | grep -c passed`): under the
        # harness's FORCE_COLOR=3 that grep runs against escape-laden text inside
        # the shell, where this engine cannot see it. No shipped template does this,
        # so nothing is fixed here. If check text ever starts parsing tool output,
        # the check itself must clear FORCE_COLOR / pass --color=no.
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
        # #601: `claimed_at` MOVES here too, and this is the whole fix. A
        # relaunched agent reuses its predecessor's session name, so it lands on
        # this branch -- and until now the branch refreshed only the heartbeat,
        # leaving `claimed_at` pinned at the FIRST leg's claim. The reading the
        # successor inherits is then `observed_at > claimed_at`, so
        # `_reading_is_pre_claim` reads it as owned and the #477 guard sits there
        # doing nothing on precisely the case it exists for. Measured live: leg 2
        # told "18% (>= hard), stand down" on turn one, having done nothing, with
        # `--force` (which skips this branch and rewrites the block below) the
        # only way to make a relaunch work.
        #
        # A claim is a claim: whoever is standing here now took the lease now.
        # The cost is one call's worth of enforcement -- readings older than this
        # moment are declined until the writer samples again, which it does on
        # the next tool call -- and that direction is fail-safe (no reading means
        # no trip) by the same rule the rest of this subsystem follows.
        #
        # The residual, stated rather than hidden: because ownership is measured
        # in TIME, `claim` is now a one-call governor deferral -- an agent over
        # the line can re-claim and get one unguarded verb before the next sample
        # lands. It is journaled, so it is auditable rather than silent, and the
        # real fix is to measure ownership by IDENTITY instead (#600), which
        # retires this whole timestamp comparison.
        existing["claimed_at"] = now
        existing["claimed_by"] = claimed_by or existing.get("claimed_by")
        if worktree is not None:
            existing["worktree"] = worktree
        return f"resumed lease {session_id} (heartbeat refreshed, claim re-stamped)"

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

    # #305: ARM the refusals counter. Armed here, at lease creation, so that a
    # `refusals: 0` is a real reading — "an engine that counts refusals drove this
    # run, and none happened" — rather than being ambiguous with "this file predates
    # the counter". That is what keeps ABSENCE meaningful, which is what lets
    # `episode_capture.mechanical_fields` REFUSE the field rather than report a
    # fabricated 0. `setdefault`, so a re-claim never resets a live tally; and
    # deliberately not on the idempotent-resume path above (which returns early),
    # because resuming a pre-counter run must not backdate a 0 over refusals that
    # really happened and were never recorded.
    cl.setdefault("refusals", 0)
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


def has_pending_refresh_request(cl: dict, gate: str, why_ref: str | None = None) -> bool:
    """Pure predicate: True iff a pending `refresh-request` targets `gate`.

    A refresh-request is a `refresh-request`-typed evidence item (attached via the
    ordinary `attach` verb) whose payload carries POINTERS ONLY: `seam` = the gate
    it concerns, `why_ref` = the why-record id it was raised against — never copies
    of state. It is pending while present and not superseded (the reopen cascade
    supersedes evidence; the flow that consumes/fulfils it is #183). No shared
    mutable state, no side effects.

    `why_ref` (#190) is an OPTIONAL identity filter. When None (the default — the
    DISPLAY semantic: "a refresh is pending for this gate"), any pending request for
    the gate matches, UNCHANGED. When given, a pending request ALSO has to carry the
    matching `payload.why_ref` — an identity match, so a NEW trip on a still-open
    gate cannot ride a stale/earlier request's coattails (HARD-band callers pass the
    current-digest why-record id; a None id degrades to the gate-only match)."""
    for t in cl.get("tasks", {}).values():
        if not isinstance(t, dict):
            continue
        for ev in t.get("evidence", []) or []:
            if not isinstance(ev, dict) or ev.get("type") != "refresh-request":
                continue
            if ev.get("superseded"):
                continue
            payload = ev.get("payload") or {}
            if payload.get("seam") != gate:
                continue
            if why_ref is not None and payload.get("why_ref") != why_ref:
                continue
            return True
    return False


def _why_suffix(cl: dict, aid: str | None) -> str:
    """The why-capture lines appended to `current`: a `DIGEST:` line carrying the
    live understanding, and a `REFRESH REQUESTED:` line when a pending
    refresh-request targets the active gate/item. Empty when neither applies. No new
    verb — these ride the read-only `current`. Renders for BOTH gated and survey
    checklists (#189): a survey never accumulates a `why_trail` (`_append_why` only
    fires on `advance`, which refuses surveys), so `_digest` is None and NO `DIGEST:`
    line appears — only the `REFRESH REQUESTED:` line, which is the reach-up target
    for survey roles (reviewer). Gated output is unchanged."""
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
#   HARD (fill >= hard): the engine REFUSES the verbs that BEGIN work at a gate —
#     `start` and `reopen` (TRIP_HARD_GUARDED_VERBS) — until a `refresh-request`
#     exists for the gate (#179's `has_pending_refresh_request`), pointing at the
#     exact `attach` command with the concrete live why-record id. HARD ALWAYS
#     forces. It does NOT refuse `advance` (#467): closing the gate you are already
#     inside IS the handoff, and an agent running out of context must be able to
#     finish and hand off the gate it is in. `resume` is not guarded either — it
#     only restores a blocked gate to the status it already held. What HARD adds on
#     the CLOSE side is a ban on SILENCE: at/over hard `advance --mechanical` is
#     refused and `why_exempt` is suspended, so the digest cannot stay pre-trip
#     while the gate closes (#431).
#
# HARD means WRAP UP. It has never meant "you are unsafe", and its advisory is
# worded as a changed instruction rather than an alarm — an agent that reads an
# alarm looks for a way past it instead of doing the thing it is being asked to do.
#
# CHECKS AT GATE BOUNDARIES ONLY — the mid-gate runaway is a deliberately accepted
# limit; there is no mid-gate check. Like the doctrine rail, this policy rides the
# CLI-boundary chokepoints in `dispatch` so the verb functions stay PURE (their
# return values are unchanged, so existing exact-equality tests keep passing): SOFT
# is a suffix on `current`'s dispatch output; HARD is a pre-verb guard on
# `start`/`reopen` plus the `require_why` flag `dispatch` passes into `advance`
# (default False, so a direct non-dispatch call is unaffected).
#
# The agent NEVER introspects fill: the engine supplies the fill fact, the agent
# supplies the stop-point judgment.
#
# ROLLOUT CAVEAT: do NOT enable/exercise the HARD band in production until #183's
# tier-skill wiring lands — an agent hitting HARD writes a refresh-request with no
# invoker watching and can strand. Both bands are built and tested here; this is a
# rollout-ordering constraint, not a build dependency.
# --------------------------------------------------------------------------- #
def _checklist_owner(cl: dict) -> str | None:
    """The owner key of the session currently driving this checklist, or None
    (#600).

    The gauge used to be one file per work DIRECTORY, so two agents whose spine
    files share an `.agent-work/<work_id>/` wrote to one path and the last one
    won. The writer now names each record for its owner; this is the read side
    of that same name, and the two are the SAME STRING BY CONSTRUCTION: the
    writer takes it from the binding entry's `engine_session`, which was parsed
    from `claim --session-id X`, and this takes it from the lease holding that
    same X. Neither side spells the name itself — `gauge_reader.owner_key` is
    the one definition both load (decision:one-owner-key-definition), because
    drift of a single character here would silently stop every reading
    resolving.

    Only an ACTIVE lease names an owner. No lease, a released lease, an absent
    reader, or a `session_id` there is nothing to key on — all yield None, which
    means the UNOWNED file, which is today's behaviour exactly (R3). Never
    raises."""
    if _gauge_reader is None or not isinstance(cl, dict):
        return None
    lease = _active_lease(cl)
    if lease is None:
        return None
    try:
        return _gauge_reader.owner_key(lease.get("session_id"))
    except Exception:
        return None


def _gauge_path(cl: dict, base_dir: Path | None) -> Path | None:
    """The gauge file for this checklist: `.agent-work/<work_id>/gauge-<owner>.json`
    when a lease names an owner, and `gauge.json` when none does — a SIBLING of
    the spine either way, because #180's writer drops it at `Path(spine).parent`
    and `base_dir` IS that spine directory. Returns None when the location is
    unresolvable (no `base_dir`, e.g. a checklist processed without a file path):
    an unresolvable work_id yields no reading and no advice.

    NO FALLBACK, and that is the point (#600,
    decision:unattributable-means-no-reading). When a lease DOES name an owner
    and no file of that name exists, this still returns the owner-keyed path, so
    the read below simply finds nothing. Reaching for the shared `gauge.json`
    instead would reinstate the folder-owned file this whole change exists to
    remove, and would hand this session a number some other agent sampled."""
    if base_dir is None:
        return None
    owner = _checklist_owner(cl)
    if _gauge_reader is None:
        return Path(base_dir) / "gauge.json"
    return Path(base_dir) / _gauge_reader.gauge_filename(owner)


def _owner_mismatch(cl: dict, path: Path | None) -> str | None:
    """The owner a record CLAIMS when that disagrees with the name it is sitting
    in, else None (#600).

    The filename removes the collision; the field makes a mismatch DETECTABLE if
    one ever reappears — both, not either (R1). A record whose stamped owner is
    not this checklist's owner can only be a bug (the two sides compute the key
    from the same string through the same function), and the safe response to a
    bug in a provenance claim is to decline the reading, which is always the
    QUIET direction and never a new refusal.

    None — no mismatch — for a record with no `owner` at all: every gauge file
    written before this field existed has none, and they must keep working."""
    if _gauge_reader is None or path is None:
        return None
    try:
        stamped = _gauge_reader.record_owner(path)
    except Exception:
        return None
    if stamped is None:
        return None
    owner = _checklist_owner(cl)
    return stamped if owner is not None and stamped != owner else None


def _read_gauge(cl: dict, base_dir: Path | None):
    """Read a fresh `Reading` for this checklist, or None. Fail-safe: an absent
    reader binding or unresolvable path collapses to None, and the reader itself
    never raises (every failure mode — absent/corrupt/malformed/stale/clock-skew —
    is already collapsed to None inside `read()`). A None reading must produce
    neither a SOFT question nor a HARD refusal.

    `cl` is threaded in for the OWNER (#600), which decides WHICH file this is.
    A record whose stamped owner contradicts that name is declined here too, so
    the band an agent is judged against and the advisory it is shown agree about
    ownership — the same one-place rule `_reading_predates_claim` already keeps
    for the sequential case."""
    if _gauge_reader is None:
        return None
    path = _gauge_path(cl, base_dir)
    if path is None:
        return None
    if _owner_mismatch(cl, path) is not None:
        return None
    return _gauge_reader.read(path)


# --- #477: a reading has an OWNER, and only the lease can name it ------------ #
#
# The gauge is written per checklist DIRECTORY, so the number a fresh agent finds
# on its first `current` was sampled by whoever drove that directory before it —
# its predecessor after a relaunch, or the Commander whose work area its own plan
# sits in. Measured live 2026-08-08 (epic 418): a crew read `fill_fraction
# 0.190464, observed_at 23:18:53Z`, NINE MINUTES before that agent existed, and
# was over the hard line on turn one having done nothing. The failure that
# follows is a LOOP — relaunch, inherit, trip, hand off, relaunch — and every
# cycle looks like correct doctrine being followed. It cost that epic four crew
# relaunches in one wave.
#
# There is NO predicate over the bare number that separates a reading I took from
# one you took; that is exactly why the bug exists. The record itself carries no
# owner (adding one is the WRITER's job, and the writer is not this module's to
# change), so the only WHO-and-WHEN fact available on the read side is the
# engine's own lease: `engine_session.claimed_at` is the moment the session
# currently driving this checklist took it. A sample from strictly before that
# moment cannot be that session's, whatever number it carries.
#
# FAIL OPEN, deliberately and in every direction. No lease, a released lease, a
# missing or unparseable `claimed_at`, no reading at all — every one of them
# means "no provenance to judge", and the engine then behaves EXACTLY as it did
# before this guard existed. A gauge subsystem that started refusing readings
# would stop every run in the fleet; the point is to stop a FOREIGN reading being
# obeyed, not to stop readings. Every `gauge.json` already on disk carries no
# provenance field and keeps working untouched.
def _lease_claimed_at(cl: dict) -> datetime | None:
    """When the session currently driving this checklist claimed it, or None.

    None means "no usable provenance anchor", and every caller must read that as
    fail-open. Only an ACTIVE lease qualifies: a released one names nobody
    currently driving, so it cannot say whose reading a sample is."""
    if not isinstance(cl, dict):
        return None
    lease = _active_lease(cl)
    if lease is None:
        return None
    raw = lease.get("claimed_at")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return _parse_ts(raw)
    except (ValueError, TypeError):
        return None


def _reading_predates_claim(cl: dict, reading) -> bool:
    """True only when `reading` was sampled STRICTLY BEFORE the acting session
    claimed this checklist — i.e. it is provably not that session's own reading.

    THE SINGLE PLACE this decision is made, so the advisory an agent is SHOWN and
    the band it is JUDGED against can never disagree about whose reading it is
    (the same one-place rule `_trip_hard_band_reading` already keeps for the hard
    line itself).

    STRICTLY before: an equal timestamp is owned. The engine's `claimed_at` and
    the writer's `observed_at` come from two different clocks at second-ish
    resolution, so treating coincidence as foreign would silence real readings
    for no gain — and the cost of that boundary going the other way is one turn
    of silence, not a wrong number.

    Returns False — fail open — for a missing reading, a missing/released lease,
    or a `claimed_at` that will not parse. Never raises."""
    if reading is None:
        return False
    claimed_at = _lease_claimed_at(cl)
    if claimed_at is None:
        return False
    observed_at = getattr(reading, "observed_at", None)
    if not isinstance(observed_at, datetime):
        return False
    try:
        return observed_at < claimed_at
    except TypeError:
        return False


def _gate_headroom_tokens(cl: dict, gate: str | None) -> int:
    """The absolute-token context reserve `gate` declares for itself, or 0 (#467).

    THE SINGLE READER of the override, and it reads ONE place:
    `tasks.<gate>.context_headroom_tokens`. A gate that is known to be expensive
    declares how much room it needs left over, and the governor holds it to that
    -- while remaining structurally incapable of asking for LESS than the shipped
    default (the tighten-only clamps live in `gauge_reader.thresholds_for`, the
    module that owns the window and the caps; this function only reads a number
    and never computes a threshold, per constraint:no-threshold-values).

    NO CHECKLIST-CONFIG TIER (decision:no-config-tier): a run-wide reserve would
    have zero users today, and a seam with one hypothetical adapter is a guess,
    not a boundary. A value parked in `config` or at the checklist root is simply
    not read.

    Total and fail-safe, exactly like the rest of this section: no gate named, an
    unknown gate, a missing key, a malformed value (anything that is not a plain
    int -- `bool` is excluded even though it is an int subclass, so a stray
    `true` cannot become a 1-token reserve), or a negative value all resolve to
    0, which means "the shipped default", never "no governor"."""
    if not gate:
        return 0
    task = (cl.get("tasks") or {}).get(gate)
    if not isinstance(task, dict):
        return 0
    raw = task.get("context_headroom_tokens")
    if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
        return 0
    return raw


def _refresh_attach_hint(gate: str, why_id: str | None = None) -> str:
    """The exact `attach` command that raises a refresh-request for `gate` — the
    remedy both bands point the agent at (payload is pointers only: seam + why_ref,
    per #179).

    `why_id` is the live why-record id, and passing it is the whole point (#467):
    the literal `<why-id>` placeholder is not a prompt an agent reliably fills in —
    four separate runs pasted it verbatim, and `attach ... --field why_ref=<why-id>`
    exits 0 while recording a request that matches no understanding, so the identity
    check (#190) never releases and the agent cannot tell why. The placeholder
    survives only as the fallback for a checklist with no live why-record to name."""
    return (f"attach {gate} --type refresh-request "
            f"--field seam={gate} --field why_ref={why_id or '<why-id>'}")


def _uncalibrated_advisory(cl: dict, base_dir: Path | None) -> str:
    """A visible notice that the context governor is OFF for this run because
    the running model has no calibration entry.

    Deliberately not a refusal and not a nudge to hand off: with no window we
    cannot claim the context is either full or empty, so the honest report is
    that the instrument is unavailable, plus the one-line fix. Fail-safe like
    everything else on this path -- an absent reader or unresolvable location
    yields the empty string."""
    if _gauge_reader is None:
        return ""
    path = _gauge_path(cl, base_dir)
    if path is None:
        return ""
    try:
        model = _gauge_reader.uncalibrated_model(path)
    except Exception:
        return ""
    if not model:
        return ""
    return (f"\nCONTEXT GAUGE OFF: no calibration entry for model {model!r}, so "
            f"context fullness is NOT being measured this run — no soft/hard "
            f"trip will fire, however long the run gets. Watch your own context "
            f"and hand off on judgement. To fix: add {model!r} to both "
            f"MODEL_WINDOWS (scripts/hooks/gauge_writer_hook.py) and _PROFILES "
            f"(scripts/gauge_reader.py), using the window from the published "
            f"model catalog — never an inferred one.")


def _format_age(delta: timedelta) -> str:
    """Render a timedelta as whole seconds/minutes/hours — pure arithmetic and
    string formatting only, NO threshold comparisons (constraint:no-threshold-
    values): the unit boundaries below (60s/min, 3600s/hr) are unit-conversion
    arithmetic, not a judgment call on whether an age is "old" — this function
    never decides that, it only renders whatever age it is handed. A negative
    delta (a caller passing a future observed_at) clamps to 0s rather than
    printing a negative age."""
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    if total_seconds < 60:
        return f"{total_seconds}s"
    if total_seconds < 3600:
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}m{seconds:02d}s"
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return f"{hours}h{minutes:02d}m"


def _skip_reason_advisory(gauge_path: Path | None) -> str:
    """A visible notice that the writer hook POSITIVELY LOCALIZED why no
    reading was written at this gauge path (issue #271) — ambiguous session->
    spine binding, or a transcript with no usable usage record. Neither cause
    is routine silence: the writer hook already knows exactly why it skipped,
    so saying nothing here would waste information it already has. Fail-safe
    like every other gauge-adjacent advisory — an absent reader, unresolvable
    path, or any problem reading the sidecar yields the empty string."""
    if _gauge_reader is None or gauge_path is None:
        return ""
    try:
        info = _gauge_reader.skip_reason(gauge_path)
    except Exception:
        return ""
    if not info:
        return ""
    age = _format_age(datetime.now(timezone.utc) - info["observed_at"])
    reason = info["reason"]
    if reason == "ambiguous-binding":
        count = info.get("candidate_count")
        candidates = f"{count} candidate spines" if count is not None else "more than one candidate spine"
        return (f"\nCONTEXT GAUGE SILENT: this session is bound to {candidates} at "
                f"once, so the writer hook could not tell which one a reading "
                f"belongs to and wrote nothing rather than guess (flagged {age} "
                f"ago). Watch your own context and hand off on judgement.")
    if reason == "no-usable-record":
        return (f"\nCONTEXT GAUGE SILENT: the writer hook found a transcript but "
                f"no usable usage record in it, so no reading was written "
                f"(flagged {age} ago). Watch your own context and hand off on "
                f"judgement.")
    # Forward-compatible fallback for a reason string this dispatcher doesn't
    # name explicitly yet — still says SOMETHING rather than staying silent.
    return (f"\nCONTEXT GAUGE SILENT: no reading was written (flagged {age} ago) "
            f"— reason: {reason!r}. Watch your own context and hand off on "
            f"judgement.")


def _stale_record_advisory(gauge_path: Path | None) -> str:
    """When `read()` itself rejected the gauge file at this path (e.g. it is
    simply too old, or clock-skewed, or names an uncalibrated model), report
    the file's OWN raw facts — fill, model, age — with explicitly NO threshold
    judgment: this is not a fresh SOFT/HARD verdict, just the last recorded
    number, so a caller never mistakes a frozen reading for a live low one.
    Fail-safe like every other gauge-adjacent advisory."""
    if _gauge_reader is None or gauge_path is None:
        return ""
    try:
        raw = _gauge_reader.raw_record(gauge_path)
    except Exception:
        return ""
    if not raw:
        return ""
    age = _format_age(datetime.now(timezone.utc) - raw["observed_at"])
    return (f"\nCONTEXT GAUGE SILENT: the last recorded reading at this path was "
            f"{raw['fill_fraction']:.0%} full on {raw['model']!r}, sampled {age} "
            f"ago — too old (or otherwise rejected) to trust as a live reading. "
            f"This is the raw last-known number, NOT a fresh soft/hard judgment. "
            f"Watch your own context and hand off on judgement.")


def _declined_reading_advisory(cl: dict, reading) -> str:
    """Why the gauge is quiet when a perfectly good reading is sitting at this
    path: it was sampled before the acting session got here, so it belongs to
    somebody else (#477).

    Declining SILENTLY would reproduce the exact failure this subsystem has
    already been burned by twice — an unexplained quiet governor is how #252's
    miscalibration and #271's ambiguous binding both survived unnoticed. So this
    says which of the four quiet causes it is, names the session the reading is
    being measured against, and gives the one-line remedy.

    The gap is rendered against `claimed_at`, not against now: "this sample is
    older than your claim by X" is the fact that decides ownership, and it does
    not drift while the agent reads it. Raw facts only, explicitly NOT a
    soft/hard verdict — the same posture as `_stale_record_advisory`, for the
    same reason: a number shown without a judgment cannot be mistaken for one."""
    claimed_at = _lease_claimed_at(cl)
    if reading is None or claimed_at is None:
        return ""
    lease = _active_lease(cl) or {}
    gap = _format_age(claimed_at - reading.observed_at)
    return (f"\nCONTEXT GAUGE DECLINED: the reading at this path "
            f"({reading.fill_fraction:.0%} on {reading.model!r}) was sampled "
            f"{gap} BEFORE session {lease.get('session_id')!r} claimed this "
            f"checklist, so it is NOT this session's reading — the gauge is "
            f"written per work directory, and a fresh agent finds its "
            f"predecessor's number there until its own first tool call lands. "
            f"No soft/hard trip fires on a reading you did not produce. Make any "
            f"tool call, then re-read `current` for your own number; do NOT file "
            f"a refresh-request against this one.")


def _owner_mismatch_advisory(cl: dict, gauge_path: Path | None,
                             stamped: str) -> str:
    """The record at this path names an owner that is not this session's (#600).

    This can only happen through a BUG — the writer and the engine compute the
    owner from the same string through the same function, so the filename and
    the field cannot honestly disagree. That is exactly why it must be loud
    rather than quiet: silence here would look identical to "no gauge yet", and
    an unexplained quiet governor is how #252's miscalibration and #271's
    ambiguous binding both survived unnoticed. Naming both strings is what makes
    the bug diagnosable from the one line an agent actually sees."""
    lease = _active_lease(cl) or {}
    return (f"\nCONTEXT GAUGE DECLINED: the reading at "
            f"{getattr(gauge_path, 'name', gauge_path)!r} is stamped for owner "
            f"{stamped!r}, but this checklist is being driven by session "
            f"{lease.get('session_id')!r}. A record's owner field and its "
            f"filename are computed from the same value, so a disagreement is a "
            f"defect, not a stale file — the reading is NOT used and no "
            f"soft/hard trip fires on it. Watch your own context and hand off on "
            f"judgement, and report this: the gauge writer and this engine have "
            f"drifted apart on how they name an owner.")


def _no_reading_advisory(cl: dict, base_dir: Path | None) -> str:
    """Dispatch across every localizable "why is there no reading" cause, in
    order, returning the FIRST non-empty result — exactly one signal reaches
    the caller even when more than one sidecar happens to exist at a path:

    1. `_owner_mismatch_advisory` (#600) — the record at this path names a
       DIFFERENT owner than the session driving this checklist. First because
       it is the only cause here that can only be a DEFECT rather than a
       condition: the other three describe a gauge that is working correctly
       and has nothing to say, and burying a code bug underneath them is how it
       stays unnoticed.
    2. `_uncalibrated_advisory` (#252) — otherwise unchanged, called exactly as
       before this gate. A STANDING defect (true until a human edits a code
       table), so it takes priority over the two TRANSIENT causes below.
    3. `_skip_reason_advisory` (#271) — the writer hook positively localized
       WHY it skipped this exact path (ambiguous binding / no usable record).
    4. `_stale_record_advisory` (#271) — last resort: `read()` itself rejected
       the file at this path, so report its raw last-known facts rather than
       staying silent about a frozen number.

    EVERY ONE of these now resolves against the file this checklist ACTUALLY
    READS (#600): they take the checklist as well as the directory, so the
    owner-keyed path is what gets inspected. Left on the shared `gauge.json`
    they would each report, in perfect detail, on a file nobody reads.

    Each branch already fails safe to "" on its own (see their docstrings);
    this dispatcher adds no new failure surface."""
    gauge_path = _gauge_path(cl, base_dir)
    mismatch = _owner_mismatch(cl, gauge_path)
    if mismatch is not None:
        return _owner_mismatch_advisory(cl, gauge_path, mismatch)
    advisory = _uncalibrated_advisory(cl, base_dir)
    if advisory:
        return advisory
    advisory = _skip_reason_advisory(gauge_path)
    if advisory:
        return advisory
    return _stale_record_advisory(gauge_path)


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
    reading = _read_gauge(cl, base_dir)
    if _reading_predates_claim(cl, reading):
        # #477: a real, fresh, well-formed reading that belongs to somebody else.
        # Checked BEFORE the None branch below because it is a different question
        # — not "why is there no reading" but "why am I not using the one that is
        # here" — and `_reading_predates_claim` is False for a None reading, so
        # the two branches cannot both fire.
        return _declined_reading_advisory(cl, reading)
    if reading is None:
        # No reading is normally silent (absent/stale gauge is routine). Three
        # causes are NOT routine and must be said out loud, in priority order:
        # an uncalibrated model (#252), a positively-localized writer skip
        # (#271), or the gauge file's own raw facts if `read()` rejected it.
        # See _no_reading_advisory for the dispatch order and why.
        return _no_reading_advisory(cl, base_dir)
    # #467: the ACTIVE gate's own headroom reserve tightens the pair this advisory
    # is computed from — the same resolver, and so the same number, the begin-work
    # guard is about to judge the agent against (`_trip_hard_band_reading`). The
    # engine passes a token count and reads back fractions; it computes no
    # threshold itself (constraint:no-threshold-values).
    soft, hard = _gauge_reader.thresholds_for(reading.model,
                                              _gate_headroom_tokens(cl, gate))
    fill = reading.fill_fraction
    if fill >= hard:
        # Identity-aware (#190): a NEW trip must carry its OWN fresh refresh-request
        # raised against the CURRENT understanding, not ride an earlier one's
        # coattails. `wid is None` (no why_trail — e.g. why_exempt gates) degrades to
        # the gate-only match, preserving all existing behavior.
        rec = _latest_why_record(cl)
        wid = rec["id"] if rec else None
        # #467 (the trip ledger): the ONE render of each compliance fact. The engine
        # already wrote the ledger at `_trip_hard_gate`; this reads it back through
        # the two pure selectors and appends up to two lines to whichever HARD
        # sub-branch is returned below. There is deliberately no second computation
        # of either fact anywhere — an over-the-line begin is reported here or not
        # at all.
        #
        # #467 B1 rework: the LIVE line alone is not enough. The close this HARD
        # band mandates (`advance --why`) is guaranteed to supersede the live
        # why-record, which empties the LIVE selector by design (close criterion
        # (b) — its keying is correct and untouched). Left alone, that means the
        # one required close is also the one thing guaranteed to silence the only
        # rendered signal. The HISTORICAL line is unkeyed and cannot be silenced by
        # any close, so it renders whenever anything is on record at all — even
        # when the live line above it has nothing to say.
        live_note = ""
        historical_note = ""
        records = begin_over_line_records(cl)
        historical = begin_over_line_records_historical(cl)
        if records:
            last = records[-1]
            live_note = (
                f"\nTRIP LEDGER: {len(records)} begin(s) at/over the hard line are on "
                f"the record under this understanding (latest: {last.get('verb') or '?'} "
                f"{last.get('gate')} -> {last.get('outcome')}). Closing THIS gate "
                f"clears this line; the line below, if present, is not.")
        if historical:
            hlast = historical[-1]
            historical_note = (
                f"\nTRIP HISTORY: {len(historical)} begin(s) at/over the hard line "
                f"are on the record across this checklist's full history (latest: "
                f"{hlast.get('verb') or '?'} {hlast.get('gate')} -> "
                f"{hlast.get('outcome')}). No close clears this line.")
        # #467: HARD has always meant "wrap up", never "you are unsafe" — but the old
        # wording ("`advance` is BLOCKED", "lost to a runaway") read as an alarm about
        # a mechanism failing, and an agent that reads an alarm looks for a way past it
        # instead of doing the one thing it is being asked to do. So the HARD band
        # states a CHANGED INSTRUCTION. For pending gates: request refresh, begin the
        # guarded gate, then close it with a handoff. For in-progress gates: close it
        # with a handoff and stop. It also no longer claims `advance` is blocked,
        # because it is not.
        pending = cl["tasks"][gate].get("status") == "pending"
        if has_pending_refresh_request(cl, gate, why_ref=wid):
            if pending:
                return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed, and "
                        f"the refresh for {gate} is already requested. Now begin THIS guarded "
                        f"gate (`start {gate}`), then close it carrying your handoff "
                        f"(`advance {gate} --why \"<understanding>\"`) and stop. A fresh agent "
                        f"picks up from your DIGEST; do not begin work at another gate.") + live_note + historical_note
            return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed, and "
                    f"the refresh for {gate} is already requested. Close THIS gate "
                    f"carrying your handoff (`advance {gate} --why \"<understanding>\"`) "
                    f"and stop. A fresh agent picks up from your DIGEST; do not begin "
                    f"work at another gate.") + live_note + historical_note
        if pending:
            return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed. "
                    f"First request a refresh with: {_refresh_attach_hint(gate, wid)}; then "
                    f"begin THIS guarded gate (`start {gate}`); then close it carrying your "
                    f"handoff (`advance {gate} --why \"<understanding>\"`) and stop. A fresh "
                    f"agent picks up from your DIGEST; do not begin work at another gate.") + live_note + historical_note
        return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed. You have "
                f"taken this as far as this context can carry it — now close THIS gate "
                f"carrying your handoff (`advance {gate} --why \"<understanding>\"`), "
                f"request a refresh, and stop. A fresh agent picks up from your DIGEST; "
                f"do not begin work at another gate. Request the refresh with: "
                f"{_refresh_attach_hint(gate, wid)}") + live_note + historical_note
    if fill >= soft:
        return (f"\nCONTEXT {fill:.0%} (>= soft): you've used most of your context. "
                f"Unless you're basically done, hand off here at {gate} rather than "
                f"pushing through (advisory — decline with a reason if you're nearly done).")
    return ""


def _trip_hard_band_reading(cl: dict, base_dir: Path | None, gate: str | None = None):
    """The gauge Reading when this checklist is in the HARD band right now, else
    None. One place decides "are we at/over hard", so the begin-work guard
    (`_trip_hard_gate`) and the no-silent-close rule (`advance`'s `require_why`)
    can never disagree about it. Fail-safe by construction: surveys and a
    missing/stale reading both yield None, which every caller reads as "band
    inactive" — HARD never forces on an absent reading.

    `gate` (#467) is the gate the question is being asked ABOUT — the one being
    begun, or the one being closed — because the hard line is now per-gate: it is
    tightened by that gate's own `context_headroom_tokens` reserve, resolved by
    `_gate_headroom_tokens` and applied by `gauge_reader.thresholds_for`. It
    defaults to the ACTIVE gate, which is the gate `_trip_advisory` reports on, so
    the number the agent is SHOWN and the number it is JUDGED against come from
    the same resolver on the same gate and cannot diverge. A reserve can only
    TIGHTEN (the clamps live in `thresholds_for`), so an override can never turn
    a Reading in the hard band into a None.

    #477: a reading sampled before the acting session claimed this checklist is
    its predecessor's, and yields None here — the SAME `_reading_predates_claim`
    the advisory consults, so what the agent is shown and what it is judged
    against agree about ownership too, not just about the line."""
    if cl.get("type") != GATED:
        return None
    reading = _read_gauge(cl, base_dir)
    if reading is None or _reading_predates_claim(cl, reading):
        return None
    _, hard = _gauge_reader.thresholds_for(
        reading.model, _gate_headroom_tokens(cl, gate or active_id(cl)))
    if reading.fill_fraction < hard:
        return None
    return reading


def _append_trip_entry(cl: dict, gate: str, verb: str | None, outcome: str,
                       reading, hard: float, why_ref: str | None) -> str:
    """Append one entry to the top-level append-only `trip_ledger` and return its
    id. ENGINE-WRITTEN ONLY: the sole caller is `_trip_hard_gate`, which is reached
    from the `dispatch` chokepoint BEFORE `_run_verb`, so no CLI verb can create,
    edit, or delete an entry.

    Same idiom as `_append_why`: `setdefault` creates the ledger on first write (so
    a spine without one drives unchanged), the id is positional, and a prior entry
    is NEVER mutated or removed.

    `why_ref` is the live why-record id at the moment of the trip. It is what lets
    the compliance selector (`begin_over_line_records`) key on the CURRENT
    understanding, so a mark left under a superseded understanding stops reading as
    present-tense non-compliance without any entry being edited."""
    ledger = cl.setdefault("trip_ledger", [])
    tid = f"tl-{len(ledger) + 1}"
    ledger.append({
        "id": tid, "gate": gate, "verb": verb, "outcome": outcome,
        "fill": round(float(reading.fill_fraction), 4), "hard": round(float(hard), 4),
        "model": reading.model, "why_ref": why_ref, "ts": _now(),
    })
    return tid


def begin_over_line_records(cl: dict) -> list[dict]:
    """PURE selector over stored state: every `trip_ledger` entry recording a BEGIN
    at/over the hard line **under the live understanding**. A `begin-instructed`
    entry is deliberately NOT one of them (#510): that begin is the one the HARD
    advisory itself instructs, so counting it would report an offence for obedience.
    Its emptiness IS the compliance predicate — an empty list means the engine holds no record of anyone
    beginning work over the line under the understanding now in force; a non-empty
    list IS the non-compliance signal.

    Pure by construction: it reads `trip_ledger` and `_latest_why_record` and
    nothing else — no subprocess, no gauge read, no clock — so it is safe to call
    from the read-only `current` path.

    Keyed to the live understanding: an entry matches only when its `why_ref` is the
    id of the CURRENT why-record. A `reopen` freshens the digest by APPENDING a
    reopen-marker, so an older entry's understanding stops being live and its mark
    stops reading as current non-compliance — the entry itself is never touched.
    (A spine with no `why_trail` has a live id of None, and entries written under
    that same silence carry None too, so they still match.)

    An EMPTY list is NOT a claim of compliance. It means "no recorded begin over the
    line under this understanding". The engine cannot see an agent that was told to
    wrap up and simply stopped without running another verb — see the scoped limit
    in `docs/CHECKLIST_SCHEMA.md`."""
    rec = _latest_why_record(cl)
    live = rec["id"] if rec else None
    out: list[dict] = []
    for e in cl.get("trip_ledger", []) or []:
        if not isinstance(e, dict):
            continue
        if e.get("outcome") not in ("begin-refused", "begin-released"):
            continue
        if e.get("why_ref") != live:
            continue
        out.append(e)
    return out


def begin_over_line_records_historical(cl: dict) -> list[dict]:
    """PURE selector, additive to `begin_over_line_records` and separate from it:
    every `begin-refused`/`begin-released` entry in `trip_ledger`, regardless of
    `why_ref` (#467 B1 rework).

    Where the LIVE selector answers "is there an over-the-line begin under the
    understanding now in force" -- and is therefore emptied by the very close the
    HARD band mandates -- this answers a question that close cannot affect: "has
    this checklist EVER recorded a begin over the line". Nothing here is keyed to
    a why-record, so nothing here can be superseded. The entries are the same
    entries the live selector reads; this is a second, unkeyed view onto them, not
    a second write and not a second source of truth.

    Pure by construction, same as the live selector: reads only `trip_ledger`, no
    subprocess/gauge/clock, so it is safe to call from the read-only `current`
    path. Never raises on a malformed ledger -- a non-list `trip_ledger` (`None`,
    a string, a dict) degrades to nothing via `or []`, and a list holding
    non-dict entries skips them one at a time, matching `begin_over_line_records`'s
    own fail-safe.

    Does not replace the live selector and must never be used to. The live
    selector's keying is close criterion (b) (Admiral pre-ruling) and stays
    exactly as it is; this selector is additive and separately rendered."""
    out: list[dict] = []
    for e in cl.get("trip_ledger", []) or []:
        if not isinstance(e, dict):
            continue
        if e.get("outcome") not in ("begin-refused", "begin-released"):
            continue
        out.append(e)
    return out


def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,
                    verb: str | None = None) -> None:
    """Trip HARD backstop at the verbs that BEGIN work at a gate — `start` (opens a
    pending gate) and `reopen` (drives a complete gate back to in-progress and
    cascades downstream). REFUSE to begin when the gauge reads `fill >= hard` and no
    `refresh-request` is pending for the gate.

    #467 moved this OFF `advance`. Closing the gate you are already inside IS the
    handoff, so it is never governor-refused; what an agent over the line must not
    do is BEGIN work it cannot finish. No-op for surveys, a missing/stale reading
    (None), or below `hard` — HARD never forces on an absent reading. Called BEFORE
    the verb runs, so a refusal leaves the gate's status exactly as it was and never
    refreshes the lease.

    #467 (the trip ledger): this is the ONLY mutating chokepoint at which the HARD
    band is evaluated for a BEGIN, so it is the only place an over-the-line begin
    can be recorded. Three outcomes are recorded here — `begin-refused` (no keyed
    request pending, so the verb raises; `main()` persists on the EngineError path,
    which is what makes the entry durable), `begin-released` (a keyed request was
    pending, so the verb proceeds while still over the line), and `begin-instructed`
    (#510: the released begin is the `start` the HARD pending advisory itself
    instructs, so it is recorded but is not counted as an over-the-line begin — see
    the branch below). The entry is the ONE state change a refusal now makes; the
    gate's own status is still untouched."""
    if not iid:
        return
    # #467: judged against the reserve declared by the gate being BEGUN — an
    # expensive gate's "I need this much room" is a statement about entering IT.
    reading = _trip_hard_band_reading(cl, base_dir, iid)
    if reading is None:
        return  # fail-safe: no reading -> no refusal, no ledger entry, no claim
    # The line the agent is being judged against, recorded alongside the fill so a
    # later reader can see BOTH numbers without re-deriving either. Same resolver,
    # same gate, same reading as `_trip_hard_band_reading` used a line above, so the
    # two cannot disagree.
    _, hard = _gauge_reader.thresholds_for(
        reading.model, _gate_headroom_tokens(cl, iid))
    # Identity-aware release (#190): the pending refresh-request must be keyed to the
    # CURRENT understanding (`_latest_why_record`), so a distinct new trip on a
    # still-open gate cannot be waved through on a stale request's coattails. A None
    # why-record id (no why_trail — why_exempt gates) degrades to the gate-only match,
    # keeping every existing Trip test green.
    rec = _latest_why_record(cl)
    wid = rec["id"] if rec else None
    if has_pending_refresh_request(cl, iid, why_ref=wid):
        # #510: ONE of these releases is the engine's OWN instruction, not the
        # agent's choice. `advance` is refused on a pending gate, so the only way an
        # over-the-line agent can leave its handoff AT a pending gate is the exact
        # sequence `_trip_advisory`'s HARD pending branch names: request the refresh,
        # `start` this gate, then `advance --why`. That start begins no work it
        # cannot finish — it IS the handoff mechanism. Recording it as an
        # over-the-line begin made the compliance signal brand an agent for obeying
        # the engine, which is the contradiction #510 was ruled on.
        #
        # So it is recorded under its OWN outcome. Nothing is hidden: the entry is
        # appended exactly as before, with the same fields and the same append-only
        # guarantee, so an auditor still sees a begin happened over the line and why
        # it was allowed. What changes is that `begin-instructed` is not one of the
        # two outcomes the compliance selectors count, so obedience stops reading as
        # non-compliance. The selectors need no change — they already ignore any
        # outcome outside their pair.
        #
        # The exemption is deliberately as narrow as the instruction that earns it,
        # and is keyed to the state the advisory is rendered from, not to a verb
        # name alone. `reopen` (which cascades downstream and is never instructed),
        # a start with no keyed request (the advisory says request FIRST), and a
        # start aimed at any gate other than the pending ACTIVE one all stay
        # exactly as #467 left them.
        instructed = (
            verb == "start"
            and iid == active_id(cl)
            and cl.get("tasks", {}).get(iid, {}).get("status") == "pending"
        )
        outcome = "begin-instructed" if instructed else "begin-released"
        # The backstop is satisfied and the verb proceeds — but a `begin-released`
        # proceeds WHILE STILL OVER THE LINE, which is exactly the event #467 exists
        # to make observable. Recorded, then released.
        _append_trip_entry(cl, iid, verb, outcome, reading, hard, wid)
        return
    _append_trip_entry(cl, iid, verb, "begin-refused", reading, hard, wid)
    raise EngineError(
        f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit, so "
        f"this is not the moment to BEGIN work here — finish and close the gate you are "
        f"already in, then request a refresh so a fresh agent starts this one. "
        f"Run: {_refresh_attach_hint(iid, wid)}"
    )


# --------------------------------------------------------------------------- #
# state projection (ports-and-adapters port; #227 gate g2) — the single
# sanctioned answer to "what is true right now and what may I legally do next,"
# so an agent never has to fall through to reading spine.json or the engine
# source to find a condition id or a recovery verb. Ratified design:
# .agent-work/archive/2026-07-24-explore-design-thrust/dit-I1-ports-RESULT.md
# (constellation-skills repo, read-only). DELIBERATE DEVIATION from that panel
# (g2 handoff): NO public --json flag, NO render_json adapter, NO explain/show
# verb — the projection below is INTERNAL STRUCTURE ONLY, consumed solely by
# render_human() to build current()'s text. `contract` is still carried so a
# future consumer can pin a shape version, but nothing exposes it yet.
#
# INV-2 (purity): state() reads STORED condition flags ONLY. It must NEVER call
# _check_condition / _run_check_command / subprocess for a command/git-change-
# policy check — reading state must never be a probe. Sharp edge, made
# explicit: a condition's `satisfied: false` in the view means "not yet
# recorded as passing," NEVER "would fail if run now" — only start()/advance()
# actually run a check.
# --------------------------------------------------------------------------- #
_STATE_CONTRACT_VERSION = 1


def _condition_kind(c: dict) -> str:
    """The condition's check kind for display: the literal `check.kind`, or
    "null" for a qualitative (`check: null`) condition. Never runs the check."""
    chk = c.get("check")
    if not isinstance(chk, dict):
        return "null"
    return chk.get("kind") or "null"


def _condition_open(c: dict) -> bool:
    """True iff the condition is NOT (yet) recorded as satisfied. Reads the
    stored `satisfied` flag only — see the INV-2 sharp edge above; this is
    never a live re-check."""
    return not bool(c.get("satisfied"))


def _condition_view(c: dict) -> dict:
    return {
        "id": c.get("id"),
        "statement": c.get("statement", ""),
        "kind": _condition_kind(c),
        "satisfied": bool(c.get("satisfied")),
        "waived": bool(c.get("waived")),
        "attested": bool(c.get("attested")),
    }


def _attestable(kind: str) -> bool:
    """`attest` accepts a qualitative (`check: null`) condition unconditionally,
    or an `artifact` condition by reference (`--evidence`). `command`/
    `git-change-policy` conditions are engine-checked and refuse attest (see
    `attest()`), so they never get an attest hint."""
    return kind in ("null", "artifact")


def _blocking_conditions(conds: list[dict]) -> list[dict]:
    """The subset of `conds` that WILL make `start()`/`advance()` refuse right
    now, from state() alone -- i.e. the conditions a `next:` hint must actually
    account for before suggesting the terminal verb (rework 1, g2 review BLOCK:
    the pre-fix `_next_verbs()` ignored this and suggested a verb that refused
    immediately).

    Only `null`/`artifact`-kind conditions qualify: `_check_condition()` never
    re-runs them (their `satisfied` flag only moves via `attest`/`waive`), so an
    open one here is a GUARANTEED refusal. `command`/`git-change-policy`
    conditions are the opposite case: they are engine-checked LIVE inside
    `start()`/`advance()` itself, so state() cannot know whether they'd pass
    right now without probing them -- and INV-2 forbids that probe. So a
    command/git-change-policy condition showing `[unmet]` must NOT suppress the
    hint; it may well pass when the suggested verb actually runs."""
    return [c for c in conds if _condition_open(c) and _attestable(_condition_kind(c))]


def _next_verbs(aid: str, t: dict, kind: str) -> list[str]:
    """Legal-from-here move templates for the active task, hand-derived from
    the RUNTIME contract of each verb's body — NOT from argparse. Two traps
    this must not reintroduce:

    INV-1 (g2 handoff): `advance --why` is optional at `parse_args()` but
    required at runtime unless `--mechanical` or the gate is `why_exempt` (see
    `advance()`); `attest --evidence` is optional at `parse_args()` but
    required at runtime whenever the condition's `check.kind == "artifact"`
    (see `attest()`). Walking `parser._actions` for `required=True` would
    silently omit exactly those two.

    Rework 1 (g2 review BLOCK): the TERMINAL verb (`start` for a pending task,
    `advance` for an in-progress one) must only appear once every blocking
    null/artifact condition for it is resolved — see `_blocking_conditions()`.
    The gate is ASYMMETRIC: `start()` refuses on unmet PREconditions, `advance()`
    on unmet POSTconditions, so each is checked against its own list only.
    `resume` carries no precondition/postcondition gate at all (see `resume()`),
    so it is never suppressed. `record` is NOT ungated -- since #422/#328 a
    `record --result pass` refuses on an unmet `command`-kind postcondition (see
    `record()`) -- yet its hint is never suppressed either, for the INV-2 reason
    spelled out at the hint itself below.

    Placeholders (`<...>`) mark free text only the agent can supply; every
    other token is a real id read off THIS task."""
    status = t.get("status")
    if status == "blocked":
        return [f'resume {aid} --reason "<why the blocker cleared>"']
    if status not in ("pending", "in-progress"):
        return []
    preconds = t.get("preconditions") or []
    postconds = t.get("postconditions") or []
    verbs: list[str] = []
    sections = [("preconditions", preconds)]
    if status == "in-progress":
        sections.append(("postconditions", postconds))
    for which, conds in sections:
        for c in conds:
            if not _condition_open(c):
                continue
            ckind = _condition_kind(c)
            if not _attestable(ckind):
                continue
            hint = f"attest {aid} --cond {c.get('id')} --which {which}"
            if ckind == "artifact":
                hint += " --evidence <evidence-id>"
            verbs.append(hint)
    if status == "pending":
        if not _blocking_conditions(preconds):
            verbs.append(f"start {aid}")
    elif kind == SURVEY:
        # Never suppressed -- but NOT because record() is ungated (it was when
        # this hint was written; #422/#328 changed that). record()'s only
        # condition gate is on `command`-kind postconditions, and only for
        # `--result pass`. Two things make the hint legal anyway:
        #   1. That gate is `command`-kind ONLY, which is exactly the class
        #      _blocking_conditions() excludes -- INV-2 forbids state() probing
        #      a command, so an [unmet] one must not suppress the hint; it may
        #      well pass when record actually runs.
        #   2. `--result fail` is never gated by it at all (recording an honest
        #      failure must not be blocked by the check that is failing), so the
        #      <pass|fail> hint always offers at least one legal move.
        # `null`/`artifact`-kind postconditions on a survey item remain
        # unevaluated by record() (#422/#328's declared scope), so unlike
        # advance() there is no _blocking_conditions() test to apply here.
        verbs.append(f'record {aid} --result <pass|fail> [--finding "<text>"]')
    elif not _blocking_conditions(postconds):
        if t.get("why_exempt"):
            verbs.append(f"advance {aid}")
        else:
            verbs.append(f'advance {aid} --why "<understanding>" (or --mechanical)')
    return verbs


def state(cl: dict) -> dict:
    """Pure state projection: `cl -> StateView`. Read-only — see the INV-2
    purity note above. `current()` is `render_human(state(cl))`; the whole
    completeness upgrade (#227 items 1+3) lives here, not in the adapter."""
    kind = cl.get("type", GATED)
    aid = active_id(cl)
    active = None
    if aid is not None:
        t = task(cl, aid)
        active = {
            "id": aid,
            "status": t.get("status"),
            "imperative": t.get("imperative", ""),
            "preconditions": [_condition_view(c) for c in (t.get("preconditions") or [])],
            "postconditions": [_condition_view(c) for c in (t.get("postconditions") or [])],
            "next_verbs": _next_verbs(aid, t, kind),
            # Issue #420 defect 2: pure passthrough, no side effect, no check
            # re-run (INV-2) -- `constraints` ([str]) and `anchors` (dict of
            # category -> [str], or a flat [str] on some archived gates) are
            # real, populated corpus content that never reached `current`
            # before this fix. render_human() does the shape-handling.
            "constraints": t.get("constraints") or [],
            "anchors": t.get("anchors"),
            # Issue #433: `directives` is the third field with the same
            # defect -- populated on 8 corpus gates (including the shipped
            # commander spine's `execute`) and never projected, so a gate's
            # standing instruction never reached the agent it binds. Same
            # pure passthrough as `anchors`; render_human() handles the two
            # live shapes via _render_directive_lines().
            "directives": t.get("directives"),
        }
    waived_postconditions: list[str] = []
    consolidation_pending = False
    if aid is None:
        if kind == SURVEY and cl.get("consolidation") is None:
            consolidation_pending = True
        else:
            for iid in cl.get("items", []):
                wt = cl["tasks"][iid]
                for c in wt.get("postconditions", []) or []:
                    if c.get("waived"):
                        waived_postconditions.append(f"{iid}.{c['id']}")
    return {
        "kind": kind,
        "active": active,
        "lease_line": _lease_line(cl),
        "why_text": _why_suffix(cl, aid),
        "consolidation_pending": consolidation_pending,
        "waived_postconditions": waived_postconditions,
        "contract": _STATE_CONTRACT_VERSION,
    }


def _anchor_category_items(items) -> list[str]:
    """Normalize one `anchors` dict category's value to a list of strings.
    Two shapes appear in the live corpus: a list of strings (most mission-
    frame anchors), or a single bare string (e.g. EXECUTE_PLAN.template.json's
    g1-review gate: `{"inherits": "g1-implement anchors — ..."}`). A bare
    string must NOT be treated as an iterable of characters — that silently
    exploded one sentence into one line per letter (found in review of issue
    #420, reproduced against `skills/commander/templates/
    EXECUTE_PLAN.template.json`'s shipped g1-review gate)."""
    if isinstance(items, str):
        return [items]
    if isinstance(items, list):
        return [item for item in items if isinstance(item, str)]
    return []


def _render_anchor_lines(anchors) -> list[str]:
    """Format the `anchors` field for display. Three shapes appear in the
    live corpus (verified against 20+ archived execute.json gates plus the
    shipped EXECUTE_PLAN.template.json, issue #420): a dict of
    category -> [str] (most Commander mission-frame anchors), a dict of
    category -> str (e.g. g1-review's `{"inherits": "..."}`), or a flat [str]
    on some archived gates. Unrecognized shapes render nothing rather than
    guessing at a format the corpus doesn't actually use."""
    if isinstance(anchors, dict):
        return [f"  {category}: {item}"
                for category, items in anchors.items()
                for item in _anchor_category_items(items)]
    if isinstance(anchors, list):
        return [f"  {item}" for item in anchors]
    return []


def _directive_leaf(value) -> str:
    """Spell one `directives` leaf for display. A string renders BARE -- these
    leaves are template paths, output paths and field names an agent pastes
    straight out of `current`, so JSON's surrounding quotes would be noise. A
    list joins its leaves with `", "`. Every other scalar takes JSON spelling,
    so a Python `False` prints as `false` and what the agent reads matches the
    JSON the gate actually carries (`auto_file_discrepancies: false` on the
    shipped commander spine)."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(_directive_leaf(v) for v in value)
    return json.dumps(value)


def _render_directive_lines(directives) -> list[str]:
    """Format the `directives` field for display (issue #433). Two shapes
    appear in the live corpus, verified against a tree-wide inventory of this
    worktree (2955 gates scanned, 8 populated `directives` blocks):

    - a dict of name -> contract dict -- the shape ALL 8 populated corpus
      gates carry, e.g. the shipped skills/commander/templates/
      COMMANDER_SPINE.template.json `execute` gate's `replan_input`. The name
      gets its own line and each contract field an indented line under it.
    - a flat [str] -- the shape docs/CHECKLIST_SCHEMA.md declares and the
      `add` amend op accepts unvalidated. One indented line per ITEM: the
      branch is total, so a non-string item takes its `_directive_leaf`
      spelling rather than being dropped. Filtering the branch to strings would
      silently swallow a populated directive the agent is meant to read, which
      is the very defect this issue closes -- and `_render_anchor_lines` does
      not filter its own list branch either.

    A dict value that is not itself a dict renders as one leaf line beside its
    name rather than an empty header. Unrecognized shapes render nothing
    rather than guessing at a format the corpus doesn't actually use -- the
    same rule _render_anchor_lines states. Deliberately NOT routed through
    the anchors normalizer: the two fields' shapes genuinely differ
    (decision:own-helper-not-anchors-helper)."""
    if isinstance(directives, dict):
        lines: list[str] = []
        for name, contract in directives.items():
            if isinstance(contract, dict):
                lines.append(f"  {name}:")
                lines.extend(f"    {field}: {_directive_leaf(value)}"
                             for field, value in contract.items())
            else:
                lines.append(f"  {name}: {_directive_leaf(contract)}")
        return lines
    if isinstance(directives, list):
        return [f"  {_directive_leaf(item)}" for item in directives]
    return []


def render_human(view: dict) -> str:
    """Human adapter: format a StateView as the text agents read from
    `current`. Pure presentation — every fact comes from `view`; this function
    adds none of its own. The FIRST line of the active branch stays exactly
    `ACTIVE {id} [{status}] — {imperative}` (tests/test_checklist_engine.py's
    GoldenOutputBriefing class, ~3779 on, pins this across every shipped
    template — the docstring used to cite line 818, a stale reference to an
    unrelated `require_session` lease test, corrected by issue #420); the
    conditions block, `n/m met` summary, `constraints:`/`anchors:` blocks (issue
    #420 defect 2 — emitted only when populated, so an empty/absent field adds
    no output), the `directives:` block (issue #433, same emitted-only-when-
    populated rule) and `next:` hint are appended AFTER it. The why/refresh suffix
    (`_why_suffix`, composed — not replaced — into `view["why_text"]` by
    `state()`) rides last, same relative order as before this change; the Trip
    `CONTEXT` advisory is a `dispatch()`-level suffix outside `current()`
    entirely and is untouched."""
    prefix = f"{view['lease_line']}\n" if view.get("lease_line") else ""
    active = view.get("active")
    if active is None:
        if view.get("consolidation_pending"):
            body = "ALL ITEMS VISITED. Next: consolidate"
        else:
            waived = view.get("waived_postconditions") or []
            body = (f"DONE: no open items. WAIVED: {waived}" if waived
                    else "DONE: no open items.")
        return prefix + body + view.get("why_text", "")

    lines = [f"ACTIVE {active['id']} [{active['status']}] — {active['imperative']}"]
    open_pre = [c for c in active["preconditions"] if not c["satisfied"]]
    open_post = [c for c in active["postconditions"] if not c["satisfied"]]
    # (rework 1, non-blocking Fowler note) share the label+lines shape with
    # _next_verbs()'s sections pattern instead of repeating it per list.
    for which, open_conds in (("preconditions", open_pre), ("postconditions", open_post)):
        if open_conds:
            lines.append(f"{which}:")
            lines.extend(f"  {c['id']} [unmet] {c['kind']} — {c['statement']}" for c in open_conds)
    total = len(active["preconditions"]) + len(active["postconditions"])
    if total:
        met = total - len(open_pre) - len(open_post)
        lines.append(f"{met}/{total} met")
    if active.get("constraints"):
        lines.append("constraints:")
        lines.extend(f"  {c}" for c in active["constraints"])
    anchor_lines = _render_anchor_lines(active.get("anchors"))
    if anchor_lines:
        lines.append("anchors:")
        lines.extend(anchor_lines)
    directive_lines = _render_directive_lines(active.get("directives"))
    if directive_lines:
        lines.append("directives:")
        lines.extend(directive_lines)
    if active.get("next_verbs"):
        lines.append("next: " + " | ".join(active["next_verbs"]))
    body = "\n".join(lines)
    return prefix + body + view.get("why_text", "")


# --------------------------------------------------------------------------- #
# verbs (each returns a human/agent-readable message; refusals raise)
# --------------------------------------------------------------------------- #
def current(cl: dict) -> str:
    return render_human(state(cl))


def start(cl: dict, iid: str, base_dir: Path | None = None) -> str:
    t = task(cl, iid)
    if t["status"] != "pending":
        raise EngineError(f"{iid} is {t['status']!r}, cannot start",
                           task_id=iid, verb="start", status=t["status"])
    if cl["type"] == GATED and active_id(cl) != iid:
        # Reviewer BLOCK (g3-review rework 3): this raise never carried
        # task_id/verb/status, so recovery_for() returned "" for it and the
        # bare message's own embedded advice ("start {active} first") was
        # unconditional -- wrong whenever the active gate isn't literally
        # pending (reproduced live for both in-progress and blocked active
        # gates). Wiring status="pending" (guaranteed true here -- the
        # status!="pending" branch above already returned) routes this
        # straight into the EXISTING pending/GATED/non-active branch below,
        # which already never guesses a command for the active gate -- no
        # new logic, just making this raise visible to the one that already
        # exists.
        raise EngineError(f"{iid} is not the active gate; start {active_id(cl)!r} first",
                           task_id=iid, verb="start", status=t["status"])
    preconds = t.get("preconditions", [])
    unmet = [c["id"] for c in preconds if not _check_condition(c, t, base_dir)]
    if unmet:
        raise EngineError(
            f"{iid}: preconditions unmet {unmet} (verify upstream work, then attest)",
            task_id=iid, verb="start",
            unmet=[{"id": c["id"], "which": "preconditions", "kind": _condition_kind(c)}
                   for c in preconds if c["id"] in unmet],
        )
    t["status"] = "in-progress"
    emit_step_manifest(cl, iid, base_dir)  # #305: AFTER the mutation — active_id() picks the step.
    return f"{iid} -> in-progress"


def advance(cl: dict, iid: str, from_child: str | None = None, base_dir: Path | None = None,
            why: str | None = None, mechanical: bool = False,
            require_why: bool = False) -> str:
    if cl["type"] != GATED:
        raise EngineError("advance is for gated checklists; use record")
    t = task(cl, iid)
    if t["status"] != "in-progress":
        raise EngineError(f"{iid} is {t['status']!r}, must be in-progress to advance",
                           task_id=iid, verb="advance", status=t["status"])
    if from_child:
        child_path = Path(from_child)
        if not child_path.is_absolute() and base_dir is not None:
            child_path = base_dir / from_child
        if not child_path.exists():
            raise EngineError(f"child checklist {from_child} not found")
        cons = json.loads(child_path.read_text(encoding="utf-8")).get("consolidation")
        if not cons:
            raise EngineError(f"child {from_child} has no consolidation yet")
        # Idempotent seam (#191): keep the attach BEFORE the guards (an artifact
        # postcondition may legitimately consume this from-child review-result), but
        # skip a duplicate. `main()` persists state even on a refused advance (missing
        # --why / unmet postcondition), so a refuse-then-retry would otherwise
        # double-attach the same consolidation — `attach` appends unconditionally.
        already = any(
            e.get("type") == "review-result" and e.get("payload") == cons
            for e in t.get("evidence", []) or []
        )
        if not already:
            attach(cl, iid, "review-result", cons)
    posts = t.get("postconditions", [])
    if not posts:
        raise EngineError(f"{iid}: a gated gate needs >=1 postcondition")
    unmet = [c["id"] for c in posts if not _check_condition(c, t, base_dir)]
    if unmet:
        raise EngineError(
            f"{iid}: postconditions unmet {unmet}",
            task_id=iid, verb="advance",
            unmet=[{"id": c["id"], "which": "postconditions", "kind": _condition_kind(c)}
                   for c in posts if c["id"] in unmet],
        )
    # Why-capture (#179): postconditions are proven ABOVE, before we ever solicit
    # the why (no buying past unfinished work — a failed postcondition yields the
    # postcondition refusal, not the why prompt). A non-exempt gate must then carry
    # either a running --why or an explicit --mechanical marker; SILENCE FAILS CLOSED.
    # A missing `why_exempt` is treated as NOT exempt (opt-out default). The record
    # lands on the append-only why_trail; a mechanical marker never becomes the digest.
    #
    # `require_why` (#467) is the CLI boundary telling this verb that the context
    # gauge is at/over the HARD threshold. Closing the gate is still NOT refused —
    # closing it is the handoff — but closing it SILENTLY is: `--mechanical` is
    # refused and `why_exempt` is SUSPENDED, so the understanding actually lands on
    # the why_trail. Without this a tripped agent closes with a mechanical marker,
    # `_latest_why_record` skips it, the DIGEST stays pre-trip, and the fresh agent
    # cold-starts from an understanding written before the work it is inheriting —
    # #431, reproduced after its own fix. The parameter defaults to False, so every
    # direct (non-dispatch) caller behaves exactly as before.
    if require_why:
        if mechanical or not (why or "").strip():
            raise EngineError(
                f"{iid}: context is at/over the hard limit, so this gate cannot be "
                f"closed silently — a mechanical or why-less close records no "
                f"understanding, and the next agent would cold-start from a digest "
                f"written before your work. Closing the gate is NOT refused; only the "
                f"silence is. Run: advance {iid} --why \"<understanding>\""
            )
        _append_why(cl, iid, why=why.strip(), mechanical=False)
    elif not bool(t.get("why_exempt")):
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


def record(cl: dict, iid: str, result: str, finding: str | None,
           base_dir: Path | None = None) -> str:
    if cl["type"] != SURVEY:
        raise EngineError("record is for survey checklists; use advance")
    if result not in ("pass", "fail"):
        raise EngineError("result must be pass or fail")
    t = task(cl, iid)
    if result == "pass":
        # #422 D-scope ruling (survey-record-check-scope): mirror advance()'s
        # postcondition check (same _check_condition, same refusal shape) for
        # `command`-kind postconditions ONLY. `null`-kind and `artifact`-kind
        # postconditions on a survey item remain UNEVALUATED here — out of
        # scope for this issue, no current template needs it (build what's
        # needed, comment the rest, pass it up). A `result=='fail'` request is
        # never gated by this check: recording an honest failure must not be
        # blocked by the very check that is failing.
        posts = t.get("postconditions", [])
        command_posts = [c for c in posts if _condition_kind(c) == "command"]
        unmet = [c["id"] for c in command_posts if not _check_condition(c, t, base_dir)]
        if unmet:
            raise EngineError(
                f"{iid}: command postconditions unmet {unmet}; cannot record pass",
                task_id=iid, verb="record",
                unmet=[{"id": c["id"], "which": "postconditions", "kind": "command"}
                       for c in command_posts if c["id"] in unmet],
            )
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
    # Record the pre-block status so `resume` can restore it (status_detail only —
    # NOT the bubbled blockers entry). On a re-block of an already-blocked gate keep
    # the ORIGINAL prior_status; a `blocked` status with no recorded prior (e.g. a
    # reopen cap-escalation) deliberately records none, so `resume` refuses it.
    prior = t["status"]
    existing = t.get("status_detail") or {}
    if prior != "blocked":
        detail["prior_status"] = prior
    elif "prior_status" in existing:
        detail["prior_status"] = existing["prior_status"]
    t["status"] = "blocked"
    t["status_detail"] = detail
    cl.setdefault("blockers", []).append({"item": iid, "blocker": blocker,
                                          "authority_needed": authority, "next_action": next_action})
    return f"{iid} -> blocked (bubbled to parent)"


def resume(cl: dict, iid: str, reason: str, note: str | None = None) -> str:
    """Move a resolved `block` forward: return a blocked gate to the status it held
    BEFORE it was blocked (recorded by `block` as status_detail.prior_status), so the
    delegate float-then-resume pattern has a sanctioned path — before this, the only
    exit from a block was `skip` (OBE). Clears the blocked markers, records the
    resolution, and drops the gate's entry from the bubbled `blockers` list.

    Restores ONLY a `pending`/`in-progress` prior status. A blocked gate with no
    restorable prior (a reopen rework-cap escalation, or a legacy block predating
    this verb) is REFUSED — resuming a cap-escalated gate would bypass the rework cap.
    Refuses a gate that is not `blocked` and an empty reason."""
    t = task(cl, iid)
    if t["status"] != "blocked":
        raise EngineError(f"can only resume a blocked gate; {iid} is {t['status']!r}",
                           task_id=iid, verb="resume", status=t["status"])
    if not (reason or "").strip():
        raise EngineError("resume requires a non-empty --reason (how the blocker was resolved)")
    detail = t.get("status_detail") or {}
    prior = detail.get("prior_status")
    if prior not in ("pending", "in-progress"):
        raise EngineError(
            f"{iid} has no restorable pre-block status (it was rework-cap escalated or "
            f"blocked before `resume` existed, not blocked via `block`); use `reopen`/"
            f"`skip` or a human decision, not `resume`",
            task_id=iid, verb="resume", status="blocked",
        )
    t["status"] = prior
    detail.pop("prior_status", None)
    detail["resume_reason"] = reason
    if note:
        detail["resume_note"] = note
    t["status_detail"] = detail
    blockers = cl.get("blockers")
    if isinstance(blockers, list):
        cl["blockers"] = [b for b in blockers if b.get("item") != iid]
    return f"{iid} resumed -> {prior} (blocker resolved: {reason})"


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


def reopen(cl: dict, iid: str, reason: str, cap: int | None = None,
           base_dir: Path | None = None) -> str:
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
        raise EngineError(f"can only reopen a complete gate; {iid} is {t['status']!r}",
                           task_id=iid, verb="reopen", status=t["status"])
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
    # #305: AFTER the mutation — active_id() picks the in-progress step.
    #
    # This call is a BACKFILL, not a live emit: reopen refuses anything that is
    # not `complete`, and a complete gate necessarily passed `start`, which
    # already wrote this step's manifest — and emit_step_manifest is
    # write-if-absent, so it returns early. On every reachable path in a spine
    # created at or after #305 this is a no-op. It earns its keep only for a
    # spine that predates the seam, where `start` ran before the emit existed
    # and this is the first chance to write the manifest at all (observed live:
    # reopening such a gate did emit). An earlier version of this comment
    # justified the call as if it emitted normally; it does not.
    emit_step_manifest(cl, iid, base_dir)
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


def _new_task(
    task_id: str,
    title: str,
    imperative: str,
    preconditions: list | None = None,
    postconditions: list | None = None,
    constraints: list | None = None,
    directives: dict | None = None,
    child_checklist: str | None = None,
) -> dict:
    """Build a full pending task dict in the one canonical shape shared by
    `append()` (fresh empty containers, no deepcopy -- there is nothing to
    alias) and `_build_amend_task()` (caller deep-copies an amend op's fields
    before passing them in, so the op dict is never aliased into canonical
    state). This constructor does not copy its arguments; that is each call
    site's responsibility, since only one of them needs it. A field added to
    the task shape has exactly one place to add it: here."""
    return {
        "id": task_id,
        "title": title,
        "imperative": imperative,
        "preconditions": preconditions if preconditions is not None else [],
        "postconditions": postconditions if postconditions is not None else [],
        "constraints": constraints if constraints is not None else [],
        "directives": directives,
        "child_checklist": child_checklist,
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }


def _build_amend_task(op: dict) -> dict:
    """Build a full pending task from an `add` op, mirroring `append()`'s shape.
    `preconditions`/`constraints` default to empty; `directives`/`child_checklist`
    default to None. Deep-copied so the caller's op dict is never aliased into
    canonical state."""
    return _new_task(
        op["id"],
        op["title"],
        op["imperative"],
        preconditions=copy.deepcopy(op.get("preconditions") or []),
        postconditions=copy.deepcopy(op["postconditions"]),
        constraints=copy.deepcopy(op.get("constraints") or []),
        directives=copy.deepcopy(op.get("directives")),
        child_checklist=op.get("child_checklist"),
    )


def amend(cl: dict, delta: dict, reason: str, authority: str, base_dir: Path | None = None) -> str:
    """Intentional mid-stream re-planning of a GATED checklist. Apply a delta of
    `add`/`drop`/`rescope` ops that touch PENDING gates only, plus a `retext-check`
    op that corrects the check TEXT of a PENDING or IN-PROGRESS gate without
    satisfying its condition — completed/blocked/skipped gates are never edited, and
    no op ever marks a condition satisfied. The whole delta is ALL-OR-NOTHING: it is
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
    - `retext-check`: correct the check TEXT of one condition on a pending or
      in-progress gate (`command` for a command check, or a same-kind `check`
      object), then reset that condition to unsatisfied — an authoring fix that
      never marks the condition satisfied (that stays `waive`'s job) and never
      changes the check's kind.
    Requires non-empty `--reason` and `--authority` (human ratification), same as
    `waive`.

    On a **survey** only a delta whose ops are ALL `retext-check` is accepted: a
    survey item's command postcondition can carry a placeholder that must be
    resolved through the engine rather than by hand (the reviewer's `r6-fowler`
    record path). `add`/`drop`/`rescope` stay gated-only — a CONSERVATIVE choice,
    not a type-level impossibility; see the refusal text below."""
    if cl.get("type") not in (GATED, SURVEY):
        raise EngineError(
            f"amend applies to gated and survey checklists (this one is {cl.get('type')!r})"
        )
    if not (authority or "").strip():
        raise EngineError("amend requires a non-empty --authority")
    if not (reason or "").strip():
        raise EngineError("amend requires a non-empty --reason")
    ops = (delta or {}).get("ops")
    if not isinstance(ops, list) or not ops:
        raise EngineError("amend delta needs a non-empty 'ops' list")

    if cl.get("type") == SURVEY:
        gated_only = sorted({
            str(op.get("op") if isinstance(op, dict) else op)
            for op in ops
            if not (isinstance(op, dict) and op.get("op") == "retext-check")
        })
        if gated_only:
            raise EngineError(
                f"amend on a survey accepts a retext-check-only delta; "
                f"{', '.join(gated_only)} refused here. This is a CONSERVATIVE "
                "choice, not a type-level impossibility: adding, dropping or "
                "rescoping a survey item is a coherent thing to want, and it is "
                "refused only because nothing needs it yet. Split the "
                "retext-check ops into "
                "their own delta, or raise the need with the authority named in "
                "your handoff."
            )

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
                raise EngineError(
                    f"drop {tid}: only a pending gate can be dropped (is {status!r})",
                    task_id=tid, verb="amend-drop", status=status,
                )
            new_items.remove(tid)
            del new_tasks[tid]
            summaries.append(f"dropped {tid}")
        elif kind == "rescope":
            tid = op.get("id")
            if tid not in new_tasks:
                raise EngineError(f"rescope {tid}: no such gate")
            status = new_tasks[tid]["status"]
            if status != "pending":
                raise EngineError(
                    f"rescope {tid}: only a pending gate can be rescoped (is {status!r})",
                    task_id=tid, verb="amend-rescope", status=status,
                )
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
        elif kind == "retext-check":
            tid = op.get("id")
            if tid not in new_tasks:
                raise EngineError(f"retext-check {tid}: no such gate")
            status = new_tasks[tid]["status"]
            if status not in ("pending", "in-progress"):
                raise EngineError(
                    f"retext-check {tid}: only a pending or in-progress gate's check text "
                    f"may be corrected (is {status!r}); reopen a complete gate instead",
                    task_id=tid, verb="amend-retext-check", status=status,
                )
            which = op.get("which", "postconditions")
            if which not in ("preconditions", "postconditions"):
                raise EngineError(f"retext-check {tid}: which must be 'preconditions' or 'postconditions'")
            cond_id = op.get("cond")
            # Deep-copy before mutating so canonical state is untouched until commit.
            updated = copy.deepcopy(new_tasks[tid])
            target = next((c for c in updated.get(which, []) if c.get("id") == cond_id), None)
            if target is None:
                raise EngineError(f"retext-check {tid}: no {which} condition {cond_id!r}")
            old_check = target.get("check")
            if not isinstance(old_check, dict):
                raise EngineError(
                    f"retext-check {tid}.{cond_id}: only an engine-checked condition has check "
                    f"text to correct (this is check:null — satisfy via attest or accept risk via waive)"
                )
            if "command" in op:
                if old_check.get("kind") != "command":
                    raise EngineError(
                        f"retext-check {tid}.{cond_id}: 'command' corrects a command check, but "
                        f"this check is kind {old_check.get('kind')!r}"
                    )
                new_command = op["command"]
                if not isinstance(new_command, str) or not new_command.strip():
                    raise EngineError(f"retext-check {tid}.{cond_id}: 'command' must be a non-empty string")
                old_check["command"] = new_command
            elif "check" in op:
                new_check = op["check"]
                if not isinstance(new_check, dict) or new_check.get("kind") is None:
                    raise EngineError(
                        f"retext-check {tid}.{cond_id}: a replacement 'check' must be an object with "
                        f"a non-null kind (a check:null swap is not a check-text correction)"
                    )
                if new_check.get("kind") != old_check.get("kind"):
                    raise EngineError(
                        f"retext-check {tid}.{cond_id}: cannot change check kind "
                        f"{old_check.get('kind')!r} -> {new_check.get('kind')!r}; correct the text, "
                        f"not the condition's nature"
                    )
                target["check"] = copy.deepcopy(new_check)
            else:
                raise EngineError(f"retext-check {tid}.{cond_id}: provide 'command' or a 'check' object")
            # Correcting the check invalidates any prior (wrong-check) verdict: force a
            # fresh re-evaluation but NEVER satisfy (that stays waive's job). Clears
            # satisfied/satisfied_by AND waived/attested so _check_condition cannot
            # short-circuit past the corrected check on a stale approval.
            _reset_conditions([target])
            new_tasks[tid] = updated
            summaries.append(f"retext-check {tid}.{cond_id}")
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
    cl["tasks"][iid] = _new_task(iid, title, imperative)
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
    raise EngineError(
        f"condition {cond_id!r} not found in preconditions or postconditions on {iid}",
        task_id=iid, verb="attest",
        valid_ids=[c["id"] for c in t.get("preconditions", [])]
        + [c["id"] for c in t.get("postconditions", [])],
    )


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
    s = sub.add_parser("resume")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s.add_argument("--note")
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
        # Trip HARD backstop (#182, re-aimed by #467): the guard hangs off the verbs
        # that BEGIN work at a gate — `start` opens a pending gate, `reopen` drives a
        # complete one back to in-progress — and NEVER off `advance`, which closes the
        # gate the agent is already inside and IS the handoff. `resume` is deliberately
        # not here: it returns a blocked gate to its pre-block status, which for an
        # in-progress prior hands back the gate already under way. Checked BEFORE the
        # verb runs so a refusal never mutates state and never stamps liveness. No-op
        # on a missing reading.
        if v in TRIP_HARD_GUARDED_VERBS:
            _trip_hard_gate(cl, getattr(args, "id", None), base_dir, verb=v)
        # Run the verb FIRST: a refused verb raises here (before the liveness stamp),
        # so it never refreshes the lease even though main() persists on the error
        # path. Only a verb that returns successfully reaches the stamp below.
        message = _run_verb(cl, args, base_dir)
        # Owner activity = liveness: a SUCCESSFUL mutating verb by the owner refreshes
        # the lease, so an actively-working session never goes stale and an idle gap
        # self-heals. A refused verb never gets here.
        if v in MUTATING_VERBS:
            _refresh_owner_heartbeat(cl, session_id)
    # Doctrine rail (#138 channel A): prepend the position-derived doctrine block
    # to the railed verbs' success output. The verb functions above stay pure; the
    # rail rides only this CLI-boundary chokepoint. `_rail_prefix` returns "" for
    # non-gated checklists. FRONT, not suffix (#227 gate g3, item b/constraint 4):
    # the operative result line must land LAST on the stream so `tail -1` reads
    # it, not the banner -- the field defect this fixes.
    if v in RAIL_VERBS:
        message = _rail_prefix(v, cl) + message
    return message


def _run_verb(cl: dict, args: argparse.Namespace, base_dir: Path | None) -> str:
    """Execute a mutating verb and return its message, or raise EngineError if the
    verb refuses. Read-only/lease verbs are handled by `dispatch` before this."""
    v = args.verb
    if v == "start":
        return start(cl, args.id, base_dir=base_dir)
    if v == "advance":
        # #467: the HARD band never refuses this advance — closing the gate you are
        # inside IS the handoff — but at/over hard it does refuse closing it in
        # SILENCE. The band decision belongs to this CLI boundary, so `advance` stays
        # a pure function of its arguments and every direct caller is unaffected.
        return advance(cl, args.id, from_child=getattr(args, "from_child", None),
                       base_dir=base_dir, why=getattr(args, "why", None),
                       mechanical=getattr(args, "mechanical", False),
                       require_why=_trip_hard_band_reading(
                           cl, base_dir, getattr(args, "id", None)) is not None)
    if v == "record":
        return record(cl, args.id, args.result, args.finding, base_dir=base_dir)
    if v == "consolidate":
        return consolidate(cl, args.verdict, args.summary, args.override_reason)
    if v == "skip":
        return skip(cl, args.id, args.reason)
    if v == "block":
        return block(cl, args.id, args.blocker, args.authority, args.next_action)
    if v == "resume":
        return resume(cl, args.id, args.reason, getattr(args, "note", None))
    if v == "reopen":
        return reopen(cl, args.id, args.reason, cap=rework_cap(load_config(cl, base_dir)),
                      base_dir=base_dir)
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
    OSError is swallowed.

    Byte-faithful, the append-only sibling of `save`'s #465 fix: preserve the
    journal's OWN line ending (a text-mode append translates every written '\\n'
    to the platform's, churning an existing file's endings one line at a time),
    and default a journal that does not exist yet to LF."""
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
    line = (json.dumps(entry, ensure_ascii=False) + "\n").encode("utf-8")
    eol = _dominant_newline(jp)
    if eol != b"\n":
        # json.dumps escapes any literal CR as \r, so no b"\r" survives in the
        # serialised bytes and this replace cannot produce b"\r\r\n".
        line = line.replace(b"\n", eol)
    try:
        with jp.open("ab") as fh:
            fh.write(line)
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.file)
    cl = load(path)
    # Nothing stands between `load` and the arming below any more (#609 g2).
    # Every verb used to pay for a git toplevel read here, on the engine's
    # ambient cwd, to feed the retired `origin.worktree` comparison.
    # Both are gone: THE ENGINE NOW READS NO LOCATION AT ALL, ambient or
    # derived, so no ambient reading is taken and none can be forged -- not
    # because the reading moved somewhere cheaper, but because the engine no
    # longer asks the question anywhere. The lexical rule that derives a
    # worktree from a spine's path is not retired; it lives in the stdlib-only
    # hook as `spine_rail._worktree_from_spine`, and the engine holds no copy
    # of it (module header, above).
    #
    # Nothing is lost by vacating this position. It existed so a refusal could
    # be raised BEFORE dispatch() and returned WITHOUT save() -- main() persists
    # state on the EngineError path for every verb except `current`, so a
    # refusal raised inside dispatch() would write into the very tree it was
    # protecting. With no refusal to raise, there is nothing here to order.
    #
    # What dispatch() still enforces is the LEASE -- and the lease is the
    # ownership guard only WHERE A LEASE EXISTS. `require_session` gates
    # mutating verbs once an active lease is held and returns early otherwise,
    # and `_active_lease` reads a RELEASED lease as absent. So on a spine with
    # NO ACTIVE LEASE -- never claimed, or claimed and since released -- the
    # retired comparison was the sole refusal, and removing it WIDENED that
    # path. That widening is ACCEPTED and deliberate: a `cd <worktree> &&`
    # prefix defeated the comparison, so it was never a boundary -- but a
    # forgeable guard is not the same as no guard. Under an active lease held
    # by another session, nothing changed (`ADMIRAL_RULING-1` R1; the module
    # header above carries the same statement in full).
    #
    # #427: arm `refusals` here, on LOAD, but ONLY for the verb that can
    # itself be the very-first-ever attempt to claim (no `engine_session` at
    # all, ever -- release() leaves the record in place with status
    # "released", it never clears the key, so `is None` really does mean
    # "never claimed"). 0 is a true reading in that case regardless of
    # whether the counter existed when this checklist was created, so
    # arming it here -- BEFORE dispatch() runs -- counts even a refusal from
    # a malformed `claim` call itself. This is deliberately separate from
    # claim()'s own `cl.setdefault("refusals", 0)` (~1030), which stays as
    # the arming point for a checklist that HAS been claimed before: that
    # one must not backdate a pre-counter checklist with a guessed number,
    # and this one cannot possibly guess wrong because "never claimed" means
    # the true count is exactly what happened since.
    #
    # Gated to `args.verb == "claim"` (#357 g1 review carry-over): a child
    # gate plan is legitimately driven with `engine_session` staying None
    # for its ENTIRE life, by design -- start/attest/advance/reopen with no
    # lease and no `claim` call, ever (the production shape #357 names).
    # Arming on any refusal while unclaimed, not just a `claim` refusal,
    # gave that shape a `refusals` key it must never carry -- the negative
    # control in tests/test_episode_negative_control.py asserts the key's
    # ABSENCE is structural there, not "zero refusals happened". Since that
    # checklist never issues a `claim` call at all, this verb-scoped guard
    # leaves it untouched while still catching the malformed-claim case
    # #427 was filed for.
    if cl.get("engine_session") is None and args.verb == "claim":
        cl.setdefault("refusals", 0)
    ev_before = _all_evidence_ids(cl)
    try:
        message = dispatch(cl, args, base_dir=path.parent)
    except EngineError as exc:
        # state may carry legitimate mutations (command results, escalation); persist unless read-only/dry-run
        if not args.dry_run and args.verb != "current":
            # #305: the ONE engine-state source for the `refusals` mechanical field.
            # It has to live here because this is the only place a refusal is
            # observable at all: the journal sidecar is success-only by construction
            # (`append_journal_entry` sits after the `return 1` below), so a refusal
            # left no trace anywhere and the field was secretly agent-dependent.
            # Incremented INSIDE the persistence guard, not above it: a bump that is
            # never saved is a tally that disagrees with its own file, and a dry-run
            # is by definition not something that happened. Run-scoped rather than
            # step-scoped, unlike `rework_count` — a refusal does not always name a
            # task (an unknown item, a lease conflict, a malformed verb), and scoping
            # it to a step would silently drop exactly those, which is the same class
            # of fabrication as inventing a value.
            # Only an ARMED counter is incremented. Creating it here on a pre-counter
            # checklist would write `refusals: 1` onto a run whose real total is
            # unknown and may be five — a plausible wrong number, which is worse than
            # an absent one and is the one thing this field must never be.
            armed = cl.get("refusals")
            if isinstance(armed, int) and not isinstance(armed, bool):
                cl["refusals"] = armed + 1
            save(path, cl)
        # Recovery (#227 gate g3, item a): a state-caused refusal names its exact
        # exit verb, composed HERE at the CLI boundary from the exception's
        # structured attributes -- never inside the verb function that raised.
        recovery = recovery_for(exc, cl)
        refused_line = f"REFUSED: {exc}" + (f" {recovery}" if recovery else "")
        # Doctrine rail (#138 channel A): a refusal is a check-failure decision
        # point. Prepend the check-failure rail (gated checklists only; "" for
        # surveys) -- FRONT, not suffix (#227 gate g3, item b): the operative
        # REFUSED(+recovery) line must land LAST so `tail -1` reads it, not the
        # banner. This is the exact field defect: an Admiral piping engine
        # output through `tail -1` twice saw only RAIL and never the refusal.
        print(f"{_rail_prefix('check-failure', cl)}{refused_line}", file=sys.stderr)
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
