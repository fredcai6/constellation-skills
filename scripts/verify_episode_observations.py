#!/usr/bin/env python
"""Guard: refuse a store whose records read as instructions instead of observations.

`episodes/` holds a record of *things that happened*. A record that tells a future
agent what to do is the retired learning playbook growing back inside the store that
replaced it — the constraint is already doctrine at
`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook", and this
script is what keeps it true after issue #460 rewrote the canon records.

CLI: `verify_episode_observations.py [--store-root PATH] [--strict]`

Exit codes:
  0  report mode (the default): the report is printed and the exit is always 0
  0  `--strict` and the store is clean — every offender is on the exception list and
     every exception list entry still names a live offender
  1  `--strict` and the store is not clean: an offender that is not on the list, or a
     STALE list entry (see below)
  2  REFUSED — the store could not be read at all. Refused, not answered.

WHAT IT LOOKS FOR — two triggers, both narrowed by measurement
--------------------------------------------------------------
1. IMPERATIVE, applied ONLY to the `workaround` and `proposed-remedy` kinds. A clause
   that opens with a bare base-form verb and no subject.
2. SECOND PERSON, applied to every kind. `you` / `your` / `yours` / `yourself` in text
   that is not inside quotation marks.

Deliberately NOT a trigger: a bare deontic modal (`must`, `should`, `always`,
`never`). Measured over all 253 assertion statements in the store, bare-modal matching
produced 30 hits that are overwhelmingly descriptive prose or recorded expectations —
"A gate that MUST prove a refusal has no direct expression..." is an observation about
a gate, and "`git check-ignore -v` ... SHOULD exit 0" is a recorded expectation. The
rule was dropped rather than filed down.

THE `task-intent` EXEMPTION. `task-intent` is written in the bare infinitive by house
convention; `docs/EPISODE_STORE.md`'s own canonical worked record is in that form. The
naive detector's 41 imperative hits included 31 `task-intent` statements — it flagged
the document that defines the format. Scoping the imperative rule to `workaround` and
`proposed-remedy` is what removes them, and it is why the rule is not applied
store-wide.

THE HONEST LIMIT — state it plainly rather than claiming more than was measured
-------------------------------------------------------------------------------
This is a LEXICAL detector over a closed verb list. It cannot parse grammar, so:

  * It can only catch an imperative that opens with a verb in `IMPERATIVE_VERBS`. A
    prescription phrased with a verb outside that list passes. The list was drawn from
    the corpus, so it is calibrated to what this store actually contains and has no
    claim to generality.
  * Its quotation handling is a regex over paired quote characters, not a parser. The
    single-quote arm requires word boundaries so a possessive apostrophe cannot shift
    every following quote, but a genuinely unbalanced quote still swallows more text
    than intended, and text inside a quoted span is not examined at all.
  * A verb that is also a noun (`run`, `use`, `note`, `check`) can open a clause as a
    noun. Measured over the current corpus this produces 0 false positives, but that is
    a fact about this corpus, not a property of the detector.

So the guard is a floor, not a proof. It catches the shape the 32 migrated canon
records actually carried. It does not establish that a record it passes is
observational, and no caller should read it as saying so.

THE EXCEPTION LIST, AND WHY IT IS NOT A LOOPHOLE
------------------------------------------------
Issue #460's rewrite gate left five statements alone because the record cannot support
a factual restatement — writing a past-tense claim the record does not contain would
falsify the store, which is worse than leaving a prescription standing. Those five are
still prescriptive, so a guard demanding a clean store would go red on exactly the
honest outcome, and the only escapes would be to fabricate a rewrite or to file the
lexicon down until the corpus passes. Both are the check-that-cannot-fail shape this
repo has a label for.

So the list is explicit, keyed by (episode id, assertion id), carries a REQUIRED
non-empty reason per entry, and is seeded from that gate's ungrounded list and from
nothing else. It fails on a STALE entry too — one whose episode is in the scanned store
but whose assertion is gone or no longer trips any trigger — so an entry cannot quietly
outlive its reason and leave the list looking like it is still doing work. See
`scan_store` for why an entry naming an episode absent from the scanned store is
reported as inapplicable rather than failed, and where that gap is closed instead.

THE VALVE. This script reads assertion `statement` text, which `verify_episode_captured.py`
deliberately does not. It therefore never PRINTS a statement: the report emits the
episode id, the assertion id, the trigger, and the matched token only. Ids and
triggers out; statements never. A guard that echoes record content into a transcript
is a read path, and the read path is the thing the store replaced.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

_QUERY_PATH = Path(__file__).resolve().parent / "query_episodes.py"
_QUERY_MODULE = "query_episodes"

EXIT_CLEAN = 0
EXIT_OFFENDERS = 1
EXIT_REFUSED = 2


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def query():
    """The retrieval module, resolved lazily on every call for the same reason
    `query_episodes.writer()` is: a caller that has already imported it shares that
    exact module object and its parser, rather than this module operating on a second,
    divergent copy of the record grammar."""
    module = sys.modules.get(_QUERY_MODULE)
    if module is not None:
        try:
            if Path(getattr(module, "__file__", "")).resolve() == _QUERY_PATH:
                return module
        except (OSError, ValueError):
            pass
    spec = importlib.util.spec_from_file_location(_QUERY_MODULE, _QUERY_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[_QUERY_MODULE] = module
    spec.loader.exec_module(module)
    return module


# --- the two triggers ----------------------------------------------------------------

# The imperative rule is scoped to these kinds and no others. See the task-intent
# exemption above — widening this tuple re-admits the 31 false positives the
# measurement removed.
IMPERATIVE_KINDS = ("workaround", "proposed-remedy")

# Closed base-form verb list, drawn from the corpus this guard was calibrated against.
# It is deliberately not a general English imperative lexicon: an open list would trade
# the measured false-positive rate for a claim about grammar this script cannot make.
IMPERATIVE_VERBS = frozenset(
    """
    accept add apply assert author avoid build call capture check collect consider
    delete demand do drop emit enumerate ensure extend fail file fix give grep hold
    instruct keep let list make mark measure name narrow note open pair pass pin place
    prefer prove provide put raise read record refuse reject rely remove replace report
    require resolve return reuse review run scope separate set ship start state stop
    surface take tell test track treat update use verify wait watch widen wrap write
    """.split()
)

# Words that may sit in front of an imperative verb without giving the clause a
# subject: coordinators, discourse leads, and adverbs. Skipped, then the next token is
# tested. "Either MEASURE ordering ... , or explicitly STOP treating ..." needs both
# halves of this.
_IMPERATIVE_LEADS = frozenset(
    """
    also always and but either explicitly finally first instead just never next now
    only optionally or rather simply so then therefore thus
    """.split()
)

# Clause openings: the start of the statement, and whatever follows a sentence or
# clause boundary. The bare-comma case is load-bearing — "When authoring or updating a
# drill ..., ENUMERATE every sibling template ..." hangs its imperative off one.
_CLAUSE_SPLIT_RE = re.compile(r"(?:[.;:]\s+|\s+--\s+|,\s+)")

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

SECOND_PERSON_RE = re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE)

# Paired quote spans, stripped before BOTH tests so that a record QUOTING the artifact
# it studied is not read as speaking in its own voice. Two measured instances, and they
# are the same principle from two directions: issue-304-g3-005 quotes the context
# imperative under study ("... re-anchoring the context imperative to 'before you open
# any source file'"), and issue-308-023 records a candidate instruction verbatim as the
# cold sensor's own words, "recorded as the sensor's words and deciding nothing". A
# record that quotes an instruction it observed IS an observation.
# The single-quote arm requires its delimiters to sit at a word boundary, so a
# word-internal apostrophe ("the sensor's words") cannot open a span and shift every
# following quote by one. Without that guard, quote pairing depends on how many
# possessives happen to precede the quotation — the detector's answer would be a matter
# of apostrophe parity rather than of what the record says.
_QUOTED_SPAN_RE = re.compile(r"\"[^\"]*\"|(?<![A-Za-z])'[^']*'(?![A-Za-z])|`[^`]*`")

# Parenthesised spans and <angle-bracket> placeholders, stripped before the imperative
# test only. Both were measured false-positive sources: an appositive list reads as a
# comma clause ("any named EDIT TARGET (section heading, file path, anchor) was
# checked" flagged `file`), and a command placeholder reads as a bare verb
# ("git log --format=%h -- <file>" flagged `file`). Neither is a clause with a verb in
# it. They are NOT stripped for the second-person test, where a parenthetical is still
# prose that can address a reader.
_BRACKETED_SPAN_RE = re.compile(r"\([^()]*\)|<[^<>]*>")


def _blank(pattern: re.Pattern, text: str) -> str:
    """Matched spans blanked, length preserved so offsets stay meaningful."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def strip_quoted(text: str) -> str:
    return _blank(_QUOTED_SPAN_RE, text)


def strip_quoted_and_bracketed(text: str) -> str:
    return _blank(_BRACKETED_SPAN_RE, strip_quoted(text))


def imperative_hits(statement: str) -> list[str]:
    """Base-form verbs found opening a clause with no subject, in order of appearance."""
    hits = []
    for clause in _CLAUSE_SPLIT_RE.split(strip_quoted_and_bracketed(statement)):
        for token in _TOKEN_RE.findall(clause):
            word = token.lower()
            if word in _IMPERATIVE_LEADS or word.endswith("ly"):
                continue  # a lead or an adverb: look past it at the next token
            if word in IMPERATIVE_VERBS:
                hits.append(token)
            break  # only the clause-opening word can be a subjectless imperative
    return hits


def second_person_hits(statement: str) -> list[str]:
    return SECOND_PERSON_RE.findall(strip_quoted(statement))


def triggers_for(kind: str, statement: str) -> list[tuple[str, str]]:
    """Every (trigger, matched token) this statement trips. Empty means it reads as an
    observation under the two rules — which is weaker than saying it IS one; see the
    honest limit in the module docstring."""
    found = []
    if kind in IMPERATIVE_KINDS:
        found += [("imperative", tok) for tok in imperative_hits(statement)]
    found += [("second-person", tok) for tok in second_person_hits(statement)]
    return found


# --- the exception list --------------------------------------------------------------
#
# Seeded from issue #460 gate g2's ungrounded list and from nothing else. Every entry
# needs a reason naming why the RECORD cannot support a factual restatement — not why
# the rewrite was inconvenient. An entry whose episode or assertion has gone, or that no
# longer trips a trigger, is STALE and fails the guard.

EXCEPTIONS: dict[tuple[str, str], str] = {
    ("issue-304-g3-005", "d2"): (
        "Two branches of advice, and the record states that NEITHER was taken: a3 files "
        "the gate as NOT DETERMINABLE AT THIS GATE and d1 says no artifact in the "
        "pipeline carries the transcript. A factual restatement would either invent an "
        "act nobody performed or collapse the assertion into a duplicate of d1."
    ),
    ("issue-308-014", "a5"): (
        "No sibling records that the drill was ever updated. a3 and a4 record only the "
        "defect. Writing that the drill was updated to enumerate every sibling would be "
        "a fabrication."
    ),
    ("issue-308-015", "a5"): (
        "Asserts an adopted standing policy the record does not contain. a4 calls it 'A "
        "single data point from one run'; no sibling says the pass was made a floor."
    ),
    ("issue-308-017", "a5"): (
        "No sibling records the replacement as made. a3 describes the two defects and a4 "
        "records detection only."
    ),
    ("issue-308-019", "a5"): (
        "The record files this explicitly as a proposal, not an application: a4 records "
        "it as 'the suggested upstream edit recorded at export'. Only one sub-clause has "
        "any applied instance; the requirement list as a whole was never adopted."
    ),
}


class Offender:
    __slots__ = ("episode_id", "aid", "kind", "trigger", "token")

    def __init__(self, episode_id, aid, kind, trigger, token):
        self.episode_id = episode_id
        self.aid = aid
        self.kind = kind
        self.trigger = trigger
        self.token = token

    @property
    def key(self):
        return (self.episode_id, self.aid)


def scan_store(root: Path, exceptions=None) -> tuple[list[Offender], list[str], list[str], int]:
    """Returns (offenders, stale entries, inapplicable entries, statements examined).

    `offenders` is every assertion that trips a trigger, INCLUDING the excepted ones —
    the caller decides what an exception forgives, so the scan cannot quietly shorten
    its own answer.

    STALE vs INAPPLICABLE, and why they are not the same failure. An entry is STALE when
    the episode IS in the scanned store but the entry no longer does any work: the
    assertion is gone, or it no longer trips a trigger. That is an exemption outliving
    its reason, and it fails the guard. An entry is INAPPLICABLE when the episode is not
    in the scanned store at all — the list is simply about a different store, which is
    the ordinary case for every temp store in the test suite and for any fixture. It is
    reported and does NOT fail, because failing there would mean no store but the real
    one could ever pass, and the guard would be untestable against a clean fixture.

    The gap that leaves — an episode DELETED from the real store, whose entry would go
    quiet as inapplicable rather than loud as stale — is closed by
    tests/test_episode_observations.py::RealStoreTests, which asserts every shipped entry
    still names a live offender in episodes/. Only a scan of the real store can answer
    that question, so that is where it is asked.
    """
    exceptions = EXCEPTIONS if exceptions is None else exceptions
    q = query()
    offenders: list[Offender] = []
    examined = 0
    present_episodes: set[str] = set()
    live_keys: set[tuple[str, str]] = set()
    tripped_keys: set[tuple[str, str]] = set()

    for episode in q.enumerate_episodes(root):
        record = q.episode_to_dict(episode)
        present_episodes.add(record["id"])
        for assertion in record["agent-supplied"] + record["diagnosis"]:
            examined += 1
            key = (record["id"], assertion["aid"])
            live_keys.add(key)
            for trigger, token in triggers_for(assertion["kind"], assertion["statement"]):
                tripped_keys.add(key)
                offenders.append(
                    Offender(record["id"], assertion["aid"], assertion["kind"], trigger, token)
                )

    stale, inapplicable = [], []
    for eid, aid in exceptions:
        if (eid, aid) in tripped_keys:
            continue
        if eid not in present_episodes:
            inapplicable.append(f"{eid}/{aid}")
        elif (eid, aid) not in live_keys:
            stale.append(f"{eid}/{aid} (no such assertion)")
        else:
            stale.append(f"{eid}/{aid}")
    return offenders, sorted(stale), sorted(inapplicable), examined


def _validate_exception_reasons(exceptions) -> list[str]:
    """An entry with an empty reason is an unexplained exemption, which is the loophole
    the list exists to close. Checked before any store read so it fails the same way on
    an unreadable store."""
    return sorted(
        f"{eid}/{aid}" for (eid, aid), reason in exceptions.items() if not (reason or "").strip()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--store-root",
        type=Path,
        default=None,
        help="the episode store to scan. Defaults to the writer's store_root().",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero on an unlisted offender or a stale exception entry",
    )
    args = parser.parse_args(argv)

    unexplained = _validate_exception_reasons(EXCEPTIONS)
    if unexplained:
        print("REFUSED: exception entries with no reason: " + ", ".join(unexplained))
        return EXIT_REFUSED

    q = query()
    root = args.store_root if args.store_root is not None else q.store_root()
    try:
        offenders, stale, inapplicable, examined = scan_store(root)
    except Exception as exc:  # noqa: BLE001 — refused, not answered
        print(f"REFUSED: the store at {root} could not be read: {exc}")
        return EXIT_REFUSED

    unlisted = [o for o in offenders if o.key not in EXCEPTIONS]
    excepted = [o for o in offenders if o.key in EXCEPTIONS]

    print(f"episode-observation guard: {examined} statements examined under {root}")
    print(f"  offenders: {len(unlisted)} unlisted, {len(excepted)} on the exception list")
    for o in unlisted:
        print(f"  OFFENDER {o.episode_id} {o.aid} ({o.kind}) {o.trigger}: {o.token!r}")
    for o in excepted:
        print(f"  excepted {o.episode_id} {o.aid} ({o.kind}) {o.trigger}: {o.token!r}")
    for entry in stale:
        print(f"  STALE EXCEPTION {entry} — it no longer trips any trigger")
    for entry in inapplicable:
        print(f"  not applicable here {entry} — no such episode in this store")

    if not args.strict:
        print("report mode: exit 0 regardless. Pass --strict to make this a gate.")
        return EXIT_CLEAN
    if unlisted or stale:
        return EXIT_OFFENDERS
    return EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main())
