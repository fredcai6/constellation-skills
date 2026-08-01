#!/usr/bin/env python
"""Deterministically apply structured episode-delta operations to the episode store.

The LLM proposes operations (create/amend-assertion/retire) in a JSON delta file; this
script validates every op and applies them mechanically, all-or-nothing: any invalid op
anywhere in the delta rejects the WHOLE delta and leaves the store byte-for-byte
unchanged. The LLM never writes an episode file directly — this script is the only
write path into episodes/.

Mirrors scripts/apply_lessons_delta.py's contract (validate-then-apply, all-or-nothing,
retire-requires-reason, "- field: value" grammar) but is NOT the same store: see
docs/EPISODE_STORE.md for the full contract this writer implements, and its section 7
in particular for why the retirement-layout question is a genuinely open seam, not
settled here.

Op vocabulary (this script's own choice — not fixed by EPISODE_STORE.md, which only
fixes the record grammar and the store's obligations):

  create           — mint a new episode. The id is ASSIGNED BY THIS WRITER (run+sequence
                     scan, EPISODE_STORE.md section 2), never supplied by the delta —
                     that is the "zero agent effort" property the doc argues for. All
                     five agent-supplied kinds are required; diagnosis is optional.
  amend-assertion  — dispute exactly ONE named assertion (agent-supplied or diagnosis):
                     changes only its lifecycle-standing and appends one history line.
                     Every sibling field, in this assertion and every other, is
                     untouched (EPISODE_STORE.md section 5).
  retire           — mark an episode excluded from ordinary search, RETAINED in history,
                     with a mandatory non-empty reason. Never touches any assertion's own
                     lifecycle-standing (EPISODE_STORE.md section 7). Routes its
                     layout-dependent effect through apply_retirement() alone.

Determinism: same delta + same starting state -> same bytes. This writer never calls
date.today() or any other wall-clock source — every free-text value that would carry a
"when" (a retire's retired-at, a dispute's history line) must be supplied BY THE DELTA,
not generated here. (apply_lessons_delta.py stamps its own dates; this store departs
from that on purpose — see the g2 handoff's determinism constraint.)

Newline handling (Windows hazard, named explicitly): every read and write in this module
passes newline="" to disable Python's own universal-newline translation, so a `\r\n` in
an existing file is preserved as literal CRLF bytes during parsing (never silently
folded to `\n`, which would corrupt a byte-for-byte-unchanged comparison), and every
write emits LF-only line endings on every platform, including Windows. Combined with the
newline-injection guard (which rejects any delta value containing a literal `\n` or `\r`
before it is ever rendered), this keeps the store's bytes fully deterministic regardless
of which OS produced them.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


# --- the record's fixed vocabulary (EPISODE_STORE.md sections 2-4) ---------------

ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*-[0-9]{3,}")
RUN_RE = re.compile(r"[a-z0-9][a-z0-9-]*")

# Mechanical bin allowlist (section 4). artifact-ref is repeated/list-shaped; every
# other mechanical field is a scalar. This is the ONE place a mechanical field name is
# recognized — a delta key outside this set (e.g. an agent-supplied concept like
# lifecycle-standing) is rejected as misfiled, never silently rendered.
MECHANICAL_SCALAR_FIELDS = (
    "run",
    "project",
    "role",
    "spine-step",
    "context-manifest-ref",
    "refusals",
    "reopens",
    "rework-count",
    "failed-commands",
)
MECHANICAL_INT_FIELDS = ("refusals", "reopens", "rework-count", "failed-commands")
MECHANICAL_ALL_FIELDS = MECHANICAL_SCALAR_FIELDS + ("artifact-ref",)

# Agent-supplied bin: EXACTLY these five kinds, no more, no less (section 4). Order is
# the record's own a1..a5 numbering (section 3's worked example).
AGENT_SUPPLIED_KINDS = (
    "task-intent",
    "expected-behavior",
    "observed-behavior",
    "impact-cost",
    "workaround",
)
ASSERTION_ALLOWED_FIELDS = ("strength", "statement")

# Diagnosis bin: optional, zero or many of each (section 4).
DIAGNOSIS_KINDS = ("suspected-cause", "proposed-remedy")

STRENGTHS = ("weak", "medium", "strong")
LIFECYCLE_STANDINGS = ("active", "disputed", "superseded", "rejected")

OP_KINDS = ("create", "amend-assertion", "retire")


class EpisodeDeltaError(Exception):
    """Raised when a delta cannot be applied; nothing is written."""


def _reject_newline(value: str, where: str) -> str:
    """C3b — the injection defense named in EPISODE_STORE.md section 7: a free-text
    value that embeds a line boundary could forge a line that LOOKS like a store
    field (e.g. "- status: retired") once rendered. Reject before it is ever written,
    rather than trying to escape it at render time.

    The predicate is `value.splitlines() != [value]`, NOT a hand-listed character
    set (the previous version checked only "\\n" / "\\r" and was demonstrated to
    silently corrupt data: parse_episode() sections the file using str.splitlines()
    throughout, and splitlines() treats a WIDER set of characters as line boundaries
    than "\\n"/"\\r" alone — \\v, \\f, \\x1c-\\x1e, \\x85 (NEL), U+2028 (LINE
    SEPARATOR), U+2029 (PARAGRAPH SEPARATOR). A value containing e.g. U+2028 has
    neither "\\n" nor "\\r" in it, so the old guard accepted it; the file wrote
    successfully once, and the NEXT parse_episode() call silently truncated the
    field at the U+2028, discarding the rest with no error. Defining the guard in
    terms of splitlines() itself — the exact function the parser uses to section the
    file — makes the guard and the parser the same source of truth, so they cannot
    drift apart again the way a maintained character list inevitably would.

    `!= [value]` (rather than `len(value.splitlines()) > 1`) also closes the
    trailing-separator case for free: a value ending in a boundary character, e.g.
    "text\\u2028", splits to a SINGLE element (["text"]) — `len(...) > 1` would
    wrongly accept it — but ["text"] != ["text\\u2028"], so this predicate still
    rejects it: the trailing separator is silently dropped on the next parse just
    as surely as an embedded one truncates the field.

    One explicit carve-out: the empty string. "".splitlines() == [] (NOT [""]), so
    the predicate alone would reject "" — wrong, since an empty value contains no
    boundary of any kind and several optional fields legitimately pass "". Guard
    with `value != ""` first rather than special-casing splitlines()'s output, so
    the boundary-detection logic itself stays a single, unmodified call to the
    parser's own function."""
    if value != "" and value.splitlines() != [value]:
        raise EpisodeDeltaError(
            f"{where}: value must be a single line (no embedded or trailing line "
            "boundary) — a multi-line value could forge a store field once rendered"
        )
    return value


def _require_str(op: dict, key: str, where: str) -> str:
    value = op.get(key)
    if not isinstance(value, str) or not value.strip():
        raise EpisodeDeltaError(f"{where}: {key} is required")
    return _reject_newline(value, f"{where}.{key}")


# --- record shape ------------------------------------------------------------------


@dataclass
class Assertion:
    aid: str  # "a1".."a5" (agent-supplied, fixed order) or "d1".."dN" (diagnosis)
    kind: str
    strength: str
    lifecycle_standing: str
    statement: str
    history: list[str] = field(default_factory=list)

    def render(self, episode_id: str) -> str:
        lines = [
            f"### assertion:{episode_id}.{self.aid}",
            f"- kind: {self.kind}",
            f"- strength: {self.strength}",
            f"- lifecycle-standing: {self.lifecycle_standing}",
            f"- statement: {self.statement}",
        ]
        for entry in self.history:
            lines.append(f"- history: {entry}")
        return "\n".join(lines)


@dataclass
class Episode:
    episode_id: str
    run: str
    project: str
    role: str
    spine_step: str
    context_manifest_ref: str
    refusals: int
    reopens: int
    rework_count: int
    failed_commands: int
    artifact_refs: list[str]
    agent_supplied: dict[str, Assertion]  # keyed by kind; always the 5 AGENT_SUPPLIED_KINDS
    diagnosis: list[Assertion] = field(default_factory=list)  # d1, d2, ... in order
    status: str = "active"
    retired_reason: str = ""
    retired_at: str = ""
    consolidated_into: str = ""
    superseded_by: str = ""

    def all_assertions(self) -> dict[str, Assertion]:
        """Flat aid -> Assertion map spanning both agent-supplied and diagnosis bins,
        for amend-assertion lookup by id (e.g. "a4" or "d1")."""
        out = {a.aid: a for a in self.agent_supplied.values()}
        for d in self.diagnosis:
            out[d.aid] = d
        return out


# --- render / parse (an exact pair: render(parse(text)) == text) -------------------


def render_episode(ep: Episode) -> str:
    parts = [
        f"<!-- episode-state: schema=1 id={ep.episode_id} status={ep.status} -->",
        "",
        f"# episode: {ep.episode_id}",
        "",
        "## Mechanical",
        f"- run: {ep.run}",
        f"- project: {ep.project}",
        f"- role: {ep.role}",
        f"- spine-step: {ep.spine_step}",
        f"- context-manifest-ref: {ep.context_manifest_ref}",
        f"- refusals: {ep.refusals}",
        f"- reopens: {ep.reopens}",
        f"- rework-count: {ep.rework_count}",
        f"- failed-commands: {ep.failed_commands}",
    ]
    for ref in ep.artifact_refs:
        parts.append(f"- artifact-ref: {ref}")
    parts += ["", "## Agent-supplied", ""]
    ordered = [ep.agent_supplied[kind] for kind in AGENT_SUPPLIED_KINDS]
    for i, assertion in enumerate(ordered):
        parts.append(assertion.render(ep.episode_id))
        parts.append("")
    if ep.diagnosis:
        parts.append("## Diagnosis (optional)")
        parts.append("")
        for assertion in ep.diagnosis:
            parts.append(assertion.render(ep.episode_id))
            parts.append("")
    parts += [
        "## Retirement",
        f"- status: {ep.status}",
        f"- retired-reason: {ep.retired_reason}",
        f"- retired-at: {ep.retired_at}",
        f"- consolidated-into: {ep.consolidated_into}",
        f"- superseded-by: {ep.superseded_by}",
    ]
    return "\n".join(parts).rstrip("\n") + "\n"


HEADER_RE = re.compile(
    r"<!--\s*episode-state:\s*schema=(\d+)\s+id=(\S+)\s+status=(\S+)\s*-->"
)
ASSERTION_HEADING_RE = re.compile(r"^### assertion:(\S+)\.([ad][0-9]+)$")
FIELD_RE = re.compile(r"^- ([a-z-]+): ?(.*)$")


def parse_episode(text: str) -> Episode:
    header = HEADER_RE.search(text)
    if not header:
        raise EpisodeDeltaError("corrupt episode: missing episode-state header")
    episode_id = header.group(2)
    status = header.group(3)

    mech_idx = text.find("\n## Mechanical")
    agent_idx = text.find("\n## Agent-supplied")
    diag_idx = text.find("\n## Diagnosis")
    retire_idx = text.find("\n## Retirement")
    if mech_idx == -1 or agent_idx == -1 or retire_idx == -1:
        raise EpisodeDeltaError(f"corrupt episode {episode_id}: missing required section")

    mech_block = text[mech_idx + len("\n## Mechanical") : agent_idx]
    agent_end = diag_idx if diag_idx != -1 else retire_idx
    agent_block = text[agent_idx + len("\n## Agent-supplied") : agent_end]
    diag_block = text[diag_idx + len("\n## Diagnosis (optional)") : retire_idx] if diag_idx != -1 else ""
    retire_block = text[retire_idx + len("\n## Retirement") :]

    mech: dict[str, str] = {}
    artifact_refs: list[str] = []
    for line in mech_block.splitlines():
        m = FIELD_RE.match(line.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if key == "artifact-ref":
            artifact_refs.append(value)
        else:
            mech[key] = value

    def parse_assertions(block: str) -> list[Assertion]:
        assertions: list[Assertion] = []
        current: dict[str, str] | None = None
        history: list[str] = []
        aid = None

        def flush():
            nonlocal current, history, aid
            if current is None:
                return
            assertions.append(
                Assertion(
                    aid=aid,
                    kind=current.get("kind", ""),
                    strength=current.get("strength", ""),
                    lifecycle_standing=current.get("lifecycle-standing", ""),
                    statement=current.get("statement", ""),
                    history=list(history),
                )
            )
            current = None
            history = []
            aid = None

        for line in block.splitlines():
            heading = ASSERTION_HEADING_RE.match(line.strip())
            if heading:
                flush()
                aid = heading.group(2)
                current = {}
                continue
            if current is None:
                continue
            m = FIELD_RE.match(line.strip())
            if not m:
                continue
            key, value = m.group(1), m.group(2)
            if key == "history":
                history.append(value)
            else:
                current[key] = value
        flush()
        return assertions

    agent_list = parse_assertions(agent_block)
    agent_supplied = {a.kind: a for a in agent_list}
    diagnosis = parse_assertions(diag_block) if diag_block else []

    retire_fields: dict[str, str] = {}
    for line in retire_block.splitlines():
        m = FIELD_RE.match(line.strip())
        if m:
            retire_fields[m.group(1)] = m.group(2)

    try:
        return Episode(
            episode_id=episode_id,
            run=mech["run"],
            project=mech["project"],
            role=mech["role"],
            spine_step=mech["spine-step"],
            context_manifest_ref=mech["context-manifest-ref"],
            refusals=int(mech["refusals"]),
            reopens=int(mech["reopens"]),
            rework_count=int(mech["rework-count"]),
            failed_commands=int(mech["failed-commands"]),
            artifact_refs=artifact_refs,
            agent_supplied=agent_supplied,
            diagnosis=diagnosis,
            status=status,
            retired_reason=retire_fields.get("retired-reason", ""),
            retired_at=retire_fields.get("retired-at", ""),
            consolidated_into=retire_fields.get("consolidated-into", ""),
            superseded_by=retire_fields.get("superseded-by", ""),
        )
    except KeyError as exc:
        raise EpisodeDeltaError(f"corrupt episode {episode_id}: missing field {exc}") from None


# --- seams (EPISODE_STORE.md section 7's seam table) --------------------------------
#
# The retirement layout is HELD OPEN — g4 binds it after human ratification. Every
# layout-dependent concern routes through exactly one named function below, and each
# implements BOTH candidate adapters behind a single switch, so binding the layout is a
# one-constant flip, never a rewrite of callers. Do not inline a path, glob, or move
# anywhere else in this module.

_LAYOUT_OPTION_A = "A"  # file-move: episodes/active/<id>.md <-> episodes/retired/<id>.md
_LAYOUT_OPTION_B = "B"  # status-field-in-place: episodes/<id>.md never moves

# TODO(g4): bind after human ratification (docs/EPISODE_STORE.md section 7). This is a
# PLACEHOLDER default, not a decision — Option B is chosen here only because it needs no
# active/retired subdirectories to exist yet, matching the store's current flat layout
# (episodes/README.md). Flipping this one constant to _LAYOUT_OPTION_A is g4's whole job
# for every seam below.
_LAYOUT_ADAPTER = _LAYOUT_OPTION_B


def store_root() -> Path:
    """The ONE named seam for where episodes/ lives (EPISODE_STORE.md section 1): the
    literal relative path from the repository root. Deliberately NOT durable_root() —
    under an active Admiral epic lease durable_root() would redirect to the worktree
    root and silo the store per worktree, which is exactly wrong for a tracked path
    that is the same logical directory in every worktree the moment a commit lands."""
    return Path(__file__).resolve().parent.parent / "episodes"


def iter_episode_ids(root: Path, include_retired: bool) -> list[str]:
    """Base enumeration seam (section 7). TODO(g4): binds to whichever adapter below is
    ratified; both are implemented now so the switch is real."""
    if _LAYOUT_ADAPTER == _LAYOUT_OPTION_A:
        ids = {p.stem for p in (root / "active").glob("*.md")} if (root / "active").exists() else set()
        if include_retired and (root / "retired").exists():
            ids |= {p.stem for p in (root / "retired").glob("*.md")}
        return sorted(ids)
    # Option B: flat glob; include_retired is a no-op for this adapter (status is not
    # encoded in the path — see is_episode_in_ordinary_search below).
    if not root.exists():
        return []
    return sorted(p.stem for p in root.glob("*.md") if p.name != "README.md")


def resolve_episode_path(episode_id: str, root: Path) -> Path | None:
    """Fetch-by-id path-resolution seam (section 7). TODO(g4): binds to whichever
    adapter is ratified. Returns None if the id does not exist under the active
    adapter."""
    if _LAYOUT_ADAPTER == _LAYOUT_OPTION_A:
        for sub in ("active", "retired"):
            candidate = root / sub / f"{episode_id}.md"
            if candidate.exists():
                return candidate
        return None
    candidate = root / f"{episode_id}.md"
    return candidate if candidate.exists() else None


def _new_episode_path(episode_id: str, root: Path) -> Path:
    """Where a brand-new (always-active) episode is written. Not one of section 7's
    five named seams (create is g2's own concern, not a retrieval primitive), but it is
    exactly as layout-dependent as they are, so it is isolated here the same way —
    TODO(g4)."""
    if _LAYOUT_ADAPTER == _LAYOUT_OPTION_A:
        return root / "active" / f"{episode_id}.md"
    return root / f"{episode_id}.md"


def is_episode_in_ordinary_search(episode_id: str, root: Path) -> bool:
    """Per-id membership seam (section 7). Not exercised by the writer itself (this is
    mostly g3's retrieval concern) — named and stubbed here per the seam table so no
    caller ever needs to inline the check. TODO(g4)."""
    if _LAYOUT_ADAPTER == _LAYOUT_OPTION_A:
        return (root / "active" / f"{episode_id}.md").exists()
    path = resolve_episode_path(episode_id, root)
    if path is None:
        return False
    ep = parse_episode(path.read_text(encoding="utf-8", newline=""))
    return ep.status != "retired"


def apply_retirement(
    episode: Episode,
    reason: str,
    *,
    retired_at: str = "",
    consolidated_into: str = "",
    superseded_by: str = "",
) -> None:
    """THE retirement write-side seam (section 7): the entire content effect of a
    retire op, identical under either layout option. The writer must call this and
    never inline a field-only write or a file-move at the call site — the layout
    effect (does the FILE also move) is decided separately, in the write-plan built by
    apply_delta(), which asks _new_retirement_path() (below) for the destination. This
    function only ever mutates the in-memory Episode; it performs no I/O itself, so the
    all-or-nothing guarantee (C4) never depends on ordering retirements before other
    ops."""
    episode.status = "retired"
    episode.retired_reason = reason
    episode.retired_at = retired_at
    episode.consolidated_into = consolidated_into
    episode.superseded_by = superseded_by


def _retirement_destination(episode_id: str, root: Path, current_path: Path) -> Path:
    """The layout-dependent HALF of retiring: does the file move? TODO(g4): binds to
    whichever adapter is ratified. Isolated from apply_retirement()'s field diff so the
    two can be tested (and eventually bound) independently."""
    if _LAYOUT_ADAPTER == _LAYOUT_OPTION_A:
        return root / "retired" / f"{episode_id}.md"
    return current_path  # Option B: the file never moves


# --- id assignment (EPISODE_STORE.md section 2) -------------------------------------


def _next_episode_id(run: str, known_ids: set[str]) -> str:
    """Zero-agent-effort id assignment: scan existing <run>-*.md basenames (across
    every episode for that run regardless of retirement status — a retired episode's
    sequence number is still taken) for the current max and increment. No counter
    file, no UUID."""
    prefix = f"{run}-"
    max_seq = 0
    for eid in known_ids:
        if eid.startswith(prefix):
            suffix = eid[len(prefix) :]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))
    return f"{run}-{max_seq + 1:03d}"


# --- validate (pure — no disk I/O, so a structurally-invalid delta is rejected before
# any file is ever touched, regardless of what the real store on disk contains) -------


def validate_delta(delta: dict) -> tuple[str, list[dict]]:
    work_id = delta.get("work_id")
    if not work_id or not isinstance(work_id, str):
        raise EpisodeDeltaError("delta requires a non-empty string work_id")

    ops = delta.get("ops", [])
    if not isinstance(ops, list) or not ops:
        raise EpisodeDeltaError("delta is a no-op: provide at least one op")

    for op in ops:
        kind = op.get("op")
        if kind not in OP_KINDS:
            raise EpisodeDeltaError(f"unknown op {kind!r} (must be one of {OP_KINDS})")

        if kind == "create":
            _validate_create(op)
        elif kind == "amend-assertion":
            _validate_amend_assertion(op)
        elif kind == "retire":
            _validate_retire(op)

    return work_id, ops


def _validate_create(op: dict) -> None:
    if "id" in op:
        raise EpisodeDeltaError(
            "create: id must not be supplied — the writer assigns it "
            "(EPISODE_STORE.md section 2, zero agent effort)"
        )

    mech = op.get("mechanical")
    if not isinstance(mech, dict):
        raise EpisodeDeltaError("create: mechanical is required and must be an object")

    # C2 (one direction): any key outside the mechanical allowlist is misfiled — most
    # dangerously, an agent-supplied concept (lifecycle-standing, strength, kind, ...)
    # smuggled onto a mechanical fact, which EPISODE_STORE.md section 5 says must never
    # happen (mechanical facts carry no epistemic status at all).
    for key in mech:
        if key not in MECHANICAL_ALL_FIELDS:
            raise EpisodeDeltaError(
                f"create: misfiled field {key!r} under mechanical — not a recognized "
                f"mechanical field (allowed: {', '.join(MECHANICAL_ALL_FIELDS)}). "
                "Agent-supplied fields belong under agent_supplied/diagnosis, never "
                "mechanical."
            )
    for key in MECHANICAL_SCALAR_FIELDS:
        value = mech.get(key)
        if key in MECHANICAL_INT_FIELDS:
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise EpisodeDeltaError(f"create.mechanical.{key}: must be a non-negative integer")
        else:
            if not isinstance(value, str) or not value.strip():
                raise EpisodeDeltaError(f"create.mechanical.{key}: is required")
            _reject_newline(value, f"create.mechanical.{key}")
    run = mech["run"]
    if not RUN_RE.fullmatch(run):
        raise EpisodeDeltaError(f"create.mechanical.run: {run!r} must be kebab-case")

    artifact_refs = mech.get("artifact-ref", [])
    if not isinstance(artifact_refs, list) or any(not isinstance(r, str) for r in artifact_refs):
        raise EpisodeDeltaError("create.mechanical.artifact-ref: must be a list of strings")
    for ref in artifact_refs:
        _reject_newline(ref, "create.mechanical.artifact-ref")

    agent_supplied = op.get("agent_supplied")
    if not isinstance(agent_supplied, dict):
        raise EpisodeDeltaError("create: agent_supplied is required and must be an object")
    given_kinds = set(agent_supplied)
    missing = [k for k in AGENT_SUPPLIED_KINDS if k not in given_kinds]
    if missing:
        raise EpisodeDeltaError(f"create.agent_supplied: missing required kind(s) {missing}")
    extra = given_kinds - set(AGENT_SUPPLIED_KINDS)
    if extra:
        # C2 (the other direction): a field that is not one of the exact five
        # agent-supplied kinds — e.g. a mechanical field name filed here instead.
        raise EpisodeDeltaError(
            f"create.agent_supplied: misfiled field(s) {sorted(extra)} — the "
            f"agent-supplied bin accepts EXACTLY {AGENT_SUPPLIED_KINDS}, no more, no less"
        )
    for kind, payload in agent_supplied.items():
        _validate_assertion_payload(payload, f"create.agent_supplied.{kind}")

    diagnosis = op.get("diagnosis", [])
    if not isinstance(diagnosis, list):
        raise EpisodeDeltaError("create.diagnosis: must be a list")
    for i, entry in enumerate(diagnosis):
        if not isinstance(entry, dict):
            raise EpisodeDeltaError(f"create.diagnosis[{i}]: must be an object")
        kind = entry.get("kind")
        if kind not in DIAGNOSIS_KINDS:
            raise EpisodeDeltaError(
                f"create.diagnosis[{i}]: misfiled kind {kind!r} — must be one of {DIAGNOSIS_KINDS}"
            )
        extra_keys = set(entry) - {"kind"} - set(ASSERTION_ALLOWED_FIELDS)
        if extra_keys:
            raise EpisodeDeltaError(f"create.diagnosis[{i}]: misfiled field(s) {sorted(extra_keys)}")
        _validate_assertion_payload(entry, f"create.diagnosis[{i}]")


def _validate_assertion_payload(payload: dict, where: str) -> None:
    if not isinstance(payload, dict):
        raise EpisodeDeltaError(f"{where}: must be an object")
    extra = set(payload) - set(ASSERTION_ALLOWED_FIELDS) - {"kind"}
    if extra:
        raise EpisodeDeltaError(
            f"{where}: misfiled field(s) {sorted(extra)} — an assertion at create time "
            f"only accepts {ASSERTION_ALLOWED_FIELDS} (lifecycle-standing always starts "
            "'active' and is never set here)"
        )
    strength = payload.get("strength")
    if strength not in STRENGTHS:
        raise EpisodeDeltaError(f"{where}.strength: must be one of {STRENGTHS}")
    _require_str(payload, "statement", where)


def _validate_amend_assertion(op: dict) -> None:
    episode_id = op.get("id")
    if not isinstance(episode_id, str) or not ID_RE.fullmatch(episode_id):
        raise EpisodeDeltaError(f"amend-assertion: invalid episode id {episode_id!r}")
    assertion_id = op.get("assertion")
    if not isinstance(assertion_id, str) or not re.fullmatch(r"[ad][0-9]+", assertion_id):
        raise EpisodeDeltaError(f"amend-assertion: invalid assertion id {assertion_id!r}")
    standing = op.get("lifecycle-standing")
    if standing not in LIFECYCLE_STANDINGS:
        raise EpisodeDeltaError(f"amend-assertion: lifecycle-standing must be one of {LIFECYCLE_STANDINGS}")
    _require_str(op, "history", "amend-assertion")


def _validate_retire(op: dict) -> None:
    episode_id = op.get("id")
    if not isinstance(episode_id, str) or not ID_RE.fullmatch(episode_id):
        raise EpisodeDeltaError(f"retire: invalid episode id {episode_id!r}")
    # C3a — the mandatory non-empty reason (mirrors apply_lessons_delta.py's own
    # mandatory retire reason).
    _require_str(op, "reason", "retire")
    for optional_key in ("retired-at", "consolidated-into", "superseded-by"):
        value = op.get(optional_key, "")
        if not isinstance(value, str):
            raise EpisodeDeltaError(f"retire.{optional_key}: must be a string")
        _reject_newline(value, f"retire.{optional_key}")


# --- apply (write-plan first, disk touched only once every op has succeeded) --------


class _Transaction:
    """Everything an apply_delta() run needs, kept in memory until every op in the
    delta has succeeded. Nothing under self.writes/self.deletes is touched on disk
    until commit() — that deferral is what makes C4 (all-or-nothing) hold even across
    multiple files in one delta."""

    def __init__(self, root: Path):
        self.root = root
        self.loaded: dict[str, Episode] = {}
        self.original_paths: dict[str, Path] = {}
        self._known_ids: set[str] | None = None

    def known_ids(self) -> set[str]:
        if self._known_ids is None:
            self._known_ids = set(iter_episode_ids(self.root, include_retired=True))
        return self._known_ids

    def load(self, episode_id: str) -> Episode:
        if episode_id in self.loaded:
            return self.loaded[episode_id]
        path = resolve_episode_path(episode_id, self.root)
        if path is None:
            raise EpisodeDeltaError(f"no such episode: {episode_id}")
        ep = parse_episode(path.read_text(encoding="utf-8", newline=""))
        self.loaded[episode_id] = ep
        self.original_paths[episode_id] = path
        return ep

    def create(self, ep: Episode) -> None:
        self.loaded[ep.episode_id] = ep
        self.known_ids().add(ep.episode_id)
        self.original_paths[ep.episode_id] = _new_episode_path(ep.episode_id, self.root)

    def write_plan(self) -> tuple[dict[Path, str], set[Path]]:
        """Renders every touched episode to its FINAL destination path. Returns
        (path -> text to write, paths to delete) — deletes only happen for a retire
        under Option A, where the file moves and the old path must be removed."""
        writes: dict[Path, str] = {}
        deletes: set[Path] = set()
        for episode_id, ep in self.loaded.items():
            original_path = self.original_paths[episode_id]
            if ep.status == "retired":
                dest = _retirement_destination(episode_id, self.root, original_path)
            else:
                dest = original_path
            writes[dest] = render_episode(ep)
            if dest != original_path and original_path.exists():
                deletes.add(original_path)
        return writes, deletes

    def commit(self) -> None:
        """REWORK (g2 review BLOCK, defect 2): stage every touched file to a temp
        path FIRST, and only move a temp file into its final place once every
        staged write has succeeded. The old version called path.write_text()
        directly on each final path in sequence — a real OS-level failure (disk
        full, permission denied, a locked file) on, say, the 2nd of 2 touched files
        left the 1st file's write landed on disk while the delta as a whole still
        failed, contradicting this module's own all-or-nothing claim. Staging
        closes that gap for the WRITE step: if any staged write raises, every temp
        file already written is removed and no final path is ever touched.

        The temp file lives NEXT TO its final path (same directory, so same store
        root, same filesystem) so the move below is a same-filesystem rename, never
        a cross-filesystem copy.

        Honest limit: moving N staged files into place is NOT atomic as a whole —
        only a SINGLE os.replace() call is atomic (on both POSIX and Windows). A
        crash between the 1st and 2nd move can still leave a partial result on
        disk. Nothing in EPISODE_STORE.md's markdown-in-git constraint provides a
        journal/WAL to close that residual gap, so this is the best available
        guarantee for the write step, not a claim of full multi-file atomicity."""
        writes, deletes = self.write_plan()
        staged: list[tuple[Path, Path]] = []
        try:
            for final_path, text in writes.items():
                final_path.parent.mkdir(parents=True, exist_ok=True)
                tmp_path = final_path.parent / f".{final_path.name}.tmp-{uuid.uuid4().hex}"
                tmp_path.write_text(text, encoding="utf-8", newline="")
                staged.append((tmp_path, final_path))
        except Exception:
            for tmp_path, _ in staged:
                tmp_path.unlink(missing_ok=True)
            raise

        # Every staged write succeeded — move each into place. See the docstring
        # above for why this loop, taken as a whole, is best-effort rather than
        # atomic.
        try:
            for tmp_path, final_path in staged:
                os.replace(tmp_path, final_path)
        finally:
            for tmp_path, _ in staged:
                tmp_path.unlink(missing_ok=True)  # no-op once moved

        for path in deletes:
            path.unlink(missing_ok=True)


def apply_delta(root: Path, delta: dict) -> list[str]:
    work_id, ops = validate_delta(delta)
    tx = _Transaction(root)
    log: list[str] = []

    for op in ops:
        kind = op["op"]
        if kind == "create":
            log.append(_apply_create(tx, op))
        elif kind == "amend-assertion":
            log.append(_apply_amend_assertion(tx, op))
        elif kind == "retire":
            log.append(_apply_retire(tx, op))

    tx.commit()
    return log


def _apply_create(tx: _Transaction, op: dict) -> str:
    mech = op["mechanical"]
    run = mech["run"]
    episode_id = _next_episode_id(run, tx.known_ids())

    agent_supplied = {}
    for i, kind in enumerate(AGENT_SUPPLIED_KINDS, start=1):
        payload = op["agent_supplied"][kind]
        agent_supplied[kind] = Assertion(
            aid=f"a{i}",
            kind=kind,
            strength=payload["strength"],
            lifecycle_standing="active",
            statement=payload["statement"].strip(),
        )

    diagnosis = []
    for i, entry in enumerate(op.get("diagnosis", []), start=1):
        diagnosis.append(
            Assertion(
                aid=f"d{i}",
                kind=entry["kind"],
                strength=entry["strength"],
                lifecycle_standing="active",
                statement=entry["statement"].strip(),
            )
        )

    ep = Episode(
        episode_id=episode_id,
        run=run,
        project=mech["project"].strip(),
        role=mech["role"].strip(),
        spine_step=mech["spine-step"].strip(),
        context_manifest_ref=mech["context-manifest-ref"].strip(),
        refusals=mech["refusals"],
        reopens=mech["reopens"],
        rework_count=mech["rework-count"],
        failed_commands=mech["failed-commands"],
        artifact_refs=[ref.strip() for ref in mech.get("artifact-ref", [])],
        agent_supplied=agent_supplied,
        diagnosis=diagnosis,
    )
    tx.create(ep)
    return f"created episode:{episode_id}"


def _apply_amend_assertion(tx: _Transaction, op: dict) -> str:
    episode_id = op["id"]
    ep = tx.load(episode_id)
    assertions = ep.all_assertions()
    assertion_id = op["assertion"]
    assertion = assertions.get(assertion_id)
    if assertion is None:
        raise EpisodeDeltaError(f"amend-assertion {episode_id}.{assertion_id}: no such assertion")
    # Surgical: only this assertion's lifecycle-standing changes, plus one appended
    # history line. kind/strength/statement, every sibling assertion, every mechanical
    # line, and the retirement block are all left exactly as parsed (C6).
    assertion.lifecycle_standing = op["lifecycle-standing"]
    assertion.history.append(op["history"].strip())
    return f"amended {episode_id}.{assertion_id} -> lifecycle-standing={assertion.lifecycle_standing}"


def _apply_retire(tx: _Transaction, op: dict) -> str:
    episode_id = op["id"]
    ep = tx.load(episode_id)
    apply_retirement(
        ep,
        op["reason"].strip(),
        retired_at=op.get("retired-at", "").strip(),
        consolidated_into=op.get("consolidated-into", "").strip(),
        superseded_by=op.get("superseded-by", "").strip(),
    )
    return f"retired episode:{episode_id} — {ep.retired_reason}"


# --- CLI -----------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta", type=Path, required=True, help="JSON delta file with work_id, ops")
    parser.add_argument(
        "--store-root",
        type=Path,
        default=None,
        help="episode store root (default: the tracked episodes/ seam — see store_root())",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    root = args.store_root if args.store_root is not None else store_root()

    try:
        delta = json.loads(args.delta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read delta: {exc}", file=sys.stderr)
        return 1

    # Split from the block above on purpose (REWORK, g2 review BLOCK defect 2):
    # an OSError here comes from the WRITE phase (apply_delta -> commit()), not
    # from reading the delta file, which already succeeded above. Reporting it as
    # "cannot read delta" would be a plausible-sounding but wrong message — fail
    # visibly with the truth instead (no hidden fallback / misleading message).
    try:
        log = apply_delta(root, delta) if not args.dry_run else _dry_run_log(root, delta)
    except EpisodeDeltaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: write failed, store left unchanged: {exc}", file=sys.stderr)
        return 1

    for line in log:
        print(line)
    return 0


def _dry_run_log(root: Path, delta: dict) -> list[str]:
    """Validate and compute the write-plan, but never call commit()."""
    work_id, ops = validate_delta(delta)
    tx = _Transaction(root)
    log: list[str] = []
    for op in ops:
        kind = op["op"]
        if kind == "create":
            log.append(_apply_create(tx, op))
        elif kind == "amend-assertion":
            log.append(_apply_amend_assertion(tx, op))
        elif kind == "retire":
            log.append(_apply_retire(tx, op))
    log.append("DRY RUN — no write")
    return log


if __name__ == "__main__":
    raise SystemExit(main())
