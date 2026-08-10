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
- Record is four REQUIRED fields (identical to #181's reader):
  {schema_version: int, fill_fraction: float 0..1, model: str,
  observed_at: ISO-8601 str -- the SAMPLED moment, not write time},
  plus ONE optional fifth on the dispatched-agent path only (#419):
  {identity_resolution_ms: float}. A top-level agent's record still
  carries exactly the four, byte-identical to before #419. The reader
  validates the four and does not reject extras, which is what makes an
  additive field free on the read side.
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
- The reading belongs to the AGENT THAT PRODUCED IT (#419). Agent-tool
  subagents share their parent's `session_id`, and their tool calls carry
  the PARENT's `transcript_path`, but the harness hands the acting agent's
  own `agent_id` over directly. So: the binding is keyed on
  `spine_rail.binding_key(payload)` (`session_id#agent_id` for a dispatched
  agent, the bare `session_id` for a top-level one), and the agent's own
  transcript is DERIVED from that id, never searched for. For a dispatched
  agent the sidechain polarity INVERTS -- every line of its own transcript
  is `isSidechain: true` -- and the line's `agentId` must equal the payload's.
  There is NO fallback to the parent's transcript: an absent derived
  transcript writes a `subagent-transcript-missing` skip and nothing else.
  Silence is an acceptable outcome; a confident wrong number is not.
- Stdlib only. Windows-friendly: UTF-8 I/O, native paths, no /tmp literals.
"""

import importlib.util
import json
import os
import re
import sys
import time
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


# --- the acting agent's identity, and the transcript derived from it --------

# An ALLOWLIST, deliberately not an extension of spine_rail's denylist. That
# denylist (`#`, `/`, `\`, `..`) is hand-maintained and still admits `:`, `*`
# and `?` -- and unlike spine_rail, which only ever uses agent_id as a dict
# KEY, this module interpolates it into `agent-{agent_id}.jsonl`, a real
# filesystem path on a Windows box. A denylist of path metacharacters is a
# list that drifts from the predicate the filesystem actually applies; the
# allowlist is defined by the ids the harness genuinely sends (measured live
# on 2.1.222: hex-ish tokens such as `a8f0a946eaaa2fe6c`), widened only to `-`
# and `_`. A value outside it means WRITE NOTHING -- never a repaired or
# sanitized path, and never an exception the outer swallow would flatten into
# the same indistinguishable silence every other failure produces.
_AGENT_ID_ALLOWED = re.compile(r"\A[A-Za-z0-9_-]{1,64}\Z")


def _is_usable_agent_id(agent_id) -> bool:
    return isinstance(agent_id, str) and _AGENT_ID_ALLOWED.match(agent_id) is not None


def derive_subagent_transcript(transcript_path, agent_id):
    """The ACTING agent's own transcript, derived from the payload:
    `<parent transcript minus .jsonl>/subagents/agent-<agent_id>.jsonl`.

    Derived, never searched for. The harness hands over `agent_id` directly,
    so resolving WHO is an O(1) payload lookup and this path follows from it
    by construction -- which is why the identical-command race a search-based
    identity would have to defend against cannot arise here at all. The shape
    was confirmed on disk for both agents of a live two-subagent probe.

    Returns None -- never a repaired path -- when the id fails
    `_is_usable_agent_id` or the parent path is unusable."""
    try:
        if not transcript_path or not _is_usable_agent_id(agent_id):
            return None
        parent = Path(transcript_path)
        return parent.with_suffix("") / "subagents" / "agent-{aid}.jsonl".format(aid=agent_id)
    except Exception:
        return None


def _binding_key(data: dict):
    """This payload's outer binding key, or None to write NOTHING.

    Thin on purpose: `spine_rail.binding_key` is the single place the
    composite `session_id#agent_id` key is composed anywhere in the codebase
    (#419 g1), and this module CALLS it rather than reimplementing it, so the
    two hooks cannot drift.

    What this adds is the `_spine_rail is None` guard, moved OUT here with the
    call. `_load_spine_rail` returns None on any import failure; leaving the
    guard behind in `resolve_gauge_path` would strand it, and an unguarded
    `_spine_rail.binding_key(...)` would raise into `handle_post_tool_use`'s
    outer `except` -- silence with zero diagnostic, wearing exactly the same
    symptom as every other silence this module works to keep distinguishable.

    It also applies THIS module's stricter `_is_usable_agent_id` allowlist
    before delegating, so an id spine_rail admits but this module could not
    safely put in a path resolves to None -- write nothing -- rather than
    reaching the `agent-{agent_id}.jsonl` interpolation.

    Deliberately carries NO try/except of its own: `binding_key` already
    swallows internally, and a bare helper makes the guard directly
    observable in a test instead of being absorbed one frame up."""
    if _spine_rail is None:
        return None
    if "agent_id" in (data or {}) and not _is_usable_agent_id((data or {}).get("agent_id")):
        return None
    return _spine_rail.binding_key(data)


def resolve_gauge_path(project_dir: Path, binding_key):
    """`.agent-work/<work_id>/gauge.json` for EVERY DISTINCT gauge path this
    BINDING KEY is currently bound to (#202: one key can hold N distinct spine
    bindings at once) -- a list of Path, possibly empty. Each candidate is
    individually checked against `_is_contained`; a candidate that fails the
    fence is dropped rather than failing the whole call, so one bad entry
    never blinds the write for the key's other, legitimate bindings.

    DEDUPED by resolved gauge path, not counted by binding (#488). Two
    bindings are two spine FILES, not necessarily two work areas: an Admiral's
    own spine and the `latitude` survey its spine step requires it to drive
    both live in one work directory (`spine.json` + `latitude-interrogation.json`
    under the same `.agent-work/<work_id>/`) and resolve to the identical
    gauge.json. The caller below treats 2+ candidates as ambiguous and skips
    the write entirely -- correct when two candidates might belong to two
    different agents sharing a session_id (#261's real protection), vacuous
    when they are the same file: there is no whose-reading-is-it question when
    either answer writes to one place. Measured live: this undeduped version
    left an Admiral's own governor dark for an entire wave (#488). Order is
    preserved (first-seen wins) so behaviour stays deterministic across calls
    with the same binding contents; genuinely different gauge paths still
    yield 2+ candidates here, so the caller's ambiguous-binding skip still
    fires for that case exactly as before.

    The key is `_binding_key(payload)`, NOT the bare `session_id` (#419):
    Agent-tool subagents share their parent's session_id, so a session-keyed
    lookup piled every crew claim under one key and left this writer with 2+
    candidates and no way to tell whose reading it held -- so it wrote nothing,
    for exactly the runs an orchestrator dispatches. A dispatched agent is
    keyed `session_id#agent_id`; a top-level agent keeps the bare session_id.

    Empty list if unresolvable (no sibling module, no key, no binding at all)
    -- skip-on-uncertainty applies to WHERE we write, not just to what."""
    try:
        if _spine_rail is None or not binding_key:
            return []
        binding = _spine_rail.load_binding(project_dir)
        sid_bindings = binding.get(binding_key) or {}
        candidates = []
        for entry in sid_bindings.values():
            spine_path = entry.get("spine") if isinstance(entry, dict) else None
            if not spine_path:
                continue
            candidate = Path(spine_path).parent / "gauge.json"
            if _is_contained(candidate) and candidate not in candidates:
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


def find_latest_usage(transcript_path, agent_id=None):
    """Scan the transcript tail for the most recent assistant message carrying
    a usage record. Returns (model, total_tokens, observed_at), or None if
    nothing usable is found in the scanned window.

    `agent_id` INVERTS the sidechain polarity, and it is deliberately ONE
    parameter rather than an `expect_sidechain` + `expect_agent_id` pair:
    "this is agent X's own transcript" is a single fact, and a pair would let
    a caller set an incoherent combination.

    - `None` (a top-level agent): today's filter exactly -- skip anything
      `isSidechain` truthy, because a subagent's turns are a different context
      window entirely.
    - set (a dispatched agent, reading its OWN derived transcript): the line
      must be `isSidechain` TRUTHY *and* carry a top-level `agentId` EQUAL to
      it. Every line of a subagent's own transcript is `isSidechain: true`
      (measured; docs/GAUGE_WRITER_HOOK.md's field table states both
      polarities), so the polarity has to flip; the `agentId` equality is what
      makes a WRONG derived path fail closed rather than produce a confidently
      misattributed number.
    """
    try:
        for line in _iter_tail_lines_reverse(transcript_path):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") != "assistant":
                continue
            if agent_id is None:
                if d.get("isSidechain"):
                    continue
            elif not d.get("isSidechain") or d.get("agentId") != agent_id:
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


def compute_record(transcript_path, agent_id=None):
    """Build the four required fields of the record for this transcript.

    Four is what THIS function returns, always. The optional fifth field
    `identity_resolution_ms` is added by `handle_post_tool_use` on the
    dispatched-agent path only -- see the module docstring.

    `agent_id` is forwarded verbatim to `find_latest_usage` -- see there for
    what it does to the sidechain polarity. One parameter, not two.

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
        found = find_latest_usage(transcript_path, agent_id)
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

# A SIDECAR, deliberately not a field on gauge.json: that record's four
# required fields are shared with the reader, and "no reading" must stay
# literally no reading so every existing fail-safe path keeps working
# untouched -- an uncalibrated model has no fill to report at all, which is a
# different thing from #419's additive fifth field riding a real reading.
# The flag rides alongside so the engine can explain the silence instead of
# the governor just going quiet -- an unexplained silent governor is how a
# miscalibration survives unnoticed, which is exactly what happened with
# claude-opus-5.
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

    THREE of the skip causes are now POSITIVELY LOCALIZED with a visible
    gauge-skip.json sidecar (two from issue #271, plus
    subagent-transcript-missing from #419) -- see _write_skip_flag's docstring
    for why this rides a SEPARATE sidecar family rather than reusing
    gauge-uncalibrated.json:
      - ambiguous binding (2+ candidates): unlike a gauge.json reading, a
        diagnostic fact about WHY nothing was written is never a fabricated/
        misattributed value, so fan-out carries none of the cross-write risk
        that killed fan-out for readings (#202/#261) -- written to EVERY
        candidate (decision:skip-sidecar-fanout-and-clear).
      - no-usable-record on the single resolved candidate: same treatment,
        one path.
      - subagent-transcript-missing: agent_id resolved but its derived
        transcript is absent. Fails closed -- never the parent's transcript.
    The other causes stay silent by design -- there is no known gauge path to
    write a sidecar TO: zero candidates (unresolvable binding, which now also
    covers a subagent whose identity would not compose a key) and a
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
        # Identity resolution is measured, not assumed (#419): the harness
        # hands `agent_id` over directly, so resolving WHO is an O(1) payload
        # lookup and the acting agent's transcript follows from it by
        # construction -- but "should be fast" is not evidence. Accumulated
        # across the two identity steps (key composition, transcript
        # derivation) and reported on the record. The binding-store read
        # between them is binding resolution, a pre-existing cost, and is
        # deliberately NOT counted.
        identity_ms = 0.0
        _t0 = time.perf_counter()
        key = _binding_key(data)
        identity_ms += (time.perf_counter() - _t0) * 1000.0
        if key is None:
            # Unresolvable acting identity (#419). NOT a fallback to the bare
            # session_id: that would file a subagent's reading under the
            # PARENT's key -- the same misattribution this keying exists to
            # remove, just wearing a different hat. Fail closed, write nothing.
            return {}
        gauge_paths = resolve_gauge_path(project_dir, key)
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
        acting_agent_id = data.get("agent_id") if "agent_id" in data else None
        if acting_agent_id is None:
            read_path = transcript_path
        else:
            # #419 FAIL CLOSED. The payload's transcript_path is the PARENT's
            # transcript, always (measured live on 2.1.222) -- so for a
            # dispatched agent the reading comes from the DERIVED transcript
            # and only from it. There is deliberately no fallback to the
            # parent: that is precisely the misattribution #202/#261 already
            # tried and reverted, where spreading one agent's reading into an
            # unrelated agent's work area was worse than silence. Read the
            # module docstring above for that history.
            _t1 = time.perf_counter()
            read_path = derive_subagent_transcript(transcript_path, acting_agent_id)
            unresolved = read_path is None or not os.path.isfile(read_path)
            identity_ms += (time.perf_counter() - _t1) * 1000.0
            if unresolved:
                # A third positively-localized skip cause. gauge_reader's
                # skip_reason does not whitelist reason strings and the
                # engine's advisory renders an unrecognized one verbatim, so
                # this costs zero change on the reading side.
                _write_skip_flag(gauge_path, "subagent-transcript-missing")
                return {}
        record, uncalibrated = compute_record(read_path, acting_agent_id)
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
        if acting_agent_id is not None:
            # An OPTIONAL FIFTH field, additive only. gauge_reader validates
            # the presence of its four required fields and does not reject
            # extras, so this costs no reader change. It rides ONLY the
            # dispatched-agent path: a payload with no agent_id must stay
            # byte-identical to before this change, and there is no identity
            # to resolve for a top-level agent anyway. The four required
            # fields keep their meaning untouched.
            record = dict(record)
            record["identity_resolution_ms"] = identity_ms
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
