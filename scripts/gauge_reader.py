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

# The frozen gauge record has exactly these four fields -- no `source`, no
# `window` (both cut as YAGNI; `fill_fraction` is already normalized).
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

# Model-keyed fill thresholds (soft, hard), each in 0..1. Engine-side and
# central -- the writer never sees this table; Trip (#182) calls
# thresholds_for() to key policy off the model in the record.
#
# These are ABSOLUTE-token caps expressed as per-model fractions (fraction =
# cap / that model's real context window -- see gauge_writer_hook.MODEL_WINDOWS).
# Context-rot research (2026-07-19, see .agent-work/epic-178/crew-handoffs/
# context-rot-research.md) found degradation is driven by ABSOLUTE token count,
# not window fraction: onset clusters ~32-100K tokens regardless of advertised
# window, and agentic/reasoning work degrades earliest. So a 1M model is usable
# to a LOWER fraction than a 200K one, and the caps collapse to small fractions
# on 1M models. Caps: SOFT ~= min(0.5*window, ~80-100K); HARD ~= min(0.7*window,
# ~150K), agentic-shaded. Human-approved starting points (Fred, 2026-07-19);
# v1-experimental -- tune from observed gauge fill. A v2 could store the literal
# absolute cap + convert by window so a new model needs no hand-recomputed
# fraction (follow-up).
_THRESHOLDS: dict[str, tuple[float, float]] = {
    # 1M-window models: ~80K soft / ~150K hard, as a fraction of 1_000_000.
    "claude-opus-4-8": (0.08, 0.15),
    "claude-sonnet-5": (0.08, 0.15),
    "claude-fable-5": (0.08, 0.15),
    # 200K-window model: ~90K soft / ~140K hard, as a fraction of 200_000
    # (here the classic ~0.5/0.75 fraction guess roughly survives).
    "claude-haiku-4-5-20251001": (0.45, 0.70),
}
# Unknown model -> conservative pair. gauge_writer's DEFAULT_WINDOW assumes 200K
# for an unknown model, so read the default against that profile but slightly
# tighter (hand off a touch earlier when we don't know the model).
DEFAULT_THRESHOLDS: tuple[float, float] = (0.40, 0.65)


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
    """Return the (soft, hard) fill thresholds for `model`.

    An unknown model falls back to DEFAULT_THRESHOLDS -- the caller always
    gets a usable pair, never a lookup failure.
    """
    return _THRESHOLDS.get(model, DEFAULT_THRESHOLDS)


def _parse_record(record: dict, now: datetime, max_age: timedelta) -> Reading | None:
    """Validate an already-decoded record dict and convert it to a Reading.

    Never raises: any problem -- missing field, wrong type, out-of-range
    value, stale timestamp, clock-skew -- returns None.
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
    if not isinstance(observed_at_raw, str):
        return None

    try:
        observed_at = datetime.fromisoformat(observed_at_raw)
    except ValueError:
        return None
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)

    age = now - observed_at
    if age > max_age:
        return None  # stale
    if age < -CLOCK_SKEW_TOLERANCE:
        return None  # observed_at too far in the future -- clock skew

    return Reading(
        schema_version=schema_version,
        fill_fraction=float(fill_fraction),
        model=model,
        observed_at=observed_at,
    )


def read(
    path: str | Path,
    *,
    now: datetime | None = None,
    max_age: timedelta = DEFAULT_MAX_AGE,
) -> Reading | None:
    """Read the gauge file at `path` and return a fresh Reading, or None.

    Collapses every failure to None and never raises: an absent file, corrupt
    JSON, a malformed/missing-field record, a stale record (by `observed_at`),
    and clock-skew (observed_at in the future beyond tolerance) all return
    None.

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
