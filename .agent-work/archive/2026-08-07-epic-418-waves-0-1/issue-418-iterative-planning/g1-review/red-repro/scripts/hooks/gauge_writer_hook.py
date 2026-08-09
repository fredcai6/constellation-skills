#!/usr/bin/env python3
"""gauge_writer_hook.py -- Claude Code PostToolUse hook: Context Governor gauge
WRITER (Module 2, write side; issue #180).

On every tool call, senses context fill from the session transcript and
atomically writes `.agent-work/<work_id>/gauge.json` for the engine-side
reader (#181) to consume. See docs/GAUGE_WRITER_HOOK.md for the wiring,
the exact transcript shape this depends on, and what breaks it.

Design contract (frozen DESIGN_SPEC #178, Module 2 post-review amendments):

- Fail-open. Any error anywhere is swallowed; the hook never blocks or
  fails the tool call it's attached to. Every handler is wrapped.
- Skip-on-uncertainty, NEVER fabricate. If fill can't be computed
  confidently (missing transcript, no usable usage record, missing
  timestamp, unresolvable work_id), write NOTHING -- the existing gauge
  file is left exactly as it was and ages into staleness naturally. A
  fabricated 0.0 would read as genuine low fill and could suppress a
  nudge that should have fired.
- Record is FROZEN, four fields only (identical to #181's reader):
  {schema_version: int, fill_fraction: float 0..1, model: str,
  observed_at: ISO-8601 str -- the SAMPLED moment, not write time}.
- Atomic write: tmp file + os.replace. A concurrent reader of gauge.json
  never observes a torn/partial record -- it always sees either the
  complete prior record or the complete new one.
- Session->spine binding is REUSED, not re-derived: `spine_rail.py`
  (this hook's sibling in the same PostToolUse rail) already maintains
  `.agent-work/.spine-rail-binding.json` mapping session_id -> spine
  path. `<work_id>` is that spine path's parent directory. If no binding
  exists for this session (e.g. no `checklist_engine.py claim` has run
  yet), the work_id is unresolvable and the hook skips -- this is a
  documented coupling, not a new mechanism (see docs/GAUGE_WRITER_HOOK.md).
  Because that binding records an unvalidated `--file` argument, the
  resolved target is CONTAINED to the documented
  `.agent-work/<work_id>/gauge.json` shape before any write (_is_contained);
  anything else skips rather than littering an arbitrary directory.
- The X2 "strategic-compact" technique: the transcript is JSONL; each
  top-level (non-sidechain) assistant message carries a `usage` block.
  Because Claude Code resends the full conversation on every turn, the
  LATEST such record's `input_tokens + cache_creation_input_tokens +
  cache_read_input_tokens` IS the current total context size (not a sum
  across lines/turns). Sidechain entries (subagent turns, `isSidechain:
  true`) are a different context window entirely and are skipped.
- Stdlib only. Windows-friendly: UTF-8 I/O, native paths, no /tmp literals.
"""

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

# Context-window token capacity per model, the fill_fraction DENOMINATOR.
# These are the real per-model windows (source: Claude API model catalog):
# Opus 4.8 / Sonnet 5 / Fable 5 ship a 1M window BY DEFAULT (standard tier, no
# beta header); Haiku 4.5 is 200k. Getting this right is load-bearing — a wrong
# (too-small) denominator makes fill read high and trips SOFT/HARD far too early
# (e.g. 200k here vs a real 1M window reads 5x high). Kept per-model (not one
# constant) because the windows genuinely differ and gauge_reader keys thresholds
# per model too; a new model just adds a row.
#
# ADDING A MODEL: every value here must come from the published model catalog
# (platform.claude.com "Models overview"), never from inference. A wrong window
# silently mis-scales every reading for that model. Add the row to
# `gauge_reader._PROFILES` in the same change — a test pins the two key sets
# equal, so a half-added model fails the suite rather than shipping.
MODEL_WINDOWS = {
    # Verified against platform.claude.com/docs/en/about-claude/models/overview,
    # 2026-07-25.
    "claude-opus-5": 1_000_000,
    "claude-opus-4-8": 1_000_000,
    "claude-sonnet-5": 1_000_000,
    "claude-fable-5": 1_000_000,
    "claude-haiku-4-5-20251001": 200_000,
}
# There is deliberately NO default window. The original 200k fallback was
# justified as fail-safe ("an unknown model reads as more-full, so the governor
# errs toward handing off early"), and that reasoning held when 200k was a
# typical window. It no longer does: every non-Haiku model in the current
# lineup is 1M, so an unknown model is far more likely to be 1M than 200k, and
# the "conservative" default produced a 5x OVER-read as its normal behavior.
# Measured live: claude-opus-5 was absent from this table during epic-226 and
# 139,750 real tokens were written as fill_fraction 0.69875 against the 200k
# default, tripping the governor HARD at roughly 14% of a real 1M window.
# An uncalibrated model now yields NO reading and raises a visible flag instead
# (see _write_uncalibrated_flag) -- skip-on-uncertainty, which is what the rest
# of this module already does, rather than a confident wrong number.

# Bounded reverse-scan window (bytes) -- see docs/GAUGE_WRITER_HOOK.md. Real
# transcripts run into the tens of MB; a full forward parse every tool call
# would be wasteful. The latest usage record is always near the tail, so
# reading the last TAIL_BYTES and scanning backward is enough in practice.
# If nothing usable is found in that window, skip-on-uncertainty applies --
# this is a deliberate bounded-cost choice, not a silent truncation bug.
TAIL_BYTES = 2_000_000


# --- reuse the hook rail's session->spine binding (never re-derive) --------

def _load_spine_rail():
    """Load scripts/hooks/spine_rail.py by file path -- robust regardless of
    whether this module is run as a script or imported by a test (mirrors
    tests/test_spine_rail.py's own loading technique). Returns None if the
    sibling module is missing or fails to load; callers then skip (the
    binding becomes unresolvable, which is itself a valid skip-on-uncertainty
    outcome -- see docs/GAUGE_WRITER_HOOK.md)."""
    try:
        path = Path(__file__).resolve().parent / "spine_rail.py"
        spec = importlib.util.spec_from_file_location("spine_rail", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_spine_rail = _load_spine_rail()


def _is_contained(gauge_path: Path) -> bool:
    """True only for the documented shape `<root>/.agent-work/<work_id>/gauge.json`.

    The binding is maintained by a sibling hook from whatever `--file` an engine
    `claim` command carried, so the spine path it records is UNVALIDATED input as
    far as this module is concerned. A claim whose `--file` resolved outside a
    work dir (e.g. a bare `spine.json` run from a checkout root) would otherwise
    make this hook drop a `gauge.json` into that directory -- untracked repo-root
    debris that nothing gitignores, since only `.agent-work/` is ignored.

    `<root>` is deliberately unconstrained: under an active Admiral epic lease
    `durable_root()` resolves to the WORKTREE root rather than the main checkout
    (see scripts/agent_work_root.py), so a legitimate gauge path may sit outside
    `project_dir` entirely. What is invariant across both is the trailing
    `.agent-work/<work_id>/` shape, which is what this checks.
    """
    try:
        return gauge_path.parent.parent.name == ".agent-work"
    except Exception:
        return False


def resolve_gauge_path(project_dir: Path, session_id):
    """`.agent-work/<work_id>/gauge.json` for EVERY spine this session_id is
    currently bound to (#202: one session_id can hold N distinct spine
    bindings at once) -- a list of Path, possibly empty. Each candidate is
    individually checked against `_is_contained`; a candidate that fails the
    fence is dropped rather than failing the whole call, so one bad entry
    never blinds the write for the session's other, legitimate bindings.
    Empty list if unresolvable (no sibling module, no session_id, no binding
    at all) -- skip-on-uncertainty applies to WHERE we write, not just to
    what."""
    try:
        if _spine_rail is None or not session_id:
            return []
        binding = _spine_rail.load_binding(project_dir)
        sid_bindings = binding.get(session_id) or {}
        candidates = []
        for entry in sid_bindings.values():
            spine_path = entry.get("spine") if isinstance(entry, dict) else None
            if not spine_path:
                continue
            candidate = Path(spine_path).parent / "gauge.json"
            if _is_contained(candidate):
                candidates.append(candidate)
        return candidates
    except Exception:
        return []


# --- X2 strategic-compact: parse transcript, sum latest usage record -------

def _iter_tail_lines_reverse(path, max_bytes=TAIL_BYTES):
    """Yield non-blank lines from the tail of `path`, most-recent-first,
    reading at most max_bytes from the end. Never raises."""
    size = os.path.getsize(path)
    read_size = min(size, max_bytes)
    with open(path, "rb") as f:
        f.seek(size - read_size)
        data = f.read(read_size)
    text = data.decode("utf-8", errors="ignore")
    lines = text.split("\n")
    if size > read_size:
        # the first fragment is a partial line (we seeked mid-file) -- drop it
        lines = lines[1:]
    for line in reversed(lines):
        line = line.strip()
        if line:
            yield line


def find_latest_usage(transcript_path):
    """Scan the transcript tail for the most recent main-chain (non-sidechain)
    assistant message carrying a usage record. Returns (model, total_tokens,
    observed_at), or None if nothing usable is found in the scanned window."""
    try:
        for line in _iter_tail_lines_reverse(transcript_path):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            model = msg.get("model")
            observed_at = d.get("timestamp")
            if not model or not observed_at:
                continue
            total = 0
            ok = True
            for field in (
                "input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            ):
                v = usage.get(field)
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    ok = False
                    break
                total += v
            if not ok:
                continue
            return model, total, observed_at
        return None
    except Exception:
        return None


def compute_record(transcript_path):
    """Build the frozen 4-field record for this transcript.

    Returns `(record, uncalibrated)`. At most one is non-None:

    - `(record, None)` -- a usable reading.
    - `(None, {"model": ..., "observed_at": ...})` -- a usable token count for
      a model absent from MODEL_WINDOWS. There is no window to divide by, so
      there is no honest fill to report; the model and the sampled moment come
      back so the caller can flag it.
    - `(None, None)` -- nothing usable found (no transcript record, no
      timestamp, unparseable usage). Write nothing, say nothing.

    "Write nothing" never means "write a placeholder" -- a fabricated fill
    reads as a genuine measurement downstream."""
    try:
        found = find_latest_usage(transcript_path)
        if found is None:
            return None, None
        model, total_tokens, observed_at = found
        window = MODEL_WINDOWS.get(model)
        if window is None:
            return None, {"model": model, "observed_at": observed_at}
        if window <= 0:
            return None, None
        fill = max(0.0, min(1.0, total_tokens / window))
        return {
            "schema_version": SCHEMA_VERSION,
            "fill_fraction": fill,
            "model": model,
            "observed_at": observed_at,
        }, None
    except Exception:
        return None, None


# --- atomic write ------------------------------------------------------------

def _atomic_write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(tmp, path)  # atomic on POSIX and Windows alike


# --- uncalibrated-model flag (visible, not silent) ---------------------------

# A SIDECAR, deliberately not a field on gauge.json: that record is frozen at
# four fields and shared with the reader, and "no reading" must stay literally
# no reading so every existing fail-safe path keeps working untouched. The flag
# rides alongside so the engine can explain the silence instead of the governor
# just going quiet -- an unexplained silent governor is how a miscalibration
# survives unnoticed, which is exactly what happened with claude-opus-5.
UNCALIBRATED_FILENAME = "gauge-uncalibrated.json"


def _uncalibrated_path(gauge_path: Path) -> Path:
    return gauge_path.with_name(UNCALIBRATED_FILENAME)


def _write_uncalibrated_flag(gauge_path: Path, uncalibrated: dict) -> None:
    """Record that this model has no window, so no reading could be produced.
    `observed_at` is the SAMPLED moment carried through from the transcript,
    consistent with the gauge record -- not write time."""
    _atomic_write_json(_uncalibrated_path(gauge_path), {
        "schema_version": SCHEMA_VERSION,
        "model": uncalibrated["model"],
        "observed_at": uncalibrated["observed_at"],
    })


def _clear_uncalibrated_flag(gauge_path: Path) -> None:
    """Drop a stale flag once the model resolves again -- otherwise adding the
    missing row to MODEL_WINDOWS would fix the reading but leave the warning
    nagging forever."""
    try:
        _uncalibrated_path(gauge_path).unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


# --- skip-reason flag (visible, not silent) -- issue #271 --------------------

# A second, independent SIDECAR family (deliberately NOT reusing
# UNCALIBRATED_FILENAME/gauge-uncalibrated.json): that flag is a STANDING
# defect -- true until a human edits MODEL_WINDOWS/_PROFILES, correctly never
# staleness-checked. Ambiguous-binding and no-usable-record are TRANSIENT
# per-call conditions that must expire as binding/transcript state changes on
# a LATER call. Sharing one file/clearing rule across both shapes would either
# make the standing flag falsely time out, or make the transient ones falsely
# persist -- so this is a parallel mechanism, additive alongside the existing
# one, both consumed by checklist_engine.py's single `_no_reading_advisory`
# dispatcher (decision:sidecar-is-a-parallel-mechanism-not-a-literal-
# extension).
SKIP_FILENAME = "gauge-skip.json"


def _skip_path(gauge_path: Path) -> Path:
    return gauge_path.with_name(SKIP_FILENAME)


def _write_skip_flag(gauge_path: Path, reason: str, *, candidate_count: int | None = None,
                      observed_at: str | None = None) -> None:
    """Record WHY no reading was written at this gauge path -- a diagnostic
    fact about the writer's own decision, never a fabricated/misattributed
    reading (unlike gauge.json itself, this is safe to fan out -- see the
    ambiguous-binding branch in handle_post_tool_use below).

    `observed_at` here is WRITE time, unlike the uncalibrated flag's SAMPLED
    moment: neither skip cause reaches a point where a transcript-sampled
    timestamp exists to carry through (ambiguous binding never gets far
    enough to parse the transcript at all; no-usable-record means parsing
    found nothing usable), so "now" is the only honest timestamp available.
    A caller (checklist_engine.py's advisory) renders this age raw, exactly
    like every other gauge-adjacent timestamp -- never a threshold judgment."""
    if observed_at is None:
        observed_at = datetime.now(timezone.utc).isoformat()
    record = {
        "schema_version": SCHEMA_VERSION,
        "reason": reason,
        "observed_at": observed_at,
    }
    if candidate_count is not None:
        record["candidate_count"] = candidate_count
    _atomic_write_json(_skip_path(gauge_path), record)


def _clear_skip_flag(gauge_path: Path) -> None:
    """Mirror _clear_uncalibrated_flag exactly: drop a stale skip sidecar once
    this path resolves to a real outcome again (a clean gauge.json write, or
    the uncalibrated-flag write -- both are called from the single-candidate
    branch below, the only place a path can go from 'skipped' to 'resolved').

    CLEARING SCOPE (decision:skip-sidecar-fanout-and-clear, cold-critic
    finding #1): only the path that is LATER resolved back to a single
    candidate ever gets cleared here. A candidate that drops out of an
    ambiguous binding set without ever again being the SOLE resolved
    candidate keeps a stale gauge-skip.json indefinitely -- there is no code
    path that revisits a former candidate this hook has no further reason to
    touch, so closing that gap would mean building cross-path bookkeeping
    (out of scope, decision:no-repair). This is an ACCEPTED, bounded
    residual: it self-heals the moment anyone actually resumes and drives
    that spine again (the very next single-candidate call clears/overwrites
    it), and while nobody resumes it, nobody is reading that spine's
    `current` either. checklist_engine.py's advisory always renders the
    flag's own age, never a threshold judgment on it, so even in the
    residual window a reader sees exactly how old the diagnosis is rather
    than trusting a silently-aging claim."""
    try:
        _skip_path(gauge_path).unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


# --- PostToolUse handler ------------------------------------------------------

def handle_post_tool_use(data: dict, project_dir: Path) -> dict:
    """Compute the record ONCE, then write it to the session's SOLE bound
    spine (#261, decision:gauge-write-skips-on-multiple-bindings -- supersedes
    #202's decision:gauge-write-fans-out-on-ambiguity). When two genuinely
    different top-level agents share one session_id (confirmed live: an
    Agent-tool-dispatched Commander and its own Admiral), find_latest_usage
    cannot tell whose activity produced the latest usage record -- fan-out
    doesn't fix that misattribution, it SPREADS the same wrong-source record
    to every spine the shared session_id happens to be bound to. So 2+
    candidates is treated as exactly the same kind of uncertainty the module
    already treats a missing binding as: skip-on-uncertainty, write NOTHING
    to gauge.json, for both the calibrated-record path and the uncalibrated-
    flag path. Only exactly one candidate ever gets a gauge.json/
    gauge-uncalibrated.json write.

    Two of the skip causes are now POSITIVELY LOCALIZED (issue #271) with a
    visible gauge-skip.json sidecar -- see _write_skip_flag's docstring for
    why this rides a SEPARATE sidecar family rather than reusing
    gauge-uncalibrated.json:
      - ambiguous binding (2+ candidates): unlike a gauge.json reading, a
        diagnostic fact about WHY nothing was written is never a fabricated/
        misattributed value, so fan-out carries none of the cross-write risk
        that killed fan-out for readings (#202/#261) -- written to EVERY
        candidate (decision:skip-sidecar-fanout-and-clear).
      - no-usable-record on the single resolved candidate: same treatment,
        one path.
    The other two causes stay silent by design -- there is no known gauge
    path to write a sidecar TO: zero candidates (unresolvable binding) and a
    missing/unreadable transcript_path (checked first, below, before
    gauge_paths is even resolved).

    NEVER raises; NEVER blocks; NEVER writes gauge.json/gauge-uncalibrated.json
    on uncertainty. Always returns {} (this hook never influences the tool
    call)."""
    try:
        transcript_path = data.get("transcript_path")
        if not transcript_path or not os.path.isfile(transcript_path):
            # No known gauge path yet (resolve_gauge_path hasn't even run) --
            # genuinely unlocatable, so this cause stays silent by design.
            return {}
        gauge_paths = resolve_gauge_path(project_dir, data.get("session_id"))
        if not gauge_paths:
            # Zero: unresolvable binding, no known gauge path to flag either.
            # Existing skip-on-uncertainty, unchanged.
            return {}
        if len(gauge_paths) > 1:
            # WHICH spine this reading belongs to is itself uncertain --
            # fabricating a gauge.json write to any of them (let alone all of
            # them) risks cross-writing a reading from an unrelated agent
            # sharing this session_id. But the AMBIGUITY ITSELF is a fact
            # every one of these candidates shares right now, so flag all N
            # (one shared observed_at for this one event).
            now_iso = datetime.now(timezone.utc).isoformat()
            for candidate in gauge_paths:
                _write_skip_flag(candidate, "ambiguous-binding",
                                  candidate_count=len(gauge_paths), observed_at=now_iso)
            return {}
        gauge_path = gauge_paths[0]
        record, uncalibrated = compute_record(transcript_path)
        if uncalibrated is not None:
            # No window for this model: raise the flag and leave gauge.json
            # exactly as it was. It ages into staleness naturally, which the
            # reader already collapses to "no reading" -- the correct
            # outcome. This IS a resolved outcome for this path, so clear any
            # stale skip flag left over from an earlier ambiguous/no-usable
            # call at this exact path.
            _write_uncalibrated_flag(gauge_path, uncalibrated)
            _clear_skip_flag(gauge_path)
            return {}
        if record is None:
            # Transcript exists and is readable, exactly one candidate, but
            # nothing usable was found in it -- the second positively-
            # localizable skip cause. Single path, no candidate_count.
            _write_skip_flag(gauge_path, "no-usable-record")
            return {}
        _atomic_write_json(gauge_path, record)
        _clear_uncalibrated_flag(gauge_path)
        _clear_skip_flag(gauge_path)
        return {}
    except Exception:
        return {}


# --- dispatch ----------------------------------------------------------------

def main(argv, stdin_text) -> int:
    """Single-purpose hook (PostToolUse only) -- no event-name dispatch is
    needed; the settings.json wiring registers this script for PostToolUse
    specifically (see docs/GAUGE_WRITER_HOOK.md). Always exits 0."""
    try:
        try:
            data = json.loads(stdin_text) if stdin_text and stdin_text.strip() else {}
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        project_dir = (
            _spine_rail.resolve_project_dir()
            if _spine_rail is not None
            else Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        )
        handle_post_tool_use(data, project_dir)
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        _stdin = sys.stdin.read()
    except Exception:
        _stdin = ""
    sys.exit(main(sys.argv, _stdin))
