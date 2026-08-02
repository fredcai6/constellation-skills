#!/usr/bin/env python
"""Orient an agent against a repo's architecture map -- or REPORT that it cannot.

The deficiency this closes is **primacy and contract, not path**. Resolving a
path to `docs/architecture/` is the easy half and several repos already do it.
The half that has to hold is the **reported degraded mode**: degrading is fine,
degrading *silently* is refused. Degraded is the COMMON case -- most repos,
including this one, have no `docs/architecture/` at all -- so the degraded
record is a first-class output, not an error path.

Subcommands
-----------
    map_orient.py orient             --root ABS --work-id ID [--entrypoint REL]
                                     [--substitute REL ...] [--unmapped TEXT ...]
                                     [--escalation TEXT]
    map_orient.py verify-orientation --root ABS --work-id ID [--report-only]
    map_orient.py verify-frame       --root ABS --work-id ID [--report-only]
    map_orient.py --self-test

`--report-only` is the gate-vs-report dial: the verdict printed is identical,
only its blocking-ness moves, so a ruling to gate or un-gate a step is a flag
flip in the template's command string rather than a rebuild here.

Where the two checks are wired, and why ASYMMETRICALLY
------------------------------------------------------
`verify-orientation` is a command postcondition at the Commander spine's
**context** step; `verify-frame` is one at the **plan** step. `verify-frame`
must NEVER run at context: no frame exists there (context precedes `understand`
and `plan`), and the only way to make it pass there is to let an ABSENT frame
pass -- which is precisely the refusal the whole check is built on. The road not
to take, recorded because the cheap symmetric resolution is tempting and a cold
critic already BLOCKed one plan over it: if `verify-frame` ever has to be
context-safe, give it a step-scoped mode; never a vacuous pass.

Exit-code vocabulary (FROZEN)
-----------------------------
The engine records only ``{cmd, exit, shell}`` for a command check and
**discards stdout**, so for anything downstream of the engine the exit code is
the only signal that survives. Three codes are already spoken for by machinery
this module does not control, and a mistyped flag must never be
indistinguishable from a truthful verdict:

    1    an unhandled Python traceback
    2    `argparse` usage error (unknown flag, missing argument)
    126  a command found but not executable
    127  the engine's synthesized "no POSIX shell found"

So every semantic code sits **above** the traceback/argparse range and
**below** the shell range -- an occupied-code-free band:

    0    contract satisfied: RESOLVED, or a DEGRADED record fully discharged,
         or a frame whose citations resolve
    10   the map contract is NOT discharged -- a DEGRADED record missing at
         least one of `substitutes` / `unmapped` / `escalation` (or one of them
         filler), or a frame whose citations do not resolve (`verify-frame`)
    11   UNRESOLVABLE-ROOT -- could not look: `--root` is not a proven repo root
    12   a required INPUT DOCUMENT is missing or unusable: the receipt, or --
         for `verify-frame` -- the mission frame itself
    13   `--self-test` falsification floor failed

`verify-frame` adds NO new codes. Two of the frozen ones carry a slightly wider
reading, stated here rather than left implicit: 12 was "the receipt is missing"
and is now "a required input document is missing", and 10 was "the degraded
record is undischarged" and is now "the map contract is undischarged". Both are
the same verdict about the same contract, reached one document later.

`0` is the only success code; `10`-`13` are the semantic verdicts; nothing this
module returns can be confused with `1`, `2`, `126`, or `127`.

Reserved stdout first line
--------------------------
The first line of stdout is ALWAYS exactly one reserved literal -- never blank,
never a bare count:

    RESOLVED  DEGRADED-NO-MAP  DEGRADED-EMPTY-MAP  DEGRADED-UNPARSEABLE
    UNRESOLVABLE-ROOT                      (the five `orient` verdicts)
    RECEIPT-MISSING                        (no usable receipt)
    FRAME-OK  FRAME-MISSING  FRAME-REFUSED (`verify-frame`)

The agent runs `orient` itself, so stdout is real there. The engine only ever
sees the exit code, which is why the table above carries the contract.

`orient` never prints an anchor id, and `verify-frame` echoes back only ids the
frame it is checking already contains. If the tool handed over the ids, citing
one would stop being evidence the map was read -- an agent could paste back what
the tool told it. The proof has to come from somewhere the tool did not give.

Resolution rule (ordered; first hit wins; EVERY candidate is still recorded)
----------------------------------------------------------------------------
    1. `--entrypoint REL`, when given
    2. `docs/architecture/generated/map.json` -- parses, >=1 `nodes[].id`
    3. `docs/architecture/index.md`
    4. `docs/architecture/` carrying >=1 non-empty `packets/*.md`

All four are evaluated and recorded in `candidates_tried[]` even after an
earlier one hits: the receipt is a delivery record of what was looked for, not
a first-hit lookup log.

RESOLVED requires CITABLE CONTENT, not mere existence. Anchors are extracted
with a deliberately format-agnostic token scan::

    \\b(struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\\-]+\\b

>=1 unique real id makes a candidate citable. A `<placeholder>` cannot match
(``<`` is outside the id character class), so a scaffolded-but-unfilled
template yields nothing and reads DEGRADED-UNPARSEABLE. This is NOT coupled to
`build_architecture_map.parse_packet` on purpose: that parser requires this
repo's bold-field packet template, while the one repo with a real map
(f1Brainz) writes YAML fences, so the strict parser returns ZERO nodes on it
(measured: 0 parsed / 16 failed). A false RESOLVED is strictly worse than an
honest DEGRADED -- it satisfies the entire contract on a map with no content.

"Could not look" vs "looked and found nothing"
----------------------------------------------
UNRESOLVABLE-ROOT requires a POSITIVE repo-root proof to fail, never an absence
test: `.git` present at the root, or `git -C <root> rev-parse --show-toplevel`
succeeding AND naming that same root. A bare non-repo directory is therefore
UNRESOLVABLE-ROOT ("I could not look"), not DEGRADED-NO-MAP ("I looked and the
map is not there"). Those two differ in exactly one bit and must never collapse.

Receipt schema (`.agent-work/<work-id>/map-orientation.json`)
------------------------------------------------------------
    schema_version   int     this file's schema revision
    work_id          str     the work id the receipt belongs to
    root             str     absolute repo root, posix separators
    mode             str     one of the five reserved `orient` verdicts
    entrypoint       str?    repo-relative path of the winning candidate, else null
    anchor_count     int     unique citable anchor ids at the entrypoint (0 when degraded)
    candidates_tried list    [{order, kind, path, exists, outcome, anchor_count, note}]
    substitutes      list    [{path, content_hash, source}] -- read INSTEAD of a map
    fallbacks_probed list    [{path, exists, content_hash}] -- the FIXED fallback
                             set, as the filesystem answers it
    unmapped         list    [str] -- what stayed unmapped, stated plainly
    escalation       str?    what is being escalated and to whom
    emitted_at       str     UTC ISO-8601 timestamp

`substitutes` are **hash-pinned**: the sha256 of each substitute's content is
recorded here so a later frame check compares against this committed prior
declaration rather than a same-breath assertion. A substitute that could not be
read carries `content_hash: null` and **refuses** the discharge -- the pin is
validated by SHAPE (64 hex chars), so no sentinel, typo, or truncated digest
can stand in for one. A single mistyped path must not be able to satisfy the
whole contract.

Each substitute also carries a provenance `source`: `known-fallback` when the
path is in the fixed corpus set (`README.md`, `AGENTS.md`, `CLAUDE.md`, a
`docs/` index) AND present on disk, `agent-declared` otherwise. `orient` probes
that whole set independently into `fallbacks_probed`. This converts HALF of the
degraded check's self-attestation into an oracle the agent does not author --
whether one of those paths resolved is the filesystem's answer, not the agent's.
It does **not** close the gap: the agent still chooses what to declare, and
anything outside the set stays labelled unverified. Do not describe it as making
the degraded check sound; it converts part of it.

Honest limits
-------------
- The token scan proves citable *shape*, not correctness: a well-formed example
  id inside prose is indistinguishable from a real anchor. It refuses empty and
  unfilled maps; it does not audit a populated one.
- Nothing here judges whether the map is accurate, current, or complete. Map
  freshness and drift are the Cartographer's job.
- The degraded record's *content* is prose the agent writes. This module can
  only check the three fields are present and are not filler -- it cannot tell a
  thoughtful substitute list from a lazy one. That judgment stays human.
- When `git` is unavailable and `.git` is absent, the verdict is
  UNRESOLVABLE-ROOT by design. Absence of proof is reported as "could not
  look", never silently upgraded to a map verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

SCHEMA_VERSION = 1

# --- reserved stdout literals -------------------------------------------------
MODE_RESOLVED = "RESOLVED"
MODE_DEGRADED_NO_MAP = "DEGRADED-NO-MAP"
MODE_DEGRADED_EMPTY_MAP = "DEGRADED-EMPTY-MAP"
MODE_DEGRADED_UNPARSEABLE = "DEGRADED-UNPARSEABLE"
MODE_UNRESOLVABLE_ROOT = "UNRESOLVABLE-ROOT"
RECEIPT_MISSING = "RECEIPT-MISSING"
FRAME_OK = "FRAME-OK"
FRAME_MISSING = "FRAME-MISSING"
FRAME_REFUSED = "FRAME-REFUSED"

ORIENT_MODES = (
    MODE_RESOLVED,
    MODE_DEGRADED_NO_MAP,
    MODE_DEGRADED_EMPTY_MAP,
    MODE_DEGRADED_UNPARSEABLE,
    MODE_UNRESOLVABLE_ROOT,
)
RESERVED_FIRST_LINES = ORIENT_MODES + (
    RECEIPT_MISSING,
    FRAME_OK,
    FRAME_MISSING,
    FRAME_REFUSED,
)

# --- frozen exit vocabulary (see the module docstring for why these values) ---
EXIT_OK = 0
EXIT_DEGRADED_UNDISCHARGED = 10
EXIT_UNRESOLVABLE_ROOT = 11
EXIT_RECEIPT_UNUSABLE = 12
EXIT_SELF_TEST_FAILED = 13

SEMANTIC_EXIT_CODES = (
    EXIT_DEGRADED_UNDISCHARGED,
    EXIT_UNRESOLVABLE_ROOT,
    EXIT_RECEIPT_UNUSABLE,
    EXIT_SELF_TEST_FAILED,
)
# Codes this module does not own and must never collide with.
OCCUPIED_EXIT_CODES = (1, 2, 126, 127)

ANCHOR_RE = re.compile(
    r"\b(?:struct|capability|event|constraint|assumption|claim|decision)"
    r":[A-Za-z0-9_.\-]+\b"
)

MAP_DIR = "docs/architecture"
GENERATED_MAP = "docs/architecture/generated/map.json"
INDEX_MD = "docs/architecture/index.md"

OUTCOME_HIT = "hit"
OUTCOME_ABSENT = "absent"
OUTCOME_EMPTY = "empty"
OUTCOME_UNPARSEABLE = "unparseable"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


# =============================================================================
# Pure decision layer -- no filesystem, no subprocess, no clock.
# =============================================================================


@dataclass(frozen=True)
class Candidate:
    """One entrypoint the resolver looked for, and what it found there."""

    order: int
    kind: str
    path: str
    exists: bool
    has_content: bool
    anchor_count: int
    note: str


@dataclass(frozen=True)
class RootProof:
    """Whether `--root` was POSITIVELY proven to be a repo root, and by what."""

    proven: bool
    evidence: str


@dataclass(frozen=True)
class Orientation:
    root: str
    mode: str
    entrypoint: str | None
    anchor_count: int
    candidates: tuple[Candidate, ...]
    root_evidence: str


def scan_anchors(text: str) -> list[str]:
    """PURE. Unique citable anchor ids in `text`, in first-seen order.

    Format-agnostic on purpose: it reads YAML-fenced packets, bold-field
    packets, generated JSON, and free prose identically. A `<placeholder>`
    cannot match -- `<` is outside the id character class -- so an unfilled
    template scaffold yields the empty list.
    """
    seen: dict[str, None] = {}
    for match in ANCHOR_RE.finditer(text):
        seen.setdefault(match.group(0), None)
    return list(seen)


def candidate_is_citable(candidate: Candidate) -> bool:
    """PURE. A candidate counts as a hit ONLY when it yields citable content.

    Falsification floor pins this predicate (tests/test_mutation_floor.py):
    weakening it to `candidate.exists` makes a scaffolded-but-empty map read
    RESOLVED, which satisfies the whole contract on a map with no content.
    """
    return candidate.anchor_count >= 1


def candidate_outcome(candidate: Candidate) -> str:
    """PURE. `hit` | `absent` | `empty` | `unparseable`."""
    if candidate_is_citable(candidate):
        return OUTCOME_HIT
    if not candidate.exists:
        return OUTCOME_ABSENT
    if not candidate.has_content:
        return OUTCOME_EMPTY
    return OUTCOME_UNPARSEABLE


def prove_repo_root(root_abs: str, dot_git_present: bool, git_toplevel: str | None) -> RootProof:
    """PURE. POSITIVE repo-root proof -- never an absence test (#265).

    "I could not look" and "I looked and found nothing" are different verdicts.
    Only affirmative evidence -- a `.git` entry at the root, or git naming this
    exact path as the toplevel -- proves we were entitled to look.
    """
    if dot_git_present:
        return RootProof(True, "positive: .git entry present at root")
    if git_toplevel is not None and _same_path(git_toplevel, root_abs):
        return RootProof(True, "positive: git rev-parse --show-toplevel names this root")
    if git_toplevel is not None:
        return RootProof(
            False,
            f"no positive proof: git toplevel is {git_toplevel!r}, not this root",
        )
    return RootProof(
        False,
        "no positive proof: no .git entry and git rev-parse --show-toplevel did not succeed",
    )


def _same_path(a: str, b: str) -> bool:
    """PURE. Case- and separator-insensitive path identity (Windows-safe)."""
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def determine_mode(root_proof: RootProof, candidates: Sequence[Candidate]) -> str:
    """PURE. The reserved verdict literal for this orientation."""
    if not root_proof.proven:
        # Falsification floor pins this branch (tests/test_mutation_floor.py):
        # collapsing it into DEGRADED-NO-MAP is the #315 failure mode wearing a
        # friendly face -- "could not look" reported as "looked, found nothing".
        return MODE_UNRESOLVABLE_ROOT
    for candidate in candidates:
        if candidate_is_citable(candidate):
            return MODE_RESOLVED
    outcomes = [candidate_outcome(candidate) for candidate in candidates]
    if all(outcome == OUTCOME_ABSENT for outcome in outcomes):
        return MODE_DEGRADED_NO_MAP
    if OUTCOME_UNPARSEABLE in outcomes:
        return MODE_DEGRADED_UNPARSEABLE
    return MODE_DEGRADED_EMPTY_MAP


def build_orientation(
    root_abs: str, root_proof: RootProof, candidates: Sequence[Candidate]
) -> Orientation:
    """PURE. Fold the root proof and every candidate into one verdict."""
    mode = determine_mode(root_proof, candidates)
    hit = None
    if mode == MODE_RESOLVED:
        hit = next(c for c in candidates if candidate_is_citable(c))
    return Orientation(
        root=root_abs,
        mode=mode,
        entrypoint=hit.path if hit is not None else None,
        anchor_count=hit.anchor_count if hit is not None else 0,
        candidates=tuple(candidates),
        root_evidence=root_proof.evidence,
    )


def classify_generated_map(text: str) -> tuple[bool, list[str], str]:
    """PURE. (has_content, anchors, note) for a `generated/map.json` candidate."""
    if not text.strip():
        return (False, [], "empty file")
    try:
        data = json.loads(text)
    except ValueError as exc:
        return (True, [], f"parses as neither: json error: {exc}")
    nodes = data.get("nodes") if isinstance(data, dict) else None
    if not isinstance(nodes, list):
        return (True, [], "parses but carries no nodes[] array")
    node_ids = [
        n.get("id")
        for n in nodes
        if isinstance(n, dict) and isinstance(n.get("id"), str) and n["id"].strip()
    ]
    if not node_ids:
        return (True, [], "parses but carries no nodes[].id")
    anchors = scan_anchors(text)
    if not anchors:
        return (True, [], f"{len(node_ids)} nodes[].id, none citable")
    return (True, anchors, f"{len(node_ids)} nodes[].id, {len(anchors)} unique anchors")


def classify_markdown(text: str) -> tuple[bool, list[str], str]:
    """PURE. (has_content, anchors, note) for a markdown candidate."""
    if not text.strip():
        return (False, [], "empty file")
    anchors = scan_anchors(text)
    if not anchors:
        return (True, [], "content but no citable anchor id (unfilled template?)")
    return (True, anchors, f"{len(anchors)} unique anchors")


def classify_packets(packet_texts: dict[str, str]) -> tuple[bool, list[str], str]:
    """PURE. (has_content, anchors, note) for the `packets/*.md` candidate."""
    non_empty = {name: text for name, text in packet_texts.items() if text.strip()}
    if not non_empty:
        return (False, [], f"{len(packet_texts)} packet(s), none non-empty")
    seen: dict[str, None] = {}
    for name in sorted(non_empty):
        for anchor in scan_anchors(non_empty[name]):
            seen.setdefault(anchor, None)
    anchors = list(seen)
    if not anchors:
        return (True, [], f"{len(non_empty)} non-empty packet(s), no citable anchor id")
    return (True, anchors, f"{len(non_empty)} non-empty packet(s), {len(anchors)} unique anchors")


# Values that occupy a required field without saying anything. A degraded
# record filled with these is a refusal wearing a discharge's clothes.
FILLER_VALUES = frozenset(
    {"-", "--", "n/a", "n\\a", "na", "none", "nil", "null", "tbd", "todo", "?", "unknown"}
)

# A pin is a sha256 hex digest and nothing else.
CONTENT_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

RECEIPT_REQUIRED_FIELDS = (
    "schema_version",
    "work_id",
    "root",
    "mode",
    "entrypoint",
    "anchor_count",
    "candidates_tried",
    "substitutes",
    "unmapped",
    "escalation",
    "emitted_at",
)


def is_filler(value: object) -> bool:
    """PURE. True when a field is absent, empty, a placeholder, or says nothing."""
    if not isinstance(value, str):
        return True
    text = value.strip().strip("`").strip()
    if not text:
        return True
    if text.startswith("<") and text.endswith(">"):
        return True
    return text.lower() in FILLER_VALUES


def is_content_hash(value: object) -> bool:
    """PURE. True only for a real sha256 hex digest.

    Checking the SHAPE, not merely "is it non-empty", is what stops a sentinel,
    a typo, or a truncated digest from passing as a hash-pin. A substitute that
    could not be read has NO hash, and a record that cannot pin what it read
    has not discharged anything.
    """
    if not isinstance(value, str):
        return False
    return CONTENT_HASH_RE.match(value.strip().lower()) is not None


def substitute_problems(receipt: dict) -> list[str]:
    """PURE. Why the declared substitutes fail to pin; empty means they pin."""
    entries = receipt.get("substitutes")
    if not isinstance(entries, list):
        return ["substitutes is not a list"]
    if not entries:
        return ["substitutes is empty -- a degraded run read SOMETHING instead of the map"]
    problems = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"substitutes[{index}] is not an object")
            continue
        if is_filler(entry.get("path")):
            problems.append(f"substitutes[{index}] has no real path: {entry.get('path')!r}")
        if not is_content_hash(entry.get("content_hash")):
            problems.append(
                f"substitutes[{index}] {entry.get('path')!r} is not hash-pinned "
                f"(content_hash={entry.get('content_hash')!r}) -- an unreadable or "
                "nonexistent substitute cannot discharge the record"
            )
    return problems


def substitutes_declared(receipt: dict) -> bool:
    """PURE. >=1 substitute, each with a real path AND a real sha256 pin.

    An empty `substitutes` list is a refusal, not a pass: a degraded run read
    SOMETHING instead of the map, and the hash pins it so a later frame check
    compares against this prior declaration rather than a same-breath claim.

    A substitute that could not be read is likewise a refusal. Emitting a
    sentinel there and accepting it would let a single typo -- a path that does
    not exist -- discharge the whole contract at exit 0, which is precisely the
    hole this module exists to close.
    """
    return not substitute_problems(receipt)


def unmapped_declared(receipt: dict) -> bool:
    """PURE. >=1 plainly-stated thing that stayed unmapped."""
    entries = receipt.get("unmapped")
    if not isinstance(entries, list) or not entries:
        return False
    return not any(is_filler(entry) for entry in entries)


def escalation_declared(receipt: dict) -> bool:
    """PURE. A real statement of what is being escalated, to whom."""
    return not is_filler(receipt.get("escalation"))


def degraded_record_is_complete(receipt: dict) -> bool:
    """PURE. A DEGRADED record discharges ONLY with all three declarations.

    Falsification floor pins this `all` (tests/test_mutation_floor.py): under
    `any`, a record carrying one field and omitting two would pass, which is
    exactly the silent-degradation this module exists to refuse.
    """
    checks = (
        substitutes_declared(receipt),
        unmapped_declared(receipt),
        escalation_declared(receipt),
    )
    return all(checks)


def missing_degraded_fields(receipt: dict) -> list[str]:
    """PURE. Which of the three declarations are missing or filler."""
    missing = []
    problems = substitute_problems(receipt)
    if problems:
        missing.append("substitutes (what you read INSTEAD of a map, each hash-pinned)")
        missing.extend(f"    {problem}" for problem in problems)
    if not unmapped_declared(receipt):
        missing.append("unmapped (what stayed unmapped, stated plainly)")
    if not escalation_declared(receipt):
        missing.append("escalation (what you are escalating, and to whom)")
    return missing


def receipt_problems(receipt: object, work_id: str) -> list[str]:
    """PURE. Structural problems with a receipt; empty means well-formed."""
    if not isinstance(receipt, dict):
        return ["receipt is not a JSON object"]
    problems = [f"missing field: {f}" for f in RECEIPT_REQUIRED_FIELDS if f not in receipt]
    if receipt.get("schema_version") != SCHEMA_VERSION:
        problems.append(
            f"schema_version {receipt.get('schema_version')!r} != {SCHEMA_VERSION}"
        )
    if receipt.get("work_id") != work_id:
        problems.append(f"work_id {receipt.get('work_id')!r} does not match {work_id!r}")
    if receipt.get("mode") not in ORIENT_MODES:
        problems.append(f"mode {receipt.get('mode')!r} is not a reserved verdict")
    tried = receipt.get("candidates_tried")
    if not isinstance(tried, list):
        problems.append("candidates_tried is not a list")
    elif not tried and receipt.get("mode") != MODE_UNRESOLVABLE_ROOT:
        # An empty list is the TRUTHFUL record when we could not look at all;
        # anywhere else it means the delivery record was never written.
        problems.append("candidates_tried is empty -- there is no delivery record")
    if receipt.get("mode") == MODE_RESOLVED:
        if is_filler(receipt.get("entrypoint")):
            problems.append("RESOLVED but no entrypoint was recorded")
        anchors = receipt.get("anchor_count")
        if not isinstance(anchors, int) or anchors < 1:
            problems.append("RESOLVED but anchor_count < 1 -- nothing citable was found")
    return problems


def verify_verdict(receipt: object, work_id: str) -> tuple[str, int, list[str]]:
    """PURE. (reserved first line, exit code, problems) for `verify-orientation`."""
    problems = receipt_problems(receipt, work_id)
    if problems:
        mode = receipt.get("mode") if isinstance(receipt, dict) else None
        return (mode if mode in ORIENT_MODES else RECEIPT_MISSING, EXIT_RECEIPT_UNUSABLE, problems)
    mode = receipt["mode"]  # type: ignore[index]
    if mode in (MODE_RESOLVED, MODE_UNRESOLVABLE_ROOT):
        return (mode, exit_code_for(mode, True), [])
    complete = degraded_record_is_complete(receipt)  # type: ignore[arg-type]
    problems = [] if complete else missing_degraded_fields(receipt)  # type: ignore[arg-type]
    return (mode, exit_code_for(mode, complete), problems)


# =============================================================================
# Frame citation contract (`verify-frame`)
# =============================================================================
#
# The seam: anchor ids exist ONLY in the map, so citing one is set-membership
# proof the map was read. That turns "did the map inform the plan" into a
# question a machine can answer with no stochastic judgement.
#
# Know what this does and does not achieve. Measured against epic-298's baseline
# five runs, this check has **sensitivity 0/4 and specificity 0/1**: four runs
# cited map artifacts while exhibiting the defect (they would pass) and the one
# run that would fail it was correct to disengage. It ships as a **regression
# floor** so map-*ignoring* cannot silently return. It is NOT the fix for the
# measured defect, which is map-*lateness* and needs a harness hook the corpus
# does not own. It also inherits the late-anchor defect it was built beside:
# anchors-in-a-late-frame is compliance without sequence.

FRAME_NAME = "MISSION_FRAME.md"

# A path-shaped token in free markdown. Deliberately loose: everything it
# over-matches (`e.g`, `struct:app.api`) fails both the source-suffix and the
# fallback-set membership tests below and is silently ignored.
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*\.[A-Za-z0-9]{1,8}\b")

# Suffixes that make a cited path CODE. A frame whose only citations are these
# is a frame cut from code, which is the shape this whole module exists to
# refuse -- the map is what a frame is supposed to be cut from.
SOURCE_SUFFIXES = frozenset(
    {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
        ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".sh", ".ps1",
        ".sql", ".kt", ".swift", ".scala", ".lua", ".pl", ".r", ".vue", ".svelte",
    }
)

# The FIXED, corpus-declared fallback search order for the degraded case.
#
# The degraded check's declared weakness is that substitutes are SELF-SELECTED:
# it verifies the author cited what the author declared. Fixing the search order
# in the corpus and probing it on the filesystem closes HALF of that -- whether
# one of these resolved is answered by an oracle the agent does not author. It
# does NOT make the degraded check sound: the agent still chooses what to
# declare, and an agent-declared path outside this set stays labelled
# unverified. Do not describe this as closing the gap; it converts part of it.
KNOWN_FALLBACKS = ("README.md", "AGENTS.md", "CLAUDE.md", "docs/index.md", "docs/README.md")
KNOWN_FALLBACK_SET = frozenset(p.lower() for p in KNOWN_FALLBACKS)

#: A substitute found in KNOWN_FALLBACKS *and* present on disk -- the half an
#: independent oracle (the filesystem) confirms.
LABEL_KNOWN_FALLBACK = "known-fallback"
#: Anything else the agent declared. Allowed, but labelled UNVERIFIED so the
#: receipt distinguishes "resolved from the known fallback set" from "the agent
#: said so". An absent or unrecognised label reads as this one: the
#: conservative default, so an older receipt is never upgraded by omission.
LABEL_AGENT_DECLARED = "agent-declared"
SUBSTITUTE_LABELS = (LABEL_KNOWN_FALLBACK, LABEL_AGENT_DECLARED)


def normalize_cited_path(value: str) -> str:
    """PURE. Comparable form of a cited path: posix separators, lowercased."""
    return value.strip().strip("`").replace("\\", "/").lstrip("./").lower()


def cited_paths(text: str) -> list[str]:
    """PURE. Unique path-shaped tokens in `text`, in first-seen order."""
    seen: dict[str, None] = {}
    for match in PATH_TOKEN_RE.finditer(text):
        seen.setdefault(match.group(0), None)
    return list(seen)


def is_source_path(value: str) -> bool:
    """PURE. True when a cited path names a code file."""
    lowered = normalize_cited_path(value)
    dot = lowered.rfind(".")
    return dot != -1 and lowered[dot:] in SOURCE_SUFFIXES


def cited_source_paths(text: str) -> list[str]:
    """PURE. The cited paths that are code files."""
    return [p for p in cited_paths(text) if is_source_path(p)]


def classify_substitute(rel_path: str, exists: bool) -> str:
    """PURE. Which oracle backs this substitute.

    `known-fallback` requires BOTH corpus membership and filesystem presence --
    membership alone would let a declared-but-absent `README.md` wear the
    verified label, which is the self-attestation this labelling exists to
    separate out.
    """
    if exists and normalize_cited_path(rel_path) in KNOWN_FALLBACK_SET:
        return LABEL_KNOWN_FALLBACK
    return LABEL_AGENT_DECLARED


def substitute_label(entry: object) -> str:
    """PURE. The label on a receipt substitute; unlabelled reads as unverified."""
    if isinstance(entry, dict) and entry.get("source") in SUBSTITUTE_LABELS:
        return entry["source"]
    return LABEL_AGENT_DECLARED


def declared_substitute_paths(receipt: dict) -> list[str]:
    """PURE. Normalized paths of every substitute the receipt hash-pinned.

    Only PINNED entries count: an entry with no real sha256 was never proven
    read, so citing it in the frame proves nothing either.
    """
    entries = receipt.get("substitutes")
    if not isinstance(entries, list):
        return []
    return [
        normalize_cited_path(e["path"])
        for e in entries
        if isinstance(e, dict)
        and isinstance(e.get("path"), str)
        and not is_filler(e.get("path"))
        and is_content_hash(e.get("content_hash"))
    ]


def frame_verdict(
    receipt: dict, frame_text: str, inventory: Sequence[str]
) -> tuple[str, int, list[str]]:
    """PURE. (reserved first line, exit code, problems) for `verify-frame`.

    The exit vocabulary is the FROZEN g1 one -- no new codes. Two of them carry
    a slightly wider reading here, stated plainly rather than left implicit:

        12  a required INPUT DOCUMENT is missing or unusable. In g1 that was
            only the receipt; an absent mission frame is the same shape.
        10  the map contract is NOT discharged. In g1 that was an undischarged
            degraded record; a frame whose citations do not resolve is the same
            verdict about the same contract.
    """
    mode = receipt.get("mode")
    if mode == MODE_UNRESOLVABLE_ROOT:
        return (
            MODE_UNRESOLVABLE_ROOT,
            EXIT_UNRESOLVABLE_ROOT,
            [
                "could not look: the root was never proven a repo root, so there is "
                "nothing for a frame to be checked against. This is NOT 'the frame is fine'."
            ],
        )
    if not frame_text.strip():
        # THE load-bearing refusal. A check that passes when its artifact does
        # not exist reports success for every run that skipped the work.
        return (
            FRAME_MISSING,
            EXIT_RECEIPT_UNUSABLE,
            [
                f"no mission frame: .agent-work/<work-id>/{FRAME_NAME} is absent or empty. "
                "An absent frame REFUSES -- it never vacuously passes."
            ],
        )

    anchors = scan_anchors(frame_text)
    sources = cited_source_paths(frame_text)
    problems: list[str] = []

    if mode == MODE_RESOLVED:
        known = set(inventory)
        if not known:
            problems.append(
                "the receipt says RESOLVED but its entrypoint yields no citable anchor "
                "now -- the map moved under the run; re-run orient"
            )
        backing = [a for a in anchors if a in known]
        for anchor in anchors:
            if anchor not in known:
                problems.append(
                    f"{anchor} does not resolve against the map inventory -- anchor ids "
                    "exist only in the map, so an id that is not in it was not read from it"
                )
    else:
        declared = set(declared_substitute_paths(receipt))
        # Keep the AS-CITED spelling alongside the comparable one: matching is
        # case-insensitive, but a refusal that renames the offender (`CLAUDE.md`
        # reported as `claude.md`) is a refusal the author has to translate
        # before they can act on it.
        cited = [(raw, normalize_cited_path(raw)) for raw in cited_paths(frame_text)]
        backing = [raw for raw, norm in cited if norm in declared]
        for raw, norm in cited:
            if norm in KNOWN_FALLBACK_SET and norm not in declared:
                problems.append(
                    f"the frame cites {raw}, which the receipt never declared as a "
                    "hash-pinned substitute -- declare what you read at orient time so the "
                    "frame is compared against a committed prior, not a same-breath claim"
                )
        for anchor in anchors:
            problems.append(
                f"{anchor} cannot resolve: this run oriented {mode}, so no map was read "
                "and there is nothing for a map anchor to be a member of"
            )

    if not backing:
        if sources:
            problems.append(
                "this frame is cut from CODE: its only citations are source paths "
                f"({', '.join(sources[:5])}) -- a mission frame is cut from the map, and "
                "source reads are meant to CONFIRM that frame, not to build it"
            )
        elif mode == MODE_RESOLVED:
            problems.append(
                "the frame cites no anchor id that resolves against the map -- the map "
                "resolved, so the frame has to be built from it"
            )
        else:
            problems.append(
                "the frame cites none of the substitutes the receipt hash-pinned -- a "
                "degraded frame is built from the declared reading or from nothing"
            )

    if problems:
        return (FRAME_REFUSED, EXIT_DEGRADED_UNDISCHARGED, problems)
    return (FRAME_OK, EXIT_OK, [])


def render_frame_report(
    first_line: str, code: int, problems: Sequence[str], frame_rel: str, mode: str
) -> list[str]:
    """PURE. stdout lines; line 0 is always a reserved literal.

    Deliberately prints NO part of the map inventory. `orient` never prints an
    anchor id for the same reason: if the tool hands over the ids, citing one
    stops being evidence the map was read. Only ids the frame itself already
    contains are echoed back, and only to name an offender.
    """
    lines = [first_line, f"frame: {frame_rel}", f"orientation: {mode}"]
    if code == EXIT_OK:
        lines.append("frame citations resolve -- contract SATISFIED")
    elif first_line == FRAME_MISSING:
        lines.append("no mission frame to check -- REFUSED, never a vacuous pass")
    else:
        lines.append("frame citations do NOT resolve -- REFUSED")
    lines.append(f"problems: {len(problems)}")
    return lines


def exit_code_for(mode: str, discharged: bool) -> int:
    """PURE. The frozen exit code for a verdict.

    Falsification floor pins the UNRESOLVABLE-ROOT arm and the undischarged
    arm (tests/test_mutation_floor.py).
    """
    if mode == MODE_RESOLVED:
        return EXIT_OK
    if mode == MODE_UNRESOLVABLE_ROOT:
        return EXIT_UNRESOLVABLE_ROOT
    return EXIT_OK if discharged else EXIT_DEGRADED_UNDISCHARGED


def build_receipt(
    work_id: str,
    orientation: Orientation,
    substitutes: Sequence[dict],
    unmapped: Sequence[str],
    escalation: str | None,
    emitted_at: str,
    fallbacks_probed: Sequence[dict] = (),
) -> dict:
    """PURE. The receipt document -- schema documented in the module docstring."""
    return {
        "schema_version": SCHEMA_VERSION,
        "work_id": work_id,
        "root": orientation.root,
        "mode": orientation.mode,
        "entrypoint": orientation.entrypoint,
        "anchor_count": orientation.anchor_count,
        "candidates_tried": [
            {
                "order": c.order,
                "kind": c.kind,
                "path": c.path,
                "exists": c.exists,
                "outcome": candidate_outcome(c),
                "anchor_count": c.anchor_count,
                "note": c.note,
            }
            for c in orientation.candidates
        ],
        "substitutes": [dict(s) for s in substitutes],
        # The independent HALF of the degraded record: which of the fixed,
        # corpus-declared fallbacks actually exist, answered by the filesystem
        # rather than by the agent's account of what it read. Recorded on every
        # receipt, including RESOLVED ones, so the probe is never something the
        # agent could have suppressed by claiming the map resolved.
        "fallbacks_probed": [dict(f) for f in fallbacks_probed],
        "unmapped": list(unmapped),
        "escalation": escalation,
        "emitted_at": emitted_at,
        "root_proof": orientation.root_evidence,
    }


def render_orient_report(orientation: Orientation, receipt_rel: str | None) -> list[str]:
    """PURE. stdout lines; line 0 is always the reserved verdict literal."""
    lines = [orientation.mode]
    lines.append(f"root: {orientation.root}")
    lines.append(f"root proof: {orientation.root_evidence}")
    lines.append(f"entrypoint: {orientation.entrypoint or '(none)'}")
    lines.append(f"anchor_count: {orientation.anchor_count}")
    lines.append("candidates tried:")
    for candidate in orientation.candidates:
        lines.append(
            f"  [{candidate.order}] {candidate.kind}: {candidate.path}"
            f" -> {candidate_outcome(candidate)} ({candidate.note})"
        )
    if receipt_rel:
        lines.append(f"receipt: {receipt_rel}")
    return lines


def render_verify_report(
    first_line: str,
    code: int,
    problems: Sequence[str],
    receipt_rel: str,
    substitutes: Sequence[object] = (),
) -> list[str]:
    """PURE. stdout lines; line 0 is always a reserved literal.

    Reports each substitute's PROVENANCE, not merely its path. The receipt
    distinguishes "resolved from the known fallback set" (the filesystem
    agreed) from "the agent said so", and a distinction no reader is ever shown
    is a distinction that does not exist -- this is the REPORTED half of
    reported-degraded-mode, which is the whole point of the mode.

    Decoding is deliberately lenient (`substitute_label`): a receipt written
    before the label existed, or carrying an unrecognised value, reads as the
    conservative `agent-declared`. An omission can therefore never be read as
    verification -- the failure direction is always toward "unverified".

    No anchor id can reach this output: a substitute is a PATH, and it was
    declared by the agent in the first place, so echoing it back hands over
    nothing the tool was not already given.
    """
    lines = [first_line, f"receipt: {receipt_rel}"]
    if code == EXIT_OK:
        lines.append("orientation contract SATISFIED")
    elif code == EXIT_DEGRADED_UNDISCHARGED:
        lines.append("degraded record INCOMPLETE -- substitutes AND unmapped AND escalation")
    elif code == EXIT_UNRESOLVABLE_ROOT:
        lines.append("could not look: the root was never proven a repo root")
    else:
        lines.append("receipt unusable")
    lines.append(f"problems: {len(problems)}")
    for entry in substitutes:
        label = substitute_label(entry)
        path = entry.get("path") if isinstance(entry, dict) else None
        if label == LABEL_KNOWN_FALLBACK:
            note = "found in the fixed fallback set and present on disk"
        else:
            note = "UNVERIFIED -- declared by the agent, not in the fixed fallback set"
        lines.append(f"substitute: {path if path else '(no path)'} [{label}] -- {note}")
    return lines


# =============================================================================
# Impure edges -- filesystem, subprocess, clock.
# =============================================================================


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_of(path: Path) -> str | None:
    """Content hash used to pin a substitute; None when unreadable."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def git_toplevel(root: Path) -> str | None:
    """`git -C <root> rev-parse --show-toplevel`, or None when it cannot answer."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def probe_root(root: Path) -> RootProof:
    """Impure edge feeding the pure `prove_repo_root`."""
    if not root.is_dir():
        return RootProof(False, f"no positive proof: {root.as_posix()} is not a directory")
    return prove_repo_root(root.as_posix(), (root / ".git").exists(), git_toplevel(root))


def _candidate_from_file(order: int, kind: str, root: Path, path: Path, is_json: bool) -> Candidate:
    rel = _rel(root, path)
    if not path.is_file():
        return Candidate(order, kind, rel, False, False, 0, "absent")
    text = _read_text(path)
    has_content, anchors, note = (
        classify_generated_map(text) if is_json else classify_markdown(text)
    )
    return Candidate(order, kind, rel, True, has_content, len(anchors), note)


def collect_candidates(root: Path, entrypoint: str | None) -> list[Candidate]:
    """Impure edge: evaluate EVERY candidate, in order, and record each one.

    Deliberately not short-circuiting on the first hit -- `candidates_tried[]`
    is a delivery record of what was looked for, not a first-hit lookup log.
    """
    candidates: list[Candidate] = []
    order = 0

    if entrypoint:
        order += 1
        target = (root / entrypoint).resolve()
        candidates.append(
            _candidate_from_file(
                order, "entrypoint", root, target, target.suffix.lower() == ".json"
            )
        )

    order += 1
    candidates.append(
        _candidate_from_file(order, "generated-map", root, root / GENERATED_MAP, True)
    )

    order += 1
    candidates.append(_candidate_from_file(order, "index", root, root / INDEX_MD, False))

    order += 1
    map_dir = root / MAP_DIR
    if not map_dir.is_dir():
        candidates.append(Candidate(order, "packets-dir", MAP_DIR, False, False, 0, "absent"))
    else:
        packets_dir = map_dir / "packets"
        texts = (
            {p.name: _read_text(p) for p in sorted(packets_dir.glob("*.md"))}
            if packets_dir.is_dir()
            else {}
        )
        has_content, anchors, note = classify_packets(texts)
        candidates.append(
            Candidate(order, "packets-dir", MAP_DIR, True, has_content, len(anchors), note)
        )

    return candidates


def receipt_path(root: Path, work_id: str) -> Path:
    return root / ".agent-work" / work_id / "map-orientation.json"


def frame_path(root: Path, work_id: str) -> Path:
    return root / ".agent-work" / work_id / FRAME_NAME


def map_inventory(root: Path, entrypoint: str | None) -> tuple[str, ...]:
    """Impure edge: every anchor id the resolved entrypoint actually carries.

    Recomputed from the map rather than read out of the receipt on purpose --
    the receipt records a COUNT, and a count cannot answer set membership.
    """
    if not entrypoint:
        return ()
    target = root / entrypoint
    texts: list[str] = []
    if target.is_file():
        texts.append(_read_text(target))
    elif target.is_dir():
        for pattern in ("*.md", "*.json"):
            texts.extend(_read_text(p) for p in sorted(target.rglob(pattern)))
    seen: dict[str, None] = {}
    for text in texts:
        for anchor in scan_anchors(text):
            seen.setdefault(anchor, None)
    return tuple(seen)


def probe_fallbacks(root: Path) -> list[dict]:
    """Impure edge: which of the FIXED fallback set actually exist on disk.

    This is the independent half of the degraded record -- existence is settled
    by the filesystem, not by the agent's account of what it read.
    """
    probed = []
    for rel in KNOWN_FALLBACKS:
        path = root / rel
        exists = path.is_file()
        probed.append(
            {
                "path": rel,
                "exists": exists,
                "content_hash": sha256_of(path) if exists else None,
            }
        )
    return probed


def write_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")


def pin_substitutes(root: Path, substitutes: Sequence[str]) -> list[dict]:
    """Hash-pin each declared substitute so a later frame check has a prior.

    An unreadable or nonexistent path gets `content_hash: null`, NOT a
    sentinel string. A sentinel would satisfy a "is it non-empty" test and let
    a mistyped path discharge the whole contract.

    Each entry also carries `source`, the provenance label: `known-fallback`
    when the path is in the fixed corpus set AND present on disk (the
    filesystem, an oracle the agent does not author, agrees), `agent-declared`
    otherwise. The label is a provenance NOTE, never a discharge -- an absent
    substitute still refuses whatever it is called, which is why the label is
    computed alongside the pin rather than in place of it.
    """
    pinned = []
    for raw in substitutes:
        absolute = Path(raw).is_absolute()
        path = Path(raw) if absolute else (root / raw).resolve()
        rel = path.as_posix() if absolute else _rel(root, path)
        pinned.append(
            {
                "path": rel,
                "content_hash": sha256_of(path),
                "source": classify_substitute(rel, path.is_file()),
            }
        )
    return pinned


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# Subcommands
# =============================================================================


def cmd_orient(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    proof = probe_root(root)
    candidates = collect_candidates(root, args.entrypoint) if proof.proven else []
    orientation = build_orientation(root.as_posix(), proof, candidates)

    receipt = build_receipt(
        args.work_id,
        orientation,
        pin_substitutes(root, args.substitute or []),
        args.unmapped or [],
        args.escalation,
        _now_iso(),
        probe_fallbacks(root) if root.is_dir() else [],
    )

    receipt_rel = None
    if root.is_dir():
        destination = receipt_path(root, args.work_id)
        write_receipt(destination, receipt)
        receipt_rel = _rel(root, destination)

    for line in render_orient_report(orientation, receipt_rel):
        print(line)
    sys.stdout.flush()

    discharged = degraded_record_is_complete(receipt)
    code = exit_code_for(orientation.mode, discharged)
    if code == EXIT_UNRESOLVABLE_ROOT:
        print(
            f"could not look: {root.as_posix()} is not a proven repo root "
            f"({proof.evidence}). This is NOT 'the map is missing'.",
            file=sys.stderr,
        )
    elif code == EXIT_DEGRADED_UNDISCHARGED:
        print("degraded and NOT discharged -- still owed:", file=sys.stderr)
        for missing in missing_degraded_fields(receipt):
            print(f"  - {missing}", file=sys.stderr)
    return code


def cmd_verify_orientation(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    path = receipt_path(root, args.work_id)
    receipt: object
    if not path.is_file():
        print(RECEIPT_MISSING)
        print(f"no receipt at {path.as_posix()} -- run `orient` first", file=sys.stderr)
        return EXIT_RECEIPT_UNUSABLE
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(RECEIPT_MISSING)
        print(f"receipt at {path.as_posix()} is unusable: {exc}", file=sys.stderr)
        return EXIT_RECEIPT_UNUSABLE

    first_line, code, problems = verify_verdict(receipt, args.work_id)
    declared = receipt.get("substitutes") if isinstance(receipt, dict) else None
    for line in render_verify_report(
        first_line, code, problems, _rel(root, path),
        declared if isinstance(declared, list) else [],
    ):
        print(line)
    sys.stdout.flush()
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return _gate(args, code)


def _gate(args: argparse.Namespace, code: int) -> int:
    """The gate-vs-report dial, as a FLAG FLIP rather than a rebuild.

    A ruling to gate or un-gate one of these checks should be an edit to the
    command string in the template -- append `--report-only` -- not a change to
    this module or to the checklist's shape. The verdict printed is identical
    either way; only its blocking-ness moves.
    """
    if getattr(args, "report_only", False) and code != EXIT_OK:
        print(f"report-only: NOT gating; would exit {code}")
        sys.stdout.flush()
        return EXIT_OK
    return code


def cmd_verify_frame(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    path = receipt_path(root, args.work_id)
    if not path.is_file():
        print(RECEIPT_MISSING)
        print(
            f"no orientation receipt at {path.as_posix()} -- the frame cannot be checked "
            "against a map nobody resolved; run `orient` at the context step first",
            file=sys.stderr,
        )
        return _gate(args, EXIT_RECEIPT_UNUSABLE)
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(RECEIPT_MISSING)
        print(f"receipt at {path.as_posix()} is unusable: {exc}", file=sys.stderr)
        return _gate(args, EXIT_RECEIPT_UNUSABLE)

    structural = receipt_problems(receipt, args.work_id)
    if structural:
        print(RECEIPT_MISSING)
        for problem in structural:
            print(f"  - {problem}", file=sys.stderr)
        return _gate(args, EXIT_RECEIPT_UNUSABLE)

    frame_file = frame_path(root, args.work_id)
    frame_text = _read_text(frame_file) if frame_file.is_file() else ""
    mode = receipt["mode"]
    inventory = map_inventory(root, receipt.get("entrypoint")) if mode == MODE_RESOLVED else ()

    first_line, code, problems = frame_verdict(receipt, frame_text, inventory)
    for line in render_frame_report(first_line, code, problems, _rel(root, frame_file), mode):
        print(line)
    sys.stdout.flush()
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return _gate(args, code)


# =============================================================================
# Falsification floor
# =============================================================================


def _check(name: str, condition: bool, failures: list[str]) -> None:
    if not condition:
        failures.append(name)


def _cand(order: int, kind: str, path: str, exists: bool, content: bool, anchors: int) -> Candidate:
    return Candidate(order, kind, path, exists, content, anchors, "self-test")


def self_test() -> int:
    """Falsification floor: assert the decision layer refuses what it must."""
    failures: list[str] = []
    proven = RootProof(True, "self-test")
    unproven = RootProof(False, "self-test")

    # --- exit vocabulary must not collide with machinery it does not own -----
    _check(
        "semantic codes avoid the argparse/traceback/shell range",
        all(code not in OCCUPIED_EXIT_CODES for code in SEMANTIC_EXIT_CODES)
        and all(2 < code < 126 for code in SEMANTIC_EXIT_CODES)
        and EXIT_OK == 0,
        failures,
    )
    _check("semantic codes are distinct", len(set(SEMANTIC_EXIT_CODES)) == len(SEMANTIC_EXIT_CODES), failures)

    # --- anchor scan ---------------------------------------------------------
    _check("scan finds a real anchor", scan_anchors("see `struct:physics` today") == ["struct:physics"], failures)
    _check(
        "scan finds every anchor kind",
        len(
            scan_anchors(
                "struct:a capability:b event:c constraint:d assumption:e claim:f decision:g"
            )
        )
        == 7,
        failures,
    )
    _check("scan rejects a bracketed placeholder", scan_anchors("`struct:<id>` `capability:<id>`") == [], failures)
    _check("scan dedupes", scan_anchors("struct:a struct:a struct:a") == ["struct:a"], failures)
    _check("scan trims trailing punctuation", scan_anchors("struct:physics.") == ["struct:physics"], failures)

    # --- the shipped index template must NOT resolve -------------------------
    template = Path(__file__).resolve().parents[1] / (
        "skills/cartographer/templates/ARCHITECTURE_INDEX.template.md"
    )
    if template.is_file():
        _check(
            "shipped ARCHITECTURE_INDEX template yields no citable anchor",
            scan_anchors(_read_text(template)) == [],
            failures,
        )

    # --- citability, not existence ------------------------------------------
    _check("existing-but-uncitable is not a hit", not candidate_is_citable(_cand(1, "index", INDEX_MD, True, True, 0)), failures)
    _check("citable is a hit", candidate_is_citable(_cand(1, "index", INDEX_MD, True, True, 3)), failures)
    _check("uncitable-with-content is unparseable", candidate_outcome(_cand(1, "index", INDEX_MD, True, True, 0)) == OUTCOME_UNPARSEABLE, failures)
    _check("existing-without-content is empty", candidate_outcome(_cand(1, "index", INDEX_MD, True, False, 0)) == OUTCOME_EMPTY, failures)
    _check("missing is absent", candidate_outcome(_cand(1, "index", INDEX_MD, False, False, 0)) == OUTCOME_ABSENT, failures)

    # --- could-not-look vs looked-and-found-nothing --------------------------
    _check("unproven root is UNRESOLVABLE-ROOT", determine_mode(unproven, []) == MODE_UNRESOLVABLE_ROOT, failures)
    _check(
        "unproven root is NOT collapsed into DEGRADED-NO-MAP",
        determine_mode(unproven, [_cand(1, "index", INDEX_MD, False, False, 0)]) != MODE_DEGRADED_NO_MAP,
        failures,
    )
    _check("dot-git proves the root", prove_repo_root("/r", True, None).proven, failures)
    _check("git toplevel naming this root proves it", prove_repo_root("/r", False, "/r").proven, failures)
    _check("git toplevel naming a PARENT does not prove it", not prove_repo_root("/r/sub", False, "/r").proven, failures)
    _check("no evidence is not proof", not prove_repo_root("/r", False, None).proven, failures)

    # --- degraded reasons are produced distinctly ----------------------------
    absent = [_cand(1, "generated-map", GENERATED_MAP, False, False, 0), _cand(2, "index", INDEX_MD, False, False, 0)]
    empty = absent[:1] + [_cand(2, "index", INDEX_MD, True, False, 0)]
    unparseable = absent[:1] + [_cand(2, "index", INDEX_MD, True, True, 0)]
    hit = absent[:1] + [_cand(2, "index", INDEX_MD, True, True, 4)]
    _check("all absent -> DEGRADED-NO-MAP", determine_mode(proven, absent) == MODE_DEGRADED_NO_MAP, failures)
    _check("empty -> DEGRADED-EMPTY-MAP", determine_mode(proven, empty) == MODE_DEGRADED_EMPTY_MAP, failures)
    _check("content-without-anchors -> DEGRADED-UNPARSEABLE", determine_mode(proven, unparseable) == MODE_DEGRADED_UNPARSEABLE, failures)
    _check("citable -> RESOLVED", determine_mode(proven, hit) == MODE_RESOLVED, failures)

    # --- ordering: first hit wins, all candidates still recorded -------------
    two_hits = [_cand(1, "entrypoint", "a.md", True, True, 2), _cand(2, "index", INDEX_MD, True, True, 9)]
    orientation = build_orientation("/r", proven, two_hits)
    _check("first hit wins", orientation.entrypoint == "a.md" and orientation.anchor_count == 2, failures)
    _check("every candidate recorded even after a hit", len(orientation.candidates) == 2, failures)
    degraded = build_orientation("/r", proven, absent)
    _check("degraded orientation names no entrypoint", degraded.entrypoint is None and degraded.anchor_count == 0, failures)

    # --- classifiers ---------------------------------------------------------
    _check("empty json is empty", classify_generated_map("   ")[0] is False, failures)
    _check("broken json is uncitable", classify_generated_map("{not json")[1] == [], failures)
    _check("json without nodes is uncitable", classify_generated_map('{"a": 1}')[1] == [], failures)
    _check("json with empty nodes is uncitable", classify_generated_map('{"nodes": []}')[1] == [], failures)
    _check(
        "json with a real node id is citable",
        classify_generated_map('{"nodes": [{"id": "struct:physics"}]}')[1] == ["struct:physics"],
        failures,
    )
    _check("empty markdown is empty", classify_markdown("\n\n")[0] is False, failures)
    _check("markdown template is uncitable", classify_markdown("# Index\n\n`struct:<id>`\n")[1] == [], failures)
    _check("no packets is empty", classify_packets({})[0] is False, failures)
    _check("blank packets are empty", classify_packets({"a.md": "  \n"})[0] is False, failures)
    _check("packet anchors are collected", classify_packets({"a.md": "struct:a", "b.md": "struct:b"})[1] == ["struct:a", "struct:b"], failures)

    # --- reserved literals + exit mapping ------------------------------------
    for mode in ORIENT_MODES:
        _check(f"{mode} is a reserved first line", mode in RESERVED_FIRST_LINES, failures)
    _check("RESOLVED exits 0", exit_code_for(MODE_RESOLVED, False) == EXIT_OK, failures)
    _check("UNRESOLVABLE-ROOT exits 11", exit_code_for(MODE_UNRESOLVABLE_ROOT, True) == EXIT_UNRESOLVABLE_ROOT, failures)
    _check("undischarged degraded exits 10", exit_code_for(MODE_DEGRADED_NO_MAP, False) == EXIT_DEGRADED_UNDISCHARGED, failures)
    _check("discharged degraded exits 0", exit_code_for(MODE_DEGRADED_NO_MAP, True) == EXIT_OK, failures)
    report = render_orient_report(degraded, "receipt.json")
    _check("stdout line 0 is a reserved literal", report[0] in RESERVED_FIRST_LINES, failures)
    _check("stdout line 0 is never blank", bool(report[0].strip()), failures)

    # --- the degraded record discharges only with ALL THREE ------------------
    complete = {
        "substitutes": [{"path": "README.md", "content_hash": "a" * 64}],
        "unmapped": ["src/engine internals were never read"],
        "escalation": "asking commander whether a map is in scope",
    }
    _check("a complete record discharges", degraded_record_is_complete(dict(complete)), failures)
    for dropped, emptied in (("substitutes", []), ("unmapped", []), ("escalation", None)):
        record = dict(complete)
        record[dropped] = emptied
        _check(f"omitting {dropped} refuses", not degraded_record_is_complete(record), failures)
    for filler in ("", "  ", "none", "N/A", "n/a", "tbd", "<placeholder>"):
        record = dict(complete)
        record["escalation"] = filler
        _check(f"filler escalation {filler!r} refuses", not degraded_record_is_complete(record), failures)
        record = dict(complete)
        record["unmapped"] = [filler]
        _check(f"filler unmapped {filler!r} refuses", not degraded_record_is_complete(record), failures)
    _check("an unhashed substitute refuses", not substitutes_declared({"substitutes": [{"path": "a.md", "content_hash": ""}]}), failures)
    _check("a filler substitute path refuses", not substitutes_declared({"substitutes": [{"path": "none", "content_hash": "a" * 64}]}), failures)
    _check("an empty substitutes list refuses", not substitutes_declared({"substitutes": []}), failures)

    # --- an UNREADABLE substitute must refuse, never discharge --------------
    # A sentinel here would let a single mistyped path satisfy the whole
    # contract at exit 0.
    for bad_hash in (None, "unreadable", "", "n/a", "a" * 63, "z" * 64, 12345):
        _check(
            f"substitute pinned with {bad_hash!r} refuses",
            not substitutes_declared({"substitutes": [{"path": "a.md", "content_hash": bad_hash}]}),
            failures,
        )
    _check("a real sha256 pin is accepted", substitutes_declared({"substitutes": [{"path": "a.md", "content_hash": "0" * 63 + "f"}]}), failures)
    _check("is_content_hash rejects a sentinel", not is_content_hash("unreadable"), failures)
    _check("is_content_hash accepts a digest", is_content_hash(hashlib.sha256(b"x").hexdigest()), failures)
    # ONE bad entry among good ones must sink the whole declaration.
    _check(
        "a mixed substitutes list with one unpinned entry refuses",
        not substitutes_declared(
            {"substitutes": [{"path": "a.md", "content_hash": "b" * 64}, {"path": "gone.md", "content_hash": None}]}
        ),
        failures,
    )

    # --- MULTI-ELEMENT filler lists: `any` and `all` must NOT coincide ------
    # Single-element lists cannot tell `not any(...)` from `not all(...)`, so a
    # mutation between them survives a floor built only from them.
    _check(
        "unmapped ['none', real] refuses (one filler poisons the list)",
        not unmapped_declared({"unmapped": ["none", "src/engine internals were never read"]}),
        failures,
    )
    _check(
        "unmapped [real, 'n/a'] refuses",
        not unmapped_declared({"unmapped": ["src/engine internals were never read", "n/a"]}),
        failures,
    )
    _check(
        "unmapped [real, real] is accepted",
        unmapped_declared({"unmapped": ["src/engine was never read", "the data layer was never read"]}),
        failures,
    )
    _check(
        "unmapped ['none', 'n/a'] refuses",
        not unmapped_declared({"unmapped": ["none", "n/a"]}),
        failures,
    )

    # --- verify-orientation verdicts ----------------------------------------
    base_receipt = build_receipt(
        "w", degraded, complete["substitutes"], complete["unmapped"], complete["escalation"], "2026-01-01T00:00:00+00:00"
    )
    _check("a complete degraded receipt passes", verify_verdict(base_receipt, "w")[1] == EXIT_OK, failures)
    starved = dict(base_receipt, substitutes=[])
    _check("an incomplete degraded receipt exits 10", verify_verdict(starved, "w")[1] == EXIT_DEGRADED_UNDISCHARGED, failures)
    _check("a wrong work_id makes the receipt unusable", verify_verdict(base_receipt, "other")[1] == EXIT_RECEIPT_UNUSABLE, failures)
    _check("a non-object receipt is unusable", verify_verdict(["nope"], "w")[1] == EXIT_RECEIPT_UNUSABLE, failures)
    _check("an unusable receipt still reports a reserved literal", verify_verdict(["nope"], "w")[0] in RESERVED_FIRST_LINES, failures)
    resolved_orientation = build_orientation("/r", proven, hit)
    resolved_receipt = build_receipt("w", resolved_orientation, [], [], None, "2026-01-01T00:00:00+00:00")
    _check("a RESOLVED receipt passes with no declarations", verify_verdict(resolved_receipt, "w")[1] == EXIT_OK, failures)
    faked = dict(resolved_receipt, anchor_count=0)
    _check("RESOLVED with anchor_count 0 is unusable", verify_verdict(faked, "w")[1] == EXIT_RECEIPT_UNUSABLE, failures)
    unresolvable = build_receipt("w", build_orientation("/r", unproven, []), complete["substitutes"], complete["unmapped"], complete["escalation"], "2026-01-01T00:00:00+00:00")
    _check("UNRESOLVABLE-ROOT never passes, even fully declared", verify_verdict(unresolvable, "w")[1] == EXIT_UNRESOLVABLE_ROOT, failures)
    _check("verify line 0 is a reserved literal", render_verify_report(*verify_verdict(base_receipt, "w"), "r.json")[0] in RESERVED_FIRST_LINES, failures)

    # --- verify-frame: the ABSENT frame must never vacuously pass ------------
    resolved_receipt_for_frame = dict(resolved_receipt)
    inventory = ("struct:app", "capability:serve_requests")
    for empty in ("", "   ", "\n\n"):
        line, code, _ = frame_verdict(resolved_receipt_for_frame, empty, inventory)
        _check(f"absent frame {empty!r} refuses", code != EXIT_OK, failures)
        _check(f"absent frame {empty!r} reports FRAME-MISSING", line == FRAME_MISSING, failures)
    _check(
        "an absent frame is NEVER FRAME-OK",
        frame_verdict(resolved_receipt_for_frame, "", inventory)[0] != FRAME_OK,
        failures,
    )
    good_frame = "cites `struct:app` and `capability:serve_requests`"
    _check(
        "a frame citing resolvable anchors passes",
        frame_verdict(resolved_receipt_for_frame, good_frame, inventory)[1] == EXIT_OK,
        failures,
    )
    unknown_frame = "cites `struct:app` and `struct:ghost`"
    line, code, problems = frame_verdict(resolved_receipt_for_frame, unknown_frame, inventory)
    _check("an unresolvable anchor refuses", code == EXIT_DEGRADED_UNDISCHARGED, failures)
    _check("the refusal names the offending anchor", any("struct:ghost" in p for p in problems), failures)
    _check("the refusal does not indict the resolvable anchor", not any("struct:app does not" in p for p in problems), failures)
    code_frame = "- `src/engine/solver.py`\n- `scripts/run.py`\n"
    line, code, problems = frame_verdict(resolved_receipt_for_frame, code_frame, inventory)
    _check("a frame cut from source paths refuses", code == EXIT_DEGRADED_UNDISCHARGED, failures)
    _check("the cut-from-code refusal names a source path", any("solver.py" in p for p in problems), failures)
    _check(
        "an UNRESOLVABLE-ROOT receipt never lets a frame pass",
        frame_verdict(unresolvable, good_frame, inventory)[1] == EXIT_UNRESOLVABLE_ROOT,
        failures,
    )
    for mode in (FRAME_OK, FRAME_MISSING, FRAME_REFUSED):
        _check(f"{mode} is a reserved first line", mode in RESERVED_FIRST_LINES, failures)
    _check(
        "verify-frame invents no exit code outside the frozen vocabulary",
        all(
            frame_verdict(resolved_receipt_for_frame, text, inventory)[1]
            in (EXIT_OK, *SEMANTIC_EXIT_CODES)
            for text in ("", good_frame, unknown_frame, code_frame)
        ),
        failures,
    )
    _check(
        "frame report line 0 is a reserved literal",
        render_frame_report(FRAME_MISSING, EXIT_RECEIPT_UNUSABLE, [], "f.md", MODE_RESOLVED)[0]
        in RESERVED_FIRST_LINES,
        failures,
    )

    # --- source-path detection ----------------------------------------------
    _check("a .py path is a source path", is_source_path("src/engine/solver.py"), failures)
    _check("a backticked .py path is a source path", is_source_path("`scripts/run.py`"), failures)
    _check("README.md is not a source path", not is_source_path("README.md"), failures)
    _check("a docs packet is not a source path", not is_source_path("docs/architecture/packets/a.md"), failures)
    _check("cited paths are found in markdown", "src/a.py" in cited_paths("- `src/a.py` — helper"), failures)

    # --- the degraded arm: substitutes as a COMMITTED PRIOR ------------------
    degraded_pinned = dict(base_receipt)
    _check(
        "a degraded frame citing a declared substitute passes",
        frame_verdict(degraded_pinned, "built from `README.md`", ())[1] == EXIT_OK,
        failures,
    )
    line, code, problems = frame_verdict(degraded_pinned, "built from `CLAUDE.md`", ())
    _check("a degraded frame citing an UNDECLARED fallback refuses", code != EXIT_OK, failures)
    # AS CITED, not normalized: matching is case-insensitive, but a refusal that
    # renames the offender makes the author translate before they can act.
    _check("that refusal names the undeclared path", any("CLAUDE.md" in p for p in problems), failures)
    _check(
        "a degraded frame citing nothing declared refuses",
        frame_verdict(degraded_pinned, "I thought about it", ())[1] != EXIT_OK,
        failures,
    )
    _check(
        "a degraded frame inventing a map anchor refuses -- there is no map to be a member of",
        frame_verdict(degraded_pinned, "`README.md` and `struct:invented`", ())[1] != EXIT_OK,
        failures,
    )
    _check(
        "an UNPINNED substitute cannot back a degraded frame",
        frame_verdict(
            dict(degraded_pinned, substitutes=[{"path": "README.md", "content_hash": None}]),
            "built from `README.md`",
            (),
        )[1]
        != EXIT_OK,
        failures,
    )

    # --- substitute labelling: filesystem oracle vs agent assertion ----------
    _check(
        "a present known fallback is labelled known-fallback",
        classify_substitute("README.md", True) == LABEL_KNOWN_FALLBACK,
        failures,
    )
    _check(
        "an ABSENT known fallback is NOT labelled verified",
        classify_substitute("README.md", False) == LABEL_AGENT_DECLARED,
        failures,
    )
    _check(
        "a path outside the fixed set is agent-declared even when present",
        classify_substitute("docs/notes/whatever.md", True) == LABEL_AGENT_DECLARED,
        failures,
    )
    _check(
        "an unlabelled substitute reads as UNVERIFIED, never upgraded by omission",
        substitute_label({"path": "README.md"}) == LABEL_AGENT_DECLARED,
        failures,
    )
    _check(
        "a bogus label reads as unverified",
        substitute_label({"path": "README.md", "source": "trust-me"}) == LABEL_AGENT_DECLARED,
        failures,
    )
    _check(
        "a real known-fallback label survives",
        substitute_label({"path": "README.md", "source": LABEL_KNOWN_FALLBACK})
        == LABEL_KNOWN_FALLBACK,
        failures,
    )

    total = len(failures)
    if total:
        print(f"self-test FAILED: {total} check(s)", file=sys.stderr)
        for name in failures:
            print(f"  - {name}", file=sys.stderr)
        return EXIT_SELF_TEST_FAILED
    print("self-test OK")
    return EXIT_OK


# =============================================================================
# CLI
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="map_orient.py",
        description="Resolve a repo's architecture-map entrypoint, or report the degraded mode.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the falsification floor over the pure decision layer and exit",
    )
    sub = parser.add_subparsers(dest="command")

    orient = sub.add_parser("orient", help="resolve an entrypoint and write the receipt")
    orient.add_argument("--root", required=True, help="absolute repo root")
    orient.add_argument("--work-id", required=True, dest="work_id")
    orient.add_argument("--entrypoint", help="repo-relative entrypoint to try first")
    orient.add_argument(
        "--substitute",
        action="append",
        help="repo-relative path you read INSTEAD of a map; hash-pinned into the "
        "receipt. Repeatable. Required to discharge a DEGRADED verdict.",
    )
    orient.add_argument(
        "--unmapped",
        action="append",
        help="something that stayed unmapped, stated plainly. Repeatable. "
        "Required to discharge a DEGRADED verdict.",
    )
    orient.add_argument(
        "--escalation",
        help="what you are escalating and to whom. Required to discharge a "
        "DEGRADED verdict.",
    )

    verify = sub.add_parser(
        "verify-orientation", help="gate check: is the orientation contract satisfied?"
    )
    verify.add_argument("--root", required=True, help="absolute repo root")
    verify.add_argument("--work-id", required=True, dest="work_id")
    _add_report_only(verify)

    frame = sub.add_parser(
        "verify-frame",
        help="gate check: does the mission frame cite anchors the map actually carries?",
    )
    frame.add_argument("--root", required=True, help="absolute repo root")
    frame.add_argument("--work-id", required=True, dest="work_id")
    _add_report_only(frame)

    return parser


def _add_report_only(sub_parser: argparse.ArgumentParser) -> None:
    sub_parser.add_argument(
        "--report-only",
        action="store_true",
        dest="report_only",
        help="print the verdict but always exit 0. The gate-vs-report dial: "
        "un-gating a step is this flag, not a rebuild.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.command:
        # argparse exits 2 here -- a usage error, distinct from every verdict.
        parser.error(
            "a subcommand is required (orient | verify-orientation | verify-frame) "
            "unless --self-test"
        )
    if args.command == "orient":
        return cmd_orient(args)
    if args.command == "verify-orientation":
        return cmd_verify_orientation(args)
    if args.command == "verify-frame":
        return cmd_verify_frame(args)
    parser.error(f"unknown subcommand: {args.command}")
    return EXIT_OK  # unreachable; parser.error exits 2


if __name__ == "__main__":
    raise SystemExit(main())
