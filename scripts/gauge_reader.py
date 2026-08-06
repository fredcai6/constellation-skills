#!/usr/bin/env python
"""Gauge reader -- fail-safe read of the context-fullness gauge file.

Module 2 (read side) of the Context Governor (epic-178). A harness-specific
writer (issue #180) drops a small JSON record at
`.agent-work/<work_id>/gauge.json` on every tool call; the Trip policy (issue
#182) reads it at each gate through `read()` below. The file format is the
whole portability seam -- this reader never branches on which harness wrote
it, and it never raises: every failure mode (absent file, corrupt JSON,
malformed record, stale-by-`observed_at`, clock-skew) collapses to a single
`None`. A `Reading` that reaches the caller is fresh and well-formed by
construction, so a caller structurally cannot act on stale or bad data.

See the epic-178 DESIGN_SPEC ("2. Gauge") for the full rationale.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# The gauge record's four REQUIRED fields -- no `source`, no `window` (both cut
# as YAGNI; `fill_fraction` is already normalized). "Required", not "the whole
# record": this reader checks these four are present and does NOT reject extras,
# which is what lets the writer add the optional `identity_resolution_ms` on a
# dispatched agent's record (#419) without touching this module. A record with
# only these four is still exactly what a top-level agent produces.
REQUIRED_FIELDS = ("schema_version", "fill_fraction", "model", "observed_at")

# Staleness is resolved from the embedded `observed_at`, never file mtime --
# that survives copy/sync and cross-machine clock skew. This default is a
# placeholder; first-run-calibration TBD.
DEFAULT_MAX_AGE = timedelta(minutes=30)

# `observed_at` may lag `now` by up to `max_age`, but it should not lead `now`
# by much -- a future timestamp means the writer's and reader's clocks
# disagree, not that the gauge is extra fresh. This tolerance absorbs ordinary
# clock skew without letting a bad clock manufacture a reading.
CLOCK_SKEW_TOLERANCE = timedelta(minutes=2)

# Model-keyed fill thresholds. Engine-side and central -- the writer never sees
# this table; Trip (#182) calls thresholds_for() to key policy off the model in
# the record.
#
# Representation is INTENT-FIRST: each model carries its own ABSOLUTE-token caps
# alongside the single source of that model's real context window --
# `(window, soft_cap, hard_cap)`, all ints in tokens. thresholds_for() divides
# the caps by the window to hand Trip the same `(soft, hard)` FRACTIONS it always
# consumed, so this is a pure representation refactor: no trip point moves.
#
# Why absolute caps are the real knob: context-rot research (2026-07-19, see
# .agent-work/epic-178/crew-handoffs/context-rot-research.md) found degradation
# is driven by ABSOLUTE token count, not window fraction -- onset clusters
# ~32-100K tokens regardless of advertised window, and agentic/reasoning work
# degrades earliest. So a 1M model is usable to a LOWER fraction than a 200K one,
# and the caps collapse to small fractions on 1M models. Storing the cap + window
# (not a hand-recomputed fraction) means a new model needs only its real window
# and caps -- the fraction falls out by division, with the window stated once.
# The reader carries its OWN window column and never imports the writer hook, so
# the read side stays writer-agnostic.
#
# Caps below are human-approved starting points (Fred, 2026-07-19), agentic-shaded
# (SOFT ~= min(~0.5*window, ~80-100K); HARD ~= min(~0.7*window, ~150K)); v1-
# experimental -- tune from observed gauge fill.
#
# FUTURE MEASUREMENT (open questions to resolve from first-run gauge data, per the
# context-rot research): (1) does the absolute degradation band shift up for the
# newest 1M frontier models or stay pinned ~32-100K? (2) the real agentic handoff
# curve (tool-call chains, scratchpad state) is unmeasured; (3) does context
# hygiene (relevant working state vs. stale tool output) push the usable fraction
# higher? (4) should HARD trigger on a degradation SIGNAL (self-consistency / probe
# drop) rather than a static token count? -- prose pointer only; no measurement
# machinery lives here.
_PROFILES: dict[str, tuple[int, int, int]] = {
    # model: (window, soft_cap, hard_cap), all in tokens.
    # Windows verified against platform.claude.com "Models overview", 2026-07-25.
    # Adding a model here means adding it to gauge_writer_hook.MODEL_WINDOWS in
    # the same change; a test pins the two key sets equal.
    # 1M-window models: 80K soft / 150K hard of 1_000_000 -> 0.08 / 0.15.
    "claude-opus-5": (1_000_000, 80_000, 150_000),
    "claude-opus-4-8": (1_000_000, 80_000, 150_000),
    "claude-sonnet-5": (1_000_000, 80_000, 150_000),
    "claude-fable-5": (1_000_000, 80_000, 150_000),
    # 200K-window model: 90K soft / 140K hard of 200_000 -> 0.45 / 0.70
    # (here the classic ~0.5/0.75 fraction guess roughly survives).
    "claude-haiku-4-5-20251001": (200_000, 90_000, 140_000),
}
# Unknown-model profile. NOTE: this is no longer reachable from a real reading --
# `read()` rejects a record whose model has no profile, and the writer no longer
# fabricates one either (both changed in #252, after an uncalibrated
# claude-opus-5 read ~5x high and tripped the governor at ~14% of its real
# window). It survives only to keep `thresholds_for` a TOTAL function, so a
# caller that asks about an arbitrary model string still gets a usable pair
# rather than a lookup failure. Do NOT reintroduce it as a fallback on the
# reading path: an uncertain model must yield no reading, not a wrong one.
_DEFAULT_PROFILE: tuple[int, int, int] = (200_000, 80_000, 130_000)

# Public fraction pair for the default profile, kept under its historical name so
# callers, tests, and the thresholds_for docstring can reference it directly.
# Computed once from _DEFAULT_PROFILE == (0.40, 0.65) -- do NOT repurpose this
# name to hold absolute caps.
DEFAULT_THRESHOLDS: tuple[float, float] = (
    _DEFAULT_PROFILE[1] / _DEFAULT_PROFILE[0],
    _DEFAULT_PROFILE[2] / _DEFAULT_PROFILE[0],
)


@dataclass(frozen=True)
class Reading:
    """A fresh, well-formed gauge sample.

    Reaching the caller means: parsed, complete, and not stale -- staleness is
    resolved inside the reader, never left for the caller to judge.
    """

    schema_version: int
    fill_fraction: float
    model: str
    observed_at: datetime


def thresholds_for(model: str) -> tuple[float, float]:
    """Return the (soft, hard) fill FRACTIONS for `model`.

    Converts the model's intent-first absolute caps to fractions against its own
    window (`soft_cap/window`, `hard_cap/window`) -- the same `(float, float)`
    shape Trip has always consumed. An unknown model falls back to
    `_DEFAULT_PROFILE` (fractions == DEFAULT_THRESHOLDS), so the caller always
    gets a usable pair, never a lookup failure.
    """
    window, soft_cap, hard_cap = _PROFILES.get(model, _DEFAULT_PROFILE)
    return (soft_cap / window, hard_cap / window)


def _parse_observed_at(raw_value) -> datetime | None:
    """Parse an `observed_at` value into a tz-aware datetime, or None if it
    isn't a well-formed ISO-8601 string. A naive timestamp is assumed UTC --
    the same convention `_parse_fields` and `_parse_record` have always used.
    Shared by `_parse_fields` (the record's `observed_at` field) and
    `skip_reason` (the sidecar's own `observed_at` field) so this parse-and-
    assume-UTC logic lives in exactly one place."""
    if not isinstance(raw_value, str):
        return None
    try:
        observed_at = datetime.fromisoformat(raw_value)
    except ValueError:
        return None
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    return observed_at


def _parse_fields(record: dict) -> Reading | None:
    """Validate an already-decoded record dict's required fields, types, and
    range, and convert it to a Reading -- WITH NO staleness, clock-skew, or
    calibration-table gate. Never raises: any problem -- missing field, wrong
    type, out-of-range value -- returns None.

    This is the field-shape half of what `_parse_record` used to do inline.
    It is shared by `_parse_record` (which layers staleness/skew/calibration
    on top of the Reading this returns) and `raw_record` (which reports the
    Reading's fields as-is, with nothing layered on top) -- one place for the
    required-fields/types/range checks, so the two callers cannot drift.
    """
    for field in REQUIRED_FIELDS:
        if field not in record:
            return None

    schema_version = record["schema_version"]
    fill_fraction = record["fill_fraction"]
    model = record["model"]
    observed_at_raw = record["observed_at"]

    # bool is a subclass of int in Python -- exclude it explicitly so a
    # stray `true`/`false` in the JSON doesn't pass as a schema_version.
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        return None
    if not isinstance(fill_fraction, (int, float)) or isinstance(fill_fraction, bool):
        return None
    if not 0.0 <= float(fill_fraction) <= 1.0:
        return None
    if not isinstance(model, str):
        return None

    observed_at = _parse_observed_at(observed_at_raw)
    if observed_at is None:
        return None

    return Reading(
        schema_version=schema_version,
        fill_fraction=float(fill_fraction),
        model=model,
        observed_at=observed_at,
    )


def _parse_record(record: dict, now: datetime, max_age: timedelta) -> Reading | None:
    """Validate an already-decoded record dict and convert it to a Reading.

    Never raises: any problem -- missing field, wrong type, out-of-range
    value, stale timestamp, clock-skew -- returns None.
    """
    reading = _parse_fields(record)
    if reading is None:
        return None

    age = now - reading.observed_at
    if age > max_age:
        return None  # stale
    if age < -CLOCK_SKEW_TOLERANCE:
        return None  # observed_at too far in the future -- clock skew

    # UNCALIBRATED -> no reading. A fill_fraction is only meaningful against the
    # window it was divided by, and this module's thresholds are what supply
    # that meaning. A model with no profile here means we cannot interpret the
    # number, so we must not hand Trip a Reading it will judge against the
    # wrong scale. The current writer never emits such a record, so in practice
    # this catches a stale file written before a model was added, or one copied
    # in from another machine -- defense in depth, not the primary guard.
    if reading.model not in _PROFILES:
        return None

    return reading


def read(
    path: str | Path,
    *,
    now: datetime | None = None,
    max_age: timedelta = DEFAULT_MAX_AGE,
) -> Reading | None:
    """Read the gauge file at `path` and return a fresh Reading, or None.

    Collapses every failure to None and never raises: an absent file, corrupt
    JSON, a malformed/missing-field record, a stale record (by `observed_at`),
    clock-skew (observed_at in the future beyond tolerance), and a record for a
    model with no entry in `_PROFILES` all return None. A Reading that reaches
    the caller is therefore fresh, well-formed, AND calibrated -- so the
    thresholds it is judged against are the real ones for its model.

    `now` and `max_age` are injectable so callers -- and tests -- never touch
    the real wall clock: `now` defaults to `datetime.now(timezone.utc)` when
    omitted, and `max_age` defaults to DEFAULT_MAX_AGE but can be overridden
    per call (e.g. by engine config).
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        # A caller-supplied naive `now` (e.g. `datetime.now()`) must not
        # reach the subtraction in _parse_record -- that would raise on
        # every well-formed record, exactly the crash this reader exists to
        # avoid. Assume UTC, same as a naive `observed_at`.
        now = now.replace(tzinfo=timezone.utc)

    try:
        raw = Path(path).read_text(encoding="utf-8")
        record = json.loads(raw)
    except (OSError, ValueError):
        return None

    if not isinstance(record, dict):
        return None

    return _parse_record(record, now, max_age)


def raw_record(gauge_path: str | Path) -> dict | None:
    """The gauge file's own facts -- `fill_fraction`, `model`, `observed_at`
    (a parsed, tz-aware datetime) -- with field-shape validation ONLY. NO
    staleness check, NO clock-skew check, NO calibration-table check: this is
    a raw report, not a judgment.

    Exists for exactly one caller-facing purpose: when `read()` itself
    rejects the file at this path (e.g. it is simply too old), this is the
    one remaining honest thing to say about it -- the file's last recorded
    numbers, displayed as-is, so a frozen `gauge.json` is never silently
    mistaken for a fresh low reading. A caller must render these facts raw
    (age included) and must not re-derive a soft/hard verdict from them --
    that verdict is exactly what `read()` already declined to give.

    Never raises: any problem -- absent file, corrupt JSON, missing/
    malformed fields -- returns None, same fail-safe contract as `read()`.
    """
    try:
        raw = Path(gauge_path).read_text(encoding="utf-8")
        record = json.loads(raw)
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None

    reading = _parse_fields(record)
    if reading is None:
        return None

    return {
        "fill_fraction": reading.fill_fraction,
        "model": reading.model,
        "observed_at": reading.observed_at,
    }


# Sidecar written by the harness hook when it sees a model it has no window for
# (gauge_writer_hook.UNCALIBRATED_FILENAME). Kept as a literal rather than an
# import: this module stays writer-agnostic by design and must not depend on a
# harness-specific hook. The filename is the seam.
UNCALIBRATED_FILENAME = "gauge-uncalibrated.json"

# Sidecar written by the harness hook when it POSITIVELY LOCALIZES why no
# reading could be written at a gauge path -- ambiguous session->spine
# binding, or a transcript with no usable usage record (issue #271,
# gauge_writer_hook.SKIP_FILENAME). Kept as a literal for the same
# writer-agnostic reason as UNCALIBRATED_FILENAME above.
SKIP_FILENAME = "gauge-skip.json"


def skip_reason(gauge_path: str | Path) -> dict | None:
    """Why the writer hook wrote NO reading at this gauge path, if it knows --
    mirrors `uncalibrated_model`'s fail-safe contract exactly: never raises,
    any problem (absent file, corrupt JSON, missing/malformed fields) is None.

    Returns `{"reason": str, "observed_at": datetime, "candidate_count": int}`
    -- `candidate_count` only present when the source file carries it as a
    valid non-bool int (it only applies to the ambiguous-binding reason).
    `observed_at` is parsed the same way `_parse_fields` parses a gauge
    record's own `observed_at`.

    Deliberately NOT staleness-checked, same rationale as `raw_record`: this
    answers "why is there no reading", which a caller displays with its own
    raw age, never a pass/fail this function decides."""
    try:
        path = Path(gauge_path).with_name(SKIP_FILENAME)
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None

    reason = record.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return None

    observed_at = _parse_observed_at(record.get("observed_at"))
    if observed_at is None:
        return None

    result = {"reason": reason, "observed_at": observed_at}
    candidate_count = record.get("candidate_count")
    if isinstance(candidate_count, int) and not isinstance(candidate_count, bool):
        result["candidate_count"] = candidate_count
    return result


def uncalibrated_model(gauge_path: str | Path) -> str | None:
    """The model name the writer could not calibrate, or None.

    Answers "why is there no reading?" so a caller can say so out loud instead
    of going silently quiet -- an unexplained silent governor is how a
    miscalibration survives unnoticed. Never raises; any problem is None.

    Deliberately NOT staleness-checked: an uncalibrated model is a defect in
    this repo's tables, not a perishable observation, and it stays true until
    someone adds the row. Staleness would let the warning expire while the bug
    it reports is still live."""
    try:
        path = Path(gauge_path).with_name(UNCALIBRATED_FILENAME)
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None
    model = record.get("model")
    if not isinstance(model, str) or not model.strip():
        return None
    # A row added since the flag was written makes it obsolete; don't nag.
    if model in _PROFILES:
        return None
    return model
