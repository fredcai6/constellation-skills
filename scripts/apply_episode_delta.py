#!/usr/bin/env python
"""Deterministically apply structured episode-delta operations to the episode store.

The LLM proposes operations (create/amend-assertion/restate-assertion/retire) in a JSON
delta file; this
script validates every op and applies them mechanically, all-or-nothing: any invalid op
anywhere in the delta rejects the WHOLE delta and leaves the store byte-for-byte
unchanged. The LLM never writes an episode file directly — this script is the only
write path into episodes/.

Mirrors scripts/apply_lessons_delta.py's contract (validate-then-apply, all-or-nothing,
retire-requires-reason, "- field: value" grammar) but is NOT the same store: see
docs/EPISODE_STORE.md for the full contract this writer implements, and its section 7
in particular for the retirement layout, ratified at gate g4 and bound in the seam block
below — retirement MOVES the file from episodes/active/<id>.md to
episodes/retired/<id>.md, and retired/ is an archive rather than a second live search
space.

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
  restate-assertion — rewrite exactly ONE named assertion's `statement`, and append one
                     history line carrying the ORIGINAL statement VERBATIM. The op exists
                     so a record written as an instruction can be restated as an
                     observation without losing what the record originally said.
                     amend-assertion cannot do this: it accepts no `statement` at all and
                     changes only lifecycle-standing, so a prescriptive sentence marked
                     `superseded` still STANDS as the live statement. The history line is
                     built HERE, from the parsed original, never supplied by the caller —
                     a caller who could author it could misquote what was there, which
                     defeats the whole point. The caller's `history` value supplies only
                     the reason. Nothing else moves: not kind, strength or
                     lifecycle-standing (a restatement changes wording, never epistemic
                     status), not a sibling assertion, not a mechanical line, not the
                     retirement block. EPISODE_STORE.md section 5 ("the record grows
                     rather than getting rewritten") is the constraint this op answers to,
                     and it is answered by preserving the original wording verbatim in the
                     assertion's own history — nothing the store ever asserted is
                     destroyed.
  retire           — move an episode out of ordinary search and into the archive,
                     RETAINED in history, with a mandatory non-empty reason. Never
                     touches any assertion's own lifecycle-standing (EPISODE_STORE.md
                     section 7). The content half routes through apply_retirement()
                     alone; the layout half (the move) through destination_for()
                     alone. Both land in one write plan, so the store is never left
                     half-retired.

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

That newline discipline goes through `read_text_exact` / `write_text_exact` below rather
than `Path.read_text(newline=...)` / `Path.write_text(newline=...)`, which exist only on
Python 3.13+ while CI pins 3.12 — see those helpers.
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


# The store's minimum interpreter. Must equal the version CI pins in
# .github/workflows/ci.yml — tests/test_episode_store.py asserts that equality, so the two
# cannot drift apart silently.
REQUIRES_PYTHON = (3, 12)


def read_text_exact(path: Path) -> str:
    """Read a store file with newline translation DISABLED, so bytes survive the round trip.

    Deliberately NOT `path.read_text(encoding=..., newline="")`: pathlib only gained the
    `newline` kwarg in Python 3.13, and CI pins 3.12, so that form raises TypeError there.
    `Path.open()` has accepted `newline` on every supported version. The `newline=""` is
    load-bearing rather than cosmetic — it is what keeps the bytes the parser sees identical
    to the bytes on disk, which is what `_reject_newline` and the byte-for-byte-unchanged
    assertions both depend on.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        return handle.read()


def write_text_exact(path: Path, text: str) -> None:
    """Write a store file emitting exactly `text`, with no platform newline translation.

    Same portability reason as `read_text_exact`, and the same load-bearing semantics: on
    Windows the default would translate every `\\n` to `\\r\\n`, making the store's bytes
    depend on which OS wrote them.
    """
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


# --- the record's fixed vocabulary (EPISODE_STORE.md sections 2-4) ---------------

# A RUN is a work-id, and a work-id is a PATH under `.agent-work/` that may NEST:
# the epic/commander convention writes `epic-418-followon/commander-424`. The run is
# what `verify_episode_captured.py <work-id>` matches on, and the closeout spine
# passes the work-id verbatim — so a run grammar that refuses `/` made the mandated
# closeout step impossible to complete: the writer forbade exactly the id the gate
# demanded. Each `/`-separated segment keeps the old flat kebab grammar, so `..`, an
# empty segment (leading/trailing/doubled separator) and an absolute path are all
# still refused.
RUN_SEGMENT = r"[a-z0-9][a-z0-9-]*"
RUN_RE = re.compile(rf"{RUN_SEGMENT}(?:/{RUN_SEGMENT})*")

# An episode ID is a FILENAME (`active/<id>.md`), and the store's layout invariant is
# that every episode sits DIRECTLY inside active/ or retired/ — `_layout_episode_ids`
# refuses a record one level deeper as misfiled. So the id may not carry the run's
# separators; it carries the run FLATTENED by `run_to_id_stem` below. `_` is the
# flattening character precisely because no run segment can contain one, which makes
# the mapping injective: an id stem determines its run and no two runs collide.
ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]*-[0-9]{3,}")


def run_to_id_stem(run: str) -> str:
    """The episode-id stem for `run` — the run with its path separators flattened.

    Injective by construction (see `ID_RE`): `/` cannot appear in an id and `_`
    cannot appear in a run, so `a/b -> a_b` is reversible and `a/b` and any literal
    flat run can never mint the same stem. This is a FILENAME encoding, not a
    normalization of identity: the episode's `- run:` line keeps the work-id exactly
    as given, which is what the capture gate matches on."""
    return run.replace("/", "_")

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

OP_KINDS = ("create", "amend-assertion", "restate-assertion", "retire")

# restate-assertion accepts EXACTLY these keys and no others. An allowlist rather than a
# denylist for the same reason create's mechanical bin uses one: the dangerous input is a
# field misfiled onto the op — most of all `lifecycle-standing`, `strength` or `kind`,
# which a caller might reasonably expect a restatement to carry. It must not; a
# restatement changes wording, and epistemic status moves only through amend-assertion.
RESTATE_ALLOWED_FIELDS = ("op", "id", "assertion", "statement", "history")


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
# THE RETIREMENT LAYOUT IS BOUND (gate g4). Ratified by Tommy, verbatim:
#
#     "move the file, prefer to keep files clean of history unless they're historical.
#      archives are available strats."
#
# That is section 7's Option A: retirement MOVES the file, episodes/active/<id>.md ->
# episodes/retired/<id>.md. Option B (a `status` field filtered negatively, file never
# moves) is REJECTED; its adapters and the switch that selected between them have been
# removed, because a switch that can still select a rejected option is a decision that is
# still open.
#
# The second half of the ruling is a design principle, not decoration: retired/ is a
# genuine ARCHIVE, not a second live search space every query must remember to exclude.
# Ordinary retrieval globs active/ and never looks at retired/; history-inclusive
# retrieval is a separate, deliberate act (the include_retired=True argument below is the
# only way to reach the archive, and no default supplies it).
#
# THE DIRECTORY NAMES BELOW ARE THE ONLY PLACE THEY MAY APPEAR. Every layout-dependent
# concern routes through exactly one named function in this block; no other primitive, in
# this module or in scripts/query_episodes.py, may inline a path, glob, or move.
#
# What binding Option A did NOT do: it made the OLD silent-omission trap (a positive
# `status: active` allowlist dropping a legitimately-not-retired `disputed` episode)
# structurally impossible — membership is now a directory fact, not a parsed field — but
# it RELOCATED the class rather than removing it. Three traps now live here instead, and
# each has an adversarial fixture in tests/test_episode_store.py:
#   1. a glob that misses a subdirectory (episodes/*.md, after the layout gained
#      active/ and retired/) — silently returns nothing, or only strays;
#   2. a history-inclusive enumeration that forgets to union BOTH directories —
#      silently returns only the active half;
#   3. a stray file at the old flat path (episodes/<id>.md, in neither subdirectory) —
#      it belongs to no set and must be surfaced as MALFORMED, not skipped. This is the
#      live migration hazard: episodes/README.md already lives at the flat root, so the
#      exclusion of non-episode strays has to be DELIBERATE, never an accident of a
#      glob's shape.
#   4. a NON-EPISODE FILE INSIDE A LAYOUT DIRECTORY — the mirror image of trap 3, and
#      the one that actually shipped at first attempt. Membership moved from file
#      CONTENT to file LOCATION, so anything a directory listing returns becomes an
#      episode id; a `README.md` placed in active/ and retired/ to keep the layout in
#      git therefore minted the phantom id `README` in BOTH sets and bricked every
#      primitive. See episode_id_for() below for why the classifier is now derived
#      rather than enumerated.
#   5. a store root, or a layout directory, that is not there at all — Path.glob over a
#      missing directory returns empty, which is trap 1's own failure description
#      ("indistinguishable from an empty store") reached by a typo'd --store-root.

ACTIVE_DIR = "active"  # the ordinary rhyme-search set
RETIRED_DIR = "retired"  # the archive — reachable only history-inclusively

# Non-episode files that legitimately sit at the store's FLAT ROOT. Scoped to that one
# directory on purpose: it is the only place a hand-maintained list is unavoidable,
# because a file there is outside the store's own naming grammar by definition (the
# store's README is documentation for humans, not a record). Inside active/ and
# retired/, membership is decided by episode_id_for() instead — see below.
NON_EPISODE_FILENAMES = frozenset({"README.md"})


def episode_id_for(path: Path) -> str | None:
    """THE classifier: is this file an episode, and if so, which one? Returns the
    episode id, or None for a file that is not an episode at all.

    Derived from the store's OWN id grammar (ID_RE, section 2) rather than from a
    hand-maintained list of filenames — and that is the whole point. The first attempt
    at this gate used a named allowlist (NON_EPISODE_FILENAMES) consulted at the flat
    root only, and it failed in the way hand-maintained enumerations always fail: the
    layout gained two directories, membership moved from content to location, and the
    classifier stayed behind. Its own placeholders then became the phantom id `README`.

    An id grammar cannot drift from itself. `README`, `notes`, `CODEOWNERS`, `index`,
    and every future `.gitkeep`-shaped afterthought are rejected by the same rule that
    accepts `governor-268-001` — no edit required when someone adds a file, and no
    silent acceptance of a real stray when someone forgets to. It is also the rule that
    REFUSES a bad placeholder at authoring time rather than at first read.

    Uniform in all three directories: episode-ness is a property of the name, so the
    answer cannot depend on which directory asked."""
    if path.suffix != ".md":
        return None
    return path.stem if ID_RE.fullmatch(path.stem) else None


def store_root() -> Path:
    """The ONE named seam for where episodes/ lives (EPISODE_STORE.md section 1): the
    literal relative path from the repository root. Deliberately NOT durable_root() —
    under an active Admiral epic lease durable_root() would redirect to the worktree
    root and silo the store per worktree, which is exactly wrong for a tracked path
    that is the same logical directory in every worktree the moment a commit lands."""
    # HAZARD, measured (#447): this resolves relative to THIS FILE, so it is only the
    # project's store while this file sits in the project's scripts/. On a copy bundled
    # into a skill and installed, it resolves to
    # ~/.claude/skills/<role>/episodes — the skill install directory, not the repo. A
    # spine that invoked this writer without an explicit --store-root would silently
    # create a store outside the repo while every gate reported green: #308's failure
    # shape wearing a new name. Callers running an INSTALLED copy must pass
    # --store-root explicitly (wired into the spine commands at g3). The semantics
    # above are deliberately unchanged — durable_root() is ruled out for the reason in
    # the docstring, and a retirement is not the place to overturn that ruling.
    # scripts/verify_episode_captured.py's --store-root default carries the same hazard
    # and names it at the same place in its own main().
    return Path(__file__).resolve().parent.parent / "episodes"


def ensure_store_layout(root: Path) -> None:
    """Create the store's two layout directories if they are absent — the WRITER's
    bootstrap, and deliberately not a reader's.

    Writing is a creating act, so `--store-root <somewhere-new>` legitimately makes a
    store there. Reading is not: a reader that quietly created a missing directory would
    then answer "0 episodes, exit 0" for a typo'd root, which is the silent-omission
    class arriving through the back door. The read seams therefore REFUSE an absent
    layout (see _require_store_layout) and only this function ever makes one."""
    (root / ACTIVE_DIR).mkdir(parents=True, exist_ok=True)
    (root / RETIRED_DIR).mkdir(parents=True, exist_ok=True)


def _require_store_layout(root: Path) -> None:
    """Every READ seam's first act: refuse a store that is not there.

    Trap 5. `Path.glob` over a missing directory returns empty and raises nothing, so the
    natural implementation answers `[]` — indistinguishable from "the store is empty",
    which is trap 1's own failure description reached by a different route. A wrong
    `--store-root`, or a layout that never got committed (git does not track empty
    directories, and this layout is two directories), must fail visibly instead."""
    if not root.is_dir():
        raise EpisodeDeltaError(
            f"missing store: {root} is not a directory. Enumerating a store that is not "
            "there would return an empty candidate set, which reads exactly like an "
            "empty store — so this is refused rather than answered. Check --store-root."
        )
    absent = [sub for sub in (ACTIVE_DIR, RETIRED_DIR) if not (root / sub).is_dir()]
    if absent:
        raise EpisodeDeltaError(
            "missing store layout: "
            + ", ".join(f"{root / sub}" for sub in absent)
            + f" — the store is the two directories {ACTIVE_DIR}/ and {RETIRED_DIR}/, "
            "and an absent one is not an empty one. Git does not track empty "
            "directories, so a layout that was never committed arrives here; the writer "
            "creates the layout (ensure_store_layout), readers refuse it."
        )


def stray_episode_paths(root: Path) -> list[Path]:
    """Every Markdown file sitting at the store's FLAT root — i.e. in neither active/
    nor retired/ — that is not one of the store's known non-episode files.

    Trap 3 (see the seam-block header). Under the bound layout an episode is a member of
    exactly one of two directories; a file at `episodes/<id>.md` is a member of neither,
    so BOTH the ordinary and the history-inclusive enumerations would return an answer
    that silently excludes it. That is the same silent-omission class the flat layout
    had, wearing a migration's clothes: a pre-layout episode left behind by a partial
    migration reads, to every query, as though it does not exist.

    So it is surfaced rather than skipped — and the exclusion of the store's own
    documentation is a NAMED allowlist (NON_EPISODE_FILENAMES), never a glob shape that
    happens not to match it. The allowlist lives HERE and only here: inside the layout
    directories the id grammar answers the same question without anyone maintaining a
    list (episode_id_for).

    Recursive, and the allowlist applies at the flat root ONLY (trap 6). A Markdown file
    at `episodes/archive/<id>.md` is exactly as invisible to every one-level-deep scan as
    one at the flat path, and "a directory nobody declared" is not a safer place to hide
    a record than "the level above". Files inside active/ and retired/ are excluded here
    because _layout_episode_ids() scans those two with its own, stricter rule."""
    if not root.is_dir():
        return []
    layout = (root / ACTIVE_DIR, root / RETIRED_DIR)
    strays = []
    for path in root.rglob("*.md"):
        if not path.is_file() or any(d in path.parents for d in layout):
            continue
        if path.parent == root and path.name in NON_EPISODE_FILENAMES:
            continue
        strays.append(path)
    return sorted(strays)


def _reject_strays(root: Path) -> None:
    strays = stray_episode_paths(root)
    if strays:
        raise EpisodeDeltaError(
            "malformed store: "
            + ", ".join(p.relative_to(root).as_posix() for p in strays)
            + f" is in neither {ACTIVE_DIR}/ nor {RETIRED_DIR}/. "
            "An episode belongs to exactly one of those two sets; a file anywhere else "
            "under the store belongs to neither and would be silently omitted by every "
            "enumeration. Move it into the directory it belongs in (or, if it is a "
            "non-episode file at the store root, add it to NON_EPISODE_FILENAMES — an "
            "allowlist that is scoped to the flat root and nowhere else)."
        )


def _layout_episode_ids(root: Path, sub: str) -> set[str]:
    """Every episode id held by ONE layout directory — the only place a directory
    listing becomes a set of ids.

    Trap 4. A listing answers "what files are here", never "what episodes are here", and
    under a location-based membership rule the gap between those two questions is where
    a phantom id comes from. episode_id_for() closes it, and a `*.md` that is NOT a
    well-formed episode id is REFUSED rather than skipped: inside active/ or retired/
    such a file is either a misfiled record or a placeholder that should not have been
    given a `.md` name, and both are things a human must look at. Skipping would be the
    silent-omission class again, one directory deeper.

    Recursive for the same reason stray_episode_paths() is (trap 6): a record at
    `active/old/<id>.md` is a well-formed episode filename at the wrong DEPTH, and a scan
    that only lists the top level omits it in silence. Depth is part of the name test
    here, so both halves of "is this an episode of this set" are answered in one place."""
    directory = root / sub
    ids: set[str] = set()
    misfiled: list[str] = []
    for path in sorted(directory.rglob("*.md")):
        if not path.is_file():
            continue
        episode_id = episode_id_for(path)
        if episode_id is None or path.parent != directory:
            misfiled.append(path.relative_to(root).as_posix())
            continue
        ids.add(episode_id)
    if misfiled:
        raise EpisodeDeltaError(
            "malformed store: "
            + ", ".join(misfiled)
            + " is not a well-formed episode file at this level (<episode-id>.md "
            f"directly inside {sub}/, where the id matches {ID_RE.pattern}). Inside "
            f"{ACTIVE_DIR}/ and {RETIRED_DIR}/ every Markdown file IS an episode — "
            "membership is the directory it sits in — so a name the store's own id "
            "grammar does not recognize, or a record buried one level deeper, is either "
            "misfiled or a non-episode file that must not carry a .md name. Refused "
            "rather than skipped: skipping is how a filename becomes a phantom id, and "
            "how a real record becomes invisible."
        )
    return ids


def _reject_half_retired(live: set[str], archived: set[str]) -> None:
    """An id present in BOTH directories is a retirement that half-happened: retired by
    content, still in the ordinary-search set by directory.

    _Transaction.commit() compensates for every failure the process survives to observe,
    so this state cannot be produced by a failed retirement — but a hard kill or power
    loss between the two placement steps runs no compensation at all, and
    markdown-in-git provides no journal to close that. Rather than claim the residue is
    impossible, this makes it LOUD: an ordinary enumeration would otherwise return the
    id and its record would read `status: retired`, which is a wrong answer with nothing
    signalling it."""
    both = sorted(live & archived)
    if both:
        raise EpisodeDeltaError(
            "half-retired store: "
            + ", ".join(both)
            + f" exists in BOTH {ACTIVE_DIR}/ and {RETIRED_DIR}/ — a retirement was "
            "interrupted between placing the archived copy and removing the source. "
            f"The {RETIRED_DIR}/ copy is the newer one; remove the {ACTIVE_DIR}/ copy to "
            "complete the retirement, or the reverse to abandon it."
        )


def iter_episode_ids(root: Path, include_retired: bool) -> list[str]:
    """Base enumeration seam (section 7), bound to Option A.

    Ordinary enumeration is the ordinary set and nothing else — the archive is not a
    second live search space that this function has to remember to exclude, which is
    exactly the ruling's second half. `include_retired=True` is the deliberate
    history-inclusive act: it UNIONS both directories. Trap 2 is forgetting that union
    and returning only the active half, so the union is written once, here, and no caller
    repeats it.

    Two malformed-store conditions raise here rather than being answered around, because
    both would otherwise produce a silently wrong candidate set — and because putting
    them in the seam every reader AND the writer's own id-assignment scan already goes
    through means no caller has to remember them:

      * a stray at the flat root (trap 3) — it belongs to neither set, so every
        enumeration omits it, and the writer would happily mint an id the stray holds;
      * an id in both directories — an interrupted retirement (see _reject_half_retired).

    The archive is listed even for an ordinary scan, solely to check the second
    condition. That listing can only ever produce a REFUSAL; it never contributes a
    candidate, so the archive remains an archive rather than a second search space.

    Both directory listings go through _layout_episode_ids(), so a file that is not an
    episode never becomes a candidate id here — the classifier is applied where the
    membership rule is applied, which is the coupling whose absence bricked this store
    the first time round."""
    _require_store_layout(root)
    _reject_strays(root)
    live = _layout_episode_ids(root, ACTIVE_DIR)
    archived = _layout_episode_ids(root, RETIRED_DIR)
    _reject_half_retired(live, archived)
    return sorted(live | archived if include_retired else live)


def resolve_episode_path(episode_id: str, root: Path) -> Path | None:
    """Fetch-by-id path-resolution seam (section 7), bound to Option A: try active/,
    then retired/. Returns None if the id does not exist.

    At most one of the two SHOULD exist for any valid id — but "should" is the whole
    point: the residual half-retired state is admitted to be possible (a hard kill
    between two filesystem calls runs no compensation), so this function checks rather
    than assuming. An earlier version of this docstring asserted "an episode is never in
    both places at once" while the code below silently returned the active/ copy when it
    was, which is the worst of both: a comment the next reader trusts instead of testing.

    Fetch-by-id deliberately reaches into the archive: "where is this specific record"
    is an addressed lookup, not a search, and the ruling excludes retired episodes from
    *search*, never from retrieval by name.

    Two refusals rather than answers, both because the alternative is a plausible wrong
    answer: a store that is not there is not a store with no such episode (trap 5), and
    an id present in BOTH directories is a half-retired store, not a choice between two
    copies. The second one is what makes the half-retirement refusal reach fetch and the
    writer, not only the scanning readers — this seam is the one they share.

    First check, before anything else touches the filesystem: the id must match the
    store's own grammar (ID_RE, section 2). A caller-handed id (fetch/neighbours'
    anchor fetch, and every other reader routed through this seam) is never validated
    upstream the way a LISTED id is (iter_episode_ids -> _layout_episode_ids runs every
    filename through episode_id_for() before it becomes a candidate) — without this
    check, a crafted id containing `..` path-traversal segments would resolve outside
    episodes/ entirely (issue #321). A malformed id can never legitimately exist, so
    `None` is the correct, contract-preserving answer here — not a new exception type."""
    if not ID_RE.fullmatch(episode_id):
        return None
    _require_store_layout(root)
    found = [
        root / sub / f"{episode_id}.md"
        for sub in (ACTIVE_DIR, RETIRED_DIR)
        if (root / sub / f"{episode_id}.md").exists()
    ]
    if len(found) > 1:
        _reject_half_retired({episode_id}, {episode_id})
    return found[0] if found else None


def _new_episode_path(episode_id: str, root: Path) -> Path:
    """Where a brand-new (always-active) episode is written. Not one of section 7's five
    named seams (create is g2's own concern, not a retrieval primitive), but it is
    exactly as layout-dependent as they are, so it is isolated here the same way."""
    return root / ACTIVE_DIR / f"{episode_id}.md"


def is_episode_in_ordinary_search(episode_id: str, root: Path) -> bool:
    """Per-id membership seam (section 7), bound to Option A: a directory check.

    This is the structural win the ruling buys. Membership is a filesystem fact, so a
    malformed, hand-edited, or forged `- status: retired` line in a free-text field
    cannot move an episode between sets — there is no field to parse and therefore no
    parse to fool.

    Like the other two read seams it refuses an absent store rather than answering about
    one: "no, that episode is not in ordinary search" and "there is no store here" are
    different facts, and a predicate that collapses them hands its caller a False that
    means nothing."""
    _require_store_layout(root)
    return (root / ACTIVE_DIR / f"{episode_id}.md").exists()


def apply_retirement(
    episode: Episode,
    reason: str,
    *,
    retired_at: str = "",
    consolidated_into: str = "",
    superseded_by: str = "",
) -> None:
    """THE retirement write-side seam (section 7): the entire CONTENT effect of a retire
    op. The writer must call this and never inline a field-only write or a file-move at
    the call site — the layout effect (the file moves into the archive) is expressed
    separately, in the write plan built by _Transaction.write_plan(), which asks
    destination_for() (below) for the destination.

    This function only ever mutates the in-memory Episode; it performs no I/O itself, so
    the all-or-nothing guarantee (C4) never depends on ordering retirements before other
    ops — and, since the field update and the move are two halves of ONE write plan
    entry, no plan this writer builds can disagree with itself: "fields updated but file
    not moved" (or the reverse) has no representation in it.

    That is a claim about the PLAN, and it is as far as the claim goes. It does not say
    the store can never be half-retired: a hard kill between the placement of the archived
    copy and the removal of the source runs no compensation at all, which is why
    _reject_half_retired() exists and why every read seam and the writer's own pre-flight
    check for that residue rather than assuming it away."""
    episode.status = "retired"
    episode.retired_reason = reason
    episode.retired_at = retired_at
    episode.consolidated_into = consolidated_into
    episode.superseded_by = superseded_by


def destination_for(episode: Episode, root: Path, current_path: Path) -> Path:
    """The layout-dependent HALF of retiring, bound to Option A: where should this
    episode's file live NOW, given its current state and where it currently is?

    The whole routing decision lives here, including the test on the episode's own
    status, so no caller anywhere reads that field to decide a path. That containment is
    the point: a caller that branched on `status` itself and then picked a directory
    would be an inlined layout check wearing a delegation's clothes, and it is exactly
    what §7's seam table exists to prevent.

    Isolated from apply_retirement()'s field diff so the two stay independently testable,
    and so the move is expressed once — the write plan then carries it, which is what
    makes the field update and the move land or fail together (see _Transaction.commit)."""
    if episode.status == "retired":
        return root / RETIRED_DIR / f"{episode.episode_id}.md"
    return current_path


# --- id assignment (EPISODE_STORE.md section 2) -------------------------------------


def _next_episode_id(run: str, known_ids: set[str]) -> str:
    """Zero-agent-effort id assignment: scan existing <run>-*.md basenames (across
    every episode for that run regardless of retirement status — a retired episode's
    sequence number is still taken) for the current max and increment. No counter
    file, no UUID.

    The scan is over the run's FLATTENED stem (`run_to_id_stem`), because that is
    what the ids on disk carry. Scanning the raw run instead would find nothing for
    a nested run and hand out `-001` forever, overwriting the previous episode."""
    prefix = f"{run_to_id_stem(run)}-"
    max_seq = 0
    for eid in known_ids:
        if eid.startswith(prefix):
            suffix = eid[len(prefix) :]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))
    return f"{prefix}{max_seq + 1:03d}"


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
        elif kind == "restate-assertion":
            _validate_restate_assertion(op)
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
        raise EpisodeDeltaError(
            f"create.mechanical.run: {run!r} must be kebab-case, optionally nested "
            f"with '/' ({RUN_RE.pattern}) — a work-id like "
            "'epic-418-followon/commander-424' is fine; an empty segment, '..' and an "
            "absolute path are not"
        )

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


def _validate_restate_assertion(op: dict) -> None:
    """The op takes EXACTLY id, assertion, statement and history — nothing else.

    The extra-field check runs FIRST, before the per-field checks, so a delta that
    misfiles `lifecycle-standing` onto a restatement is refused for the reason it is
    actually wrong (that field has no business here) rather than passing quietly because
    the four required fields happened to be well-formed alongside it.

    `statement` goes through the same _require_str() as create's own statement, so
    single-line enforcement on the new text is not a second implementation that could
    drift from create's — it IS create's."""
    extra = set(op) - set(RESTATE_ALLOWED_FIELDS)
    if extra:
        raise EpisodeDeltaError(
            f"restate-assertion: misfiled field(s) {sorted(extra)} — the op accepts "
            f"EXACTLY {RESTATE_ALLOWED_FIELDS}, no more, no less. lifecycle-standing, "
            "strength and kind in particular are NOT restated: a restatement changes "
            "wording, and epistemic status moves only through amend-assertion."
        )
    episode_id = op.get("id")
    if not isinstance(episode_id, str) or not ID_RE.fullmatch(episode_id):
        raise EpisodeDeltaError(f"restate-assertion: invalid episode id {episode_id!r}")
    assertion_id = op.get("assertion")
    if not isinstance(assertion_id, str) or not re.fullmatch(r"[ad][0-9]+", assertion_id):
        raise EpisodeDeltaError(f"restate-assertion: invalid assertion id {assertion_id!r}")
    _require_str(op, "statement", "restate-assertion")
    _require_str(op, "history", "restate-assertion")


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


def _place(tmp_path: Path, final_path: Path) -> None:
    """Move one staged temp file onto its final path. A single os.replace() is atomic on
    both POSIX and Windows, and the temp file is created in the SAME directory as its
    destination, so this is always a same-filesystem rename rather than a copy.

    A named function rather than an inlined call so a test can inject a failure at
    exactly this step — the same discipline the write step's write_text_exact() seam
    already made possible."""
    os.replace(tmp_path, final_path)


def _remove_superseded(path: Path) -> None:
    """Remove the source path a moved episode has left behind — the second half of a
    retirement's move, and the only place in the module that deletes a live episode file.

    Named for the same reason as _place(): this is the exact step whose failure would
    leave an id in BOTH active/ and retired/, so a test has to be able to force it."""
    path.unlink(missing_ok=True)


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
        ep = parse_episode(read_text_exact(path))
        self.loaded[episode_id] = ep
        self.original_paths[episode_id] = path
        return ep

    def create(self, ep: Episode) -> None:
        self.loaded[ep.episode_id] = ep
        self.known_ids().add(ep.episode_id)
        self.original_paths[ep.episode_id] = _new_episode_path(ep.episode_id, self.root)

    def write_plan(self) -> tuple[dict[Path, str], set[Path]]:
        """Renders every touched episode to its FINAL destination path. Returns
        (path -> text to write, paths to delete) — deletes only happen for a retire,
        where the file moves into the archive and the old active/ path must go.

        C6, half-retirement, is answered here first and by construction: a retirement's
        field update and its move are not two operations that could disagree. The updated
        CONTENT is only ever rendered to the NEW path, so "fields updated but file not
        moved" has no representation in this plan at all, and neither does "moved but
        fields not updated" — there is exactly one entry, and it carries both halves.
        What remains is only whether that entry, plus its paired delete, lands as a unit;
        commit() below makes it do so."""
        writes: dict[Path, str] = {}
        deletes: set[Path] = set()
        for episode_id, ep in self.loaded.items():
            original_path = self.original_paths[episode_id]
            dest = destination_for(ep, self.root, original_path)
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

        g4 (C6, half-retirement). Binding Option A gave the placement phase a SECOND
        step — a retirement both writes `retired/<id>.md` and removes `active/<id>.md` —
        and a failure between those two steps would leave the id present in BOTH
        directories: retired by content, still in the ordinary-search set by directory.
        That is precisely the half-retired store the gate must rule out, and the old
        placement loop had no answer for it (it removed sources in an unguarded loop
        after an unguarded replace loop).

        So the placement phase now snapshots the prior bytes of every path it is about
        to overwrite or remove, and on ANY failure restores all of them and deletes the
        paths it newly created. A failed retirement therefore ends with the episode
        wholly un-retired — active/<id>.md back with its original bytes, no
        retired/<id>.md — rather than half of each. The compensating restore is
        deliberately not silent: if it fails too, that exception propagates.

        Honest limit, unchanged in kind: this is compensation, not atomicity. A hard
        process kill or power loss BETWEEN two of these calls runs no compensation at
        all, and nothing in EPISODE_STORE.md's markdown-in-git constraint provides a
        journal/WAL to close that. What is closed is every failure the process itself
        survives to observe — an OSError from a locked file, a permission denial, a full
        disk — which is the class this store can actually defend against. The residue
        that remains is made LOUD at every seam that could meet it: the enumeration seam
        for scanning readers, resolve_episode_path() for fetch-by-id, and apply_delta()'s
        own pre-flight scan for every write op — not only the ops that scan anyway."""
        writes, deletes = self.write_plan()
        staged: list[tuple[Path, Path]] = []
        try:
            for final_path, text in writes.items():
                final_path.parent.mkdir(parents=True, exist_ok=True)
                tmp_path = final_path.parent / f".{final_path.name}.tmp-{uuid.uuid4().hex}"
                write_text_exact(tmp_path, text)
                staged.append((tmp_path, final_path))
        except Exception:
            for tmp_path, _ in staged:
                tmp_path.unlink(missing_ok=True)
            raise

        # Prior bytes of every path the placement phase can disturb. None means "did not
        # exist", which the rollback below reads as "delete it again".
        prior: dict[Path, bytes | None] = {
            path: (path.read_bytes() if path.exists() else None)
            for path in list(writes) + sorted(deletes)
        }

        try:
            for tmp_path, final_path in staged:
                _place(tmp_path, final_path)
            for path in deletes:
                _remove_superseded(path)
        except Exception:
            for path, original in prior.items():
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(original)
            raise
        finally:
            for tmp_path, _ in staged:
                tmp_path.unlink(missing_ok=True)  # no-op once moved


def _unhandled_op_kind_message(kind: str, site: str) -> str:
    """The message behind the `else: raise` both op dispatch sites now carry.

    Before this, apply_delta() and _dry_run_log() each dispatched on op kind through an
    if/elif chain with NO else. validate_delta() rejects a kind outside OP_KINDS, so the
    two chains only ever saw known kinds — but they are SEPARATE chains, and nothing tied
    them together. An op added to OP_KINDS and wired into only one of them was silently
    skipped by the other: for a dry run that meant no log line, no error, exit 0 and a
    cheerful "DRY RUN — no write", i.e. a caller told its op was fine when the op had
    never been looked at. A silent skip in the store's only write path is the worst
    available failure mode, so both chains now end here instead of falling through."""
    return (
        f"internal: op kind {kind!r} is in OP_KINDS but has no branch in {site}() — "
        "an op must be registered at BOTH dispatch sites (apply_delta and _dry_run_log), "
        "or it is silently skipped at the one that missed it"
    )


def apply_delta(root: Path, delta: dict) -> list[str]:
    work_id, ops = validate_delta(delta)
    # The writer, and only the writer, may bring the layout into being: a create into a
    # store root that does not exist yet is how a store starts. Readers refuse instead
    # (_require_store_layout), so a typo'd --store-root can never read as "empty".
    ensure_store_layout(root)
    tx = _Transaction(root)
    # Then check the store BEFORE applying any op, rather than only where an op happens
    # to look. known_ids() is the full enumeration seam — strays, misfiled files, an id
    # in both directories — so every op inherits the refusal, not just `create` (whose
    # id assignment used to be the only caller). A retire that committed against a store
    # already known to be corrupt was g4's F2: loud in one hand, silent in the other.
    tx.known_ids()
    log: list[str] = []

    for op in ops:
        kind = op["op"]
        if kind == "create":
            log.append(_apply_create(tx, op))
        elif kind == "amend-assertion":
            log.append(_apply_amend_assertion(tx, op))
        elif kind == "restate-assertion":
            log.append(_apply_restate_assertion(tx, op))
        elif kind == "retire":
            log.append(_apply_retire(tx, op))
        else:
            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "apply_delta"))

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


def _restatement_history_line(reason: str, original_statement: str) -> str:
    """Build the ONE history line a restatement appends.

    Deliberately a named function taking the original statement as an argument the CALLER
    of this function cannot forge: _apply_restate_assertion() passes the statement it read
    off the parsed record, and the delta has no field that reaches this text. That is the
    protected property — a restatement must never be able to claim the record said
    something other than what it said.

    Format: `restated — <reason> — original statement was: <original>`. The original goes
    LAST, behind a fixed marker, and is exactly the text following the marker's LAST
    occurrence — read it from the right (str.rpartition), never by searching forward. The
    marker is NOT unique on the line: the reason is free text and may contain it, which
    puts two markers on one line. Nothing the record said is destroyed when that happens
    (the true original is still the tail, verbatim), but a reader that splits on the FIRST
    marker gets text the caller wrote rather than what the record said. Both halves are
    single-line-validated before they get here — the reason by _require_str() on the op,
    the original by the same guard at the time it was written — so the rendered line cannot
    grow a second line and forge a store field."""
    return f"restated — {reason} — original statement was: {original_statement}"


def _apply_restate_assertion(tx: _Transaction, op: dict) -> str:
    episode_id = op["id"]
    ep = tx.load(episode_id)
    assertions = ep.all_assertions()
    assertion_id = op["assertion"]
    assertion = assertions.get(assertion_id)
    if assertion is None:
        raise EpisodeDeltaError(f"restate-assertion {episode_id}.{assertion_id}: no such assertion")
    # Read the original BEFORE overwriting it, and build the history line from that read
    # rather than from anything the delta carries. Surgical in exactly the same sense as
    # _apply_amend_assertion(): only this assertion's statement changes, plus one appended
    # history line. kind/strength/lifecycle-standing, every sibling assertion, every
    # mechanical line and the retirement block are left exactly as parsed.
    original_statement = assertion.statement
    assertion.statement = op["statement"].strip()
    assertion.history.append(
        _restatement_history_line(op["history"].strip(), original_statement)
    )
    return f"restated {episode_id}.{assertion_id}"


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
    """Validate and compute the write-plan, but never call commit().

    Runs the same store pre-flight as apply_delta() so a dry run answers about the store
    that is really there — but never creates the layout, because a dry run writes
    nothing at all, including a directory."""
    work_id, ops = validate_delta(delta)
    tx = _Transaction(root)
    tx.known_ids()
    log: list[str] = []
    for op in ops:
        kind = op["op"]
        if kind == "create":
            log.append(_apply_create(tx, op))
        elif kind == "amend-assertion":
            log.append(_apply_amend_assertion(tx, op))
        elif kind == "restate-assertion":
            log.append(_apply_restate_assertion(tx, op))
        elif kind == "retire":
            log.append(_apply_retire(tx, op))
        else:
            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "_dry_run_log"))
    log.append("DRY RUN — no write")
    return log


if __name__ == "__main__":
    raise SystemExit(main())
