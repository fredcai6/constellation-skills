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

import hashlib
import json
import re
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

# The top of the REPRESENTABLE fill range: the upper bound `_parse_fields`
# validates against below, and the value the writer's clamp in
# `gauge_writer_hook.compute_record` saturates at. Hoisted out of that range
# check so callers, tests and the engine refer to a NAME instead of re-typing
# the bound in a third place.
#
# THIS IS A DRIFT PIN, NOT A DERIVATION -- say it plainly rather than dressing
# it up. This module does not and must not import `gauge_writer_hook` (the
# reader ships bundled into every install; the harness-specific writer does
# not, and that portability seam is the whole point of the file format), so
# this side stays a TYPED LITERAL. What keeps it honest is a TEST that pins it
# to a value obtained by EXECUTING `compute_record()` against a saturating
# transcript -- structurally identical to the bargain `ModelTableSyncTests`
# already makes between `_PROFILES` and `MODEL_WINDOWS`. Only the test sees
# both modules.
#
# decision:no-threshold-values -- this is the top of the representable range,
# never a statement about how much context is acceptable. It must not become
# one.
FILL_CEILING = 1.0


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


def thresholds_for(model: str, headroom_tokens: float = 0) -> tuple[float, float]:
    """Return the (soft, hard) fill FRACTIONS for `model`, minus an optional
    absolute-token reserve.

    Converts the model's intent-first absolute caps to fractions against its own
    window (`soft_cap/window`, `hard_cap/window`) -- the same `(float, float)`
    shape Trip has always consumed. An unknown model falls back to
    `_DEFAULT_PROFILE` (fractions == DEFAULT_THRESHOLDS), so the caller always
    gets a usable pair, never a lookup failure.

    `headroom_tokens` (#467) is a caller-declared reserve of context a
    particular piece of work needs left over -- an ABSOLUTE token count, in the
    same unit as the caps, because context-rot degradation tracks absolute
    tokens rather than window fraction (see _PROFILES above). It comes off BOTH
    caps before the division, so a reserve tightens the soft and hard bands by
    the same absolute amount, and a 30K reserve means the same 30K of real room
    on a 1M model as on a 200K one.

    TIGHTEN-ONLY, and structurally so -- this is a safety property, not a style
    choice: an override that could RAISE a threshold would let a caller opt out
    of the governor entirely. Two clamps make loosening unreachable rather than
    merely untested:

      1. the reserve itself is clamped non-negative, so a negative (or hostile)
         value is a NO-OP that reproduces the shipped default exactly, never an
         addition to a cap;
      2. each reduced cap is clamped non-negative, so an absurdly large reserve
         floors the fraction at 0.0 (trip immediately -- the TIGHTEST possible
         setting) rather than going negative.

    Neither clamp can be satisfied by a value above the shipped cap, so for every
    input the returned pair is <= the un-overridden pair for that model.

    Still a TOTAL function under an override: an arbitrary model string yields a
    pair computed off `_DEFAULT_PROFILE`'s own window. That is NOT a reading-path
    fallback -- `read()` rejects a record whose model has no profile (#252), so
    an override can never be judged against a guessed window.
    """
    window, soft_cap, hard_cap = _PROFILES.get(model, _DEFAULT_PROFILE)
    reserve = max(0, headroom_tokens)
    return (max(0, soft_cap - reserve) / window, max(0, hard_cap - reserve) / window)


def implied_tokens(reading) -> int | None:
    """The ABSOLUTE token count `reading` implies, or None.

    `fill_fraction x window`, taking the window from this module's `_PROFILES`
    row for the reading's model. A DERIVED RENDERING, not a threshold: the
    precedent is `checklist_engine._format_age`, which renders whatever age it
    is handed and never decides anything. Nothing here states, or may ever
    state, how full is acceptable (decision:no-threshold-values).

    THE CONSTRAINT, STATED PLAINLY RATHER THAN PAPERED OVER: this reader
    CANNOT know the window the writer actually divided by. The gauge record is
    frozen at four fields and `decision:no-schema-change` forbids a fifth, so
    the writer's window has nowhere to travel. What comes back is therefore

        fill x READER_window

    -- this module's INTERPRETATION of the writer's fraction, not a
    measurement it received.

    That gap is not a defect to hide; it is exactly what makes a writer/reader
    window divergence VISIBLE. A fraction alone is unfalsifiable -- 0.69875
    looks like a perfectly ordinary reading. The same fraction rendered as an
    absolute count against a window a human knows is wrong on its face, with
    no recall of session size required: #252's 139,750 real tokens, divided by
    a wrongly-assumed 200K window, come back here as ~698,750 tokens on a
    `claude-opus-5` whose window is 1,000,000. A human noticing that number
    looked wrong is what ended those eight days.

    TOTAL and FAIL-SAFE, matching every other entry point in this module:
    anything unknown or malformed -- an object with no `fill_fraction`/`model`,
    a non-numeric or non-finite fill, a model with no profile -- returns None,
    and nothing raises. An uncalibrated model yields NO implied count rather
    than one computed against `_DEFAULT_PROFILE`, for the same reason `read()`
    rejects it outright (#252): an uncertain model must produce no number, not
    a wrong one.
    """
    fill = getattr(reading, "fill_fraction", None)
    model = getattr(reading, "model", None)
    if not isinstance(fill, (int, float)) or isinstance(fill, bool):
        return None
    if not isinstance(model, str):
        return None
    profile = _PROFILES.get(model)
    if profile is None:
        return None
    try:
        return round(profile[0] * float(fill))
    except (ValueError, OverflowError):
        # NaN/inf can't reach here through `read()` (the range check rejects
        # both), but this function is total over ANY object handed to it.
        return None


def pinned_at_ceiling(fill) -> bool:
    """A SECONDARY NOTICE: is this fill pinned at the top of the range?

    Deliberately NOT the headline, and never to be described as the answer to
    #264 -- `implied_tokens` above is that
    (decision:implied-tokens-over-ceiling-predicate). This predicate is silent
    across the entire range where a wrong window actually did its damage: it
    says nothing at 0.69875 (#252's real reading) or 0.126658 (#271's). And
    because every shipped profile has `hard_cap < window`, the engine's HARD
    band is entered at `hard_cap` tokens while this can only fire at `window`
    tokens -- far too late to prevent the wrongful block it would be reporting.

    EXACT REACH. `fill == FILL_CEILING` iff `tokens >= window`, because that is
    where the writer's clamp saturates. A live session cannot outgrow its real
    window -- the harness compacts first -- so a pinned reading is proof that
    the RATIO is wrong: the window too small OR the token count too large.

    EXACT LIMIT, both halves. (1) It CANNOT SAY WHICH. A double-counted
    numerator against a correct window arrives here as exactly the same pinned
    value as a correct numerator against a five-times-small window; the cause
    is not recoverable from the result. (2) It can NEVER PROVE A WINDOW RIGHT.
    An unpinned reading is consistent with every window large enough not to
    saturate, so silence here is not evidence of correct calibration.

    Compares with `>=` rather than `==` because this is total over any float a
    caller hands it; on a Reading that came through `_parse_fields` the two are
    identical, since that range check already rejects anything above the
    ceiling. Fail-safe like the rest of this module: a non-numeric `fill` is
    False, never an exception.
    """
    if not isinstance(fill, (int, float)) or isinstance(fill, bool):
        return False
    return float(fill) >= FILL_CEILING


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
    if not 0.0 <= float(fill_fraction) <= FILL_CEILING:
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


# --- who a reading BELONGS to (issue #600) ----------------------------------
#
# The gauge used to be one file per work DIRECTORY. Two agents whose spine files
# sit in one `.agent-work/<work_id>/` therefore wrote to one path and the last
# one won. Measured live, in a fresh process driving the real writer with two
# distinct binding keys bound into one work directory: an orchestrator's 0.9
# overwrote a dispatched agent's 0.02 and NOTHING noticed -- no sidecar, no
# guard. The writer's ambiguity guard enumerates candidates for ONE binding key,
# so it is WITHIN-key and structurally cannot see across keys; and the overwrite
# is FRESH, so #477/#601's `observed_at < claimed_at` comparison cannot see it
# either. Identity fixes the CONCURRENT case, time fixes the SEQUENTIAL relaunch
# case, and both are permanent (decision:identity-not-time, as amended).
#
# WHY THIS LIVES HERE, in the reader, and not in the writer. The key is computed
# on BOTH sides of a process boundary -- the harness hook composes it from the
# binding entry's `engine_session`, the engine composes it from its own active
# lease's `session_id`, and those are the same string by construction (the entry
# is parsed from `claim --session-id X` and the lease holds that same X). If the
# two sides ever disagreed by a character, every reading would silently stop
# resolving and the governor would go dark with no failing test anywhere. So
# there is ONE definition, and the harness-specific writer loads THIS module by
# path to reach it (decision:one-owner-key-definition). The dependency direction
# is deliberate and unchanged: the reader ships bundled into every install and
# still never imports the writer.

# The unowned name -- what a LEASELESS checklist still reads, exactly as it did
# before this change (R3). Owner-keying applies only where a lease exists: with
# no lease there is no owner, and going quiet there would be a real loss of
# coverage taken as a side effect of a rename. The fail-safe is "no ATTRIBUTABLE
# reading yields None"; it is not "no lease yields nothing".
GAUGE_FILENAME = "gauge.json"

# The slug is for humans reading a directory listing; the hash is what carries
# CORRECTNESS. The slug is lossy on purpose (case folded, separators collapsed,
# truncated) and the fleet's real lease names share long prefixes -- two of them
# in this checkout differ only at character 28 of 55 -- so a slug-only key would
# reintroduce exactly the collision this issue exists to remove. 12 hex
# characters of SHA-256 over the EXACT id is what makes two distinct sessions
# structurally unable to share a file.
_OWNER_SLUG_MAX = 32
_OWNER_HASH_CHARS = 12

# Characters safe to interpolate into a filename on every platform this repo
# runs on -- the same alphabet `spine_rail.is_usable_agent_id` reasons about for
# `agent-<id>.jsonl`. Read that function for the character-class reasoning; do
# NOT copy its REJECTION. Rejecting an id that falls outside the alphabet was
# the original proposal here and it is withdrawn (R2): 89 of the 426 distinct
# lease session ids in this checkout are slash-bearing, because slash-bearing
# lease names are current fleet practice, not a defect. Rejecting would take the
# governor away from a fifth of the fleet permanently and INVISIBLY -- losing
# the governor never shows up as a test failure, and this repo has been burned
# twice by a silent governor (#252, #271) and once by a wave-long dark one
# (#488). A normalization that is ugly and total beats an invariant that is
# clean and partial.
_OWNER_UNSAFE = re.compile(r"[^A-Za-z0-9_-]+")


def owner_key(session_id) -> str | None:
    """The owner key for an engine lease `session_id`: a slug plus a hash.

    TOTAL over every string input -- there is no such thing as a session id this
    function refuses. Returns None only when there is no id to key on at all (a
    non-string, or blank), which is not a rejection but the absence of an owner:
    the caller then uses the UNOWNED `GAUGE_FILENAME`, which is today's
    behaviour exactly. The live binding store carries `engine_session: null`
    entries and one holding the literal `'$SID'` from a shell-quoting bug; the
    first lands on the None branch, the second normalizes like any other string.

    `skip` and `uncalibrated` are RESERVED -- an owner named either would make
    `gauge-<owner>.json` collide with `SKIP_FILENAME`/`UNCALIBRATED_FILENAME`.
    They are unreachable STRUCTURALLY rather than by a check that could rot:
    every key ends in `-` plus 12 hex characters, and neither reserved word has
    that shape. `OwnerKeyNormalization` in tests/test_gauge_reader.py pins it.

    Stable across processes and runs by construction: SHA-256 of the exact id,
    with no salt, no clock, and no environment input.
    """
    if not isinstance(session_id, str):
        return None
    raw = session_id.strip()
    if not raw:
        return None
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:_OWNER_HASH_CHARS]
    # Lower-cased so the name is stable on case-insensitive filesystems; the
    # hash is taken over the ORIGINAL id, so two ids differing only in case
    # still get different files.
    slug = _OWNER_UNSAFE.sub("-", raw).strip("-_").lower()[:_OWNER_SLUG_MAX]
    slug = slug.strip("-_")
    return f"{slug}-{digest}" if slug else digest


def gauge_filename(owner: str | None) -> str:
    """The gauge file name for `owner`, or the unowned name when there is none.

    The one place the `gauge-<owner>.json` shape is composed, so the writer and
    the engine cannot spell it differently."""
    if not owner:
        return GAUGE_FILENAME
    return f"gauge-{owner}.json"


def record_owner(gauge_path: str | Path) -> str | None:
    """The `owner` the record at this path claims for itself, or None.

    The filename REMOVES the collision; this field makes a mismatch DETECTABLE
    if one ever reappears -- both, not either. A record whose stamped owner
    disagrees with the name it is sitting in can only be a bug, and a caller
    that notices should decline the reading rather than act on it (declining is
    always the quiet direction, never a new refusal).

    Field-shape validation only, and never raises -- the same fail-safe contract
    as `raw_record` and `skip_reason`. Records written before this field existed
    simply have no owner, which is None, which is not a mismatch."""
    try:
        record = json.loads(Path(gauge_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None
    owner = record.get("owner")
    if not isinstance(owner, str) or not owner.strip():
        return None
    return owner


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
