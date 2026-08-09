#!/usr/bin/env python
"""Deterministic retrieval over the episode store (docs/EPISODE_STORE.md section 8).

The store never guesses. This module exposes exactly four primitives — fetch by id,
enumerate, select by exact field value / set membership, and enumerate an episode's
neighbours by shared exact join key — and nothing else. There is no ranking, no
scoring, no similarity, no embedding, no ordering by relevance. What it hands a
downstream sensor is a candidate set that is COMPLETE by construction and unordered
(results are id-sorted purely so the same store always produces the same bytes;
alphabetical order is a canonical enumeration, not a relevance ranking). Deciding that
two episodes *rhyme* is a stochastic sensor's job, owned at issue #308, and happens
entirely on top of this surface — never inside it (governing principle B0.1, the
stochastic boundary).

Silent omission is the failure mode this module is written against. A retrieval that
crashes is a bug you find; a retrieval that quietly returns one record fewer than it
should is a bug you ship. Three concrete defenses, each with an adversarial test in
tests/test_episode_store.py:

  1. Every field read goes through field_values(), which returns a LIST for every
     field. artifact-ref is genuinely list-shaped, and the natural implementation of
     "read the mechanical block into a dict" keeps only the LAST artifact-ref line and
     silently drops the rest — so an episode whose only matching ref is not the final
     one vanishes from the candidate set with no error at all.
  2. Matching compares whole parsed field VALUES with ==, never a substring of the file
     text. A substring match over-returns (a prefix matching a longer value); a
     line-oriented grep that forgot to anchor under-returns once free text is involved.
     Neither failure is available to an == over parsed values.
  3. An unrecognized field name RAISES. It never returns an empty candidate set, which
     is what makes a typo'd field name a visible failure instead of a silent "no
     episodes matched".

Retirement (EPISODE_STORE.md section 7, ratified at gate g4). Retiring an episode MOVES
its file out of the ordinary-search set and into the archive. The ruling's second half —
"prefer to keep files clean of history unless they're historical; archives are available
strats" — is a design principle this module implements literally:

  * **the archive is opt-in, never opt-out.** Ordinary retrieval scans the ordinary set
    and never touches the archive, so it is not a second live search space that every
    query has to remember to exclude. Every scanning primitive takes `include_retired`,
    defaulting to False; history-inclusive retrieval is a deliberate, separate act.
    A default that included the archive would make every future caller's *omission* of a
    filter a silent correctness bug — the exact failure class this module exists against;
  * **fetch-by-id is exempt, on purpose.** An addressed lookup by name is not a search;
    retirement excludes an episode from search, never from retrieval by name. A
    cross-reference (`consolidated-into:`, `superseded-by:`) would dangle otherwise.

Store-level refusals. A store that is ABSENT (a typo'd --store-root, or a layout that was
never committed), MALFORMED (a Markdown file outside the two layout directories, or one
inside them whose name is not a well-formed episode id), or HALF-RETIRED (an id in both
directories) is refused by every primitive here, with an exit code, rather than answered.
Each of those would otherwise produce a plausible wrong answer — most often `count: 0`,
which reads exactly like an empty store. The refusals live in the writer's seams, so
retrieval inherits them instead of restating them.

Layout containment. Every path resolution goes through resolve_episode_path(), every
store scan through iter_episode_ids(), every membership question through
is_episode_in_ordinary_search() — all three are the writer's seams
(scripts/apply_episode_delta.py). This module inlines no path, no glob, and no grep, and
tests/test_episode_store.py asserts it: with the layout bound, the containment is what
keeps the binding in one place instead of scattered across call sites.

Section 7's composition rule for the ordinary set — scan with
iter_episode_ids(include_retired=False), then confirm each returned id through
is_episode_in_ordinary_search(), always both steps, never one folded into the other — is
followed here. Under the bound layout the second step cannot subtract anything from the
first, so it is kept for a different reason than the one that introduced it: the scan and
the membership predicate are two INDEPENDENT seams, and a change that updated only one of
them is caught here. Their disagreement is therefore raised, never silently dropped —
dropping is how a candidate set gets quietly shorter.

Newline handling (Windows hazard): every read passes newline="" so a stored \r\n is
never silently folded to \n, exactly as the writer does. Retrieval must see the bytes
that are actually on disk, since one of this gate's obligations is proving a stored
line is BYTE-identical before and after an unrelated write. That read goes through the
writer's read_text_exact() helper — NOT Path.read_text(newline=...), which is Python
3.13+ while CI pins 3.12.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

_WRITER_PATH = Path(__file__).resolve().parent / "apply_episode_delta.py"
_WRITER_MODULE = "apply_episode_delta"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def writer():
    """g2's writer module — the single home of the record grammar (parse_episode) and
    of EPISODE_STORE.md section 7's seams. Resolved lazily on every call rather than
    bound once at import, so a caller that has already imported the writer (a test, a
    harness) shares that exact module object and its seams, instead of this module
    quietly operating on a second, divergent copy."""
    module = sys.modules.get(_WRITER_MODULE)
    if module is not None:
        try:
            if Path(getattr(module, "__file__", "")).resolve() == _WRITER_PATH:
                return module
        except (OSError, ValueError):
            pass
    spec = importlib.util.spec_from_file_location(_WRITER_MODULE, _WRITER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[_WRITER_MODULE] = module
    spec.loader.exec_module(module)
    return module


class QueryError(Exception):
    """Raised when a query cannot be answered. Never swallowed into an empty result —
    an unanswerable query and a query with no matches are different facts, and
    collapsing them is how a silent omission gets shipped."""


class EpisodeNotFound(QueryError):
    """The named episode does not exist. A distinct type (and a distinct CLI exit code)
    from an invalid query, so a caller can tell "there is no such episode" from "your
    query was malformed" — and neither from "nothing matched"."""


def store_root() -> Path:
    """The store-root seam (EPISODE_STORE.md section 1), re-exported from the writer so
    retrieval and writing can never disagree about where the store is. Deliberately NOT
    durable_root()."""
    return writer().store_root()


def _read_episode(path: Path):
    # read_text_exact is re-exported from the writer for the same reason store_root() is:
    # reading and writing must never disagree about newline handling. It exists because
    # Path.read_text(newline=...) is Python 3.13+ and CI pins 3.12.
    text = writer().read_text_exact(path)
    return writer().parse_episode(text)


# --- primitive 1: fetch by id --------------------------------------------------------


def fetch_episode(episode_id: str, root: Path):
    """Fetch one episode by id. Returns the parsed Episode, or None if no episode with
    that id exists. Resolves its path through resolve_episode_path() (section 7) and
    reads whatever that returns — it never constructs a path itself, because which
    directory (if any) holds the file IS the open layout question. No scan, no
    membership check (section 8)."""
    path = writer().resolve_episode_path(episode_id, root)
    if path is None:
        return None
    return _read_episode(path)


# --- primitive 2: enumerate ----------------------------------------------------------


class HalfRetiredStore(QueryError):
    """The base scan and the membership predicate disagree about one id. Under the bound
    layout they are two reads of the same filesystem fact, so a disagreement means the
    store is mid-move (an interrupted retirement) or the two seams have drifted apart.
    Either way it is reported, never resolved by dropping the id — a candidate set that
    quietly loses a record is the one outcome this module refuses."""


def enumerate_episode_ids(root: Path, include_retired: bool = False) -> list[str]:
    """Every episode id in the ordinary rhyme-search set, id-sorted for determinism.
    Pass `include_retired=True` for the history-inclusive set — the archive is reached
    deliberately or not at all.

    Ordinary enumeration follows section 7's composition rule exactly: scan through the
    iter_episode_ids() seam, then confirm each returned id through the
    is_episode_in_ordinary_search() seam. Both steps, always, and a disagreement between
    them raises rather than silently shortening the answer.

    History-inclusive enumeration is the union of both sets and takes NO membership
    filter — filtering here would re-exclude exactly what the caller asked to see, which
    is the "forgot the union" trap arriving from the other direction."""
    scanned = sorted(writer().iter_episode_ids(root, include_retired=include_retired))
    if include_retired:
        return scanned
    denied = [eid for eid in scanned if not writer().is_episode_in_ordinary_search(eid, root)]
    if denied:
        raise HalfRetiredStore(
            "the base scan returned "
            + ", ".join(denied)
            + " but the membership predicate denies them — the store is mid-move or the "
            "two seams have drifted apart. Refusing to answer rather than returning a "
            "candidate set that is silently short."
        )
    return scanned


def enumerate_episodes(root: Path, include_retired: bool = False) -> list:
    """Every episode in the ordinary set as parsed records, id-sorted — or the
    history-inclusive set when asked. The candidate set every other scanning primitive is
    built from.

    An id that the scan returned but fetch cannot resolve RAISES. It is the same rule as
    the composition check above, one layer out: an earlier version dropped such an id with
    an `if ep is not None`, which is a candidate set getting quietly shorter between two
    lines of the same function — exactly the outcome this module exists to refuse. The
    condition means the store changed underneath the scan, or the enumeration and
    resolution seams disagree; both are facts a caller needs, and neither is "no match"."""
    episodes = []
    for episode_id in enumerate_episode_ids(root, include_retired=include_retired):
        episode = fetch_episode(episode_id, root)
        if episode is None:
            raise QueryError(
                f"{episode_id} was returned by the store scan but no longer resolves to "
                "a file — the store changed underneath this query, or the enumeration "
                "and path-resolution seams disagree. Refusing to answer rather than "
                "returning a candidate set that is silently one record short."
            )
        episodes.append(episode)
    return episodes


# --- field reading: the one place a field name becomes values ------------------------
#
# Every reader returns a LIST, including the scalars. That uniformity is not cosmetic:
# artifact-ref is genuinely repeated, and any representation that can hold only one
# value per field name silently drops all but one of them. Making the list the ONLY
# shape means no caller can accidentally introduce the collapse — there is no scalar
# path to take.

_FIELD_READERS = {
    "id": lambda ep: [ep.episode_id],
    "run": lambda ep: [ep.run],
    "project": lambda ep: [ep.project],
    "role": lambda ep: [ep.role],
    "spine-step": lambda ep: [ep.spine_step],
    "context-manifest-ref": lambda ep: [ep.context_manifest_ref],
    "refusals": lambda ep: [str(ep.refusals)],
    "reopens": lambda ep: [str(ep.reopens)],
    "rework-count": lambda ep: [str(ep.rework_count)],
    "failed-commands": lambda ep: [str(ep.failed_commands)],
    "artifact-ref": lambda ep: list(ep.artifact_refs),
}

SELECTABLE_FIELDS = tuple(sorted(_FIELD_READERS))


def _selectable_field_reader(field: str):
    """The one place a field name is checked and the one place the refusal is worded.

    Both `field_values()` (which reads a field off one episode) and `select_episodes()`
    (which validates the caller's field before scanning anything) have to reject an
    unknown name, and they used to carry the same sentence twice — two copies of a
    contract that must not drift, since "your field name is wrong" has to read identically
    whether the caller arrived through the CLI or through the API."""
    reader = _FIELD_READERS.get(field)
    if reader is None:
        raise QueryError(
            f"{field!r} is not a selectable field (selectable: {', '.join(SELECTABLE_FIELDS)})"
        )
    return reader


def field_values(episode, field: str) -> list[str]:
    """Every value an episode carries for `field`, as strings — one element for a
    scalar, N for a repeated field like artifact-ref, zero if the episode carries none.

    Counted fields are compared as strings (refusals "0", not 0) so one comparison rule
    covers every field and a CLI --value never needs a per-field type. An unrecognized
    field name RAISES: returning [] instead would make a typo indistinguishable from a
    genuine no-match, which is the silent-omission failure mode wearing a different
    hat."""
    return _selectable_field_reader(field)(episode)


# --- primitive 3: select by exact field value / set membership ------------------------


def select_episodes(root: Path, field: str, values, include_retired: bool = False) -> list:
    """Every episode whose `field` carries at least one of `values` — exact match, set
    membership. Nothing is ranked and nothing is scored; the answer is a complete,
    unordered candidate set, returned id-sorted only for determinism. Restricted to the
    ordinary-search set unless `include_retired` deliberately asks for the archive too.

    Matching compares whole parsed values with ==. It never searches the file text, so
    it can neither over-return on a prefix nor under-return on an unanchored line
    pattern. field_values() is validated once, up front, against the FIRST episode
    scanned — and, when the store is empty, still validated below — so an unknown field
    name always raises even when no episode would have matched anyway.

    `values` must be an iterable of whole values, NOT a bare string. A bare string is
    refused rather than wrapped: `set("implementer")` is a set of eleven CHARACTERS, so
    accepting one would silently match single-character values and silently miss the value
    the caller actually named — a wrong answer with no error, which is the one failure mode
    this store is built to avoid. Refusing is safe because the natural caller idiom
    (`select_episodes(root, "role", "implementer")`) is exactly the broken one, and #305 /
    #308's callers are agent-written."""
    if isinstance(values, (str, bytes)):
        raise QueryError(
            f"select values must be an iterable of whole values, not a bare "
            f"{type(values).__name__} — pass [{values!r}] rather than {values!r} "
            f"(a bare string would match its individual characters)"
        )
    wanted = set(values)
    if not wanted:
        raise QueryError("select requires at least one value to match")
    _selectable_field_reader(field)
    matched = []
    for episode in enumerate_episodes(root, include_retired=include_retired):
        if wanted & set(field_values(episode, field)):
            matched.append(episode)
    return matched


def select_episode_ids(root: Path, field: str, values, include_retired: bool = False) -> list[str]:
    return [
        ep.episode_id
        for ep in select_episodes(root, field, values, include_retired=include_retired)
    ]


# --- primitive 4: enumerate neighbours -----------------------------------------------
#
# "Neighbour" needs a definition, and EPISODE_STORE.md deliberately does not fix one —
# it says "shared exact join key" and leaves which keys to the gate that builds the
# primitive. Chosen here, and stated so a reader never has to infer it from the code:
#
#   artifact-ref   — two episodes touched at least one identical artifact. This is the
#                    join the record shape itself already privileges: section 6's
#                    Stratum A mapping names artifact-ref lines as an assertion's
#                    SUPPORTING EVIDENCE, so a shared artifact is a shared piece of
#                    evidence — the strongest mechanical signal available that two
#                    episodes are about the same thing.
#   (role, spine-step) — the same kind of agent hit the same point in a spine. This is
#                    the "same situation, different run" join, and it is a PAIR rather
#                    than two separate keys on purpose: role alone would make every
#                    implementer episode a neighbour of every other, which is a
#                    candidate set so large it stops being a candidate set.
#
# Explicitly NOT join keys: run (an episode's own run's other episodes are already
# reachable by id — section 2 makes the filename a free run-lookup key — and joining on
# it would flood the neighbourhood with a run's unrelated episodes), project, and every
# counter field (two episodes both having rework-count 1 says nothing about them).
#
# The result is the UNION over every join key, never the first key that matched. A
# first-key-wins implementation silently omits every neighbour joined on a later key —
# demonstrated by naive_neighbours_first_key_wins in tests/test_episode_store.py.

JOIN_KEYS = ("artifact-ref", "role+spine-step")


def _join_key_values(episode) -> set[tuple[str, str]]:
    """An episode's join-key values as (key-name, value) pairs. Two episodes are
    neighbours exactly when these sets intersect — one set operation, so no join key
    can be skipped, short-circuited, or ordered ahead of another."""
    keys = {("artifact-ref", ref) for ref in field_values(episode, "artifact-ref")}
    keys.add(("role+spine-step", f"{episode.role}\x00{episode.spine_step}"))
    return keys


def neighbours(root: Path, episode_id: str, include_retired: bool = False) -> list:
    """Every OTHER episode sharing at least one exact join key with `episode_id`.

    Complete by construction (a union over all of JOIN_KEYS), unranked (id-sorted for
    determinism only — a neighbour joined on two keys does not sort above one joined on
    one; counting shared keys would be scoring, which section 8 forbids), and self
    excluded. An unknown episode id raises rather than returning an empty
    neighbourhood: "this episode has no neighbours" and "there is no such episode" are
    different answers.

    The NEIGHBOURHOOD is the ordinary set unless `include_retired` asks otherwise; the
    ANCHOR is fetched by id, so an already-retired episode's surviving neighbours are
    still reachable — which is what #308's consolidation pass needs in order to walk back
    from an archived member of a cluster."""
    anchor = fetch_episode(episode_id, root)
    if anchor is None:
        raise EpisodeNotFound(f"no such episode: {episode_id}")
    anchor_keys = _join_key_values(anchor)
    return [
        episode
        for episode in enumerate_episodes(root, include_retired=include_retired)
        if episode.episode_id != episode_id and (anchor_keys & _join_key_values(episode))
    ]


def neighbour_ids(root: Path, episode_id: str, include_retired: bool = False) -> list[str]:
    return [
        ep.episode_id for ep in neighbours(root, episode_id, include_retired=include_retired)
    ]


# --- serialization -------------------------------------------------------------------


def assertion_to_dict(assertion) -> dict:
    return {
        "aid": assertion.aid,
        "kind": assertion.kind,
        "strength": assertion.strength,
        "lifecycle-standing": assertion.lifecycle_standing,
        "statement": assertion.statement,
        "history": list(assertion.history),
    }


def episode_to_dict(episode) -> dict:
    """The record as data. Carries no score, rank, distance or relevance field — there
    is nothing of the kind to carry (section 8)."""
    w = writer()
    ordered_kinds = w.AGENT_SUPPLIED_KINDS
    return {
        "id": episode.episode_id,
        "mechanical": {
            "run": episode.run,
            "project": episode.project,
            "role": episode.role,
            "spine-step": episode.spine_step,
            "context-manifest-ref": episode.context_manifest_ref,
            "refusals": episode.refusals,
            "reopens": episode.reopens,
            "rework-count": episode.rework_count,
            "failed-commands": episode.failed_commands,
            "artifact-ref": list(episode.artifact_refs),
        },
        "agent-supplied": [
            assertion_to_dict(episode.agent_supplied[kind])
            for kind in ordered_kinds
            if kind in episode.agent_supplied
        ],
        "diagnosis": [assertion_to_dict(a) for a in episode.diagnosis],
        "retirement": {
            "status": episode.status,
            "retired-reason": episode.retired_reason,
            "retired-at": episode.retired_at,
            "consolidated-into": episode.consolidated_into,
            "superseded-by": episode.superseded_by,
        },
    }


def _envelope(query: str, root: Path, episodes: list, include_retired: bool) -> dict:
    """The CLI's answer shape. `pid` names the OS process that produced this answer —
    provenance, and the thing that makes a cross-SESSION retrieval exercise able to
    prove it really crossed a process boundary instead of calling a function twice.

    `include_retired` states which universe the answer came from. Without it a caller
    could mistake an archive-excluding answer for a complete one — a silent omission that
    happens at the consumer's end rather than this module's, and is no less silent for
    it."""
    return {
        "query": query,
        "store_root": str(root),
        "pid": os.getpid(),
        "include_retired": include_retired,
        "count": len(episodes),
        "ids": [ep.episode_id for ep in episodes],
        "results": [episode_to_dict(ep) for ep in episodes],
    }


# --- CLI -----------------------------------------------------------------------------
#
# Exit codes: 0 answered; 1 the query itself was invalid (bad field name, bad usage) —
# never an empty result standing in for a rejected query; 2 fetch found no such
# episode. A caller can therefore tell "your query was wrong" from "nothing is there".


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic retrieval over the episode store.")
    parser.add_argument(
        "--store-root",
        type=Path,
        default=None,
        help="episode store root (default: the tracked episodes/ seam)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # The archive flag, attached to every SCANNING subcommand and to none other. Not a
    # top-level option: making it global would silently offer it on `fetch`, where it has
    # no meaning (a lookup by id already reaches the archive) and would imply, wrongly,
    # that fetch's default hides something.
    def add_archive_flag(p):
        p.add_argument(
            "--include-retired",
            action="store_true",
            help=(
                "also scan the archive of retired episodes. Off by default: retirement "
                "means excluded from ordinary search, retained in history, so reaching "
                "into history is a deliberate act"
            ),
        )
        return p

    fetch_parser = sub.add_parser(
        "fetch",
        help="fetch one episode by id (finds retired episodes too — a lookup is not a search)",
    )
    fetch_parser.add_argument("episode_id")

    add_archive_flag(sub.add_parser("enumerate", help="enumerate every episode in the store"))

    select_parser = add_archive_flag(
        sub.add_parser("select", help="select episodes by exact field value / set membership")
    )
    # Deliberately NOT argparse `choices`: an unknown field must come back as this
    # module's own QueryError (exit 1, naming the selectable fields) rather than
    # argparse's exit-2 usage error, so "your field name is wrong" reads the same
    # whether the caller came through the CLI or through select_episodes() directly.
    select_parser.add_argument("--field", required=True, metavar="FIELD")
    select_parser.add_argument(
        "--value",
        required=True,
        action="append",
        dest="values",
        help="repeat for set membership: match any episode carrying ANY of these values",
    )

    neighbours_parser = add_archive_flag(
        sub.add_parser(
            "neighbours", help="every other episode sharing an exact join key with this one"
        )
    )
    neighbours_parser.add_argument("episode_id")

    args = parser.parse_args(argv)
    root = args.store_root if args.store_root is not None else store_root()
    include_retired = getattr(args, "include_retired", False)

    try:
        if args.command == "fetch":
            episode = fetch_episode(args.episode_id, root)
            if episode is None:
                print(f"error: no such episode: {args.episode_id}", file=sys.stderr)
                return 2
            episodes = [episode]
        elif args.command == "select":
            episodes = select_episodes(
                root, args.field, args.values, include_retired=include_retired
            )
        elif args.command == "neighbours":
            episodes = neighbours(root, args.episode_id, include_retired=include_retired)
        else:
            episodes = enumerate_episodes(root, include_retired=include_retired)
    except EpisodeNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except QueryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except writer().EpisodeDeltaError as exc:
        # No prefix: every store-level refusal already names its own condition ("missing
        # store", "missing store layout", "malformed store", "half-retired store"), and a
        # blanket "corrupt store:" in front of them was wrong for the one that means the
        # store is not there at all.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            _envelope(args.command, root, episodes, include_retired),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
